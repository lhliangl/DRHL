from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from drhl.analysis.denials import extract_source_denial_markers


class SourceDenialMarkerTests(unittest.TestCase):
    def test_extracts_termination_messages_from_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guard.php").write_text(
                "<?php if (!$ok) { die('Access denied'); } echo \"Please login\"; exit();",
                encoding="utf-8",
            )

            markers = extract_source_denial_markers(root)

            self.assertIn("Access denied", markers)
            self.assertNotIn("Please login", markers)

    def test_does_not_invent_markers_from_ordinary_form_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "login.php").write_text(
                "<form><label>Password:</label><input name='password'></form>",
                encoding="utf-8",
            )

            markers = extract_source_denial_markers(root)

            self.assertNotIn("Password:", markers)


if __name__ == "__main__":
    unittest.main()

