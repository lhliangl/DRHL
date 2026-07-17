from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import TargetConfig
from .java_jsp_source_analysis import analyze_java_jsp_source
from .go_source_analysis import analyze_go_source
from .php_source_analysis import analyze_php_source
from .python_source_analysis import analyze_python_source


def _empty(language: str) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "language": language,
        "parser": None,
        "parse_errors": [],
        "summary": {
            "cst_files": 0,
            "candidate_parameters": 0,
            "candidate_functions": 0,
            "parameters": 0,
            "functions": 0,
            "snippets": 0,
        },
        "cst": [],
        "candidate_parameters": [],
        "candidate_functions": [],
        "parameters": [],
        "functions": [],
        "snippets": [],
    }


def analyze_access_control_source(
    target: TargetConfig,
    skip_dirs: list[str] | None = None,
    *,
    identity_parameters: list[str] | None = None,
    access_control_database_fields: list[str] | None = None,
    database_schema: Path | None = None,
    include_cst: bool = False,
    validated_function_name_patterns: list[str] | None = None,
    validated_function_code_patterns: list[str] | None = None,
    normalize_curly_string_offsets: bool = False,
    termination_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Extract candidates, validate authorization semantics, and build repair context."""
    if target.language == "php":
        return analyze_php_source(
            target.source_root,
            skip_dirs=skip_dirs,
            identity_parameters=identity_parameters,
            access_control_database_fields=access_control_database_fields,
            database_schema=database_schema,
            include_cst=include_cst,
            validated_function_name_patterns=validated_function_name_patterns,
            validated_function_code_patterns=validated_function_code_patterns,
            normalize_curly_string_offsets=normalize_curly_string_offsets,
            termination_patterns=termination_patterns,
        )
    if target.language in {"java", "jsp"}:
        return analyze_java_jsp_source(
            target.source_root,
            language=target.language,
            skip_dirs=skip_dirs,
            identity_parameters=identity_parameters,
            access_control_database_fields=access_control_database_fields,
            database_schema=database_schema,
            include_cst=include_cst,
            validated_function_name_patterns=validated_function_name_patterns,
            validated_function_code_patterns=validated_function_code_patterns,
        )
    if target.language == "python":
        return analyze_python_source(
            target.source_root,
            skip_dirs=skip_dirs,
            identity_parameters=identity_parameters,
            access_control_database_fields=access_control_database_fields,
            database_schema=database_schema,
            include_cst=include_cst,
            validated_function_name_patterns=validated_function_name_patterns,
            validated_function_code_patterns=validated_function_code_patterns,
        )
    if target.language == "go":
        return analyze_go_source(
            target.source_root,
            skip_dirs=skip_dirs,
            identity_parameters=identity_parameters,
            access_control_database_fields=access_control_database_fields,
            database_schema=database_schema,
            include_cst=include_cst,
            validated_function_name_patterns=validated_function_name_patterns,
            validated_function_code_patterns=validated_function_code_patterns,
        )
    return _empty(target.language)

