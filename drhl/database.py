from __future__ import annotations

import os
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, BinaryIO, Sequence

from .errors import DatabaseError


def _execute(
    args: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
    timeout: float | None = None,
    cwd: str | Path | None = None,
) -> None:
    try:
        subprocess.run(
            list(args), check=True, env=env, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE,
            timeout=timeout, cwd=str(cwd) if cwd is not None else None,
        )
    except FileNotFoundError as exc:
        raise DatabaseError(f"database executable was not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise DatabaseError(f"database command timed out ({args[0]}) after {timeout}s") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        if not message:
            message = (exc.stdout or b"").decode("utf-8", errors="replace").strip()
        raise DatabaseError(f"database command failed ({args[0]}): {message}") from exc


def _command_value(config: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = config.get(name)
        if value:
            return value
    return None


def _optional_command(config: dict[str, Any], *names: str) -> None:
    value = _command_value(config, *names)
    if not value:
        return
    cwd = None
    timeout = None
    command = value
    if isinstance(value, dict):
        command = value.get("command") or value.get("args")
        cwd = value.get("cwd")
        timeout = value.get("timeout")
    if not isinstance(command, list) or not command:
        raise DatabaseError(f"database.{names[0]} must be a non-empty argument list or command object")
    _execute([str(item) for item in command], env=os.environ.copy(), timeout=float(timeout) if timeout else None, cwd=cwd)


class Snapshot(ABC):
    def __init__(self, config: dict[str, Any], directory: Path):
        self.config = config
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def create(self) -> Path:
        pass

    @abstractmethod
    def restore(self) -> None:
        pass


class MySQLSnapshot(Snapshot):
    def __init__(self, config: dict[str, Any], directory: Path):
        super().__init__(config, directory)
        self.path = directory / "baseline.sql"

    def _connection_args(self) -> list[str]:
        args = [
            "--host", str(self.config.get("host", "127.0.0.1")),
            "--port", str(self.config.get("port", 3306)),
            "--user", str(self.config["user"]),
            "--protocol", "TCP",
        ]
        args.extend(str(item) for item in self.config.get("extra_args", []))
        return args

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.config.get("password"):
            env["MYSQL_PWD"] = str(self.config["password"])
        return env

    def create(self) -> Path:
        # InnoDB can use a non-blocking consistent transaction. MyISAM cannot,
        # so applications such as scarf must request a global read lock.
        consistency = (
            ["--single-transaction"]
            if self.config.get("single_transaction", True)
            else ["--lock-all-tables"]
        )
        command = [
            str(self.config.get("mysqldump", "mysqldump")),
            *self._connection_args(),
            *consistency,
            "--routines",
            "--triggers",
            "--events",
            "--add-drop-table",
            "--add-drop-database",
            "--databases",
            str(self.config["database"]),
        ]
        with self.path.open("wb") as output:
            _execute(command, env=self._env(), stdout=output)
        if self.path.stat().st_size == 0:
            raise DatabaseError("mysqldump created an empty baseline")
        return self.path

    def restore(self) -> None:
        if not self.path.is_file():
            raise DatabaseError("MySQL baseline does not exist")
        _optional_command(self.config, "before_restore_command", "pre_restore_command")
        try:
            command = [str(self.config.get("mysql", "mysql")), *self._connection_args()]
            with self.path.open("rb") as source:
                _execute(command, env=self._env(), stdin=source)
        finally:
            _optional_command(self.config, "after_restore_command", "post_restore_command")


class SQLiteSnapshot(Snapshot):
    def __init__(self, config: dict[str, Any], directory: Path):
        super().__init__(config, directory)
        self.database = Path(str(config["path"])).resolve()
        self.path = directory / "baseline.sqlite3"

    def create(self) -> Path:
        if not self.database.is_file():
            raise DatabaseError(f"SQLite database does not exist: {self.database}")
        shutil.copy2(self.database, self.path)
        return self.path

    def restore(self) -> None:
        if not self.path.is_file():
            raise DatabaseError("SQLite baseline does not exist")
        _optional_command(self.config, "before_restore_command", "pre_restore_command")
        try:
            temporary = self.database.with_name(f"{self.database.name}.{os.getpid()}.{time.time_ns()}.drhl-restore")
            shutil.copy2(self.path, temporary)
            os.replace(temporary, self.database)
        finally:
            _optional_command(self.config, "after_restore_command", "post_restore_command")


class PostgreSQLSnapshot(Snapshot):
    def __init__(self, config: dict[str, Any], directory: Path):
        super().__init__(config, directory)
        self.path = directory / "baseline.sql"

    def _connection_args(self) -> list[str]:
        args = [
            "--host", str(self.config.get("host", "127.0.0.1")),
            "--port", str(self.config.get("port", 5432)),
            "--username", str(self.config["user"]),
            "--dbname", str(self.config["database"]),
        ]
        args.extend(str(item) for item in self.config.get("extra_args", []))
        return args

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.config.get("password"):
            env["PGPASSWORD"] = str(self.config["password"])
        return env

    def create(self) -> Path:
        command = [
            str(self.config.get("pg_dump", "pg_dump")),
            *self._connection_args(),
            "--format=plain",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
        ]
        command.extend(str(item) for item in self.config.get("dump_extra_args", []))
        with self.path.open("wb") as output:
            _execute(command, env=self._env(), stdout=output, timeout=float(self.config.get("timeout", 120)))
        if self.path.stat().st_size == 0:
            raise DatabaseError("pg_dump created an empty baseline")
        return self.path

    def restore(self) -> None:
        if not self.path.is_file():
            raise DatabaseError("PostgreSQL baseline does not exist")
        _optional_command(self.config, "before_restore_command", "pre_restore_command")
        try:
            command = [
                str(self.config.get("psql", "psql")),
                *self._connection_args(),
                "--set",
                "ON_ERROR_STOP=on",
                "--single-transaction",
                "--file",
                str(self.path),
            ]
            command.append("--quiet")
            command.extend(str(item) for item in self.config.get("restore_extra_args", []))
            _execute(
                command,
                env=self._env(),
                stdout=subprocess.DEVNULL,
                timeout=float(self.config.get("timeout", 120)),
            )
        finally:
            _optional_command(self.config, "after_restore_command", "post_restore_command")


class CommandSnapshot(Snapshot):
    def __init__(self, config: dict[str, Any], directory: Path):
        super().__init__(config, directory)
        self.path = directory / str(config.get("snapshot_name", "baseline.snapshot"))

    def _command(self, name: str) -> list[str]:
        value = self.config.get(name)
        if not isinstance(value, list) or not value:
            raise DatabaseError(f"database.{name} must be a non-empty argument list")
        return [str(item).replace("{snapshot}", str(self.path)) for item in value]

    def create(self) -> Path:
        _execute(self._command("snapshot_command"), env=os.environ.copy())
        if self.config.get("snapshot_must_exist", True) and not self.path.exists():
            raise DatabaseError(f"snapshot command did not create: {self.path}")
        return self.path

    def restore(self) -> None:
        _optional_command(self.config, "before_restore_command", "pre_restore_command")
        try:
            _execute(self._command("restore_command"), env=os.environ.copy())
        finally:
            _optional_command(self.config, "after_restore_command", "post_restore_command")


def create_snapshot(config: dict[str, Any], directory: Path) -> Snapshot:
    driver = str(config.get("driver", "none")).lower()
    if driver == "mysql":
        if not config.get("database") or not config.get("user"):
            raise DatabaseError("MySQL requires database.database and database.user")
        return MySQLSnapshot(config, directory)
    if driver == "sqlite":
        if not config.get("path"):
            raise DatabaseError("SQLite requires database.path")
        return SQLiteSnapshot(config, directory)
    if driver in {"postgres", "postgresql"}:
        if not config.get("database") or not config.get("user"):
            raise DatabaseError("PostgreSQL requires database.database and database.user")
        return PostgreSQLSnapshot(config, directory)
    if driver == "command":
        return CommandSnapshot(config, directory)
    raise DatabaseError(f"unsupported database driver: {driver!r}")
