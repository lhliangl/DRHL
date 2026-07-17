from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Iterable


AUTH_TOKEN_RE = re.compile(
    r"\b(?:request\.user|current_user|session|login_required|permission_required|"
    r"user_passes_test|staff_member_required|is_authenticated|is_staff|is_superuser|"
    r"has_perm|has_perms|groups?|permissions?|PermissionDenied|Http404|HttpResponseForbidden|"
    r"redirect|forbidden|unauthori[sz]ed|denied|is_admin|administrator|staff|superuser)\b",
    re.I,
)
CALL_GUARD_RE = re.compile(
    r"\b(?:login_required|permission_required|user_passes_test|staff_member_required|"
    r"is_authenticated|is_staff|is_superuser|has_perm|has_perms|PermissionDenied|Http404|"
    r"HttpResponseForbidden|redirect|forbidden|unauthori[sz]ed|denied)\b",
    re.I,
)
STRICT_ACCESS_FIELD_SIGNAL = re.compile(
    r"\b(?:user_?id|userid|uid|owner_?id|author_?id|created_?by|creator_?id|"
    r"member_?id|admin_?id|role|rank_?id|group_?id|usergroup|privilege|"
    r"permission|is_?admin|staff|superuser)\b",
    re.I,
)
DENY_OR_REDIRECT_RE = re.compile(
    r"\b(?:PermissionDenied|Http404|HttpResponseForbidden|redirect|forbidden|"
    r"unauthori[sz]ed|denied|raise|abort)\b",
    re.I,
)
PARAM_TOKEN_RE = STRICT_ACCESS_FIELD_SIGNAL


def _files(root: Path, skip_dirs: Iterable[str] | None = None) -> list[Path]:
    skipped = {str(item).casefold() for item in (skip_dirs or [])}
    result: list[Path] = []
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        relative_parts = {part.casefold() for part in path.relative_to(root).parts[:-1]}
        if relative_parts & skipped:
            continue
        result.append(path.resolve())
    return sorted(result)


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _source_segment(source: str, node: ast.AST) -> str:
    try:
        return ast.get_source_segment(source, node) or ""
    except Exception:
        return ""


def _node_lines(lines: list[str], node: ast.AST, context: int = 0) -> str:
    start = max(1, int(getattr(node, "lineno", 1)) - context)
    end = min(len(lines), int(getattr(node, "end_lineno", start)) + context)
    return "\n".join(lines[start - 1:end])


def _dotted_name(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _dotted_name(node.func)
    if isinstance(node, ast.Subscript):
        return _dotted_name(node.value)
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return ""


def _constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    return None


def _subscript_key(node: ast.Subscript) -> str | None:
    slice_node = node.slice
    if isinstance(slice_node, ast.Index):  # pragma: no cover - py<3.9 compatibility
        slice_node = slice_node.value
    return _constant_string(slice_node)


def _call_name(node: ast.Call) -> str:
    return _dotted_name(node.func)


def _decorator_name(node: ast.AST) -> str:
    return _dotted_name(node)

def _is_django_project(root: Path) -> bool:
    return (root / "manage.py").exists()


def _is_user_passes_test_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node).split(".")[-1] == "user_passes_test"


def _lambda_permission_attributes(node: ast.Call) -> list[dict[str, Any]]:
    """Extract permission attributes from user_passes_test(lambda u: u.is_staff, ...)."""
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    lambdas = [arg for arg in node.args if isinstance(arg, ast.Lambda)]
    for keyword in node.keywords:
        if isinstance(keyword.value, ast.Lambda):
            lambdas.append(keyword.value)
    for lambda_node in lambdas:
        arg_names = {arg.arg for arg in lambda_node.args.args}
        if not arg_names:
            continue
        identity_key = ("request.user", "request.user")
        if identity_key not in seen:
            seen.add(identity_key)
            result.append({
                "name": "request.user",
                "expression": "request.user",
                "decorator_expression": next(iter(arg_names)),
                "line": int(getattr(lambda_node, "lineno", getattr(node, "lineno", 0)) or 0),
            })
        for child in ast.walk(lambda_node.body):
            if not isinstance(child, ast.Attribute):
                continue
            if not isinstance(child.value, ast.Name) or child.value.id not in arg_names:
                continue
            key = (child.attr, f"{child.value.id}.{child.attr}")
            if key in seen:
                continue
            seen.add(key)
            result.append({
                "name": child.attr,
                "expression": child.attr,
                "decorator_expression": key[1],
                "line": int(getattr(child, "lineno", getattr(node, "lineno", 0)) or 0),
            })
    return result




