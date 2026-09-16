from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drhl.cli import _analyze_source
from drhl.config import load_config, validate_config
from drhl.io import write_json


TEST_ROOT = Path(__file__).resolve().parent


def _read_items(path: Path, key: str) -> list[dict]:
    if not path.is_file():
        raise RuntimeError(f"required extraction artifact is missing: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in document.get(key, []) if isinstance(item, dict)]


def _normalized_code(item: dict) -> str:
    value = item.get("if_framework") or item.get("code") or ""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def assert_three_stage_consistency(output_dir: Path) -> dict[str, int]:
    """Verify validated elements -> sourced snippets -> minimal LLM snippets."""
    source_dir = output_dir / "source"
    parameters = _read_items(source_dir / "parameters.json", "parameters")
    functions = _read_items(source_dir / "functions.json", "functions")
    snippets = _read_items(source_dir / "snippets.json", "snippets")
    llm_snippets = _read_items(source_dir / "llm_snippets.json", "snippets")

    parameter_ids = {str(item.get("id") or "") for item in parameters}
    function_ids = {str(item.get("id") or "") for item in functions}
    if "" in parameter_ids or "" in function_ids:
        raise RuntimeError("validated parameters/functions must have stable ids")

    problems: list[str] = []

    def references(item: dict) -> tuple[set[str], set[str]]:
        return (
            {str(value) for value in item.get("parameter_ids", [])},
            {str(value) for value in item.get("function_ids", [])},
        )

    raw_parameter_ids: set[str] = set()
    raw_function_ids: set[str] = set()
    raw_signatures: set[tuple[str, str]] = set()
    for index, item in enumerate(snippets):
        referenced_parameters, referenced_functions = references(item)
        if not referenced_parameters and not referenced_functions:
            problems.append(f"snippets[{index}] has no validated-element provenance")
        unknown_parameters = referenced_parameters - parameter_ids
        unknown_functions = referenced_functions - function_ids
        if unknown_parameters or unknown_functions:
            problems.append(
                f"snippets[{index}] references unknown ids: "
                f"parameters={sorted(unknown_parameters)}, functions={sorted(unknown_functions)}"
            )
        raw_parameter_ids.update(referenced_parameters)
        raw_function_ids.update(referenced_functions)
        signature = (str(item.get("path") or "").replace("\\", "/"), _normalized_code(item))
        if not signature[0] or not signature[1]:
            problems.append(f"snippets[{index}] has no path/code context")
            continue
        raw_signatures.add(signature)

    missing_parameters = parameter_ids - raw_parameter_ids
    missing_functions = function_ids - raw_function_ids
    if missing_parameters:
        problems.append(f"validated parameters without snippets: {sorted(missing_parameters)}")
    if missing_functions:
        problems.append(f"validated functions without snippets: {sorted(missing_functions)}")

    llm_signatures: set[tuple[str, str]] = set()
    for index, item in enumerate(llm_snippets):
        selected_field = (
            "if_framework"
            if _normalized_code({"if_framework": item.get("if_framework")})
            else "code"
        )
        expected_fields = {"path", selected_field}
        if set(item) != expected_fields:
            problems.append(
                f"llm_snippets[{index}] is not minimal: "
                f"expected fields={sorted(expected_fields)}, actual={sorted(item)}"
            )
        signature = (str(item.get("path") or "").replace("\\", "/"), _normalized_code(item))
        if signature in llm_signatures:
            problems.append(f"llm_snippets[{index}] duplicates a path/code context")
        llm_signatures.add(signature)
        if signature not in raw_signatures:
            problems.append(f"llm_snippets[{index}] is not derived from snippets.json")

    missing_signatures = raw_signatures - llm_signatures
    if missing_signatures:
        problems.append(
            "llm_snippets.json lost source-file/code contexts: "
            + repr(sorted(missing_signatures)[:10])
        )
    if problems:
        raise RuntimeError("three-stage source artifact consistency failed:\n- " + "\n- ".join(problems))
    return {
        "validated_parameters": len(parameter_ids),
        "validated_functions": len(function_ids),
        "snippets": len(snippets),
        "llm_snippets": len(llm_snippets),
    }


def _prepare_isolated_schema(source_run_dir: Path, output_dir: Path) -> str | None:
    """Make the existing schema available without writing to the formal run."""
    source = source_run_dir / "database" / "baseline.sql"
    destination = output_dir / "database" / "baseline.sql"
    if not source.is_file():
        if destination.is_file():
            destination.unlink()
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(source)


def run_extract(config_path: Path, save_cst_override: bool | None = None) -> dict:
    config = load_config(config_path)
    validate_config(config)

    app_name = config.run_dir.name or config.path.stem
    output_dir = (TEST_ROOT / "runs" / app_name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(config.path, output_dir / "config.json")
    schema_source = _prepare_isolated_schema(config.run_dir, output_dir)

    isolated_config = replace(config, run_dir=output_dir)
    result = _analyze_source(isolated_config, save_cst_override)
    consistency = assert_three_stage_consistency(output_dir)

    # Do not leave an obsolete CST from an earlier --save-cst invocation.
    cst_path = output_dir / "source" / "cst.json"
    if "cst" not in result["artifacts"] and cst_path.is_file():
        cst_path.unlink()

    summary = {
        "config": str(config.path),
        "source_root": str(config.target.source_root),
        "formal_run_dir": str(config.run_dir),
        "output_dir": str(output_dir),
        "database_schema_source": schema_source,
        "three_stage_consistency": consistency,
        **result,
    }
    write_json(output_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Test DRHL access-control source extraction without modifying formal run artifacts."
    )
    parser.add_argument("--config", required=True, help="Path to a DRHL application config JSON.")
    parser.add_argument(
        "--save-cst",
        action="store_true",
        default=None,
        help="Save CST output; otherwise follow analysis.source_analysis.save_cst.",
    )
    args = parser.parse_args(argv)
    summary = run_extract(Path(args.config), args.save_cst)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
