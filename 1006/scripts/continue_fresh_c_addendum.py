#!/usr/bin/env python3
"""Wait for Fresh C's technical gate, then execute its frozen addendum."""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
SCRIPTS = ROOT / "1006/scripts"
STATE_PATH = DATA / "FRESH_C_ADDENDUM_EXECUTION_STATE.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / "addendum_watcher.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = {"pid": os.getpid(), "stage": "WAIT_PRIMARY_INTEGRITY_GATE",
                 "started_utc": utc_now(), "steps": []}

        def save() -> None:
            state["updated_utc"] = utc_now()
            temporary = STATE_PATH.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(state, indent=2) + "\n")
            temporary.replace(STATE_PATH)

        save()
        try:
            gate_path = DATA / "FRESH_C_INTEGRITY_GATE.json"
            while not gate_path.exists():
                closure_path = DATA / "FRESH_C_CLOSURE_EXECUTION_STATE.json"
                if closure_path.exists():
                    closure = json.loads(closure_path.read_text())
                    if closure.get("stage") == "STOP_REQUIRES_RECORDED_REVIEW":
                        raise RuntimeError("primary Fresh C closure stopped; addendum will not run")
                time.sleep(15)
            gate = json.loads(gate_path.read_text())
            if gate.get("status") != "PASS":
                raise RuntimeError("primary Fresh C integrity gate failed; addendum will not run")

            for script, args in (
                ("launch_fresh_c_addendum.py", ()),
                ("audit_analyze_fresh_c_addendum.py", ("integrity",)),
                ("audit_analyze_fresh_c_addendum.py", ("analyze",)),
            ):
                state["stage"] = script + (":" + " ".join(args) if args else "")
                attempt = {"script": script, "args": list(args), "started_utc": utc_now()}
                state["steps"].append(attempt)
                save()
                result = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                                        cwd=ROOT, check=False)
                attempt["returncode"] = result.returncode
                attempt["finished_utc"] = utc_now()
                save()
                if result.returncode:
                    raise RuntimeError(f"addendum step failed: {script} {args}; preserve state and outputs")
            state["stage"] = "COMPLETE_ANALYZED"
        except Exception as exc:  # noqa: BLE001
            state["stage"] = "STOP_REQUIRES_RECORDED_REVIEW"
            state["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            save()


if __name__ == "__main__":
    main()
