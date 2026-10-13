#!/usr/bin/env python3
"""Run the pre-output Fresh C LLH/linear addendum in its own namespace."""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from fresh_c_input_embedding_gate import load_verified_input_embeddings

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
RUN = DATA / "runs/revision_era_addendum"
LOCK = ROOT / "1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.json"
GPU_LOCK = ROOT / "1006/data/scientific_gpu_campaign.lock"
CONDITIONS = ("layer_llh", "gen_linear")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def gpu_is_idle() -> bool:
    raw = subprocess.check_output([
        "nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
        "--format=csv,noheader,nounits"], text=True)
    rows = [list(map(int, row.split(","))) for row in raw.splitlines() if row.strip()]
    return len(rows) >= 2 and all(memory < 1024 and util <= 10 for memory, util in rows[:2])


def main() -> None:
    lock = json.loads(LOCK.read_text())
    embedding_manifest, embedding_manifest_hash = load_verified_input_embeddings()
    amendment = json.loads((ROOT / "1006/evidence/protocols/FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_20261006.json").read_text())
    if lock.get("status") != "FROZEN_PRE_OUTPUT":
        raise RuntimeError("addendum lock is not frozen")
    if amendment.get("original_addendum_lock_sha256") != sha256(LOCK):
        raise RuntimeError("input amendment does not bind the unchanged original addendum lock")
    if amendment.get("original_addendum_orchestration_hashes") != lock.get("orchestration_hashes"):
        raise RuntimeError("input amendment does not preserve the original orchestration hash record")
    if sha256(LOCK.with_suffix(".md")) != lock["protocol_markdown_sha256"]:
        raise RuntimeError("addendum protocol text differs from its machine lock")
    if sha256(ROOT / "1006/evidence/protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md") != lock["original_protocol_sha256"]:
        raise RuntimeError("original Fresh C protocol changed after the addendum lock")
    if sha256(DATA / "CANDIDATE_QUEUE_LOCK.json") != lock["candidate_queue_lock_sha256"]:
        raise RuntimeError("frozen Fresh C candidate queue changed after the addendum lock")
    primary_gate_path = DATA / "FRESH_C_INTEGRITY_GATE.json"
    if not primary_gate_path.is_file() or json.loads(primary_gate_path.read_text()).get("status") != "PASS":
        raise RuntimeError("primary four-condition Fresh C integrity gate must pass before addendum launch")
    primary_launch = json.loads((DATA / "runs/c3_confirmation/LAUNCH_IDENTITY.json").read_text())
    cohort_path = DATA / "FRESH_C_COHORT_MANIFEST.json"
    cohort = json.loads(cohort_path.read_text())
    uids_path = DATA / "fresh_c_objects.txt"
    uids = [line.strip() for line in uids_path.read_text().splitlines() if line.strip()]
    if cohort.get("selected_count") != len(uids) or len(set(uids)) != len(uids):
        raise RuntimeError("frozen cohort count/UID uniqueness mismatch")
    if len(uids) < 276 or len(uids) > 300:
        raise RuntimeError(f"cohort N outside frozen range: {len(uids)}")
    if primary_launch.get("cohort_uid_list_sha256") != sha256(uids_path):
        raise RuntimeError("primary launch and frozen UID list do not match")
    if primary_launch.get("cohort_manifest_sha256") != sha256(cohort_path):
        raise RuntimeError("primary launch and frozen cohort manifest do not match")
    if primary_launch.get("conditions") != ["no_adapter", "native_gfl", "native_gfh", "native_gc3"]:
        raise RuntimeError("primary launch conditions differ from the original lock")
    if primary_launch.get("input_embeddings_manifest_sha256") != embedding_manifest_hash:
        raise RuntimeError("primary run used a different precomputed embedding manifest")
    if embedding_manifest["cohort_n"] != len(uids):
        raise RuntimeError("embedding manifest does not cover the frozen addendum cohort")

    from launch_fresh_c_confirm import CHECKPOINT, CONFIG, EXPECTED, RUNNER
    if EXPECTED != lock["source_hashes"]:
        raise RuntimeError("primary source-hash registry differs from the addendum lock")
    source_paths = {
        "runner": RUNNER,
        "adapter_wrapper": ROOT / "MVPainter/mvpainter/model_unet_geotex.py",
        "data_utils": ROOT / "geotex/data_utils.py",
        "generation_logic": ROOT / "geotex/explore_contradiction.py",
        "metric_implementation": ROOT / "geotex/eval_exploration.py",
        "checkpoint": CHECKPOINT,
        "config": CONFIG,
    }
    actual_hashes = {key: sha256(path) for key, path in source_paths.items()}
    if actual_hashes != lock["source_hashes"]:
        raise RuntimeError("source/checkpoint/config changed after the addendum lock")

    identity_path = RUN / "LAUNCH_IDENTITY.json"
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "logs").mkdir(exist_ok=True)
    identity = {
        "protocol": lock["protocol_id"],
        "protocol_lock_sha256": sha256(LOCK),
        "protocol_markdown_sha256": sha256(LOCK.with_suffix(".md")),
        "primary_integrity_gate_sha256": sha256(primary_gate_path),
        "input_embeddings_manifest_sha256": embedding_manifest_hash,
        "cohort_manifest_sha256": sha256(cohort_path),
        "cohort_uid_list_sha256": sha256(uids_path),
        "cohort_n": len(uids),
        "conditions": list(CONDITIONS),
        "source_hashes": actual_hashes,
        "runner": str(RUNNER), "checkpoint": str(CHECKPOINT), "config": str(CONFIG),
        "data_root": str((DATA / "renders").resolve()),
        "two_gpu_shards": [0, 1], "num_shards": 2,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    if identity_path.exists():
        previous = json.loads(identity_path.read_text())
        for key, value in identity.items():
            if key not in {"created_at_utc", "primary_integrity_gate_sha256"} and previous.get(key) != value:
                raise RuntimeError(f"existing addendum namespace identity mismatch: {key}")
        identity = previous

    with GPU_LOCK.open("a") as gpu_lock:
        fcntl.flock(gpu_lock, fcntl.LOCK_EX)
        while not gpu_is_idle():
            time.sleep(15)
        atomic_json(identity_path, identity)
        processes, handles = [], []
        for shard, device in ((0, "cuda:0"), (1, "cuda:1")):
            env = os.environ.copy()
            env.update({
                "MVP_REPO_ROOT": str(ROOT), "MVP_CONFIG": str(CONFIG),
                "MVP_CHECKPOINT": str(CHECKPOINT), "MVP_OBJECT_LIST": str(uids_path),
                "MVP_DATA_ROOT": str((DATA / "renders").resolve()),
                "MVP_RUN_DIR": str(RUN), "MVP_CONDITIONS": ",".join(CONDITIONS),
                "MVP_DEVICE": device, "MVP_SHARD": str(shard), "MVP_NUM_SHARDS": "2",
                "MVP_SAVE_PREDICTED": "1", "MVP_SAVE_RESIDUAL": "1",
                "MVP_NUM_THREADS": "6", "OMP_NUM_THREADS": "6", "MKL_NUM_THREADS": "6",
                "PYTHONUNBUFFERED": "1",
            })
            handle = (RUN / "logs" / f"shard{shard}.log").open("ab")
            handles.append(handle)
            process = subprocess.Popen([sys.executable, str(RUNNER)], cwd=ROOT, env=env,
                                       stdout=handle, stderr=subprocess.STDOUT)
            processes.append((shard, device, process))
        identity["processes"] = [
            {"shard": shard, "device": device, "pid": process.pid}
            for shard, device, process in processes
        ]
        atomic_json(identity_path, identity)
        codes = [process.wait() for _, _, process in processes]
        for handle in handles:
            handle.close()
        identity["returncodes"] = codes
        identity["completed_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_json(identity_path, identity)
        if any(codes):
            raise RuntimeError(f"addendum runner failed; preserve outputs for audit: {codes}")
    print(json.dumps({"status": "RUNS_COMPLETE_AWAITING_INTEGRITY_AUDIT",
                      "run_dir": str(RUN), "n_objects": len(uids),
                      "expected_rows": len(uids) * 2, "returncodes": codes}, indent=2))


if __name__ == "__main__":
    main()
