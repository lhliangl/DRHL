from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drhl.io import write_json
from test_extract.extract import TEST_ROOT, assert_three_stage_consistency, run_extract


GROUND_TRUTH_ROOT = TEST_ROOT / "ground_truth"
DEFAULT_REPORT = TEST_ROOT / "extraction_metrics.md"
DEFAULT_DETAILS = TEST_ROOT / "evaluation.json"


def _normalized_name(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = text.replace('"', "'")
    text = re.sub(r"\s+", "", text)
    return text.lstrip("$")


def _name_variants(value: Any) -> set[str]:
    normalized = _normalized_name(value)
    if not normalized:
        return set()
    variants = {normalized}
    # PHP object/array parameters keep their complete expression.  Treating an
    # index such as ['action'] as an independent variant lets unrelated values
    # (for example an admin permission and a request action) match each other.
    # Receiver-insensitive matching is reserved for ordinary dotted fields in
    # the Python/Java/Go representations documented by this harness.
    if "[" not in normalized and "->" not in normalized and "." in normalized:
        variants.add(_normalized_name(normalized.rsplit(".", 1)[-1]))
    return {item for item in variants if item}


def _semantic_parameter_key(value: Any) -> str:
    normalized = _normalized_name(value)
    if not normalized:
        return ""
    if "[" in normalized or "->" in normalized:
        return normalized
    if normalized == "request.user" or normalized.startswith("request.user."):
        return normalized
    if "->" in normalized:
        return _normalized_name(normalized.rsplit("->", 1)[-1])
    if "." in normalized:
        return _normalized_name(normalized.rsplit(".", 1)[-1])
    return normalized


def _unique_ground_truth(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        name = str(item.get("name") or "").strip()
        key = _normalized_name(name)
        if not key or key in seen:
            continue
        seen.add(key)
        variants = _name_variants(name)
        variants.add(key)
        result.append({"name": name, "variants": sorted(variants)})
    return result


def _unique_predicted_parameters(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        expression = str(item.get("expression") or item.get("name") or "").strip()
        key = _semantic_parameter_key(expression)
        if not key:
            continue
        entry = grouped.setdefault(
            key,
            {"name": expression, "aliases": set(), "paths": set(), "variants": set()},
        )
        candidates = [expression, *[str(alias) for alias in item.get("aliases", [])]]
        entry["aliases"].update(candidate for candidate in candidates if candidate)
        entry["paths"].add(str(item.get("path") or ""))
        for candidate in candidates:
            entry["variants"].update(_name_variants(candidate))
            semantic_key = _semantic_parameter_key(candidate)
            if semantic_key:
                entry["variants"].add(semantic_key)
    return [
        {
            "name": item["name"],
            "aliases": sorted(item["aliases"]),
            "paths": sorted(path for path in item["paths"] if path),
            "variants": sorted(item["variants"]),
        }
        for _, item in sorted(grouped.items())
    ]


def _unique_predicted_functions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        name = str(item.get("name") or item.get("function") or "").strip()
        key = _normalized_name(name)
        if not key:
            continue
        entry = grouped.setdefault(key, {"name": name, "paths": set(), "variants": {key}})
        entry["paths"].add(str(item.get("path") or ""))
    return [
        {
            "name": item["name"],
            "paths": sorted(path for path in item["paths"] if path),
            "variants": sorted(item["variants"]),
        }
        for _, item in sorted(grouped.items())
    ]


def _match_entities(
    ground_truth: list[dict[str, Any]], predicted: list[dict[str, Any]]
) -> dict[str, Any]:
    unmatched_predictions = set(range(len(predicted)))
    matches: list[dict[str, Any]] = []
    false_negatives: list[str] = []

    for expected in ground_truth:
        expected_name = _normalized_name(expected["name"])
        expected_variants = set(expected["variants"])
        ranked: list[tuple[int, int]] = []
        for index in unmatched_predictions:
            actual = predicted[index]
            actual_name = _normalized_name(actual["name"])
            actual_variants = set(actual["variants"])
            if expected_name == actual_name:
                ranked.append((0, index))
            elif expected_name in actual_variants:
                ranked.append((1, index))
            elif expected_variants & actual_variants:
                ranked.append((2, index))
        if not ranked:
            false_negatives.append(expected["name"])
            continue
        _, selected = min(ranked)
        unmatched_predictions.remove(selected)
        matches.append(
            {
                "ground_truth": expected["name"],
                "prediction": predicted[selected]["name"],
                "prediction_paths": predicted[selected].get("paths", []),
            }
        )

    false_positives = [predicted[index]["name"] for index in sorted(unmatched_predictions)]
    tp = len(matches)
    fp = len(false_positives)
    fn = len(false_negatives)
    return {
        "ground_truth_count": len(ground_truth),
        "prediction_count": len(predicted),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "matches": matches,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def _read_items(path: Path, key: str) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [dict(item) for item in data.get(key, []) if isinstance(item, dict)]


def _evaluate_app(app: str) -> dict[str, Any]:
    output = TEST_ROOT / "runs" / app / "source"
    ground_truth = GROUND_TRUTH_ROOT / app

    expected_parameters = _unique_ground_truth(_read_items(ground_truth / "parameters.json", "parameters"))
    expected_functions = _unique_ground_truth(_read_items(ground_truth / "functions.json", "functions"))
    predicted_parameters = _unique_predicted_parameters(_read_items(output / "parameters.json", "parameters"))
    predicted_functions = _unique_predicted_functions(_read_items(output / "functions.json", "functions"))

    parameter_result = _match_entities(expected_parameters, predicted_parameters)
    function_result = _match_entities(expected_functions, predicted_functions)
    tp = parameter_result["tp"] + function_result["tp"]
    fp = parameter_result["fp"] + function_result["fp"]
    fn = parameter_result["fn"] + function_result["fn"]
    return {
        "app": app,
        "parameters": parameter_result,
        "functions": function_result,
        "total": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
        },
    }


def _percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def _list_or_none(items: list[str]) -> str:
    return "、".join(f"`{item}`" for item in items) if items else "无"


def _write_report(
    results: list[dict[str, Any]],
    extraction_summaries: dict[str, Any],
    report_path: Path,
) -> None:
    total_tp = sum(item["total"]["tp"] for item in results)
    total_fp = sum(item["total"]["fp"] for item in results)
    total_fn = sum(item["total"]["fn"] for item in results)
    total_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 0.0
    total_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn else 0.0

    actual_parameter_gt = sum(item["parameters"]["ground_truth_count"] for item in results)
    actual_function_gt = sum(item["functions"]["ground_truth_count"] for item in results)
    manifest = json.loads((GROUND_TRUTH_ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_apps = {
        str(name).casefold(): value for name, value in dict(manifest.get("apps", {})).items()
    }
    manifest_parameter_gt = sum(
        int(value.get("parameters", 0))
        for name, value in manifest_apps.items()
    )
    manifest_function_gt = sum(
        int(value.get("functions", 0))
        for name, value in manifest_apps.items()
    )
    parse_errors = {
        app: summary.get("parse_errors", [])
        for app, summary in extraction_summaries.items()
        if summary.get("parse_errors")
    }

    lines = [
        "# 访问控制代码提取评测",
        "",
        f"生成时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "## 评测方法",
        "",
        "使用 `test_extract/extract.py` 生成提取结果。该入口调用与 DRHL 主流程相同的源码分析和 `llm_snippets.json` 精简逻辑，并评测全部已配置应用。",
        "",
        "以 `test_extract/ground_truth/<app>/parameters.json` 和 `functions.json` 中的人工审核条目为参考集。参数按规范化语义名匹配：保留 PHP 超全局变量及对象数组的完整表达式；普通点号对象字段去除接收者前缀，例如 `user.IsSuperAdmin` 与 `profileUser.IsSuperAdmin` 均归一为 `IsSuperAdmin`。同名预测去重并使用 `aliases` 辅助匹配。函数按不区分大小写的唯一函数名匹配。每个预测实体最多匹配一个参考实体。",
        "",
        "每个应用的总指标由参数实体和函数实体相加：",
        "",
        "- `precision = TP / (TP + FP)`",
        "- `recall = TP / (TP + FN)`",
        "",
        "## 结果",
        "",
        "| 应用 | TP | FP | FN | Precision | Recall | 参数 TP/FP/FN | 函数 TP/FP/FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in results:
        total = item["total"]
        parameters = item["parameters"]
        functions = item["functions"]
        lines.append(
            f"| {item['app']} | {total['tp']} | {total['fp']} | {total['fn']} | "
            f"{_percentage(total['precision'])} | {_percentage(total['recall'])} | "
            f"{parameters['tp']}/{parameters['fp']}/{parameters['fn']} | "
            f"{functions['tp']}/{functions['fp']}/{functions['fn']} |"
        )
    lines.extend(
        [
            f"| **微平均总计** | **{total_tp}** | **{total_fp}** | **{total_fn}** | "
            f"**{_percentage(total_precision)}** | **{_percentage(total_recall)}** | — | — |",
            "",
            "## Ground truth 一致性说明",
            "",
            f"本次直接读取全部应用 JSON 数组并按唯一语义名去重，得到参数 {actual_parameter_gt} 项、函数 {actual_function_gt} 项。`manifest.json` 中按文件条目统计为参数 {manifest_parameter_gt} 项、函数 {manifest_function_gt} 项；最终指标以去重后的实际评测实体为准。",
            "",
            "## 解析说明",
            "",
        ]
    )
    if parse_errors:
        for app, errors in parse_errors.items():
            for error in errors:
                lines.append(
                    f"- {app}: `{error.get('path', '')}:{error.get('line', '')}` — {error.get('message', '')}"
                )
    else:
        lines.append("- 所有应用均无解析错误。")
    lines.extend(["", "## 错误明细", ""])
    for item in results:
        lines.extend(
            [
                f"### {item['app']}",
                "",
                f"- 参数 FP：{_list_or_none(item['parameters']['false_positives'])}",
                f"- 参数 FN：{_list_or_none(item['parameters']['false_negatives'])}",
                f"- 函数 FP：{_list_or_none(item['functions']['false_positives'])}",
                f"- 函数 FN：{_list_or_none(item['functions']['false_negatives'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## 复现方式",
            "",
            "在仓库根目录使用主实验的 Conda 环境运行：",
            "",
            "```powershell",
            "D:\\Anaconda3\\envs\\drhl\\python.exe test_extract\\evaluate.py",
            "```",
            "",
            "机器可读的匹配明细保存在 `test_extract/evaluation.json`，各应用提取产物保存在 `test_extract/runs/<app>`。",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_evaluation(*, run_extraction: bool = True) -> dict[str, Any]:
    config_paths = sorted((ROOT / "configs").glob("*.json"))
    ground_truth_apps = {path.name.casefold(): path.name for path in GROUND_TRUTH_ROOT.iterdir() if path.is_dir()}
    results: list[dict[str, Any]] = []
    extraction_summaries: dict[str, Any] = {}

    for config_path in config_paths:
        app = ground_truth_apps.get(config_path.stem.casefold())
        if app is None:
            raise FileNotFoundError(f"ground truth directory was not found for {config_path.stem}")
        if run_extraction:
            print(f"[test_extract] extracting {app}...", flush=True)
            extraction_summaries[app] = run_extract(config_path)
        else:
            summary_path = TEST_ROOT / "runs" / app / "summary.json"
            extraction_summaries[app] = json.loads(summary_path.read_text(encoding="utf-8"))
        extraction_summaries[app]["three_stage_consistency"] = (
            assert_three_stage_consistency(TEST_ROOT / "runs" / app)
        )
        results.append(_evaluate_app(app))

    details = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "excluded_apps": [],
        "matching_unit": "unique normalized semantic parameter/function name",
        "results": results,
        "extraction_summaries": extraction_summaries,
    }
    write_json(DEFAULT_DETAILS, details)
    _write_report(results, extraction_summaries, DEFAULT_REPORT)
    return {
        "applications": len(results),
        "report": str(DEFAULT_REPORT),
        "details": str(DEFAULT_DETAILS),
        "runs": str(TEST_ROOT / "runs"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run isolated source extraction and evaluate it against manual ground truth."
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Recalculate metrics from existing test_extract/runs outputs without rerunning extraction.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_evaluation(run_extraction=not args.no_extract), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
