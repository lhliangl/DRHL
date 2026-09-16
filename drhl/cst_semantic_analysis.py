from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Iterable


PHP_SUPERGLOBALS = {
    "$_COOKIE",
    "$_ENV",
    "$_FILES",
    "$_GET",
    "$_POST",
    "$_REQUEST",
    "$_SERVER",
    "$_SESSION",
    "$GLOBALS",
}
PHP_ACCESS_CONTROL_SUPERGLOBALS = {"$_COOKIE", "$_SESSION"}


@dataclass
class ConditionRecord:
    path: str
    condition: str
    parameters: list[str]
    body: str
    terminations: list[dict[str, Any]]
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    code: str = ""
    is_control: bool = True
    semantic_evidence: list[dict[str, Any]] = field(default_factory=list)
    function_calls: list[str] = field(default_factory=list)


@dataclass
class FunctionRecord:
    path: str
    name: str
    parameters: list[str]
    body: str
    code: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int


@dataclass
class FunctionCallRecord:
    path: str
    name: str
    code: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int


@dataclass
class FileRecord:
    path: str
    conditions: list[ConditionRecord] = field(default_factory=list)
    functions: list[FunctionRecord] = field(default_factory=list)
    function_calls: list[FunctionCallRecord] = field(default_factory=list)
    alias_pairs: list[tuple[str, str]] = field(default_factory=list)
    database_relations: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, value: str) -> None:
        if value:
            self.parent.setdefault(value, value)

    def find(self, value: str) -> str:
        self.add(value)
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        if not left or not right:
            return
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root

    def groups(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        for value in self.parent:
            result.setdefault(self.find(value), set()).add(value)
        return result


def serialize_cst(source: bytes, node: Any, depth: int = 0, max_depth: int = 80) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": node.type,
        "start_line": int(node.start_point[0]) + 1,
        "end_line": int(node.end_point[0]) + 1,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "named": bool(getattr(node, "is_named", False)),
    }
    if node.child_count == 0:
        value = source[node.start_byte:node.end_byte].decode("utf-8", errors="replace").strip()
        if value:
            item["text"] = value[:240]
    elif depth < max_depth:
        item["children"] = [serialize_cst(source, child, depth + 1, max_depth) for child in node.children]
    else:
        item["children_truncated"] = node.child_count
    return item


def walk(node: Any) -> Iterable[Any]:
    yield node
    for child in node.children:
        yield from walk(child)


def walk_direct_control_region(node: Any, nested_control_types: set[str]) -> Iterable[Any]:
    """Walk a branch without attributing nested conditions to its parent condition."""
    yield node
    for child in node.children:
        if child.type in nested_control_types:
            continue
        yield from walk_direct_control_region(child, nested_control_types)


