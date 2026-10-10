#!/usr/bin/env python3
"""Continue the unchanged Fresh C protocol after its existing render process.

Preserves the locked renderer and reserve sequence; analysis is gated by full
integrity. Uses the same GPU lease as E6, so the campaigns cannot overlap.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "1006/data/fresh_c"
SCRIPTS = ROOT / "1006/scripts"
HOTFIX_PATH = ROOT / "1006/evidence/protocols/FRESH_C_CLOSURE_RESUME_HOTFIX_20261006.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def alive(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().split()
        return stat[2] != "Z"
    except FileNotFoundError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-pid", type=int, help="Recorded same-protocol recovery process; only needed for legacy stage identities without PID")
    parser.add_argument("--resume-frozen-cohort", action="store_true",
                        help="Resume only from the already frozen cohort after a documented pre-output technical stop")
    args = parser.parse_args()
    hotfix = json.loads(HOTFIX_PATH.read_text())
    if hotfix.get("status") != "FROZEN_PRE_INFERENCE_RESUME_DRIVER":
        raise RuntimeError("resume-driver hotfix is not frozen")
    if sha256(HOTFIX_PATH.with_suffix(".md")) != hotfix.get("hotfix_markdown_sha256"):
        raise RuntimeError("resume-driver hotfix document hash mismatch")
    if sha256(Path(__file__)) != hotfix.get("resume_driver_sha256"):
        raise RuntimeError("resume driver differs from its frozen hotfix hash")
    if sha256(SCRIPTS / "continue_fresh_c_closure.py") != hotfix.get("parent_closure_driver_sha256"):
        raise RuntimeError("original closure driver changed after the recorded stop")
    from fresh_c_input_embedding_gate import load_verified_input_embeddings
    _, active_embedding_manifest_hash = load_verified_input_embeddings()
    if active_embedding_manifest_hash != hotfix.get("input_embeddings_manifest_sha256"):
        raise RuntimeError("resume driver is bound to a different input-embedding manifest")
    with (DATA / "closure_driver.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        old_state_path = DATA / "FRESH_C_CLOSURE_EXECUTION_STATE.json"
        old_state_bytes = old_state_path.read_bytes() if old_state_path.exists() else None
        old_state = json.loads(old_state_path.read_text()) if old_state_path.exists() else None
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

        if not args.resume_frozen_cohort:
            save()
        try:
            if args.resume_frozen_cohort:
                if old_state is None or old_state.get("stage") != "STOP_REQUIRES_RECORDED_REVIEW":
                    raise RuntimeError("frozen-cohort resume requires a recorded pre-output STOP state")
                prior_resume_failure = json.loads((DATA / "FRESH_C_CLOSURE_RESUME_ATTEMPT1_20261006.json").read_text())
                if old_state.get("error") != prior_resume_failure.get("closure_state", {}).get("error"):
                    raise RuntimeError("current STOP state differs from the recorded resume-driver failure")
                first_failure = json.loads((DATA / "FRESH_C_TECHNICAL_SMOKE_FAILURE_20261006.json").read_text())
                if first_failure.get("status") != "RECORDED_PREINFERENCE_TECHNICAL_FAILURE" or \
                        first_failure.get("execution_state", {}).get("error") != "two-object technical smoke failed: [1, 1]":
                    raise RuntimeError("original two-object smoke failure record is missing or inconsistent")
                prior_bytes = old_state_bytes or b""
                failed_path = DATA / "FRESH_C_CLOSURE_FAILED_ATTEMPT3.json"
                if failed_path.exists():
                    raise RuntimeError("failed-attempt archive already exists; refusing to overwrite it")
                smoke_logs = [DATA / "runs/technical_smoke" / f"shard{shard}.log" for shard in (0, 1)]
                archive = {
                    "original_smoke_failure_record_sha256": sha256(DATA / "FRESH_C_TECHNICAL_SMOKE_FAILURE_20261006.json"),
                    "original_smoke_failure_state": first_failure["execution_state"],
                    "resume_driver_failure_record_sha256": sha256(DATA / "FRESH_C_CLOSURE_RESUME_ATTEMPT1_20261006.json"),
                    "resume_driver_failure_state": old_state,
                    "resume_driver_failure_state_sha256": hashlib.sha256(prior_bytes).hexdigest(),
                    "smoke_logs": {path.name: sha256(path) for path in smoke_logs if path.is_file()},
                    "failed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "method_outputs_exist": False,
                }
                failed_path.write_text(json.dumps(archive, indent=2) + "\n")
                cohort = json.loads((DATA / "FRESH_C_COHORT_MANIFEST.json").read_text())
                audit = json.loads((DATA / "FRESH_C_COHORT_AUDIT.json").read_text())
                if cohort.get("status") not in {"FROZEN_FRESH_C_300", "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET"}:
                    raise RuntimeError("resume requires the existing frozen Fresh C cohort")
                if audit.get("method_outputs_exist") is not False or audit.get("selected_n") != cohort.get("selected_count"):
                    raise RuntimeError("cohort audit does not certify the frozen pre-output cohort")
                for run_name in ("c3_confirmation", "revision_era_addendum"):
                    method_run = DATA / "runs" / run_name
                    if method_run.exists() and any(method_run.glob("rows_shard*.json")):
                        raise RuntimeError(f"method rows already exist in {method_run}")
                    if method_run.exists() and any(method_run.glob("run_manifest_shard*.json")):
                        raise RuntimeError(f"method run manifests already exist in {method_run}")
                from fresh_c_input_embedding_gate import load_verified_input_embeddings
                embedding_manifest, embedding_hash = load_verified_input_embeddings()
                if embedding_manifest.get("cohort_n") != cohort.get("selected_count"):
                    raise RuntimeError("precomputed inputs do not cover the frozen cohort")
                state.update({"stage": "RESUME_FROZEN_COHORT_PREINFERENCE_REMEDIATION",
                              "resumed_from_state_sha256": archive["resume_driver_failure_state_sha256"],
                              "originating_smoke_failure_record_sha256": archive["original_smoke_failure_record_sha256"],
                              "resume_driver_sha256": hotfix["resume_driver_sha256"],
                              "resume_hotfix_sha256": sha256(HOTFIX_PATH),
                              "failed_attempt_archive": str(failed_path),
                              "input_embeddings_manifest_sha256": embedding_hash})
                save()
            else:
                identity = json.loads((DATA / "FRESH_C_RENDER_STAGE_IDENTITY.json").read_text())
                render_pid = args.render_pid or identity["stages"][-1].get("process_pid")
                if render_pid is None:
                    raise RuntimeError("render stage lacks PID; supply the recorded recovery --render-pid")
                if args.render_pid:
                    command = Path(f"/proc/{render_pid}/cmdline").read_bytes().replace(b"\x00", b" ")
                    if b"prepare_fresh_c_pool.py render" not in command:
                        raise RuntimeError("recovery PID does not identify the original render command")
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
                from launch_fresh_c_confirm import EXPECTED
                from run_e5_residual_dose import source_hashes
                actual = source_hashes()
                if {k: actual[k] for k in EXPECTED} != EXPECTED:
                    raise RuntimeError("pre-smoke frozen source mismatch")
                smoke = DATA / "runs/technical_smoke_retry1" if args.resume_frozen_cohort else DATA / "runs/technical_smoke"
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
                        "input_embeddings_manifest_sha256": embedding_hash if args.resume_frozen_cohort else None,
                        "retry_directory": str(smoke),
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
                old_addendum_state = DATA / "FRESH_C_ADDENDUM_EXECUTION_STATE.json"
                if old_addendum_state.exists():
                    failed_addendum = DATA / "FRESH_C_ADDENDUM_FAILED_ATTEMPT1.json"
                    if not failed_addendum.exists():
                        failed_addendum.write_bytes(old_addendum_state.read_bytes())
                watcher_log = DATA / "addendum_watcher_retry1.log"
                with watcher_log.open("ab") as watcher_out:
                    watcher = subprocess.Popen([sys.executable, str(SCRIPTS / "continue_fresh_c_addendum.py")],
                                               cwd=ROOT, stdout=watcher_out, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                state["addendum_watcher_pid"] = watcher.pid
                state["stage"] = "WAIT_REVISION_ERA_ADDENDUM"
                save()
                addendum_state_path = DATA / "FRESH_C_ADDENDUM_EXECUTION_STATE.json"
                while True:
                    if addendum_state_path.exists():
                        addendum_state = json.loads(addendum_state_path.read_text())
                        if addendum_state.get("pid") == watcher.pid and addendum_state.get("stage") == "COMPLETE_ANALYZED":
                            break
                        if addendum_state.get("pid") == watcher.pid and addendum_state.get("stage") == "STOP_REQUIRES_RECORDED_REVIEW":
                            raise RuntimeError(f"Fresh C addendum stopped: {addendum_state.get('error')}")
                    if not alive(watcher.pid):
                        raise RuntimeError("addendum watcher exited before completion; preserve its state/log")
                    time.sleep(15)
            state["stage"] = "COMPLETE_BOUNDED_C3_CONFIRMATION"
        except Exception as exc:
            state.update(stage="STOP_REQUIRES_RECORDED_REVIEW", error=str(exc))
            raise
        finally:
            save()


if __name__ == "__main__":
    main()
