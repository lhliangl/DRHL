"""Shared helpers for manual ground-truth verification of DRHL benchmark apps.

This module is intentionally read-only with respect to DRHL: it imports DRHL
classes (config loading, database snapshot/restore, detector sessions) but
never modifies DRHL code, configs, or run artifacts.

Database hygiene: before verifying an app we create a fresh baseline snapshot
in evidence/<app>/baseline.* using DRHL's own snapshot backend; after all
records of that app are verified we restore it, so the test database ends in
exactly the state it started from.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]  # DRHL repository root
AUDITS = Path(__file__).resolve().parent.parent  # ground_truth/audit (per-app subdirs)
sys.path.insert(0, str(ROOT))

from drhl.config import load_config  # noqa: E402
from drhl.database import create_snapshot  # noqa: E402
from drhl.analysis.detector import ActiveDetector  # noqa: E402


def app_evidence_dir(app: str) -> Path:
    """Directory holding the validation experiments for one application."""
    return AUDITS / app / "evidence"


def _mysql_bin(config: dict[str, Any], name: str, default: str) -> str:
    return str(config.get(name, default))


class DB:
    """Thin wrapper over the mysql CLI configured for an application.

    Every SQL statement executed through this wrapper (instrumentation
    INSERT/UPDATE/DELETE and before/after verification SELECTs) is appended to
    ``sql_log`` so it can be recorded in the evidence file."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.bin = _mysql_bin(config, "mysql", "mysql")
        self.sql_log: list[dict[str, str]] = []

    def _record_sql(self, kind: str, sql: str) -> None:
        self.sql_log.append({"kind": kind, "sql": sql})

    def drain_sql(self) -> list[dict[str, str]]:
        """Return and clear the accumulated SQL log."""
        log, self.sql_log = self.sql_log, []
        return log

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.config.get("password"):
            env["MYSQL_PWD"] = str(self.config["password"])
        return env

    def _args(self) -> list[str]:
        return [
            "--host", str(self.config.get("host", "127.0.0.1")),
            "--port", str(self.config.get("port", 3306)),
            "--user", str(self.config["user"]),
            "--protocol", "TCP",
        ]

    def _run(self, sql: str, batch: bool = True) -> subprocess.CompletedProcess:
        command = [self.bin, *self._args()]
        if batch:
            command += ["--batch", "--skip-column-names"]
        command += ["--database", str(self.config["database"]), "--execute", sql]
        return subprocess.run(command, capture_output=True, text=True, env=self._env(), timeout=120)

    def execute(self, sql: str) -> None:
        self._record_sql("execute", sql)
        completed = self._run(sql, batch=False)
        if completed.returncode != 0:
            raise RuntimeError(f"mysql execute failed: {completed.stderr.strip()[:500]}\nsql={sql[:300]}")

    def scalar(self, sql: str) -> str:
        self._record_sql("scalar", sql)
        completed = self._run(sql)
        if completed.returncode != 0:
            raise RuntimeError(f"mysql scalar failed: {completed.stderr.strip()[:500]}")
        return (completed.stdout or "").strip()

    def lines(self, sql: str) -> list[str]:
        self._record_sql("query", sql)
        completed = self._run(sql)
        if completed.returncode != 0:
            raise RuntimeError(f"mysql query failed: {completed.stderr.strip()[:500]}")
        return [line for line in (completed.stdout or "").splitlines() if line.strip()]

    def rows(self, sql: str) -> list[list[str]]:
        return [line.split("\t") for line in self.lines(sql)]

    def log_sql(self, kind: str, sql: str) -> None:
        """Record a SQL statement that was executed outside this wrapper."""
        self._record_sql(kind, sql)


def token(label: str, salt: int | None = None) -> str:
    stamp = int(time.time() * 1000) % 10**10 if salt is None else salt
    return f"DRHLGT_{label}_{stamp}"


