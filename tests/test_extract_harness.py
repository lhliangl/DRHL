from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_extract.evaluate import (
    _match_entities,
    _unique_ground_truth,
    _unique_predicted_parameters,
)
from test_extract.extract import assert_three_stage_consistency, run_extract


class ExtractHarnessTests(unittest.TestCase):
    def test_php_array_keys_are_not_standalone_matching_variants(self) -> None:
        expected = _unique_ground_truth(
            [
                {
                    "name": "$mybb->admin['permissions'][$action['module']][$action['action']]"
                }
            ]
        )
        predicted = _unique_predicted_parameters(
            [
                {
                    "expression": "$mybb->input['action']",
                    "aliases": ["$mybb->input['action']"],
                    "path": "global.php",
                }
            ]
        )

        result = _match_entities(expected, predicted)

        self.assertEqual(result["tp"], 0)
        self.assertEqual(result["fp"], 1)
        self.assertEqual(result["fn"], 1)

    def test_three_stage_assertion_rejects_uncovered_validated_element(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            source = output / "source"
            source.mkdir()
            (source / "parameters.json").write_text(
                '{"parameters": [{"id": "P1"}]}', encoding="utf-8"
            )
            (source / "functions.json").write_text(
                '{"functions": []}', encoding="utf-8"
            )
            (source / "snippets.json").write_text(
                '{"snippets": []}', encoding="utf-8"
            )
            (source / "llm_snippets.json").write_text(
                '{"snippets": []}', encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "validated parameters without snippets"):
                assert_three_stage_consistency(output)

    def test_three_stage_assertion_rejects_llm_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "parameters.json").write_text(
                '{"parameters": [{"id": "P1"}]}', encoding="utf-8"
            )
            (source / "functions.json").write_text(
                '{"functions": []}', encoding="utf-8"
            )
            (source / "snippets.json").write_text(
                json.dumps(
                    {
                        "snippets": [
                            {
                                "path": "auth.php",
                                "code": "guard();",
                                "parameter_ids": ["P1"],
                                "function_ids": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (source / "llm_snippets.json").write_text(
                json.dumps(
                    {
                        "snippets": [
                            {
                                "path": "auth.php",
                                "code": "guard();",
                                "parameter_ids": ["P1"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "is not minimal"):
                assert_three_stage_consistency(Path(tmp))

    def test_uses_isolated_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "source"
            source_root.mkdir()
            formal_run = root / "formal-runs" / "demo"
            schema = formal_run / "database" / "baseline.sql"
            schema.parent.mkdir(parents=True)
            schema.write_text("CREATE TABLE users (id INT);", encoding="utf-8")
            config_path = root / "demo.json"
            config_path.write_text(
                json.dumps(
                    {
                        "run_dir": str(formal_run),
                        "target": {
                            "base_url": "http://localhost/",
                            "source_root": str(source_root),
                            "language": "php",
                            "public_extensions": [".php"],
                        },
                        "database": {"driver": "mysql"},
                        "crawl": {
                            "mode": "selenium",
                            "roles": [{"name": "visitor", "kind": "visitor"}],
                        },
                        "analysis": {"active_detection": True},
                    }
                ),
                encoding="utf-8",
            )

            captured_run_dirs: list[Path] = []

            def fake_analyze(config, _save_cst):
                captured_run_dirs.append(config.run_dir)
                source_dir = config.run_dir / "source"
                source_dir.mkdir(parents=True, exist_ok=True)
                artifact = source_dir / "snippets.json"
                artifact.write_text('{"snippets": []}', encoding="utf-8")
                (source_dir / "parameters.json").write_text(
                    '{"parameters": []}', encoding="utf-8"
                )
                (source_dir / "functions.json").write_text(
                    '{"functions": []}', encoding="utf-8"
                )
                (source_dir / "llm_snippets.json").write_text(
                    '{"snippets": []}', encoding="utf-8"
                )
                return {
                    "summary": {"snippets": 0},
                    "parser": "test",
                    "parse_errors": [],
                    "artifacts": {"snippets": str(artifact)},
                }

            with patch("test_extract.extract.TEST_ROOT", root / "test_extract"), patch(
                "test_extract.extract._analyze_source", side_effect=fake_analyze
            ):
                summary = run_extract(config_path)

            expected = (root / "test_extract" / "runs" / "demo").resolve()
            self.assertEqual(captured_run_dirs, [expected])
            self.assertEqual(Path(summary["output_dir"]), expected)
            self.assertTrue((expected / "database" / "baseline.sql").is_file())
            self.assertTrue((expected / "summary.json").is_file())
            self.assertEqual(schema.read_text(encoding="utf-8"), "CREATE TABLE users (id INT);")
            self.assertFalse((formal_run / "source").exists())


if __name__ == "__main__":
    unittest.main()
