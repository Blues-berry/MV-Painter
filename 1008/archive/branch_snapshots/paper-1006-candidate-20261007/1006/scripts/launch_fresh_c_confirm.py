#!/usr/bin/env python3
"""Launch the frozen Fresh C confirmation on the two verified GPU shards."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
RUN = DATA / "runs/c3_confirmation"
RUNNER = ROOT / "scripts/run_validation_v3_experiment.py"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
EXPECTED = {
    "runner": "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3",
    "adapter_wrapper": "b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0",
    "data_utils": "e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3",
    "generation_logic": "5da7fff22ea73b6d9500603d0905eda9a1ac9c44406346b259f3aba368b6ca13",
    "metric_implementation": "adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5",
    "checkpoint": "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0",
    "config": "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b",
}
CONDITIONS = "no_adapter,native_gfl,native_gfh,native_gc3"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    cohort_audit = json.loads((DATA / "FRESH_C_COHORT_AUDIT.json").read_text())
    cohort_manifest_path = DATA / "FRESH_C_COHORT_MANIFEST.json"
    cohort_manifest = json.loads(cohort_manifest_path.read_text())
    if cohort_manifest["status"] not in {
        "FROZEN_FRESH_C_300", "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET"
    }:
        raise RuntimeError(f"C cohort is not frozen for inference: {cohort_manifest['status']}")
    if cohort_manifest["selected_count"] < 276:
        raise RuntimeError("C cohort is below the frozen minimum N=276")
    if cohort_audit.get("method_outputs_exist") is not False:
        raise RuntimeError("cohort audit does not certify pre-inference freeze")

    paths = {
        "runner": RUNNER,
        "adapter_wrapper": ROOT / "MVPainter/mvpainter/model_unet_geotex.py",
        "data_utils": ROOT / "geotex/data_utils.py",
        "generation_logic": ROOT / "geotex/explore_contradiction.py",
        "metric_implementation": ROOT / "geotex/eval_exploration.py",
        "checkpoint": CHECKPOINT,
        "config": CONFIG,
    }
    actual = {key: sha256(path) for key, path in paths.items()}
    if actual != EXPECTED:
        raise RuntimeError(f"source/checkpoint/config hash mismatch: {actual}")
    object_list = DATA / "fresh_c_objects.txt"
    uids = [x.strip() for x in object_list.read_text().splitlines() if x.strip()]
    if len(uids) != cohort_manifest["selected_count"] or len(set(uids)) != len(uids):
        raise RuntimeError("frozen UID list count/uniqueness mismatch")
    object_rows = {r["uid"]: r for r in cohort_manifest["objects"]}
    for uid in uids:
        row = object_rows.get(uid)
        if row is None or sha256(Path(row["asset_path"])) != row["asset_sha256"]:
            raise RuntimeError(f"selected source GLB hash mismatch: {uid}")
        for view in ("000", "014", "012", "013", "015", "016"):
            image = Path(row["render_dir"]) / "image" / f"{view}.png"
            if not image.is_file():
                raise RuntimeError(f"missing frozen model input {uid}/{view}")

    gpu_query = subprocess.run([
        "nvidia-smi", "--query-gpu=index,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits"], check=True, capture_output=True, text=True)
    gpu_rows = [line.strip() for line in gpu_query.stdout.splitlines() if line.strip()]
    if len(gpu_rows) < 2:
        raise RuntimeError(f"two GPUs required, found {len(gpu_rows)}")
    parsed = [list(map(float, row.split(","))) for row in gpu_rows[:2]]
    if any(row[2] > 1024 or row[3] > 10 for row in parsed):
        raise RuntimeError(f"GPUs are not idle enough for the locked run: {gpu_rows[:2]}")

    RUN.mkdir(parents=True, exist_ok=True)
    log_dir = RUN / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    identity = {
        "protocol": "fresh_c3_confirmation_revision_era_v1",
        "cohort_manifest_sha256": sha256(cohort_manifest_path),
        "cohort_uid_list_sha256": sha256(object_list),
        "cohort_n": len(uids), "conditions": CONDITIONS.split(","),
        "source_hashes": actual,
        "runner": str(RUNNER), "checkpoint": str(CHECKPOINT), "config": str(CONFIG),
        "data_root": str((DATA / "renders").resolve()),
        "two_gpu_shards": [0, 1], "num_shards": 2,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    identity_path = RUN / "LAUNCH_IDENTITY.json"
    if identity_path.exists():
        old = json.loads(identity_path.read_text())
        for key in identity:
            if key == "created_at_utc":
                continue
            if old.get(key) != identity[key]:
                raise RuntimeError(f"resume identity mismatch at {key}")
        identity = old
    else:
        identity_path.write_text(json.dumps(identity, indent=2) + "\n")

    processes = []
    for shard, device in ((0, "cuda:0"), (1, "cuda:1")):
        env = os.environ.copy()
        env.update({
            "MVP_REPO_ROOT": str(ROOT), "MVP_CONFIG": str(CONFIG),
            "MVP_CHECKPOINT": str(CHECKPOINT), "MVP_OBJECT_LIST": str(object_list),
            "MVP_DATA_ROOT": str((DATA / "renders").resolve()),
            "MVP_RUN_DIR": str(RUN), "MVP_CONDITIONS": CONDITIONS,
            "MVP_DEVICE": device, "MVP_SHARD": str(shard), "MVP_NUM_SHARDS": "2",
            "MVP_SAVE_PREDICTED": "1", "MVP_SAVE_RESIDUAL": "1",
            "MVP_NUM_THREADS": "6", "OMP_NUM_THREADS": "6", "MKL_NUM_THREADS": "6",
        })
        log_path = log_dir / f"shard{shard}.log"
        log_handle = log_path.open("ab")
        proc = subprocess.Popen([os.sys.executable, str(RUNNER)], cwd=ROOT, env=env,
                                stdout=log_handle, stderr=subprocess.STDOUT)
        processes.append({"shard": shard, "device": device, "pid": proc.pid,
                          "log": str(log_path), "returncode": proc.poll()})
    identity["processes"] = processes
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")
    print(json.dumps({"status": "LAUNCHED", "run_dir": str(RUN),
                      "n_objects": len(uids), "expected_rows": len(uids) * 4,
                      "processes": processes}, indent=2))


if __name__ == "__main__":
    main()
