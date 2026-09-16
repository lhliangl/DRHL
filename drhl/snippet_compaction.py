from __future__ import annotations

import re
from typing import Any, Iterable


def _normalized_code(value: Any) -> str:
    """Normalize formatting noise without changing the code's structure."""
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def _configured_prefix(path: str, code: str, rules: Iterable[Any] | None) -> str:
    """Return opt-in context that a configured application wants prepended."""
    for raw in rules or []:
        if not isinstance(raw, dict):
            continue
        path_pattern = str(raw.get("path_pattern") or "")
        code_pattern = str(raw.get("code_pattern") or "")
        prefix = _normalized_code(raw.get("prefix"))
        if not prefix:
            continue
        if path_pattern and re.search(path_pattern, path, re.I) is None:
            continue
        if code_pattern and re.search(code_pattern, code, re.I | re.S) is None:
            continue
        return prefix
    return ""


def compact_snippets(
    snippets: Iterable[Any],
    *,
    exclude_kinds: Iterable[str] | None = None,
    exclude_code_patterns: Iterable[str] | None = None,
    require_if_framework: bool = False,
    prefix_rules: Iterable[Any] | None = None,
) -> list[dict[str, Any]]:
    """Build the minimal access-control snippet representation sent to the LLM.

    Prefer a parameter snippet's if_framework when it is available, otherwise
    retain its complete code. Duplicate code is removed only within the same
    source file. The compact LLM artifact intentionally contains no semantic
    metadata: each item is exactly path plus the selected code field.
    """
    compacted: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    excluded = {str(kind).strip().casefold() for kind in (exclude_kinds or []) if str(kind).strip()}
    excluded_code = [
        re.compile(str(pattern), re.I | re.S)
        for pattern in (exclude_code_patterns or [])
        if str(pattern).strip()
    ]

    for raw in snippets:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("kind") or "").strip().casefold() in excluded:
            continue
        path = str(raw.get("path") or "").strip().replace("\\", "/")
        if_framework = _normalized_code(raw.get("if_framework"))
        if require_if_framework and not if_framework:
            continue
        field = "if_framework" if if_framework else "code"
        selected_code = if_framework or _normalized_code(raw.get("code"))
        if not path or not selected_code:
            continue
        if any(pattern.search(selected_code) for pattern in excluded_code):
            continue
        prefix = _configured_prefix(path, selected_code, prefix_rules)
        if prefix:
            selected_code = f"{prefix}\n{selected_code}"
        key = (path, selected_code)
        if key in seen:
            continue
        seen.add(key)
        compacted.append({"path": path, field: selected_code})
    return compacted


def compact_snippet_document(
    snippets: Iterable[Any],
    *,
    exclude_kinds: Iterable[str] | None = None,
    exclude_code_patterns: Iterable[str] | None = None,
    require_if_framework: bool = False,
    prefix_rules: Iterable[Any] | None = None,
) -> dict[str, Any]:
    source = list(snippets)
    compacted = compact_snippets(
        source,
        exclude_kinds=exclude_kinds,
        exclude_code_patterns=exclude_code_patterns,
        require_if_framework=require_if_framework,
        prefix_rules=prefix_rules,
    )
    return {
        "summary": {
            "source_items": len(source),
            "llm_items": len(compacted),
            "items_removed": len(source) - len(compacted),
        },
        "snippets": compacted,
    }
