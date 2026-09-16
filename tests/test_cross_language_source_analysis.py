from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.config import TargetConfig
from drhl.source_analysis import analyze_access_control_source


class CrossLanguageSourceAnalysisTests(unittest.TestCase):
    def _analyze(self, language: str, suffix: str, source: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / f"sample{suffix}").write_text(source, encoding="utf-8")
            target = TargetConfig("http://localhost/", root, language, (suffix,))
            return analyze_access_control_source(
                target,
                access_control_database_fields=["objects.owner_id", "users.role"],
                include_cst=True,
            )

    def test_python_uses_tree_sitter_and_shared_semantic_contract(self):
        result = self._analyze(
            "python",
            ".py",
            """def require_owner(request, obj):
    owner = request.user
    ignored = request.GET.get('page')
    if owner != obj.owner_id:
        raise PermissionError('forbidden')
""",
        )
        self.assertEqual(result["parser"], "tree-sitter-python")
        self.assertEqual(result["cst"][0]["root"]["type"], "module")
        aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
        self.assertIn("request.user", aliases)
        self.assertFalse(any("ignored" in item["aliases"] for item in result["candidate_parameters"]))
        self.assertEqual({item["name"] for item in result["functions"]}, {"require_owner"})

    def test_django_framework_mode_handles_decorators_and_permission_denied(self):
        source = """from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def student_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_student or u.is_superuser
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def dispatch(request, quiz):
    if quiz.draft and not request.user.has_perm('quiz.change_quiz'):
        raise PermissionDenied
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "views.py").write_text(source, encoding="utf-8")
            target = TargetConfig("http://localhost/", root, "python", (".py",))
            regular = analyze_access_control_source(target)
            django = analyze_access_control_source(target, framework="django")

        self.assertEqual(regular["parameters"], [])
        self.assertEqual(regular["functions"], [])
        aliases = {alias for item in django["parameters"] for alias in item["aliases"]}
        self.assertTrue(
            {"request.user", "u.is_active", "u.is_student", "u.is_superuser", "request.user.has_perm"}
            <= aliases
        )
        self.assertIn("quiz.draft", aliases)
        self.assertEqual(
            {item["name"] for item in django["functions"]},
            {"student_required", "dispatch"},
        )

    def test_django_declarative_filter_is_explicitly_opt_in(self):
        source = """class PostList:
    queryset = Post.objects.filter(status=1).order_by('-created_on')
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "views.py").write_text(source, encoding="utf-8")
            target = TargetConfig("http://localhost/", root, "python", (".py",))
            regular = analyze_access_control_source(
                target,
                framework="django",
                access_control_database_fields=["status"],
            )
            configured = analyze_access_control_source(
                target,
                framework="django",
                access_control_database_fields=["status"],
                declarative_access_control_fields=["Post.status"],
            )

        self.assertEqual(regular["parameters"], [])
        self.assertEqual(
            {item["expression"] for item in configured["parameters"]},
            {"Post.status"},
        )
        self.assertFalse(
            any(item["kind"] == "conditional" for item in configured["snippets"])
        )
        database_snippet = next(
            item
            for item in configured["snippets"]
            if item["kind"] == "database_operation"
        )
        self.assertEqual(database_snippet["code"], "Post.objects.filter(status=1)")
        self.assertEqual(database_snippet["related_conditions"], [])
        self.assertNotIn("if_framework", database_snippet)
        self.assertEqual(
            database_snippet["parameter_ids"],
            [configured["parameters"][0]["id"]],
        )

    def test_go_candidates_come_from_tree_sitter_conditions(self):
        result = self._analyze(
            "go",
            ".go",
            """package sample
import "net/http"
func requireOwner(w http.ResponseWriter, userID int, ownerID int) {
    ignored := 1
    if userID != ownerID {
        http.Error(w, "forbidden", http.StatusForbidden)
        return
    }
}
""",
        )
        self.assertEqual(result["parser"], "tree-sitter-go")
        self.assertEqual(result["cst"][0]["root"]["type"], "source_file")
        expressions = {item["expression"] for item in result["candidate_parameters"]}
        self.assertEqual(expressions, {"userID", "ownerID"})
        self.assertEqual({item["name"] for item in result["functions"]}, {"requireOwner"})

    def test_java_alias_and_terminating_branch_validate_function(self):
        result = self._analyze(
            "java",
            ".java",
            """class Guard {
  void requireAdmin(HttpSession session, HttpServletResponse response) throws Exception {
    String role = (String) session.getAttribute("role");
    String ignored = "business";
    if (!role.equals("admin")) {
      response.sendError(403);
      return;
    }
  }
}
""",
        )
        aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
        self.assertIn("role", aliases)
        self.assertFalse(any("ignored" in item["aliases"] for item in result["candidate_parameters"]))
        self.assertEqual({item["name"] for item in result["functions"]}, {"requireAdmin"})

    def test_java_jsp_recovers_concatenated_sql_and_session_admin_role(self):
        result = self._analyze(
            "jsp",
            ".jsp",
            '''<%
String sessionUsername = (String) session.getAttribute("username");
String sessionType = (String) session.getAttribute("type");
if (sessionUsername != null) {
    db.selectQuery("SELECT * FROM objects " +
                   "WHERE owner_id=\\\"" + sessionUsername + "\\\"");
}
if (sessionType.equals("Admin")) {
    showAdminControls();
}
%>''',
        )
        parameters = {
            alias
            for item in result["parameters"]
            for alias in item["aliases"]
        }
        self.assertIn("username", parameters)
        self.assertIn("type", parameters)
        self.assertEqual(result["functions"], [])
        self.assertTrue(
            any(
                evidence.get("kind") == "java_jsp_session_admin_role"
                for item in result["parameters"]
                for evidence in item["validation_evidence"]
            )
        )
    def test_java_role_source_propagates_across_method_calls(self):
        result = self._analyze(
            "java",
            ".java",
            '''class Roles {
  void entry(ServerInterface server) {
    forward(server.isUserInRole("administrator"));
    save(server.isUserInRole("trusted"));
  }
  void forward(boolean administrator) { enforce(administrator); }
  void enforce(boolean isAdmin) { if (!isAdmin) auditVote(); }
  void save(boolean trusted) { if (!trusted) sanitizeHtml(); }
}''',
        )
        aliases = {
            alias
            for item in result["parameters"]
            for alias in item["aliases"]
        }
        self.assertIn("administrator", aliases)
        self.assertIn("isAdmin", aliases)
        self.assertIn("trusted", aliases)
        self.assertEqual(result["functions"], [])
        self.assertEqual(
            {
                item["condition"]
                for item in result["snippets"]
                if item["kind"] == "conditional"
            },
            {"(!isAdmin)", "(!trusted)"},
        )
        self.assertTrue(
            all(
                any(evidence.get("kind") == "java_jsp_role_source" for evidence in item["validation_evidence"])
                for item in result["parameters"]
            )
        )

    def test_jsp_wrapper_maps_cross_scriptlet_conditions_to_original_ranges(self):
        result = self._analyze(
            "jsp",
            ".jsp",
            '''<% if(sessionType.equals("Admin")){ %>
<a href="admin.jsp"><%= forum_id %></a>
<% } %>
<% if(sessionType.equals("Admin")){ %>
<span>admin</span>
<% } %>''',
        )
        snippets = [
            item for item in result["snippets"] if item["kind"] == "conditional"
        ]
        self.assertEqual([item["start_line"] for item in snippets], [1, 4])
        self.assertTrue(
            all('sessionType.equals("Admin")' in item["code"] for item in snippets)
        )

    def test_php_rejects_request_superglobal_but_keeps_other_dbmatch_parameters(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
function require_owner($owner) {
    $requested = $_GET['owner_id'];
    $sql = "SELECT * FROM objects WHERE owner_id=$owner";
    if ($requested != $owner) {
        http_response_code(403);
        exit;
    }
}
""",
        )
        aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
        candidate_aliases = {
            alias for item in result["candidate_parameters"] for alias in item["aliases"]
        }
        self.assertNotIn("$_GET['owner_id']", aliases)
        self.assertIn("$_GET['owner_id']", candidate_aliases)
        self.assertIn("$owner", aliases)
        self.assertEqual({item["name"] for item in result["functions"]}, {"require_owner"})

    def test_php_only_cookie_and_session_superglobals_validate(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
if ($_GET['role']) { http_response_code(403); }
if ($_POST['role']) { http_response_code(403); }
if ($_REQUEST['role']) { http_response_code(403); }
if ($_SESSION['role']) { http_response_code(403); }
if ($_COOKIE['role']) { http_response_code(403); }
""",
        )
        candidates = {item["expression"] for item in result["candidate_parameters"]}
        validated = {item["expression"] for item in result["parameters"]}
        self.assertEqual(
            candidates,
            {
                "$_GET['role']",
                "$_POST['role']",
                "$_REQUEST['role']",
                "$_SESSION['role']",
                "$_COOKIE['role']",
            },
        )
        self.assertEqual(validated, {"$_SESSION['role']", "$_COOKIE['role']"})

    def test_php_call_names_are_function_semantics_not_parameters(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
function guard($fid) {
    if (!is_moderator($fid)) {
        http_response_code(403);
    }
}
""",
        )
        candidates = {item["expression"] for item in result["candidate_parameters"]}
        self.assertIn("$fid", candidates)
        self.assertNotIn("is_moderator", candidates)

    def test_php_aliases_do_not_cross_function_scopes(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
function auth_gate() {
    $state = $_SESSION['role'];
    if ($state != 'admin') { http_response_code(403); }
}
function business_gate() {
    $state = $_GET['action'];
    if ($state) { http_response_code(403); }
}
""",
        )
        aliases = {alias for item in result["parameters"] for alias in item["aliases"]}
        self.assertIn("$_SESSION['role']", aliases)
        self.assertNotIn("$_GET['action']", aliases)

    def test_php_function_results_are_not_aliases_of_arguments(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
$permissions = forum_permissions($fid);
if ($permissions['canview'] != 1) { http_response_code(403); }
if ($fid == 0) { $missing = true; }
""",
        )
        self.assertFalse(
            any(
                "$fid" in item["aliases"]
                and "$permissions['canview']" in item["aliases"]
                for item in result["candidate_parameters"]
            )
        )

    def test_php_recovers_mybb_database_wrapper_and_dynamic_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.php").write_text(
                """<?php
if (isset($_COOKIE['adminsid'])) { $present = true; }
$query = $db->simple_select(
    "adminsessions",
    "*",
    "sid='".$db->escape_string($_COOKIE['adminsid'])."'"
);
""",
                encoding="utf-8",
            )
            target = TargetConfig("http://localhost/", root, "php", (".php",))
            result = analyze_access_control_source(
                target,
                access_control_database_fields=["mybb_adminsessions.sid"],
            )
        parameter = next(
            item for item in result["parameters"]
            if "$_COOKIE['adminsid']" in item["aliases"]
        )
        self.assertTrue(
            any(
                evidence.get("kind") == "database_field"
                and evidence.get("table") == "adminsessions"
                and evidence.get("field") == "sid"
                for evidence in parameter["validation_evidence"]
            )
        )
        database_snippet = next(
            item
            for item in result["snippets"]
            if item["kind"] == "database_operation"
        )
        self.assertIn("simple_select", database_snippet["code"])
        self.assertEqual(database_snippet["parameter_ids"], [parameter["id"]])

    def test_php_propagates_boolean_state_to_later_denial(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
function check_token($expected) {
    $showform = false;
    if ($_COOKIE['token'] != $expected) {
        $showform = true;
    } else {
        $showform = false;
    }
    if ($showform) {
        http_response_code(403);
        exit;
    }
}
""",
        )
        cookie = next(
            item for item in result["parameters"]
            if "$_COOKIE['token']" in item["aliases"]
        )
        self.assertTrue(
            any(
                evidence.get("kind") == "terminating_condition"
                and any(
                    termination.get("kind") == "propagated_termination"
                    for termination in evidence.get("terminations", [])
                )
                for evidence in cookie["validation_evidence"]
            )
        )
        self.assertIn("check_token", {item["name"] for item in result["functions"]})

    def test_generic_business_control_flow_is_not_access_denial(self):
        samples = [
            (
                "python",
                ".py",
                """def save(valid):
    if not valid:
        raise ValueError('bad input')
""",
            ),
            (
                "go",
                ".go",
                """package sample
func save(err error) error {
    if err != nil { return err }
    return nil
}
""",
            ),
            (
                "java",
                ".java",
                """class Save {
  void save(boolean valid) {
    if (!valid) throw new IllegalArgumentException("bad input");
  }
}
""",
            ),
            (
                "php",
                ".php",
                """<?php
if ($saved) {
    header('Location: success.php');
    exit;
}
""",
            ),
        ]
        for language, suffix, source in samples:
            with self.subTest(language=language):
                result = self._analyze(language, suffix, source)
                self.assertEqual(result["parameters"], [])
                self.assertEqual(result["functions"], [])

    def test_nested_denial_belongs_to_nearest_condition(self):
        result = self._analyze(
            "php",
            ".php",
            """<?php
if ($action === 'delete') {
    if ($role !== 'admin') {
        http_response_code(403);
        exit;
    }
}
""",
        )
        validated = {item["expression"] for item in result["parameters"]}
        candidates = {item["expression"] for item in result["candidate_parameters"]}
        self.assertIn("$action", candidates)
        self.assertNotIn("$action", validated)
        self.assertIn("$role", validated)

    def test_if_frameworks_keep_language_syntax_and_drop_unrelated_code(self):
        python = self._analyze(
            "python",
            ".py",
            """if not request.user.is_staff:
    audit('staff check')
    raise PermissionError('forbidden')
""",
        )
        go = self._analyze(
            "go",
            ".go",
            """package sample
import "net/http"
func guard(w http.ResponseWriter, role string) {
    if role != "admin" {
        audit(role)
        http.Error(w, "forbidden", http.StatusForbidden)
    }
}
""",
        )
        python_snippet = next(item for item in python["snippets"] if item["kind"] == "conditional")
        go_snippet = next(item for item in go["snippets"] if item["kind"] == "conditional")
        self.assertIn("audit('staff check')", python_snippet["code"])
        self.assertNotIn("audit('staff check')", python_snippet["if_framework"])
        self.assertTrue(python_snippet["if_framework"].startswith("if not request.user.is_staff:\n"))
        self.assertIn("audit(role)", go_snippet["code"])
        self.assertNotIn("audit(role)", go_snippet["if_framework"])
        self.assertTrue(go_snippet["if_framework"].startswith('if role != "admin" {\n'))


if __name__ == "__main__":
    unittest.main()
