from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

try:
    from tree_sitter import Language, Parser
    import tree_sitter_go
except ImportError as exc:  # pragma: no cover
    Language = Parser = None  # type: ignore[assignment]
    tree_sitter_go = None
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


FUNCTION_NODES = {"function_declaration", "method_declaration"}
ACCESS_NODES = {"identifier", "selector_expression", "index_expression"}
ASSIGNMENT_NODES = {"short_var_declaration", "assignment_statement", "var_spec"}
STATEMENT_NODES = {"expression_statement", "return_statement"}
SQL_START = re.compile(r"\b(?:SELECT|UPDATE|DELETE|INSERT)\b", re.I)
SQL_TABLE = re.compile(r"\b(?:FROM|UPDATE|INTO|JOIN)\s+[`\"]?([A-Za-z_]\w*)", re.I)
SQL_FIELD = re.compile(
    r"(?:\bWHERE\b|\bAND\b|\bOR\b|,)\s*[`\"]?(?:[A-Za-z_]\w*[.`\"]+)?"
    r"([A-Za-z_]\w*)[`\"]?\s*(?:=|!=|<>|<|>|LIKE|IN)\s*",
    re.I,
)
DENIAL_CALL = re.compile(
    r"(?:^|\.)(?:Error|Redirect|Abort|AbortWithStatus|AbortWithStatusJSON|Forbidden|"
    r"Unauthorized|Panic|Fatal|Fatalf)$",
    re.I,
)
ACCESS_DENIAL_TEXT = re.compile(
    r"\b(?:access|permission|authentication|authorization)\s+(?:denied|required|failed)\b|"
    r"\b(?:forbidden|unauthori[sz]ed|login|log[_ ]?in|sign[_ ]?in)\b",
    re.I,
)
NON_PARAMETER_CALLS = {"append", "cap", "close", "copy", "delete", "len", "make", "new"}


def _parser() -> Any:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_go is None:
        raise RuntimeError(
            "Go source analysis requires tree-sitter and tree-sitter-go; run `pip install -e .`"
        ) from _IMPORT_ERROR
    return Parser(Language(tree_sitter_go.language()))


def _files(root: Path, skip_dirs: Iterable[str] | None = None) -> list[Path]:
    skipped = {str(item).casefold() for item in (skip_dirs or [])}
    result: list[Path] = []
    for path in root.rglob("*.go"):
        if not path.is_file() or path.name.endswith("_test.go"):
            continue
        if {part.casefold() for part in path.relative_to(root).parts[:-1]} & skipped:
            continue
        result.append(path.resolve())
    return sorted(result)


def _outer_access(node: Any) -> bool:
    parent = node.parent
    if parent is None:
        return True
    if parent.type in {"selector_expression", "index_expression"}:
        return False
    if parent.type == "call_expression" and parent.child_by_field_name("function") == node:
        return False
    return True


def _condition_parameters(source: bytes, node: Any | None) -> list[str]:
    if node is None:
        return []
    result: list[str] = []
    for child in walk(node):
        if child.type in {"selector_expression", "index_expression"} and _outer_access(child):
            result.append(text(source, child).strip())
        elif child.type == "call_expression":
            function = text(source, child.child_by_field_name("function")).strip()
            if function and function.rsplit(".", 1)[-1].casefold() not in NON_PARAMETER_CALLS:
                result.append(function)
        elif child.type == "identifier" and _outer_access(child):
            result.append(text(source, child).strip())
    return list(dict.fromkeys(item for item in result if item))


def _direct_reference(source: bytes, node: Any | None) -> str | None:
    if node is None:
        return None
    current = node
    while current.type in {"expression_list", "parenthesized_expression"} and len(current.named_children) == 1:
        current = current.named_children[0]
    if current.type in ACCESS_NODES:
        return text(source, current).strip()
    return None


