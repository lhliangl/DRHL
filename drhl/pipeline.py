from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from .analysis import ActiveDetector, generate_vectors
from .config import PipelineConfig, validate_config
from .crawling import crawl_all_roles, load_role_artifacts
from .database import Snapshot, create_snapshot
from .graphs import build_dynamic_graph, build_static_graph, fuse_graphs
from .io import write_json
from .models import AttackVector, Finding, RequestSpec
from .progress import progress
from .repair.patcher import create_repairs, serialize_repairs, write_repair_report
from .source_analysis import analyze_access_control_source


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _findings_report(findings) -> dict[str, Any]:
    vulnerable = sum(item.status == "vulnerable" for item in findings)
    not_vulnerable = len(findings) - vulnerable
    return {
        "summary": {
            "vulnerable": vulnerable,
            "not_vulnerable": not_vulnerable,
        },
        "findings": [item.to_dict() for item in findings],
    }


def _empty_metrics() -> dict[str, Any]:
    return {
        "hsng_construction_seconds": 0.0,
        "detection_seconds": 0.0,
        "access_control_snippets_extraction_seconds": 0.0,
        "llm_inference_seconds": 0.0,
        "tokens_in": 0,
        "tokens_out": 0,
        "tokens_total": 0,
        "api_cost_usd": 0.0,
        "api_cost_pricing_configured": False,
        "llm_requests": 0,
        "total_seconds": 0.0,
    }


def _rounded_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    result = dict(metrics)
    for key in (
        "hsng_construction_seconds",
        "detection_seconds",
        "access_control_snippets_extraction_seconds",
        "llm_inference_seconds",
        "total_seconds",
        "api_cost_usd",
    ):
        result[key] = round(float(result.get(key, 0.0)), 6)
    for key in ("tokens_in", "tokens_out", "tokens_total", "llm_requests"):
        result[key] = int(result.get(key, 0))
    result["api_cost_pricing_configured"] = bool(result.get("api_cost_pricing_configured", False))
    return result



def _graph_counts(graph: dict[str, Any], edge_key: str = "edges") -> dict[str, int]:
    return {
        "nodes": len(graph.get("nodes", [])),
        "edges": len(graph.get(edge_key, [])),
    }


def _write_graph_summary(graphs_dir, dynamic: dict[str, Any], static: dict[str, Any], fused: dict[str, Any]) -> dict[str, str]:
    summary = {
        "dynamic": _graph_counts(dynamic),
        "static": _graph_counts(static),
        "fused": _graph_counts(fused),
    }
    json_path = graphs_dir / "summary.json"
    csv_path = graphs_dir / "summary.csv"
    rows = [
        ["graph", "nodes", "edges"],
        ["dynamic", str(summary["dynamic"]["nodes"]), str(summary["dynamic"]["edges"])],
        ["static", str(summary["static"]["nodes"]), str(summary["static"]["edges"])],
        ["fused", str(summary["fused"]["nodes"]), str(summary["fused"]["edges"])],
    ]
    csv_content = "\n".join(",".join(row) for row in rows) + "\n"
    write_json(json_path, {"graphs": summary})
    try:
        csv_path.write_text(csv_content, encoding="utf-8-sig")
    except PermissionError:
        fallback_csv_path = graphs_dir / f"summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        fallback_csv_path.write_text(csv_content, encoding="utf-8-sig")
        csv_path = fallback_csv_path
    return {"json": str(json_path), "csv": str(csv_path)}


