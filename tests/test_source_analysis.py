from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path
from types import SimpleNamespace

from drhl.cli import _analyze_source
from drhl.config import TargetConfig
from drhl.source_analysis import analyze_access_control_source


class SourceAnalysisTests(unittest.TestCase):
    def test_cli_forwards_application_termination_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source"
            source.mkdir()
            (source / "guard.php").write_text(
                "<?php if ($gate) { application_denied(); }\n"
                "if ($business) { application_denied(); }",
                encoding="utf-8",
            )
            run_dir = base / "run"
            config = SimpleNamespace(
                target=TargetConfig("http://localhost/", source, "php", (".php",)),
                run_dir=run_dir,
                crawl={},
                analysis={
                    "source_analysis": {
                        "termination_patterns": [r"application_denied\s*\("],
                        "termination_exclude_patterns": [r"\$business"],
                    }
                },
            )

            _analyze_source(config)

            result = json.loads(
                (run_dir / "source" / "parameters.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {item["expression"] for item in result["parameters"]},
                {"$gate"},
            )

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
                termination_patterns=[
                    r"\$_SESSION\['privilege'\].*return\s+FALSE",
                ],
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
            self.assertTrue(any(
                "$_GET['user_id']" in item["aliases"]
                for item in result["candidate_parameters"]
            ))

            snippets = result["snippets"]
            self.assertTrue(any(
                item["kind"] == "validation_function"
                and item.get("function") == "require_admin"
                for item in snippets
            ))
            guard_calls = [item for item in snippets if item["kind"] == "guard_call"]
            self.assertEqual(
                {item["function"] for item in guard_calls},
                {"is_admin", "require_admin"},
            )
            self.assertTrue(all(item["function_ids"] for item in guard_calls))
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
                "\n".join(privilege["if_framework"].splitlines()),
                "if ($_SESSION['privilege'] != 'admin') {\n    return FALSE;\n}",
            )
            self.assertTrue(privilege["parameter_ids"])
            self.assertTrue(all(
                "if_framework" not in item
                for item in snippets
                if item["kind"] in {"validation_function", "guard_call"}
            ))

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

    def test_php_alias_tracking_keeps_single_source_transformations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guard.php").write_text(
                """<?php
$decoded = $_COOKIE['member_id'] - 197;
$sql = "SELECT * FROM users WHERE user_id=$decoded";
if ($decoded < 1) { http_response_code(403); exit; }
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(
                target,
                access_control_database_fields=["users.user_id"],
            )
            aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
            self.assertIn("$_COOKIE['member_id']", aliases)

    def test_php_config_can_exclude_business_termination_conditions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "upload.php").write_text(
                """<?php
function file_check($file_extension, $file_extensions) {
    if (in_array($file_extension, $file_extensions)) {
        return 'File extension is not allowed';
    }
}
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(
                target,
                termination_exclude_patterns=[
                    r"in_array\s*\(\s*\$file_extension\s*,\s*\$file_extensions\s*\)",
                ],
            )
            self.assertTrue(result["candidate_parameters"])
            self.assertEqual(result["parameters"], [])
            self.assertEqual(result["functions"], [])

    def test_php_termination_exclusion_survives_state_propagation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reset.php").write_text(
                """<?php
$db_reset = false;
if ($ready) { $db_reset = true; }
if ($db_reset == true) {
    header('Location: login.php');
    exit;
}
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(
                target,
                termination_exclude_patterns=[r"\$db_reset\s*==\s*true"],
            )
            self.assertIn(
                "$db_reset",
                {item["expression"] for item in result["candidate_parameters"]},
            )
            self.assertNotIn(
                "$db_reset",
                {item["expression"] for item in result["parameters"]},
            )

    def test_php_session_role_inherits_database_field_across_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "login.php").write_text(
                """<?php
$sql = "SELECT * FROM users WHERE login='alice'";
$result = $db->query($sql);
$row = $result->fetch_object();
$_SESSION['admin'] = $row->admin;
""",
                encoding="utf-8",
            )
            (root / "admin.php").write_text(
                "<?php if ($_SESSION['admin'] != 1) { $message = 'insufficient privilege'; }",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(
                target,
                access_control_database_fields=["users.admin"],
            )
            admin = next(
                item
                for item in result["parameters"]
                if "$_SESSION['admin']" in item["aliases"]
            )
            self.assertTrue(
                any(
                    evidence.get("kind") == "database_field"
                    and evidence.get("table") == "users"
                    and evidence.get("field") == "admin"
                    for evidence in admin["validation_evidence"]
                )
            )

    def test_php_session_derived_boolean_return_becomes_condition_parameter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guard.php").write_text(
                """<?php
function &session_grab() {
    return $_SESSION['app'];
}
function appIsLoggedIn() {
    $session =& session_grab();
    return isset($session['username']);
}
function current_user() {
    $session =& session_grab();
    return $session['username'];
}
function page_startup() {
    if (!appIsLoggedIn()) {
        header('Location: login.php');
        exit;
    }
}
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(target)
            self.assertIn(
                "appisloggedin",
                {item["expression"].casefold() for item in result["parameters"]},
            )
            self.assertNotIn(
                "current_user",
                {item["expression"].casefold() for item in result["candidate_parameters"]},
            )
            self.assertIn(
                "page_startup",
                {item["name"] for item in result["functions"]},
            )

    def test_php_session_identity_keys_are_semantic_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "session.php").write_text(
                """<?php
$_SESSION['username'] = $row['name'];
$_SESSION[userID] = $row['id'];
$_SESSION['user_id'] = $row['id'];
$_SESSION['display_name'] = $row['display_name'];
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(target)
            expressions = {item["expression"].casefold() for item in result["parameters"]}
            self.assertIn("$_session['username']", expressions)
            self.assertIn("$_session['userid']", expressions)
            aliases = {
                alias.casefold()
                for item in result["parameters"]
                for alias in item["aliases"]
            }
            self.assertIn("$_session[userid]", aliases)
            self.assertIn("$_session['user_id']", aliases)
            self.assertNotIn("$_session['display_name']", aliases)
            semantic_snippets = [
                item for item in result["snippets"] if item["kind"] == "semantic_source"
            ]
            self.assertEqual(len(semantic_snippets), 3)
            self.assertTrue(all(item["parameter_ids"] for item in semantic_snippets))


if __name__ == "__main__":
    unittest.main()

