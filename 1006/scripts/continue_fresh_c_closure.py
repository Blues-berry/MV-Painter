#!/usr/bin/env python3
"""Continue the unchanged Fresh C protocol after its existing render process.

Preserves the locked renderer and reserve sequence; analysis is gated by full
integrity. Uses the same GPU lease as E6, so the campaigns cannot overlap.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "1006/data/fresh_c"
SCRIPTS = ROOT / "1006/scripts"


def alive(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().split()
        return stat[2] != "Z"
    except FileNotFoundError:
        return False


def main():
    with (DATA / "closure_driver.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = {"pid": os.getpid(), "stage": "WAIT_EXISTING_RENDER",
                 "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "steps": []}

        def save():
            state["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
            temp = DATA / "FRESH_C_CLOSURE_EXECUTION_STATE.json.tmp"
            temp.write_text(json.dumps(state, indent=2)+"\n")
            temp.replace(DATA / "FRESH_C_CLOSURE_EXECUTION_STATE.json")

        def run(script, *args):
            state["stage"] = script + ":" + " ".join(args)
            save()
            attempt = {"command": [script, *args], "started_utc": state["updated_utc"]}
            state["steps"].append(attempt)
            save()
            proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=ROOT)
            attempt["returncode"] = proc.returncode
            save()
            if proc.returncode:
                raise RuntimeError(f"stage failed without changing protocol: {script} {args}")

        save()
        try:
            identity = json.loads((DATA / "FRESH_C_RENDER_STAGE_IDENTITY.json").read_text())
            render_pid = identity["stages"][-1]["process_pid"]
            while not (DATA / "render_log_600.json").exists():
                if not alive(render_pid):
                    raise RuntimeError("existing renderer exited before final log; preserve failed attempt")
                time.sleep(10)
            run("prepare_fresh_c_pool.py", "depth")
            run("prepare_fresh_c_pool.py", "freeze")
            while True:
                audit = json.loads((DATA / "FRESH_C_COHORT_AUDIT.json").read_text())
                if audit["status"] != "RESERVE_BLOCK_REQUIRED":
                    break
                start = int(audit["reserve_next_rank"])
                if start not in (601, 801):
                    raise RuntimeError(f"reserve start outside frozen two-block sequence: {start}")
                run("download_fresh_c_assets.py", "--start-rank", str(start), "--count", "200", "--append")
                run("prepare_fresh_c_pool.py", "asset-audit")
                run("prepare_fresh_c_pool.py", "render")
                run("prepare_fresh_c_pool.py", "depth")
                run("prepare_fresh_c_pool.py", "freeze")
            if audit["selected_n"] < 276:
                raise RuntimeError("exhausted frozen candidate queue below technical minimum")
            state["stage"] = "WAIT_GPU_LEASE"
            save()
            with (ROOT / "1006/data/scientific_gpu_campaign.lock").open("w") as gpu_lock:
                fcntl.flock(gpu_lock, fcntl.LOCK_EX)
                while True:
                    query = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True)
                    gpus = [list(map(int, line.split(","))) for line in query.splitlines()]
                    if len(gpus) >= 2 and all(m < 1024 and u <= 10 for m, u in gpus[:2]):
                        break
                    time.sleep(10)
                # Two-object smoke: GFL only, no metrics, no prediction display.
                from launch_fresh_c_confirm import EXPECTED, sha256
                from run_e5_residual_dose import source_hashes
                actual = source_hashes()
                if {k: actual[k] for k in EXPECTED} != EXPECTED:
                    raise RuntimeError("pre-smoke frozen source mismatch")
                smoke = DATA / "runs/technical_smoke"
                state["stage"] = "TWO_OBJECT_TECHNICAL_SMOKE"
                save()
                smoke.mkdir(parents=True, exist_ok=True)
                from launch_fresh_c_confirm import CONFIG, CHECKPOINT, RUNNER
                processes, logs = [], []
                for shard in (0, 1):
                    env = {**os.environ, "MVP_REPO_ROOT": str(ROOT), "MVP_CONFIG": str(CONFIG),
                           "MVP_CHECKPOINT": str(CHECKPOINT), "MVP_OBJECT_LIST": str(DATA / "fresh_c_objects.txt"),
                           "MVP_DATA_ROOT": str(DATA / "renders"), "MVP_RUN_DIR": str(smoke),
                           "MVP_CONDITIONS": "native_gfl", "MVP_DEVICE": f"cuda:{shard}",
                           "MVP_SHARD": str(shard), "MVP_NUM_SHARDS": "2", "MVP_OBJECT_INDICES": "0,1",
                           "MVP_RESIDUALS_ONLY": "1", "MVP_SAVE_RESIDUAL": "1", "MVP_SAVE_PREDICTED": "0",
                           "MVP_NUM_THREADS": "6", "PYTHONUNBUFFERED": "1"}
                    log = (smoke / f"shard{shard}.log").open("ab")
                    logs.append(log)
                    processes.append(subprocess.Popen([sys.executable, str(RUNNER)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT))
                codes = [p.wait() for p in processes]
                for log in logs:
                    log.close()
                if any(codes):
                    raise RuntimeError(f"two-object technical smoke failed: {codes}")
                traces = list((smoke / "residual_logs/native_gfl").glob("*.json"))
                if len(traces) != 2:
                    raise RuntimeError("technical smoke did not preserve two residual outputs")
                gate = {"status": "PASS", "two_objects": 2, "quality_metrics_inspected": False,
                        "source_hashes": {k: actual[k] for k in EXPECTED},
                        "trace_hashes": {p.name: sha256(p) for p in traces}}
                (DATA / "FRESH_C_TECHNICAL_SMOKE_GATE.json").write_text(json.dumps(gate, indent=2)+"\n")
                run("launch_fresh_c_confirm.py")
                campaign = DATA / "runs/c3_confirmation"
                launch = json.loads((campaign / "LAUNCH_IDENTITY.json").read_text())
                state["stage"] = "CONFIRMATION_RUNNING_NO_ANALYSIS"
                state["worker_pids"] = [p["pid"] for p in launch["processes"]]
                save()
                while not all((campaign / f"run_manifest_shard{s}.json").exists() for s in (0, 1)):
                    if not any(alive(pid) for pid in state["worker_pids"]):
                        raise RuntimeError("confirmation exited before both completion manifests")
                    time.sleep(10)
                run("audit_analyze_fresh_c.py", "integrity")
                run("audit_analyze_fresh_c.py", "analyze")
            state["stage"] = "COMPLETE_BOUNDED_C3_CONFIRMATION"
        except Exception as exc:
            state.update(stage="STOP_REQUIRES_RECORDED_REVIEW", error=str(exc))
            raise
        finally:
            save()


if __name__ == "__main__":
    main()
