from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import secrets
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
from ..io import write_json
from ..models import AttackVector, Finding, RequestSpec
from ..progress import progress
from ..snippet_compaction import compact_snippets


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
    database_validation_passed: bool = True
    database_validation: dict[str, Any] = field(default_factory=dict)


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
    database_validation_applied: int = 0
    database_validation_passed: int = 0
    successful: bool = False
    validation_artifact: str | None = None
    attempt_details: list[RepairAttempt] = field(default_factory=list)
    coverage: dict[str, Any] | None = None


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


def _vector_operation(vector: AttackVector) -> str:
    for name in ("action", "operation", "do", "mode"):
        value = vector.request.params.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return vector.request.method.upper()


def _vector_summary(vector: AttackVector) -> dict[str, Any]:
    params = {
        str(name): (
            "<redacted>"
            if re.search(r"pass(word)?|secret|csrf|token|api[_-]?key", str(name), re.I)
            else value
        )
        for name, value in vector.request.params.items()
    }
    return {
        "operation": _vector_operation(vector),
        "method": vector.request.method,
        "page": vector.page,
        "page_overrides": list(vector.page_overrides),
        "params": params,
        "referer": vector.request.referer,
    }


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
    configured = _configured_source_override(config, page)
    if configured:
        return configured
    for candidate in _page_match_candidates(page):
        mapped = source_map.get(candidate)
        if mapped:
            return str(mapped)
    return None

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