def text(source: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def line(node: Any) -> int:
    return int(node.start_point[0]) + 1


def end_line(node: Any) -> int:
    return int(node.end_point[0]) + 1


def field_patterns(fields: list[str] | None) -> dict[str, Any]:
    exact: set[tuple[str, str]] = set()
    wildcard: set[str] = set()
    unqualified: set[str] = set()
    for raw in fields or []:
        value = str(raw).strip().strip('`"').casefold()
        if not value:
            continue
        if "." not in value:
            unqualified.add(value)
            continue
        table, field_name = (part.strip().strip('`"') for part in value.split(".", 1))
        if table == "*":
            wildcard.add(field_name)
        elif table and field_name:
            exact.add((table, field_name))
    return {"exact": exact, "wildcard": wildcard, "unqualified": unqualified}


def relation_matches(patterns: dict[str, Any], relation: dict[str, Any]) -> bool:
    table = str(relation.get("table", "")).strip().strip('`"').casefold()
    field_name = str(relation.get("field", "")).strip().strip('`"').casefold()
    if not field_name:
        return False
    exact_table_match = any(
        configured_field == field_name
        and (
            configured_table == table
            or configured_table.endswith("_" + table)
            or table.endswith("_" + configured_table)
        )
        for configured_table, configured_field in patterns["exact"]
    )
    return bool(
        exact_table_match
        or field_name in patterns["wildcard"]
        or field_name in patterns["unqualified"]
    )


def _php_superglobal(expression: str) -> str | None:
    upper = str(expression).strip().upper()
    for name in PHP_SUPERGLOBALS:
        if upper == name or upper.startswith(name + "["):
            return name
    return None


def _php_validated_expression(candidate: dict[str, Any]) -> str | None:
    """Enforce the PHP policy that only session/cookie superglobals carry AC state."""
    aliases = [str(item) for item in candidate.get("aliases", [])]
    globals_in_group = [
        (alias, name)
        for alias in aliases
        if (name := _php_superglobal(alias)) is not None
    ]
    allowed = [
        alias
        for alias, name in globals_in_group
        if name in PHP_ACCESS_CONTROL_SUPERGLOBALS
    ]
    disallowed = [
        alias
        for alias, name in globals_in_group
        if name not in PHP_ACCESS_CONTROL_SUPERGLOBALS
    ]
    if disallowed and not allowed:
        return None
    if allowed:
        for alias in allowed:
            match = re.fullmatch(
                r"\$_SESSION\s*\[\s*(['\"]?)(user_id|userid|username)\1\s*\]",
                alias,
                re.I,
            )
            if match:
                return f"$_SESSION['{match.group(2).casefold()}']"
        return allowed[0]
    return str(candidate.get("expression", ""))


def _dedupe_relations(relations: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    for relation in relations:
        item = dict(relation)
        key = (
            str(item.get("table", "")).casefold(),
            str(item.get("field", "")).casefold(),
            int(item.get("line", 0) or 0),
        )
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _if_framework(condition: ConditionRecord, language: str) -> str:
    """Keep only a parameter condition and its concrete termination statements."""
    predicate = condition.condition.strip()
    if language != "python" and predicate.startswith("(") and predicate.endswith(")"):
        predicate = predicate[1:-1].strip()
    if language == "python":
        lines = [f"if {predicate}:"]
    elif language == "go":
        lines = [f"if {predicate} {{"]
    else:
        lines = [f"if ({predicate}) {{"]
    for termination in condition.terminations:
        if termination.get("is_statement", True) is False:
            continue
        code = str(termination.get("code", "")).strip()
        if code:
            lines.extend("    " + part for part in code.splitlines())
    if language != "python":
        lines.append("}")
    return "\n".join(lines)


def _unique_strings(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def _simple_function_name(value: Any) -> str:
    name = str(value or "").strip().replace("\\", ".")
    for separator in ("::", "->", "."):
        if separator in name:
            name = name.rsplit(separator, 1)[-1]
    return name.casefold()


def finalize_analysis(
    *,
    language: str,
    parser_name: str,
    files: list[FileRecord],
    access_control_database_fields: list[str] | None,
    parse_errors: list[Any],
    cst_files: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply the language-independent rules from paper Sections 4.3.1-4.3.3."""
    patterns = field_patterns(access_control_database_fields)
    candidate_parameters: list[dict[str, Any]] = []
    candidate_functions: list[dict[str, Any]] = []
    validated_parameters: list[dict[str, Any]] = []
    validated_functions: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []

    global_parameter_index = 0
    global_function_index = 0

    function_contexts: list[tuple[FunctionRecord, list[ConditionRecord]]] = []
    validated_function_keys: set[tuple[str, int, str]] = set()
    function_ids: dict[tuple[str, int, str], str] = {}
    file_contexts: list[dict[str, Any]] = []

    for file_record in files:
        union = UnionFind()
        for condition in file_record.conditions:
            for expression in condition.parameters:
                union.add(expression)
        for left, right in file_record.alias_pairs:
            union.union(left, right)
        for expression in file_record.database_relations:
            union.add(expression)

        groups = union.groups()
        expression_to_group = {
            expression: root for root, members in groups.items() for expression in members
        }
        condition_indexes: dict[str, set[int]] = {}
        condition_expressions: dict[str, list[str]] = {}
        for index, condition in enumerate(file_record.conditions):
            for expression in condition.parameters:
                group = expression_to_group.get(expression, expression)
                condition_indexes.setdefault(group, set()).add(index)
                condition_expressions.setdefault(group, []).append(expression)

        parameter_by_group: dict[str, dict[str, Any]] = {}
        for group, indexes in condition_indexes.items():
            members = groups.get(group, {group})
            direct = list(dict.fromkeys(condition_expressions.get(group, [])))
            if not direct:
                continue
            expression = direct[0]
            aliases = [expression, *sorted(member for member in members if member != expression)]
            relations = _dedupe_relations(
                relation
                for member in members
                for relation in file_record.database_relations.get(member, [])
            )
            locations = [
                {
                    "source": (
                        "conditional"
                        if file_record.conditions[index].is_control
                        else "database"
                    ),
                    "line": file_record.conditions[index].start_line,
                    "condition": file_record.conditions[index].condition,
                }
                for index in sorted(indexes)
            ]
            global_parameter_index += 1
            candidate = {
                "id": f"{file_record.path}:LCP{global_parameter_index}",
                "path": file_record.path,
                "expression": expression,
                "aliases": aliases,
                "database_relations": relations,
                "sources": list(dict.fromkeys(item["source"] for item in locations)),
                "locations": locations,
                "condition_indexes": sorted(indexes),
            }
            candidate_parameters.append(candidate)
            parameter_by_group[group] = candidate

        validated_groups: set[str] = set()
        validated_parameter_by_group: dict[str, dict[str, Any]] = {}
        for group, candidate in parameter_by_group.items():
            validated_expression = str(candidate["expression"])
            if language == "php":
                php_expression = _php_validated_expression(candidate)
                if php_expression is None:
                    continue
                validated_expression = php_expression
            evidence: list[dict[str, Any]] = []
            for relation in candidate["database_relations"]:
                if relation_matches(patterns, relation):
                    evidence.append(
                        {
                            "kind": "database_field",
                            **{
                                key: relation[key]
                                for key in ("table", "field", "line")
                                if key in relation
                            },
                        }
                    )
            for index in candidate["condition_indexes"]:
                condition = file_record.conditions[index]
                if condition.terminations:
                    evidence.append(
                        {
                            "kind": "terminating_condition",
                            "line": condition.start_line,
                            "condition": condition.condition,
                            "terminations": condition.terminations,
                        }
                    )
                evidence.extend(dict(item) for item in condition.semantic_evidence)
            if evidence:
                validated_groups.add(group)
                validated = dict(candidate)
                if validated_expression != candidate["expression"]:
                    validated["canonicalized_from"] = candidate["expression"]
                    validated["expression"] = validated_expression
                validated["validation_evidence"] = evidence
                validated_parameters.append(validated)
                validated_parameter_by_group[group] = validated

        for function in file_record.functions:
            global_function_index += 1
            candidate_function = {
                    "id": f"{file_record.path}:LCF{global_function_index}",
                    "path": file_record.path,
                    "name": function.name,
                    "parameters": function.parameters,
                    "body": function.body,
                    "start_line": function.start_line,
                    "end_line": function.end_line,
                    "code": function.code,
                }
            candidate_functions.append(candidate_function)
            function_key = (function.path, function.start_byte, function.name.casefold())
            function_ids[function_key] = candidate_function["id"]

            matching: list[ConditionRecord] = []
            contained_conditions = [
                condition
                for condition in file_record.conditions
                if function.start_byte <= condition.start_byte
                and condition.end_byte <= function.end_byte
            ]
            function_contexts.append((function, contained_conditions))
            for condition in contained_conditions:
                if not (
                    condition.terminations
                ):
                    continue
                participant_groups = {
                    expression_to_group.get(expression, expression)
                    for expression in condition.parameters
                }
                if participant_groups & validated_groups:
                    matching.append(condition)
            if not matching:
                continue
            validated_function_keys.add(function_key)
            matching_parameter_ids = _unique_strings(
                validated_parameter_by_group[group]["id"]
                for condition in matching
                for expression in condition.parameters
                if (group := expression_to_group.get(expression, expression))
                in validated_parameter_by_group
            )
            validated_functions.append(
                {
                    "id": candidate_function["id"],
                    "path": file_record.path,
                    "name": function.name,
                    "parameters": function.parameters,
                    "body": function.body,
                    "start_line": function.start_line,
                    "end_line": function.end_line,
                    "conditions": [condition.condition for condition in matching],
                    "code": function.code,
                    "parameter_ids": matching_parameter_ids,
                    "validation_evidence": [
                        "validated_parameter_condition",
                        "same_branch_termination",
                    ],
                }
            )
        file_contexts.append(
            {
                "file": file_record,
                "expression_to_group": expression_to_group,
                "validated_parameter_by_group": validated_parameter_by_group,
            }
        )

    # A wrapper may enforce a decision returned by a directly validated
    # function.  Keep the call as function semantics rather than turning the
    # callee name into a candidate parameter.
    changed = True
    while changed:
        changed = False
        validated_names = {
            str(item.get("name", "")).casefold() for item in validated_functions
        }
        for function, contained_conditions in function_contexts:
            key = (function.path, function.start_byte, function.name.casefold())
            if key in validated_function_keys:
                continue
            matching = [
                condition
                for condition in contained_conditions
                if condition.terminations
                and validated_names.intersection(
                    call.casefold() for call in condition.function_calls
                )
            ]
            if not matching:
                continue
            validated_function_keys.add(key)
            called_function_ids = _unique_strings(
                item["id"]
                for item in validated_functions
                if item["name"].casefold()
                in {
                    call.casefold()
                    for condition in matching
                    for call in condition.function_calls
                }
            )
            validated_functions.append(
                {
                    "id": function_ids[key],
                    "path": function.path,
                    "name": function.name,
                    "parameters": function.parameters,
                    "body": function.body,
                    "start_line": function.start_line,
                    "end_line": function.end_line,
                    "conditions": [condition.condition for condition in matching],
                    "code": function.code,
                    "parameter_ids": _unique_strings(
                        parameter_id
                        for item in validated_functions
                        if item["id"] in called_function_ids
                        for parameter_id in item.get("parameter_ids", [])
                    ),
                    "called_function_ids": called_function_ids,
                    "validation_evidence": [
                        "calls_validated_function",
                        "same_branch_termination",
                    ],
                }
            )
            changed = True

    validated_functions_by_path: dict[str, list[dict[str, Any]]] = {}
    validated_functions_by_name: dict[str, list[dict[str, Any]]] = {}
    for function in validated_functions:
        validated_functions_by_path.setdefault(str(function["path"]), []).append(function)
        validated_functions_by_name.setdefault(
            _simple_function_name(function["name"]), []
        ).append(function)
        snippets.append(
            {
                "path": function["path"],
                "kind": "validation_function",
                "start_line": function["start_line"],
                "end_line": function["end_line"],
                "function": function["name"],
                "code": function["code"],
                "parameter_ids": _unique_strings(function.get("parameter_ids", [])),
                "function_ids": [function["id"]],
            }
        )

    for context in file_contexts:
        file_record = context["file"]
        for call in file_record.function_calls:
            matched_functions = validated_functions_by_name.get(
                _simple_function_name(call.name), []
            )
            if not matched_functions:
                continue
            snippets.append(
                {
                    "path": call.path,
                    "kind": "guard_call",
                    "start_line": call.start_line,
                    "end_line": call.end_line,
                    "function": call.name,
                    "code": call.code,
                    "parameter_ids": _unique_strings(
                        parameter_id
                        for function in matched_functions
                        for parameter_id in function.get("parameter_ids", [])
                    ),
                    "function_ids": _unique_strings(
                        function["id"] for function in matched_functions
                    ),
                }
            )

    database_snippets: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for context in file_contexts:
        file_record = context["file"]
        expression_to_group = context["expression_to_group"]
        validated_parameter_by_group = context["validated_parameter_by_group"]

        for condition in file_record.conditions:
            parameter_ids = _unique_strings(
                validated_parameter_by_group[group]["id"]
                for expression in condition.parameters
                if (group := expression_to_group.get(expression, expression))
                in validated_parameter_by_group
            )
            if not parameter_ids:
                continue
            code = (condition.code or condition.body).strip()
            if not code:
                continue
            if not condition.is_control:
                snippets.append(
                    {
                        "path": file_record.path,
                        "kind": "semantic_source",
                        "start_line": condition.start_line,
                        "end_line": condition.end_line,
                        "code": code,
                        "semantic_evidence": condition.semantic_evidence,
                        "parameter_ids": parameter_ids,
                        "function_ids": [],
                    }
                )
                continue
            function_ids_for_condition = _unique_strings(
                function["id"]
                for function in validated_functions_by_path.get(file_record.path, [])
                if int(function["start_line"]) <= condition.start_line
                and condition.end_line <= int(function["end_line"])
            )
            snippet = {
                "path": file_record.path,
                "kind": "conditional",
                "start_line": condition.start_line,
                "end_line": condition.end_line,
                "condition": condition.condition,
                "terminations": condition.terminations,
                "code": code,
                "parameter_ids": parameter_ids,
                "function_ids": function_ids_for_condition,
            }
            if condition.semantic_evidence:
                snippet["semantic_evidence"] = condition.semantic_evidence
            if condition.terminations:
                if_framework = _if_framework(condition, language)
                if any(
                    str(item.get("code", "")).strip()
                    for item in condition.terminations
                    if item.get("is_statement", True) is not False
                ):
                    snippet["if_framework"] = if_framework
            snippets.append(snippet)

        for group, parameter in validated_parameter_by_group.items():
            matched_relations = [
                relation
                for relation in parameter.get("database_relations", [])
                if relation_matches(patterns, relation)
            ]
            if not matched_relations:
                continue
            related_conditions = [
                {
                    "start_line": file_record.conditions[index].start_line,
                    "end_line": file_record.conditions[index].end_line,
                    "condition": file_record.conditions[index].condition,
                }
                for index in parameter.get("condition_indexes", [])
                if file_record.conditions[index].is_control
            ]
            for relation in matched_relations:
                operation_code = str(relation.get("code", "")).strip()
                if not operation_code:
                    continue
                start = int(relation.get("start_line", relation.get("line", 0)) or 0)
                end = int(relation.get("end_line", start) or start)
                key = (file_record.path, start, end, operation_code)
                snippet = database_snippets.setdefault(
                    key,
                    {
                        "path": file_record.path,
                        "kind": "database_operation",
                        "start_line": start,
                        "end_line": end,
                        "code": operation_code,
                        "database_relations": [],
                        "related_conditions": [],
                        "parameter_ids": [],
                        "function_ids": _unique_strings(
                            function["id"]
                            for function in validated_functions_by_path.get(
                                file_record.path, []
                            )
                            if int(function["start_line"]) <= start
                            and end <= int(function["end_line"])
                        ),
                    },
                )
                relation_summary = {
                    key: relation[key]
                    for key in ("table", "field", "line")
                    if key in relation
                }
                if relation_summary not in snippet["database_relations"]:
                    snippet["database_relations"].append(relation_summary)
                if parameter["id"] not in snippet["parameter_ids"]:
                    snippet["parameter_ids"].append(parameter["id"])
                for item in related_conditions:
                    if item not in snippet["related_conditions"]:
                        snippet["related_conditions"].append(item)

    snippets.extend(database_snippets.values())

    # Database operation source belongs to snippets.json. Keep the validated
    # element documents focused on semantic field relations and stable IDs.
    for parameter in [*candidate_parameters, *validated_parameters]:
        parameter["database_relations"] = [
            {
                key: relation[key]
                for key in ("table", "field", "line")
                if key in relation
            }
            for relation in parameter.get("database_relations", [])
        ]

    snippets.sort(key=lambda item: (item["path"], item["start_line"], item["kind"]))
    return {
        "schema_version": 5,
        "language": language,
        "parser": parser_name,
        "parse_errors": parse_errors,
        "summary": {
            "cst_files": len({file_record.path for file_record in files}),
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