class Recorder:
    """Accumulates verification steps for one ground-truth record and writes
    a self-contained evidence JSON under evidence/<app>/<gt_id>.json."""

    def __init__(self, app: str, gt_id: str, db: "DB | None" = None):
        self.app = app
        self.gt_id = gt_id
        self.steps: list[dict[str, Any]] = []
        self.db = db
        self.out_dir = app_evidence_dir(app)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def add(self, kind: str, detail: dict[str, Any]) -> None:
        self.steps.append({"kind": kind, **detail})

    def save_body(self, name: str, body: str, limit: int = 4000) -> str:
        path = self.out_dir / f"{self.gt_id}_{name}.html"
        path.write_text(body[:limit], encoding="utf-8", errors="replace")
        return str(path.relative_to(self.out_dir))

    def finish(self, verdict: str, summary: str) -> dict[str, Any]:
        result = {
            "gt_id": self.gt_id,
            "app": self.app,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verdict": verdict,  # vulnerable | not_confirmed | not_vulnerable
            "summary": summary,
            "sql_statements": self.db.drain_sql() if self.db is not None else [],
            "steps": self.steps,
        }
        write = app_evidence_dir(self.app) / f"{self.gt_id}.json"
        write.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result


def app_context(app: str) -> tuple[Any, Any, ActiveDetector, DB]:
    """Load DRHL config for *app* and build detector + DB handle."""
    config = load_config(ROOT / "configs" / f"{app}.json")
    snapshot = create_snapshot(config.database, app_evidence_dir(app))
    detector = ActiveDetector(config, snapshot)
    db = DB(config.database)
    return config, snapshot, detector, db


def run_record(snapshot: Any, fn, baseline: Path | None = None, db_config: dict[str, Any] | None = None) -> dict:
    """Run one GT record and restore the database baseline immediately after,
    so every single record leaves the database in its original state.

    When *baseline* and *db_config* are given, the restore is verified by
    re-dumping the database with DRHL's own snapshot backend and comparing
    with the baseline (ignoring dump-date lines)."""
    result = None
    try:
        result = fn()
    finally:
        snapshot.restore()
        if baseline is not None and db_config is not None and result is not None:
            result["restore_verified"] = db_matches(db_config, baseline)
    return result


def _dump_normalized(path: Path) -> str:
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        lowered = line.strip().casefold()
        if "dump completed on" in lowered or "dump completed at" in lowered:
            continue
        if lowered.startswith("-- host:") or lowered.startswith("-- server version"):
            continue
        # pg_dump 14 emits a per-dump random session token.
        if lowered.startswith("\\restrict ") or lowered.startswith("\\unrestrict "):
            continue
        lines.append(line)
    return "\n".join(lines)


def db_matches(db_config: dict[str, Any], baseline: Path) -> bool:
    """True when a fresh dump of the current database equals the baseline
    modulo timestamp lines. Uses DRHL's snapshot backend (read-only)."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory(prefix="drhl-verify-restore-") as tmp:
        fresh = create_snapshot(db_config, Path(tmp)).create()
        return _dump_normalized(fresh) == _dump_normalized(baseline)


def role_session(detector: ActiveDetector, role_name: str) -> Any:
    """Return a requests.Session logged in as *role_name* (None = visitor)."""
    role = next((r for r in detector.config.roles if r.name == role_name), None)
    return detector._session(role)


def role_for(detector: ActiveDetector, role_name: str) -> Any:
    """Return the RoleConfig for *role_name* (None when not found)."""
    return next((r for r in detector.config.roles if r.name == role_name), None)


def replay(detector: ActiveDetector, session: Any, page: str, spec: dict[str, Any],
           role: Any = None) -> dict[str, Any]:
    """Replay one request through DRHL's send pipeline; return a digest.

    *role* enables DRHL's runtime token injection (e.g. MyBB my_post_key)."""
    from drhl.models import RequestSpec

    request = RequestSpec(
        method=str(spec.get("method", "GET")).upper(),
        params=dict(spec.get("params", {})),
        referer=spec.get("referer"),
    )
    response = detector._send(session, page, request, role=role)
    body = str(response.text or "")
    headers = {k: v for k, v in response.headers.items()}
    return {
        "url": str(response.url),
        "status_code": int(response.status_code),
        "headers": headers,
        "body": body,
        "body_length": len(body),
    }


def close_session(session: Any) -> None:
    try:
        session.close()
    except Exception:
        pass


def page_contains(page_url: str, page_config: dict[str, Any] | None = None) -> bool:
    """True when the current content belongs to the configured login page."""
    del page_url, page_config
    return False


def set_cookie(session: Any, name: str, value: str, domain: str | None = None, path: str = "/") -> None:
    # Host-only cookie: requests/urllib3 does not reliably send cookies that
    # carry an explicit domain of "localhost", so omit the domain attribute.
    if domain:
        session.cookies.set(name, value, domain=domain, path=path)
    else:
        session.cookies.set(name, value, path=path)
