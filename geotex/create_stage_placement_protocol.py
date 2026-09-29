"""Create the prespecified follow-up protocol for temporal scale placement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/STAGE_PLACEMENT_PROTOCOL.json"
OBJ = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
EVAL_MANIFEST = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/evaluation_manifest.json"
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    objects = [x.strip() for x in OBJ.read_text().splitlines() if x.strip()]
    protocol = {
        "protocol": "clean-v2-stage-placement-followup-v1",
        "status": "pre-specified follow-up mechanistic ablation; not blind",
        "reason": "follow-up to observed C3 versus fixed-low/fixed-high clean-v2 results",
        "checkpoint": {"path": str(CHECKPOINT), "sha256": sha256(CHECKPOINT), "step": 2000, "label": "controlled_retraining_checkpoint"},
        "dataset": {"list": str(OBJ), "sha256": sha256(OBJ), "count": len(objects), "object_ids": [f"obj_{i + 24:04d}" for i in range(len(objects))], "uids": objects},
        "evaluation": {"target_view_mode": "unique6", "target_views": [0, 15, 12, 16, 13, 14], "per_view_resolution": [256, 256], "panel_resolution": [768, 512], "seed": 42, "steps": 50, "gt": "same frozen GT and camera/mask pipeline as eval300_clean_v2_unique6", "evaluation_code": "/tmp/mv_main_rerun/geotex/eval_exploration.py", "baseline_runner": "geotex/round2_main_eval.py"},
        "stage_mapping": {"rule": "scheduler.timesteps index fraction: early frac<0.33, mid 0.33<=frac<0.66, late frac>=0.66", "steps_50": {"early_indices": list(range(0, 17)), "mid_indices": list(range(17, 33)), "late_indices": list(range(33, 50)), "early_count": 17, "mid_count": 16, "late_count": 17}, "important": "boundaries are timestep-list positions, not raw timestep numeric thresholds"},
        "conditions": {"fixed_mean": {"type": "global_scale", "scale": 5 / 3, "mean_scale": 5 / 3}, "hll": {"type": "timestep_schedule", "early": 2.5, "mid": 1.25, "late": 1.25, "mean_scale": 5 / 3}, "lhl_c3": {"type": "timestep_schedule", "early": 1.25, "mid": 2.5, "late": 1.25, "mean_scale": 5 / 3}, "llh": {"type": "timestep_schedule", "early": 1.25, "mid": 1.25, "late": 2.5, "mean_scale": 5 / 3}},
        "hypotheses": ["At equal mean scale, temporal placement changes metrics.", "Middle-high (LHL/C3) is not interchangeable with early-high (HLL) or late-high (LLH).", "Any C3 gain over fixed-low is not explained solely by avoiding a full-time 2.50 scale.", "Placement effects should be reported separately for global, foreground, edge and texture metrics."],
        "selection_policy": "No schedules or objects will be added/removed based on results; this 276-object strict holdout is fixed before the new run.",
        "resource_status": "formal inference pending CUDA resource handoff; dry-run is permitted on CPU",
    }
    OUT.write_text(json.dumps(protocol, indent=2) + "\n")
    print(json.dumps({"count": len(objects), "sha256": sha256(OBJ), "stage_mapping": protocol["stage_mapping"]["steps_50"]}, indent=2))


if __name__ == "__main__":
    main()
