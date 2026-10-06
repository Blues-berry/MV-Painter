#!/usr/bin/env python3
"""Finish the fixed E6 stages; no independent confirmation launched here."""
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "1006/data/e6_cap_calibration"
SCRIPT = ROOT / "1006/scripts/run_e6_cap_calibration.py"


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / "driver.lock").open("w") as driver_lock:
        fcntl.flock(driver_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        gpu_lock = (ROOT / "1006/data/scientific_gpu_campaign.lock").open("w")
        fcntl.flock(gpu_lock, fcntl.LOCK_EX)
        status = {"stage": "WAITING_FOR_IDLE_GPUS", "pid": os.getpid(),
                  "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "attempts": []}

        def save():
            temporary = DATA / "E6_EXECUTION_STATE.json.tmp"
            temporary.write_text(json.dumps(status, indent=2)+"\n")
            temporary.replace(DATA / "E6_EXECUTION_STATE.json")

        save()
        while True:
            query = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True)
            gpus = [list(map(int, row.split(","))) for row in query.splitlines()]
            if len(gpus) >= 2 and all(memory < 1024 and utilization <= 10 for memory, utilization in gpus[:2]):
                break
            time.sleep(10)
        try:
            for stage, reduction in (("calibrate", "summarize-calibration"), ("technical", "audit-technical"), ("develop", "analyze-development")):
                status["stage"] = stage
                save()
                processes, handles = [], []
                for shard in (0, 1):
                    logfile = DATA / f"{stage}_shard{shard}.log"
                    handle = logfile.open("ab")
                    handles.append(handle)
                    processes.append(subprocess.Popen([sys.executable, str(SCRIPT), stage,
                        "--shard", str(shard), "--device", str(shard)], cwd=ROOT,
                        env={**os.environ, "PYTHONUNBUFFERED": "1"}, stdout=handle, stderr=subprocess.STDOUT))
                status["worker_pids"] = [p.pid for p in processes]
                save()
                codes = [p.wait() for p in processes]
                for handle in handles:
                    handle.close()
                status["attempts"].append({"stage": stage, "returncodes": codes})
                if any(codes):
                    raise RuntimeError(f"{stage} worker failed: {codes}; do not retune the frozen candidate")
                subprocess.run([sys.executable, str(SCRIPT), reduction], cwd=ROOT, check=True)
            status["stage"] = "DEVELOPMENT_COMPLETE_REVIEW_REQUIRED"
        except Exception as exc:
            status["stage"] = "STOP_REQUIRES_RECORDED_REVIEW"
            status["error"] = str(exc)
            raise
        finally:
            status["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
            save()
            gpu_lock.close()


if __name__ == "__main__":
    main()
