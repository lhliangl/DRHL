from __future__ import annotations

import hashlib
import json
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

from .cst_semantic_analysis import (
    ConditionRecord,
    FileRecord,
    FunctionCallRecord,
    FunctionRecord,
    end_line,
    finalize_analysis,
    line,
    serialize_cst,
    text,
    walk,
    walk_direct_control_region,
)


SOURCE_EXTENSIONS = {".java", ".jsp"}
FUNCTION_NODES = {"method_declaration", "constructor_declaration"}
ACCESS_NODES = {"identifier", "field_access", "array_access"}
STATEMENT_NODES = {"expression_statement", "throw_statement", "return_statement"}
ACCESS_SOURCE_METHODS = {
    "getattribute",
    "getsessionattribute",
    "getparameter",
    "getcookie",
    "isuserinrole",
}
SQL_START = re.compile(r"\b(?:SELECT|UPDATE|DELETE|INSERT)\b", re.I)
SQL_TABLE = re.compile(r"\b(?:FROM|UPDATE|INTO|JOIN)\s+[`\"]?([A-Za-z_]\w*)", re.I)
SQL_FIELD = re.compile(
    r"(?:\bWHERE\b|\bAND\b|\bOR\b|,)\s*[`\"]?(?:[A-Za-z_]\w*[.`\"]+)?"
    r"([A-Za-z_]\w*)[`\"]?\s*(?:=|!=|<>|<|>|LIKE|IN)\s*",
    re.I,
)
ACCESS_DENIAL_TEXT = re.compile(
    r"\b(?:access|permission|authentication|authorization)\s+(?:denied|required|failed)\b|"
    r"\b(?:forbidden|unauthori[sz]ed|securityexception|accessdenied|"
    r"login|log[_ ]?in|sign[_ ]?in)\b",
    re.I,
)
SESSION_ADMIN_ROLE = re.compile(
    r"\bsessionType\s*\.\s*equals\s*\(\s*['\"]admin['\"]\s*\)",
    re.I,
)
SQL_EXPRESSION_MARKER = re.compile(r"__DRHL_SQL_EXPR_(\d+)__")


@dataclass
class ParsedUnit:
    path: str
    source: bytes
    parse_source: bytes
    tree: Any
    jsp_blocks: list[dict[str, Any]]


@dataclass
class MethodScope:
    key: tuple[str, int]
    identity: tuple[str, int]
    path: str
    source: bytes
    node: Any
    parameter_names: list[str]
    record: FileRecord


def _parser() -> Any:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_java is None:
        raise RuntimeError(
            "JSP/Java source analysis requires tree-sitter and tree-sitter-java; run `pip install -e .`"
        ) from _IMPORT_ERROR
    return Parser(Language(tree_sitter_java.language()))


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


