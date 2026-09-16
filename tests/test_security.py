from __future__ import annotations

import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.config import PipelineConfig, TargetConfig
from drhl.crawling.selenium import SeleniumRoleCrawler
from drhl.models import RoleCrawl


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

    def test_database_restore_after_form_is_opt_in_and_marker_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={},
                crawl={"restore_database_after_form_markers": ["delete"]},
                roles=(),
                analysis={},
                repair={},
            )
            crawler = SeleniumRoleCrawler(config)
            restores = []
            crawler.set_database_restore_callback(lambda: restores.append("restore"))

            self.assertEqual(
                crawler._restore_database_after_form_marker(
                    "user.php user.php?do=deleteusers user.php?do=deleteusers"
                ),
                "delete",
            )
            self.assertIsNone(
                crawler._restore_database_after_form_marker(
                    "user.php?do=edit user.php?do=editp user.php?do=editp"
                )
            )
            crawler._restore_database_after_form("delete", "user.php?do=deleteusers")
            self.assertEqual(restores, ["restore"])

    def test_delete_form_request_is_recorded_before_database_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={},
                crawl={
                    "execute_forms": True,
                    "restore_database_after_form_markers": ["delete"],
                },
                roles=(),
                analysis={},
                repair={},
            )
            crawler = SeleniumRoleCrawler(config)
            form = object()

            class Driver:
                current_url = "http://example.test/user.php"

                def get(self, url):
                    self.current_url = url

                def find_elements(self, _by, selector):
                    return [form] if selector == "form" else []

            crawler.driver = Driver()
            crawler._dismiss_alert = lambda: None
            crawler._form_target = lambda _form, _url: (
                "http://example.test/user.php?do=deleteusers",
                "user.php?do=deleteusers",
                "POST",
            )
            crawler._collect_form_params = lambda _form, _target, fill=False: {"11": "11"}
            crawler._submit_form = lambda _form: None
            crawler._network_requests = lambda _result, _referer: None
            crawler._extract_links_and_forms = lambda _result, _url, _page: ["unexpected.php"]
            restores = []
            crawler.set_database_restore_callback(lambda: restores.append("restore"))

            result = RoleCrawl("user1", "user")
            selenium_module = types.ModuleType("selenium")
            webdriver_module = types.ModuleType("selenium.webdriver")
            common_module = types.ModuleType("selenium.webdriver.common")
            by_module = types.ModuleType("selenium.webdriver.common.by")
            by_module.By = type("By", (), {"CSS_SELECTOR": "css selector"})
            with patch.dict(
                "sys.modules",
                {
                    "selenium": selenium_module,
                    "selenium.webdriver": webdriver_module,
                    "selenium.webdriver.common": common_module,
                    "selenium.webdriver.common.by": by_module,
                },
            ):
                discovered = crawler._execute_forms_on_page(
                    result,
                    "http://example.test/user.php",
                    "user.php",
                )

            self.assertEqual(restores, ["restore"])
            self.assertEqual(result.requests["user.php?do=deleteusers"].params, {"11": "11"})
            self.assertEqual(discovered, [])


if __name__ == "__main__":
    unittest.main()
