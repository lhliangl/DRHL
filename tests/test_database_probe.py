from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from drhl.database_probe import PostgreSQLProbe, create_database_probe


class DatabaseProbeTests(unittest.TestCase):
    @patch("drhl.database_probe.subprocess.run")
    def test_postgresql_scalar_uses_psql_without_headers(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, stdout=b"7\n", stderr=b"")
        probe = create_database_probe({
            "driver": "postgresql",
            "host": "db.example.test",
            "port": 5433,
            "database": "app",
            "user": "tester",
            "password": "secret",
            "psql": "psql-custom",
        })

        self.assertIsInstance(probe, PostgreSQLProbe)
        self.assertEqual(probe.scalar("SELECT COUNT(*) FROM items"), "7")
        command = run.call_args.args[0]
        self.assertEqual(command[0], "psql-custom")
        self.assertIn("--tuples-only", command)
        self.assertIn("--no-align", command)
        self.assertEqual(run.call_args.kwargs["env"]["PGPASSWORD"], "secret")


if __name__ == "__main__":
    unittest.main()
