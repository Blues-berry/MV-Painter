#!/usr/bin/env python3
"""Launch the frozen E5 development-only pilot on two idle GPUs."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/e5_residual_dose"
RUN = DATA / "runs"
PILOT = ROOT / "1006/scripts/run_e5_residual_dose.py"
AUDITOR = ROOT / "1006/scripts/audit_e5_residual_dose.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lock_path = DATA / "E5_LOCK.json"
    lock = json.loads(lock_path.read_text())
    if lock["pilot_script_sha256"] != sha256(PILOT) or lock["audit_script_sha256"] != sha256(AUDITOR):
        raise RuntimeError("pilot/auditor changed after E5 lock")
    if lock["launcher_script_sha256"] != sha256(Path(__file__).resolve()):
        raise RuntimeError("launcher changed after E5 lock")
    if lock["protocol_sha256"] != sha256(ROOT / "1006/evidence/protocols/E5_RESIDUAL_DOSE_FEASIBILITY_PROTOCOL_20261006.md"):
        raise RuntimeError("E5 protocol changed after lock")
    if any((RUN / name).exists() for name in ("rows_shard0.json", "rows_shard1.json")):
        raise RuntimeError("E5 output ledger already exists")
    query = subprocess.run([
        "nvidia-smi", "--query-gpu=index,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits"], check=True, capture_output=True, text=True)
    rows = [line.strip() for line in query.stdout.splitlines() if line.strip()]
    if len(rows) < 2:
        raise RuntimeError(f"two GPUs required: {rows}")
    parsed = [list(map(float, row.split(","))) for row in rows[:2]]
    if any(row[2] > 1024 or row[3] > 10 for row in parsed):
        raise RuntimeError(f"GPUs are not idle enough: {rows[:2]}")
    RUN.mkdir(parents=True, exist_ok=True)
    logs = RUN / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    identity = {
        "status": "running", "locked_at_utc": lock["locked_at_utc"],
        "lock_sha256": sha256(lock_path), "protocol_sha256": lock["protocol_sha256"],
        "pilot_script_sha256": lock["pilot_script_sha256"],
        "audit_script_sha256": lock["audit_script_sha256"],
        "gpus": rows[:2], "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "expected_generations": 174, "processes": [],
    }
    procs = []
    for shard, device in ((0, 0), (1, 1)):
        log_path = logs / f"shard{shard}.log"
        handle = log_path.open("ab")
        proc = subprocess.Popen(
            [sys.executable, str(PILOT), "--shard", str(shard), "--device", str(device)],
            cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        procs.append((shard, proc, handle, log_path))
        identity["processes"].append({"shard": shard, "device": f"cuda:{device}",
                                      "pid": proc.pid, "log": str(log_path)})
    identity_path = RUN / "LAUNCH_IDENTITY.json"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")
    print(json.dumps({"status": "launched", "identity": str(identity_path),
                      "processes": identity["processes"]}, indent=2), flush=True)
    returncodes = {}
    try:
        while any(proc.poll() is None for _, proc, _, _ in procs):
            for shard, proc, _, _ in procs:
                returncodes[str(shard)] = proc.poll()
            time.sleep(10)
    finally:
        for _, _, handle, _ in procs:
            handle.close()
    returncodes = {str(shard): proc.wait() for shard, proc, _, _ in procs}
    identity["process_returncodes"] = returncodes
    identity["finished_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    identity["status"] = "shards_complete" if all(v == 0 for v in returncodes.values()) else "shard_failure"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")
    print(json.dumps({"status": identity["status"], "returncodes": returncodes}, indent=2), flush=True)
    if identity["status"] != "shards_complete":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
