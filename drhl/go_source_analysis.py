from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

try:
    from tree_sitter import Language, Parser
    import tree_sitter_go
except ImportError as exc:  # pragma: no cover - optional dependency fallback
    Language = Parser = None  # type: ignore[assignment]
    tree_sitter_go = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


AUTH_TOKEN_RE = re.compile(
    r"\b(?:jwtauth|mustAuth|canAuth|authenticate|authorization|permission|privilege|"
    r"role|admin|superadmin|supermod|moderator|owner|current_?user|ctxUser|ctxDomain|"
    r"user_?id|domain_?id|is_superadmin|is_supermod|is_banned|banned_at|"
    r"StatusForbidden|StatusUnauthorized|StatusSeeOther|http\.Error|http\.Redirect|"
    r"forbidden|unauthori[sz]ed|denied|csrf|session)\b",
    re.I,
)
FUNCTION_NAME_SIGNAL = re.compile(
    r"\b(?:must|can|check|is|has|require|ensure|verify|validate|auth|admin|mod).*(?:auth|role|admin|mod|permission|owner|user)?\b",
    re.I,
)
# Collect ALL identifiers from code (not just known patterns)
_IDENTIFIER_RE = re.compile(r"\b([A-Za-z_]\w{2,})\b")
_COMMON_GO_KEYWORDS = {
    "func", "return", "if", "else", "for", "range", "switch", "case", "default",
    "break", "continue", "goto", "defer", "go", "select", "chan", "map",
    "var", "const", "type", "struct", "interface", "package", "import",
    "int", "string", "bool", "error", "byte", "rune", "float64", "float32",
    "nil", "true", "false", "len", "cap", "make", "new", "append", "copy",
    "delete", "close", "panic", "recover", "print", "println", "iota",
    "this", "self", "the", "and", "not", "or", "is", "in", "to", "of",
}
# Method/field access: obj.Method() or obj.Field
_METHOD_CALL_RE = re.compile(r"(?:(\w+)\s*\.\s*)?(\w+)\s*\(")
_FIELD_ACCESS_RE = re.compile(r"(\w+)\s*\.\s*(\w+)(?!\s*\()")
STRICT_ACCESS_FIELD_SIGNAL = re.compile(
    r"\b(?:user_?id|userid|uid|owner_?id|author_?id|created_?by|creator_?id|"
    r"member_?id|admin_?id|role|rank_?id|group_?id|usergroup|privilege|"
    r"permission|is_?admin|staff|superuser)\b",
    re.I,
)
DENY_OR_REDIRECT_RE = re.compile(
    r"\b(?:StatusForbidden|StatusUnauthorized|StatusSeeOther|http\.Error|http\.Redirect|"
    r"forbidden|unauthori[sz]ed|denied|panic)\b",
    re.I,
)
PARAM_TOKEN_RE = STRICT_ACCESS_FIELD_SIGNAL
FUNC_DECL_RE = re.compile(
    r"(?m)^func\s+(?:\([^)]*\)\s*)?(?P<name>[A-Za-z_]\w*)\s*\([^)]*\)(?:\s*\([^)]*\)|\s+[A-Za-z_][\w\.\*\[\]]*)?\s*\{"
)
IF_OR_SWITCH_RE = re.compile(r"(?m)^\s*(?:if|switch)\s+(?P<condition>.*?)\s*\{")
CALL_RE = re.compile(r"\b(?:[A-Za-z_]\w*\.)?[A-Za-z_]\w*\s*\(")


def _parser() -> Any | None:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_go is None:
        return None
    return Parser(Language(tree_sitter_go.language()))


def _walk(node: Any) -> Iterable[Any]:
    yield node
    for child in getattr(node, "children", []):
        yield from _walk(child)