def _write_metrics(run_dir, metrics: dict[str, Any]) -> dict[str, str]:
    metrics_dir = run_dir / "metrics"
    summary = _rounded_metrics(metrics)
    json_path = metrics_dir / "summary.json"
    csv_path = metrics_dir / "summary.csv"
    notes: list[str] = []
    columns = {
        "HSNG Construction Time(s)": summary["hsng_construction_seconds"],
        "Detection Time (s)": summary["detection_seconds"],
        "Access Control Snippets Extraction Time (s)": summary[
            "access_control_snippets_extraction_seconds"
        ],
        "LLM Inference (s)": summary["llm_inference_seconds"],
        "Tokens (In / Out)": f"{summary['tokens_in']} / {summary['tokens_out']}",
        "API Cost ($)": summary["api_cost_usd"],
        "Total Time (s)": summary["total_seconds"],
    }
    if not summary.get("api_cost_pricing_configured"):
        notes.append("API cost is 0.0 because repair.llm input/output token pricing is not configured.")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    header = list(columns)
    row = [str(columns[name]) for name in header]
    csv_content = ",".join(header) + "\n" + ",".join(row) + "\n"
    try:
        csv_path.write_text(csv_content, encoding="utf-8-sig")
    except PermissionError:
        fallback_csv_path = metrics_dir / f"summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        fallback_csv_path.write_text(csv_content, encoding="utf-8-sig")
        notes.append(
            f"summary.csv was locked or not writable, so metrics CSV was written to {fallback_csv_path.name}."
        )
        csv_path = fallback_csv_path
    write_json(
        json_path,
        {
            "metrics": summary,
            "columns": columns,
            "notes": notes,
        },
    )
    return {"json": str(json_path), "csv": str(csv_path)}


