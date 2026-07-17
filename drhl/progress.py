from __future__ import annotations

from datetime import datetime


def progress(message: str) -> None:
    """Print a timestamped progress line immediately, including in conda terminals."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[DRHL {timestamp}] {message}", flush=True)