def _assignment_pairs(source: bytes, root: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for node in walk(root):
        if node.type not in ASSIGNMENT_NODES:
            continue
        left = node.child_by_field_name("left") or node.child_by_field_name("name")
        right = node.child_by_field_name("right") or node.child_by_field_name("value")
        left_value = _direct_reference(source, left)
        right_value = _direct_reference(source, right)
        if left_value and right_value:
            pairs.append((left_value, right_value))
    return pairs


def _database_relations(source: bytes, root: Any) -> dict[str, list[dict[str, Any]]]:
    relations: dict[str, list[dict[str, Any]]] = {}
    for node in walk(root):
        if node.type != "call_expression":
            continue
        function = text(source, node.child_by_field_name("function")).strip()
        arguments = node.child_by_field_name("arguments")
        if arguments is None:
            continue
        named_args = list(arguments.named_children)
        if not named_args:
            continue
        method = function.rsplit(".", 1)[-1].casefold()
        if method == "where":
            sql = text(source, named_args[0]).strip().strip('`"')
            fields = [match.group(1) for match in SQL_FIELD.finditer("WHERE " + sql)]
            values = [expr for arg in named_args[1:] for expr in _condition_parameters(source, arg)]
            for field_name, expression in zip(fields, values):
                relations.setdefault(expression, []).append(
                    {
                        "table": "",
                        "field": field_name,
                        "line": line(node),
                        "start_line": line(node),
                        "end_line": end_line(node),
                        "code": text(source, node).strip(),
                    }
                )
            continue
        if method not in {"query", "queryrow", "exec", "select", "get"}:
            continue
        sql = text(source, named_args[0]).strip().strip('`"')
        if not SQL_START.search(sql):
            continue
        table_match = SQL_TABLE.search(sql)
        table = table_match.group(1) if table_match else ""
        fields = [match.group(1) for match in SQL_FIELD.finditer(sql)]
        values = [expr for arg in named_args[1:] for expr in _condition_parameters(source, arg)]
        for field_name, expression in zip(fields, values):
            relations.setdefault(expression, []).append(
                {
                    "table": table,
                    "field": field_name,
                    "line": line(node),
                    "start_line": line(node),
                    "end_line": end_line(node),
                    "code": text(source, node).strip(),
                }
            )
    return relations


def _configured_match(patterns: list[str] | None, value: str) -> bool:
    return any(re.search(pattern, value, re.I | re.S) for pattern in patterns or [])


def _termination_kind(
    code: str,
    extra_patterns: list[str] | None,
    context: str = "",
) -> str | None:
    if re.search(r"\b(?:StatusForbidden|StatusUnauthorized|StatusProxyAuthRequired)\b", code):
        return "http_denial"
    call_match = re.search(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\(", code)
    if call_match and DENIAL_CALL.search(call_match.group(1)):
        is_redirect = call_match.group(1).casefold().endswith("redirect")
        explicit_denial_call = bool(
            re.search(r"(?:^|\.)(?:Forbidden|Unauthorized|AbortWithStatus(?:JSON)?)$", call_match.group(1), re.I)
        )
        if explicit_denial_call or ACCESS_DENIAL_TEXT.search(code):
            return "redirect" if is_redirect else "denial"
    if _configured_match(extra_patterns, code):
        return "configured_denial"
    if _configured_match(extra_patterns, context) and (
        re.match(r"\s*return\b", code, re.I)
        or bool(call_match and DENIAL_CALL.search(call_match.group(1)))
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
        {"if_statement", "expression_switch_statement", "type_switch_statement"},
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


def _if_record(
    source: bytes, relative: str, node: Any, termination_patterns: list[str] | None
) -> ConditionRecord | None:
    condition = node.child_by_field_name("condition")
    consequence = node.child_by_field_name("consequence")
    alternative = node.child_by_field_name("alternative")
    branches = [branch for branch in (consequence, alternative) if branch is not None and branch.type != "if_statement"]
    condition_code = text(source, condition).strip()
    if not condition_code:
        return None
    return ConditionRecord(
        path=relative,
        condition=condition_code,
        parameters=_condition_parameters(source, condition),
        body="\n".join(text(source, branch).strip() for branch in branches),
        terminations=[
            term
            for branch in branches
            for term in _terminations(
                source,
                branch,
                termination_patterns,
                f"{condition_code}\n{text(source, branch)}",
            )
        ],
        start_line=line(node),
        end_line=end_line(node),
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        code=text(source, node).strip(),
    )


def _switch_records(
    source: bytes, relative: str, node: Any, termination_patterns: list[str] | None
) -> list[ConditionRecord]:
    value = node.child_by_field_name("value")
    value_code = text(source, value).strip()
    result: list[ConditionRecord] = []
    for case in node.named_children:
        if case.type not in {"expression_case", "default_case"}:
            continue
        case_values = case.named_children[0] if case.type == "expression_case" and case.named_children else None
        case_code = text(source, case_values).strip() if case_values is not None else "default"
        condition = f"{value_code} == {case_code}" if value_code else case_code
        parameters = _condition_parameters(source, value)
        if case_values is not None:
            parameters.extend(_condition_parameters(source, case_values))
        result.append(
            ConditionRecord(
                path=relative,
                condition=condition,
                parameters=list(dict.fromkeys(parameters)),
                body=text(source, case).strip(),
                terminations=_terminations(
                    source,
                    case,
                    termination_patterns,
                    f"{condition}\n{text(source, case)}",
                ),
                start_line=line(case),
                end_line=end_line(case),
                start_byte=case.start_byte,
                end_byte=case.end_byte,
                code=text(source, case).strip(),
            )
        )
    return result


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
    termination_patterns: list[str] | None = None,
) -> dict[str, Any]:
    del identity_parameters, database_schema, validated_function_name_patterns, validated_function_code_patterns
    parser = _parser()
    source_root = Path(root).resolve()
    parsed_files: list[FileRecord] = []
    cst_files: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for path in _files(source_root, skip_dirs):
        relative = path.relative_to(source_root).as_posix()
        source = path.read_bytes()
        tree = parser.parse(source)
        if include_cst:
            cst_files.append(
                {
                    "path": relative,
                    "encoding": "utf-8",
                    "size_bytes": len(source),
                    "sha256": hashlib.sha256(source).hexdigest(),
                    "has_error": bool(tree.root_node.has_error),
                    "root": serialize_cst(source, tree.root_node),
                }
            )
        for node in walk(tree.root_node):
            if node.type == "ERROR" or bool(getattr(node, "is_error", False)):
                parse_errors.append(
                    {"path": relative, "line": line(node), "message": f"parse error near: {text(source, node)[:120]}"}
                )

        record = FileRecord(path=relative)
        record.alias_pairs = _assignment_pairs(source, tree.root_node)
        record.database_relations = _database_relations(source, tree.root_node)
        for node in walk(tree.root_node):
            if node.type == "if_statement":
                condition = _if_record(source, relative, node, termination_patterns)
                if condition is not None:
                    record.conditions.append(condition)
            elif node.type == "expression_switch_statement":
                record.conditions.extend(_switch_records(source, relative, node, termination_patterns))
            elif node.type in FUNCTION_NODES:
                name = text(source, node.child_by_field_name("name")).strip() or "<anonymous>"
                body = node.child_by_field_name("body")
                record.functions.append(
                    FunctionRecord(
                        path=relative,
                        name=name,
                        parameters=_function_parameters(source, node),
                        body=text(source, body).strip(),
                        code=text(source, node).strip(),
                        start_line=line(node),
                        end_line=end_line(node),
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                    )
                )
            elif node.type == "call_expression":
                function = text(source, node.child_by_field_name("function")).strip()
                if function:
                    record.function_calls.append(
                        FunctionCallRecord(
                            path=relative,
                            name=function,
                            code=text(source, node).strip(),
                            start_line=line(node),
                            end_line=end_line(node),
                            start_byte=node.start_byte,
                            end_byte=node.end_byte,
                        )
                    )
        parsed_files.append(record)

    return finalize_analysis(
        language="go",
        parser_name="tree-sitter-go",
        files=parsed_files,
        access_control_database_fields=access_control_database_fields,
        parse_errors=parse_errors,
        cst_files=cst_files,
    )
