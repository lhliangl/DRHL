from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.analysis.vectors import generate_vectors
from drhl.config import TargetConfig
from drhl.crawling.urls import canonical_page
from drhl.graphs.dynamic import build_dynamic_graph
from drhl.graphs.fusion import fuse_graphs
from drhl.graphs.static import build_static_graph
from drhl.models import RequestSpec, RoleCrawl


class URLTests(unittest.TestCase):
    def test_query_values_are_normalized_but_control_parameters_are_preserved(self):
        page = canonical_page(
            "http://localhost/app/user.php?id=17&action=edit",
            "http://localhost/app/",
            ["action"],
        )
        self.assertEqual(page, "user.php?action=edit&id=p1")


class GraphTests(unittest.TestCase):
    def test_static_dynamic_fusion_and_vector_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.php").write_text("<?php include 'auth.php';", encoding="utf-8")
            (root / "auth.php").write_text("<?php", encoding="utf-8")
            (root / "admin.php").write_text("<?php require 'auth.php';", encoding="utf-8")
            (root / "hidden.php").write_text("<?php", encoding="utf-8")
            (root / "header.php").write_text("<?php", encoding="utf-8")
            (root / "functions.php").write_text("<?php", encoding="utf-8")
            (root / "config.php").write_text("<?php", encoding="utf-8")
            admin_dir = root / "admin"
            admin_dir.mkdir()
            (admin_dir / "nav.php").write_text("<?php", encoding="utf-8")
            (admin_dir / "form.php").write_text("<?php", encoding="utf-8")
            crawls = [
                RoleCrawl(
                    "admin",
                    "admin",
                    ["index.php", "admin.php", "profile.php?id=p1", "admin/nav.php", "admin/form.php"],
                    [],
                    {"profile.php?id=p1": RequestSpec("GET", {"id": "1"})},
                ),
                RoleCrawl(
                    "user1",
                    "user",
                    ["index.php", "profile.php?id=p1"],
                    [],
                    {"profile.php?id=p1": RequestSpec("GET", {"id": "1"})},
                ),
                RoleCrawl("visitor", "visitor", ["index.php"], [], {}),
            ]
            dynamic = build_dynamic_graph(crawls)
            static = build_static_graph(
                TargetConfig("http://localhost/app/", root, "php", (".php",)), dynamic["nodes"]
            )
            fused = fuse_graphs(dynamic, static)
            vectors = generate_vectors(fused, ["id"])
            categories = {(vector.category, vector.page) for vector in vectors}
            self.assertIn(("admin_only", "admin.php"), categories)
            self.assertIn(("authenticated_only", "profile.php?id=p1"), categories)
            self.assertIn(("horizontal", "profile.php?id=p1"), categories)
            self.assertIn(("static_only", "hidden.php"), categories)
            self.assertIn("admin/nav.php", fused["nodes"])
            self.assertIn("admin/form.php", fused["nodes"])
            self.assertNotIn(("static_only", "header.php"), categories)
            self.assertNotIn(("static_only", "functions.php"), categories)
            self.assertNotIn(("static_only", "config.php"), categories)
            self.assertNotIn(("admin_only", "admin/nav.php"), categories)
            self.assertNotIn(("admin_only", "admin/form.php"), categories)


if __name__ == "__main__":
    unittest.main()
