from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "wackopicko.json"
DEFAULT_SNAPSHOT = Path(__file__).resolve().parent / "wackopicko" / "wackopicko_baseline.sql"


class RecoveryError(RuntimeError):
    pass


def _load_database_config(config_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RecoveryError(f"configuration file was not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise RecoveryError(f"configuration file is not valid JSON: {config_path}: {exc}") from exc

    database = dict(data.get("database") or {})
    if database.get("driver") != "mysql":
        raise RecoveryError("this recovery script currently supports only database.driver=mysql")
    for key in ("host", "port", "database", "user"):
        if database.get(key) in (None, ""):
            raise RecoveryError(f"database.{key} is required in {config_path}")
    return database


def _connection_args(database: dict[str, Any]) -> list[str]:
    args = [
        "--host",
        str(database.get("host", "127.0.0.1")),
        "--port",
        str(database.get("port", 3306)),
        "--user",
        str(database["user"]),
    ]
    password = str(database.get("password", ""))
    if password:
        args.append(f"--password={password}")
    return args


def _run(command: list[str], *, stdin: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RecoveryError(f"database executable was not found: {command[0]}") from exc

    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        if not message:
            message = completed.stdout.decode("utf-8", errors="replace").strip()
        raise RecoveryError(f"database command failed: {command[0]}: {message}")
    return completed


def capture_snapshot(config_path: Path, snapshot_path: Path, metadata_path: Path) -> None:
    database = _load_database_config(config_path)
    mysqldump = str(database.get("mysqldump") or "mysqldump")
    command = [
        mysqldump,
        *_connection_args(database),
        "--default-character-set=utf8",
        "--routines",
        "--triggers",
        "--events",
        "--add-drop-database",
        "--databases",
        str(database["database"]),
    ]
    if bool(database.get("single_transaction", False)):
        command.append("--single-transaction")

    completed = _run(command)
    if not completed.stdout.strip():
        raise RecoveryError("mysqldump produced an empty snapshot; refusing to overwrite baseline")

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_bytes(completed.stdout)
    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.resolve()),
        "snapshot": str(snapshot_path.resolve()),
        "database": {
            "driver": "mysql",
            "host": database.get("host"),
            "port": database.get("port"),
            "database": database.get("database"),
            "user": database.get("user"),
        },
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def restore_snapshot(config_path: Path, snapshot_path: Path) -> None:
    database = _load_database_config(config_path)
    if not snapshot_path.is_file():
        raise RecoveryError(
            f"baseline snapshot does not exist: {snapshot_path}\n"
            "Run this first to record the current WackoPicko database:\n"
            f"  python {Path(__file__).name} --capture"
        )
    sql = snapshot_path.read_bytes()
    if not sql.strip():
        raise RecoveryError(f"baseline snapshot is empty: {snapshot_path}")

    mysql = str(database.get("mysql") or "mysql")
    command = [
        mysql,
        *_connection_args(database),
        "--default-character-set=utf8",
    ]
    _run(command, stdin=sql)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture or restore the WackoPicko MySQL database. "
            "Default action is restore, so the web application database returns to the recorded baseline."
        )
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--capture",
        action="store_true",
        help="Record the current WackoPicko database as the reusable baseline snapshot.",
    )
    action.add_argument(
        "--restore",
        action="store_true",
        help="Restore the WackoPicko database from the recorded baseline snapshot. This is the default action.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Path to DRHL config JSON. Default: {DEFAULT_CONFIG}",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_SNAPSHOT,
        help=f"Path to the baseline SQL snapshot. Default: {DEFAULT_SNAPSHOT}",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    config_path = args.config.resolve()
    snapshot_path = args.snapshot.resolve()
    metadata_path = snapshot_path.with_suffix(".metadata.json")

    try:
        if args.capture:
            capture_snapshot(config_path, snapshot_path, metadata_path)
            print(f"[database_recovery] captured baseline: {snapshot_path}")
            print(f"[database_recovery] metadata: {metadata_path}")
        else:
            restore_snapshot(config_path, snapshot_path)
            print(f"[database_recovery] restored database from baseline: {snapshot_path}")
    except RecoveryError as exc:
        print(f"[database_recovery] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
