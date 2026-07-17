from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.config import TargetConfig
from drhl.source_analysis import analyze_access_control_source


class SourceAnalysisTests(unittest.TestCase):
    def test_php_candidates_are_validated_before_snippet_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "functions.php").write_text(
                """<?php
function query($sql) {
    $result = mysql_query($sql);
    if (!$result) die(mysql_error());
    return $result;
}
function is_admin() {
    if ($_SESSION['privilege'] != 'admin') {
        return FALSE;
    }
    return TRUE;
}
function require_admin() {
    if (!is_admin()) {
        header('Location: login.php');
        exit;
    }
}
""",
                encoding="utf-8",
            )
            (root / "admin.php").write_text(
                "<?php\nrequire_once 'functions.php';\nrequire_admin();\n",
                encoding="utf-8",
            )
            (root / "owner.php").write_text(
                """<?php
+$owner = $_GET['user_id'];
+if ($owner !== getUserID()) {
+    http_response_code(403);
+    exit;
+}
+""".replace("+", ""),
                encoding="utf-8",
            )
            schema = root / "schema.sql"
            schema.write_text(
                """CREATE TABLE `users` (
`user_id` int NOT NULL,
`privilege` enum('admin','user') NOT NULL
) ENGINE=InnoDB;
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))

            result = analyze_access_control_source(
                target,
                identity_parameters=["user_id"],
                database_schema=schema,
                include_cst=True,
            )

            self.assertEqual(result["summary"]["cst_files"], 3)
            admin_cst = next(item for item in result["cst"] if item["path"] == "admin.php")
            self.assertEqual(admin_cst["root"]["type"], "program")
            self.assertFalse(admin_cst["has_error"])
            candidate_names = {item["name"] for item in result["candidate_functions"]}
            self.assertEqual(candidate_names, {"query", "is_admin", "require_admin"})
            validated_names = {item["name"] for item in result["functions"]}
            self.assertEqual(validated_names, {"is_admin", "require_admin"})

            parameters = {item["expression"]: item for item in result["parameters"]}
            self.assertIn("$_SESSION['privilege']", parameters)
            self.assertIn("terminating_condition", {
                evidence["kind"] for evidence in parameters["$_SESSION['privilege']"]["validation_evidence"]
            })
            self.assertFalse(any(
                "$_GET['user_id']" in item["aliases"]
                for item in result["parameters"]
            ))

            snippets = result["snippets"]
            self.assertTrue(any(
                item["kind"] == "guard_call" and item["path"] == "admin.php"
                and item["code"] == "require_admin();"
                for item in snippets
            ))
            self.assertFalse(any(item["kind"] == "parameter_context" for item in snippets))
            self.assertTrue(all("function" in item or "condition" in item for item in snippets))
            self.assertFalse(any(
                item["kind"] == "validation_function" and item.get("function") == "query"
                for item in snippets
            ))
            privilege = next(
                item for item in snippets
                if item["kind"] == "conditional" and "$_SESSION['privilege']" in item["condition"]
            )
            self.assertEqual(
                "\n".join(privilege["code"].splitlines()),
                "if ($_SESSION['privilege'] != 'admin') {\n    return FALSE;\n}",
            )

    def test_comments_and_strings_do_not_create_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plain.php").write_text(
                "<?php // require_admin();\nprint 'if ($role) { access denied }';",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))

            result = analyze_access_control_source(target)

            self.assertEqual(result["summary"], {
                "cst_files": 1,
                "candidate_parameters": 0,
                "candidate_functions": 0,
                "parameters": 0,
                "functions": 0,
                "snippets": 0,
            })

    def test_configured_database_fields_limit_lcp_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "paper.php").write_text(
                "<?php\n$id = (int) $_GET['paper_id'];\n$sql = \"SELECT * FROM papers WHERE paper_id=$id\";\n",
                encoding="utf-8",
            )
            (root / "admin.php").write_text(
                "<?php\nif ($_SESSION['privilege'] != 'admin') { die('Access denied'); }\n",
                encoding="utf-8",
            )
            schema = root / "schema.sql"
            schema.write_text(
                """CREATE TABLE `papers` (
`paper_id` int NOT NULL
) ENGINE=InnoDB;
CREATE TABLE `users` (
`user_id` int NOT NULL,
`privilege` enum('admin','user') NOT NULL
) ENGINE=InnoDB;
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))

            result = analyze_access_control_source(
                target,
                identity_parameters=[],
                access_control_database_fields=["users.privilege"],
                database_schema=schema,
            )

            aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
            self.assertIn("$_SESSION['privilege']", aliases)
            self.assertNotIn("$_GET['paper_id']", aliases)
            self.assertFalse(any(
                item["kind"] == "parameter_context" and "$_GET['paper_id']" in item.get("variables", [])
                for item in result["snippets"]
            ))


if __name__ == "__main__":
    unittest.main()

