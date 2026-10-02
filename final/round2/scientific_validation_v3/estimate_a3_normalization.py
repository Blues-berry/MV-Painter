#!/usr/bin/env python3
"""A3 dose-normalization estimation on DEV objects (probe-24) ONLY.

Protocol (Experiment A3, MASTER_PROTOCOL_LOCK.md):
  * estimate baseline residual magnitudes from development/probe-24 objects
  * NO image-quality outcomes are read; only residual logs of a_baseline
  * choose per-layer high values so the expected integrated residual
    increment over a 10-step window is approximately equal across
    deep / middle / shallow
  * freeze a3_normalization.json BEFORE any FRESH_CONFIRM_N A3 run

Pre-registered rule (frozen here, before fresh-cohort evaluation):
  R_l,t     = sqrt(sum of squared per-wrapper l2 norms in group l at step t),
              averaged over probe objects (a_baseline run)
  M_l,w     = sum_{t in window w} R_l,t
  C         = 1.25 * mean_w M_deep,w        (deep keeps the frozen A2 delta)
  delta_l   = C / mean_w M_l,w
  high_l    = LOW_l + delta_l
  cap check: if high_l > native cap (deep 3.0 / middle 3.5 / shallow 0.8)
             for ANY layer, the WHOLE A3 map runs under the uncapped
             injection path (a3_baseline included, which is cap-inactive
             anyway) — recorded via "uncapped": true in the spec.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN_DIR = V3 / "a3_dev_baseline_probe24"
PROBE_LIST = ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
STEPS = 50
WINDOWS = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49)]
LOW = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
DEEP_A2_DELTA = 1.25
SEED = 20261002


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    run_marker = RUN_DIR / "run_manifest_shard0.json"
    if not run_marker.exists():
        env_cmd = (
            f"MVP_RUN_DIR={RUN_DIR} "
            f"MVP_OBJECT_LIST={PROBE_LIST} "
            f"MVP_DEVICE=cuda:1 "
            f"MVP_CONDITIONS=a_baseline "
            f"python3 scripts/run_validation_v3_experiment.py"
        )
        print("launching dev baseline run:", env_cmd)
        subprocess.run(["bash", "-c", env_cmd], cwd=ROOT, check=True)

    uids = [l.strip() for l in PROBE_LIST.open() if l.strip()]
    per_obj = {}  # obj -> {group: [R_l,t for 50 steps]}
    for uid in uids:
        log = json.loads((RUN_DIR / "residual_logs" / "a_baseline" / f"{uid}.json").read_text())
        table = {g: [0.0] * STEPS for g in LOW}
        for step_key, entries in log.items():
            s = int(step_key)
            sq = {}
            for e in entries.values():
                sq[e["depth"]] = sq.get(e["depth"], 0.0) + float(e["l2"]) ** 2
            for g, v in sq.items():
                table[g][s] = math.sqrt(v)
        per_obj[uid] = table

    # mean over objects
    R = {g: np.mean([per_obj[u][g] for u in uids], axis=0) for g in LOW}
    M = {g: [float(R[g][lo:hi + 1].sum()) for lo, hi in WINDOWS] for g in LOW}
    mean_M = {g: float(np.mean(M[g])) for g in LOW}
    C = DEEP_A2_DELTA * mean_M["deep"]
    deltas = {g: C / mean_M[g] for g in LOW}
    highs = {g: LOW[g] + deltas[g] for g in LOW}
    uncapped = any(highs[g] > CAPS[g] + 1e-9 for g in LOW)

    spec = {
        "rule": (
            "R_l,t=sqrt(sum sq l2 in group), mean over probe-24 a_baseline runs; "
            "M_l,w=sum over 10-step window; C=1.25*mean_w M_deep,w (deep keeps "
            "frozen A2 delta); delta_l=C/mean_w M_l,w; high_l=LOW_l+delta_l; "
            "if any high_l exceeds its native cap the whole A3 map runs uncapped"
        ),
        "dev_run_dir": str(RUN_DIR),
        "dev_run_manifest_sha256": sha256(run_marker),
        "probe_list_sha256": sha256(PROBE_LIST),
        "dev_object_count": len(uids),
        "window_M": M,
        "mean_M": mean_M,
        "C": C,
        "deltas": deltas,
        "high_values": highs,
        "native_caps": CAPS,
        "uncapped": uncapped,
        "frozen_before_fresh_evaluation": True,
        "seed": SEED,
    }
    out = V3 / "a3_normalization.json"
    out.write_text(json.dumps(spec, indent=2) + "\n")
    print(json.dumps({k: v for k, v in spec.items() if k != "window_M"}, indent=2))
    print(f"\nFROZEN -> {out}")
    print("achievable dose ratios (delta_l * mean_M_l / C):",
          {g: round(deltas[g] * mean_M[g] / C, 4) for g in LOW})


if __name__ == "__main__":
    sys.exit(main())
