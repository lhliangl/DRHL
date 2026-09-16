from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.config import PipelineConfig, RoleConfig, TargetConfig
from drhl.models import AttackVector, Finding, RequestSpec
from drhl.repair.patcher import (
    _authorized_regression_passed,
    _chat_completion,
    _database_validation,
    _llm_retry_feedback,
    _progress_validation_dimensions,
    _repair_source_name,
    _runtime_validation,
    _stage1_messages,
    _stage2_messages,
    _syntax_check,
    create_repairs,
    serialize_repairs,
    write_repair_report,
)


class RepairTests(unittest.TestCase):
    def test_patch_generation_prompt_requires_session_initialization_and_redirect_denial(self):
        finding = Finding(
            "admin_only", "admin.php", "visitor", "vulnerable", "high", "GET", 200,
        )
        vector = AttackVector("admin_only", "admin.php", ["admin"], RequestSpec("GET"))
        stage1 = _stage1_messages(
            finding, "admin.php", "<?php", [], vector=vector
        )[1]["content"]
        stage2 = _stage2_messages(
            finding, "admin.php", "<?php", [], {}, vector=vector
        )[1]["content"]

        self.assertNotIn("session_start()", stage1)
        self.assertNotIn("bare exit or die", stage1)
        self.assertIn("session_start()", stage2)
        self.assertIn("denial redirect", stage2)
        self.assertIn("bare exit or die", stage2)

    def test_horizontal_response_regression_uses_oracle_owner_and_attack_override(self):
        observed = {}

        class FakeSnapshot:
            def restore(self):
                observed["restored"] = True

        class FakeSession:
            def close(self):
                return None

        class FakeResponse:
            status_code = 200
            text = "owner profile"
            url = "http://example.test/member.php?id=3"

        class FakeDetector:
            def __init__(self, config, snapshot):
                return None

            def _session(self, role):
                observed["role"] = role.name
                return FakeSession()

            def _send(self, session, page, request):
                observed["page"] = page
                observed["params"] = dict(request.params)
                return FakeResponse()

            def _denial(self, response):
                return []

        config = PipelineConfig(
            path=Path("config.json"), run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "php", (".php",)),
            database={}, crawl={},
            roles=(RoleConfig("user1", "user"), RoleConfig("user2", "user")),
            analysis={"horizontal_overrides": {"id": "3"}},
            repair={"validation": {"database_oracles": [{
                "page_pattern": r"^member\.php",
                "category": "horizontal",
                "authorized": {"role": "user2"},
            }]}},
        )
        vector = AttackVector(
            "horizontal", "member.php?id=p1", ["user1", "user2"],
            RequestSpec("GET", {"id": "no"}), ["id"],
        )

        with patch("drhl.analysis.detector.ActiveDetector", FakeDetector):
            passed, _ = _authorized_regression_passed(config, FakeSnapshot(), vector)

        self.assertTrue(passed)
        self.assertEqual(observed["role"], "user2")
        self.assertEqual(observed["page"], "member.php?id=p1")
        self.assertEqual(observed["params"], {"id": "3"})
        self.assertTrue(observed["restored"])

    def test_source_map_override_precedes_graph_mapping(self):
        config = PipelineConfig(
            path=Path("config.json"),
            run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "jsp", (".jsp",)),
            database={}, crawl={}, roles=(), analysis={},
            repair={
                "source_map_overrides": [{
                    "pattern": r"^forum/index\.jsp\?(?:[^&]+&)*page=editmessage(?:&.*)?$",
                    "source": "forum/editmessage.jsp",
                }],
            },
        )

        pages = [
            "forum/index.jsp?page=editmessage&forum_id=0&thread_id=0&reply_id=2&start=0",
            "forum/index.jsp?forum_id=p1&page=editmessage&reply_id=p1&thread_id=p1",
        ]
        for page in pages:
            with self.subTest(page=page):
                source = _repair_source_name(
                    config,
                    {"forum/index.jsp": "forum/index.jsp"},
                    page,
                )
                self.assertEqual(source, "forum/editmessage.jsp")

    def test_jsp_syntax_check_is_deferred_to_runtime_without_calling_javac(self):
        config = PipelineConfig(
            path=Path("config.json"),
            run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "jsp", (".jsp",)),
            database={}, crawl={}, roles=(), analysis={},
            repair={"validation": {"syntax_check": True}},
        )

        with patch("drhl.repair.patcher._java_compile") as java_compile:
            ok, message = _syntax_check(config, Path("forum/editmessage.jsp"))

        self.assertTrue(ok)
        self.assertIn("Tomcat/Jasper runtime request", message)
        java_compile.assert_not_called()

    def test_java_syntax_check_still_calls_javac_for_jsp_projects(self):
        config = PipelineConfig(
            path=Path("config.json"),
            run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "jsp", (".jsp",)),
            database={}, crawl={}, roles=(), analysis={},
            repair={"validation": {"syntax_check": True}},
        )

        with patch("drhl.repair.patcher._java_compile", return_value=(True, "javac exited with 0")) as java_compile:
            ok, message = _syntax_check(config, Path("WEB-INF/classes/forum/AddForum.java"))

        self.assertTrue(ok)
        self.assertEqual(message, "javac exited with 0")
        java_compile.assert_called_once()

    def test_skip_findings_filters_only_the_configured_category(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "source"
            source = source_root / "users" / "sample.php"
            source.parent.mkdir(parents=True)
            source.write_text("<?php\necho 'sample';\n", encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json",
                run_dir=root / "run",
                target=TargetConfig("http://example.test/", source_root, "php", (".php",)),
                database={}, crawl={}, roles=(), analysis={},
                repair={
                    "skip_findings": [{
                        "category": "horizontal",
                        "page": "users/sample.php?userid=p1",
                        "reason": "covered by a shared include repair",
                    }],
                    "llm": {"enabled": True, "api_key": ""},
                },
            )
            findings = [
                Finding("horizontal", "users/sample.php?userid=p1", "user1", "vulnerable", "high", "GET", 200),
                Finding("authenticated_only", "users/sample.php?userid=p1", "visitor", "vulnerable", "high", "GET", 200),
            ]

            results = create_repairs(
                config,
                {"source_map": {"users/sample.php": "users/sample.php"}},
                findings,
            )

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].category, "authenticated_only")
            self.assertEqual(results[0].page, "users/sample.php?userid=p1")

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
                 patch("drhl.repair.patcher._runtime_validation", side_effect=[
                     (
                         False,
                         True,
                         False,
                         "deployment=(source patch applied); exploit=(visitor:not_vulnerable); "
                         "regression=(authorized status=200); "
                         "database_validation=(failed:GT-secret[attack:scalar_equals "
                         "expected=TOKEN1 observed=TOKEN2])",
                         {
                             "applicable": True,
                             "passed": False,
                             "combined_dimensions": {
                                 "vulnerability_blocking": {
                                     "response_oracle_passed": True,
                                     "database_oracle_applicable": True,
                                     "database_oracle_passed": False,
                                 },
                                 "regression": {
                                     "response_oracle_passed": True,
                                     "database_oracle_applicable": True,
                                     "database_oracle_passed": True,
                                 },
                             },
                         },
                     ),
                     (
                         True,
                         True,
                         True,
                         "blocked",
                         {
                             "applicable": True,
                             "passed": True,
                             "combined_dimensions": {
                                 "vulnerability_blocking": {
                                     "response_oracle_passed": True,
                                     "database_oracle_applicable": True,
                                     "database_oracle_passed": True,
                                 },
                                 "regression": {
                                     "response_oracle_passed": True,
                                     "database_oracle_applicable": True,
                                     "database_oracle_passed": True,
                                 },
                             },
                         },
                     ),
                 ]):
                results = create_repairs(
                    config,
                    {"source_map": {"admin.php": "admin.php"}},
                    [finding],
                    source_context=source_context,
                    vectors=[vector],
                    snapshot=object(),
                )

            self.assertEqual(chat.call_count, 4)
            second_attempt_messages = chat.call_args_list[2].args[1]
            second_attempt_prompt = "\n".join(message["content"] for message in second_attempt_messages)
            self.assertNotIn("database_validation", second_attempt_prompt)
            self.assertNotIn("GT-secret", second_attempt_prompt)
            self.assertNotIn("TOKEN1", second_attempt_prompt)
            self.assertNotIn("TOKEN2", second_attempt_prompt)
            self.assertIn("The vulnerability was not blocked.", second_attempt_prompt)
            self.assertNotIn("exploit=(visitor:not_vulnerable)", second_attempt_prompt)
            self.assertNotIn("regression=(authorized status=200)", second_attempt_prompt)
            self.assertEqual(results[0].status, "successful_repair")
            self.assertEqual(results[0].attempts, 2)
            self.assertEqual(results[0].patches_generated, 2)
            self.assertEqual(results[0].syntax_compile_ok, 2)
            self.assertEqual(results[0].exploit_blocked, 1)
            self.assertEqual(results[0].regression_passed, 2)
            self.assertEqual(results[0].database_validation_applied, 2)
            self.assertEqual(results[0].database_validation_passed, 1)
            self.assertTrue(results[0].successful)
            self.assertIn("database_validation=(failed:GT-secret", results[0].attempt_details[0].message)
            self.assertTrue(Path(results[0].prompt_artifact).is_file())
            self.assertIn("require_admin();", Path(results[0].output).read_text(encoding="utf-8"))
            self.assertEqual(source.read_text(encoding="utf-8"), original)

            manifest = serialize_repairs(results)
            self.assertEqual(manifest["summary"]["Patches Generated"], 2)
            self.assertEqual(manifest["summary"]["Database Validation Applied"], 2)
            self.assertEqual(manifest["summary"]["Database Validation Passed"], 1)
            self.assertEqual(manifest["summary"]["Successful Repairs"], 1)
            self.assertNotIn("Covered Vulnerable Findings", manifest["summary"])
            self.assertNotIn("coverage", manifest["repairs"][0])
            report_path = root / "run" / "repair" / "repair_report.md"
            write_repair_report(results, report_path)
            self.assertIn("Successful Repairs: 1", report_path.read_text(encoding="utf-8"))

    def test_llm_retry_feedback_returns_only_dimension_failure_reasons(self):
        message = (
            "syntax=(ok); deployment=(applied); exploit=(blocked); regression=(passed); "
            "database_validation=(failed:GT-014[attack:scalar_equals "
            "expected=SECRET_BEFORE observed=SECRET_AFTER])"
        )

        self.assertEqual(
            _llm_retry_feedback(
                message,
                syntax_ok=True,
                exploit_blocked=False,
                regression_passed=True,
            ),
            "The vulnerability was not blocked.",
        )

    def test_create_repairs_aggregates_vectors_only_when_opted_in(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "comments.go"
            source.write_text("package views", encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json", run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "go", (".go",)),
                database={}, crawl={}, roles=(), analysis={},
                repair={
                    "output_dir": "repair/files",
                    "llm": {"enabled": True, "api_key": "test-key"},
                    "validation": {
                        "max_attempts": 1,
                        "aggregate_vectors_by_repair_item": True,
                    },
                },
            )
            findings = [
                Finding(
                    "horizontal", "comments/34/edit", "user1", "vulnerable",
                    "high", "POST", 303,
                ),
                Finding(
                    "horizontal", "comments/34/edit", "user1", "vulnerable",
                    "high", "POST", 303,
                ),
            ]
            update = AttackVector(
                "horizontal", "comments/p1/edit", ["user1"],
                RequestSpec("POST", {"action": "Update"}),
                page_overrides=["comments/34/edit"],
            )
            delete = AttackVector(
                "horizontal", "comments/p1/edit", ["user1"],
                RequestSpec("POST", {"action": "Delete"}),
                page_overrides=["comments/34/edit"],
            )
            details = {
                "applicable": False,
                "passed": True,
                "dimensions": {
                    "vulnerability_blocking": {"passed": True},
                    "regression": {"passed": True},
                },
                "scenarios": [],
            }
            prompt_path = root / "prompt.json"
            with patch(
                "drhl.repair.patcher._repair_with_llm",
                return_value=("package views // patched", {"reason": "owner guard"}, prompt_path),
            ) as repair, patch(
                "drhl.repair.patcher._syntax_check", return_value=(True, "ok"),
            ), patch(
                "drhl.repair.patcher._runtime_validation",
                return_value=(True, True, True, "ok", details),
            ) as runtime:
                results = create_repairs(
                    config,
                    {"source_map": {"comments/34/edit": "comments.go"}},
                    findings,
                    vectors=[update, delete],
                    snapshot=object(),
                )

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].coverage, {
                "covered_vulnerable_findings": 2,
                "aggregated_attack_vectors": 2,
                "validated_operations": ["Update", "Delete"],
            })
            self.assertEqual(repair.call_args.kwargs["vectors"], [update, delete])
            self.assertEqual(runtime.call_args.kwargs["validation_vectors"], [update, delete])
            manifest = serialize_repairs(results)
            self.assertEqual(manifest["summary"]["Repair Items"], 1)
            self.assertEqual(manifest["summary"]["Covered Vulnerable Findings"], 2)
            report_path = root / "report.md"
            write_repair_report(results, report_path)
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Covered Vulnerable Findings: 2", report)
            self.assertIn("Validated Operations: Update, Delete", report)

            prompt = _stage1_messages(
                findings[0], "comments.go", "package views", [],
                vector=update, vectors=[update, delete],
            )[1]["content"]
            self.assertIn('"attack_variants"', prompt)
            self.assertIn('"operation": "Update"', prompt)
            self.assertIn('"operation": "Delete"', prompt)

            token_vector = AttackVector(
                "horizontal", "comments/p1/edit", ["user1"],
                RequestSpec("POST", {"action": "Update", "csrf_token": "secret-value"}),
            )
            redacted_prompt = _stage1_messages(
                findings[0], "comments.go", "package views", [],
                vector=update, vectors=[update, token_vector],
            )[1]["content"]
            self.assertNotIn("secret-value", redacted_prompt)
            self.assertIn("<redacted>", redacted_prompt)
        self.assertEqual(
            _llm_retry_feedback(
                "syntax=(failed); runtime validation skipped",
                syntax_ok=False,
                exploit_blocked=False,
                regression_passed=False,
            ),
            "The syntax/compile check failed.",
        )
        self.assertEqual(
            _llm_retry_feedback(
                "syntax=(ok); runtime validation error: DatabaseError: "
                "SELECT secret FROM private_table failed",
                syntax_ok=True,
                exploit_blocked=False,
                regression_passed=False,
            ),
            "The vulnerability was not blocked. The regression test did not pass.",
        )

    def test_database_validation_covers_read_create_update_and_delete(self):
        class FakeSnapshot:
            def __init__(self):
                self.state = {"value": "baseline", "rows": set()}

            def restore(self):
                self.state = {"value": "baseline", "rows": set()}

        class FakeProbe:
            def __init__(self, snapshot):
                self.snapshot = snapshot

            def execute(self, sql):
                command, _, value = sql.partition(" ")
                if command == "SET":
                    self.snapshot.state["value"] = value
                elif command == "ADD":
                    self.snapshot.state["rows"].add(value)

            def scalar(self, sql):
                command, _, value = sql.partition(" ")
                if command == "VALUE":
                    return str(self.snapshot.state["value"])
                if command == "COUNT":
                    return "1" if value in self.snapshot.state["rows"] else "0"
                raise AssertionError(f"unexpected query: {sql}")

        class FakeSession:
            def __init__(self, role):
                self.role = role

            def close(self):
                return None

        class FakeResponse:
            def __init__(self, text=""):
                self.status_code = 200
                self.url = "http://example.test/result"
                self.text = text

        snapshot = FakeSnapshot()
        session_states = []

        class FakeDetector:
            def __init__(self, config, ignored_snapshot):
                self.config = config

            def _session(self, role):
                session_states.append((getattr(role, "name", "visitor"), snapshot.state["value"]))
                return FakeSession(role)

            def _send(self, session, page, request, role=None):
                authorized = bool(role and role.name == "admin")
                if page == "read":
                    return FakeResponse(snapshot.state["value"] if authorized else "public")
                if page == "create" and authorized:
                    snapshot.state["rows"].add(str(request.params["value"]))
                elif page == "update" and authorized:
                    snapshot.state["value"] = str(request.params["value"])
                elif page == "delete" and authorized:
                    snapshot.state["rows"].discard(str(next(iter(request.params.values()))))
                return FakeResponse()

        rules = [
            {
                "name": "read",
                "page_pattern": "^item\\.php",
                "operation": "read",
                "setup_sql": ["SET {token}"],
                "attack": {
                    "request": {"page": "read", "method": "GET", "replace_params": True},
                    "assert": {"response_not_contains": "{token}"},
                },
                "authorized": {
                    "session_before_setup": True,
                    "request": {"page": "read", "method": "GET", "replace_params": True},
                    "assert": {"response_contains": "{token}"},
                },
            },
            {
                "name": "create",
                "page_pattern": "^item\\.php",
                "operation": "create",
                "attack": {
                    "request": {"page": "create", "method": "POST", "replace_params": True,
                                "params": {"value": "{token}"}},
                    "assert": {"query": "COUNT {token}", "scalar_zero": True},
                },
                "authorized": {
                    "request": {"page": "create", "method": "POST", "replace_params": True,
                                "params": {"value": "{token}"}},
                    "assert": {"query": "COUNT {token}", "scalar_nonzero": True},
                },
            },
            {
                "name": "update",
                "page_pattern": "^item\\.php",
                "operation": "update",
                "setup_sql": ["SET {token1}"],
                "attack": {
                    "request": {"page": "update", "method": "POST", "replace_params": True,
                                "params": {"value": "{token2}"}},
                    "assert": {"query": "VALUE", "scalar_equals": "{token1}"},
                },
                "authorized": {
                    "request": {"page": "update", "method": "POST", "replace_params": True,
                                "params": {"value": "{token2}"}},
                    "assert": {"query": "VALUE", "scalar_equals": "{token2}"},
                },
            },
            {
                "name": "delete",
                "page_pattern": "^item\\.php",
                "operation": "delete",
                "setup_sql": ["ADD {token}"],
                "attack": {
                    "request": {"page": "delete", "method": "POST", "replace_params": True,
                                "params": {"{token}": "{token}"}},
                    "assert": {"query": "COUNT {token}", "scalar_nonzero": True},
                },
                "authorized": {
                    "request": {"page": "delete", "method": "POST", "replace_params": True,
                                "params": {"{token}": "{token}"}},
                    "assert": {"query": "COUNT {token}", "scalar_zero": True},
                },
            },
        ]
        config = PipelineConfig(
            path=Path("config.json"), run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "php", (".php",)),
            database={"driver": "sqlite", "path": "unused"}, crawl={},
            roles=(RoleConfig("user1", "user"), RoleConfig("admin", "admin")), analysis={},
            repair={"validation": {"database_oracles": rules}},
        )
        finding = Finding("horizontal", "item.php?id=2", "user1", "vulnerable", "high", "GET", 200)
        vector = AttackVector("horizontal", "item.php?id=2", ["admin"], RequestSpec("GET", {"id": "2"}))

        with patch("drhl.repair.patcher.create_database_probe", return_value=FakeProbe(snapshot)), \
             patch("drhl.analysis.detector.ActiveDetector", FakeDetector):
            passed, details = _database_validation(config, snapshot, finding, vector)

        self.assertTrue(passed)
        self.assertTrue(details["applicable"])
        self.assertEqual([item["operation"] for item in details["scenarios"]],
                         ["read", "create", "update", "delete"])
        self.assertTrue(all(item["passed"] for item in details["scenarios"]))
        self.assertTrue(details["dimensions"]["vulnerability_blocking"]["passed"])
        self.assertTrue(details["dimensions"]["regression"]["passed"])
        self.assertIn(("admin", "baseline"), session_states)
        self.assertEqual(snapshot.state, {"value": "baseline", "rows": set()})

        rules[0]["attack"]["assert"] = {"response_contains": "{token}"}
        with patch("drhl.repair.patcher.create_database_probe", return_value=FakeProbe(snapshot)), \
             patch("drhl.analysis.detector.ActiveDetector", FakeDetector):
            passed, details = _database_validation(config, snapshot, finding, vector)

        self.assertFalse(passed)
        self.assertFalse(details["dimensions"]["vulnerability_blocking"]["passed"])
        self.assertTrue(details["dimensions"]["regression"]["passed"])

    def test_database_validation_is_not_applicable_without_matching_rule(self):
        config = PipelineConfig(
            path=Path("config.json"), run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "php", (".php",)),
            database={}, crawl={}, roles=(), analysis={}, repair={"validation": {}},
        )
        finding = Finding("static_only", "install.php", "visitor", "vulnerable", "high", "GET", 200)
        vector = AttackVector("static_only", "install.php", [], RequestSpec("GET"))

        passed, details = _database_validation(config, object(), finding, vector)

        self.assertTrue(passed)
        self.assertFalse(details["applicable"])
        self.assertEqual(details["status"], "not_configured")
        self.assertFalse(details["dimensions"]["vulnerability_blocking"]["applicable"])
        self.assertFalse(details["dimensions"]["regression"]["applicable"])

    def test_response_only_database_oracle_is_neutral_and_displays_as_passed(self):
        config = PipelineConfig(
            path=Path("config.json"), run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "php", (".php",)),
            database={}, crawl={}, roles=(), analysis={},
            repair={"validation": {"database_oracles": {
                "response_only_patterns": [r"^install\.php(?:\?|$)"],
                "rules": [],
            }}},
        )
        finding = Finding("static_only", "install.php", "visitor", "vulnerable", "high", "GET", 200)
        vector = AttackVector("static_only", "install.php", [], RequestSpec("GET"))

        passed, details = _database_validation(config, object(), finding, vector)

        self.assertTrue(passed)
        self.assertFalse(details["applicable"])
        self.assertEqual(details["status"], "response_only")
        self.assertTrue(details["display_as_passed"])
        details["combined_dimensions"] = {
            "vulnerability_blocking": {
                "response_oracle_passed": True,
                "database_oracle_applicable": False,
                "database_oracle_passed": True,
            },
            "regression": {
                "response_oracle_passed": True,
                "database_oracle_applicable": False,
                "database_oracle_passed": True,
            },
        }
        with patch("drhl.repair.patcher.progress") as mocked_progress:
            _progress_validation_dimensions(True, True, True, details)
        messages = [call.args[0] for call in mocked_progress.call_args_list]
        self.assertTrue(all("response oracle=passed; database oracle=passed" in item for item in messages))

    def test_runtime_validation_combines_each_database_phase_with_its_dimension(self):
        class FakeSnapshot:
            def restore(self):
                return None

        class FakeSession:
            def close(self):
                return None

        class FakeResponse:
            status_code = 200
            text = "authorized"
            url = "http://example.test/admin.php"

        class FakeDetector:
            def __init__(self, config, snapshot):
                return None

            def run(self, vectors):
                return [
                    Finding(
                        "admin_only", "admin.php", "visitor", "not_vulnerable",
                        "none", "GET", 403,
                    )
                ]

            def _session(self, role):
                return FakeSession()

            def _send(self, session, page, request):
                return FakeResponse()

            def _denial(self, response):
                return None

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "admin.php"
            source.write_text("<?php echo 'admin';", encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json", run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={}, crawl={}, roles=(RoleConfig("admin", "admin"),), analysis={},
                repair={"validation": {"temporary_apply_to_source": True}},
            )
            finding = Finding(
                "admin_only", "admin.php", "visitor", "vulnerable", "high", "GET", 200,
            )
            vector = AttackVector("admin_only", "admin.php", ["admin"], RequestSpec("GET"))

            cases = [
                (False, True, False, True),
                (True, False, True, False),
            ]
            for database_attack, database_regression, expected_exploit, expected_regression in cases:
                details = {
                    "applicable": True,
                    "passed": database_attack and database_regression,
                    "dimensions": {
                        "vulnerability_blocking": {"passed": database_attack},
                        "regression": {"passed": database_regression},
                    },
                }
                with self.subTest(
                    database_attack=database_attack,
                    database_regression=database_regression,
                ), patch("drhl.analysis.detector.ActiveDetector", FakeDetector), patch(
                    "drhl.repair.patcher._database_validation",
                    return_value=(details["passed"], details),
                ):
                    exploit, regression, _, _, returned_details = _runtime_validation(
                        config, FakeSnapshot(), source, "<?php echo 'patched';",
                        finding, vector,
                    )
                self.assertEqual(exploit, expected_exploit)
                self.assertEqual(regression, expected_regression)
                combined = returned_details["combined_dimensions"]
                self.assertEqual(combined["vulnerability_blocking"]["passed"], expected_exploit)
                self.assertEqual(combined["regression"]["passed"], expected_regression)

    def test_runtime_validation_can_use_matched_database_oracle_as_primary(self):
        class FakeSnapshot:
            def restore(self):
                return None

        class FakeSession:
            def close(self):
                return None

        class FakeResponse:
            status_code = 200
            text = "normal response"
            url = "http://example.test/admin.php"

        class FakeDetector:
            def __init__(self, config, snapshot):
                return None

            def run(self, vectors):
                return [Finding(
                    "admin_only", "admin.php", "visitor", "vulnerable", "high", "POST", 200,
                )]

            def _session(self, role):
                return FakeSession()

            def _send(self, session, page, request):
                return FakeResponse()

            def _denial(self, response):
                return []

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "admin.php"
            source.write_text("<?php echo 'admin';", encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json", run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "php", (".php",)),
                database={}, crawl={}, roles=(RoleConfig("admin", "admin"),), analysis={},
                repair={"validation": {
                    "temporary_apply_to_source": True,
                    "database_oracles": {
                        "database_primary_patterns": [r"^admin\.php$"],
                        "rules": [{"page_pattern": r"^admin\.php$"}],
                    },
                }},
            )
            finding = Finding(
                "admin_only", "admin.php", "visitor", "vulnerable", "high", "POST", 200,
            )
            vector = AttackVector("admin_only", "admin.php", ["admin"], RequestSpec("POST"))
            details = {
                "applicable": True,
                "passed": True,
                "dimensions": {
                    "vulnerability_blocking": {"passed": True},
                    "regression": {"passed": True},
                },
            }
            with patch("drhl.analysis.detector.ActiveDetector", FakeDetector), patch(
                "drhl.repair.patcher._database_validation", return_value=(True, details),
            ):
                exploit, regression, _, _, returned = _runtime_validation(
                    config, FakeSnapshot(), source, "<?php echo 'patched';", finding, vector,
                )

            self.assertTrue(exploit)
            self.assertTrue(regression)
            self.assertFalse(
                returned["combined_dimensions"]["vulnerability_blocking"]
                ["response_oracle_applicable"]
            )

    def test_runtime_validation_aggregates_opt_in_response_vectors(self):
        class FakeSnapshot:
            def restore(self):
                return None

        operations = []

        class FakeDetector:
            def __init__(self, config, snapshot):
                return None

            def run(self, vectors):
                self.assert_single_vector(vectors)
                vector = vectors[0]
                operations.append(vector.request.params["action"])
                return [Finding(
                    "horizontal", vector.page, "user1", "not_vulnerable",
                    "high", "POST", 403,
                )]

            @staticmethod
            def assert_single_vector(vectors):
                if len(vectors) != 1:
                    raise AssertionError(vectors)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "comments.go"
            source.write_text("package views", encoding="utf-8")
            config = PipelineConfig(
                path=root / "config.json", run_dir=root / "run",
                target=TargetConfig("http://example.test/", root, "go", (".go",)),
                database={}, crawl={}, roles=(), analysis={},
                repair={"validation": {"temporary_apply_to_source": True}},
            )
            finding = Finding(
                "horizontal", "comments/34/edit", "user1", "vulnerable",
                "high", "POST", 303,
            )
            update = AttackVector(
                "horizontal", "comments/p1/edit", ["user1"],
                RequestSpec("POST", {"action": "Update"}),
                page_overrides=["comments/34/edit"],
            )
            delete = AttackVector(
                "horizontal", "comments/p1/edit", ["user1"],
                RequestSpec("POST", {"action": "Delete"}),
                page_overrides=["comments/34/edit"],
            )
            database_details = {
                "applicable": False,
                "passed": True,
                "dimensions": {
                    "vulnerability_blocking": {"passed": True},
                    "regression": {"passed": True},
                },
                "scenarios": [],
            }
            with patch("drhl.analysis.detector.ActiveDetector", FakeDetector), patch(
                "drhl.repair.patcher._authorized_regression_passed",
                side_effect=[(True, "update allowed"), (True, "delete allowed")],
            ), patch(
                "drhl.repair.patcher._database_validation",
                return_value=(True, database_details),
            ):
                exploit, regression, _, message, returned = _runtime_validation(
                    config, FakeSnapshot(), source, "package views // patched",
                    finding, update, validation_vectors=[update, delete],
                )

            self.assertTrue(exploit)
            self.assertTrue(regression)
            self.assertEqual(operations, ["Update", "Delete"])
            self.assertEqual(
                [item["operation"] for item in returned["response_vectors"]],
                ["Update", "Delete"],
            )
            self.assertIn("Update:", message)
            self.assertIn("Delete:", message)

    def test_database_validation_supports_repair_only_cookies_and_session_requests(self):
        class FakeSnapshot:
            def restore(self):
                return None

        class FakeProbe:
            def execute(self, sql):
                return None

            def scalar(self, sql):
                return ""

        class FakeSession:
            def __init__(self):
                self.cookies = {}
                self.bootstrapped = False

            def close(self):
                return None

        class FakeResponse:
            status_code = 200
            url = "http://example.test/result"

            def __init__(self, text):
                self.text = text

        class FakeDetector:
            def __init__(self, config, snapshot):
                return None

            def _session(self, role):
                return FakeSession()

            def _send(self, session, page, request, role=None):
                if page == "bootstrap":
                    session.bootstrapped = True
                    return FakeResponse("logged in")
                if session.bootstrapped:
                    return FakeResponse("authorized")
                return FakeResponse(session.cookies.get("awcm_member", ""))

        rules = [{
            "name": "cookie-and-bootstrap",
            "page_pattern": "^item\\.php",
            "attack": {
                "role": "visitor",
                "request": {
                    "page": "item.php",
                    "cookies": {"awcm_member": "{token}"},
                },
                "assert": {"response_contains": "{token}"},
            },
            "authorized": {
                "role": "admin",
                "session_requests": [{
                    "page": "bootstrap",
                    "method": "POST",
                    "replace_params": True,
                    "params": {"password": "secret"},
                }],
                "request": {"page": "item.php"},
                "assert": {"response_contains": "authorized"},
            },
        }]
        config = PipelineConfig(
            path=Path("config.json"), run_dir=Path("run"),
            target=TargetConfig("http://example.test/", Path("source"), "php", (".php",)),
            database={}, crawl={},
            roles=(RoleConfig("visitor", "visitor"), RoleConfig("admin", "admin")),
            analysis={}, repair={"validation": {"database_oracles": rules}},
        )
        finding = Finding("static_only", "item.php", "visitor", "vulnerable", "high", "GET", 200)
        vector = AttackVector("static_only", "item.php", ["admin"], RequestSpec("GET"))

        with patch("drhl.repair.patcher.create_database_probe", return_value=FakeProbe()), \
             patch("drhl.analysis.detector.ActiveDetector", FakeDetector):
            passed, details = _database_validation(config, FakeSnapshot(), finding, vector)

        self.assertTrue(passed)
        phases = details["scenarios"][0]["phases"]
        self.assertEqual(phases[0]["request"]["cookie_names"], ["awcm_member"])
        self.assertEqual(phases[1]["session_requests"][0]["page"], "bootstrap")
        self.assertEqual(phases[1]["session_requests"][0]["params"]["password"], "<redacted>")

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
