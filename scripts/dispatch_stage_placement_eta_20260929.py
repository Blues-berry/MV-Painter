#!/usr/bin/env python
"""Durable low-frequency dispatcher for the A-2 ETA acceptance gate.

It sleeps until the declared ETA, performs one acceptance check, and only if
the runner is still active waits for the next explicitly declared checkpoint.
It never reads intermediate records during the training window.
"""

from __future__ import annotations

import fcntl
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/stage_placement_276_20260929"
LOCK = OUT / ".eta_dispatcher.lock"
STATE = OUT / "eta_dispatch_status.json"
VALIDATOR = ROOT / "scripts/validate_stage_placement_276_20260929.py"
ETA = datetime(2026, 9, 29, 5, 45, 7, tzinfo=timezone.utc)
RECHECK_INTERVAL = timedelta(minutes=30)


def stamp(value: datetime | None = None) -> str:
    value = value or datetime.now(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def write_state(payload: dict[str, object]) -> None:
    temporary = STATE.with_suffix(STATE.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(STATE)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    lock_handle = LOCK.open("w")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 73
    write_state({"status": "waiting", "pid": __import__("os").getpid(), "eta": stamp(ETA), "updated_at": stamp()})
    checkpoint = ETA
    while True:
        delay = (checkpoint - datetime.now(timezone.utc)).total_seconds()
        if delay > 0:
            time.sleep(delay)
        write_state({"status": "checking", "pid": __import__("os").getpid(), "checkpoint": stamp(checkpoint), "updated_at": stamp()})
        result = subprocess.run([
            sys.executable,
            str(VALIDATOR),
        ], cwd=ROOT, check=False)
        if result.returncode != 2:
            write_state({"status": "terminal", "pid": __import__("os").getpid(), "checkpoint": stamp(checkpoint), "validator_exit_code": result.returncode, "updated_at": stamp()})
            return result.returncode
        checkpoint = datetime.now(timezone.utc) + RECHECK_INTERVAL
        write_state({"status": "waiting_for_next_checkpoint", "pid": __import__("os").getpid(), "next_checkpoint": stamp(checkpoint), "validator_exit_code": result.returncode, "updated_at": stamp()})


if __name__ == "__main__":
    raise SystemExit(main())
