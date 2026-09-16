from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .cst_semantic_analysis import (
    ConditionRecord,
    FileRecord,
    FunctionCallRecord,
    FunctionRecord,
    UnionFind,
    finalize_analysis,
    text,
)
from .php_source_analysis import (
    CONTROL_NODES,
    FUNCTION_NODES,
    _condition_record,
    _call_name,
    _direct_alias_variables,
    _end_line,
    _line,
    _normalize_curly_string_offsets,
    _parser,
    _serialize_cst,
    _sql_relations,
    _statement,
    _text,
    _variables,
    _walk,
)


# Language/runtime predicates consume data but are not themselves candidate
# parameters.  Their operands are still collected from the CST.
NON_PARAMETER_CALLS = {
    "array_key_exists",
    "count",
    "defined",
    "empty",
    "file_exists",
    "in_array",
    "is_array",
    "is_bool",
    "is_file",
    "is_null",
    "is_numeric",
    "is_object",
    "is_readable",
    "isset",
    "mysql_num_rows",
    "mysqli_num_rows",
    "preg_match",
    "sizeof",
    "strlen",
}

SESSION_IDENTITY_KEY = re.compile(
    r"^\$_SESSION\s*\[\s*(['\"]?)(user_id|userid|username)\1\s*\]$",
    re.I,
)


def _function_parameters(source: bytes, node: Any) -> list[str]:
    parameters = node.child_by_field_name("parameters")
    if parameters is None:
        return []
    return [
        _text(source, child).strip()
        for child in parameters.named_children
        if _text(source, child).strip()
    ]


def _condition_parameters(
    source: bytes,
    node: Any,
    semantic_predicates: set[str] | None = None,
) -> list[str]:
    """Return variables plus calls proven to return access-control booleans."""
    result = list(_variables(source, node))
    if semantic_predicates:
        result.extend(
            call
            for call in _condition_calls(source, node)
            if call.casefold() in semantic_predicates
        )
    return list(dict.fromkeys(result))


def _condition_calls(source: bytes, node: Any) -> list[str]:
    result: list[str] = []
    for child in _walk(node):
        if child.type not in {"function_call_expression", "scoped_call_expression"}:
            continue
        name = _call_name(source, child)
        if name:
            result.append(name)
    return list(dict.fromkeys(result))


def _depends_on_alias(expression: str, aliases: set[str]) -> bool:
    value = re.sub(r"\s+", "", expression)
    return any(
        value == alias or value.startswith(alias + "[") or value.startswith(alias + "->")
        for alias in aliases
    )


def _is_access_control_global(expression: str) -> bool:
    value = re.sub(r"\s+", "", expression).upper()
    return any(
        value == name or value.startswith(name + "[")
        for name in ("$_COOKIE", "$_SESSION")
    )


def _boolean_return_expression(code: str) -> bool:
    value = code.strip().rstrip(";").strip()
    if value.casefold().startswith("return"):
        value = value[6:].strip()
    while value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    return bool(
        value.casefold() in {"true", "false"}
        or re.match(r"^(?:!\s*)?(?:isset|empty)\s*\(", value, re.I)
        or re.search(r"===?|!==?|<=|>=|<|>", value)
    )


