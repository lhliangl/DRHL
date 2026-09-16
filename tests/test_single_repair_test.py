from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.config import PipelineConfig, RoleConfig, TargetConfig
from drhl.io import write_json
from drhl.pipeline import run_single_repair_test
from drhl.repair.patcher import RepairResult


class _FakeSnapshot:
    def __init__(self, path: Path):
        self.path = path
        self.restore_calls = 0

    def restore(self) -> None:
        self.restore_calls += 1


class SingleRepairTestTests(unittest.TestCase):
    def test_runs_only_selected_finding_and_leaves_formal_artifacts_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "runs" / "phpns"
            source_root = root / "web"
            source_root.mkdir(parents=True)
            source = source_root / "user.php"
            source.write_text("<?php echo 'original';", encoding="utf-8")
            baseline = run_dir / "database" / "baseline.sql"
            baseline.parent.mkdir(parents=True)
            baseline.write_text("baseline", encoding="utf-8")
            write_json(
                run_dir / "graphs" / "fused.json",
                {"source_map": {"user.php": "user.php"}},
            )
            write_json(
                run_dir / "analysis" / "findings.json",
                {
                    "findings": [
                        {
                            "category": "horizontal",
                            "page": "user.php?do=edit&id=p1",
                            "actor": "user1",
                            "status": "vulnerable",
                            "confidence": "high",
                            "method": "GET",
                            "http_status": 200,
                        },
                        {
                            "category": "horizontal",
                            "page": "article.php?id=p1",
                            "actor": "user1",
                            "status": "vulnerable",
                            "confidence": "high",
                            "method": "GET",
                            "http_status": 200,
                        },
                    ]
                },
            )
            write_json(
                run_dir / "analysis" / "vectors.json",
                {
                    "vectors": [
                        {
                            "category": "horizontal",
                            "page": "user.php?do=edit&id=p1",
                            "authorized_roles": ["user2"],
                            "request": {"method": "GET", "params": {}},
                        },
                        {
                            "category": "horizontal",
                            "page": "article.php?id=p1",
                            "authorized_roles": ["user2"],
                            "request": {"method": "GET", "params": {}},
                        },
                    ]
                },
            )
            write_json(
                run_dir / "source" / "snippets.json",
                {"snippets": [{"path": "user.php", "code": "guard();"}]},
            )
            config = PipelineConfig(
                path=root / "phpns.json",
                run_dir=run_dir,
                target=TargetConfig(
                    base_url="http://127.0.0.1/phpns",
                    source_root=source_root,
                    language="php",
                    public_extensions=(".php",),
                ),
                database={"driver": "mysql", "database": "phpns", "user": "root"},
                crawl={"mode": "selenium"},
                roles=(RoleConfig(name="user1", kind="user"),),
                analysis={},
                repair={},
            )
            snapshot = _FakeSnapshot(baseline)
            seen: dict[str, object] = {}

            def fake_create_repairs(temp_config, graph, findings, **kwargs):
                seen["run_dir"] = temp_config.run_dir
                seen["findings"] = [(item.category, item.page) for item in findings]
                temp_output = temp_config.run_dir / "repair" / "files" / "user.php"
                temp_output.parent.mkdir(parents=True)
                temp_output.write_text("patched", encoding="utf-8")
                source.write_text("temporarily patched", encoding="utf-8")
                return [
                    RepairResult(
                        category="horizontal",
                        page="user.php?do=edit&id=p1",
                        source=str(source),
                        output=str(temp_output),
                        status="successful_repair",
                        message="passed",
                        successful=True,
                    )
                ]

            with patch("drhl.pipeline.create_snapshot", return_value=snapshot), patch(
                "drhl.pipeline.create_repairs", side_effect=fake_create_repairs
            ):
                result = run_single_repair_test(
                    config, "horizontal", "user.php?do=edit&id=p1"
                )

            self.assertEqual(
                seen["findings"], [("horizontal", "user.php?do=edit&id=p1")]
            )
            self.assertNotEqual(seen["run_dir"], run_dir)
            self.assertFalse(Path(seen["run_dir"]).exists())
            self.assertEqual(source.read_text(encoding="utf-8"), "<?php echo 'original';")
            self.assertEqual(snapshot.restore_calls, 1)
            self.assertFalse((run_dir / "repair").exists())
            self.assertFalse((run_dir / "metrics").exists())
            self.assertFalse((run_dir / "source" / "llm_snippets.json").exists())
            self.assertEqual(result["repair_summary"]["Repair Items"], 1)
            self.assertEqual(
                result["cleanup"],
                {
                    "source_restored": True,
                    "database_restored": True,
                    "temporary_artifacts_removed": True,
                    "formal_run_artifacts_modified": False,
                },
            )

            interrupted: dict[str, Path] = {}

            def interrupting_create_repairs(temp_config, graph, findings, **kwargs):
                interrupted["run_dir"] = temp_config.run_dir
                source.write_text("interrupted patch", encoding="utf-8")
                raise KeyboardInterrupt

            with patch("drhl.pipeline.create_snapshot", return_value=snapshot), patch(
                "drhl.pipeline.create_repairs", side_effect=interrupting_create_repairs
            ):
                with self.assertRaises(KeyboardInterrupt):
                    run_single_repair_test(
                        config, "horizontal", "user.php?do=edit&id=p1"
                    )

            self.assertEqual(source.read_text(encoding="utf-8"), "<?php echo 'original';")
            self.assertEqual(snapshot.restore_calls, 2)
            self.assertFalse(interrupted["run_dir"].exists())


if __name__ == "__main__":
    unittest.main()
