from __future__ import annotations

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .errors import DatabaseError


class DatabaseProbe(ABC):
    @abstractmethod
    def capture(self) -> str:
        """Return a deterministic representation of application data."""

    @abstractmethod
    def execute(self, sql: str) -> None:
        """Execute trusted setup SQL from the local DRHL configuration."""

    @abstractmethod
    def scalar(self, sql: str) -> str:
        """Execute a scalar verification query."""


class MySQLProbe(DatabaseProbe):
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.config.get("password"):
            env["MYSQL_PWD"] = str(self.config["password"])
        return env

    def _connection(self) -> list[str]:
        return [
            "--host", str(self.config.get("host", "127.0.0.1")),
            "--port", str(self.config.get("port", 3306)),
            "--user", str(self.config["user"]),
            "--protocol", "TCP",
        ]

    def _run(self, command: list[str]) -> bytes:
        try:
            completed = subprocess.run(
                command, check=True, env=self._env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return completed.stdout
        except FileNotFoundError as exc:
            raise DatabaseError(f"database probe executable was not found: {command[0]}") from exc
        except subprocess.CalledProcessError as exc:
            message = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
            raise DatabaseError(f"database probe failed: {message}") from exc

    def capture(self) -> str:
        command = [
            str(self.config.get("mysqldump", "mysqldump")),
            *self._connection(),
            "--no-create-info",
            "--skip-extended-insert",
            "--complete-insert",
            "--hex-blob",
            "--skip-comments",
            "--compact",
            "--order-by-primary",
            str(self.config["database"]),
        ]
        return self._run(command).decode("utf-8", errors="replace")

    def execute(self, sql: str) -> None:
        command = [
            str(self.config.get("mysql", "mysql")),
            *self._connection(),
            "--database", str(self.config["database"]),
            "--execute", sql,
        ]
        self._run(command)

    def scalar(self, sql: str) -> str:
        command = [
            str(self.config.get("mysql", "mysql")),
            *self._connection(),
            "--database", str(self.config["database"]),
            "--batch",
            "--skip-column-names",
            "--execute", sql,
        ]
        return self._run(command).decode("utf-8", errors="replace").strip()


class SQLiteProbe(DatabaseProbe):
    def __init__(self, config: dict[str, Any]):
        self.path = Path(str(config["path"])).resolve()

    def capture(self) -> str:
        import sqlite3

        with sqlite3.connect(str(self.path)) as connection:
            return "\n".join(connection.iterdump())

    def execute(self, sql: str) -> None:
        import sqlite3

        with sqlite3.connect(str(self.path)) as connection:
            connection.executescript(sql)
            connection.commit()

    def scalar(self, sql: str) -> str:
        import sqlite3

        with sqlite3.connect(str(self.path)) as connection:
            row = connection.execute(sql).fetchone()
            return "" if not row else str(row[0])


class PostgreSQLProbe(DatabaseProbe):
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.config.get("password"):
            env["PGPASSWORD"] = str(self.config["password"])
        return env

    def _connection(self) -> list[str]:
        args = [
            "--host", str(self.config.get("host", "127.0.0.1")),
            "--port", str(self.config.get("port", 5432)),
            "--username", str(self.config["user"]),
            "--dbname", str(self.config["database"]),
        ]
        args.extend(str(item) for item in self.config.get("extra_args", []))
        return args

    def _run(self, command: list[str]) -> bytes:
        try:
            completed = subprocess.run(
                command,
                check=True,
                env=self._env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=float(self.config.get("timeout", 120)),
            )
            return completed.stdout
        except FileNotFoundError as exc:
            raise DatabaseError(f"database probe executable was not found: {command[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            raise DatabaseError(f"database probe timed out: {command[0]}") from exc
        except subprocess.CalledProcessError as exc:
            message = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
            raise DatabaseError(f"database probe failed: {message}") from exc

    def capture(self) -> str:
        command = [
            str(self.config.get("pg_dump", "pg_dump")),
            *self._connection(),
            "--data-only",
            "--column-inserts",
            "--no-owner",
            "--no-privileges",
        ]
        return self._run(command).decode("utf-8", errors="replace")

    def execute(self, sql: str) -> None:
        command = [
            str(self.config.get("psql", "psql")),
            *self._connection(),
            "--set", "ON_ERROR_STOP=on",
            "--quiet",
            "--command", sql,
        ]
        self._run(command)

    def scalar(self, sql: str) -> str:
        command = [
            str(self.config.get("psql", "psql")),
            *self._connection(),
            "--set", "ON_ERROR_STOP=on",
            "--tuples-only",
            "--no-align",
            "--quiet",
            "--command", sql,
        ]
        return self._run(command).decode("utf-8", errors="replace").strip()


def create_database_probe(config: dict[str, Any]) -> DatabaseProbe:
    driver = str(config.get("driver", "none")).lower()
    if driver == "mysql":
        return MySQLProbe(config)
    if driver == "sqlite":
        return SQLiteProbe(config)
    if driver in {"postgres", "postgresql"}:
        return PostgreSQLProbe(config)
    raise DatabaseError(f"database mutation oracle is not supported for driver: {driver}")
