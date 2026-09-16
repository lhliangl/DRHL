from __future__ import annotations

import argparse
import json
import sys

from .config import load_config, validate_config
from .errors import DRHLError
from .io import write_json
from .pipeline import (
    run_detection_stage,
    run_pipeline,
    run_repair_stage,
    run_single_repair_test,
)
from .snippet_compaction import compact_snippet_document
from .source_analysis import analyze_access_control_source


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="drhl", description="Access-control detection and repair pipeline")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "run", "detect", "repair", "repair-test", "analyze-source"):
        command = commands.add_parser(name)
        command.add_argument("--config", required=True, help="JSON configuration file")
    commands.choices["repair"].description = (
        "Refresh access-control source artifacts, generate and validate repairs, "
        "then update run metrics and recompute total time."
    )
    commands.choices["repair-test"].add_argument(
        "--category", required=True, help="exact vulnerability category to test"
    )
    commands.choices["repair-test"].add_argument(
        "--page", required=True, help="exact vulnerable page from analysis/findings.json"
    )
    commands.choices["analyze-source"].add_argument(
        "--save-cst", action="store_true", default=None, help="save all source CSTs in one JSON file"
    )
    return root


def _analyze_source(config, save_cst_override: bool | None = None) -> dict:
    schema_path = config.run_dir / "database" / "baseline.sql"
    source_options = dict(config.analysis.get("source_analysis", {}))
    configured_save_cst = bool(source_options.get("save_cst", False))
    save_cst = configured_save_cst if save_cst_override is None else save_cst_override
    source_identity_parameters = source_options.get(
        "identity_parameters", config.analysis.get("identity_parameters", [])
    )
    source_database_fields = source_options.get(
        "access_control_database_fields", source_options.get("access_control_fields", [])
    )
    context = analyze_access_control_source(
        config.target,
        list(config.crawl.get("skip_source_dirs", [])),
        identity_parameters=[str(item) for item in source_identity_parameters],
        access_control_database_fields=[str(item) for item in source_database_fields],
        database_schema=schema_path if schema_path.is_file() else None,
        include_cst=save_cst,
        validated_function_name_patterns=[
            str(item) for item in source_options.get("validated_function_name_patterns", [])
        ],
        validated_function_code_patterns=[
            str(item) for item in source_options.get("validated_function_code_patterns", [])
        ],
        normalize_curly_string_offsets=bool(source_options.get("normalize_curly_string_offsets", False)),
        termination_patterns=[
            str(item) for item in source_options.get("termination_patterns", [])
        ],
        termination_exclude_patterns=[
            str(item) for item in source_options.get("termination_exclude_patterns", [])
        ],
        framework=(
            str(source_options["framework"])
            if source_options.get("framework")
            else None
        ),
        declarative_access_control_fields=[
            str(item)
            for item in source_options.get("declarative_access_control_fields", [])
        ],
    )
    output = config.run_dir / "source"
    paths = {
        "candidate_parameters": output / "candidate_parameters.json",
        "candidate_functions": output / "candidate_functions.json",
        "parameters": output / "parameters.json",
        "functions": output / "functions.json",
        "snippets": output / "snippets.json",
        "llm_snippets": output / "llm_snippets.json",
    }
    write_json(paths["candidate_parameters"], {"parameters": context["candidate_parameters"]})
    write_json(paths["candidate_functions"], {"functions": context["candidate_functions"]})
    write_json(paths["parameters"], {"parameters": context["parameters"]})
    write_json(paths["functions"], {"functions": context["functions"]})
    write_json(paths["snippets"], {"snippets": context["snippets"]})
    write_json(
        paths["llm_snippets"],
        compact_snippet_document(
            context["snippets"],
            exclude_kinds=source_options.get("llm_snippet_exclude_kinds", []),
            exclude_code_patterns=source_options.get("llm_snippet_exclude_code_patterns", []),
            require_if_framework=bool(
                source_options.get("llm_snippet_require_if_framework", False)
            ),
            prefix_rules=source_options.get("llm_snippet_prefix_rules", []),
        ),
    )
    if save_cst:
        paths["cst"] = output / "cst.json"
        write_json(
            paths["cst"], {"files": context["cst"], "cross_file_relations": "../graphs/static.json"}
        )
    return {
        "summary": context["summary"],
        "parser": context["parser"],
        "parse_errors": context["parse_errors"],
        "artifacts": {name: str(path) for name, path in paths.items()},
    }


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config = load_config(args.config)
        validate_config(config)
        if args.command == "validate":
            print(f"configuration is valid: {config.path}")
            return 0
        if args.command == "analyze-source":
            print(json.dumps(_analyze_source(config, args.save_cst), ensure_ascii=False, indent=2))
            return 0
        if args.command == "repair":
            result = run_repair_stage(config)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "repair-test":
            result = run_single_repair_test(config, args.category, args.page)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "detect":
            result = run_detection_stage(config)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        result = run_pipeline(config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except DRHLError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