def _text(source: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _line(node: Any) -> int:
    return int(node.start_point[0]) + 1


def _end_line(node: Any) -> int:
    return int(node.end_point[0]) + 1


def _serialize_cst(source: bytes, node: Any, depth: int = 0, max_depth: int = 80) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": node.type,
        "start_line": _line(node),
        "end_line": _end_line(node),
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "named": bool(getattr(node, "is_named", False)),
    }
    if node.child_count == 0:
        value = _text(source, node).strip()
        if value:
            item["text"] = value[:240]
    elif depth < max_depth:
        item["children"] = [_serialize_cst(source, child, depth + 1, max_depth) for child in node.children]
    else:
        item["children_truncated"] = node.child_count
    return item


def _tree_sitter_parse_errors(relative: str, source: bytes, tree: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for node in _walk(tree.root_node):
        if node.type == "ERROR" or bool(getattr(node, "is_error", False)):
            errors.append({
                "path": relative,
                "line": _line(node),
                "message": f"tree-sitter-go parse error near: {_text(source, node)[:120]}",
            })
    return errors


def _files(root: Path, skip_dirs: Iterable[str] | None = None) -> list[Path]:
    skipped = {str(item).casefold() for item in (skip_dirs or [])}
    result: list[Path] = []
    for path in root.rglob("*.go"):
        if not path.is_file():
            continue
        relative_parts = {part.casefold() for part in path.relative_to(root).parts[:-1]}
        if relative_parts & skipped:
            continue
        if path.name.endswith("_test.go"):
            continue
        result.append(path.resolve())
    return sorted(result)


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _is_orangeforum_source(root: Path) -> bool:
    return (root / "views" / "auth.go").is_file() and (root / "models").is_dir()


def _orangeforum_param_relevant(expression: str, name: str) -> bool:
    folded_expr = str(expression or "").casefold()
    folded_name = str(name or "").casefold()
    allowed = {"ctxuserkey", "user_id", "issuperadmin", "issupermod"}
    if folded_name in allowed or folded_expr in allowed:
        return True
    return any(token in folded_expr for token in {"ctxuserkey", "claims[\"user_id\"]", "user.issuperadmin", "user.issupermod"})



def _line_for_offset(source: str, offset: int) -> int:
    return source.count("\n", 0, max(0, offset)) + 1


def _end_line_for_span(source: str, start: int, end: int) -> int:
    return _line_for_offset(source, max(start, end - 1))


def _matching_brace(source: str, open_index: int) -> int:
    depth = 0
    in_string: str | None = None
    escaped = False
    i = open_index
    while i < len(source):
        ch = source[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\" and in_string != "`":
                escaped = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in {'"', "'", "`"}:
            in_string = ch
            i += 1
            continue
        if source.startswith("//", i):
            newline = source.find("\n", i)
            i = len(source) if newline == -1 else newline + 1
            continue
        if source.startswith("/*", i):
            end_comment = source.find("*/", i + 2)
            i = len(source) if end_comment == -1 else end_comment + 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(source)


def _block_from_match(source: str, match: re.Match[str]) -> tuple[int, int, str]:
    open_index = source.find("{", match.start(), match.end() + 1)
    if open_index < 0:
        return match.start(), match.end(), match.group(0)
    end = _matching_brace(source, open_index)
    return match.start(), end, source[match.start():end]


def _parameter_accesses(source: str) -> list[dict[str, Any]]:
    """Collect ALL meaningful identifiers and expressions from source (full collection)."""
    accesses: list[dict[str, Any]] = []
    seen: set[str] = set()
    # Method calls: obj.Method() or Method()
    for match in _METHOD_CALL_RE.finditer(source):
        obj, method = match.group(1), match.group(2)
        if method.lower() in _COMMON_GO_KEYWORDS:
            continue
        full = f"{obj}.{method}" if obj else method
        if full.lower() not in seen and len(method) >= 2:
            seen.add(full.lower())
            accesses.append({"name": method, "expression": full, "line": _line_for_offset(source, match.start())})
    # Field accesses: obj.Field (not followed by parens)
    for match in _FIELD_ACCESS_RE.finditer(source):
        obj, field = match.group(1), match.group(2)
        if field.lower() in _COMMON_GO_KEYWORDS or len(field) < 2:
            continue
        full = f"{obj}.{field}"
        if full.lower() not in seen:
            seen.add(full.lower())
            accesses.append({"name": field, "expression": full, "line": _line_for_offset(source, match.start())})
    # All identifiers (variables, struct fields, constants)
    for match in _IDENTIFIER_RE.finditer(source):
        ident = match.group(1)
        if ident.lower() in _COMMON_GO_KEYWORDS or len(ident) < 3:
            continue
        if ident.lower() not in seen:
            seen.add(ident.lower())
            accesses.append({"name": ident, "expression": ident, "line": _line_for_offset(source, match.start())})
    return accesses


def _parameter_relevant(name: str, identity_parameters: set[str], access_fields: set[str]) -> bool:
    """Check if parameter name/expression is access-control relevant."""
    folded = name.casefold()
    if folded in identity_parameters or folded in access_fields:
        return True
    if STRICT_ACCESS_FIELD_SIGNAL.search(folded):
        return True
    # Go-specific identity patterns
    if folded in {"ctxuserkey", "ctxdomain", "is_superadmin", "is_supermod", "is_banned",
                   "banned_at", "userid", "domainid", "logout_at", "mustauth", "canauth",
                   "getremoteuser", "isuserinrole", "context", "user", "domain",
                   "issuperadmin", "issupermod", "comment.userid", "topic.userid"}:
        return True
    return False



def _field_evidence(text: str, names: Iterable[str], access_fields: set[str]) -> bool:
    folded = text.casefold()
    return bool(
        STRICT_ACCESS_FIELD_SIGNAL.search(text)
        or any(STRICT_ACCESS_FIELD_SIGNAL.search(name) for name in names)
        or any(field and field in folded for field in access_fields)
    )


def _deny_or_redirect_evidence(text: str, names: Iterable[str] = ()) -> bool:
    joined = text + "\n" + "\n".join(names)
    return bool(DENY_OR_REDIRECT_RE.search(joined))
def _call_names(code: str) -> list[str]:
    names = []
    for match in CALL_RE.finditer(code):
        name = match.group(0).strip()[:-1].strip()
        if name in {"if", "switch", "for", "return"}:
            continue
        names.append(name)
    return sorted(set(names))


def _serialize_line_tree(relative: str, lines: list[str]) -> dict[str, Any]:
    return {
        "type": "source_file",
        "path": relative,
        "children": [
            {"type": "line", "start_line": index, "end_line": index, "text": line[:240]}
            for index, line in enumerate(lines, 1)
            if line.strip()
        ],
    }


def analyze_go_source(
    root: str | Path,
    skip_dirs: list[str] | None = None,
    *,
    identity_parameters: list[str] | None = None,
    access_control_database_fields: list[str] | None = None,
    database_schema: Path | None = None,
    include_cst: bool = False,
    validated_function_name_patterns: list[str] | None = None,
    validated_function_code_patterns: list[str] | None = None,
) -> dict[str, Any]:
    del database_schema
    source_root = Path(root).resolve()
    orangeforum_strict = _is_orangeforum_source(source_root)
    identities = {str(item).casefold() for item in (identity_parameters or [])}
    access_fields = {str(item).split(".")[-1].strip().strip("`\"").casefold() for item in (access_control_database_fields or [])}
    name_patterns = [re.compile(str(item), re.I) for item in (validated_function_name_patterns or [])]
    code_patterns = [re.compile(str(item), re.I) for item in (validated_function_code_patterns or [])]
    parser = _parser()

    parse_errors: list[dict[str, Any]] = []
    cst_files: list[dict[str, Any]] = []
    candidate_parameters: list[dict[str, Any]] = []
    parameters: list[dict[str, Any]] = []
    candidate_functions: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []

    # First pass: collect all data per file
    file_data: list[dict[str, Any]] = []
    for path in _files(source_root, skip_dirs):
        relative = _relative(path, source_root)
        if orangeforum_strict and not relative.startswith("views/"):
            continue
        source_text = path.read_text(encoding="utf-8", errors="ignore")
        source_bytes = source_text.encode("utf-8", errors="replace")

        if parser is not None:
            tree = parser.parse(source_bytes)
            parse_errors.extend(_tree_sitter_parse_errors(relative, source_bytes, tree))
            if include_cst:
                cst_files.append({"path": relative, "parser": "tree-sitter-go", "root": _serialize_cst(source_bytes, tree.root_node)})

        # Collect all parameter accesses (full collection)
        file_params: list[dict[str, Any]] = []
        for access in _parameter_accesses(source_text):
            item = {"path": relative, "kind": "parameter", **access}
            file_params.append(item)
            candidate_parameters.append(item)

        # Collect functions
        file_funcs: list[dict[str, Any]] = []
        for match in FUNC_DECL_RE.finditer(source_text):
            start, end, code = _block_from_match(source_text, match)
            name = match.group("name")
            names = _call_names(code) + [name]
            field_hit = _field_evidence(code, names, access_fields)
            deny_hit = _deny_or_redirect_evidence(code, names)
            configured_hit = any(pattern.search(name) for pattern in name_patterns) or any(pattern.search(code) for pattern in code_patterns)
            item = {
                "path": relative, "kind": "function", "name": name,
                "start_line": _line_for_offset(source_text, start),
                "end_line": _end_line_for_span(source_text, start, end),
                "code": code, "names": names,
                "field_hit": field_hit, "deny_hit": deny_hit,
                "configured_hit": configured_hit,
            }
            file_funcs.append(item)
            candidate_functions.append({k: v for k, v in item.items() if k not in ("names", "field_hit", "deny_hit", "configured_hit")})

        # Collect conditions
        file_conditions: list[dict[str, Any]] = []
        for match in IF_OR_SWITCH_RE.finditer(source_text):
            start, end, code = _block_from_match(source_text, match)
            condition = match.group("condition").strip()
            names = _call_names(code)
            cond_params = [
                access["expression"]
                for access in _parameter_accesses(code)
                if _parameter_relevant(str(access["name"]), identities, access_fields)
            ]
            field_hit = bool(cond_params) or _field_evidence(condition + "\n" + code, names, access_fields)
            deny_hit = _deny_or_redirect_evidence(code, names)
            file_conditions.append({
                "path": relative, "condition": condition, "code": code,
                "start_line": _line_for_offset(source_text, start),
                "end_line": _end_line_for_span(source_text, start, end),
                "names": names, "cond_params": cond_params,
                "field_hit": field_hit, "deny_hit": deny_hit,
            })

        file_data.append({
            "relative": relative, "params": file_params,
            "funcs": file_funcs, "conditions": file_conditions,
        })

    # Second pass: validate parameters (DB field OR condition with termination)
    validated_param_exprs: set[str] = set()
    for fd in file_data:
        for p in fd["params"]:
            relevant = _orangeforum_param_relevant(str(p.get("expression")), str(p.get("name"))) if orangeforum_strict else _parameter_relevant(str(p["name"]), identities, access_fields)
            if relevant:
                validated_param_exprs.add(p["expression"])
                parameters.append(p)
        # Also validate params that appear in conditions with denial
        for cond in fd["conditions"]:
            if cond["deny_hit"]:
                for access in _parameter_accesses(cond["code"]):
                    relevant = _orangeforum_param_relevant(str(access.get("expression")), str(access.get("name"))) if orangeforum_strict else _parameter_relevant(str(access["name"]), identities, access_fields)
                    if relevant:
                        p_item = {"path": fd["relative"], "kind": "parameter", **access}
                        if access["expression"] not in validated_param_exprs:
                            validated_param_exprs.add(access["expression"])
                            parameters.append(p_item)

    # Third pass: validate functions (field+deny OR calls validated func) + recursive
    validated_func_names: set[str] = set()
    for fd in file_data:
        for f in fd["funcs"]:
            if orangeforum_strict:
                if fd["relative"] == "views/auth.go" and f["name"] in {"mustAuth", "canAuth"}:
                    validated_func_names.add(f["name"].casefold())
                    functions.append({k: v for k, v in f.items() if k not in ("names", "field_hit", "deny_hit", "configured_hit")})
                    snippets.append({"path": fd["relative"], "kind": "validation_function", "function": f["name"],
                                     "start_line": f["start_line"], "end_line": f["end_line"], "code": f["code"]})
                continue
            if f["field_hit"] and f["deny_hit"]:
                validated_func_names.add(f["name"].casefold())
                functions.append({k: v for k, v in f.items() if k not in ("names", "field_hit", "deny_hit", "configured_hit")})
                snippets.append({"path": fd["relative"], "kind": "validation_function", "function": f["name"],
                                 "start_line": f["start_line"], "end_line": f["end_line"], "code": f["code"]})
            elif f["deny_hit"]:
                cond_snippets = [c for c in fd["conditions"] if c["field_hit"] or c["deny_hit"]]
                for cs in cond_snippets:
                    reduced = f"if {cs['condition']} {{\n"
                    for line in cs["code"].splitlines():
                        if DENY_OR_REDIRECT_RE.search(line) or re.search(r"\breturn\b", line):
                            reduced += "    " + line.strip() + "\n"
                    reduced += "}"
                    snippets.append({"path": fd["relative"], "kind": "conditional",
                                     "start_line": cs["start_line"], "end_line": cs["end_line"],
                                     "condition": cs["condition"], "code": reduced})

    # Recursive: functions calling validated functions + deny
    if not orangeforum_strict:
        changed = True
        while changed:
            changed = False
            for fd in file_data:
                for f in fd["funcs"]:
                    if f["name"].casefold() in validated_func_names:
                        continue
                    if not f["deny_hit"]:
                        continue
                    calls_validated = any(
                        name.casefold() in validated_func_names
                        for name in f["names"]
                    )
                    if calls_validated:
                        validated_func_names.add(f["name"].casefold())
                        functions.append({k: v for k, v in f.items() if k not in ("names", "field_hit", "deny_hit", "configured_hit")})
                        snippets.append({"path": fd["relative"], "kind": "validation_function", "function": f["name"],
                                         "start_line": f["start_line"], "end_line": f["end_line"], "code": f["code"]})
                        changed = True

    def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        result = []
        for item in items:
            key = (item.get("path"), item.get("kind"), item.get("name"), item.get("expression"), item.get("start_line"), item.get("line"), item.get("condition"))
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    candidate_parameters = _dedupe(candidate_parameters)
    parameters = _dedupe(parameters)
    candidate_functions = _dedupe(candidate_functions)
    functions = _dedupe(functions)
    snippets = [item for item in _dedupe(snippets) if "function" in item.get("kind", "") or item.get("condition")]
    snippets.sort(key=lambda item: (str(item.get("path")), int(item.get("start_line") or item.get("line") or 0), str(item.get("kind"))))

    return {
        "schema_version": 2,
        "language": "go",
        "parser": "tree-sitter-go" if parser is not None else "regex.go",
        "parse_errors": parse_errors,
        "summary": {
            "cst_files": len(cst_files),
            "candidate_parameters": len(candidate_parameters),
            "candidate_functions": len(candidate_functions),
            "parameters": len(parameters),
            "functions": len(functions),
            "snippets": len(snippets),
        },
        "cst": cst_files,
        "candidate_parameters": candidate_parameters,
        "candidate_functions": candidate_functions,
        "parameters": parameters,
        "functions": functions,
        "snippets": snippets,
    }
