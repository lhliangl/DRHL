from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.config import PipelineConfig, TargetConfig
from drhl.crawling.selenium import SeleniumRoleCrawler


class CrawlArtifactSecurityTests(unittest.TestCase):
    def test_default_secret_parameter_names_cover_credentials_and_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={}, crawl={}, roles=(), analysis={}, repair={},
            )
            names = SeleniumRoleCrawler(config)._secret_names()
            self.assertTrue({"password", "token", "csrf", "_token"}.issubset(names))
            self.assertFalse(SeleniumRoleCrawler(config)._should_record_parameter("password"))

    def test_secret_parameter_redaction_can_be_disabled_per_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={}, crawl={"redact_secret_parameters": False}, roles=(), analysis={}, repair={},
            )
            crawler = SeleniumRoleCrawler(config)
            self.assertTrue(crawler._should_record_parameter("password"))

    def test_synthetic_form_values_are_generated_by_field_name_and_type(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={}, crawl={"redact_secret_parameters": False}, roles=(), analysis={}, repair={},
            )
            crawler = SeleniumRoleCrawler(config)
            page = "showpaper.php?paper_id=p1"
            self.assertTrue(crawler._synthetic_form_value("comment", "textarea", "", page).startswith("comment_"))
            self.assertTrue(crawler._synthetic_form_value("email2", "email", "", page).endswith("@example.test"))
            self.assertEqual(crawler._synthetic_form_value("password", "password", "", page), "12345678")
            self.assertEqual(crawler._synthetic_form_value("paper_id", "number", "", page), "1")


if __name__ == "__main__":
    unittest.main()