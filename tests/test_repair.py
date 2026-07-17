from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.config import PipelineConfig, TargetConfig
from drhl.models import AttackVector, Finding, RequestSpec
from drhl.repair.patcher import _chat_completion, create_repairs, serialize_repairs, write_repair_report


class RepairTests(unittest.TestCase):
    def test_repair_without_llm_key_is_manual(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "source"
            source_root.mkdir()
            source = source_root / "admin.php"
            original = "<?php\necho 'admin';\n"
            source.write_text(original, encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", source_root, "php", (".php",)),
                database={}, crawl={}, roles=(), analysis={},
                repair={"llm": {"enabled": True, "api_key": ""}},
            )
            finding = Finding("admin_only", "admin.php", "visitor", "vulnerable", "high", "GET", 200)
            results = create_repairs(config, {"source_map": {"admin.php": "admin.php"}}, [finding])
            self.assertEqual(results[0].status, "manual")
            self.assertEqual(results[0].engine, "llm")
            self.assertIsNone(results[0].output)
            self.assertEqual(results[0].patches_generated, 0)
            self.assertFalse(results[0].successful)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_llm_repair_retries_until_validation_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "source"
            source_root.mkdir()
            source = source_root / "admin.php"
            original = "<?php\nrequire_once 'functions.php';\necho 'admin';\n"
            source.write_text(original, encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", source_root, "php", (".php",)),
                database={}, crawl={}, roles=(), analysis={},
                repair={
                    "validation": {"max_attempts": 3, "temporary_apply_to_source": True},
                    "llm": {
                        "enabled": True,
                        "base_url": "https://api.deepseek.com/v1",
                        "model": "deepseek-v4-flash",
                        "api_key": "test-key",
                    },
                },
            )
            finding = Finding("admin_only", "admin.php", "visitor", "vulnerable", "high", "GET", 200)
            vector = AttackVector("admin_only", "admin.php", ["admin"], RequestSpec("GET"))
            source_context = {
                "snippets": [
                    {
                        "path": "functions.php",
                        "kind": "validation_function",
                        "function": "require_admin",
                        "code": "function require_admin() { if (!is_admin()) { exit; } }",
                    },
                    {
                        "path": "admin.php",
                        "kind": "guard_call",
                        "function": "require_admin",
                        "code": "require_admin();",
                    },
                ]
            }
            responses = [
                '{"missing_check":"The page is missing an administrator authorization check.","insertion_location":"Insert the guard after require_once statements and before business logic.","recommended_guard":"require_admin();","reason":"The project already defines and uses require_admin as an administrator guard."}',
                '{"patched_source":"<?php\\nrequire_once \'functions.php\';\\necho \'admin\';\\n","explanation":"No effective change."}',
                '{"missing_check":"The previous patch did not block the exploit; add the existing admin guard.","insertion_location":"After require_once statements.","recommended_guard":"require_admin();","reason":"The first attempt failed exploit validation."}',
                '{"patched_source":"<?php\\nrequire_once \'functions.php\';\\nrequire_admin();\\necho \'admin\';\\n","explanation":"Added the existing administrator guard before the protected logic."}',
            ]

            with patch("drhl.repair.patcher._chat_completion", side_effect=responses) as chat, \
                 patch("drhl.repair.patcher._syntax_check", return_value=(True, "ok")), \
                 patch("drhl.repair.patcher._runtime_validation", side_effect=[(False, True, "still vulnerable"), (True, True, "blocked")]):
                results = create_repairs(
                    config,
                    {"source_map": {"admin.php": "admin.php"}},
                    [finding],
                    source_context=source_context,
                    vectors=[vector],
                    snapshot=object(),
                )

            self.assertEqual(chat.call_count, 4)
            self.assertEqual(results[0].status, "successful_repair")
            self.assertEqual(results[0].attempts, 2)
            self.assertEqual(results[0].patches_generated, 2)
            self.assertEqual(results[0].syntax_compile_ok, 2)
            self.assertEqual(results[0].exploit_blocked, 1)
            self.assertEqual(results[0].regression_passed, 2)
            self.assertTrue(results[0].successful)
            self.assertTrue(Path(results[0].prompt_artifact).is_file())
            self.assertIn("require_admin();", Path(results[0].output).read_text(encoding="utf-8"))
            self.assertEqual(source.read_text(encoding="utf-8"), original)

            manifest = serialize_repairs(results)
            self.assertEqual(manifest["summary"]["Patches Generated"], 2)
            self.assertEqual(manifest["summary"]["Successful Repairs"], 1)
            report_path = root / "run" / "repair" / "repair_report.md"
            write_repair_report(results, report_path)
            self.assertIn("Successful Repairs: 1", report_path.read_text(encoding="utf-8"))

    def test_chat_completion_accumulates_usage_metrics_and_cost(self):
        class FakeResponse:
            status_code = 200
            text = "ok"

            def json(self):
                return {
                    "choices": [{"message": {"content": "{\"ok\": true}"}}],
                    "usage": {
                        "prompt_tokens": 1000,
                        "completion_tokens": 250,
                        "total_tokens": 1250,
                    },
                }

        metrics = {}
        llm = {
            "api_key": "test-key",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-v4-flash",
            "input_cost_per_million_tokens": 0.1,
            "output_cost_per_million_tokens": 0.2,
        }
        with patch("drhl.repair.patcher.requests.post", return_value=FakeResponse()):
            content = _chat_completion(llm, [{"role": "user", "content": "hello"}], metrics)

        self.assertEqual(content, '{"ok": true}')
        self.assertEqual(metrics["tokens_in"], 1000)
        self.assertEqual(metrics["tokens_out"], 250)
        self.assertEqual(metrics["tokens_total"], 1250)
        self.assertEqual(metrics["llm_requests"], 1)
        self.assertTrue(metrics["api_cost_pricing_configured"])
        self.assertAlmostEqual(metrics["api_cost_usd"], 0.00015)


if __name__ == "__main__":
    unittest.main()