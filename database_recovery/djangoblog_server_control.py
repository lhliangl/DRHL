from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APP_ROOT = Path("D:/project/python/DjangoBlog")
DEFAULT_PYTHON = Path("D:/Anaconda3/envs/django/python.exe")
DEFAULT_LOG_DIR = ROOT / "database_recovery" / "djangoblog"


def _ps_quote(value: str | Path) -> str:
    text = str(value).replace("'", "''")
    return f"'{text}'"


def _listening_pids(port: int) -> set[int]:
    try:
        completed = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return set()
    pids: set[int] = set()
    marker = f":{port}"
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        local_address = parts[1]
        state = parts[3].upper()
        pid = parts[-1]
        if marker in local_address and state == "LISTENING" and pid.isdigit():
            pids.add(int(pid))
    return pids


def _is_up(url: str, timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 100 <= int(response.status) < 600
    except Exception:
        return False


def stop_server(port: int, wait_seconds: float) -> None:
    pids = _listening_pids(port)
    if not pids:
        print(f"[djangoblog_server] no process is listening on port {port}")
        return
    failed: list[str] = []
    for pid in sorted(pids):
        if pid == os.getpid():
            continue
        completed = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            print(f"[djangoblog_server] stopped PID {pid}")
        else:
            message = (completed.stderr or completed.stdout or f"taskkill exited with {completed.returncode}").strip()
            failed.append(f"PID {pid}: {message}")
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        remaining = _listening_pids(port)
        if not remaining:
            return
        time.sleep(0.25)
    remaining = sorted(_listening_pids(port))
    detail = "; ".join(failed) if failed else f"still listening: {remaining}"
    raise SystemExit(f"[djangoblog_server] failed to stop server on port {port}: {detail}")


def start_server(
    app_root: Path,
    python_binary: Path,
    host: str,
    port: int,
    wait_seconds: float,
    log_dir: Path,
) -> None:
    url = f"http://{host}:{port}/"
    if _is_up(url):
        print(f"[djangoblog_server] already running: {url}")
        return
    if not app_root.is_dir():
        raise SystemExit(f"[djangoblog_server] app root does not exist: {app_root}")
    if not python_binary.is_file():
        raise SystemExit(f"[djangoblog_server] python binary does not exist: {python_binary}")
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / "runserver.stdout.log"
    stderr_path = log_dir / "runserver.stderr.log"
    command = [
        str(python_binary),
        "-m",
        "coverage",
        "run",
        "--source=.",
        "manage.py",
        "runserver",
        "--noreload",
        f"{host}:{port}",
    ]
    process = None
    if os.name == "nt":
        args = ["-m", "coverage", "run", "--source=.", "manage.py", "runserver", "--noreload", f"{host}:{port}"]
        ps_args = "@(" + ",".join(_ps_quote(item) for item in args) + ")"
        ps_command = (
            "$p = Start-Process "
            f"-FilePath {_ps_quote(python_binary)} "
            f"-ArgumentList {ps_args} "
            f"-WorkingDirectory {_ps_quote(app_root)} "
            "-WindowStyle Hidden -PassThru; "
            "$p.Id"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit((completed.stderr or completed.stdout or "PowerShell Start-Process failed").strip())
        pid_text = (completed.stdout or "").strip().splitlines()[-1] if completed.stdout.strip() else "unknown"
        (log_dir / "runserver.pid").write_text(str(pid_text), encoding="utf-8")
        print(f"[djangoblog_server] started PID {pid_text}: {url}")
    else:
        with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
            process = subprocess.Popen(
                command,
                cwd=str(app_root),
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                close_fds=True,
            )
        (log_dir / "runserver.pid").write_text(str(process.pid), encoding="utf-8")
        print(f"[djangoblog_server] started PID {process.pid}: {url}")
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if _is_up(url):
            print(f"[djangoblog_server] ready: {url}")
            return
        if process is not None and process.poll() is not None:
            raise SystemExit(
                f"[djangoblog_server] runserver exited early with code {process.returncode}; "
                f"see {stderr_path}"
            )
        time.sleep(0.5)
    raise SystemExit(f"[djangoblog_server] timed out waiting for {url}; see {stderr_path}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stop/start the DjangoBlog development server for SQLite restore safety.")
    parser.add_argument("action", choices=["stop", "start", "restart"])
    parser.add_argument("--app-root", type=Path, default=DEFAULT_APP_ROOT)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--wait", type=float, default=20.0)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.action in {"stop", "restart"}:
            stop_server(args.port, args.wait)
        if args.action in {"start", "restart"}:
            start_server(args.app_root.resolve(), args.python.resolve(), args.host, args.port, args.wait, args.log_dir.resolve())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[djangoblog_server] ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
