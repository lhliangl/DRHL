from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from tree_sitter import Language, Parser
    import tree_sitter_java
except ImportError as exc:  # pragma: no cover
    Language = Parser = None  # type: ignore[assignment]
    tree_sitter_java = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


SOURCE_EXTENSIONS = {".java", ".jsp"}
JAVA_CONTROL_NODES = {"if_statement", "switch_expression", "switch_statement"}
JAVA_FUNCTION_NODES = {"method_declaration", "constructor_declaration"}
JAVA_CALL_NODES = {"method_invocation"}

ACCESS_SIGNAL = re.compile(
    r"\b(?:session|getSession|getAttribute|setAttribute|isLoggedIn|logged_?in|"
    r"login|auth|authenticate|authorize|authorization|permission|privilege|"
    r"role|admin|administrator|owner|current_?user|user_?id|username|password|"
    r"isUserInRole|getUserPrincipal|principal)\b",
    re.I,
)
STRICT_ACCESS_FIELD_SIGNAL = re.compile(
    r"\b(?:user_?id|userid|uid|owner_?id|author_?id|created_?by|creator_?id|"
    r"member_?id|admin_?id|role|rank_?id|group_?id|usergroup|privilege|"
    r"permission|is_?admin|staff|superuser)\b",
    re.I,
)
PARAMETER_SIGNAL = re.compile(r"\brequest\s*\.\s*getParameter\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
SESSION_SIGNAL = re.compile(r"\bsession\s*\.\s*(?:getAttribute|setAttribute)\s*\(\s*['\"]([^'\"]+)['\"]", re.I)
DENY_OR_REDIRECT = re.compile(
    r"\b(?:sendRedirect|forward|sendError)\s*\(|"
    r"\b(?:throw)\b|access\s+denied|permission\s+denied|unauthori[sz]ed|"
    r"forbidden|wrong\s+password|not\s+allowed|<form[^>]+login|type=[\'\"]password[\'\"]",
    re.I,
)
FUNCTION_NAME_SIGNAL = re.compile(
    r"\b(?:check|is|has|require|ensure|verify|validate).*(?:login|auth|role|admin|permission|owner|user)\b",
    re.I,
)


@dataclass
class ParsedUnit:
    path: str
    source: bytes
    parse_source: bytes
    tree: Any
    jsp_blocks: list[dict[str, Any]]


def _parser() -> Any:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_java is None:
        raise RuntimeError(
            "JSP/Java source analysis requires tree-sitter and tree-sitter-java; "
            "run `pip install tree-sitter-java`"
        ) from _IMPORT_ERROR
    return Parser(Language(tree_sitter_java.language()))


def _walk(node: Any) -> Iterable[Any]:
    yield node
    for child in node.children:
        yield from _walk(child)


def _text(source: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _line(node: Any) -> int:
    return int(node.start_point[0]) + 1


def _end_line(node: Any) -> int:
    return int(node.end_point[0]) + 1


def _skip(path: Path, root: Path, skipped: set[str]) -> bool:
    return bool({part.casefold() for part in path.relative_to(root).parts[:-1]} & skipped)


def _skip_path(path: Path, root: Path, skipped: set[str]) -> bool:
    relative = path.relative_to(root).as_posix().casefold()
    parts = {part.casefold() for part in path.relative_to(root).parts[:-1]}
    for item in skipped:
        normalized = str(item).replace("\\", "/").strip("/").casefold()
        if not normalized:
            continue
        if "/" in normalized:
            if relative.startswith(normalized + "/") or relative == normalized:
                return True
        elif normalized in parts:
            return True
    return False


def _clean_java_name(value: str) -> str:
    value = str(value or "").strip().strip("'\"")
    if not value:
        return ""
    value = re.sub(r"\s+", "", value)
    if value.startswith("session."):
        return value.split(".", 1)[1]
    return value


def _is_noise_java_name(value: str) -> bool:
    folded = str(value or "").casefold()
    if not folded or len(folded) < 2:
        return True
    if folded.startswith("__clr") or "clover" in folded or folded in {"lambdainc", "invoke", "iget", "r"}:
        return True
    if folded in {"equals", "equal", "get", "set", "println", "print", "size", "tostring", "string", "integer", "boolean", "request", "response", "session", "out"}:
        return True
    return False


def _is_explicit_access_source(source: str) -> bool:
    return source in {"session_attribute", "session_set_attribute", "remote_user", "role_check", "cookie"}


def _is_accessish_java_param(name: str, aliases: set[str], sources: set[str], identities: set[str], access_fields: set[str]) -> bool:
    folded_values = {_clean_java_name(value).casefold() for value in ({name} | aliases)}
    folded_values = {value for value in folded_values if value and not _is_noise_java_name(value)}
    credential_names = {"password", "passwd", "pass", "pwd", "token", "csrf"}
    value_tails = {value.rsplit(".", 1)[-1] for value in folded_values}
    if value_tails and value_tails <= credential_names:
        return False
    if sources & {"remote_user", "role_check"}:
        return True
    if folded_values & identities or folded_values & access_fields:
        return True
    session_auth_names = {"user", "username", "user_name", "type", "role", "isloggedin", "loggedin", "autologin", "login"}
    if sources & {"session_attribute", "session_set_attribute", "cookie"} and (folded_values & session_auth_names):
        return True
    joined = "\n".join(folded_values)
    return bool(ACCESS_SIGNAL.search(joined) or STRICT_ACCESS_FIELD_SIGNAL.search(joined))


def _register_param(locations: dict[tuple[str, str], list[dict[str, Any]]], path: str, name: str, *, source: str, line: int, aliases: set[str] | None = None) -> None:
    name = _clean_java_name(name)
    if not name or _is_noise_java_name(name):
        return
    item: dict[str, Any] = {"source": source, "line": line}
    if aliases:
        item["aliases"] = sorted({_clean_java_name(alias) for alias in aliases if _clean_java_name(alias)})
    locations.setdefault((path, name), []).append(item)


def _explicit_parameter_scan(unit_path: str, source_text: str, locations: dict[tuple[str, str], list[dict[str, Any]]], assignment_links: dict[tuple[str, str], set[str]]) -> None:
    patterns = [
        (r"(?:request|serverInterface)\s*\.\s*getParameter\s*\(\s*['\"]([^'\"]+)['\"]", "request_parameter"),
        (r"(?:session|request\s*\.\s*getSession\s*\(\s*\)|serverInterface)\s*\.\s*getSessionAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_attribute"),
        (r"(?:session|request\s*\.\s*getSession\s*\(\s*\)|serverInterface)\s*\.\s*setSessionAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_set_attribute"),
        (r"session\s*\.\s*getAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_attribute"),
        (r"session\s*\.\s*setAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_set_attribute"),
        (r"(?:request|serverInterface)\s*\.\s*getCookie\s*\(\s*['\"]([^'\"]+)['\"]", "cookie"),
        (r"(?:request|serverInterface)\s*\.\s*isUserInRole\s*\(\s*['\"]([^'\"]+)['\"]", "role_check"),
    ]
    for pattern, source in patterns:
        for match in re.finditer(pattern, source_text, re.I):
            _register_param(locations, unit_path, match.group(1), source=source, line=_line_for_offset(source_text, match.start()))
    for match in re.finditer(r"(?:request|serverInterface)\s*\.\s*getRemoteUser\s*\(\s*\)", source_text, re.I):
        _register_param(locations, unit_path, "remoteUser", source="remote_user", line=_line_for_offset(source_text, match.start()))
    assignment_patterns = [
        (r"\b(?:String|Object|User|boolean|Boolean)?\s*([A-Za-z_]\w*)\s*=\s*(?:\([^)]*\)\s*)?session\s*\.\s*getAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_attribute"),
        (r"\b(?:String|Object|User|boolean|Boolean)?\s*([A-Za-z_]\w*)\s*=\s*(?:\([^)]*\)\s*)?(?:request\s*\.\s*getSession\s*\(\s*\)|serverInterface)\s*\.\s*getSessionAttribute\s*\(\s*['\"]([^'\"]+)['\"]", "session_attribute"),
        (r"\b(?:String|Object|User)?\s*([A-Za-z_]\w*)\s*=\s*(?:request|serverInterface)\s*\.\s*getRemoteUser\s*\(\s*\)", "remote_user"),
        (r"\b(?:boolean|Boolean)?\s*([A-Za-z_]\w*)\s*=\s*(?:request|serverInterface)\s*\.\s*isUserInRole\s*\(\s*['\"]([^'\"]+)['\"]", "role_check"),
        (r"\b(?:Cookie|String|Object)?\s*([A-Za-z_]\w*)\s*=\s*(?:request|serverInterface)\s*\.\s*getCookie\s*\(\s*['\"]([^'\"]+)['\"]", "cookie"),
    ]
    for pattern, source in assignment_patterns:
        for match in re.finditer(pattern, source_text, re.I):
            lhs, key = match.group(1), match.group(2) if match.lastindex and match.lastindex >= 2 else "remoteUser"
            aliases = {lhs, key}
            if source == "remote_user":
                aliases.add("remoteUser")
            assignment_links.setdefault((unit_path, lhs), set()).update(aliases)
            _register_param(locations, unit_path, key, source=source, line=_line_for_offset(source_text, match.start()), aliases=aliases)


def _line_for_offset(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _jsp_java_source(source_text: str) -> tuple[str, list[dict[str, Any]]]:
    declarations: list[str] = []
    statements: list[str] = []
    blocks: list[dict[str, Any]] = []
    for match in re.finditer(r"<%([@!=]?)(.*?)%>", source_text, re.S):
        marker = match.group(1)
        code = match.group(2).strip()
        block = {
            "kind": {("@"): "directive", ("!"): "declaration", ("="): "expression"}.get(marker, "scriptlet"),
            "start_line": _line_for_offset(source_text, match.start()),
            "end_line": _line_for_offset(source_text, match.end()),
            "code": code,
        }
        blocks.append(block)
        if marker == "@":
            continue
        if marker == "!":
            declarations.append(code)
        elif marker == "=":
            statements.append(f"Object __drhl_expr_{len(statements)} = ({code});")
        else:
            statements.append(code)
    wrapper = (
        "import java.io.*;\n"
        "import java.sql.*;\n"
        "import javax.servlet.*;\n"
        "import javax.servlet.http.*;\n"
        "class __DRHL_JSP {\n"
        "  HttpServletRequest request;\n"
        "  HttpServletResponse response;\n"
        "  HttpSession session;\n"
        "  JspWriter out;\n"
        + "\n".join(declarations)
        + "\n  void __drhl_service() throws Exception {\n"
        + "\n".join(statements)
        + "\n  }\n"
        "}\n"
    )
    return wrapper, blocks


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
        text = _text(source, node).strip()
        if text:
            item["text"] = text[:240]
    elif depth < max_depth:
        item["children"] = [_serialize_cst(source, child, depth + 1, max_depth) for child in node.children]
    else:
        item["children_truncated"] = node.child_count
    return item


def _condition_text(source: bytes, node: Any) -> str:
    condition = node.child_by_field_name("condition")
    if condition is not None:
        return _text(source, condition).strip()
    code = _text(source, node)
    match = re.search(r"\bif\s*\((.*?)\)", code, re.S)
    return match.group(1).strip() if match else code.strip()


def _method_name(source: bytes, node: Any) -> str:
    name = node.child_by_field_name("name")
    if name is not None:
        return _text(source, name).strip()
    match = re.search(r"\b([A-Za-z_]\w*)\s*\(", _text(source, node))
    return match.group(1) if match else "<anonymous>"


def _call_name(source: bytes, node: Any) -> str:
    name = node.child_by_field_name("name")
    if name is not None:
        return _text(source, name).strip()
    match = re.search(r"\.?\s*([A-Za-z_]\w*)\s*\(", _text(source, node))
    return match.group(1) if match else ""


def _variables(code: str) -> list[str]:
    """Extract ALL identifiers from code, not just request/session patterns."""
    values: list[str] = []
    # Method calls: obj.method(args) or method(args) or obj.method
    for match in re.finditer(r"(?:(\w+)\s*\.\s*)?(\w+)\s*\(", code):
        obj = match.group(1)
        method = match.group(2)
        if obj:
            values.append(f"{obj}.{method}")
        else:
            values.append(method)
    # Field accesses: obj.field
    for match in re.finditer(r"(\w+)\s*\.\s*(\w+)(?!\s*\()", code):
        values.append(f"{match.group(1)}.{match.group(2)}")
    # Simple identifiers (variables, parameters)
    for match in re.finditer(r"\b([a-zA-Z_]\w{2,})\b", code):
        token = match.group(1)
        if token.lower() not in {"the", "and", "not", "new", "this", "super", "null", "true", "false",
                                  "int", "long", "void", "class", "public", "private", "protected",
                                  "static", "final", "throws", "import", "package", "return", "if",
                                  "else", "for", "while", "switch", "case", "break", "continue"}:
            values.append(token)
    return sorted(set(values))


def _terminations(code: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for pattern, kind in [
        (r"response\s*\.\s*sendRedirect\s*\((.*?)\)", "redirect"),
        (r"response\s*\.\s*sendError\s*\((.*?)\)", "send_error"),
        (r"\.forward\s*\((.*?)\)", "forward"),
        (r"out\s*\.\s*println\s*\((.*?)\)", "output"),
    ]:
        for match in re.finditer(pattern, code, re.S | re.I):
            result.append({"kind": kind, "code": match.group(0).strip()[:400]})
    if re.search(r"\breturn\b", code):
        result.append({"kind": "return", "code": "return"})
    if re.search(r"\bthrow\b", code):
        result.append({"kind": "throw", "code": "throw"})
    return result


def _line_window(source: bytes, start_line: int, end_line: int, before: int = 20, after: int = 12) -> str:
    lines = source.decode("utf-8", errors="replace").splitlines()
    start = max(1, start_line - before)
    end = min(len(lines), end_line + after)
    return "\n".join(lines[start - 1:end]).strip()


def _nearest_original_line(unit: ParsedUnit, parse_line: int) -> int:
    if not unit.jsp_blocks:
        return parse_line
    scriptlets = [block for block in unit.jsp_blocks if block["kind"] != "directive"]
    if not scriptlets:
        return 1
    return scriptlets[min(len(scriptlets) - 1, max(0, len(scriptlets) // 2))]["start_line"]


def _original_window(unit: ParsedUnit, node: Any) -> tuple[int, int, str]:
    if not unit.jsp_blocks:
        return _line(node), _end_line(node), _text(unit.parse_source, node).strip()
    code = _text(unit.parse_source, node).strip()
    for block in unit.jsp_blocks:
        if block["kind"] == "directive":
            continue
        if code and (code in block["code"] or block["code"] in code):
            return block["start_line"], block["end_line"], block["code"]
    line = _nearest_original_line(unit, _line(node))
    return line, line, _line_window(unit.source, line, line)


def _candidate_parameter(path: str, name: str, locations: list[dict[str, Any]], index: int,
                         extra_aliases: set[str] | None = None) -> dict[str, Any]:
    aliases = [name]
    if extra_aliases:
        aliases.extend(sorted(extra_aliases - {name}))
    return {
        "id": f"{path}:LCP{index}",
        "path": path,
        "expression": name,
        "aliases": aliases,
        "values": [],
        "database_relations": [],
        "sources": sorted({item["source"] for item in locations}),
        "locations": locations,
        "condition_indexes": sorted({int(item["condition_index"]) for item in locations if "condition_index" in item}),
    }


def analyze_java_jsp_source(
    root: Path,
    *,
    language: str = "jsp",
    skip_dirs: list[str] | None = None,
    identity_parameters: list[str] | None = None,
    access_control_database_fields: list[str] | None = None,
    database_schema: Path | None = None,
    include_cst: bool = False,
    validated_function_name_patterns: list[str] | None = None,
    validated_function_code_patterns: list[str] | None = None,
) -> dict[str, Any]:
    del database_schema
    parser = _parser()
    root = root.resolve()
    skipped = {item.casefold() for item in (skip_dirs or [".git", "vendor", "venv", ".venv", "target", "build"])}
    identities = {item.casefold() for item in (identity_parameters or [])}
    access_fields = {str(item).split(".")[-1].strip().strip("`\"").casefold() for item in (access_control_database_fields or [])}
    name_patterns = [re.compile(pattern, re.I) for pattern in (validated_function_name_patterns or [])]
    code_patterns = [re.compile(pattern, re.I | re.S) for pattern in (validated_function_code_patterns or [])]

    parsed_units: list[ParsedUnit] = []
    cst_files: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    candidate_parameters: list[dict[str, Any]] = []
    candidate_functions: list[dict[str, Any]] = []
    validated_parameters: list[dict[str, Any]] = []
    validated_functions: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if _skip_path(file_path, root, skipped):
            continue
        path = file_path.relative_to(root).as_posix()
        source = file_path.read_bytes()
        source_text = source.decode("utf-8", errors="replace")
        jsp_blocks: list[dict[str, Any]] = []
        parse_text = source_text
        if file_path.suffix.lower() == ".jsp":
            parse_text, jsp_blocks = _jsp_java_source(source_text)
        parse_source = parse_text.encode("utf-8", errors="replace")
        tree = parser.parse(parse_source)
        unit = ParsedUnit(path, source, parse_source, tree, jsp_blocks)
        parsed_units.append(unit)
        if tree.root_node.has_error:
            parse_errors.append(path)
        if include_cst:
            cst_files.append({
                "path": path,
                "encoding": "utf-8",
                "size_bytes": len(source),
                "sha256": hashlib.sha256(source).hexdigest(),
                "parser_source": "jsp-scriptlet-java-wrapper" if jsp_blocks else "java",
                "has_error": bool(tree.root_node.has_error),
                "jsp_blocks": jsp_blocks,
                "root": _serialize_cst(parse_source, tree.root_node),
            })

    condition_records: list[dict[str, Any]] = []
    parameter_locations: dict[tuple[str, str], list[dict[str, Any]]] = {}
    validated_function_names: set[str] = set()

    # Track assignments: LHS variable <- RHS session.getAttribute("key") etc.
    assignment_links: dict[tuple[str, str], set[str]] = {}  # (path, lhs_var) -> {session_key, ...}

    for unit in parsed_units:
        _explicit_parameter_scan(unit.path, unit.source.decode("utf-8", errors="replace"), parameter_locations, assignment_links)
        for node in _walk(unit.tree.root_node):
            code = _text(unit.parse_source, node).strip()
            # Track variable declarations and assignments
            if node.type in {"variable_declarator", "assignment_expression"}:
                lhs_name = None
                if node.type == "variable_declarator":
                    name_node = node.child_by_field_name("name")
                    if name_node:
                        lhs_name = _text(unit.parse_source, name_node).strip()
                else:
                    left_node = node.child_by_field_name("left")
                    if left_node:
                        lhs_name = _text(unit.parse_source, left_node).strip()
                if lhs_name and lhs_name not in {"", "if", "for", "while"}:
                    # Find method invocations in the RHS (value/right side)
                    rhs_node = node.child_by_field_name("value") or node.child_by_field_name("right")
                    if rhs_node:
                        for child in _walk(rhs_node):
                            if child.type in JAVA_CALL_NODES:
                                call_code = _text(unit.parse_source, child).strip()
                                args_node = child.child_by_field_name("arguments")
                                if args_node:
                                    for arg in args_node.children:
                                        if arg.type == "string_literal":
                                            arg_val = _text(unit.parse_source, arg).strip().strip("'\"")
                                            if arg_val:
                                                key = (unit.path, lhs_name)
                                                assignment_links.setdefault(key, set()).add(arg_val)
                                                # Also register the session key as a parameter location
                                                session_key = f"session.{arg_val}"
                                                parameter_locations.setdefault((unit.path, session_key), []).append({
                                                    "source": "session",
                                                    "line": _nearest_original_line(unit, _line(node)),
                                                })
            if node.type in JAVA_CONTROL_NODES:
                condition = _condition_text(unit.parse_source, node)
                start_line, end_line, original_code = _original_window(unit, node)
                variables = _variables(condition)
                record = {
                    "path": unit.path,
                    "condition": condition,
                    "variables": variables,
                    "terminations": _terminations(code),
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": original_code,
                }
                condition_index = len(condition_records)
                condition_records.append(record)
                for variable in variables:
                    parameter_locations.setdefault((unit.path, variable), []).append({
                        "source": "conditional",
                        "line": start_line,
                        "condition": condition,
                        "condition_index": condition_index,
                    })
            elif node.type in JAVA_FUNCTION_NODES:
                name = _method_name(unit.parse_source, node)
                if name == "__drhl_service":
                    continue
                start_line, end_line, original_code = _original_window(unit, node)
                candidate_functions.append({
                    "id": f"{unit.path}:LCF{len(candidate_functions) + 1}",
                    "path": unit.path,
                    "name": name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": original_code,
                })
            elif node.type in JAVA_CALL_NODES:
                # Method calls are not promoted to parameters by default; explicit
                # request/session/role/cookie sources are scanned separately.
                pass


    for index, ((path, name), locations) in enumerate(sorted(parameter_locations.items()), start=1):
        # Check if this parameter has session assignment links
        extra_aliases: set[str] = set()
        # Also look up assignment links by the variable name
        for (link_path, lhs_var), keys in assignment_links.items():
            if link_path == path and lhs_var == name:
                extra_aliases.update(keys)
                extra_aliases.update(f"session.{k}" for k in keys)
        candidate = _candidate_parameter(path, name, locations, index, extra_aliases)
        candidate_parameters.append(candidate)
        name_lower = _clean_java_name(name).casefold()
        aliases = {name_lower}
        for location in locations:
            if isinstance(location, dict):
                aliases.update(_clean_java_name(str(alias)).casefold() for alias in location.get("aliases", []))
        aliases.update(_clean_java_name(str(alias)).casefold() for alias in extra_aliases)
        aliases = {alias for alias in aliases if alias and not _is_noise_java_name(alias)}
        credential_names = {"password", "passwd", "pass", "pwd", "token", "csrf"}
        alias_tails = {alias.rsplit(".", 1)[-1] for alias in aliases}
        if alias_tails and alias_tails <= credential_names:
            continue
        sources = {str(location.get("source")) for location in locations if isinstance(location, dict)}
        explicit_source = any(_is_explicit_access_source(source) for source in sources)
        identity_hit = bool(aliases & identities) or any(alias in access_fields for alias in aliases)
        field_hit = identity_hit or any(STRICT_ACCESS_FIELD_SIGNAL.search(alias) for alias in aliases)
        accessish = _is_accessish_java_param(name, aliases, sources, identities, access_fields)
        if explicit_source and accessish:
            validated = dict(candidate)
            evidence = [{"kind": "explicit_access_source"}]
            if field_hit:
                evidence.append({"kind": "access_control_field"})
            validated["validation_evidence"] = evidence
            validated_parameters.append(validated)


    for record in condition_records:
        condition_lower = record["condition"].casefold()
        field_evidence = STRICT_ACCESS_FIELD_SIGNAL.search(record["condition"]) is not None or any(
            field and field in condition_lower for field in access_fields
        )
        has_deny_or_redirect = any(
            item["kind"] in {"redirect", "send_error", "forward", "throw"} for item in record["terminations"]
        ) or DENY_OR_REDIRECT.search(record["code"]) is not None
        if field_evidence and has_deny_or_redirect:
            reduced = f"if ({record['condition']}) {{\n"
            for term in record["terminations"]:
                reduced += "    " + term["code"].strip() + "\n"
            reduced += "}"
            snippets.append({
                "path": record["path"],
                "kind": "conditional",
                "start_line": record["start_line"],
                "end_line": record["end_line"],
                "condition": record["condition"],
                "code": reduced,
            })

    # Standalone Java/JSP validation functions are not promoted unless a future
    # rule proves they encapsulate validated parameters and terminating failure branches.

    for unit in parsed_units:
        for node in _walk(unit.tree.root_node):
            if node.type not in JAVA_CALL_NODES:
                continue
            name = _call_name(unit.parse_source, node)
            if name.casefold() not in validated_function_names:
                continue
            start_line, end_line, original_code = _original_window(unit, node)
            snippets.append({
                "path": unit.path,
                "kind": "guard_call",
                "start_line": start_line,
                "end_line": end_line,
                "function": name,
                "code": original_code,
            })

    snippets = [item for item in snippets if "function" in item or "condition" in item]
    snippets.sort(key=lambda item: (item["path"], item["start_line"], item["kind"]))
    return {
        "schema_version": 3,
        "language": language,
        "parser": "tree-sitter-java",
        "parse_errors": parse_errors,
        "summary": {
            "cst_files": len(parsed_units),
            "candidate_parameters": len(candidate_parameters),
            "candidate_functions": len(candidate_functions),
            "parameters": len(validated_parameters),
            "functions": len(validated_functions),
            "snippets": len(snippets),
        },
        "cst": cst_files,
        "candidate_parameters": candidate_parameters,
        "candidate_functions": candidate_functions,
        "parameters": validated_parameters,
        "functions": validated_functions,
        "snippets": snippets,
    }