def _semantic_predicate_functions(source: bytes, function_nodes: list[Any]) -> set[str]:
    """Find functions whose boolean return value is derived from session/cookie state."""
    summaries: dict[str, dict[str, Any]] = {}
    for function_node in function_nodes:
        name_node = function_node.child_by_field_name("name")
        name = _text(source, name_node).strip().casefold()
        body = function_node.child_by_field_name("body")
        if not name or body is None:
            continue
        assignments: list[tuple[list[str], list[str], list[str]]] = []
        returns: list[tuple[str, list[str]]] = []
        for node in _walk(body):
            if node.type in {"assignment_expression", "reference_assignment_expression"}:
                left = _variables(source, node.child_by_field_name("left"))
                right_node = node.child_by_field_name("right")
                right_calls = _condition_calls(source, right_node) if right_node is not None else []
                assignments.append((left, _variables(source, right_node), right_calls))
            elif node.type == "return_statement":
                returns.append((_text(source, node), _variables(source, node)))
        summaries[name] = {"assignments": assignments, "returns": returns}

    carrier_functions: set[str] = set()
    aliases_by_function: dict[str, set[str]] = {}
    changed = True
    while changed:
        changed = False
        for name, summary in summaries.items():
            state_aliases: set[str] = set()
            for left_values, right_values, right_calls in summary["assignments"]:
                derived = any(_is_access_control_global(value) for value in right_values)
                derived = derived or any(
                    _depends_on_alias(value, state_aliases) for value in right_values
                )
                derived = derived or bool(
                    carrier_functions.intersection(call.casefold() for call in right_calls)
                )
                if derived:
                    state_aliases.update(re.sub(r"\s+", "", value) for value in left_values)
            aliases_by_function[name] = state_aliases
            returns_state = any(
                any(_is_access_control_global(value) for value in return_values)
                or any(_depends_on_alias(value, state_aliases) for value in return_values)
                for _, return_values in summary["returns"]
            )
            if returns_state and name not in carrier_functions:
                carrier_functions.add(name)
                changed = True

    predicates: set[str] = set()
    for name in carrier_functions:
        returns = summaries[name]["returns"]
        aliases = aliases_by_function.get(name, set())
        state_return = any(
            any(_is_access_control_global(value) for value in return_values)
            or any(_depends_on_alias(value, aliases) for value in return_values)
            for _, return_values in returns
        )
        if returns and state_return and all(_boolean_return_expression(code) for code, _ in returns):
            predicates.add(name)
    return predicates


def _global_state_key(expression: str) -> str | None:
    value = re.sub(r"\s+", "", expression).replace('"', "'")
    upper = value.upper()
    for name in ("$_COOKIE", "$_SESSION"):
        if upper == name or upper.startswith(name + "["):
            return upper
    return None


def _propagate_global_database_relations(files: list[FileRecord]) -> None:
    """Carry DBMatch evidence assigned to PHP session/cookie state across files."""
    global_relations: dict[str, list[dict[str, Any]]] = {}
    for file_record in files:
        union = UnionFind()
        for left, right in file_record.alias_pairs:
            union.union(left, right)
        for expression in file_record.database_relations:
            union.add(expression)
        for members in union.groups().values():
            relations = [
                relation
                for member in members
                for relation in file_record.database_relations.get(member, [])
            ]
            if not relations:
                continue
            for member in members:
                key = _global_state_key(member)
                if key is None:
                    continue
                target = global_relations.setdefault(key, [])
                for relation in relations:
                    if relation not in target:
                        target.append(relation)

    for file_record in files:
        for condition in file_record.conditions:
            for expression in condition.parameters:
                key = _global_state_key(expression)
                if key is None:
                    continue
                target = file_record.database_relations.setdefault(expression, [])
                for relation in global_relations.get(key, []):
                    if relation not in target:
                        target.append(relation)


def _state_gate(condition: str) -> tuple[str, bool] | None:
    """Return a simple boolean decision variable and its denying value."""
    value = condition.strip()
    while value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    variable = r"(\$[A-Za-z_]\w*)"
    patterns = [
        (rf"^{variable}$", True),
        (rf"^!\s*{variable}$", False),
        (rf"^{variable}\s*(===?|!=|!==)\s*(true|false|1|0)$", None),
    ]
    for pattern, fixed in patterns:
        match = re.match(pattern, value, re.I)
        if not match:
            continue
        if fixed is not None:
            return match.group(1), fixed
        operator = match.group(2)
        literal = match.group(3).casefold()
        expected = literal in {"true", "1"}
        if operator in {"!=", "!=="}:
            expected = not expected
        return match.group(1), expected
    return None


