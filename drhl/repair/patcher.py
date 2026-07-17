from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from time import perf_counter
from typing import Any

import requests

from ..config import PipelineConfig
from ..database import Snapshot
from ..database_probe import create_database_probe
from ..errors import DatabaseError
from ..io import write_json
from ..models import AttackVector, Finding, RequestSpec


@dataclass
class RepairAttempt:
    attempt: int
    output: str | None
    syntax_compile_ok: bool
    exploit_blocked: bool
    regression_passed: bool
    successful: bool
    message: str
    prompt_artifact: str | None = None
    plan: str | None = None


@dataclass
class RepairResult:
    category: str
    page: str
    source: str | None
    output: str | None
    status: str
    message: str
    engine: str = "llm"
    plan: str | None = None
    prompt_artifact: str | None = None
    attempts: int = 0
    patches_generated: int = 0
    syntax_compile_ok: int = 0
    exploit_blocked: int = 0
    regression_passed: int = 0
    successful: bool = False
    validation_artifact: str | None = None
    attempt_details: list[RepairAttempt] = field(default_factory=list)


def _safe_source(root: Path, relative: str) -> Path | None:
    candidate = (root / Path(*PurePosixPath(relative).parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _page_match_candidates(page: str) -> list[str]:
    full = str(page).lstrip("/").replace("\\", "/")
    normalized = PurePosixPath(full.split("?", 1)[0]).as_posix()
    parameterized = re.sub(r"(?<=/)\d+(?=/|$)", "p1", normalized)
    candidates = [
        full,
        normalized,
        normalized.rstrip("/"),
        normalized.rstrip("/") + "/",
        parameterized,
        parameterized.rstrip("/"),
        parameterized.rstrip("/") + "/",
    ]
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _configured_source_override(config: PipelineConfig, page: str) -> str | None:
    overrides = config.repair.get("source_map_overrides", [])
    for item in overrides:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or item.get("file") or "")
        if not source:
            continue
        pattern = str(item.get("pattern") or "")
        exact = str(item.get("page") or "").lstrip("/").replace("\\", "/")
        candidates = _page_match_candidates(page)
        if exact and exact in candidates:
            return source
        if pattern and any(re.search(pattern, candidate, re.I) for candidate in candidates):
            return source
    return None


def _repair_source_name(config: PipelineConfig, source_map: dict[str, Any], page: str) -> str | None:
    for candidate in _page_match_candidates(page):
        mapped = source_map.get(candidate)
        if mapped:
            return str(mapped)
    return _configured_source_override(config, page)

def _secret(value: Any) -> str:
    text = str(value or "")
    if text.startswith("env:"):
        return os.environ.get(text[4:], "")
    return text


def _endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def _chat_completion(llm: dict[str, Any], messages: list[dict[str, str]], metrics: dict[str, Any] | None = None) -> str:
    api_key = _secret(llm.get("api_key"))
    if not api_key:
        raise ValueError("repair.llm.api_key is not configured")
    body: dict[str, Any] = {
        "model": str(llm.get("model", "deepseek-v4-flash")),
        "messages": messages,
        "temperature": float(llm.get("temperature", 0.1)),
    }
    if llm.get("response_format_json", True):
        body["response_format"] = {"type": "json_object"}
    if llm.get("max_tokens"):
        body["max_tokens"] = int(llm["max_tokens"])
    started = perf_counter()
    response = requests.post(
        _endpoint(str(llm.get("base_url", "https://api.deepseek.com/v1"))),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=float(llm.get("timeout", 120)),
    )
    elapsed = perf_counter() - started
    if metrics is not None:
        metrics["llm_inference_seconds"] = metrics.get("llm_inference_seconds", 0.0) + elapsed
        metrics["llm_requests"] = metrics.get("llm_requests", 0) + 1
    if response.status_code >= 400:
        raise RuntimeError(f"LLM request failed: HTTP {response.status_code}: {response.text[:600]}")
    data = response.json()
    usage = data.get("usage") if isinstance(data, dict) else None
    if metrics is not None and isinstance(usage, dict):
        prompt_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))
        metrics["tokens_in"] = metrics.get("tokens_in", 0) + prompt_tokens
        metrics["tokens_out"] = metrics.get("tokens_out", 0) + completion_tokens
        metrics["tokens_total"] = metrics.get("tokens_total", 0) + total_tokens
        input_cost_per_million = float(llm.get("input_cost_per_million_tokens", 0) or 0)
        output_cost_per_million = float(llm.get("output_cost_per_million_tokens", 0) or 0)
        if input_cost_per_million or output_cost_per_million:
            metrics["api_cost_usd"] = metrics.get("api_cost_usd", 0.0) + (
                prompt_tokens * input_cost_per_million + completion_tokens * output_cost_per_million
            ) / 1_000_000
            metrics["api_cost_pricing_configured"] = True
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"unexpected LLM response shape: {data}") from exc