def _parameter_accesses(source: str, node: ast.AST) -> list[dict[str, Any]]:
    """Collect ALL identifiers from AST (full collection, not just request params)."""
    accesses: list[dict[str, Any]] = []
    seen: set[str] = set()
    for child in ast.walk(node):
        name = None
        expression = ""
        if isinstance(child, ast.Name):
            name = child.id
            expression = name
        elif isinstance(child, ast.Attribute):
            name = _dotted_name(child)
            expression = name
        elif isinstance(child, ast.Call):
            call = _call_name(child)
            # Also collect string arguments as access keys
            for arg in child.args:
                val = _constant_string(arg)
                if val:
                    key = f"{call}({val})"
                    if key not in seen:
                        seen.add(key)
                        accesses.append({"name": val, "expression": key, "line": int(getattr(child, "lineno", 0) or 0)})
            name = call
            expression = call
        if name and len(name) >= 2 and name.lower() not in {"if", "for", "and", "not", "is", "in", "or", "none", "true", "false", "self", "cls"}:
            if name not in seen:
                seen.add(name)
                accesses.append({"name": name, "expression": expression, "line": int(getattr(child, "lineno", 0) or 0)})
    return accesses


def _call_keyword_names(node: ast.Call) -> list[str]:
    names: list[str] = []
    for keyword in node.keywords:
        if keyword.arg:
            names.append(keyword.arg)
    return names


def _call_names(node: ast.AST) -> list[str]:
    names = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if name:
                names.append(name)
        elif isinstance(child, ast.Attribute):
            name = _dotted_name(child)
            if name and AUTH_TOKEN_RE.search(name):
                names.append(name)
    return sorted(set(names))


def _looks_access_control(text: str, names: Iterable[str] = ()) -> bool:
    joined = text + "\n" + "\n".join(names)
    return bool(AUTH_TOKEN_RE.search(joined))


def _parameter_relevant(name: str, identity_parameters: set[str], access_fields: set[str]) -> bool:
    folded = name.casefold()
    if folded in identity_parameters or folded in access_fields:
        return True
    if STRICT_ACCESS_FIELD_SIGNAL.search(folded):
        return True
    if AUTH_TOKEN_RE.search(folded):
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
    return bool(DENY_OR_REDIRECT_RE.search(joined) or CALL_GUARD_RE.search(joined))
def _serialize_ast(source: str, node: ast.AST, depth: int = 0, max_depth: int = 80) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": type(node).__name__,
        "start_line": getattr(node, "lineno", None),
        "end_line": getattr(node, "end_lineno", None),
    }
    text = _source_segment(source, node)
    if text and len(text) <= 240:
        item["text"] = text
    if depth < max_depth:
        children = [_serialize_ast(source, child, depth + 1, max_depth) for child in ast.iter_child_nodes(node)]
        if children:
            item["children"] = children
    return item