def _direct_assignments(source: bytes, branch: Any | None) -> list[tuple[str, bool]]:
    if branch is None:
        return []
    assignments: list[tuple[str, bool]] = []

    def visit(node: Any):
        if node is not branch and node.type in CONTROL_NODES:
            return
        if node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            left_text = _text(source, left).strip()
            right_text = _text(source, right).strip().casefold()
            if left_text.startswith("$") and right_text in {"true", "false", "1", "0"}:
                assignments.append((left_text, right_text in {"true", "1"}))
        for child in node.named_children:
            visit(child)

    visit(branch)
    return assignments


def _condition_is_excluded(
    source: bytes,
    condition: Any,
    exclude_patterns: list[str] | None,
) -> bool:
    if not exclude_patterns:
        return False
    node = condition.node
    context = "\n".join(
        part
        for part in (
            condition.condition,
            _text(source, node.child_by_field_name("body")),
            _text(source, node.child_by_field_name("alternative")),
        )
        if part
    )
    return any(re.search(pattern, context, re.I | re.S) for pattern in exclude_patterns)


def _propagate_conditional_state(
    source: bytes,
    conditions: list[Any],
    exclude_patterns: list[str] | None = None,
) -> None:
    """Connect a boolean decision flag to the later branch that enforces it."""
    # A plain exit/die is intentionally not a global PHP denial heuristic, but
    # it is an enforcement terminal when guarded by a simple decision flag.
    for condition in conditions:
        if _condition_is_excluded(source, condition, exclude_patterns):
            continue
        gate = _state_gate(condition.condition)
        if gate is None or condition.terminations:
            continue
        state, denying_value = gate
        has_upstream_decision = False
        for source_condition in conditions:
            if source_condition.node.start_byte >= condition.node.start_byte:
                continue
            body = source_condition.node.child_by_field_name("body")
            alternative = source_condition.node.child_by_field_name("alternative")
            assignments = _direct_assignments(source, body) + _direct_assignments(
                source, alternative
            )
            if (state, denying_value) in assignments:
                has_upstream_decision = True
                break
        if not has_upstream_decision:
            continue
        branch = condition.node.child_by_field_name("body")
        if branch is None:
            continue

        def direct_nodes(node: Any):
            yield node
            for child in node.named_children:
                if child.type in CONTROL_NODES:
                    continue
                yield from direct_nodes(child)

        for node in direct_nodes(branch):
            if node.type != "exit_statement":
                continue
            condition.terminations.append(
                {
                    "kind": "execution_termination",
                    "line": _line(node),
                    "code": _text(source, node).strip(),
                    "denial_text": False,
                }
            )

    changed = True
    while changed:
        changed = False
        for target in conditions:
            if _condition_is_excluded(source, target, exclude_patterns):
                continue
            gate = _state_gate(target.condition)
            if gate is None or not target.terminations:
                continue
            state, denying_value = gate
            propagated = [
                {
                    **termination,
                    "kind": "propagated_termination",
                    "via_state": state,
                    "line": int(termination.get("line", target.start_line)),
                }
                for termination in target.terminations
            ]
            for source_condition in conditions:
                if _condition_is_excluded(source, source_condition, exclude_patterns):
                    continue
                if source_condition.node.start_byte >= target.node.start_byte:
                    continue
                body = source_condition.node.child_by_field_name("body")
                alternative = source_condition.node.child_by_field_name("alternative")
                assignments = _direct_assignments(source, body) + _direct_assignments(
                    source, alternative
                )
                if (state, denying_value) not in assignments:
                    continue
                for termination in propagated:
                    if termination not in source_condition.terminations:
                        source_condition.terminations.append(termination)
                        changed = True


