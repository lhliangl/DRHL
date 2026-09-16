from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

try:
    from tree_sitter import Language, Parser
    import tree_sitter_python
except ImportError as exc:  # pragma: no cover
    Language = Parser = None  # type: ignore[assignment]
    tree_sitter_python = None
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


CONTROL_NODES = {"if_statement", "elif_clause", "conditional_expression", "assert_statement"}
FUNCTION_NODES = {"function_definition"}
ASSIGNMENT_NODES = {"assignment", "named_expression"}
ACCESS_NODES = {"identifier", "attribute", "subscript"}
STATEMENT_NODES = {"return_statement", "raise_statement", "expression_statement"}
SQL_START = re.compile(r"\b(?:SELECT|UPDATE|DELETE|INSERT)\b", re.I)
SQL_TABLE = re.compile(r"\b(?:FROM|UPDATE|INTO|JOIN)\s+[`\"]?([A-Za-z_]\w*)", re.I)
SQL_FIELD = re.compile(
    r"(?:\bWHERE\b|\bAND\b|\bOR\b|,)\s*[`\"]?(?:[A-Za-z_]\w*[.`\"]+)?"
    r"([A-Za-z_]\w*)[`\"]?\s*(?:=|!=|<>|<|>|LIKE|IN)\s*",
    re.I,
)
DENIAL_CALL = re.compile(
    r"(?:^|\.)(?:abort|redirect|permissiondenied|http404|httpresponseforbidden|"
    r"forbidden|unauthorized|deny|exit|quit)$",
    re.I,
)
ACCESS_DENIAL_TEXT = re.compile(
    r"\b(?:access|permission|authentication|authorization)\s+(?:denied|required|failed)\b|"
    r"\b(?:forbidden|unauthori[sz]ed|not[_ ]authenticated|not[_ ]authorized)\b|"
    r"\b(?:login|log[_ ]?in|sign[_ ]?in)\b",
    re.I,
)
NON_PARAMETER_CALLS = {
    "all",
    "any",
    "bool",
    "dict",
    "hasattr",
    "isinstance",
    "len",
    "list",
    "set",
    "str",
    "tuple",
}
DJANGO_ACCESS_PARAMETER = re.compile(
    r"(?:^|\.)(?:user(?:\.id)?|is_staff|is_superuser|is_active|is_student|"
    r"is_lecturer|is_parent|is_dep_head|is_authenticated|has_perm)$",
    re.I,
)


def _parser() -> Any:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_python is None:
        raise RuntimeError(
            "Python source analysis requires tree-sitter and tree-sitter-python; run `pip install -e .`"
        ) from _IMPORT_ERROR
    return Parser(Language(tree_sitter_python.language()))


def _files(root: Path, skip_dirs: Iterable[str] | None = None) -> list[Path]:
    skipped = {str(item).casefold() for item in (skip_dirs or [])}
    result: list[Path] = []
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if {part.casefold() for part in path.relative_to(root).parts[:-1]} & skipped:
            continue
        result.append(path.resolve())
    return sorted(result)


def _outer_access(node: Any) -> bool:
    parent = node.parent
    if parent is None:
        return True
    if parent.type in {"attribute", "subscript"}:
        return False
    if parent.type == "call" and parent.child_by_field_name("function") == node:
        return False
    return True


def _condition_parameters(source: bytes, node: Any | None) -> list[str]:
    if node is None:
        return []
    result: list[str] = []
    for child in walk(node):
        if child.type in {"attribute", "subscript"} and _outer_access(child):
            result.append(text(source, child).strip())
        elif child.type == "call":
            function = child.child_by_field_name("function")
            value = text(source, function).strip()
            if value and value.rsplit(".", 1)[-1].casefold() not in NON_PARAMETER_CALLS:
                result.append(value)
        elif child.type == "identifier" and _outer_access(child):
            result.append(text(source, child).strip())
    return list(dict.fromkeys(item for item in result if item))


def _direct_reference(source: bytes, node: Any | None) -> str | None:
    current = node
    while current is not None and current.type == "parenthesized_expression":
        named = list(current.named_children)
        current = named[-1] if named else None
    if current is None:
        return None
    if current.type in ACCESS_NODES:
        return text(source, current).strip()
    if current.type == "call":
        function = text(source, current.child_by_field_name("function")).strip()
        arguments = current.child_by_field_name("arguments")
        string_arg = None
        if arguments is not None:
            string_arg = next(
                (
                    text(source, child).strip("'\"")
                    for child in arguments.named_children
                    if child.type in {"string", "concatenated_string"}
                ),
                None,
            )
        if string_arg and re.search(
            r"(?:session|request|cookie|context).*\.(?:get|pop|value)$", function, re.I
        ):
            return f"{function.rsplit('.', 1)[0]}.{string_arg}"
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


