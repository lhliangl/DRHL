from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.config import PipelineConfig, RoleConfig, TargetConfig
from drhl.crawling.runner import crawl_all_roles
from drhl.models import RoleCrawl


def config(root: Path) -> PipelineConfig:
    return PipelineConfig(
        path=root / "config.json",
        run_dir=root / "run",
        target=TargetConfig("http://example.test/", root, "php", (".php",)),
        database={},
        crawl={},
        roles=(RoleConfig("admin", "admin"), RoleConfig("user1", "user")),
        analysis={},
        repair={},
    )


class CrawlIsolationTests(unittest.TestCase):
    def test_browser_closes_and_database_restores_after_each_role(self):
        events = []

        class Snapshot:
            def create(self):
                events.append("snapshot")

            def restore(self):
                events.append("restore")

        class Crawler:
            def __init__(self, _config):
                self.role = None

            def crawl(self, role):
                self.role = role.name
                events.append(f"crawl:{role.name}")
                return RoleCrawl(role.name, role.kind)

            def close(self):
                events.append(f"close:{self.role}")

        with tempfile.TemporaryDirectory() as directory:
            crawl_all_roles(config(Path(directory)), Snapshot(), Crawler)
        self.assertEqual(
            events,
            ["snapshot", "crawl:admin", "close:admin", "restore", "crawl:user1", "close:user1", "restore"],
        )

    def test_failed_crawl_is_restored_before_error_is_raised(self):
        events = []

        class Snapshot:
            def create(self):
                events.append("snapshot")

            def restore(self):
                events.append("restore")

        class Crawler:
            def __init__(self, _config):
                pass

            def crawl(self, role):
                events.append("crawl")
                raise RuntimeError("failed")

            def close(self):
                events.append("close")

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(Exception):
                crawl_all_roles(config(Path(directory)), Snapshot(), Crawler)
        self.assertEqual(events, ["snapshot", "crawl", "close", "restore"])

    def test_configured_form_restore_callback_uses_shared_snapshot(self):
        events = []

        class Snapshot:
            def create(self):
                events.append("snapshot")

            def restore(self):
                events.append("restore")

        class Crawler:
            def __init__(self, _config):
                self.restore = None

            def set_database_restore_callback(self, callback):
                self.restore = callback

            def crawl(self, role):
                events.append(f"crawl:{role.name}")
                assert self.restore is not None
                self.restore()
                return RoleCrawl(role.name, role.kind)

            def close(self):
                events.append("close")

        with tempfile.TemporaryDirectory() as directory:
            test_config = config(Path(directory))
            test_config.crawl["restore_database_after_form_markers"] = ["delete"]
            crawl_all_roles(test_config, Snapshot(), Crawler)
        self.assertEqual(
            events,
            [
                "snapshot",
                "crawl:admin",
                "restore",
                "close",
                "restore",
                "crawl:user1",
                "restore",
                "close",
                "restore",
            ],
        )


if __name__ == "__main__":
    unittest.main()