def analyze_php_cst_source(
    root: Path,
    *,
    skip_dirs: list[str] | None = None,
    identity_parameters: list[str] | None = None,
    access_control_database_fields: list[str] | None = None,
    database_schema: Path | None = None,
    include_cst: bool = False,
    validated_function_name_patterns: list[str] | None = None,
    validated_function_code_patterns: list[str] | None = None,
    normalize_curly_string_offsets: bool = False,
    termination_patterns: list[str] | None = None,
    termination_exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Tree-sitter PHP adapter for the shared Sections 4.3.1-4.3.3 contract."""
    del identity_parameters, database_schema, validated_function_name_patterns, validated_function_code_patterns
    parser = _parser()
    source_root = root.resolve()
    skipped = {item.casefold() for item in (skip_dirs or [".git", "vendor", "venv", ".venv"])}
    parsed_files: list[FileRecord] = []
    cst_files: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for file_path in sorted(source_root.rglob("*.php")):
        if {part.casefold() for part in file_path.relative_to(source_root).parts[:-1]} & skipped:
            continue
        relative = file_path.relative_to(source_root).as_posix()
        source = file_path.read_bytes()
        if normalize_curly_string_offsets:
            source = _normalize_curly_string_offsets(source)
        tree = parser.parse(source)
        if include_cst:
            cst_files.append(
                {
                    "path": relative,
                    "encoding": "utf-8",
                    "size_bytes": len(source),
                    "sha256": hashlib.sha256(source).hexdigest(),
                    "has_error": bool(tree.root_node.has_error),
                    "root": _serialize_cst(source, tree.root_node),
                }
            )
        for node in _walk(tree.root_node):
            if node.type == "ERROR" or bool(getattr(node, "is_error", False)):
                parse_errors.append(
                    {
                        "path": relative,
                        "line": _line(node),
                        "message": f"parse error near: {_text(source, node)[:120]}",
                    }
                )

        function_nodes = [node for node in _walk(tree.root_node) if node.type in FUNCTION_NODES]
        semantic_predicates = _semantic_predicate_functions(source, function_nodes)

        def scope_key(node: Any) -> str:
            current = node
            while current is not None:
                if current.type in FUNCTION_NODES:
                    return f"function:{current.start_byte}:{current.end_byte}"
                current = current.parent
            return "module"

        records: dict[str, FileRecord] = {"module": FileRecord(path=relative)}
        raw_conditions: dict[str, list[Any]] = {"module": []}
        for function_node in function_nodes:
            key = scope_key(function_node)
            records.setdefault(key, FileRecord(path=relative))
            raw_conditions.setdefault(key, [])

        for node in _walk(tree.root_node):
            key = scope_key(node)
            record = records.setdefault(key, FileRecord(path=relative))
            raw_conditions.setdefault(key, [])
            if node.type == "assignment_expression":
                left_node = node.child_by_field_name("left")
                right_node = node.child_by_field_name("right")
                left_values = _variables(source, left_node)
                right_values = _direct_alias_variables(source, right_node)
                for left in left_values:
                    # Appending a value to a collection records containment,
                    # not semantic aliasing with the collection itself.
                    if left.endswith("[]"):
                        continue
                    for right in right_values:
                        record.alias_pairs.append((left, right))
            elif node.type in CONTROL_NODES:
                condition = _condition_record(
                    relative,
                    source,
                    node,
                    termination_patterns,
                    termination_exclude_patterns,
                )
                if condition is None:
                    continue
                # A switch selector is dispatch state, not a condition whose
                # entire multi-case body is one denial branch.
                if node.type == "switch_statement":
                    condition.terminations = []
                raw_conditions[key].append(condition)
            elif node.type in FUNCTION_NODES:
                name_node = node.child_by_field_name("name")
                body_node = node.child_by_field_name("body")
                record.functions.append(
                    FunctionRecord(
                        path=relative,
                        name=_text(source, name_node).strip() or "<anonymous>",
                        parameters=_function_parameters(source, node),
                        body=_text(source, body_node).strip(),
                        code=_text(source, node).strip(),
                        start_line=_line(node),
                        end_line=_end_line(node),
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                    )
                )
            elif node.type in {
                "function_call_expression",
                "scoped_call_expression",
                "member_call_expression",
            }:
                name = _call_name(source, node)
                if name:
                    record.function_calls.append(
                        FunctionCallRecord(
                            path=relative,
                            name=name,
                            code=_text(source, node).strip(),
                            start_line=_line(node),
                            end_line=_end_line(node),
                            start_byte=node.start_byte,
                            end_byte=node.end_byte,
                        )
                    )

        # Session identity keys are explicit PHP authentication state sources.
        # Keep their real containing statement as source context even when the
        # value is assigned or consumed outside a conditional expression.
        semantic_sources_seen: set[tuple[str, int, int, str]] = set()
        for node in _walk(tree.root_node):
            if node.type != "subscript_expression":
                continue
            expression = re.sub(r"\s+", "", _text(source, node))
            match = SESSION_IDENTITY_KEY.fullmatch(expression)
            if match is None:
                continue
            statement = _statement(node)
            key = scope_key(node)
            signature = (key, statement.start_byte, statement.end_byte, expression)
            if signature in semantic_sources_seen:
                continue
            semantic_sources_seen.add(signature)
            records[key].conditions.append(
                ConditionRecord(
                    path=relative,
                    condition=expression,
                    parameters=[expression],
                    body=_text(source, statement).strip(),
                    terminations=[],
                    start_line=_line(statement),
                    end_line=_end_line(statement),
                    start_byte=statement.start_byte,
                    end_byte=statement.end_byte,
                    code=_text(source, statement).strip(),
                    is_control=False,
                    semantic_evidence=[
                        {
                            "kind": "php_session_identity_key",
                            "key": match.group(2).casefold(),
                        }
                    ],
                )
            )

        # Keep database relations in the lexical scope where the wrapper or
        # SQL statement occurs; repeated local names in unrelated functions
        # must not share DBMatch evidence.
        for expression, relations in _sql_relations(source, tree.root_node).items():
            for relation in relations:
                relation_line = int(relation.get("line", 0) or 0)
                containing = [
                    function_node
                    for function_node in function_nodes
                    if _line(function_node) <= relation_line <= _end_line(function_node)
                ]
                owner = min(
                    containing,
                    key=lambda item: item.end_byte - item.start_byte,
                    default=None,
                )
                key = scope_key(owner) if owner is not None else "module"
                scoped_relations = records[key].database_relations.setdefault(expression, [])
                if relation not in scoped_relations:
                    scoped_relations.append(relation)

        for key, conditions in raw_conditions.items():
            _propagate_conditional_state(source, conditions, termination_exclude_patterns)
            record = records[key]
            for condition in conditions:
                body_node = condition.node.child_by_field_name("body") or condition.node.child_by_field_name("consequence")
                record.conditions.append(
                    ConditionRecord(
                        path=relative,
                        condition=condition.condition,
                        parameters=_condition_parameters(
                            source,
                            condition.condition_node,
                            semantic_predicates,
                        ),
                        body=_text(source, body_node).strip(),
                        terminations=condition.terminations,
                        start_line=condition.start_line,
                        end_line=condition.end_line,
                        start_byte=condition.node.start_byte,
                        end_byte=condition.node.end_byte,
                        code=_text(source, condition.node).strip(),
                        function_calls=_condition_calls(source, condition.condition_node),
                    )
                )
        parsed_files.extend(records.values())

    _propagate_global_database_relations(parsed_files)

    return finalize_analysis(
        language="php",
        parser_name="tree-sitter-php",
        files=parsed_files,
        access_control_database_fields=access_control_database_fields,
        parse_errors=parse_errors,
        cst_files=cst_files,
    )