def _call_name(source: bytes, call: Any) -> str:
    return text(source, call.child_by_field_name("function")).strip()


def _django_access_parameters(parameters: list[str]) -> list[str]:
    selected = [item for item in parameters if DJANGO_ACCESS_PARAMETER.search(item)]
    return list(dict.fromkeys(selected))


def _django_user_passes_test_record(
    source: bytes, relative: str, node: Any
) -> ConditionRecord | None:
    if _call_name(source, node).rsplit(".", 1)[-1].casefold() != "user_passes_test":
        return None
    arguments = node.child_by_field_name("arguments")
    if arguments is None:
        return None
    predicate = next(
        (
            child
            for child in arguments.named_children
            if child.type == "lambda" and child.child_by_field_name("body") is not None
        ),
        None,
    )
    if predicate is None:
        return None
    body = predicate.child_by_field_name("body")
    condition = text(source, body).strip()
    parameters = _django_access_parameters(_condition_parameters(source, body))
    if not condition or not parameters:
        return None
    # The lambda argument is the current Django principal.  Preserve that
    # framework-level identity alongside the concrete role/permission fields.
    parameters.insert(0, "request.user")
    code = text(source, node).strip()
    return ConditionRecord(
        path=relative,
        condition=condition,
        parameters=list(dict.fromkeys(parameters)),
        body=code,
        terminations=[
            {
                "kind": "django_user_passes_test",
                "line": line(node),
                "code": code,
                "is_statement": False,
            }
        ],
        start_line=line(node),
        end_line=end_line(node),
        start_byte=node.start_byte,
        end_byte=node.end_byte,
        code=code,
    )


def _django_declarative_filter_record(
    source: bytes,
    relative: str,
    node: Any,
    configured_fields: set[str],
) -> tuple[ConditionRecord, list[tuple[str, dict[str, Any]]]] | None:
    match = re.fullmatch(
        r"([A-Za-z_]\w*)\.objects\.(?:filter|exclude|get)",
        _call_name(source, node),
        re.I,
    )
    arguments = node.child_by_field_name("arguments")
    if match is None or arguments is None:
        return None
    model = match.group(1)
    relations: list[tuple[str, dict[str, Any]]] = []
    for argument in arguments.named_children:
        if argument.type != "keyword_argument":
            continue
        name_node = argument.child_by_field_name("name")
        field_name = text(source, name_node).strip().split("__", 1)[0]
        expression = f"{model}.{field_name}"
        if expression.casefold() not in configured_fields:
            continue
        relations.append(
            (
                expression,
                {
                    "table": model,
                    "field": field_name,
                    "line": line(node),
                    "start_line": line(node),
                    "end_line": end_line(node),
                    "code": text(source, node).strip(),
                },
            )
        )
    if not relations:
        return None
    code = text(source, node).strip()
    return (
        ConditionRecord(
            path=relative,
            condition=code,
            parameters=list(dict.fromkeys(item[0] for item in relations)),
            body="",
            terminations=[],
            start_line=line(node),
            end_line=end_line(node),
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            code=code,
            is_control=False,
        ),
        relations,
    )