def _snippet_context(source_relative: str, source_context: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not source_context:
        return []
    snippets = list(source_context.get("snippets", []))
    related = [item for item in snippets if item.get("path") == source_relative]
    compact_format = bool(snippets) and all(
        isinstance(item, dict)
        and set(item).issubset({"path", "code", "if_framework"})
        for item in snippets
    )
    if compact_format:
        reusable = [item for item in snippets if item.get("path") != source_relative]
    else:
        reusable = [
            item for item in snippets
            if item.get("kind") in {
                "validation_function",
                "guard_call",
                "condition",
                "conditional",
                "database_operation",
            }
            and item.get("path") != source_relative
        ]

    has_scored_snippets = any("access_control_score" in item for item in related + reusable)

    if not has_scored_snippets:
        def priority(item: dict[str, Any]) -> tuple[int, int]:
            text = " ".join(
                str(item.get(key, ""))
                for key in ("kind", "function", "condition", "code", "if_framework")
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
        return compact_snippets(result[:80])

    def priority(item: dict[str, Any]) -> tuple[int, int]:
        text = " ".join(
            str(item.get(key, ""))
            for key in ("kind", "function", "condition", "code", "if_framework", "context_code")
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
    return compact_snippets(result[:60])


def _stage1_messages(
    finding: Finding,
    source_relative: str,
    source_code: str,
    snippets: list[dict[str, Any]],
    feedback: list[str] | None = None,
    vector: AttackVector | None = None,
    vectors: list[AttackVector] | None = None,
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
    if vectors and len(vectors) > 1:
        payload["attack_variants"] = [_vector_summary(item) for item in vectors]
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
    feedback: list[str] | None = None,
    vector: AttackVector | None = None,
    vectors: list[AttackVector] | None = None,
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
    if vectors and len(vectors) > 1:
        payload["attack_variants"] = [_vector_summary(item) for item in vectors]
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
                "4) In PHP, if the patch reads $_SESSION, ensure session_start() has already run; otherwise reuse or add that initialization before the guard. "
                "5) Prefer an existing denial redirect from the validated snippets followed by exit over a bare exit or die. "
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
    vectors: list[AttackVector] | None = None,
) -> tuple[str, dict[str, Any], Path]:
    llm = dict(config.repair.get("llm", {}))
    snippets = _snippet_context(source_relative, source_context)
    stage1_messages = _stage1_messages(
        finding, source_relative, source_code, snippets, feedback, vector, vectors
    )
    stage1_raw = _chat_completion(llm, stage1_messages, metrics)
    plan = _json_from_model(stage1_raw)
    stage2_messages = _stage2_messages(
        finding, source_relative, source_code, snippets, plan, feedback, vector, vectors
    )
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
    if _java_validation_enabled(config) and path.suffix.lower() == ".jsp":
        return True, "JSP syntax/compile validation deferred to Tomcat/Jasper runtime request"
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
    if _java_validation_enabled(config) and path.suffix.lower() == ".java":
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
        oracle_role_names = {
            str(rule.get("authorized", {}).get("role") or "").strip()
            for rule in _database_oracle_rules(config, vector)
            if isinstance(rule.get("authorized"), dict)
        }
        oracle_role_names.discard("")
        if len(oracle_role_names) == 1:
            authorized = roles.get(next(iter(oracle_role_names)))
    if authorized is None:
        authorized = next((roles[name] for name in vector.authorized_roles if name in roles), None)
    if authorized is None:
        return False, "authorized role is unavailable for regression validation"
    regression_page = _regression_page(vector)
    regression_request = _regression_request(config, vector, regression_page)
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


def _regression_request(
    config: PipelineConfig, vector: AttackVector, page: str
) -> RequestSpec:
    request = vector.request
    referer = page if request.referer == vector.page else request.referer
    params = dict(request.params)
    if vector.category == "horizontal":
        horizontal_overrides = config.analysis.get("horizontal_overrides", {})
        if isinstance(horizontal_overrides, dict):
            for name in vector.identity_parameters:
                if name not in horizontal_overrides:
                    continue
                value = horizontal_overrides[name]
                if isinstance(value, list):
                    if not value:
                        continue
                    value = value[0]
                params[name] = value
    return RequestSpec(request.method, params, referer)


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


_ORACLE_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _database_oracle_rules(config: PipelineConfig, vector: AttackVector) -> list[dict[str, Any]]:
    """Return repair-only database/content oracle rules matching *vector*."""
    raw_rules = _validation_options(config).get("database_oracles", [])
    if isinstance(raw_rules, dict):
        raw_rules = raw_rules.get("rules", [])
    if not isinstance(raw_rules, list):
        return []
    candidates: list[str] = []
    for page in [vector.page, *getattr(vector, "page_overrides", [])]:
        candidates.extend(_page_match_candidates(page))
    result: list[dict[str, Any]] = []
    for raw in raw_rules:
        if not isinstance(raw, dict):
            continue
        category = str(raw.get("category") or "").strip()
        if category and category != vector.category:
            continue
        exact = str(raw.get("page") or "").lstrip("/").replace("\\", "/")
        pattern = str(raw.get("page_pattern") or raw.get("pattern") or "").strip()
        if exact and exact not in candidates:
            continue
        if pattern and not any(re.search(pattern, candidate, re.I) for candidate in candidates):
            continue
        if not exact and not pattern:
            continue
        result.append(dict(raw))
    return result


def _database_oracle_is_response_only(config: PipelineConfig, vector: AttackVector) -> bool:
    """Return whether *vector* intentionally skips database validation."""
    raw = _validation_options(config).get("database_oracles", {})
    if not isinstance(raw, dict):
        return False
    patterns = raw.get("response_only_patterns", [])
    if not isinstance(patterns, list):
        return False
    candidates: list[str] = []
    for page in [vector.page, *getattr(vector, "page_overrides", [])]:
        candidates.extend(_page_match_candidates(page))
    return any(
        isinstance(pattern, str)
        and pattern
        and any(re.search(pattern, candidate, re.I) for candidate in candidates)
        for pattern in patterns
    )


def _database_oracle_is_primary(config: PipelineConfig, vector: AttackVector) -> bool:
    """Return whether a matched database oracle is authoritative for *vector*."""
    raw = _validation_options(config).get("database_oracles", {})
    if not isinstance(raw, dict):
        return False
    patterns = raw.get("database_primary_patterns", [])
    if not isinstance(patterns, list):
        return False
    candidates: list[str] = []
    for page in [vector.page, *getattr(vector, "page_overrides", [])]:
        candidates.extend(_page_match_candidates(page))
    return any(
        isinstance(pattern, str)
        and pattern
        and any(re.search(pattern, candidate, re.I) for candidate in candidates)
        for pattern in patterns
    )


def _repair_finding_is_skipped(config: PipelineConfig, finding: Finding) -> tuple[bool, str]:
    """Match a repair-only exclusion without changing detection findings."""
    raw_rules = config.repair.get("skip_findings", [])
    if isinstance(raw_rules, dict):
        raw_rules = [raw_rules]
    if not isinstance(raw_rules, list):
        return False, ""
    candidates = _page_match_candidates(finding.page)
    for raw in raw_rules:
        if not isinstance(raw, dict):
            continue
        category = str(raw.get("category") or "").strip()
        if category and category != finding.category:
            continue
        exact = str(raw.get("page") or "").lstrip("/").replace("\\", "/")
        pattern = str(raw.get("page_pattern") or raw.get("pattern") or "").strip()
        if exact and exact not in candidates:
            continue
        if pattern and not any(re.search(pattern, candidate, re.I) for candidate in candidates):
            continue
        if not exact and not pattern:
            continue
        reason = str(raw.get("reason") or "matched repair.skip_findings").strip()
        return True, reason
    return False, ""


def _render_oracle_value(value: Any, context: dict[str, str]) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in context:
                raise ValueError(f"database oracle placeholder is undefined: {name}")
            return context[name]

        return _ORACLE_PLACEHOLDER.sub(replace, value)
    if isinstance(value, list):
        return [_render_oracle_value(item, context) for item in value]
    if isinstance(value, dict):
        return {
            str(_render_oracle_value(str(key), context)): _render_oracle_value(item, context)
            for key, item in value.items()
        }
    return value


def _oracle_context(rule: dict[str, Any]) -> dict[str, str]:
    marker = f"DRHLR_{secrets.token_hex(6)}"
    return {
        "token": marker,
        "token1": marker + "_BEFORE",
        "token2": marker + "_AFTER",
        "oracle_name": str(rule.get("name") or rule.get("id") or "database_oracle"),
    }


def _resolve_oracle_variables(probe: Any, raw: Any, context: dict[str, str]) -> dict[str, str]:
    if not isinstance(raw, dict):
        return context
    pending = dict(raw)
    resolved = dict(context)
    while pending:
        progressed = False
        for name, specification in list(pending.items()):
            try:
                if isinstance(specification, dict) and specification.get("query") is not None:
                    query = str(_render_oracle_value(specification["query"], resolved))
                    value = probe.scalar(query)
                else:
                    value = _render_oracle_value(specification, resolved)
            except ValueError:
                continue
            resolved[str(name)] = str(value)
            del pending[name]
            progressed = True
        if not progressed:
            names = ", ".join(str(name) for name in pending)
            raise ValueError(f"database oracle variables could not be resolved: {names}")
    return resolved


def _oracle_role(
    roles: dict[str, Any], configured_name: Any, default_role: Any | None, default_name: str
) -> tuple[Any | None, str]:
    name = str(configured_name or default_name or "visitor").strip()
    if name.casefold() == "visitor":
        return roles.get(name), name
    role = roles.get(name) if configured_name else default_role
    if role is None:
        raise ValueError(f"database oracle role is unavailable: {name}")
    return role, name


def _oracle_request(
    vector: AttackVector, phase: dict[str, Any], context: dict[str, str]
) -> tuple[str, RequestSpec, dict[str, Any]]:
    raw_request = phase.get("request", {})
    if not isinstance(raw_request, dict):
        raise ValueError("database oracle phase.request must be an object")
    rendered = _render_oracle_value(raw_request, context)
    page = str(rendered.get("page") or vector.page).lstrip("/")
    replace_params = bool(rendered.get("replace_params", False))
    params = {} if replace_params else dict(vector.request.params)
    request_params = rendered.get("params", {})
    if not isinstance(request_params, dict):
        raise ValueError("database oracle request.params must be an object")
    params.update(request_params)
    method = str(rendered.get("method") or vector.request.method).upper()
    referer = rendered.get("referer", vector.request.referer)
    request = RequestSpec(method, params, str(referer) if referer is not None else None)
    logged_params = {
        str(key): ("<redacted>" if re.search(r"pass(word)?|secret|api[_-]?key", str(key), re.I) else value)
        for key, value in params.items()
    }
    cookies = rendered.get("cookies", {})
    if not isinstance(cookies, dict):
        raise ValueError("database oracle request.cookies must be an object")
    cookie_names = sorted(str(key) for key in cookies)
    return page, request, {
        "method": method,
        "page": page,
        "params": logged_params,
        "referer": request.referer,
        "cookie_names": cookie_names,
    }


def _oracle_request_cookies(phase: dict[str, Any], context: dict[str, str]) -> dict[str, str]:
    raw_request = phase.get("request", {})
    if not isinstance(raw_request, dict):
        raise ValueError("database oracle phase.request must be an object")
    rendered = _render_oracle_value(raw_request, context)
    cookies = rendered.get("cookies", {})
    if not isinstance(cookies, dict):
        raise ValueError("database oracle request.cookies must be an object")
    return {str(key): str(value) for key, value in cookies.items()}


def _oracle_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _evaluate_oracle_assertions(
    probe: Any, response: Any, raw: Any, context: dict[str, str]
) -> tuple[bool, list[dict[str, Any]], str | None, str | None]:
    if not isinstance(raw, dict):
        raise ValueError("database oracle phase.assert must be an object")
    expected = _render_oracle_value(raw, context)
    body = str(response.text or "")
    checks: list[dict[str, Any]] = []

    for marker in _oracle_values(expected.get("response_contains")):
        checks.append({"type": "response_contains", "expected": marker, "passed": marker in body})
    for marker in _oracle_values(expected.get("response_not_contains")):
        checks.append({"type": "response_not_contains", "expected": marker, "passed": marker not in body})

    query = str(expected.get("query") or "").strip()
    observed: str | None = None
    if query:
        observed = probe.scalar(query)
        if "scalar_equals" in expected:
            wanted = str(expected["scalar_equals"])
            checks.append({"type": "scalar_equals", "expected": wanted, "observed": observed, "passed": observed == wanted})
        if "scalar_not_equals" in expected:
            wanted = str(expected["scalar_not_equals"])
            checks.append({"type": "scalar_not_equals", "expected": wanted, "observed": observed, "passed": observed != wanted})
        if bool(expected.get("scalar_zero", False)):
            checks.append({"type": "scalar_zero", "expected": "0", "observed": observed, "passed": observed.strip() in {"", "0"}})
        if bool(expected.get("scalar_nonzero", False)):
            checks.append({"type": "scalar_nonzero", "expected": "nonzero", "observed": observed, "passed": observed.strip() not in {"", "0"}})
        for marker in _oracle_values(expected.get("scalar_contains")):
            checks.append({"type": "scalar_contains", "expected": marker, "observed": observed, "passed": marker in observed})
    if not checks:
        raise ValueError("database oracle phase.assert contains no supported assertion")
    return all(bool(item["passed"]) for item in checks), checks, query or None, observed


def _run_database_oracle_phase(
    config: PipelineConfig,
    snapshot: Snapshot,
    vector: AttackVector,
    rule: dict[str, Any],
    phase_name: str,
    phase: dict[str, Any],
    base_context: dict[str, str],
    default_role: Any | None,
    default_role_name: str,
) -> dict[str, Any]:
    from ..analysis.detector import ActiveDetector

    snapshot.restore()
    probe = create_database_probe(config.database)
    context = _resolve_oracle_variables(probe, rule.get("variables", {}), dict(base_context))
    context = _resolve_oracle_variables(probe, phase.get("variables", {}), context)

    common_setup = rule.get("setup_sql", [])
    phase_setup = phase.get("setup_sql", [])
    if not isinstance(common_setup, list) or not isinstance(phase_setup, list):
        raise ValueError("database oracle setup_sql must be a list")
    setup_sql = [str(_render_oracle_value(sql, context)) for sql in [*common_setup, *phase_setup]]

    roles = {role.name: role for role in config.roles}
    role, role_name = _oracle_role(roles, phase.get("role"), default_role, default_role_name)
    detector = ActiveDetector(config, snapshot)
    session_before_setup = bool(phase.get("session_before_setup", False))
    session = detector._session(role) if session_before_setup else None
    session_request_logs: list[dict[str, Any]] = []
    try:
        for sql in setup_sql:
            probe.execute(sql)
        if session is None:
            session = detector._session(role)
        raw_session_requests = phase.get("session_requests", [])
        if not isinstance(raw_session_requests, list):
            raise ValueError("database oracle phase.session_requests must be a list")
        for raw_session_request in raw_session_requests:
            if not isinstance(raw_session_request, dict):
                raise ValueError("database oracle session request must be an object")
            bootstrap_phase = {"request": raw_session_request}
            bootstrap_page, bootstrap_request, bootstrap_log = _oracle_request(
                vector, bootstrap_phase, context
            )
            bootstrap_cookies = _oracle_request_cookies(bootstrap_phase, context)
            if bootstrap_cookies:
                session.cookies.update(bootstrap_cookies)
            bootstrap_response = detector._send(
                session, bootstrap_page, bootstrap_request, role=role
            )
            bootstrap_log["response"] = {
                "status_code": int(bootstrap_response.status_code),
                "url": str(bootstrap_response.url),
                "body_length": len(str(bootstrap_response.text or "")),
            }
            session_request_logs.append(bootstrap_log)
        page, request, request_log = _oracle_request(vector, phase, context)
        request_cookies = _oracle_request_cookies(phase, context)
        if request_cookies:
            session.cookies.update(request_cookies)
        response = detector._send(session, page, request, role=role)
        passed, checks, query, observed = _evaluate_oracle_assertions(
            probe, response, phase.get("assert", {}), context
        )
        return {
            "phase": phase_name,
            "role": role_name,
            "session_before_setup": session_before_setup,
            "setup_sql": setup_sql,
            "session_requests": session_request_logs,
            "request": request_log,
            "response": {
                "status_code": int(response.status_code),
                "url": str(response.url),
                "body_length": len(str(response.text or "")),
            },
            "query": query,
            "observed": observed,
            "assertions": checks,
            "passed": passed,
        }
    finally:
        if session is not None:
            session.close()


def _database_validation(
    config: PipelineConfig,
    snapshot: Snapshot,
    finding: Finding,
    vector: AttackVector,
) -> tuple[bool, dict[str, Any]]:
    rules = _database_oracle_rules(config, vector)
    if not rules:
        response_only = _database_oracle_is_response_only(config, vector)
        return True, {
            "oracle_version": 2,
            "scope": "repair_only",
            "applicable": False,
            "passed": True,
            "status": "response_only" if response_only else "not_configured",
            "display_as_passed": response_only,
            "message": (
                "database validation intentionally skipped; response oracle retained"
                if response_only
                else "no repair database oracle matched; response oracle retained"
            ),
            "dimensions": {
                "vulnerability_blocking": {"phase": "attack", "applicable": False, "passed": True},
                "regression": {"phase": "authorized", "applicable": False, "passed": True},
            },
            "scenarios": [],
        }

    roles = {role.name: role for role in config.roles}
    attack_default = roles.get(finding.actor) if finding.actor.casefold() != "visitor" else roles.get("visitor")
    authorized_default = _configured_regression_role(config, roles, vector)
    if authorized_default is None:
        authorized_default = next((roles[name] for name in vector.authorized_roles if name in roles), None)
    authorized_name = getattr(authorized_default, "name", "")
    scenarios: list[dict[str, Any]] = []

    for index, rule in enumerate(rules, start=1):
        name = str(rule.get("name") or rule.get("id") or f"database_oracle_{index}")
        operation = str(rule.get("operation") or "crud").lower()
        scenario: dict[str, Any] = {"name": name, "operation": operation, "passed": False, "phases": []}
        context = _oracle_context(rule)
        try:
            attack = rule.get("attack")
            authorized = rule.get("authorized")
            if not isinstance(attack, dict) or not isinstance(authorized, dict):
                raise ValueError("database oracle requires attack and authorized phase objects")
            scenario["phases"].append(_run_database_oracle_phase(
                config, snapshot, vector, rule, "attack", attack, context,
                attack_default, finding.actor,
            ))
            scenario["phases"].append(_run_database_oracle_phase(
                config, snapshot, vector, rule, "authorized", authorized, context,
                authorized_default, authorized_name,
            ))
            scenario["passed"] = all(bool(phase["passed"]) for phase in scenario["phases"])
        except Exception as exc:
            scenario["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            try:
                snapshot.restore()
            except Exception as exc:
                scenario["passed"] = False
                scenario["restore_error"] = f"{type(exc).__name__}: {exc}"
        scenarios.append(scenario)

    def phase_passed(phase_name: str) -> bool:
        for scenario in scenarios:
            if scenario.get("error") or scenario.get("restore_error"):
                return False
            phases = [
                phase for phase in scenario.get("phases", [])
                if phase.get("phase") == phase_name
            ]
            if not phases or not all(bool(phase.get("passed")) for phase in phases):
                return False
        return True

    attack_passed = phase_passed("attack")
    authorized_passed = phase_passed("authorized")
    passed = attack_passed and authorized_passed
    return passed, {
        "oracle_version": 2,
        "scope": "repair_only",
        "applicable": True,
        "passed": passed,
        "status": "passed" if passed else "failed",
        "dimensions": {
            "vulnerability_blocking": {
                "phase": "attack",
                "applicable": True,
                "passed": attack_passed,
            },
            "regression": {
                "phase": "authorized",
                "applicable": True,
                "passed": authorized_passed,
            },
        },
        "scenarios": scenarios,
    }


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
    finding: Finding,
    vector: AttackVector | None,
    validation_vectors: list[AttackVector] | None = None,
) -> tuple[bool, bool, bool, str, dict[str, Any]]:
    database_not_run = {
        "oracle_version": 2,
        "scope": "repair_only",
        "applicable": False,
        "passed": False,
        "status": "not_run",
        "dimensions": {
            "vulnerability_blocking": {"phase": "attack", "applicable": False, "passed": False},
            "regression": {"phase": "authorized", "applicable": False, "passed": False},
        },
        "scenarios": [],
    }
    options = _validation_options(config)
    active_vectors = list(validation_vectors or ([vector] if vector is not None else []))
    if not bool(options.get("temporary_apply_to_source", False)):
        return False, False, False, "runtime validation disabled; set repair.validation.temporary_apply_to_source=true", database_not_run
    if not active_vectors:
        return False, False, False, "attack vector is unavailable for runtime validation", database_not_run
    if snapshot is None:
        return False, False, False, "database snapshot is unavailable for runtime validation", database_not_run
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
                return False, False, False, f"runtime Java deployment failed: {apply_message}", database_not_run
        elif options.get("reload_command") or options.get("after_apply_command"):
            hook_ok, hook_message = _run_validation_hook(options, "reload_command", "after_apply_command")
            apply_message = f"{apply_message}; reload=({hook_message})"
            if not hook_ok:
                return False, False, False, f"runtime deployment hook failed: {hook_message}", database_not_run
        detector = ActiveDetector(config, snapshot)
        exploit_findings: list[Finding] = []
        response_vector_details: list[dict[str, Any]] = []
        response_exploit_checks: list[bool] = []
        response_regression_checks: list[bool] = []
        regression_messages: list[str] = []
        for active_vector in active_vectors:
            vector_findings = detector.run([active_vector])
            vector_exploit_passed = bool(vector_findings) and all(
                item.status != "vulnerable" for item in vector_findings
            )
            vector_regression_passed, vector_regression_message = _authorized_regression_passed(
                config, snapshot, active_vector
            )
            operation = _vector_operation(active_vector)
            exploit_findings.extend(vector_findings)
            response_exploit_checks.append(vector_exploit_passed)
            response_regression_checks.append(vector_regression_passed)
            regression_messages.append(f"{operation}: {vector_regression_message}")
            response_vector_details.append({
                **_vector_summary(active_vector),
                "vulnerability_blocking_passed": vector_exploit_passed,
                "regression_passed": vector_regression_passed,
                "findings": [item.to_dict() for item in vector_findings],
                "regression_evidence": vector_regression_message,
            })
        response_exploit_passed = all(response_exploit_checks)
        response_regression_passed = all(response_regression_checks)
        regression_message = "; ".join(regression_messages)
        primary_vector = vector or active_vectors[0]
        database_passed, database_details = _database_validation(
            config, snapshot, finding, primary_vector
        )
        database_details["response_vectors"] = response_vector_details
        database_dimensions = database_details.get("dimensions", {})
        database_attack_passed = bool(
            database_dimensions.get("vulnerability_blocking", {}).get("passed", database_passed)
        )
        database_regression_passed = bool(
            database_dimensions.get("regression", {}).get("passed", database_passed)
        )
        database_applicable = bool(database_details.get("applicable"))
        database_primary = database_applicable and all(
            _database_oracle_is_primary(config, item) for item in active_vectors
        )
        response_oracle_applicable = not database_primary
        exploit_blocked = database_attack_passed and (
            response_exploit_passed or not response_oracle_applicable
        )
        regression_passed = database_regression_passed and (
            response_regression_passed or not response_oracle_applicable
        )
        database_details["combined_dimensions"] = {
            "vulnerability_blocking": {
                "passed": exploit_blocked,
                "response_oracle_applicable": response_oracle_applicable,
                "response_oracle_passed": response_exploit_passed,
                "database_oracle_applicable": database_applicable,
                "database_oracle_passed": database_attack_passed,
            },
            "regression": {
                "passed": regression_passed,
                "response_oracle_applicable": response_oracle_applicable,
                "response_oracle_passed": response_regression_passed,
                "database_oracle_applicable": database_applicable,
                "database_oracle_passed": database_regression_passed,
            },
        }
        exploit_messages: list[str] = []
        finding_offset = 0
        for active_vector, detail in zip(active_vectors, response_vector_details):
            count = len(detail["findings"])
            vector_findings = exploit_findings[finding_offset:finding_offset + count]
            finding_offset += count
            evidence = ", ".join(
                f"{item.actor}:{item.status}" for item in vector_findings
            ) or "no exploit findings"
            exploit_messages.append(f"{_vector_operation(active_vector)}: {evidence}")
        exploit_message = "; ".join(exploit_messages)
        database_attack_label = "passed" if database_attack_passed else "failed"
        database_regression_label = "passed" if database_regression_passed else "failed"
        if not database_details.get("applicable"):
            neutral_label = "passed" if database_details.get("display_as_passed") else "not_applicable"
            database_attack_label = database_regression_label = neutral_label
        return exploit_blocked, regression_passed, database_passed, (
            f"deployment=({apply_message}); "
            f"vulnerability_blocking=(response={response_exploit_passed}; "
            f"database={database_attack_label}; evidence={exploit_message}); "
            f"regression=(response={response_regression_passed}; "
            f"database={database_regression_label}; evidence={regression_message})"
        ), database_details
    except Exception as exc:
        return False, False, False, f"runtime validation error: {type(exc).__name__}: {exc}", database_not_run
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


def _progress_validation_dimensions(
    syntax_ok: bool,
    exploit_blocked: bool,
    regression_passed: bool,
    details: dict[str, Any],
) -> None:
    if not syntax_ok:
        progress("repair validation: vulnerability blocking=skipped (syntax/compile failed)")
        progress("repair validation: regression=skipped (syntax/compile failed)")
        return

    combined = details.get("combined_dimensions", {})
    for name, passed in (
        ("vulnerability_blocking", exploit_blocked),
        ("regression", regression_passed),
    ):
        dimension = combined.get(name, {})
        response_passed = bool(dimension.get("response_oracle_passed", passed))
        response_applicable = bool(dimension.get("response_oracle_applicable", True))
        database_applicable = bool(
            dimension.get("database_oracle_applicable", details.get("applicable", False))
        )
        database_passed = bool(
            dimension.get("database_oracle_passed", details.get("passed", passed))
        )
        response_label = (
            "passed" if response_passed else "failed"
        ) if response_applicable else "not_applicable"
        if database_applicable or details.get("display_as_passed"):
            database_label = "passed" if database_passed else "failed"
        else:
            database_label = "not_applicable"
        display_name = name.replace("_", " ")
        progress(
            f"repair validation: {display_name}={'passed' if passed else 'failed'} "
            f"(response oracle={response_label}; database oracle={database_label})"
        )


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
    summary = {
        "Repair Items": len(results),
        "Total Repair Attempts": sum(item.attempts for item in results),
        "Patch Generation Attempts": sum(len(item.attempt_details) for item in results),
        "Patches Generated": sum(item.patches_generated for item in results),
        "Failed Patches": failed_patches,
        "Syntax / Compile OK": sum(item.syntax_compile_ok for item in results),
        "Exploit Blocked": sum(item.exploit_blocked for item in results),
        "Regression Passed": sum(item.regression_passed for item in results),
        "Database Validation Applied": sum(item.database_validation_applied for item in results),
        "Database Validation Passed": sum(item.database_validation_passed for item in results),
        "Successful Repairs": sum(1 for item in results if item.successful),
        "Failed Repairs": sum(1 for item in results if not item.successful),
        "Successful on Attempt 1": successful_attempt_buckets.get(1, 0),
        "Successful on Attempt 2": successful_attempt_buckets.get(2, 0),
        "Successful on Attempt 3": successful_attempt_buckets.get(3, 0),
    }
    covered = [item.coverage for item in results if item.coverage is not None]
    if covered:
        summary["Covered Vulnerable Findings"] = sum(
            int(item.get("covered_vulnerable_findings", 0)) for item in covered
        )
        summary["Aggregated Attack Vectors"] = sum(
            int(item.get("aggregated_attack_vectors", 0)) for item in covered
        )
    return summary


def _llm_retry_feedback(
    attempt_message: str,
    *,
    syntax_ok: bool | None = None,
    exploit_blocked: bool | None = None,
    regression_passed: bool | None = None,
) -> str:
    """Return only dimension-level failure reasons; never expose oracle evidence."""
    lowered = attempt_message.lower()
    if syntax_ok is None:
        syntax_ok = not (
            "syntax=(failed" in lowered
            or "syntax/compile failed" in lowered
            or lowered.startswith("attempt error:")
        )
    if exploit_blocked is None:
        exploit_blocked = any(
            marker in lowered
            for marker in ("exploit=(blocked", "vulnerability_blocking=(response=true")
        ) and "database=failed" not in lowered
    if regression_passed is None:
        regression_passed = any(
            marker in lowered
            for marker in ("regression=(passed", "regression=(response=true")
        ) and "regression=(response=true; database=failed" not in lowered

    failures: list[str] = []
    if not syntax_ok:
        failures.append("The syntax/compile check failed.")
    else:
        if not exploit_blocked:
            failures.append("The vulnerability was not blocked.")
        if not regression_passed:
            failures.append("The regression test did not pass.")
    return " ".join(failures) or "The previous patch failed validation."


def write_repair_report(results: list[RepairResult], output: Path) -> None:
    summary = _repair_summary(results)
    lines = [
        "# DRHL Repair Report",
        "",
        f"- Repair Items: {summary['Repair Items']}",
    ]
    if "Covered Vulnerable Findings" in summary:
        lines.extend([
            f"- Covered Vulnerable Findings: {summary['Covered Vulnerable Findings']}",
            f"- Aggregated Attack Vectors: {summary['Aggregated Attack Vectors']}",
        ])
    lines.extend([
        f"- Total Repair Attempts: {summary['Total Repair Attempts']}",
        f"- Patch Generation Attempts: {summary['Patch Generation Attempts']}",
        f"- Patches Generated: {summary['Patches Generated']}",
        f"- Failed Patches: {summary['Failed Patches']}",
        f"- Syntax / Compile OK: {summary['Syntax / Compile OK']}",
        f"- Exploit Blocked: {summary['Exploit Blocked']}",
        f"- Regression Passed: {summary['Regression Passed']}",
        f"- Database Validation Applied: {summary['Database Validation Applied']}",
        f"- Database Validation Passed: {summary['Database Validation Passed']}",
        f"- Successful Repairs: {summary['Successful Repairs']}",
        f"- Failed Repairs: {summary['Failed Repairs']}",
        f"- Successful on Attempt 1: {summary['Successful on Attempt 1']}",
        f"- Successful on Attempt 2: {summary['Successful on Attempt 2']}",
        f"- Successful on Attempt 3: {summary['Successful on Attempt 3']}",
        "",
        "> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.",
        "> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.",
        "> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.",
        "> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.",
        "",
        "## Details",
        "",
    ])
    if not results:
        lines.extend(["No repair candidates were generated.", ""])
    for item in results:
        detail_lines = [
            f"### `{item.page}`",
            "",
            f"- Category: {item.category}",
        ]
        if item.coverage is not None:
            operations = ", ".join(
                str(value) for value in item.coverage.get("validated_operations", [])
            ) or "none"
            detail_lines.extend([
                f"- Covered Vulnerable Findings: {item.coverage.get('covered_vulnerable_findings', 0)}",
                f"- Aggregated Attack Vectors: {item.coverage.get('aggregated_attack_vectors', 0)}",
                f"- Validated Operations: {operations}",
            ])
        detail_lines.extend([
            f"- Status: {item.status}",
            f"- Attempts: {item.attempts}",
            f"- Patches Generated: {item.patches_generated}",
            f"- Failed Patches: {sum(1 for attempt in item.attempt_details if attempt.output and not attempt.successful)}",
            f"- Syntax / Compile OK: {item.syntax_compile_ok}",
            f"- Exploit Blocked: {item.exploit_blocked}",
            f"- Regression Passed: {item.regression_passed}",
            f"- Database Validation Applied: {item.database_validation_applied}",
            f"- Database Validation Passed: {item.database_validation_passed}",
            f"- Successful: {str(item.successful).lower()}",
            f"- Message: {item.message}",
            "",
        ])
        lines.extend(detail_lines)
        for attempt in item.attempt_details:
            lines.extend([
                f"  - Attempt {attempt.attempt}: syntax={attempt.syntax_compile_ok}, "
                f"exploit_blocked={attempt.exploit_blocked}, regression={attempt.regression_passed}, "
                f"database_validation={attempt.database_validation_passed}, successful={attempt.successful}",
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
    validation = _validation_options(config)
    aggregate_vectors = bool(validation.get("aggregate_vectors_by_repair_item", False))
    vector_lookup: dict[tuple[str, str], list[AttackVector]] = {}
    for vector in vectors or []:
        for page_candidate in [vector.page, *getattr(vector, "page_overrides", [])]:
            for match_candidate in _page_match_candidates(page_candidate):
                bucket = vector_lookup.setdefault((vector.category, match_candidate), [])
                if vector not in bucket:
                    bucket.append(vector)
    results: list[RepairResult] = []
    processed: set[tuple[str, str]] = set()
    max_attempts = max(1, int(validation.get("max_attempts", 3)))

    for finding in findings:
        if finding.status != "vulnerable":
            continue
        skipped, skip_reason = _repair_finding_is_skipped(config, finding)
        if skipped:
            progress(f"Skipping repair for {finding.category}: {finding.page} ({skip_reason})")
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
        matched_vectors: list[AttackVector] = []
        for match_candidate in _page_match_candidates(finding.page):
            for matched in vector_lookup.get((finding.category, match_candidate), []):
                if matched not in matched_vectors:
                    matched_vectors.append(matched)
        vector = (
            matched_vectors[0] if aggregate_vectors and matched_vectors
            else matched_vectors[-1] if matched_vectors
            else None
        )
        validation_vectors = matched_vectors if aggregate_vectors else None
        coverage = None
        if aggregate_vectors:
            operations = list(dict.fromkeys(_vector_operation(item) for item in matched_vectors))
            coverage = {
                "covered_vulnerable_findings": sum(
                    1 for item in findings
                    if item.status == "vulnerable"
                    and item.category == finding.category
                    and item.page == finding.page
                ),
                "aggregated_attack_vectors": len(matched_vectors),
                "validated_operations": operations,
            }
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
                    vectors=validation_vectors,
                )
                output = output_root / f"attempt-{attempt_number}" / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(patched, encoding="utf-8")
                syntax_ok, syntax_message = _syntax_check(config, output)
                progress(
                    f"repair validation: syntax/compile={'passed' if syntax_ok else 'failed'}"
                )
                if syntax_ok:
                    exploit_ok, regression_ok, database_ok, runtime_message, database_details = _runtime_validation(
                        config, snapshot, source, patched, finding, vector,
                        validation_vectors=validation_vectors,
                    )
                else:
                    exploit_ok, regression_ok, database_ok = False, False, False
                    runtime_message = "runtime validation skipped because syntax/compile failed"
                    database_details = {
                        "oracle_version": 2,
                        "scope": "repair_only",
                        "applicable": False,
                        "passed": False,
                        "status": "skipped",
                        "message": "syntax/compile failed",
                        "dimensions": {
                            "vulnerability_blocking": {
                                "phase": "attack", "applicable": False, "passed": False,
                            },
                            "regression": {
                                "phase": "authorized", "applicable": False, "passed": False,
                            },
                        },
                        "scenarios": [],
                    }
                successful = syntax_ok and exploit_ok and regression_ok
                attempt_message = f"syntax=({syntax_message}); {runtime_message}"
                _progress_validation_dimensions(
                    syntax_ok, exploit_ok, regression_ok, database_details
                )
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
                    database_validation_passed=database_ok,
                    database_validation=database_details,
                ))
                final_output = output
                final_plan = plan
                final_prompt = prompt_artifact
                if successful:
                    status = "successful_repair"
                    message = (
                        "syntax/compile, vulnerability blocking, and regression validation all passed"
                    )
                    break
                feedback.append(_llm_retry_feedback(
                    attempt_message,
                    syntax_ok=syntax_ok,
                    exploit_blocked=exploit_ok,
                    regression_passed=regression_ok,
                ))
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
                feedback.append(_llm_retry_feedback(
                    attempt_message,
                    syntax_ok=False,
                    exploit_blocked=False,
                    regression_passed=False,
                ))

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
            database_validation_applied=sum(
                1 for attempt in attempts if attempt.database_validation.get("applicable")
            ),
            database_validation_passed=sum(
                1 for attempt in attempts
                if attempt.database_validation.get("applicable") and attempt.database_validation_passed
            ),
            successful=any(attempt.successful for attempt in attempts),
            validation_artifact=str(validation_artifact),
            attempt_details=attempts,
            coverage=coverage,
        )
        write_json(validation_artifact, _repair_result_dict(result))
        results.append(result)
    return results


def _repair_result_dict(result: RepairResult) -> dict[str, Any]:
    data = asdict(result)
    if data.get("coverage") is None:
        data.pop("coverage", None)
    return data


def serialize_repairs(results: list[RepairResult]) -> dict[str, Any]:
    return {
        "summary": _repair_summary(results),
        "repairs": [_repair_result_dict(result) for result in results],
    }





