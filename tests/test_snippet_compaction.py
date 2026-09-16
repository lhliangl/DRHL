from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from drhl.io import write_json
from drhl.pipeline import _load_repair_source_context
from drhl.repair.patcher import _snippet_context
from drhl.snippet_compaction import compact_snippet_document, compact_snippets


class SnippetCompactionTests(unittest.TestCase):
    def test_keeps_cross_file_duplicates_and_deduplicates_same_file_code(self):
        compacted = compact_snippets(
            [
                {
                    "path": "a.php",
                    "kind": "conditional",
                    "start_line": 1,
                    "code": "guard();",
                    "parameter_ids": ["P1"],
                    "function_ids": [],
                },
                {
                    "path": "a.php",
                    "kind": "conditional",
                    "start_line": 9,
                    "code": "guard();",
                    "parameter_ids": ["P2"],
                    "function_ids": [],
                },
                {
                    "path": "b.php",
                    "kind": "conditional",
                    "start_line": 1,
                    "code": "guard();",
                    "parameter_ids": ["P3"],
                    "function_ids": [],
                },
            ]
        )
        self.assertEqual(compacted, [
            {"path": "a.php", "code": "guard();"},
            {"path": "b.php", "code": "guard();"},
        ])

    def test_prefers_if_framework_falls_back_to_code_and_deduplicates(self):
        source = [
            {
                "path": "inc\\auth.php",
                "kind": "conditional",
                "code": "if ($logged_in) {\r\n  allow();  \r\n}",
                "if_framework": "if (!$logged_in) {\r\n    deny();  \r\n}",
            },
            {
                "path": "inc/auth.php",
                "kind": "condition",
                "if_framework": "if (!$logged_in) {\n    deny();\n}",
            },
            {"path": "admin.php", "kind": "guard_call", "code": "require_admin();"},
            {"path": "admin.php", "kind": "guard_call", "code": "require_admin();\n"},
            {"path": "other.php", "kind": "guard_call", "code": "require_admin();"},
            {"path": "empty.php", "kind": "conditional", "code": ""},
        ]

        compacted = compact_snippets(source)

        self.assertEqual(compacted, [
            {
                "path": "inc/auth.php",
                "if_framework": "if (!$logged_in) {\n    deny();\n}",
            },
            {
                "path": "admin.php",
                "code": "require_admin();",
            },
            {
                "path": "other.php",
                "code": "require_admin();",
            },
        ])
        document = compact_snippet_document(source)
        self.assertEqual(document["summary"], {
            "source_items": 6,
            "llm_items": 3,
            "items_removed": 3,
        })

    def test_can_filter_only_the_llm_artifact_by_kind_and_guard_framework(self):
        source = [
            {
                "path": "target.php",
                "kind": "database_operation",
                "code": "$sql = \"SELECT * FROM users\";",
            },
            {
                "path": "target.php",
                "kind": "conditional",
                "code": "if (!$logged_in) { die(); }",
                "if_framework": "if (!$logged_in) {\n    die();\n}",
            },
            {
                "path": "business.php",
                "kind": "conditional",
                "code": "if ($id) { $sql = 'SELECT 1'; }",
            },
        ]

        default_document = compact_snippet_document(source)
        filtered_document = compact_snippet_document(
            source,
            exclude_kinds=["database_operation"],
            require_if_framework=True,
        )

        self.assertEqual(len(default_document["snippets"]), 3)
        self.assertEqual(filtered_document["snippets"], [
            {"path": "target.php", "if_framework": "if (!$logged_in) {\n    die();\n}"},
        ])
        self.assertEqual(filtered_document["summary"], {
            "source_items": 3,
            "llm_items": 1,
            "items_removed": 2,
        })

    def test_prefix_rules_are_opt_in_and_match_path_and_code(self):
        source = [
            {
                "path": "admin/votanti.php",
                "if_framework": "if (isset($_COOKIE[$cookie])) { allow(); }",
            },
            {
                "path": "public.php",
                "if_framework": "if (isset($_COOKIE[$cookie])) { allow(); }",
            },
        ]
        rules = [
            {
                "path_pattern": r"^admin/",
                "code_pattern": r"\$_COOKIE",
                "prefix": "$cookie = 'admin_cookie';",
            }
        ]

        default = compact_snippets(source)
        configured = compact_snippets(source, prefix_rules=rules)

        self.assertEqual(default[0]["if_framework"], "if (isset($_COOKIE[$cookie])) { allow(); }")
        self.assertEqual(
            configured[0]["if_framework"],
            "$cookie = 'admin_cookie';\nif (isset($_COOKIE[$cookie])) { allow(); }",
        )
        self.assertEqual(configured[1], default[1])

    def test_code_pattern_exclusions_are_opt_in(self):
        source = [
            {"path": "a.php", "if_framework": "if ($legacy) { allow(); }"},
            {"path": "b.php", "if_framework": "if ($current) { allow(); }"},
        ]

        default = compact_snippets(source)
        configured = compact_snippets(
            source,
            exclude_code_patterns=[r"^if\s*\(\$legacy\)"],
        )

        self.assertEqual(len(default), 2)
        self.assertEqual(configured, [default[1]])

    def test_repair_loader_generates_llm_snippets_without_replacing_original(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            original = {
                "snippets": [
                    {
                        "path": "inc/auth.php",
                        "kind": "conditional",
                        "start_line": 10,
                        "code": "if (!$ok) { die(); }",
                        "if_framework": "if (!$ok) {\n    die();\n}",
                    }
                ]
            }
            original_path = run_dir / "source" / "snippets.json"
            write_json(original_path, original)

            context = _load_repair_source_context(run_dir)

            self.assertEqual(json.loads(original_path.read_text(encoding="utf-8")), original)
            self.assertEqual(context["snippets"], [
                {
                    "path": "inc/auth.php",
                    "if_framework": "if (!$ok) {\n    die();\n}",
                }
            ])
            generated = json.loads(
                (run_dir / "source" / "llm_snippets.json").read_text(encoding="utf-8")
            )
            self.assertEqual(generated["snippets"], context["snippets"])

    def test_prompt_selection_accepts_compact_format_and_keeps_minimal_fields(self):
        context = {
            "snippets": [
                {"path": "target.php", "if_framework": "require_login();"},
                {"path": "inc/auth.php", "code": "if (!$logged_in) { die(); }"},
            ]
        }

        selected = _snippet_context("target.php", context)

        self.assertEqual(len(selected), 2)
        self.assertTrue(all(set(item) in ({"path", "code"}, {"path", "if_framework"}) for item in selected))


if __name__ == "__main__":
    unittest.main()