def analyze_python_source(
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
    is_django_project = _is_django_project(source_root)
    identities = {str(item).casefold() for item in (identity_parameters or [])}
    access_fields = {str(item).split(".")[-1].strip().strip("`\"").casefold() for item in (access_control_database_fields or [])}
    name_patterns = [re.compile(str(item), re.I) for item in (validated_function_name_patterns or [])]
    code_patterns = [re.compile(str(item), re.I) for item in (validated_function_code_patterns or [])]

    parse_errors: list[dict[str, Any]] = []
    cst_files: list[dict[str, Any]] = []
    candidate_parameters: list[dict[str, Any]] = []
    parameters: list[dict[str, Any]] = []
    candidate_functions: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []

    for path in _files(source_root, skip_dirs):
        relative = _relative(path, source_root)
        source = path.read_text(encoding="utf-8", errors="ignore")
        lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            parse_errors.append({"path": relative, "line": exc.lineno, "message": exc.msg})
            if is_django_project:
                # Narrow fallback for legacy Python2 Django login views that stdlib ast
                # cannot parse under Python3, e.g. `if user is not None: auth.login(...)`.
                for match in re.finditer(r"\bif\s+([A-Za-z_]\w*)\s+is\s+not\s+None\s*:", source):
                    name = match.group(1)
                    if name.casefold() not in identities:
                        continue
                    body_window = source[match.end():match.end() + 500]
                    if not re.search(r"\bauth\.login\s*\(|\blogin\s*\(", body_window):
                        continue
                    line = source.count("\n", 0, match.start()) + 1
                    item = {
                        "path": relative,
                        "name": name,
                        "expression": name,
                        "line": line,
                        "source": "legacy_django_authenticate_condition",
                    }
                    candidate_parameters.append(item)
                    parameters.append(item)
                    snippets.append({
                        "path": relative,
                        "kind": "condition",
                        "start_line": line,
                        "end_line": line,
                        "condition": match.group(0).rstrip(":"),
                        "functions": ["auth.login"],
                        "variables": [name],
                        "code": "\n".join(lines[max(0, line - 2): min(len(lines), line + 4)]),
                        "access_control_score": 4,
                    })
            continue

        if include_cst:
            cst_files.append(
                {
                    "path": relative,
                    "parser": "python.ast",
                    "note": "Python stdlib ast is used as the normalized syntax tree when tree-sitter-python is unavailable.",
                    "root": _serialize_ast(source, tree),
                }
            )

        for access in _parameter_accesses(source, tree):
            item = {
                "path": relative,
                "name": access["name"],
                "expression": access["expression"],
                "line": access["line"],
                "source": "request_parameter",
            }
            candidate_parameters.append(item)
            if (not is_django_project) and _parameter_relevant(access["name"], identities, access_fields):
                parameters.append(item)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                code = _node_lines(lines, node)
                decorators = [_decorator_name(item) for item in node.decorator_list]
                item = {
                    "path": relative,
                    "kind": "function",
                    "name": node.name,
                    "start_line": int(getattr(node, "lineno", 0) or 0),
                    "end_line": int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
                    "decorators": [item for item in decorators if item],
                    "code": code,
                }
                candidate_functions.append(item)
                field_hit = _field_evidence(code, decorators + [node.name], access_fields)
                deny_hit = _deny_or_redirect_evidence(code, decorators)
                configured_hit = (not is_django_project) and any(pattern.search(node.name) for pattern in name_patterns)
                # Django: only functions with AC decorators are validated
                has_ac_decorator = any(
                    re.search(r"\b(?:login_required|staff_member_required|permission_required|user_passes_test|student_required|lecturer_required|admin_required)\b", d, re.I)
                    for d in decorators
                )
                validated = bool((has_ac_decorator and not is_django_project) or configured_hit)
                django_decorator_params: list[dict[str, Any]] = []
                if is_django_project:
                    for child in ast.walk(node):
                        if _is_user_passes_test_call(child):
                            django_decorator_params.extend(_lambda_permission_attributes(child))
                if django_decorator_params:
                    validated_item = dict(item)
                    validated_item["validation_evidence"] = ["django_decorator_user_passes_test"]
                    functions.append(validated_item)
                    snippets.append({
                        **validated_item,
                        "kind": "validation_function",
                        "function": node.name,
                        "condition": "user_passes_test decorator predicate",
                        "variables": sorted({param["expression"] for param in django_decorator_params}),
                        "access_control_score": 4,
                    })
                    for param in django_decorator_params:
                        parameters.append({
                            "path": relative,
                            "name": param["name"],
                            "expression": param["expression"],
                            "decorator_expression": param["decorator_expression"],
                            "line": param["line"],
                            "source": "django_decorator_user_passes_test",
                        })
                elif validated:
                    functions.append(item)
                    snippets.append({**item, "access_control_score": 3})

            if isinstance(node, ast.Call):
                name = _call_name(node)
                if not name:
                    continue
                text = _source_segment(source, node)
                item = {
                    "path": relative,
                    "kind": "call",
                    "name": name,
                    "start_line": int(getattr(node, "lineno", 0) or 0),
                    "end_line": int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
                    "code": text,
                }
                candidate_functions.append(item)
                keyword_names = _call_keyword_names(node)
                relevant_keywords = [
                    key for key in keyword_names
                    if _parameter_relevant(key, identities, access_fields) or key.casefold() in access_fields
                ]
                orm_visibility_call = (
                    (".objects.filter" in name or name.endswith(".filter") or name.endswith(".exclude") or name.endswith(".get"))
                    and relevant_keywords
                )
                if orm_visibility_call:
                    full_code = _node_lines(lines, node)
                    reduced = _source_segment(source, node.test if hasattr(node, 'test') else node).strip() + " {\n"
                    for line in full_code.splitlines():
                        if DENY_OR_REDIRECT_RE.search(line) or re.search(r"\braise\b|\breturn\b", line):
                            reduced += "    " + line.strip() + "\n"
                    reduced += "}"
                    snippets.append(
                        {
                            "path": relative,
                            "kind": "condition",
                            "start_line": int(getattr(node, "lineno", 0) or 0),
                            "end_line": int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
                            "condition": text,
                            "code": reduced,
                        }
                    )
                    for key in sorted(set(relevant_keywords)):
                        parameters.append({
                            "path": relative,
                            "name": key,
                            "expression": key,
                            "line": int(getattr(node, "lineno", 0) or 0),
                            "source": "database_field",
                        })
                    if not is_django_project:
                        functions.append(item)

            if isinstance(node, (ast.If, ast.IfExp, ast.Assert)):
                test = node.test if hasattr(node, "test") else node
                condition = _source_segment(source, test)
                code = _node_lines(lines, node, context=0)
                names = _call_names(node)
                condition_params = _parameter_accesses(source, test if is_django_project else node)
                relevant_params = [
                    item["expression"]
                    for item in condition_params
                    if _parameter_relevant(str(item["name"]), identities, access_fields)
                ]
                field_hit = bool(relevant_params) or _field_evidence(condition + "\n" + code, names, access_fields)
                deny_hit = _deny_or_redirect_evidence(code, names)
                django_deny_hit = bool(re.search(r"\b(?:PermissionDenied|Http404|HttpResponseForbidden|raise|abort)\b", code + "\n" + "\n".join(names), re.I))
                include_condition = (field_hit and django_deny_hit) if is_django_project else (field_hit or deny_hit)
                if include_condition:
                    reduced_code = condition + " {\n"
                    for line in code.splitlines():
                        if DENY_OR_REDIRECT_RE.search(line) or re.search(r"\braise\b|\breturn\b", line):
                            reduced_code += "    " + line.strip() + "\n"
                    reduced_code += "}"
                    snippets.append(
                        {
                            "path": relative,
                            "kind": "condition",
                            "start_line": int(getattr(node, "lineno", 0) or 0),
                            "end_line": int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
                            "condition": condition,
                            "code": reduced_code,
                        }
                    )
                    if is_django_project:
                        for expr in sorted(set(relevant_params)):
                            parameters.append({
                                "path": relative,
                                "name": expr.split(".")[-1],
                                "expression": expr,
                                "line": int(getattr(node, "lineno", 0) or 0),
                                "source": "terminating_condition",
                            })

        # Decorator-only guards are important in non-Django Python apps.
        # For Django projects, user_passes_test(...) is handled above as the
        # validation function; the decorated view itself is not promoted.
        if not is_django_project:
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                dec_list = getattr(node, "decorator_list", [])
                decorators = [_decorator_name(item) for item in dec_list]
                guard_decorators = [item for item in decorators if AUTH_TOKEN_RE.search(item)]
                if not guard_decorators:
                    continue
                dec_attrs = set()
                for dec_node in dec_list:
                    for child in ast.walk(dec_node):
                        if isinstance(child, ast.Attribute):
                            dec_attrs.add(child.attr)
                snippets.append(
                    {
                        "path": relative,
                        "kind": "condition",
                        "start_line": int(getattr(node, "lineno", 0) or 0),
                        "end_line": int(getattr(node, "lineno", 0) or 0),
                        "condition": "decorators: " + ", ".join(guard_decorators),
                        "functions": guard_decorators,
                        "variables": sorted(dec_attrs),
                        "code": "\n".join(_source_segment(source, item) for item in dec_list),
                        "access_control_score": 4,
                    }
                )
                for attr in dec_attrs:
                    parameters.append({
                        "path": relative,
                        "name": attr,
                        "expression": attr,
                        "line": int(getattr(node, "lineno", 0) or 0),
                        "source": "decorator",
                    })

    def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        result = []
        for item in items:
            key = (
                item.get("path"),
                item.get("kind"),
                item.get("name"),
                item.get("expression"),
                item.get("start_line"),
                item.get("line"),
                item.get("condition"),
            )
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
        "language": "python",
        "parser": "python.ast",
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