def run_pipeline(config: PipelineConfig) -> dict[str, Any]:
    validate_config(config)
    total_started = perf_counter()
    metrics = _empty_metrics()
    config.run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = config.run_dir / "run.json"
    manifest: dict[str, Any] = {
        "status": "running",
        "started_at": _timestamp(),
        "config": str(config.path),
        "artifacts": {},
    }
    write_json(manifest_path, manifest)
    snapshot: Snapshot | None = None
    excluded_total_seconds = 0.0
    source_context: dict[str, Any] = {
        "candidate_parameters": [],
        "candidate_functions": [],
        "parameters": [],
        "functions": [],
        "snippets": [],
        "summary": {},
        "cst": [],
    }
    progress(f"Pipeline started. Run directory: {config.run_dir}")

    try:
        mode = str(config.crawl.get("mode", "selenium")).lower()
        progress(f"Stage 1/6: collect dynamic data (mode: {mode})")
        hsng_started = perf_counter()
        if mode == "selenium":
            snapshot = create_snapshot(config.database, config.run_dir / "database")
            crawls = crawl_all_roles(config, snapshot)
        else:
            crawls = load_role_artifacts(config)

        progress("Stage 2/6: build dynamic graph")
        dynamic = build_dynamic_graph(crawls)
        dynamic_path = config.run_dir / "graphs" / "dynamic.json"
        write_json(dynamic_path, dynamic)
        manifest["artifacts"]["dynamic_graph"] = str(dynamic_path)
        progress(f"Dynamic graph: {len(dynamic['nodes'])} nodes, {len(dynamic['edges'])} edges")

        progress(f"Stage 3/6: analyze {config.target.language} source and dependencies")
        skip_source_dirs = list(config.crawl.get("skip_source_dirs", []))
        static = build_static_graph(
            config.target,
            dynamic["nodes"],
            skip_source_dirs,
        )
        static_path = config.run_dir / "graphs" / "static.json"
        write_json(static_path, static)
        manifest["artifacts"]["static_graph"] = str(static_path)
        metrics["hsng_construction_seconds"] += perf_counter() - hsng_started

        source_options = dict(config.analysis.get("source_analysis", {}))
        save_cst = bool(source_options.get("save_cst", False))
        source_identity_parameters = source_options.get(
            "identity_parameters", config.analysis.get("identity_parameters", [])
        )
        source_database_fields = source_options.get(
            "access_control_database_fields", source_options.get("access_control_fields", [])
        )
        snippet_started = perf_counter()
        source_context = analyze_access_control_source(
            config.target,
            skip_source_dirs,
            identity_parameters=[str(item) for item in source_identity_parameters],
            access_control_database_fields=[str(item) for item in source_database_fields],
            database_schema=getattr(snapshot, "path", None),
            include_cst=save_cst,
            validated_function_name_patterns=[
                str(item) for item in source_options.get("validated_function_name_patterns", [])
            ],
            validated_function_code_patterns=[
                str(item) for item in source_options.get("validated_function_code_patterns", [])
            ],
            normalize_curly_string_offsets=bool(source_options.get("normalize_curly_string_offsets", False)),
        )
        metrics["access_control_snippets_extraction_seconds"] += perf_counter() - snippet_started

        source_dir = config.run_dir / "source"
        candidate_parameter_path = source_dir / "candidate_parameters.json"
        candidate_function_path = source_dir / "candidate_functions.json"
        parameter_path = source_dir / "parameters.json"
        function_path = source_dir / "functions.json"
        snippet_path = source_dir / "snippets.json"
        write_json(candidate_parameter_path, {"parameters": source_context["candidate_parameters"]})
        write_json(candidate_function_path, {"functions": source_context["candidate_functions"]})
        write_json(parameter_path, {"parameters": source_context["parameters"]})
        write_json(function_path, {"functions": source_context["functions"]})
        write_json(snippet_path, {"snippets": source_context["snippets"]})
        if save_cst:
            cst_path = source_dir / "cst.json"
            write_json(cst_path, {"files": source_context["cst"], "cross_file_relations": "../graphs/static.json"})
            manifest["artifacts"]["source_cst"] = str(cst_path)
        manifest["artifacts"]["candidate_parameters"] = str(candidate_parameter_path)
        manifest["artifacts"]["candidate_functions"] = str(candidate_function_path)
        manifest["artifacts"]["access_control_parameters"] = str(parameter_path)
        manifest["artifacts"]["access_control_functions"] = str(function_path)
        manifest["artifacts"]["access_control_snippets"] = str(snippet_path)
        summary = source_context["summary"]
        progress(
            "Access-control source analysis: "
            f"{summary['candidate_parameters']} LCP candidates -> {summary['parameters']} validated; "
            f"{summary['candidate_functions']} LCF candidates -> {summary['functions']} validated; "
            f"{summary['snippets']} snippets"
        )
        progress(f"Static graph: {len(static['nodes'])} source files, {len(static['edges'])} dependency edges")

        progress("Stage 4/6: fuse graphs and generate attack vectors")
        hsng_started = perf_counter()
        fused = fuse_graphs(dynamic, static)
        fused_path = config.run_dir / "graphs" / "fused.json"
        write_json(fused_path, fused)
        manifest["artifacts"]["fused_graph"] = str(fused_path)
        graph_summary_paths = _write_graph_summary(config.run_dir / "graphs", dynamic, static, fused)
        manifest["artifacts"]["graph_summary"] = graph_summary_paths["json"]
        manifest["artifacts"]["graph_summary_csv"] = graph_summary_paths["csv"]
        progress(
            "Graph node counts: "
            f"dynamic={len(dynamic.get('nodes', []))}, "
            f"static={len(static.get('nodes', []))}, "
            f"fused={len(fused.get('nodes', []))}"
        )
        vectors = generate_vectors(
            fused,
            [str(item) for item in config.analysis.get("identity_parameters", [])],
            [str(item) for item in config.analysis.get("static_exclude_patterns", [])],
            [str(item) for item in config.analysis.get("force_static_pages", [])],
            [str(item) for item in config.analysis.get("force_horizontal_pages", [])],
            [str(item) for item in config.analysis.get("horizontal_exclude_patterns", [])],
            [str(item) for item in config.analysis.get("vertical_only_patterns", [])],
            [str(item) for item in config.analysis.get("force_vertical_pages", [])],
            dict(config.analysis.get("vertical_overrides", {})),
            [str(item) for item in config.analysis.get("post_page_open_get_patterns", [])],
            [dict(item) for item in config.analysis.get("horizontal_page_overrides", [])],
            [str(item) for item in config.analysis.get("admin_only_exclude_patterns", [])],
            [str(item) for item in config.analysis.get("authenticated_only_exclude_patterns", [])],
        )
        vector_path = config.run_dir / "analysis" / "vectors.json"
        write_json(vector_path, {"vectors": [vector.to_dict() for vector in vectors]})
        manifest["artifacts"]["attack_vectors"] = str(vector_path)
        metrics["hsng_construction_seconds"] += perf_counter() - hsng_started
        progress(f"Attack vectors generated: {len(vectors)}")

        findings = []
        progress("Stage 5/6: active access-control verification")
        if config.analysis.get("active_detection", True):
            if snapshot is None:
                snapshot = create_snapshot(config.database, config.run_dir / "database")
                snapshot.create()
            detector = ActiveDetector(config, snapshot)
            detection_started = perf_counter()
            findings = detector.run(vectors)
            metrics["detection_seconds"] += perf_counter() - detection_started
            findings_path = config.run_dir / "analysis" / "findings.json"
            report = _findings_report(findings)
            write_json(findings_path, report)
            manifest["artifacts"]["findings"] = str(findings_path)
            progress(
                f"Active detection completed: {report['summary']['vulnerable']} vulnerable, "
                f"{report['summary']['not_vulnerable']} not vulnerable"
            )
        else:
            progress("Active detection disabled by configuration")

        progress("Stage 6/6: generate repair copies and manifest")
        repair_dir = config.run_dir / "repair"
        shutil.rmtree(repair_dir, ignore_errors=True)
        if config.repair.get("enabled", True) and findings:
            repairs = create_repairs(
                config,
                fused,
                findings,
                source_context=source_context,
                metrics=metrics,
                vectors=vectors,
                snapshot=snapshot,
            )
            repair_path = config.run_dir / "repair" / "manifest.json"
            repair_report_path = config.run_dir / "repair" / "repair_report.md"
            write_json(repair_path, serialize_repairs(repairs))
            write_repair_report(repairs, repair_report_path)
            if snapshot is not None:
                snapshot.restore()
                progress("Repair validation cleanup completed: database baseline restored")
            manifest["artifacts"]["repairs"] = str(repair_path)
            manifest["artifacts"]["repair_report"] = str(repair_report_path)
            progress(f"Repair stage completed: {len(repairs)} items")
        else:
            progress("No repair items generated")

        metrics["total_seconds"] = max(0.0, perf_counter() - total_started - excluded_total_seconds)
        metrics_paths = _write_metrics(config.run_dir, metrics)
        manifest["artifacts"]["metrics_json"] = metrics_paths["json"]
        manifest["artifacts"]["metrics_csv"] = metrics_paths["csv"]
        manifest["status"] = "completed"
        manifest["finished_at"] = _timestamp()
        write_json(manifest_path, manifest)
        progress(f"Metrics written: {metrics_paths['json']}")
        progress("Pipeline completed")
        return manifest
    except BaseException as exc:
        metrics["total_seconds"] = max(0.0, perf_counter() - total_started - excluded_total_seconds)
        try:
            metrics_paths = _write_metrics(config.run_dir, metrics)
            manifest["artifacts"]["metrics_json"] = metrics_paths["json"]
            manifest["artifacts"]["metrics_csv"] = metrics_paths["csv"]
        except Exception:
            pass
        manifest["status"] = "failed"
        manifest["finished_at"] = _timestamp()
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        write_json(manifest_path, manifest)
        progress(f"Pipeline failed: {manifest['error']}")
        raise