def _line_for_offset(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _jsp_java_source(source_text: str) -> tuple[str, list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    for match in re.finditer(r"<%([@!=]?)(.*?)%>", source_text, re.S):
        marker = match.group(1)
        code = match.group(2).strip()
        blocks.append({
            "kind": {"@": "directive", "!": "declaration", "=": "expression"}.get(marker, "scriptlet"),
            "start_line": _line_for_offset(source_text, match.start()),
            "end_line": _line_for_offset(source_text, match.end()),
            "code": code,
            "source_start": match.start(),
            "source_end": match.end(),
        })

    chunks: list[str] = []
    wrapper_bytes = 0

    def append(value: str) -> None:
        nonlocal wrapper_bytes
        chunks.append(value)
        wrapper_bytes += len(value.encode("utf-8"))

    def append_block(block: dict[str, Any], rendered: str) -> None:
        block["parse_start_byte"] = wrapper_bytes
        append(rendered)
        block["parse_end_byte"] = wrapper_bytes
        append("\n")

    append(
        "import java.io.*;\nimport java.sql.*;\nimport javax.servlet.*;\n"
        "import javax.servlet.http.*;\nclass __DRHL_JSP {\n"
        "  HttpServletRequest request;\n  HttpServletResponse response;\n"
        "  HttpSession session;\n  JspWriter out;\n"
    )
    for block in blocks:
        if block["kind"] == "declaration":
            append_block(block, block["code"])
    append("  void __drhl_service() throws Exception {\n")
    expression_index = 0
    for block in blocks:
        if block["kind"] in {"directive", "declaration"}:
            continue
        if block["kind"] == "expression":
            rendered = f"Object __drhl_expr_{expression_index} = ({block['code']});"
            expression_index += 1
        else:
            rendered = block["code"]
        append_block(block, rendered)
    append("  }\n}\n")
    return "".join(chunks), blocks


def _original_window(unit: ParsedUnit, node: Any) -> tuple[int, int, str]:
    if not unit.jsp_blocks:
        return line(node), end_line(node), text(unit.parse_source, node).strip()
    matched = [
        block
        for block in unit.jsp_blocks
        if "parse_start_byte" in block
        and int(block["parse_start_byte"]) < node.end_byte
        and node.start_byte < int(block["parse_end_byte"])
    ]
    if not matched:
        return line(node), end_line(node), text(unit.parse_source, node).strip()
    matched.sort(key=lambda item: int(item["source_start"]))
    source_text = unit.source.decode("utf-8", errors="replace")
    start = int(matched[0]["source_start"])
    end = int(matched[-1]["source_end"])
    return (
        int(matched[0]["start_line"]),
        int(matched[-1]["end_line"]),
        source_text[start:end].strip(),
    )


def _method_name(source: bytes, node: Any) -> str:
    name = node.child_by_field_name("name")
    return text(source, name).strip()


def _string_argument(source: bytes, call: Any) -> str | None:
    arguments = call.child_by_field_name("arguments")
    if arguments is None:
        return None
    for child in arguments.named_children:
        if child.type == "string_literal":
            return text(source, child).strip().strip("'\"")
    return None


def _access_source_expression(source: bytes, call: Any) -> str | None:
    method = _method_name(source, call).casefold()
    if method == "getremoteuser":
        return "remoteUser"
    if method not in ACCESS_SOURCE_METHODS:
        return None
    value = _string_argument(source, call)
    return value or None


def _outer_access(node: Any) -> bool:
    parent = node.parent
    if parent is None:
        return True
    if parent.type in {"field_access", "array_access"}:
        return False
    if parent.type == "method_invocation":
        if parent.child_by_field_name("name") == node or parent.child_by_field_name("object") == node:
            return False
    return True


def _condition_parameters(source: bytes, node: Any | None) -> list[str]:
    if node is None:
        return []
    result: list[str] = []
    for child in walk(node):
        if child.type == "method_invocation":
            access_source = _access_source_expression(source, child)
            if access_source:
                result.append(access_source)
                continue
            obj = child.child_by_field_name("object")
            if obj is not None:
                value = text(source, obj).strip()
                if value:
                    result.append(value)
        elif child.type in {"field_access", "array_access"} and _outer_access(child):
            result.append(text(source, child).strip())
        elif child.type == "identifier" and _outer_access(child):
            result.append(text(source, child).strip())
    return list(dict.fromkeys(item for item in result if item))


def _unwrap_reference(node: Any | None) -> Any | None:
    current = node
    while current is not None and current.type in {
        "parenthesized_expression",
        "cast_expression",
    }:
        named = list(current.named_children)
        current = named[-1] if named else None
    return current


def _direct_reference(source: bytes, node: Any | None) -> str | None:
    current = _unwrap_reference(node)
    if current is None:
        return None
    if current.type in ACCESS_NODES:
        return text(source, current).strip()
    if current.type == "method_invocation":
        return _access_source_expression(source, current)
    return None


def _assignment_pairs(source: bytes, root: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for node in walk(root):
        if node.type == "variable_declarator":
            left = node.child_by_field_name("name")
            right = node.child_by_field_name("value")
        elif node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
        else:
            continue
        left_value = _direct_reference(source, left)
        right_value = _direct_reference(source, right)
        if left_value and right_value:
            pairs.append((left_value, right_value))
    return pairs


def _java_string_value(value: str) -> str:
    try:
        return str(json.loads(value))
    except (json.JSONDecodeError, TypeError):
        return value[1:-1] if len(value) >= 2 else value


def _sql_template(source: bytes, node: Any) -> tuple[str, dict[int, list[str]]]:
    expressions: dict[int, list[str]] = {}

    def render(current: Any) -> str:
        if current.type == "string_literal":
            return _java_string_value(text(source, current))
        if current.type in {"binary_expression", "parenthesized_expression"}:
            return "".join(render(child) for child in current.named_children)
        index = len(expressions)
        expressions[index] = _condition_parameters(source, current)
        return f"__DRHL_SQL_EXPR_{index}__"

    return render(node), expressions


def _predicate_relations(
    sql: str,
    expressions: dict[int, list[str]],
    table: str,
    operation: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    relations: dict[str, list[dict[str, Any]]] = {}
    matches = list(SQL_FIELD.finditer(sql))
    for index, field_match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(sql)
        marker = SQL_EXPRESSION_MARKER.search(sql, field_match.end(), end)
        if marker is None:
            continue
        for expression in expressions.get(int(marker.group(1)), []):
            relations.setdefault(expression, []).append(
                {"table": table, "field": field_match.group(1), **operation}
            )
    return relations


def _database_relations(unit: ParsedUnit) -> dict[str, list[dict[str, Any]]]:
    source = unit.parse_source
    root = unit.tree.root_node
    relations: dict[str, list[dict[str, Any]]] = {}
    prepared: dict[str, dict[str, Any]] = {}

    def operation(node: Any) -> dict[str, Any]:
        start, end, code = _original_window(unit, node)
        return {
            "line": start,
            "start_line": start,
            "end_line": end,
            "code": code,
        }

    for node in walk(root):
        if node.type != "variable_declarator":
            continue
        name = text(source, node.child_by_field_name("name")).strip()
        value = node.child_by_field_name("value")
        if value is None:
            continue
        code = text(source, value)
        if not re.search(r"\bprepareStatement\s*\(", code):
            continue
        sql_match = re.search(r"['\"]([^'\"]*(?:SELECT|UPDATE|DELETE|INSERT)[^'\"]*)['\"]", code, re.I)
        if not sql_match:
            continue
        sql = sql_match.group(1)
        table_match = SQL_TABLE.search(sql)
        table = table_match.group(1) if table_match else ""
        prepared[name] = {
            "table": table,
            "fields": [match.group(1) for match in SQL_FIELD.finditer(sql)],
            "operation": operation(node),
        }

    for node in walk(root):
        if node.type != "method_invocation":
            continue
        method = _method_name(source, node)
        obj = text(source, node.child_by_field_name("object")).strip()
        arguments = node.child_by_field_name("arguments")
        args = list(arguments.named_children) if arguments is not None else []
        if obj in prepared and re.match(r"set(?:String|Int|Long|Object|Boolean)$", method) and len(args) >= 2:
            try:
                position = int(text(source, args[0]).strip()) - 1
            except ValueError:
                position = -1
            prepared_statement = prepared[obj]
            table = str(prepared_statement["table"])
            fields = list(prepared_statement["fields"])
            if 0 <= position < len(fields):
                setter = operation(node)
                preparation = dict(prepared_statement["operation"])
                operation_context = {
                    "line": int(preparation["line"]),
                    "start_line": int(preparation["start_line"]),
                    "end_line": int(setter["end_line"]),
                    "code": "\n".join(
                        part
                        for part in (str(preparation["code"]), str(setter["code"]))
                        if part
                    ),
                }
                for expression in _condition_parameters(source, args[1]):
                    relations.setdefault(expression, []).append(
                        {"table": table, "field": fields[position], **operation_context}
                    )
            continue
        sql = ""
        dynamic_expressions: dict[int, list[str]] = {}
        for argument in args:
            candidate_sql, candidate_expressions = _sql_template(source, argument)
            if SQL_START.search(candidate_sql):
                sql = candidate_sql
                dynamic_expressions = candidate_expressions
                break
        if not sql:
            continue
        table_match = SQL_TABLE.search(sql)
        table = table_match.group(1) if table_match else ""
        for expression, items in _predicate_relations(
            sql, dynamic_expressions, table, operation(node)
        ).items():
            relations.setdefault(expression, []).extend(items)
    return relations


def _configured_match(patterns: list[str] | None, value: str) -> bool:
    return any(re.search(pattern, value, re.I | re.S) for pattern in patterns or [])


def _termination_kind(
    code: str,
    extra_patterns: list[str] | None,
    context: str = "",
) -> str | None:
    if re.match(r"\s*throw\b", code) and ACCESS_DENIAL_TEXT.search(code):
        return "exception"
    if re.search(r"\bSystem\s*\.\s*exit\s*\(", code) and ACCESS_DENIAL_TEXT.search(code):
        return "execution_termination"
    if re.search(r"\bsendError\s*\(\s*(?:40[13]|HttpServletResponse\.SC_(?:UNAUTHORIZED|FORBIDDEN))", code, re.I):
        return "http_denial"
    if re.search(r"\bsetStatus\s*\(\s*(?:40[13]|HttpServletResponse\.SC_(?:UNAUTHORIZED|FORBIDDEN))", code, re.I):
        return "http_denial"
    if re.search(r"\bsendRedirect\s*\(", code) and ACCESS_DENIAL_TEXT.search(code):
        return "redirect"
    if re.search(r"\.forward\s*\(", code) and ACCESS_DENIAL_TEXT.search(code):
        return "redirect"
    if _configured_match(extra_patterns, code):
        return "configured_denial"
    if _configured_match(extra_patterns, context) and re.search(
        r"^\s*(?:return|throw)\b|\b(?:sendRedirect|sendError|forward|System\s*\.\s*exit)\s*\(",
        code,
        re.I | re.S,
    ):
        return "configured_denial"
    return None


def _terminations(
    source: bytes,
    branch: Any | None,
    extra_patterns: list[str] | None,
    context: str = "",
) -> list[dict[str, Any]]:
    if branch is None:
        return []
    result: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for node in walk_direct_control_region(
        branch,
        {"if_statement", "switch_expression", "switch_statement"},
    ):
        if node.type not in STATEMENT_NODES:
            continue
        code = text(source, node).strip()
        kind = _termination_kind(code, extra_patterns, context)
        if not kind:
            continue
        key = (node.start_byte, node.end_byte)
        if key in seen:
            continue
        seen.add(key)
        result.append({"kind": kind, "line": line(node), "code": code})
    return result


def _function_parameters(source: bytes, node: Any) -> list[str]:
    parameters = node.child_by_field_name("parameters")
    if parameters is None:
        return []
    return [text(source, child).strip() for child in parameters.named_children if text(source, child).strip()]


def _function_parameter_names(source: bytes, node: Any) -> list[str]:
    parameters = node.child_by_field_name("parameters")
    if parameters is None:
        return []
    result: list[str] = []
    for parameter in parameters.named_children:
        name = parameter.child_by_field_name("name")
        value = text(source, name).strip()
        if value:
            result.append(value)
    return result


def _argument_nodes(node: Any) -> list[Any]:
    arguments = node.child_by_field_name("arguments")
    return list(arguments.named_children) if arguments is not None else []


def _role_sources(source: bytes, node: Any) -> set[str]:
    roles: set[str] = set()
    for child in walk(node):
        if child.type != "method_invocation":
            continue
        if _method_name(source, child).casefold() != "isuserinrole":
            continue
        role = _string_argument(source, child)
        if role:
            roles.add(role)
    return roles


def _argument_identifiers(source: bytes, node: Any) -> set[str]:
    return {
        text(source, child).strip()
        for child in walk(node)
        if child.type == "identifier" and text(source, child).strip()
    }


def _alias_components(record: FileRecord) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for left, right in record.alias_pairs:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    result: dict[str, set[str]] = {}
    for value in adjacency:
        if value in result:
            continue
        pending = [value]
        component: set[str] = set()
        while pending:
            current = pending.pop()
            if current in component:
                continue
            component.add(current)
            pending.extend(adjacency.get(current, ()))
        for member in component:
            result[member] = component
    return result


def _apply_interprocedural_role_aliases(
    units: list[tuple[ParsedUnit, FileRecord]],
) -> None:
    methods: list[MethodScope] = []
    methods_by_key: dict[tuple[str, int], list[MethodScope]] = {}
    method_by_identity: dict[tuple[str, int], MethodScope] = {}
    for unit, record in units:
        for node in walk(unit.tree.root_node):
            if node.type not in FUNCTION_NODES:
                continue
            names = _function_parameter_names(unit.parse_source, node)
            scope = MethodScope(
                key=(_method_name(unit.parse_source, node).casefold(), len(names)),
                identity=(unit.path, node.start_byte),
                path=unit.path,
                source=unit.parse_source,
                node=node,
                parameter_names=names,
                record=record,
            )
            methods.append(scope)
            methods_by_key.setdefault(scope.key, []).append(scope)
            method_by_identity[scope.identity] = scope

    calls: list[tuple[MethodScope | None, list[MethodScope], list[Any], bytes]] = []
    for unit, _record in units:
        for node in walk(unit.tree.root_node):
            if node.type != "method_invocation":
                continue
            arguments = _argument_nodes(node)
            targets = methods_by_key.get(
                (_method_name(unit.parse_source, node).casefold(), len(arguments)), []
            )
            if not targets:
                continue
            parent = node.parent
            while parent is not None and parent.type not in FUNCTION_NODES:
                parent = parent.parent
            caller = (
                method_by_identity.get((unit.path, parent.start_byte))
                if parent is not None
                else None
            )
            calls.append((caller, targets, arguments, unit.parse_source))

    roles_by_method: dict[tuple[str, int], dict[str, set[str]]] = {
        method.identity: {name: set() for name in method.parameter_names}
        for method in methods
    }
    aliases_by_record = {
        id(record): _alias_components(record)
        for _unit, record in units
    }
    changed = True
    while changed:
        changed = False
        for caller, targets, arguments, source in calls:
            caller_roles = roles_by_method.get(caller.identity, {}) if caller else {}
            caller_aliases = aliases_by_record.get(id(caller.record), {}) if caller else {}
            for position, argument in enumerate(arguments):
                roles = _role_sources(source, argument)
                identifiers = _argument_identifiers(source, argument)
                for parameter, parameter_roles in caller_roles.items():
                    component = caller_aliases.get(parameter, {parameter})
                    if identifiers & component:
                        roles.update(parameter_roles)
                if not roles:
                    continue
                for target in targets:
                    if position >= len(target.parameter_names):
                        continue
                    parameter = target.parameter_names[position]
                    destination = roles_by_method[target.identity][parameter]
                    before = len(destination)
                    destination.update(roles)
                    changed = changed or len(destination) != before

    for method in methods:
        for parameter, roles in roles_by_method[method.identity].items():
            for role in sorted(roles, key=str.casefold):
                method.record.alias_pairs.append((parameter, role))
                evidence = {
                    "kind": "java_jsp_role_source",
                    "source": "isUserInRole",
                    "role": role,
                }
                component = aliases_by_record[id(method.record)].get(parameter, {parameter})
                for condition in method.record.conditions:
                    if not (
                        method.node.start_byte <= condition.start_byte
                        and condition.end_byte <= method.node.end_byte
                        and set(condition.parameters) & component
                    ):
                        continue
                    if evidence not in condition.semantic_evidence:
                        condition.semantic_evidence.append(dict(evidence))


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
    termination_patterns: list[str] | None = None,
) -> dict[str, Any]:
    del identity_parameters, database_schema, validated_function_name_patterns, validated_function_code_patterns
    parser = _parser()
    source_root = root.resolve()
    skipped = {item.casefold() for item in (skip_dirs or [".git", "vendor", "venv", ".venv", "target", "build"])}
    parsed_files: list[FileRecord] = []
    parsed_units: list[tuple[ParsedUnit, FileRecord]] = []
    cst_files: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for file_path in sorted(source_root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if _skip_path(file_path, source_root, skipped):
            continue
        relative = file_path.relative_to(source_root).as_posix()
        source = file_path.read_bytes()
        source_text = source.decode("utf-8", errors="replace")
        parse_text, jsp_blocks = _jsp_java_source(source_text) if file_path.suffix.lower() == ".jsp" else (source_text, [])
        parse_source = parse_text.encode("utf-8", errors="replace")
        tree = parser.parse(parse_source)
        unit = ParsedUnit(relative, source, parse_source, tree, jsp_blocks)
        if include_cst:
            cst_files.append(
                {
                    "path": relative,
                    "encoding": "utf-8",
                    "size_bytes": len(source),
                    "sha256": hashlib.sha256(source).hexdigest(),
                    "parser_source": "jsp-scriptlet-java-wrapper" if jsp_blocks else "java",
                    "has_error": bool(tree.root_node.has_error),
                    "jsp_blocks": jsp_blocks,
                    "root": serialize_cst(parse_source, tree.root_node),
                }
            )
        for node in walk(tree.root_node):
            if node.type == "ERROR" or bool(getattr(node, "is_error", False)):
                parse_errors.append(
                    {"path": relative, "line": line(node), "message": f"parse error near: {text(parse_source, node)[:120]}"}
                )

        record = FileRecord(path=relative)
        record.alias_pairs = _assignment_pairs(parse_source, tree.root_node)
        record.database_relations = _database_relations(unit)
        for node in walk(tree.root_node):
            if node.type == "if_statement":
                condition = node.child_by_field_name("condition")
                consequence = node.child_by_field_name("consequence")
                alternative = node.child_by_field_name("alternative")
                branches = [branch for branch in (consequence, alternative) if branch is not None and branch.type != "if_statement"]
                condition_code = text(parse_source, condition).strip()
                if not condition_code:
                    continue
                start, end, original = _original_window(unit, node)
                record.conditions.append(
                    ConditionRecord(
                        path=relative,
                        condition=condition_code,
                        parameters=_condition_parameters(parse_source, condition),
                        body=original,
                        terminations=[
                            term
                            for branch in branches
                            for term in _terminations(
                                parse_source,
                                branch,
                                termination_patterns,
                                f"{condition_code}\n{text(parse_source, branch)}",
                            )
                        ],
                        start_line=start,
                        end_line=end,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        code=original,
                        semantic_evidence=(
                            [
                                {
                                    "kind": "java_jsp_session_admin_role",
                                    "line": start,
                                    "condition": condition_code,
                                }
                            ]
                            if SESSION_ADMIN_ROLE.search(condition_code)
                            else []
                        ),
                    )
                )
            elif node.type in FUNCTION_NODES:
                name = _method_name(parse_source, node) or "<anonymous>"
                if name == "__drhl_service":
                    continue
                body = node.child_by_field_name("body")
                start, end, original = _original_window(unit, node)
                record.functions.append(
                    FunctionRecord(
                        path=relative,
                        name=name,
                        parameters=_function_parameters(parse_source, node),
                        body=text(parse_source, body).strip(),
                        code=original,
                        start_line=start,
                        end_line=end,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                    )
                )
            elif node.type == "method_invocation":
                name = _method_name(parse_source, node)
                if name:
                    start, end, original = _original_window(unit, node)
                    record.function_calls.append(
                        FunctionCallRecord(
                            path=relative,
                            name=name,
                            code=original,
                            start_line=start,
                            end_line=end,
                            start_byte=node.start_byte,
                            end_byte=node.end_byte,
                        )
                    )
        parsed_files.append(record)
        parsed_units.append((unit, record))

    _apply_interprocedural_role_aliases(parsed_units)

    return finalize_analysis(
        language=language,
        parser_name="tree-sitter-java",
        files=parsed_files,
        access_control_database_fields=access_control_database_fields,
        parse_errors=parse_errors,
        cst_files=cst_files,
    )
