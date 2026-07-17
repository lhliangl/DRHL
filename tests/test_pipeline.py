from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from drhl.config import load_config
from drhl.io import write_json
from drhl.models import RequestSpec, RoleCrawl
from drhl.pipeline import run_pipeline


class OfflinePipelineTests(unittest.TestCase):
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
