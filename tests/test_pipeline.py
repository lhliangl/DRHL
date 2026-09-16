from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.config import PipelineConfig, TargetConfig, load_config
from drhl.io import write_json
from drhl.models import AttackVector, Finding, RequestSpec, RoleCrawl
from drhl.pipeline import (
    _combine_extraction_repair_metrics,
    _replace_repair_only_timing,
    run_detection_stage,
    run_pipeline,
    run_repair_stage,
)


class OfflinePipelineTests(unittest.TestCase):
    def test_detection_rerun_rebuilds_graphs_but_skips_extraction_repair_and_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "source"
            source_root.mkdir()
            run_dir = root / "run"
            write_json(run_dir / "run.json", {"artifacts": {}, "finished_at": "original"})
            metrics_json = run_dir / "metrics" / "summary.json"
            metrics_csv = run_dir / "metrics" / "summary.csv"
            metrics_json.parent.mkdir(parents=True)
            metrics_json.write_bytes(b'{"metrics":{"detection_seconds":123.0}}\n')
            metrics_csv.write_bytes(b"original metrics csv\n")
            original_json = metrics_json.read_bytes()
            original_csv = metrics_csv.read_bytes()
            baseline = run_dir / "database" / "baseline.sql"
            baseline.parent.mkdir(parents=True)
            baseline.write_text("baseline", encoding="utf-8")

            config = PipelineConfig(
                path=root / "config.json", run_dir=run_dir,
                target=TargetConfig("http://example.test/", source_root, "php", (".php",)),
                database={}, crawl={"mode": "artifacts"}, roles=(), analysis={}, repair={},
            )
            vector = AttackVector("static_only", "install.php", [], RequestSpec("GET"))
            finding = Finding("static_only", "install.php", "visitor", "vulnerable", "high", "GET", 200)
            dynamic = {"nodes": ["install.php"], "edges": []}
            static = {"nodes": ["install.php"], "edges": [], "source_map": {"install.php": "install.php"}}
            fused = {"nodes": ["install.php"], "edges": [], "source_map": {"install.php": "install.php"}}

            class FakeSnapshot:
                path = baseline
                creates = 0
                restores = 0

                def create(self):
                    self.creates += 1
                    return self.path

                def restore(self):
                    self.restores += 1

            snapshot = FakeSnapshot()

            class FakeDetector:
                def __init__(self, ignored_config, ignored_snapshot):
                    pass

                def run(self, vectors):
                    self.received = vectors
                    return [finding]

            with patch("drhl.pipeline.validate_config"), \
                 patch("drhl.pipeline.load_role_artifacts", return_value=[]), \
                 patch("drhl.pipeline.build_dynamic_graph", return_value=dynamic), \
                 patch("drhl.pipeline.build_static_graph", return_value=static) as build_static, \
                 patch("drhl.pipeline.fuse_graphs", return_value=fused), \
                 patch("drhl.pipeline.generate_vectors", return_value=[vector]), \
                 patch("drhl.pipeline.create_snapshot", return_value=snapshot), \
                 patch("drhl.pipeline.ActiveDetector", FakeDetector), \
                 patch("drhl.pipeline.analyze_access_control_source", side_effect=AssertionError("source extraction must not run")), \
                 patch("drhl.pipeline.create_repairs", side_effect=AssertionError("repair must not run")), \
                 patch("drhl.pipeline._write_metrics", side_effect=AssertionError("metrics must not be written")):
                result = run_detection_stage(config)

            self.assertEqual(result["summary"], {"vulnerable": 1, "not_vulnerable": 0})
            self.assertEqual(snapshot.creates, 1)
            self.assertEqual(snapshot.restores, 1)
            build_static.assert_called_once()
            self.assertEqual(metrics_json.read_bytes(), original_json)
            self.assertEqual(metrics_csv.read_bytes(), original_csv)
            self.assertTrue((run_dir / "graphs" / "dynamic.json").is_file())
            self.assertTrue((run_dir / "graphs" / "static.json").is_file())
            self.assertTrue((run_dir / "graphs" / "fused.json").is_file())
            self.assertTrue((run_dir / "analysis" / "vectors.json").is_file())
            findings = json.loads((run_dir / "analysis" / "findings.json").read_text(encoding="utf-8"))
            self.assertEqual(findings["summary"]["vulnerable"], 1)
            self.assertTrue((run_dir / "analysis" / "vulnerability_report.md").is_file())
            run_manifest = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_manifest["finished_at"], "original")
            self.assertIn("detection_rerun_finished_at", run_manifest)

    def test_repair_only_timing_replaces_llm_time_and_tokens_and_preserves_other_metrics(self):
        existing = {
            "hsng_construction_seconds": 10.0,
            "detection_seconds": 5.0,
            "access_control_snippets_extraction_seconds": 2.0,
            "llm_inference_seconds": 80.0,
            "tokens_in": 123,
            "tokens_out": 456,
            "tokens_total": 579,
            "llm_requests": 8,
            "api_cost_usd": 1.25,
            "api_cost_pricing_configured": True,
            "total_seconds": 100.0,
        }
        repair = {
            "llm_inference_seconds": 30.0,
            "tokens_in": 999,
            "tokens_out": 888,
            "tokens_total": 123,
            "total_seconds": 999.0,
        }

        updated = _replace_repair_only_timing(existing, repair)

        self.assertEqual(updated["llm_inference_seconds"], 30.0)
        self.assertEqual(updated["tokens_in"], 999)
        self.assertEqual(updated["tokens_out"], 888)
        self.assertEqual(updated["tokens_total"], 1887)
        self.assertEqual(updated["total_seconds"], 50.0)
        for key in (
            "hsng_construction_seconds", "detection_seconds",
            "access_control_snippets_extraction_seconds", "llm_requests", "api_cost_usd",
            "api_cost_pricing_configured",
        ):
            self.assertEqual(updated[key], existing[key])

    def test_extraction_repair_metrics_replace_rerun_stages_and_recompute_total(self):
        existing = {
            "hsng_construction_seconds": 10.0,
            "detection_seconds": 5.0,
            "access_control_snippets_extraction_seconds": 2.0,
            "llm_inference_seconds": 80.0,
            "tokens_in": 123,
            "tokens_out": 456,
            "tokens_total": 579,
            "llm_requests": 8,
            "api_cost_usd": 1.25,
            "api_cost_pricing_configured": True,
            "total_seconds": 100.0,
        }
        rerun = {
            "access_control_snippets_extraction_seconds": 3.0,
            "llm_inference_seconds": 30.0,
            "tokens_in": 999,
            "tokens_out": 888,
            "llm_requests": 2,
            "api_cost_usd": 0.5,
            "api_cost_pricing_configured": True,
        }

        updated = _combine_extraction_repair_metrics(existing, rerun)

        self.assertEqual(updated["hsng_construction_seconds"], 10.0)
        self.assertEqual(updated["detection_seconds"], 5.0)
        self.assertEqual(updated["access_control_snippets_extraction_seconds"], 3.0)
        self.assertEqual(updated["llm_inference_seconds"], 30.0)
        self.assertEqual(updated["tokens_in"], 999)
        self.assertEqual(updated["tokens_out"], 888)
        self.assertEqual(updated["tokens_total"], 1887)
        self.assertEqual(updated["llm_requests"], 2)
        self.assertEqual(updated["api_cost_usd"], 0.5)
        self.assertEqual(updated["total_seconds"], 51.0)

    def test_repair_command_refreshes_source_artifacts_before_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "source"
            source_root.mkdir()
            (source_root / "auth.php").write_text("<?php guard();", encoding="utf-8")
            run_dir = root / "run"
            baseline = run_dir / "database" / "baseline.sql"
            baseline.parent.mkdir(parents=True)
            baseline.write_text("baseline", encoding="utf-8")
            write_json(run_dir / "graphs" / "fused.json", {"source_map": {}})
            write_json(run_dir / "analysis" / "findings.json", {"findings": []})
            write_json(run_dir / "analysis" / "vectors.json", {"vectors": []})
            write_json(
                run_dir / "metrics" / "summary.json",
                {
                    "metrics": {
                        "hsng_construction_seconds": 7.0,
                        "detection_seconds": 3.0,
                        "access_control_snippets_extraction_seconds": 99.0,
                        "llm_inference_seconds": 88.0,
                        "total_seconds": 200.0,
                    }
                },
            )
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=run_dir,
                target=TargetConfig("http://example.test/", source_root, "php", (".php",)),
                database={},
                crawl={"mode": "artifacts"},
                roles=(),
                analysis={},
                repair={},
            )

            class FakeSnapshot:
                path = baseline
                restored = False

                def restore(self):
                    self.restored = True

            snapshot = FakeSnapshot()
            extracted_context = {
                "candidate_parameters": [],
                "candidate_functions": [],
                "parameters": [],
                "functions": [],
                "snippets": [{"path": "auth.php", "code": "guard();"}],
                "summary": {
                    "candidate_parameters": 0,
                    "candidate_functions": 0,
                    "parameters": 0,
                    "functions": 0,
                    "snippets": 1,
                },
                "cst": [],
            }
            seen = {}

            def fake_repairs(ignored_config, ignored_graph, ignored_findings, **kwargs):
                seen["snippets"] = kwargs["source_context"]["snippets"]
                return []

            with patch("drhl.pipeline.validate_config"), patch(
                "drhl.pipeline.create_snapshot", return_value=snapshot
            ), patch(
                "drhl.pipeline.analyze_access_control_source", return_value=extracted_context
            ) as analyze, patch(
                "drhl.pipeline.create_repairs", side_effect=fake_repairs
            ):
                result = run_repair_stage(config)

            analyze.assert_called_once()
            self.assertEqual(seen["snippets"], [{"path": "auth.php", "code": "guard();"}])
            self.assertTrue(snapshot.restored)
            self.assertTrue((run_dir / "source" / "snippets.json").is_file())
            self.assertTrue((run_dir / "source" / "llm_snippets.json").is_file())
            self.assertEqual(result["updated_metrics"]["hsng_construction_seconds"], 7.0)
            self.assertEqual(result["updated_metrics"]["detection_seconds"], 3.0)
            self.assertLess(result["updated_metrics"]["access_control_snippets_extraction_seconds"], 99.0)
            self.assertGreaterEqual(result["updated_metrics"]["total_seconds"], 13.0)
            self.assertLess(result["updated_metrics"]["total_seconds"], 14.0)

    def test_artifacts_run_from_role_crawls_to_attack_vectors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "index.php").write_text("<?php include 'auth.php';", encoding="utf-8")
            (source / "auth.php").write_text("<?php", encoding="utf-8")
            (source / "admin.php").write_text("<?php require 'auth.php';", encoding="utf-8")
            (source / "hidden.php").write_text("<?php", encoding="utf-8")

            artifact_dir = root / "artifacts"
            write_json(
                artifact_dir / "admin.json",
                RoleCrawl(
                    "admin", "admin", ["index.php", "admin.php", "profile.php?id=p1"], [],
                    {"profile.php?id=p1": RequestSpec("GET", {"id": "1"})},
                ).to_dict(),
            )
            write_json(
                artifact_dir / "user1.json",
                RoleCrawl(
                    "user1", "user", ["index.php", "profile.php?id=p1"], [],
                    {"profile.php?id=p1": RequestSpec("GET", {"id": "1"})},
                ).to_dict(),
            )
            write_json(
                artifact_dir / "visitor.json",
                RoleCrawl("visitor", "visitor", ["index.php"], [], {}).to_dict(),
            )
            config = {
                "run_dir": "run",
                "target": {
                    "base_url": "http://localhost/app/",
                    "source_root": "source",
                    "language": "php"
                },
                "database": {"driver": "none"},
                "crawl": {
                    "mode": "artifacts",
                    "roles": [
                        {"name": "admin", "kind": "admin", "artifact": "artifacts/admin.json"},
                        {"name": "user1", "kind": "user", "artifact": "artifacts/user1.json"},
                        {"name": "visitor", "kind": "visitor", "artifact": "artifacts/visitor.json"}
                    ]
                },
                "analysis": {"active_detection": False, "identity_parameters": ["id"]},
                "repair": {"enabled": False}
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            manifest = run_pipeline(load_config(config_path))
            self.assertEqual(manifest["status"], "completed")
            vectors = json.loads(
                Path(manifest["artifacts"]["attack_vectors"]).read_text(encoding="utf-8")
            )["vectors"]
            categories = {(item["category"], item["page"]) for item in vectors}
            self.assertIn(("admin_only", "admin.php"), categories)
            self.assertIn(("horizontal", "profile.php?id=p1"), categories)
            self.assertIn(("static_only", "hidden.php"), categories)
            self.assertTrue(Path(manifest["artifacts"]["access_control_parameters"]).is_file())
            self.assertTrue(Path(manifest["artifacts"]["access_control_snippets"]).is_file())
            self.assertTrue(Path(manifest["artifacts"]["metrics_json"]).is_file())
            self.assertTrue(Path(manifest["artifacts"]["metrics_csv"]).is_file())
            metrics = json.loads(Path(manifest["artifacts"]["metrics_json"]).read_text(encoding="utf-8"))
            self.assertIn("HSNG Construction Time(s)", metrics["columns"])


if __name__ == "__main__":
    unittest.main()
