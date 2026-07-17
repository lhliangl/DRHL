from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "djangoblog.json"
DEFAULT_SNAPSHOT = Path(__file__).resolve().parent / "djangoblog" / "djangoblog_baseline.sqlite3"


class RecoveryError(RuntimeError):
    pass


def _run_config_command(database: dict[str, Any], *names: str) -> None:
    value: Any = None
    selected = names[0]
    for name in names:
        if database.get(name):
            value = database.get(name)
            selected = name
            break
    if not value:
        return
    command = value
    cwd = None
    timeout = None
    if isinstance(value, dict):
        command = value.get("command") or value.get("args")
        cwd = value.get("cwd")
        timeout = value.get("timeout")
    if not isinstance(command, list) or not command:
        raise RecoveryError(f"database.{selected} must be a non-empty argument list or command object")
    try:
        completed = subprocess.run(
            [str(item) for item in command],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=float(timeout) if timeout else None,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RecoveryError(f"hook executable was not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RecoveryError(f"database.{selected} timed out after {timeout}s") from exc
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "").strip()
        raise RecoveryError(f"database.{selected} failed with exit code {completed.returncode}: {message}")
    output = (completed.stdout or "").strip()
    if output:
        print(output)


def _load_database_config(config_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RecoveryError(f"configuration file was not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise RecoveryError(f"configuration file is not valid JSON: {config_path}: {exc}") from exc

    database = dict(data.get("database") or {})
    if database.get("driver") != "sqlite":
        raise RecoveryError("this recovery script supports only database.driver=sqlite")
    if not database.get("path"):
        raise RecoveryError(f"database.path is required in {config_path}")
    database["path"] = str(Path(str(database["path"])).expanduser().resolve())
    return database


def capture_snapshot(config_path: Path, snapshot_path: Path, metadata_path: Path) -> None:
    database = _load_database_config(config_path)
    source = Path(str(database["path"])).resolve()
    if not source.is_file():
        raise RecoveryError(f"SQLite database does not exist: {source}")
    if source.stat().st_size == 0:
        raise RecoveryError(f"SQLite database is empty; refusing to capture baseline: {source}")

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = snapshot_path.with_suffix(snapshot_path.suffix + ".tmp")
    shutil.copy2(source, temporary)
    temporary.replace(snapshot_path)
    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.resolve()),
        "snapshot": str(snapshot_path.resolve()),
        "database": {
            "driver": "sqlite",
            "path": str(source),
        },
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def restore_snapshot(config_path: Path, snapshot_path: Path) -> None:
    database = _load_database_config(config_path)
    target = Path(str(database["path"])).resolve()
    if not snapshot_path.is_file():
        raise RecoveryError(
            f"baseline snapshot does not exist: {snapshot_path}\n"
            "Run this first to record the current DjangoBlog SQLite database:\n"
            f"  python {Path(__file__).name} --capture"
        )
    if snapshot_path.stat().st_size == 0:
        raise RecoveryError(f"baseline snapshot is empty: {snapshot_path}")

    _run_config_command(database, "before_restore_command", "pre_restore_command")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f"{target.name}.{os.getpid()}.{time.time_ns()}.drhl-restore")
        shutil.copy2(snapshot_path, temporary)
        temporary.replace(target)
    finally:
        _run_config_command(database, "after_restore_command", "post_restore_command")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture or restore the DjangoBlog SQLite database. "
            "Default action is restore, so db.sqlite3 returns to the recorded baseline."
        )
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--capture",
        action="store_true",
        help="Record the current DjangoBlog db.sqlite3 as the reusable baseline snapshot.",
    )
    action.add_argument(
        "--restore",
        action="store_true",
        help="Restore db.sqlite3 from the recorded baseline snapshot. This is the default action.",
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
        help=f"Path to the baseline SQLite snapshot. Default: {DEFAULT_SNAPSHOT}",
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