def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_repair_source_context(run_dir) -> dict[str, Any]:
    source_dir = run_dir / "source"
    def load(name: str, key: str) -> list[Any]:
        path = source_dir / name
        if not path.is_file():
            return []
        return list(_read_json(path).get(key, []))
    return {
        "candidate_parameters": load("candidate_parameters.json", "parameters"),
        "candidate_functions": load("candidate_functions.json", "functions"),
        "parameters": load("parameters.json", "parameters"),
        "functions": load("functions.json", "functions"),
        "snippets": load("snippets.json", "snippets"),
        "summary": {},
        "cst": [],
    }


def _load_repair_vectors(run_dir) -> list[AttackVector]:
    path = run_dir / "analysis" / "vectors.json"
    vectors = []
    for item in _read_json(path).get("vectors", []):
        vectors.append(
            AttackVector(
                str(item["category"]),
                str(item["page"]),
                [str(role) for role in item.get("authorized_roles", [])],
                RequestSpec.from_dict(item.get("request", {})),
                [str(name) for name in item.get("identity_parameters", [])],
                [str(page) for page in item.get("page_overrides", [])],
            )
        )
    return vectors


def _load_repair_findings(run_dir) -> list[Finding]:
    path = run_dir / "analysis" / "findings.json"
    findings = []
    for item in _read_json(path).get("findings", []):
        findings.append(
            Finding(
                str(item["category"]),
                str(item["page"]),
                str(item["actor"]),
                str(item["status"]),
                str(item.get("confidence", "")),
                str(item.get("method") or "GET"),
                item.get("http_status"),
                list(item.get("evidence", [])),
                item.get("error"),
            )
        )
    return findings


