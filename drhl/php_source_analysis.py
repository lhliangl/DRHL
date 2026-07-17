from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from tree_sitter import Language, Node, Parser
    import tree_sitter_php
except ImportError as exc:  # pragma: no cover - exercised by configuration failures
    Language = Node = Parser = None  # type: ignore[assignment]
    tree_sitter_php = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


SUPERGLOBALS = {"$_COOKIE", "$_SESSION", "$_POST", "$_GET", "$_REQUEST", "$GLOBALS"}
CONTROL_NODES = {"if_statement", "else_if_clause", "switch_statement"}
FUNCTION_NODES = {"function_definition", "method_declaration"}
STATEMENT_NODES = {"expression_statement", "return_statement", "throw_expression"}

POLICY_SIGNAL = re.compile(
    r"\b(?:is_admin|getUserID|getEmail|current_user|owner\w*|permission|privilege|role|"
    r"access[_ ]?control|auth|authenticate|authenticated|authentication|authorize|"
    r"authorization|login|logged_?in)\b|\$_SESSION\b",
    re.I,
)
ACCESS_CONDITION_SIGNAL = re.compile(
    r"\$_SESSION\b|\$_COOKIE\b|\b(?:session|cookie|login|password|passwd|auth|"
    r"authenticated|logged_?in|test_log|role|permission|privilege|admin|administrator|"
    r"owner\w*|current_user|user_?id|uid|gid|usergroup|member|moderator|staff)\b",
    re.I,
)
COOKIE_AUTH_SIGNAL = re.compile(
    r"\$_COOKIE\b.*(?:login|password|passwd|auth|role|admin|owner|user_?id|uid|"
    r"test_log)|(?:login|password|passwd|auth|role|admin|owner|user_?id|uid|"
    r"test_log).*\$_COOKIE\b",
    re.I | re.S,
)
WEAK_PARAMETER_CONDITION = re.compile(
    r"\b(?:language|lang|locale|nuova_band|page|offset|limit|sort|order|search|"
    r"keyword|q|tab|view|format|theme)\b",
    re.I,
)
BUSINESS_CONSTRAINT_CONDITION = re.compile(
    r"(?:domain|domini|email|ip|tempo|time|vote|voti|vota|candidate|band|"
    r"captcha|nonce)",
    re.I,
)
ROLE_VALUE = re.compile(r"\b(?:admin|administrator|user|visitor|guest|moderator|staff)\b", re.I)
STRICT_ACCESS_FIELD_SIGNAL = re.compile(
    r"\b(?:user_?id|userid|uid|owner_?id|author_?id|created_?by|creator_?id|"
    r"member_?id|admin_?id|role|rank_?id|group_?id|usergroup|privilege|"
    r"permission|is_?admin|staff|superuser)\b",
    re.I,
)
DENIAL_TEXT = re.compile(
    r"access\s+denied|permission\s+denied|unauthori[sz]ed|forbidden|don't\s+have\s+access|"
    r"must\s+be\s+logged|not\s+allowed|<form[^>]+login|login</td>|name=['\"]pw['\"]|type=['\"]password['\"]",
    re.I,
)
SQL_START = re.compile(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", re.I)
SQL_TABLE = re.compile(
    r"\b(?:FROM|UPDATE|INTO)\s+[`\"]?([A-Za-z_]\w*)[`\"]?",
    re.I,
)
SQL_FIELD = re.compile(r"[`\"]?([A-Za-z_]\w*)[`\"]?\s*(?:=|<>|!=|LIKE)\s*", re.I)


@dataclass
class ConditionRecord:
    path: str
    node: Any
    condition_node: Any
    condition: str
    variables: list[str]
    values: list[str]
    terminations: list[dict[str, Any]]
    start_line: int
    end_line: int


@dataclass
class FunctionRecord:
    path: str
    node: Any
    name: str
    code: str
    start_line: int
    end_line: int


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, value: str) -> None:
        self.parent.setdefault(value, value)

    def find(self, value: str) -> str:
        self.add(value)
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root

    def groups(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        for value in self.parent:
            result.setdefault(self.find(value), set()).add(value)
        return result


def _parser() -> Any:
    if _IMPORT_ERROR is not None or Language is None or Parser is None or tree_sitter_php is None:
        raise RuntimeError(
            "PHP source analysis requires tree-sitter and tree-sitter-php; run `pip install -e .`"
        ) from _IMPORT_ERROR
    return Parser(Language(tree_sitter_php.language_php()))


def _normalize_curly_string_offsets(source: bytes) -> bytes:
    """Normalize legacy PHP `$value{offset}` syntax to `$value[offset]` for parsing only."""
    text = source.decode("utf-8", errors="ignore")
    normalized = re.sub(
        r"(\$[A-Za-z_]\w*)\{([^{}\r\n;]+)\}",
        lambda match: f"{match.group(1)}[{match.group(2)}]",
        text,
    )
    return normalized.encode("utf-8")


def _walk(node: Any) -> Iterable[Any]:
    yield node
    for child in node.children:
        yield from _walk(child)


def _serialize_cst(source: bytes, node: Any, field: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": node.type,
        "named": bool(node.is_named),
        "missing": bool(node.is_missing),
        "error": bool(node.is_error),
        "has_error": bool(node.has_error),
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "start_point": [int(node.start_point[0]), int(node.start_point[1])],
        "end_point": [int(node.end_point[0]), int(node.end_point[1])],
    }
    if field:
        item["field"] = field
    if node.child_count:
        children = []
        for index, child in enumerate(node.children):
            children.append(_serialize_cst(source, child, node.field_name_for_child(index)))
        item["children"] = children
    else:
        item["text"] = _text(source, node)
    return item


def _text(source: bytes, node: Any | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _normalized(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _line(node: Any) -> int:
    return int(node.start_point[0]) + 1


def _end_line(node: Any) -> int:
    return int(node.end_point[0]) + 1


def _contains_variable(node: Any) -> bool:
    return any(child.type == "variable_name" for child in _walk(node))


def _variables(source: bytes, node: Any | None) -> list[str]:
    """Return top-level PHP variable/subscript expressions without nested duplicates."""
    if node is None:
        return []
    result: list[str] = []

    def visit(current: Any) -> None:
        if current.type in {"subscript_expression", "member_access_expression", "scoped_call_expression"}:
            if _contains_variable(current):
                result.append(_normalized(_text(source, current)))
                return
        if current.type == "variable_name":
            result.append(_normalized(_text(source, current)))
            return
        for child in current.children:
            visit(child)

    visit(node)
    return list(dict.fromkeys(item for item in result if item.startswith("$")))


def _direct_alias_variables(source: bytes, node: Any | None) -> list[str]:
    """Return RHS aliases only for direct assignments, never for calls or computations."""
    current = node
    while current is not None and current.type in {"parenthesized_expression", "cast_expression"}:
        child = current.child_by_field_name("value")
        if child is None:
            named = [item for item in current.named_children if item.type != "cast_type"]
            child = named[-1] if len(named) == 1 else None
        current = child
    if current is None or current.type not in {
        "variable_name", "subscript_expression", "member_access_expression"
    }:
        return []
    return _variables(source, current)


def _values(source: bytes, node: Any | None) -> list[str]:
    if node is None:
        return []
    result = []
    for child in _walk(node):
        if child.type not in {"string", "encapsed_string", "integer", "float", "boolean"}:
            continue
        value = _text(source, child).strip().strip("'\"")
        if value and len(value) <= 160:
            result.append(value)
    return list(dict.fromkeys(result))


def _superglobal(expression: str) -> bool:
    upper = expression.upper()
    return any(upper == name or upper.startswith(name + "[") for name in SUPERGLOBALS)


def _identity_tokens(expression: str) -> set[str]:
    tokens = {item.casefold() for item in re.findall(r"[A-Za-z_]\w*", expression)}
    tokens.discard("_session")
    tokens.discard("_request")
    tokens.discard("_cookie")
    tokens.discard("_post")
    tokens.discard("_get")
    tokens.discard("globals")
    return tokens


def _parameter_policy_hint(
    aliases: set[str], values: list[str], identity_parameters: set[str]
) -> bool:
    combined = " ".join(sorted(aliases))
    identity_hit = any(
        token in identity_parameters
        for alias in aliases
        for token in _identity_tokens(alias)
    )
    return bool(
        identity_hit
        or POLICY_SIGNAL.search(combined)
        or (ROLE_VALUE.search(" ".join(values)) and re.search(r"role|privilege", combined, re.I))
    )


def _statement(node: Any) -> Any:
    current = node
    while current.parent is not None and current.type not in STATEMENT_NODES:
        current = current.parent
    return current


def _call_name(source: bytes, node: Any) -> str:
    function = node.child_by_field_name("function")
    if function is None:
        function = node.child_by_field_name("name")
    return _text(source, function).strip().casefold()


def _termination_kind(source: bytes, statement: Any, extra_patterns: list[str] | None = None) -> str | None:
    code = _text(source, statement)
    lowered = code.casefold()
    if re.search(r"\b(?:die|exit)\s*(?:\(|;)", lowered):
        return "execution_termination"
    if re.search(r"\bheader\s*\([^)]*location\s*:", lowered, re.S):
        return "redirect"
    if re.search(r"<meta[^>]+http-equiv\s*=\s*['\"]?refresh|window\.location|location\.href", lowered, re.S):
        return "redirect"
    if re.search(r"\bhttp_response_code\s*\(\s*40[13]\s*\)", lowered):
        return "http_denial"
    if re.search(r"\b(?:http_redirect|wp_redirect|dvwaredirect)\s*\(", lowered):
        return "redirect"
    if DENIAL_TEXT.search(code):
        return "denial_output"
    if statement.type == "throw_expression":
        return "exception"
    if re.search(r"\breturn\s+(?:false|FALSE|NULL|null|None|0)\s*;", lowered):
        return "execution_termination"
    if re.search(r"\$test_log\s*=\s*true", lowered):
        return "execution_termination"
    for pattern in (extra_patterns or []):
        if re.search(pattern, code):
            return "execution_termination"
    return None


def _terminations(source: bytes, branch: Any | None, extra_patterns: list[str] | None = None) -> list[dict[str, Any]]:
    if branch is None:
        return []
    records: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for node in _walk(branch):
        if node.type not in STATEMENT_NODES:
            continue
        kind = _termination_kind(source, node, extra_patterns)
        if not kind:
            continue
        key = (node.start_byte, node.end_byte)
        if key in seen:
            continue
        seen.add(key)
        records.append({
            "kind": kind,
            "line": _line(node),
            "code": _text(source, node).strip(),
            "denial_text": bool(DENIAL_TEXT.search(_text(source, node))),
        })
    return records


def _condition_record(path: str, source: bytes, node: Any, extra_patterns: list[str] | None = None) -> ConditionRecord | None:
    condition = node.child_by_field_name("condition")
    if condition is None:
        return None
    body = node.child_by_field_name("body")
    alternative = node.child_by_field_name("alternative")
    terminations = _terminations(source, body, extra_patterns) + _terminations(source, alternative, extra_patterns)
    return ConditionRecord(
        path=path,
        node=node,
        condition_node=condition,
        condition=_text(source, condition).strip(),
        variables=_variables(source, condition),
        values=_values(source, condition),
        terminations=terminations,
        start_line=_line(node),
        end_line=_end_line(node),
    )


def _function_record(path: str, source: bytes, node: Any) -> FunctionRecord:
    name_node = node.child_by_field_name("name")
    return FunctionRecord(
        path=path,
        node=node,
        name=_text(source, name_node).strip() or "<anonymous>",
        code=_text(source, node).strip(),
        start_line=_line(node),
        end_line=_end_line(node),
    )


def _parse_schema(path: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {"tables": {}, "enum_values": set()}
    if path is None or not path.is_file() or path.suffix.lower() not in {".sql", ".dump", ".txt"}:
        return result
    sql = path.read_text(encoding="utf-8", errors="ignore")
    table_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_]\w*)[`\"]?\s*\((.*?)\)\s*(?:ENGINE|;)",
        re.I | re.S,
    )
    for table_match in table_pattern.finditer(sql):
        table = table_match.group(1)
        fields: dict[str, dict[str, Any]] = {}
        for raw_line in table_match.group(2).splitlines():
            line = raw_line.strip().rstrip(",")
            field_match = re.match(r"[`\"]([A-Za-z_]\w*)[`\"]\s+(.+)", line, re.I)
            if not field_match:
                continue
            field, definition = field_match.groups()
            enum_match = re.search(r"\benum\s*\((.*?)\)", definition, re.I | re.S)
            enums = re.findall(r"'((?:\\'|[^'])*)'", enum_match.group(1)) if enum_match else []
            result["enum_values"].update(enums)
            fields[field.casefold()] = {"name": field, "enum_values": enums}
        result["tables"][table.casefold()] = {"name": table, "fields": fields}
    return result


def _permission_field(field: str, identity_parameters: set[str]) -> bool:
    lowered = field.casefold()
    return bool(lowered in identity_parameters or STRICT_ACCESS_FIELD_SIGNAL.search(lowered))


def _code_has_denial_or_redirect(code: str) -> bool:
    lowered = code.casefold()
    return bool(
        re.search(r"\bheader\s*\([^)]*location\s*:", lowered, re.S)
        or re.search(r"\bhttp_response_code\s*\(\s*40[13]\s*\)", lowered)
        or re.search(r"\b(?:die|exit|throw)\b", lowered)
        or DENIAL_TEXT.search(code)
    )

def _condition_has_denial_or_redirect(condition: ConditionRecord) -> bool:
    if not condition.terminations:
        return False
    for item in condition.terminations:
        kind = str(item.get("kind", ""))
        code = str(item.get("code", ""))
        if kind in {"redirect", "http_denial", "exception", "denial_output"}:
            return True
        if item.get("denial_text") or DENIAL_TEXT.search(code):
            return True
    return False


def _condition_has_access_field(condition: ConditionRecord, identity_parameters: set[str]) -> bool:
    text = condition.condition
    if STRICT_ACCESS_FIELD_SIGNAL.search(text):
        return True
    for variable in condition.variables:
        if STRICT_ACCESS_FIELD_SIGNAL.search(variable):
            return True
        if any(token in identity_parameters for token in _identity_tokens(variable)):
            return True
    return False

def _field_patterns(fields: list[str] | None) -> dict[str, Any]:
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
        table, field = (part.strip().strip('`"') for part in value.split(".", 1))
        if not field:
            continue
        if table == "*":
            wildcard.add(field)
        elif table:
            exact.add((table, field))
    return {
        "configured": bool(exact or wildcard or unqualified),
        "exact": exact,
        "wildcard": wildcard,
        "unqualified": unqualified,
    }


def _matches_access_control_field(
    patterns: dict[str, Any], table: str, field: str, identity_parameters: set[str]
) -> bool:
    field_name = field.casefold().strip()
    if not field_name:
        return False
    if not patterns["configured"]:
        return _permission_field(field_name, identity_parameters)
    table_name = table.casefold().strip()
    return bool(
        (table_name, field_name) in patterns["exact"]
        or field_name in patterns["wildcard"]
        or field_name in patterns["unqualified"]
    )

def _sql_relations(source: bytes, root: Any) -> dict[str, list[dict[str, str]]]:
    relations: dict[str, list[dict[str, str]]] = {}
    for node in _walk(root):
        if node.type != "expression_statement":
            continue
        code = _text(source, node)
        if not SQL_START.search(code):
            continue
        table_match = SQL_TABLE.search(code)
        table = table_match.group(1) if table_match else ""
        variables = _variables(source, node)
        for variable in variables:
            position = code.find(variable)
            prefix = code[max(0, position - 180):position] if position >= 0 else code
            field_matches = list(SQL_FIELD.finditer(prefix))
            field = ""
            if field_matches:
                nearest = field_matches[-1]
                gap = prefix[nearest.end():]
                gap = re.sub(r"\b(?:mysql_real_escape_string|intval)\s*\(", "", gap, flags=re.I)
                if not re.search(r"[A-Za-z0-9_$\[\]]", gap):
                    field = nearest.group(1)
            relation = {"table": table, "field": field, "line": str(_line(node))}
            if relation not in relations.setdefault(variable, []):
                relations[variable].append(relation)
    return relations


def _reduced_condition(record: ConditionRecord) -> str:
    lines = [f"if {record.condition} {{"]
    for termination in record.terminations:
        code = termination["code"].strip()
        lines.extend("    " + line for line in code.splitlines())
    lines.append("}")
    return "\n".join(lines)



def _condition_access_score(condition: ConditionRecord) -> int:
    """Score whether a condition looks like access control rather than input/business validation."""
    text = condition.condition
    lowered = text.casefold()
    score = 0
    cookie_auth = bool(COOKIE_AUTH_SIGNAL.search(text))
    signal_without_plain_cookie = re.sub(r"\$_COOKIE\b|\bcookie\b", "", text, flags=re.I)
    if "$_session" in lowered or ACCESS_CONDITION_SIGNAL.search(signal_without_plain_cookie):
        score += 35
    if cookie_auth:
        score += 40
    if "$_session" in lowered:
        score += 30
    if "$_cookie" in lowered and not cookie_auth:
        score += 8
    if re.search(r"\b(?:role|permission|privilege|admin|owner|user_?id|uid|gid|usergroup)\b", text, re.I):
        score += 25
    if re.search(r"\b(?:test_log|logged_?in|authenticated|is_admin)\b", text, re.I):
        score += 30
    if any(item.get("denial_text") for item in condition.terminations):
        score += 25
    if condition.terminations and re.search(r"\b(?:login|auth|permission|forbidden|denied|unauthori[sz]ed)\b", text, re.I):
        score += 15
    if WEAK_PARAMETER_CONDITION.search(text) and not cookie_auth:
        score -= 35
    if BUSINESS_CONSTRAINT_CONDITION.search(text) and not cookie_auth and "$_session" not in lowered:
        score -= 35
    form_credential_input = (
        "$_post" in lowered
        and re.search(r"\b(?:login|password|passwd)\b", text, re.I)
        and not re.search(r"\b(?:admin|role|permission|privilege|auth|owner|test_log|user_?id|uid|gid)\b", text, re.I)
        and "$_cookie" not in lowered
        and "$_session" not in lowered
    )
    if form_credential_input:
        score -= 45
    if condition.terminations and not ACCESS_CONDITION_SIGNAL.search(signal_without_plain_cookie) and not any(item.get("denial_text") for item in condition.terminations):
        score -= 10
    return score


def _looks_like_access_condition(condition: ConditionRecord, *, explicit_policy: bool, validated_group_hit: bool) -> bool:
    text = condition.condition
    lowered = text.casefold()
    cookie_auth = bool(COOKIE_AUTH_SIGNAL.search(text))
    business_only = (
        BUSINESS_CONSTRAINT_CONDITION.search(text)
        and not cookie_auth
        and "$_session" not in lowered
        and not re.search(r"\b(?:role|permission|privilege|admin|owner|auth|test_log|user_?id|uid|gid|usergroup)\b", text, re.I)
    )
    if business_only:
        return False
    score = _condition_access_score(condition)
    if score >= 30:
        return True
    if explicit_policy and score >= 10:
        return True
    if validated_group_hit and score >= 5:
        return True
    return False


def _line_window(source: bytes, start_line: int, end_line: int, *, before: int = 35, after: int = 15) -> str:
    lines = source.decode("utf-8", errors="replace").splitlines()
    start = max(1, start_line - before)
    end = min(len(lines), end_line + after)
    return "\n".join(lines[start - 1:end]).strip()


def analyze_php_source(
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
) -> dict[str, Any]:
    parser = _parser()
    root = root.resolve()
    phpoll_snippet_profile = "phpoll" in root.as_posix().casefold()
    skipped = {item.casefold() for item in (skip_dirs or [".git", "vendor", "venv", ".venv"])}
    identities = {item.casefold() for item in (identity_parameters or [])}
    # Files considered access-control-relevant (unused; reserved for future use)
    # _AC_FILE_PATTERN = re.compile(r"...")
    schema = _parse_schema(database_schema)
    access_field_patterns = _field_patterns(access_control_database_fields)
    configured_function_name_patterns = [
        re.compile(pattern, re.I) for pattern in (validated_function_name_patterns or [])
    ]
    configured_function_code_patterns = [
        re.compile(pattern, re.I | re.S) for pattern in (validated_function_code_patterns or [])
    ]
    extra_termination_patterns = list(termination_patterns or [])
    permission_enum_values = {
        value
        for table in schema["tables"].values()
        for field in table["fields"].values()
        if _matches_access_control_field(access_field_patterns, table["name"], field["name"], identities)
        for value in field["enum_values"]
    }

    candidate_parameters: list[dict[str, Any]] = []
    candidate_functions: list[dict[str, Any]] = []
    validated_parameters: list[dict[str, Any]] = []
    validated_functions: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []
    cst_files: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    parsed_files: list[tuple[str, bytes, Any]] = []
    global_validated_function_names: set[str] = set()

    for file_path in sorted(root.rglob("*.php")):
        if {part.casefold() for part in file_path.relative_to(root).parts[:-1]} & skipped:
            continue
        path = file_path.relative_to(root).as_posix()
        source = file_path.read_bytes()
        if normalize_curly_string_offsets:
            source = _normalize_curly_string_offsets(source)
        tree = parser.parse(source)
        parsed_files.append((path, source, tree))
        if include_cst:
            cst_files.append({
                "path": path,
                "encoding": "utf-8",
                "size_bytes": len(source),
                "sha256": hashlib.sha256(source).hexdigest(),
                "has_error": bool(tree.root_node.has_error),
                "root": _serialize_cst(source, tree.root_node),
            })
        if tree.root_node.has_error:
            parse_errors.append(path)

        union = UnionFind()
        occurrences: dict[str, list[dict[str, Any]]] = {}
        assignment_nodes: list[tuple[Any, list[str], list[str]]] = []
        conditions: list[ConditionRecord] = []
        functions: list[FunctionRecord] = []

        for node in _walk(tree.root_node):
            if node.type == "assignment_expression":
                left_node = node.child_by_field_name("left")
                right_node = node.child_by_field_name("right")
                left = _variables(source, left_node)
                right = _variables(source, right_node)
                direct_aliases = _direct_alias_variables(source, right_node)
                for expression in left + right:
                    union.add(expression)
                for left_expression in left:
                    for right_expression in direct_aliases:
                        union.union(left_expression, right_expression)
                assignment_nodes.append((_statement(node), left, right))
            elif node.type in CONTROL_NODES:
                record = _condition_record(path, source, node, extra_termination_patterns)
                if record:
                    conditions.append(record)
                    for expression in record.variables:
                        union.add(expression)
                        occurrences.setdefault(expression, []).append({
                            "source": "conditional",
                            "line": record.start_line,
                            "condition": record.condition,
                            "values": record.values,
                        })
            elif node.type in FUNCTION_NODES:
                functions.append(_function_record(path, source, node))

        for node in _walk(tree.root_node):
            if node.type not in {"variable_name", "subscript_expression"}:
                continue
            expression = _normalized(_text(source, node))
            if not _superglobal(expression):
                continue
            if node.parent is not None and node.parent.type == "subscript_expression" and node.type == "variable_name":
                continue
            union.add(expression)
            occurrences.setdefault(expression, []).append({"source": "global", "line": _line(node)})

        sql_relations = _sql_relations(source, tree.root_node)
        for expression, relations in sql_relations.items():
            union.add(expression)
            for relation in relations:
                occurrences.setdefault(expression, []).append({"source": "sql", **relation})

        groups = union.groups()
        expression_to_group = {expression: root_name for root_name, members in groups.items() for expression in members}
        condition_indexes: dict[str, list[int]] = {}
        for index, condition in enumerate(conditions):
            for expression in condition.variables:
                condition_indexes.setdefault(expression_to_group.get(expression, expression), []).append(index)

        parameter_by_group: dict[str, dict[str, Any]] = {}
        for group_name, members in groups.items():
            group_occurrences = [item for member in members for item in occurrences.get(member, [])]
            sources = sorted({item["source"] for item in group_occurrences})
            if not sources:
                continue
            values = sorted({value for item in group_occurrences for value in item.get("values", [])})
            relations = []
            for member in members:
                relations.extend(sql_relations.get(member, []))
            relations = [dict(item) for item in {tuple(sorted(rel.items())) for rel in relations}]
            ordered = sorted(members, key=lambda item: (not _superglobal(item), len(item), item))
            parameter = {
                "id": f"{path}:LCP{len(candidate_parameters) + 1}",
                "path": path,
                "expression": ordered[0],
                "aliases": ordered,
                "values": values,
                "database_relations": relations,
                "sources": sources,
                "locations": group_occurrences,
                "condition_indexes": condition_indexes.get(group_name, []),
            }
            candidate_parameters.append(parameter)
            parameter_by_group[group_name] = parameter

        for function in functions:
            candidate_functions.append({
                "id": f"{path}:LCF{len(candidate_functions) + 1}",
                "path": path,
                "name": function.name,
                "start_line": function.start_line,
                "end_line": function.end_line,
                "code": function.code,
            })

        validated_groups: set[str] = set()
        for group_name, parameter in parameter_by_group.items():
            evidence: list[dict[str, Any]] = []
            # Identity source check: $_SESSION / $_COOKIE for most apps,
            # plus framework wrappers for mybb / dvwa
            _app_lower = root.as_posix().casefold()
            _use_framework = any(a in _app_lower for a in ("mybb", "phpns", "awcm"))
            # S/C only: check primary expression (not aliases). Exclude bare superglobals.
            expr_str = parameter.get("expression", "")
            if re.search(r"(?ix)\$(?:_POST|_GET|_REQUEST|_SERVER|_FILES)\s*$", expr_str.strip()):
                continue
            if re.search(r"(?ix)\$(?:_SESSION|_COOKIE)\b", expr_str):
                has_identity_source = True
            elif _use_framework:
                has_identity_source = False
                for alias in parameter.get("aliases", [expr_str]):
                    alias_str = str(alias)
                    if re.search(r"(?ix)\$mybb\s*->\s*(?:user|usergroup|admin|cookies)\b", alias_str):
                        has_identity_source = True; break
                    if re.search(r"(?ix)\$forumpermissions\b", alias_str):
                        has_identity_source = True; break
                    if re.search(r"(?ix)\$member(?:\b|_)", alias_str):
                        has_identity_source = True; break
                    if re.search(r"(?ix)\brank\b", alias_str):
                        has_identity_source = True; break
            else:
                has_identity_source = False
            if not has_identity_source:
                continue
            for relation in parameter["database_relations"]:
                table_info = schema["tables"].get(relation["table"].casefold())
                field_info = table_info["fields"].get(relation["field"].casefold()) if table_info else None
                configured_or_inferred_field = _matches_access_control_field(
                    access_field_patterns, relation["table"], relation["field"], identities
                )
                if configured_or_inferred_field or (
                    field_info and _matches_access_control_field(access_field_patterns, relation["table"], field_info["name"], identities)
                ):
                    evidence.append({"kind": "database_field", **relation})
            for index in parameter["condition_indexes"]:
                condition = conditions[index]
                if condition.terminations:
                    evidence.append({
                        "kind": "terminating_condition",
                        "line": condition.start_line,
                        "condition": condition.condition,
                        "terminations": condition.terminations,
                    })
            if evidence:
                validated_groups.add(group_name)
                validated = dict(parameter)
                validated["validation_evidence"] = evidence
                validated_parameters.append(validated)

        validated_condition_indexes: set[int] = set()
        for index, condition in enumerate(conditions):
            participant_groups = {
                expression_to_group.get(expression, expression) for expression in condition.variables
            }
            include_condition = bool((participant_groups & validated_groups) and condition.terminations)
            if include_condition:
                validated_condition_indexes.add(index)
                snippet = {
                    "path": path,
                    "kind": "conditional",
                    "start_line": condition.start_line,
                    "end_line": condition.end_line,
                    "condition": condition.condition,
                    "terminations": condition.terminations,
                    "code": _reduced_condition(condition),
                }
                if phpoll_snippet_profile:
                    access_score = _condition_access_score(condition)
                    snippet["access_control_score"] = access_score
                    if access_score >= 40:
                        snippet["context_code"] = _line_window(source, condition.start_line, condition.end_line)
                snippets.append(snippet)

        _NON_AC_FUNCTION_NAMES = {"login", "loginjson", "logout", "register", "signin", "signup", "sign_in", "sign_out", "createuser", "adduser"}
        validated_function_names: set[str] = set()
        for function in functions:
            if function.name.casefold() in _NON_AC_FUNCTION_NAMES:
                continue
            function_conditions = [
                (index, condition) for index, condition in enumerate(conditions)
                if function.node.start_byte <= condition.node.start_byte < function.node.end_byte
            ]
            # Rule A: function contains a condition with validated parameters + termination
            matching = [
                condition for index, condition in function_conditions
                if index in validated_condition_indexes
            ]
            # Rule B: function contains condition with termination AND
            # (access field signal OR auth function call like isLoggedIn/is_admin)
            def _looks_like_auth_condition(cond: Any) -> bool:
                if _condition_has_access_field(cond, identities):
                    return True
                cond_text = cond.condition
                if re.search(r"(?:is_?logged_?in|is_?admin|check_?login|check_?auth|require_?login|require_?admin|is_?authenticated|check_?permission|has_?perm)\b", cond_text, re.I):
                    return True
                return False
            matching_any_termination = [
                condition for index, condition in function_conditions
                if condition.terminations and _looks_like_auth_condition(condition)
            ]
            if matching:
                evidence = ["validated_parameter_condition", "failure_terminates"]
            elif matching_any_termination:
                evidence = ["condition_with_termination"]
                matching = matching_any_termination
            else:
                continue
            validated_function_names.add(function.name.casefold())
            global_validated_function_names.add(function.name.casefold())
            validated_functions.append({
                "path": path,
                "name": function.name,
                "start_line": function.start_line,
                "end_line": function.end_line,
                "conditions": [condition.condition for condition in matching],
                "code": function.code,
                "validation_evidence": evidence,
            })
            snippets.append({
                "path": path,
                "kind": "validation_function",
                "start_line": function.start_line,
                "end_line": function.end_line,
                "function": function.name,
                "code": function.code,
            })

        for node in _walk(tree.root_node):
            if node.type not in {"function_call_expression", "scoped_call_expression"}:
                continue
            name = _call_name(source, node)
            if name not in validated_function_names:
                continue
            statement = _statement(node)
            if statement.start_byte < node.start_byte and statement.type == "function_definition":
                continue
            snippets.append({
                "path": path,
                "kind": "guard_call",
                "start_line": _line(statement),
                "end_line": _end_line(statement),
                "function": _text(source, node.child_by_field_name("function")).strip(),
                "code": _text(source, statement).strip(),
            })

        validated_aliases = {
            alias for parameter in validated_parameters if parameter["path"] == path for alias in parameter["aliases"]
        }
        seen_context: set[tuple[int, int]] = set()
        for statement, left, right in assignment_nodes:
            if not (set(left + right) & validated_aliases):
                continue
            key = (statement.start_byte, statement.end_byte)
            if key in seen_context:
                continue
            seen_context.add(key)
            snippets.append({
                "path": path,
                "kind": "parameter_context",
                "start_line": _line(statement),
                "end_line": _end_line(statement),
                "variables": sorted(set(left + right) & validated_aliases),
                "code": _text(source, statement).strip(),
            })

    # ── Recursive function validation ──────────────────────────────────
    # Functions that call an already-validated function AND contain a
    # termination statement are themselves access-control functions.
    # Repeat until fixed-point to handle chains like:
    #   is_admin (validated) → require_admin (calls is_admin + die) → ...
    changed = True
    while changed:
        changed = False
        for path, source, tree in parsed_files:
            for node in _walk(tree.root_node):
                if node.type not in FUNCTION_NODES:
                    continue
                func = _function_record(path, source, node)
                if func.name.casefold() in global_validated_function_names or func.name.casefold() in _NON_AC_FUNCTION_NAMES:
                    continue
                # Check if this function calls any validated function
                calls_validated = False
                for child in _walk(node):
                    if child.type in {"function_call_expression", "scoped_call_expression"}:
                        if _call_name(source, child) in global_validated_function_names:
                            calls_validated = True
                            break
                if not calls_validated:
                    continue
                # Check if this function has a termination statement
                terminations = _terminations(source, node, extra_termination_patterns)
                if not terminations:
                    continue
                # Validate via call chain
                global_validated_function_names.add(func.name.casefold())
                validated_functions.append({
                    "path": path,
                    "name": func.name,
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "conditions": [],
                    "code": func.code,
                    "validation_evidence": ["calls_validated_function", "failure_terminates"],
                })
                snippets.append({
                    "path": path,
                    "kind": "validation_function",
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "function": func.name,
                    "code": func.code,
                })
                changed = True

    existing_guards = {
        (item["path"], item["start_line"], item.get("function", "").casefold())
        for item in snippets if item["kind"] == "guard_call"
    }
    for path, source, tree in parsed_files:
        for node in _walk(tree.root_node):
            if node.type not in {"function_call_expression", "scoped_call_expression"}:
                continue
            name = _call_name(source, node)
            if name not in global_validated_function_names:
                continue
            statement = _statement(node)
            key = (path, _line(statement), name)
            if key in existing_guards:
                continue
            existing_guards.add(key)
            snippets.append({
                "path": path,
                "kind": "guard_call",
                "start_line": _line(statement),
                "end_line": _end_line(statement),
                "function": _text(source, node.child_by_field_name("function")).strip(),
                "code": _text(source, statement).strip(),
            })

    # Deduplicate: same expression across files → keep one, merge locations.
    # Also normalize array indices for dedup (e.g. $globalvars['rank'][10] → $globalvars['rank'])
    def _dedup_key(expr: str) -> str:
        return re.sub(r"(\[\d+\])+$", "", expr.casefold())
    seen: dict[str, dict[str, Any]] = {}
    for param in validated_parameters:
        key = _dedup_key(param.get("expression", ""))
        if key in seen:
            seen[key]["locations"].extend(param.get("locations", []))
            seen[key].setdefault("_files", []).append(param.get("path", ""))
        else:
            param["_files"] = [param.get("path", "")]
            seen[key] = param
    validated_parameters = list(seen.values())

    snippets = [
        item for item in snippets
        if "function" in item or "condition" in item
    ]
    snippets.sort(key=lambda item: (item["path"], item["start_line"], item["kind"]))
    return {
        "schema_version": 2,
        "language": "php",
        "parser": "tree-sitter-php",
        "parse_errors": parse_errors,
        "summary": {
            "cst_files": len(parsed_files),
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

