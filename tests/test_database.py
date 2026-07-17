from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drhl.database import MySQLSnapshot, SQLiteSnapshot


class DatabaseTests(unittest.TestCase):
    def test_sqlite_restore_replaces_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "app.sqlite3"
            database.write_bytes(b"baseline")
            snapshot = SQLiteSnapshot({"path": str(database)}, root / "snapshot")
            snapshot.create()
            database.write_bytes(b"changed")
            snapshot.restore()
            self.assertEqual(database.read_bytes(), b"baseline")

    def test_mysql_dump_is_database_level(self):
        calls = []

        def fake_execute(args, **kwargs):
            calls.append(list(args))
            if kwargs.get("stdout"):
                kwargs["stdout"].write(b"DROP DATABASE IF EXISTS `app`;\n")

        with tempfile.TemporaryDirectory() as directory:
            snapshot = MySQLSnapshot(
                {"database": "app", "user": "root", "password": "secret"}, Path(directory)
            )
            with patch("drhl.database._execute", side_effect=fake_execute):
                snapshot.create()
                snapshot.restore()
        self.assertIn("--add-drop-database", calls[0])
        self.assertIn("--databases", calls[0])
        self.assertEqual(calls[1][0], "mysql")


if __name__ == "__main__":
    unittest.main()