def _load_existing_metrics(run_dir) -> dict[str, Any]:
    path = run_dir / "metrics" / "summary.json"
    if not path.is_file():
        return _empty_metrics()
    metrics = dict(_read_json(path).get("metrics", {}))
    defaults = _empty_metrics()
    defaults.update(metrics)
    return defaults


def run_repair_stage(config: PipelineConfig) -> dict[str, Any]:
    validate_config(config)
    metrics = _empty_metrics()
    for key, value in {
        "llm_inference_seconds": 0.0,
        "tokens_in": 0,
        "tokens_out": 0,
        "tokens_total": 0,
        "api_cost_usd": 0.0,
        "api_cost_pricing_configured": False,
        "llm_requests": 0,
    }.items():
        metrics[key] = value

    progress(f"Repair-only stage started. Run directory: {config.run_dir}")
    fused = _read_json(config.run_dir / "graphs" / "fused.json")
    findings = _load_repair_findings(config.run_dir)
    vectors = _load_repair_vectors(config.run_dir)
    source_context = _load_repair_source_context(config.run_dir)
    snapshot = create_snapshot(config.database, config.run_dir / "database")
    if not getattr(snapshot, "path", config.run_dir / "database" / "baseline.sql").is_file():
        progress("Database baseline was missing; creating a fresh repair baseline...")
        snapshot.create()

    repair_dir = config.run_dir / "repair"
    shutil.rmtree(repair_dir, ignore_errors=True)
    repairs = create_repairs(
        config,
        fused,
        findings,
        source_context=source_context,
        metrics=metrics,
        vectors=vectors,
        snapshot=snapshot,
    )
    repair_path = repair_dir / "manifest.json"
    repair_report_path = repair_dir / "repair_report.md"
    write_json(repair_path, serialize_repairs(repairs))
    write_repair_report(repairs, repair_report_path)
    try:
        snapshot.restore()
        progress("Repair-only cleanup completed: database baseline restored")
    except Exception as exc:
        progress(f"Repair-only cleanup warning: database restore failed: {type(exc).__name__}: {exc}")

    run_path = config.run_dir / "run.json"
    if run_path.is_file():
        manifest = _read_json(run_path)
    else:
        manifest = {"artifacts": {}}
    artifacts = manifest.setdefault("artifacts", {})
    artifacts["repairs"] = str(repair_path)
    artifacts["repair_report"] = str(repair_report_path)
    manifest["repair_only_finished_at"] = _timestamp()
    write_json(run_path, manifest)
    progress(f"Repair-only stage completed: {len(repairs)} items")
    progress("Repair-only stage did not rewrite metrics; metrics are written only by full pipeline runs")
    return {
        "status": "completed",
        "artifacts": {
            "repairs": str(repair_path),
            "repair_report": str(repair_report_path),
        },
        "repair_metrics": _rounded_metrics(metrics),
        "repair_summary": serialize_repairs(repairs)["summary"],
    }