def _database_relations(source: bytes, root: Any) -> dict[str, list[dict[str, Any]]]:
    relations: dict[str, list[dict[str, Any]]] = {}
    for node in walk(root):
        if node.type != "call":
            continue
        name = _call_name(source, node)
        arguments = node.child_by_field_name("arguments")
        if arguments is None:
            continue
        if re.search(r"\.(?:filter|exclude|get|update)$", name, re.I):
            table_match = re.match(r"([A-Za-z_]\w*)\.objects\.", name)
            table = table_match.group(1) if table_match else name.split(".", 1)[0]
            for argument in arguments.named_children:
                if argument.type != "keyword_argument":
                    continue
                field_node = argument.child_by_field_name("name")
                value_node = argument.child_by_field_name("value")
                field_name = text(source, field_node).strip().split("__", 1)[0]
                for expression in _condition_parameters(source, value_node):
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
        if name.rsplit(".", 1)[-1].casefold() not in {"execute", "executemany"}:
            continue
        named_args = list(arguments.named_children)
        if not named_args:
            continue
        sql = text(source, named_args[0]).strip().strip("'\"")
        if not SQL_START.search(sql):
            continue
        table_match = SQL_TABLE.search(sql)
        table = table_match.group(1) if table_match else ""
        fields = [match.group(1) for match in SQL_FIELD.finditer(sql)]
        values: list[str] = []
        for argument in named_args[1:]:
            values.extend(_condition_parameters(source, argument))
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
    lowered = code.casefold()
    if re.search(
        r"\b(?:status(?:_code)?\s*=\s*40[13]|HTTPStatus\.(?:UNAUTHORIZED|FORBIDDEN))\b",
        code,
        re.I,
    ):
        return "http_denial"
    if re.match(r"\s*raise\b", code) and ACCESS_DENIAL_TEXT.search(code):
        return "exception"
    call_match = re.search(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\(", code)
    if call_match and DENIAL_CALL.search(call_match.group(1)):
        if re.search(r"\babort\s*\(\s*40[13]", code, re.I):
            return "http_denial"
        explicit_denial_call = bool(
            re.search(
                r"(?:^|\.)(?:PermissionDenied|HttpResponseForbidden|Forbidden|Unauthorized|Deny)$",
                call_match.group(1),
                re.I,
            )
        )
        if explicit_denial_call or ACCESS_DENIAL_TEXT.search(code):
            return "redirect" if "redirect" in lowered else "denial"
    if re.search(r"\b(?:sys\.)?(?:exit|quit)\s*\(", code, re.I) and ACCESS_DENIAL_TEXT.search(code):
        return "execution_termination"
    if _configured_match(extra_patterns, code):
        return "configured_denial"
    if _configured_match(extra_patterns, context) and re.match(
        r"\s*(?:return|raise)\b|.*\b(?:redirect|abort|exit|quit)\s*\(", code, re.I | re.S
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
    for node in walk_direct_control_region(branch, CONTROL_NODES):
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


def _condition_parts(node: Any) -> tuple[Any | None, list[Any]]:
    if node.type == "assert_statement":
        return (node.named_children[0] if node.named_children else None), []
    condition = node.child_by_field_name("condition")
    consequence = node.child_by_field_name("consequence") or node.child_by_field_name("body")
    branches = [consequence] if consequence is not None else []
    alternative = node.child_by_field_name("alternative")
    if alternative is not None and alternative.type == "else_clause":
        branches.append(alternative)
    return condition, branches


def _function_parameters(source: bytes, node: Any) -> list[str]:
    parameters = node.child_by_field_name("parameters")
    if parameters is None:
        return []
    return [text(source, child).strip() for child in parameters.named_children if text(source, child).strip()]


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
    termination_patterns: list[str] | None = None,
    framework: str | None = None,
    declarative_access_control_fields: list[str] | None = None,
) -> dict[str, Any]:
    del identity_parameters, database_schema, validated_function_name_patterns, validated_function_code_patterns
    django_mode = str(framework or "").casefold() == "django"
    declarative_fields = {
        str(item).strip().casefold()
        for item in (declarative_access_control_fields or [])
        if str(item).strip()
    }
    effective_termination_patterns = list(termination_patterns or [])
    if django_mode:
        effective_termination_patterns.append(
            r"^\s*raise\s+(?:PermissionDenied|Http404)\b"
        )
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
                    {
                        "path": relative,
                        "line": line(node),
                        "message": f"parse error near: {text(source, node)[:120]}",
                    }
                )

        record = FileRecord(path=relative)
        record.alias_pairs = _assignment_pairs(source, tree.root_node)
        record.database_relations = _database_relations(source, tree.root_node)
        for node in walk(tree.root_node):
            if node.type in CONTROL_NODES:
                condition_node, branches = _condition_parts(node)
                condition = text(source, condition_node).strip()
                if not condition:
                    continue
                terminations = [
                    termination
                    for branch in branches
                    for termination in _terminations(
                        source,
                        branch,
                        effective_termination_patterns,
                        f"{condition}\n{text(source, branch)}",
                    )
                ]
                parameters = _condition_parameters(source, condition_node)
                record.conditions.append(
                    ConditionRecord(
                        path=relative,
                        condition=condition,
                        parameters=parameters,
                        body="\n".join(text(source, branch).strip() for branch in branches),
                        terminations=terminations,
                        start_line=line(node),
                        end_line=end_line(node),
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        code=text(source, node).strip(),
                    )
                )
            elif node.type == "call":
                name = _call_name(source, node)
                if name:
                    record.function_calls.append(
                        FunctionCallRecord(
                            path=relative,
                            name=name,
                            code=text(source, node).strip(),
                            start_line=line(node),
                            end_line=end_line(node),
                            start_byte=node.start_byte,
                            end_byte=node.end_byte,
                        )
                    )
                if django_mode:
                    condition = _django_user_passes_test_record(source, relative, node)
                    if condition is not None:
                        record.conditions.append(condition)
                    declarative = _django_declarative_filter_record(
                        source, relative, node, declarative_fields
                    )
                    if declarative is not None:
                        condition, relations = declarative
                        record.conditions.append(condition)
                        for expression, relation in relations:
                            record.database_relations.setdefault(expression, []).append(relation)
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
        parsed_files.append(record)

    return finalize_analysis(
        language="python",
        parser_name="tree-sitter-python",
        files=parsed_files,
        access_control_database_fields=access_control_database_fields,
        parse_errors=parse_errors,
        cst_files=cst_files,
    )