def _json_from_model(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("LLM response must be a JSON object")
    return value


def _page_type(category: str) -> str:
    mapping = {
        "admin_only": "Admin-only page: block visitors and ordinary users; allow authorized admin roles.",
        "authenticated_only": "Login-required page: block visitors; allow authenticated authorized roles.",
        "static_only": "Standalone protected page: block unauthorized direct access; preserve intended admin/authorized access.",
        "vertical": "Role-restricted page: block lower-privilege actors; keep authorized higher-privilege roles working.",
        "horizontal": "Owner-restricted page: block cross-user object access; keep owner or existing privileged role access working.",
    }
    return mapping.get(category, f"Protected page in category {category}.")


def _repair_goal(category: str) -> str:
    mapping = {
        "admin_only": "Exploit must be blocked for visitor/ordinary users; regression must pass for admin/authorized role.",
        "authenticated_only": "Exploit must be blocked for visitor; regression must pass for logged-in authorized role.",
        "static_only": "Exploit must be blocked for unauthorized direct access; preserve intended admin/authorized access inferred from path, snippets, or existing guard semantics.",
        "vertical": "Exploit must be blocked for lower-privilege actor; regression must pass for authorized higher-privilege role. Do not add owner-only checks unless an existing privileged-role bypass is preserved.",
        "horizontal": "Exploit must be blocked for cross-user identity values; regression must pass for the owner or existing privileged role.",
    }
    return mapping.get(category, "Block the attacking actor while preserving authorized behavior.")


def _vulnerability_type(category: str) -> str:
    return "horizontal privilege escalation" if category == "horizontal" else "vertical privilege escalation"



_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_sql_identifier(value: Any) -> str | None:
    text = str(value or "").strip()
    return text if _SQL_IDENTIFIER_RE.match(text) else None


def _sql_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def _parse_tabular_rows(raw: str, columns: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        values = line.rstrip("\r\n").split("\t")
        rows.append({column: values[index] if index < len(values) else "" for index, column in enumerate(columns)})
    return rows


def _infer_role_column(columns: list[str], options: dict[str, Any]) -> str | None:
    configured = _safe_sql_identifier(options.get("role_column"))
    if configured and configured in columns:
        return configured
    candidates = options.get("role_column_candidates", [
        "role",
        "role_id",
        "rank",
        "rank_id",
        "group",
        "group_id",
        "usergroup",
        "user_group",
        "user_group_id",
        "level",
        "privilege",
        "permission",
    ])
    normalized_candidates = {str(item).lower() for item in candidates}
    for column in columns:
        lowered = column.lower()
        if lowered in normalized_candidates:
            return column
    for column in columns:
        lowered = column.lower()
        if any(token in lowered for token in ("role", "rank", "group", "level", "priv", "permission")):
            return column
    return None


def _sample_user_table_rows(rows: list[dict[str, str]], role_column: str | None, threshold: int, max_per_role: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    strategy: dict[str, Any] = {
        "input_rows": len(rows),
        "threshold": threshold,
        "role_column": role_column,
        "max_rows_per_role": max_per_role,
        "applied": False,
    }
    if len(rows) < threshold or not role_column:
        strategy["reason"] = "row count below threshold or no role column was available"
        return rows, strategy

    counts: dict[str, int] = {}
    sampled: list[dict[str, str]] = []
    for row in rows:
        role_value = str(row.get(role_column, ""))
        count = counts.get(role_value, 0)
        if count >= max_per_role:
            continue
        sampled.append(row)
        counts[role_value] = count + 1
    strategy.update({
        "applied": True,
        "output_rows": len(sampled),
        "role_value_counts": counts,
    })
    return sampled, strategy


def _repair_user_table_context(config: PipelineConfig) -> dict[str, Any]:
    options = dict(config.repair.get("user_table_context", {}))
    if not options:
        llm_options = config.repair.get("llm", {})
        if isinstance(llm_options, dict):
            options = dict(llm_options.get("user_table_context", {}))
    if not options or not bool(options.get("enabled", False)):
        return {}

    table = _safe_sql_identifier(options.get("table"))
    configured_columns = options.get("columns", [])
    columns = [_safe_sql_identifier(column) for column in configured_columns if _safe_sql_identifier(column)]
    if not table or not columns:
        return {
            "enabled": False,
            "reason": "repair.user_table_context requires a safe table name and explicit safe columns",
        }

    try:
        limit = max(1, min(int(options.get("limit", 20)), 200))
    except (TypeError, ValueError):
        limit = 20
    try:
        sampling_threshold = max(1, int(options.get("sample_by_role_when_rows_gte", 5)))
    except (TypeError, ValueError):
        sampling_threshold = 5
    try:
        max_rows_per_role = max(1, min(int(options.get("max_rows_per_role", 2)), 20))
    except (TypeError, ValueError):
        max_rows_per_role = 2
    try:
        scan_limit = max(limit, min(int(options.get("scan_limit", 1000)), 5000))
    except (TypeError, ValueError):
        scan_limit = max(limit, 1000)

    order_by = _safe_sql_identifier(options.get("order_by")) or columns[0]
    if order_by not in columns:
        order_by = columns[0]

    try:
        probe = create_database_probe(config.database)
        database_name = str(config.database.get("database", ""))
        column_list_raw = probe.scalar(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            f"WHERE TABLE_SCHEMA={_sql_literal(database_name)} AND TABLE_NAME={_sql_literal(table)} "
            "ORDER BY ORDINAL_POSITION"
        )
        actual_columns = {line.strip() for line in column_list_raw.splitlines() if line.strip()}
        selected_columns = [column for column in columns if column in actual_columns]
        if not selected_columns:
            return {
                "enabled": False,
                "table": table,
                "reason": "configured user table columns were not found in the database",
            }
        role_column = _infer_role_column(selected_columns, options)
        select_sql = ", ".join(f"`{column}`" for column in selected_columns)
        total_rows_raw = probe.scalar(f"SELECT COUNT(*) FROM `{table}`")
        try:
            total_rows = int((total_rows_raw.splitlines() or ["0"])[0] or 0)
        except ValueError:
            total_rows = 0

        if total_rows >= sampling_threshold and role_column:
            raw_rows = probe.scalar(
                f"SELECT {select_sql} FROM `{table}` ORDER BY `{role_column}`, `{order_by}` LIMIT {scan_limit}"
            )
            rows, sampling = _sample_user_table_rows(
                _parse_tabular_rows(raw_rows, selected_columns),
                role_column,
                sampling_threshold,
                max_rows_per_role,
            )
        else:
            raw_rows = probe.scalar(f"SELECT {select_sql} FROM `{table}` ORDER BY `{order_by}` LIMIT {limit}")
            rows = _parse_tabular_rows(raw_rows, selected_columns)
            sampling = {
                "applied": False,
                "input_rows": total_rows,
                "threshold": sampling_threshold,
                "role_column": role_column,
                "max_rows_per_role": max_rows_per_role,
                "reason": "row count below threshold or no role column was available",
            }

        return {
            "enabled": True,
            "table": table,
            "columns": selected_columns,
            "total_rows": total_rows,
            "sampling": sampling,
            "rows": rows,
            "notes": [
                "This is the only database table context provided to the repair model.",
                "When the user table is large, rows are sampled by the configured/inferred role column with a small maximum per role value.",
                "Use it only to identify real user ids, usernames, and role/rank fields; do not infer unrelated schema.",
            ],
        }
    except DatabaseError as exc:
        return {"enabled": False, "table": table, "reason": f"database probe failed: {exc}"}
    except Exception as exc:
        return {"enabled": False, "table": table, "reason": f"unexpected error: {type(exc).__name__}: {exc}"}


def _binding_matches(binding: dict[str, Any], source_relative: str, vector: AttackVector | None) -> bool:
    source_path = str(binding.get("source_path") or binding.get("path") or "").strip().replace("\\", "/")
    if source_path and source_path != source_relative:
        return False
    if vector is None:
        return True
    page_pattern = str(binding.get("page_pattern") or "").strip()
    if page_pattern and not re.search(page_pattern, vector.page):
        return False
    required_params = binding.get("where_params", {})
    if isinstance(required_params, dict):
        params = dict(vector.request.params)
        for key, expected in required_params.items():
            if str(params.get(str(key), "")) != str(expected):
                return False
    return True


def _repair_identity_context(config: PipelineConfig, source_relative: str, vector: AttackVector | None) -> dict[str, Any]:
    options = dict(config.repair.get("identity_context", {}))
    if not options or not bool(options.get("enabled", False)):
        return {}

    current_user = options.get("current_user", [])
    if isinstance(current_user, dict):
        current_user_entries = [current_user]
    elif isinstance(current_user, list):
        current_user_entries = [entry for entry in current_user if isinstance(entry, dict)]
    else:
        current_user_entries = []

    bindings: list[dict[str, Any]] = []
    raw_bindings = options.get("bindings", [])
    if isinstance(raw_bindings, list):
        for raw in raw_bindings:
            if not isinstance(raw, dict) or not _binding_matches(raw, source_relative, vector):
                continue
            table = _safe_sql_identifier(raw.get("table"))
            lookup_column = _safe_sql_identifier(raw.get("lookup_column", "id"))
            owner_column = _safe_sql_identifier(raw.get("owner_column"))
            parameter = str(raw.get("parameter") or "").strip()
            if not table or not lookup_column or not owner_column or not parameter:
                continue
            binding = dict(raw)
            binding["table"] = table
            binding["lookup_column"] = lookup_column
            binding["owner_column"] = owner_column
            binding["parameter"] = parameter
            if vector is not None:
                binding["request_parameter_value"] = str(vector.request.params.get(parameter, ""))
            bindings.append(binding)

    context: dict[str, Any] = {
        "enabled": True,
        "current_user": current_user_entries,
        "bindings": [],
        "notes": [
            "For horizontal access-control repairs, prefer this identity binding context over guessing from names.",
            "Compare the configured target owner column with the configured current-user expression, preserving the configured privileged bypass when present.",
        ],
    }
    if not bindings:
        context["reason"] = "no identity binding matched this source/vector"
        return context

    try:
        probe = create_database_probe(config.database)
    except Exception as exc:
        context["reason"] = f"database probe unavailable for target samples: {type(exc).__name__}: {exc}"
        context["bindings"] = bindings
        return context

    for binding in bindings:
        sample_columns = [
            _safe_sql_identifier(column) for column in binding.get("sample_columns", []) if _safe_sql_identifier(column)
        ]
        for required in (binding["lookup_column"], binding["owner_column"]):
            if required not in sample_columns:
                sample_columns.insert(0, required)
        sample_columns = list(dict.fromkeys(sample_columns))[:12]
        value = str(binding.get("request_parameter_value", ""))
        sample_rows: list[dict[str, str]] = []
        if value:
            try:
                select_sql = ", ".join(f"`{column}`" for column in sample_columns)
                raw_rows = probe.scalar(
                    f"SELECT {select_sql} FROM `{binding['table']}` "
                    f"WHERE `{binding['lookup_column']}`={_sql_literal(value)} LIMIT 3"
                )
                sample_rows = _parse_tabular_rows(raw_rows, sample_columns)
            except Exception as exc:
                binding["sample_error"] = f"{type(exc).__name__}: {exc}"
        item = dict(binding)
        item["target_resource_sample"] = sample_rows
        context["bindings"].append(item)
    return context


def _repair_page_guidance(config: PipelineConfig, finding: Finding, vector: AttackVector | None) -> dict[str, Any]:
    entries = config.repair.get("page_repair_guidance", [])
    if not isinstance(entries, list):
        return {}
    page = vector.page if vector is not None else finding.page
    category = vector.category if vector is not None else finding.category
    for raw in entries:
        if not isinstance(raw, dict):
            continue
        pattern = str(raw.get("page_pattern") or "").strip()
        if pattern and not re.search(pattern, page, re.I):
            continue
        wanted_category = str(raw.get("category") or "").strip()
        if wanted_category and wanted_category != category:
            continue
        guidance = dict(raw)
        guidance["matched_page"] = page
        guidance["matched_category"] = category
        return guidance
    return {}


def _snippet_context(source_relative: str, source_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not source_context:
        return []
    snippets = list(source_context.get("snippets", []))
    related = [item for item in snippets if item.get("path") == source_relative]
    reusable = [
        item for item in snippets
        if item.get("kind") in {"validation_function", "guard_call", "condition", "conditional"}
        and item.get("path") != source_relative
    ]

    has_scored_snippets = any("access_control_score" in item for item in related + reusable)

    if not has_scored_snippets:
        def priority(item: dict[str, Any]) -> tuple[int, int]:
            text = " ".join(
                str(item.get(key, ""))
                for key in ("kind", "function", "condition", "code", "reduced_code")
            ).lower()
            score = 0
            kind = str(item.get("kind") or "")
            if kind in {"condition", "conditional"}:
                score -= 35
            if any(token in text for token in ("unauthenticated", "not authenticated", "not logged", "guest", "== 'no'", '== "no"')):
                score -= 30
            if any(token in text for token in ("session", "cookie", "login", "logout", "signin", "auth")):
                score -= 24
            if any(token in text for token in ("denied", "forbidden", "unauthorized", "not allowed", "no permission")):
                score -= 18
            if any(token in text for token in ("location:", "refresh", "redirect", "exit", "die(")):
                score -= 16
            if any(token in text for token in ("permission", "privilege", "role", "admin", "level", "owner", "author")):
                score -= 14
            if kind == "validation_function":
                score -= 10
            if item.get("path") == source_relative:
                score -= 8
            return (score, int(item.get("start_line") or 0))

        result = sorted(related + reusable, key=priority)
        return result[:80]

    def priority(item: dict[str, Any]) -> tuple[int, int]:
        text = " ".join(
            str(item.get(key, ""))
            for key in ("kind", "function", "condition", "code", "reduced_code", "context_code")
        ).lower()
        condition_text = str(item.get("condition", "")).lower()
        score = 0
        kind = str(item.get("kind") or "")
        try:
            score -= int(item.get("access_control_score") or 0)
        except (TypeError, ValueError):
            pass
        if kind in {"condition", "conditional"}:
            score -= 15
        if any(token in text for token in ("unauthenticated", "not authenticated", "not logged", "guest", "== 'no'", '== "no"')):
            score -= 30
        if any(token in text for token in ("session", "cookie", "login", "logout", "signin", "auth", "password", "test_log")):
            score -= 28
        if any(token in text for token in ("denied", "forbidden", "unauthorized", "not allowed", "no permission")):
            score -= 18
        if any(token in text for token in ("location:", "refresh", "redirect", "exit", "die(")):
            score -= 12
        if any(token in text for token in ("permission", "privilege", "role", "admin", "level", "owner", "author", "usergroup", "uid", "gid")):
            score -= 18
        weak_parameter_only = (
            any(token in condition_text for token in ("language", "lang", "locale", "nuova_band", "page", "sort", "limit", "offset"))
            and not any(token in condition_text for token in ("session", "cookie", "login", "password", "auth", "role", "admin", "owner", "uid", "usergroup"))
        )
        if weak_parameter_only:
            score += 80
        if kind == "validation_function":
            score -= 20
        if kind == "guard_call":
            score -= 18
        if item.get("path") == source_relative:
            score += 5 if weak_parameter_only else -4
        return (score, int(item.get("start_line") or 0))

    result = sorted(related + reusable, key=priority)
    return result[:60]


def _stage1_messages(
    finding: Finding,
    source_relative: str,
    source_code: str,
    snippets: list[dict[str, Any]],
    user_table_context: dict[str, Any] | None = None,
    identity_context: dict[str, Any] | None = None,
    page_guidance: dict[str, Any] | None = None,
    feedback: list[str] | None = None,
    vector: AttackVector | None = None,
) -> list[dict[str, str]]:
    payload = {
        "target": {
            "url": finding.page,
            "source_path": source_relative,
        },
        "access_policy": {
            "category": finding.category,
            "attacker_role": finding.actor,
            "authorized_roles": list(vector.authorized_roles) if vector else [],
            "identity_parameters": list(vector.identity_parameters) if vector else [],
        },
        "attack": {
            "method": finding.method,
            "evidence": finding.evidence,
        },
        "source_code": source_code,
        "validated_access_control_snippets": snippets,
        "previous_attempt_feedback": feedback or [],
    }
    context_rules = ""
    if identity_context:
        payload["identity_binding_context"] = identity_context
        context_rules += "4) Use identity_binding_context as the source of truth for current-user expressions, target lookup parameters, owner columns, and privileged bypasses. "
    if user_table_context:
        payload["database_user_table_context"] = user_table_context
        context_rules += "5) Use database_user_table_context only to resolve real user ids, usernames, and role/rank fields; do not invent other database fields. "
    if page_guidance:
        payload["page_repair_guidance"] = page_guidance
        context_rules += "6) Follow page_repair_guidance exactly when it is present; it is application-specific ground truth for this repair item. "
    return [
        {
            "role": "system",
            "content": (
                "Plan a minimal access-control fix. Use project snippets as the source of truth. "
                "Unauthorized requests must be blocked before sensitive operations. "
                "Do not write patched source in this stage. Return only JSON, no Markdown."
            ),
        },
        {
            "role": "user",
            "content": (
                "Infer the missing guard and exact insertion point. Rules: "
                "1) Reuse the app's real auth/role/owner variables, sentinel values, and denial/redirect style from snippets. "
                "2) Do not invent generic checks such as empty(), isset(), or new session keys unless snippets use them. "
                "3) Do not use a guard variable/function unless the target source or its included context initializes it; otherwise include or reuse the correct project guard context. "
                + context_rules +
                "static_only is usually an admin/authorized standalone entry: block unauthorized direct access, but do not disable intended admin access. "
                "vertical means role/privilege: block the attacking lower-privilege actor but keep authorized_roles working; do not make it owner-only. "
                "horizontal means ownership: compare the requested identity with the current user, while preserving any existing privileged-role bypass. "
                "If feedback says regression failed, the patch is too strict; relax it for the authorized role. "
                "Return exactly: missing_check, insertion_location, recommended_guard, reused_project_semantics, reason.\n\n"
                + json.dumps(payload, ensure_ascii=False, indent=2)
            ),
        },
    ]


def _stage2_messages(
    finding: Finding,
    source_relative: str,
    source_code: str,
    snippets: list[dict[str, Any]],
    plan: dict[str, Any],
    user_table_context: dict[str, Any] | None = None,
    identity_context: dict[str, Any] | None = None,
    page_guidance: dict[str, Any] | None = None,
    feedback: list[str] | None = None,
    vector: AttackVector | None = None,
) -> list[dict[str, str]]:
    payload = {
        "source_path": source_relative,
        "page_type": _page_type(finding.category),
        "vulnerability_type": _vulnerability_type(finding.category),
        "category": finding.category,
        "repair_goal": _repair_goal(finding.category),
        "authorized_roles": list(vector.authorized_roles) if vector else [],
        "identity_parameters": list(vector.identity_parameters) if vector else [],
        "stage1_plan": plan,
        "source_code": source_code,
        "validated_access_control_snippets": snippets,
        "previous_attempt_feedback": feedback or [],
    }
    context_rules = ""
    if identity_context:
        payload["identity_binding_context"] = identity_context
        context_rules += "4) Use identity_binding_context as the source of truth for current-user expressions, target lookup parameters, owner columns, and privileged bypasses. "
    if user_table_context:
        payload["database_user_table_context"] = user_table_context
        context_rules += "5) Use database_user_table_context only to choose real user ids, usernames, and role/rank fields; do not invent other database fields. "
    if page_guidance:
        payload["page_repair_guidance"] = page_guidance
        context_rules += "6) Follow page_repair_guidance exactly when it is present; it is application-specific ground truth for this repair item. "
    return [
        {
            "role": "system",
            "content": (
                "Generate a minimal source-code access-control patch. Reuse project guard semantics exactly. "
                "Unauthorized requests must be blocked before sensitive operations. "
                "Do not refactor unrelated code. Return only JSON, no Markdown."
            ),
        },
        {
            "role": "user",
            "content": (
                "Generate the complete patched source file from stage1_plan. Hard rules: "
                "1) Preserve business logic and existing includes. "
                "2) Use the app's actual auth sentinel, role/owner variables, and redirect/deny style from snippets. "
                "3) Only use guard variables/functions that are initialized in the target source or its included context; if needed, add the correct existing include before the guard. "
                + context_rules +
                "After denying access, exit immediately. "
                "Place the denial guard before protected content is returned or before a protected state-changing operation is executed. "
                "Use the target language's normal safe comparison style, and handle missing or unauthenticated users cleanly. "
                "For static_only fixes, block unauthorized direct access while preserving intended admin/authorized access; do not blindly disable the page. "
                "For vertical fixes, never block the authorized higher-privilege role; if an owner check is needed, add an existing admin/privileged bypass. "
                "For horizontal fixes, block cross-user access but preserve owner and existing privileged-role access. "
                "If feedback says regression failed or authorized response had denial, the guard is too strict; allow the authorized role. "
                "Return exactly: patched_source, explanation.\n\n"
                + json.dumps(payload, ensure_ascii=False, indent=2)
            ),
        },
    ]


def _repair_with_llm(
    config: PipelineConfig,
    finding: Finding,
    source: Path,
    source_relative: str,
    source_code: str,
    source_context: dict[str, Any] | None,
    metrics: dict[str, Any] | None = None,
    attempt: int = 1,
    feedback: list[str] | None = None,
    vector: AttackVector | None = None,
) -> tuple[str, dict[str, Any], Path]:
    llm = dict(config.repair.get("llm", {}))
    snippets = _snippet_context(source_relative, source_context)
    user_table_context = _repair_user_table_context(config)
    identity_context = _repair_identity_context(config, source_relative, vector)
    page_guidance = _repair_page_guidance(config, finding, vector)
    stage1_messages = _stage1_messages(finding, source_relative, source_code, snippets, user_table_context, identity_context, page_guidance, feedback, vector)
    stage1_raw = _chat_completion(llm, stage1_messages, metrics)
    plan = _json_from_model(stage1_raw)
    stage2_messages = _stage2_messages(finding, source_relative, source_code, snippets, plan, user_table_context, identity_context, page_guidance, feedback, vector)
    stage2_raw = _chat_completion(llm, stage2_messages, metrics)
    patch = _json_from_model(stage2_raw)
    patched_source = str(patch.get("patched_source", ""))
    if not patched_source.strip():
        raise ValueError("LLM response did not contain patched_source")
    if config.target.language == "php" and "<?php" not in patched_source[:5000]:
        raise ValueError("LLM patched_source does not look like a PHP file")

    prompt_dir = config.run_dir / "repair" / "prompts"
    digest = hashlib.sha256(f"{finding.category}\0{finding.page}\0{attempt}".encode("utf-8")).hexdigest()[:12]
    artifact = prompt_dir / f"{source.stem}-attempt{attempt}-{digest}.json"
    write_json(artifact, {
        "finding": finding.to_dict(),
        "source": str(source),
        "source_relative": source_relative,
        "attempt": attempt,
        "feedback": feedback or [],
        "snippets": snippets,
        "database_user_table_context": user_table_context,
        "identity_binding_context": identity_context,
        "page_repair_guidance": page_guidance,
        "stage1_messages": stage1_messages,
        "stage1_response": stage1_raw,
        "stage1_plan": plan,
        "stage2_messages": stage2_messages,
        "stage2_response": stage2_raw,
        "stage2_patch": {key: value for key, value in patch.items() if key != "patched_source"},
    })
    return patched_source, plan, artifact


def _llm_enabled(config: PipelineConfig) -> bool:
    llm = dict(config.repair.get("llm", {}))
    return bool(llm.get("enabled", False) and _secret(llm.get("api_key")))


def _validation_options(config: PipelineConfig) -> dict[str, Any]:
    return dict(config.repair.get("validation", {}))



def _java_validation_enabled(config: PipelineConfig) -> bool:
    return config.target.language in {"java", "jsp"}


def _java_web_root(config: PipelineConfig) -> Path:
    return config.target.source_root.resolve()


def _java_classes_dir(config: PipelineConfig) -> Path:
    options = _validation_options(config)
    configured = options.get("classes_dir") or options.get("java_classes_dir")
    if configured:
        candidate = Path(str(configured)).expanduser()
        return candidate.resolve() if candidate.is_absolute() else (_java_web_root(config) / candidate).resolve()
    return (_java_web_root(config) / "WEB-INF" / "classes").resolve()


def _java_tomcat_home(config: PipelineConfig) -> Path | None:
    options = _validation_options(config)
    configured = options.get("tomcat_home")
    if configured:
        return Path(str(configured)).expanduser().resolve()
    root = _java_web_root(config)
    if root.parent.name.lower() == "webapps":
        return root.parent.parent.resolve()
    return None


def _expand_java_classpath_entry(config: PipelineConfig, value: str) -> list[str]:
    root = _java_web_root(config)
    entry = Path(value).expanduser()
    if not entry.is_absolute():
        entry = root / entry
    text = str(entry)
    if any(char in text for char in "*?"):
        return [str(Path(item).resolve()) for item in sorted(glob.glob(text))]
    return [str(entry.resolve())]


def _java_classpath(config: PipelineConfig) -> str:
    options = _validation_options(config)
    entries: list[str] = [str(_java_classes_dir(config))]
    tomcat_home = _java_tomcat_home(config)
    if tomcat_home:
        servlet_api = tomcat_home / "lib" / "servlet-api.jar"
        if servlet_api.is_file():
            entries.append(str(servlet_api.resolve()))
    lib_dir = _java_web_root(config) / "WEB-INF" / "lib"
    if lib_dir.is_dir():
        entries.extend(str(path.resolve()) for path in sorted(lib_dir.glob("*.jar")))
    for raw in options.get("classpath", []) or options.get("java_classpath", []) or []:
        entries.extend(_expand_java_classpath_entry(config, str(raw)))
    return os.pathsep.join(list(dict.fromkeys(entries)))


def _java_source_package(source: Path) -> str:
    try:
        text = source.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    match = re.search(r"(?m)^\s*package\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*;", text)
    return match.group(1) if match else ""


def _java_class_glob(config: PipelineConfig, source: Path) -> str:
    package = _java_source_package(source)
    package_dir = Path(*package.split(".")) if package else Path()
    return str((_java_classes_dir(config) / package_dir / f"{source.stem}*.class").resolve())


def _java_class_files(config: PipelineConfig, source: Path) -> list[Path]:
    package = _java_source_package(source)
    package_dir = Path(*package.split(".")) if package else Path()
    class_dir = _java_classes_dir(config) / package_dir
    return sorted(class_dir.glob(f"{source.stem}*.class")) if class_dir.is_dir() else []


def _java_compile(config: PipelineConfig, source: Path, destination: Path) -> tuple[bool, str]:
    options = _validation_options(config)
    javac = str(options.get("javac") or options.get("java_compiler") or "javac")
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        javac,
        "-encoding",
        str(options.get("encoding", "UTF-8")),
        "-cp",
        _java_classpath(config),
        "-d",
        str(destination),
        str(source),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=float(options.get("syntax_timeout", 30)),
        )
    except FileNotFoundError:
        return False, f"javac was not found: {javac}"
    except Exception as exc:
        return False, f"javac failed to run: {type(exc).__name__}: {exc}"
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode == 0, output or f"javac exited with {completed.returncode}"


def _java_resolve_path(config: PipelineConfig, value: Any, base: Path | None = None) -> Path:
    path = Path(str(value)).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((base or _java_web_root(config)) / path).resolve()


def _java_compile_workdir(config: PipelineConfig, source: Path) -> Path:
    options = _validation_options(config)
    configured = options.get("compile_workdir") or options.get("java_compile_workdir")
    if configured:
        return _java_resolve_path(config, configured)
    return source.parent.resolve()


def _java_compile_source_files(config: PipelineConfig, source: Path, workdir: Path) -> list[Path]:
    options = _validation_options(config)
    patterns = options.get("compile_sources") or options.get("java_compile_sources")
    if not patterns:
        patterns = [str(source)]
    result: list[Path] = []
    for raw in patterns:
        pattern = str(raw)
        candidate = Path(pattern)
        search_pattern = str(candidate if candidate.is_absolute() else workdir / candidate)
        matched = sorted(Path(item).resolve() for item in glob.glob(search_pattern))
        if matched:
            result.extend(path for path in matched if path.is_file())
        else:
            resolved = candidate.resolve() if candidate.is_absolute() else (workdir / candidate).resolve()
            if resolved.is_file():
                result.append(resolved)
    return list(dict.fromkeys(result))


def _java_compile_sources(config: PipelineConfig, source: Path, destination: Path) -> tuple[bool, str]:
    options = _validation_options(config)
    javac = str(options.get("javac") or options.get("java_compiler") or "javac")
    workdir = _java_compile_workdir(config, source)
    sources = _java_compile_source_files(config, source, workdir)
    if not sources:
        return False, f"no Java source files matched in {workdir}"
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        javac,
        "-encoding",
        str(options.get("encoding", "UTF-8")),
        "-cp",
        _java_classpath(config),
        "-d",
        str(destination),
        *[str(item) for item in sources],
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=float(options.get("compile_timeout", options.get("syntax_timeout", 30))),
        )
    except FileNotFoundError:
        return False, f"javac was not found: {javac}"
    except Exception as exc:
        return False, f"javac failed to run: {type(exc).__name__}: {exc}"
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode == 0, output or f"javac exited with {completed.returncode}; compiled {len(sources)} source files"


def _java_class_tree_backups(config: PipelineConfig) -> dict[Path, bytes | None]:
    classes_dir = _java_classes_dir(config)
    if not classes_dir.is_dir():
        return {}
    return {path: path.read_bytes() for path in sorted(classes_dir.rglob("*.class")) if path.is_file()}


def _tomcat_context_path(config: PipelineConfig) -> str:
    options = _validation_options(config)
    configured = options.get("context_path") or options.get("tomcat_context_path")
    if configured:
        text = str(configured).strip()
        return text if text.startswith("/") else "/" + text
    from urllib.parse import urlsplit

    path = urlsplit(config.target.base_url).path.strip("/")
    first = path.split("/", 1)[0] if path else _java_web_root(config).name
    return "/" + first if first else ""


def _reload_java_webapp(config: PipelineConfig) -> tuple[bool, str]:
    if not _java_validation_enabled(config):
        return True, "reload not required for non-Java target"
    options = _validation_options(config)
    strategy = str(options.get("reload_strategy") or options.get("tomcat_reload") or "touch_web_xml").lower()
    wait = float(options.get("reload_wait", 2.0))
    if strategy in {"none", "disabled", "false"}:
        return True, "Tomcat reload disabled by configuration"
    if strategy in {"manager", "tomcat_manager"}:
        manager_url = str(options.get("manager_url") or options.get("tomcat_manager_url") or "").rstrip("/")
        username = options.get("manager_username") or options.get("tomcat_manager_username")
        password = options.get("manager_password") or options.get("tomcat_manager_password")
        if not manager_url:
            return False, "Tomcat manager reload requested but manager_url is not configured"
        url = manager_url + "/text/reload"
        try:
            response = requests.get(
                url,
                params={"path": _tomcat_context_path(config)},
                auth=(str(username), str(password)) if username is not None or password is not None else None,
                timeout=float(options.get("reload_timeout", 30)),
            )
            ok = response.status_code < 400 and response.text.strip().upper().startswith("OK")
            time.sleep(wait)
            return ok, f"Tomcat manager reload HTTP {response.status_code}: {response.text.strip()[:300]}"
        except Exception as exc:
            return False, f"Tomcat manager reload failed: {type(exc).__name__}: {exc}"
    if strategy in {"command", "restart_command"}:
        command = options.get("restart_command") or options.get("reload_command")
        if not command:
            return False, "command reload requested but restart_command/reload_command is not configured"
        try:
            if isinstance(command, list):
                completed = subprocess.run([str(item) for item in command], capture_output=True, text=True, timeout=float(options.get("reload_timeout", 60)))
            else:
                completed = subprocess.run(str(command), capture_output=True, text=True, timeout=float(options.get("reload_timeout", 60)), shell=True)
            output = (completed.stdout + "\n" + completed.stderr).strip()
            time.sleep(wait)
            return completed.returncode == 0, output or f"reload command exited with {completed.returncode}"
        except Exception as exc:
            return False, f"reload command failed: {type(exc).__name__}: {exc}"
    web_xml = _java_web_root(config) / "WEB-INF" / "web.xml"
    try:
        if web_xml.is_file():
            os.utime(web_xml, None)
            time.sleep(wait)
            return True, f"touched {web_xml}"
        marker = _java_web_root(config) / "WEB-INF" / ".drhl-reload"
        marker.write_text(str(time.time()), encoding="utf-8")
        time.sleep(wait)
        return True, f"touched {marker}"
    except Exception as exc:
        return False, f"touch_web_xml reload failed: {type(exc).__name__}: {exc}"


def _compile_and_reload_java_patch(config: PipelineConfig, source: Path) -> tuple[bool, str, dict[Path, bytes | None]]:
    options = _validation_options(config)
    strategy = str(
        options.get("deployment_strategy")
        or options.get("java_deployment_strategy")
        or "single_class"
    ).lower()
    if strategy in {"bulk", "bulk_compile", "source_tree", "compile_sources"}:
        backups = _java_class_tree_backups(config)
        ok, compile_message = _java_compile_sources(config, source, _java_classes_dir(config))
        for path in sorted(_java_classes_dir(config).rglob("*.class")) if _java_classes_dir(config).is_dir() else []:
            backups.setdefault(path, None)
    else:
        before_files = _java_class_files(config, source)
        backups = {path: path.read_bytes() for path in before_files}
        ok, compile_message = _java_compile(config, source, _java_classes_dir(config))
        after_files = _java_class_files(config, source)
        for path in after_files:
            backups.setdefault(path, path.read_bytes() if path in before_files else None)
    if not ok:
        _restore_java_classes(backups)
        return False, f"javac=({compile_message})", backups
    reload_ok, reload_message = _reload_java_webapp(config)
    if not reload_ok:
        _restore_java_classes(backups)
        return False, f"javac=({compile_message}); reload=({reload_message})", backups
    return True, f"javac=({compile_message}); reload=({reload_message})", backups


def _restore_java_classes(backups: dict[Path, bytes | None]) -> None:
    for path, data in backups.items():
        if data is None:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


def _repair_output_relative(config: PipelineConfig, path: Path) -> Path | None:
    output_root = config.run_dir / str(config.repair.get("output_dir", "repair/files"))
    try:
        relative = path.resolve().relative_to(output_root.resolve())
    except ValueError:
        return None
    parts = list(relative.parts)
    if parts and parts[0].startswith("attempt-"):
        parts = parts[1:]
    return Path(*parts) if parts else None


def _go_syntax_check(config: PipelineConfig, path: Path) -> tuple[bool, str]:
    options = _validation_options(config)
    go_binary = str(options.get("go_binary") or options.get("compiler") or "go")
    gofmt_binary = str(options.get("gofmt_binary") or "gofmt")
    timeout = float(options.get("syntax_timeout", 60))
    relative = _repair_output_relative(config, path)

    if relative is None:
        try:
            completed = subprocess.run([gofmt_binary, "-w", str(path)], capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError:
            return False, f"gofmt binary was not found: {gofmt_binary}"
        except Exception as exc:
            return False, f"gofmt failed to run: {type(exc).__name__}: {exc}"
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return completed.returncode == 0, output or f"gofmt exited with {completed.returncode}"

    source_root = config.target.source_root.resolve()
    source_file = (source_root / relative).resolve()
    try:
        source_file.relative_to(source_root)
    except ValueError:
        return False, f"patched Go file is outside source root: {relative.as_posix()}"
    if not source_file.is_file():
        return False, f"original Go source file was not found: {relative.as_posix()}"

    ignore = shutil.ignore_patterns(".git", ".idea", ".vscode", "tmp", "coverage", "coverage_report", "node_modules")
    with tempfile.TemporaryDirectory(prefix="drhl-go-compile-") as temporary:
        temp_root = Path(temporary) / "src"
        try:
            shutil.copytree(source_root, temp_root, ignore=ignore)
        except Exception as exc:
            return False, f"failed to copy Go source tree: {type(exc).__name__}: {exc}"
        temp_file = (temp_root / relative).resolve()
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_bytes(path.read_bytes())

        try:
            fmt = subprocess.run([gofmt_binary, "-w", str(temp_file)], capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError:
            return False, f"gofmt binary was not found: {gofmt_binary}"
        except Exception as exc:
            return False, f"gofmt failed to run: {type(exc).__name__}: {exc}"
        fmt_output = (fmt.stdout + "\n" + fmt.stderr).strip()
        if fmt.returncode != 0:
            return False, fmt_output or f"gofmt exited with {fmt.returncode}"

        default_package = "." if str(relative.parent) == "." else "./" + relative.parent.as_posix()
        args = options.get("go_test_args") or ["test", default_package, "-run", "^$"]
        if isinstance(args, str):
            args = args.split()
        args = [str(item).replace("{package}", default_package).replace("{file}", relative.as_posix()) for item in args]
        command = [go_binary, *args[1:]] if args and Path(args[0]).name.lower() == Path(go_binary).name.lower() else [go_binary, *args]
        env = os.environ.copy()
        go_cache = Path(temporary) / "gocache"
        go_cache.mkdir(parents=True, exist_ok=True)
        env["GOCACHE"] = str(go_cache)
        try:
            completed = subprocess.run(command, cwd=str(temp_root), capture_output=True, text=True, timeout=timeout, env=env)
        except FileNotFoundError:
            return False, f"Go binary was not found: {go_binary}"
        except Exception as exc:
            return False, f"go compile check failed to run: {type(exc).__name__}: {exc}"
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return completed.returncode == 0, output or f"{' '.join(command)} exited with {completed.returncode}"

def _syntax_check(config: PipelineConfig, path: Path) -> tuple[bool, str]:
    options = _validation_options(config)
    if not bool(options.get("syntax_check", True)):
        return True, "syntax check disabled by configuration"
    if config.target.language == "php":
        php_binary = str(options.get("php_binary") or options.get("compiler") or "php")
        try:
            completed = subprocess.run(
                [php_binary, "-l", str(path)],
                capture_output=True,
                text=True,
                timeout=float(options.get("syntax_timeout", 30)),
            )
        except FileNotFoundError:
            return False, f"PHP binary was not found: {php_binary}"
        except Exception as exc:
            return False, f"syntax check failed to run: {type(exc).__name__}: {exc}"
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return completed.returncode == 0, output or f"php -l exited with {completed.returncode}"
    if config.target.language == "python":
        python_binary = str(options.get("python_binary") or options.get("compiler") or sys.executable)
        try:
            completed = subprocess.run(
                [python_binary, "-m", "py_compile", str(path)],
                capture_output=True,
                text=True,
                timeout=float(options.get("syntax_timeout", 30)),
            )
        except FileNotFoundError:
            return False, f"Python binary was not found: {python_binary}"
        except Exception as exc:
            return False, f"syntax check failed to run: {type(exc).__name__}: {exc}"
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return completed.returncode == 0, output or f"py_compile exited with {completed.returncode}"
    if config.target.language == "go":
        return _go_syntax_check(config, path)
    if _java_validation_enabled(config):
        with tempfile.TemporaryDirectory(prefix="drhl-javac-") as temporary:
            ok, output = _java_compile(config, path, Path(temporary))
            return ok, output
    return False, f"syntax check is not implemented for language {config.target.language!r}"



def _authorized_success_redirect(config: PipelineConfig, detector: Any, response: Any, vector: AttackVector) -> bool:
    if vector.request.method.upper() == "GET" or not (300 <= response.status_code < 400):
        return False
    location = detector._redirect_location(response)
    if not location:
        return False
    from urllib.parse import urlsplit

    base = config.target.base_url.rstrip("/") + "/"
    candidates = [location]
    if location.startswith(base):
        candidates.append(location[len(base):])
    parsed = urlsplit(location)
    path = parsed.path.lstrip("/")
    scope = urlsplit(base).path.strip("/")
    if scope and path.startswith(scope + "/"):
        path = path[len(scope) + 1:]
    if path:
        candidates.append(path + (("?" + parsed.query) if parsed.query else ""))
    oracle = dict(config.analysis.get("oracle", {}))
    patterns = [
        *oracle.get("authorized_success_redirect_patterns", []),
        *oracle.get("public_page_patterns", []),
    ]
    return any(re.search(str(pattern), candidate, re.I) for pattern in patterns for candidate in candidates)


def _authorized_regression_passed(
    config: PipelineConfig, snapshot: Snapshot | None, vector: AttackVector
) -> tuple[bool, str]:
    if vector.category == "static_only" or not vector.authorized_roles:
        return True, "regression is not applicable because the vector has no authorized role"
    if snapshot is None:
        return False, "database snapshot is unavailable for regression validation"
    from ..analysis.detector import ActiveDetector

    roles = {role.name: role for role in config.roles}
    authorized = _configured_regression_role(config, roles, vector)
    if authorized is None:
        authorized = next((roles[name] for name in vector.authorized_roles if name in roles), None)
    if authorized is None:
        return False, "authorized role is unavailable for regression validation"
    regression_page = _regression_page(vector)
    regression_request = _regression_request(vector, regression_page)
    detector = ActiveDetector(config, snapshot)
    try:
        session = detector._session(authorized)
        try:
            response = detector._send(session, regression_page, regression_request)
        finally:
            session.close()
        denial = detector._denial(response)
        success_redirect = _authorized_success_redirect(config, detector, response, vector)
        ok = (200 <= response.status_code < 400 and not denial) or success_redirect
        evidence = f"authorized status={response.status_code}; denial={denial}"
        if success_redirect:
            evidence += "; authorized success redirect accepted"
        return ok, evidence
    except Exception as exc:
        return False, f"regression validation error: {type(exc).__name__}: {exc}"
    finally:
        try:
            snapshot.restore()
        except Exception:
            pass


def _regression_page(vector: AttackVector) -> str:
    return (vector.page_overrides[0] if getattr(vector, "page_overrides", []) else vector.page)


def _regression_request(vector: AttackVector, page: str) -> RequestSpec:
    request = vector.request
    referer = page if request.referer == vector.page else request.referer
    return RequestSpec(request.method, dict(request.params), referer)


def _configured_regression_role(
    config: PipelineConfig,
    roles: dict[str, Any],
    vector: AttackVector,
) -> Any | None:
    options = _validation_options(config)
    rules = options.get("regression_roles") or options.get("regression_role_overrides") or []
    page_candidates: list[str] = []
    for page in [vector.page, *getattr(vector, "page_overrides", [])]:
        page_candidates.extend(_page_match_candidates(page))
    for item in rules:
        if not isinstance(item, dict):
            continue
        role_name = str(item.get("role") or item.get("name") or "")
        if not role_name or role_name not in roles:
            continue
        pattern = str(item.get("pattern") or "")
        exact = str(item.get("page") or "").lstrip("/").replace("\\", "/")
        if exact and any(exact == candidate for candidate in page_candidates):
            return roles[role_name]
        if pattern and any(re.search(pattern, candidate, re.I) for candidate in page_candidates):
            return roles[role_name]
    return None

def _run_validation_hook(options: dict[str, Any], *names: str) -> tuple[bool, str]:
    value: Any = None
    selected = names[0]
    for name in names:
        if options.get(name):
            value = options.get(name)
            selected = name
            break
    if not value:
        return True, "no validation hook configured"
    command = value
    cwd = None
    timeout = options.get("reload_timeout", options.get("hook_timeout", 60))
    if isinstance(value, dict):
        command = value.get("command") or value.get("args")
        cwd = value.get("cwd")
        timeout = value.get("timeout", timeout)
    if not isinstance(command, list) or not command:
        return False, f"repair.validation.{selected} must be a non-empty argument list or command object"
    try:
        completed = subprocess.run(
            [str(item) for item in command],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=float(timeout) if timeout else None,
            check=False,
        )
    except FileNotFoundError:
        return False, f"hook executable was not found: {command[0]}"
    except Exception as exc:
        return False, f"hook failed to run: {type(exc).__name__}: {exc}"
    output = (completed.stdout + "\n" + completed.stderr).strip()
    if completed.returncode != 0:
        return False, f"repair.validation.{selected} exited with {completed.returncode}: {output}"
    return True, output or f"repair.validation.{selected} completed"


def _runtime_validation(
    config: PipelineConfig,
    snapshot: Snapshot | None,
    source: Path,
    patched_source: str,
    vector: AttackVector | None,
) -> tuple[bool, bool, str]:
    options = _validation_options(config)
    if not bool(options.get("temporary_apply_to_source", False)):
        return False, False, "runtime validation disabled; set repair.validation.temporary_apply_to_source=true"
    if vector is None:
        return False, False, "attack vector is unavailable for runtime validation"
    if snapshot is None:
        return False, False, "database snapshot is unavailable for runtime validation"
    from ..analysis.detector import ActiveDetector

    original = source.read_bytes()
    class_backups: dict[Path, bytes | None] = {}
    apply_message = "source patch applied"
    java_reload_needed = False
    try:
        source.write_text(patched_source, encoding="utf-8")
        if _java_validation_enabled(config) and source.suffix.lower() == ".java":
            java_reload_needed = True
            compile_ok, apply_message, class_backups = _compile_and_reload_java_patch(config, source)
            if not compile_ok:
                return False, False, f"runtime Java deployment failed: {apply_message}"
        elif options.get("reload_command") or options.get("after_apply_command"):
            hook_ok, hook_message = _run_validation_hook(options, "reload_command", "after_apply_command")
            apply_message = f"{apply_message}; reload=({hook_message})"
            if not hook_ok:
                return False, False, f"runtime deployment hook failed: {hook_message}"
        detector = ActiveDetector(config, snapshot)
        exploit_findings = detector.run([vector])
        exploit_blocked = bool(exploit_findings) and all(item.status != "vulnerable" for item in exploit_findings)
        regression_passed, regression_message = _authorized_regression_passed(config, snapshot, vector)
        exploit_message = "; ".join(
            f"{item.actor}:{item.status}" for item in exploit_findings
        ) or "no exploit findings"
        return exploit_blocked, regression_passed, (
            f"deployment=({apply_message}); exploit=({exploit_message}); "
            f"regression=({regression_message})"
        )
    except Exception as exc:
        return False, False, f"runtime validation error: {type(exc).__name__}: {exc}"
    finally:
        try:
            source.write_bytes(original)
            if class_backups:
                _restore_java_classes(class_backups)
            if java_reload_needed:
                _reload_java_webapp(config)
            elif options.get("after_restore_command") or options.get("restore_command"):
                _run_validation_hook(options, "after_restore_command", "restore_command")
        finally:
            try:
                snapshot.restore()
            except Exception:
                pass


def _repair_summary(results: list[RepairResult]) -> dict[str, int]:
    successful_attempt_buckets = {1: 0, 2: 0, 3: 0}
    for item in results:
        for attempt in item.attempt_details:
            if attempt.successful:
                successful_attempt_buckets[attempt.attempt] = successful_attempt_buckets.get(attempt.attempt, 0) + 1
                break
    failed_patches = sum(
        1
        for item in results
        for attempt in item.attempt_details
        if attempt.output and not attempt.successful
    )
    return {
        "Repair Items": len(results),
        "Total Repair Attempts": sum(item.attempts for item in results),
        "Patch Generation Attempts": sum(len(item.attempt_details) for item in results),
        "Patches Generated": sum(item.patches_generated for item in results),
        "Failed Patches": failed_patches,
        "Syntax / Compile OK": sum(item.syntax_compile_ok for item in results),
        "Exploit Blocked": sum(item.exploit_blocked for item in results),
        "Regression Passed": sum(item.regression_passed for item in results),
        "Successful Repairs": sum(1 for item in results if item.successful),
        "Failed Repairs": sum(1 for item in results if not item.successful),
        "Successful on Attempt 1": successful_attempt_buckets.get(1, 0),
        "Successful on Attempt 2": successful_attempt_buckets.get(2, 0),
        "Successful on Attempt 3": successful_attempt_buckets.get(3, 0),
    }


def write_repair_report(results: list[RepairResult], output: Path) -> None:
    summary = _repair_summary(results)
    lines = [
        "# DRHL Repair Report",
        "",
        f"- Repair Items: {summary['Repair Items']}",
        f"- Total Repair Attempts: {summary['Total Repair Attempts']}",
        f"- Patch Generation Attempts: {summary['Patch Generation Attempts']}",
        f"- Patches Generated: {summary['Patches Generated']}",
        f"- Failed Patches: {summary['Failed Patches']}",
        f"- Syntax / Compile OK: {summary['Syntax / Compile OK']}",
        f"- Exploit Blocked: {summary['Exploit Blocked']}",
        f"- Regression Passed: {summary['Regression Passed']}",
        f"- Successful Repairs: {summary['Successful Repairs']}",
        f"- Failed Repairs: {summary['Failed Repairs']}",
        f"- Successful on Attempt 1: {summary['Successful on Attempt 1']}",
        f"- Successful on Attempt 2: {summary['Successful on Attempt 2']}",
        f"- Successful on Attempt 3: {summary['Successful on Attempt 3']}",
        "",
        "> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.",
        "> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.",
        "> A repair is counted as successful only when syntax/compile, exploit-blocking, and regression validation all pass for the same generated patch.",
        "> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.",
        "",
        "## Details",
        "",
    ]
    if not results:
        lines.extend(["No repair candidates were generated.", ""])
    for item in results:
        lines.extend([
            f"### `{item.page}`",
            "",
            f"- Category: {item.category}",
            f"- Status: {item.status}",
            f"- Attempts: {item.attempts}",
            f"- Patches Generated: {item.patches_generated}",
            f"- Failed Patches: {sum(1 for attempt in item.attempt_details if attempt.output and not attempt.successful)}",
            f"- Syntax / Compile OK: {item.syntax_compile_ok}",
            f"- Exploit Blocked: {item.exploit_blocked}",
            f"- Regression Passed: {item.regression_passed}",
            f"- Successful: {str(item.successful).lower()}",
            f"- Message: {item.message}",
            "",
        ])
        for attempt in item.attempt_details:
            lines.extend([
                f"  - Attempt {attempt.attempt}: syntax={attempt.syntax_compile_ok}, "
                f"exploit_blocked={attempt.exploit_blocked}, regression={attempt.regression_passed}, "
                f"successful={attempt.successful}",
                f"    - Message: {attempt.message}",
            ])
        lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def create_repairs(
    config: PipelineConfig,
    graph: dict[str, Any],
    findings: list[Finding],
    source_context: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    vectors: list[AttackVector] | None = None,
    snapshot: Snapshot | None = None,
) -> list[RepairResult]:
    output_root = config.run_dir / str(config.repair.get("output_dir", "repair/files"))
    source_map = dict(graph.get("source_map", {}))
    vector_lookup: dict[tuple[str, str], AttackVector] = {}
    for vector in vectors or []:
        for page_candidate in [vector.page, *getattr(vector, "page_overrides", [])]:
            for match_candidate in _page_match_candidates(page_candidate):
                vector_lookup[(vector.category, match_candidate)] = vector
    results: list[RepairResult] = []
    processed: set[tuple[str, str]] = set()
    validation = _validation_options(config)
    max_attempts = max(1, int(validation.get("max_attempts", 3)))

    for finding in findings:
        if finding.status != "vulnerable":
            continue
        key = (finding.category, finding.page)
        if key in processed:
            continue
        processed.add(key)
        source_name = _repair_source_name(config, source_map, finding.page)
        source = _safe_source(config.target.source_root, source_name) if source_name else None
        if source is None:
            results.append(RepairResult(finding.category, finding.page, None, None, "manual", "source mapping was not found"))
            continue
        if not _llm_enabled(config):
            results.append(RepairResult(
                finding.category,
                finding.page,
                str(source),
                None,
                "manual",
                "LLM repair is not enabled or repair.llm.api_key is missing",
                engine="llm",
            ))
            continue

        relative = source.relative_to(config.target.source_root.resolve())
        source_relative = relative.as_posix()
        vector = None
        for match_candidate in _page_match_candidates(finding.page):
            vector = vector_lookup.get((finding.category, match_candidate))
            if vector is not None:
                break
        attempts: list[RepairAttempt] = []
        feedback: list[str] = []
        final_output: Path | None = None
        final_plan: dict[str, Any] | None = None
        final_prompt: Path | None = None
        status = "repair_failed"
        message = "repair failed after maximum attempts"
        original_source_bytes = source.read_bytes()

        for attempt_number in range(1, max_attempts + 1):
            try:
                original = source.read_text(encoding="utf-8", errors="strict")
                patched, plan, prompt_artifact = _repair_with_llm(
                    config,
                    finding,
                    source,
                    source_relative,
                    original,
                    source_context,
                    metrics,
                    attempt=attempt_number,
                    feedback=feedback,
                    vector=vector,
                )
                output = output_root / f"attempt-{attempt_number}" / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(patched, encoding="utf-8")
                syntax_ok, syntax_message = _syntax_check(config, output)
                if syntax_ok:
                    exploit_ok, regression_ok, runtime_message = _runtime_validation(
                        config, snapshot, source, patched, vector
                    )
                else:
                    exploit_ok, regression_ok = False, False
                    runtime_message = "runtime validation skipped because syntax/compile failed"
                successful = syntax_ok and exploit_ok and regression_ok
                attempt_message = f"syntax=({syntax_message}); {runtime_message}"
                attempts.append(RepairAttempt(
                    attempt=attempt_number,
                    output=str(output),
                    syntax_compile_ok=syntax_ok,
                    exploit_blocked=exploit_ok,
                    regression_passed=regression_ok,
                    successful=successful,
                    message=attempt_message,
                    prompt_artifact=str(prompt_artifact),
                    plan=json.dumps(plan, ensure_ascii=False),
                ))
                final_output = output
                final_plan = plan
                final_prompt = prompt_artifact
                if successful:
                    status = "successful_repair"
                    message = "syntax/compile, exploit blocking, and regression validation all passed"
                    break
                feedback.append(attempt_message)
            except Exception as exc:
                attempt_message = f"attempt error: {type(exc).__name__}: {exc}"
                attempts.append(RepairAttempt(
                    attempt=attempt_number,
                    output=None,
                    syntax_compile_ok=False,
                    exploit_blocked=False,
                    regression_passed=False,
                    successful=False,
                    message=attempt_message,
                ))
                feedback.append(attempt_message)

        try:
            if source.read_bytes() != original_source_bytes:
                source.write_bytes(original_source_bytes)
        except Exception as exc:
            message = f"{message}; warning: failed to restore original source after repair validation: {type(exc).__name__}: {exc}"

        validation_artifact = config.run_dir / "repair" / "validation" / f"{source.stem}-{hashlib.sha256(finding.page.encode('utf-8')).hexdigest()[:12]}.json"
        result = RepairResult(
            finding.category,
            finding.page,
            str(source),
            str(final_output) if final_output else None,
            status,
            message,
            engine="llm",
            plan=json.dumps(final_plan, ensure_ascii=False) if final_plan else None,
            prompt_artifact=str(final_prompt) if final_prompt else None,
            attempts=len(attempts),
            patches_generated=sum(1 for attempt in attempts if attempt.output),
            syntax_compile_ok=sum(1 for attempt in attempts if attempt.syntax_compile_ok),
            exploit_blocked=sum(1 for attempt in attempts if attempt.exploit_blocked),
            regression_passed=sum(1 for attempt in attempts if attempt.regression_passed),
            successful=any(attempt.successful for attempt in attempts),
            validation_artifact=str(validation_artifact),
            attempt_details=attempts,
        )
        write_json(validation_artifact, asdict(result))
        results.append(result)
    return results


def serialize_repairs(results: list[RepairResult]) -> dict[str, Any]:
    return {"summary": _repair_summary(results), "repairs": [asdict(result) for result in results]}





