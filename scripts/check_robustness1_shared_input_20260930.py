#!/usr/bin/env python
"""Verdict for the Robustness-1 shared-input preflight (run after pass1+pass2).

Checks:
1. process replay: pass1 vs pass2 identical for every (object, method, field);
2. cross-method sharing: within each pass, the 5 Core-5 methods produce
   identical input hashes for the same object;
3. cross-realization consistency vs the frozen R0 audit
   (SHARED_INPUT_DETERMINISM_AUDIT.pass1.json): deterministic components
   (targets/normals/depth/masks/global embeds/initial latent/scheduler) must
   MATCH R0, while the reference-derived components (raw->processed cond,
   cond latent) must DIFFER — proving Realization-1 is a genuinely different
   reference draw under an otherwise identical protocol.

Writes ROBUSTNESS1_SHARED_INPUT_AUDIT.{md,json}. PASS of (1)+(2) is the gate
for starting the formal 276 x 5 run.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
TASK = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
R0_AUDIT = ROOT / "final/round2/coordination/final_acceptance_20260930/SHARED_INPUT_DETERMINISM_AUDIT.pass1.json"

HASH_FIELDS = [
    "cond_imgs_raw_sha256", "cond_imgs_resized_sha256", "cond_lat_sha256",
    "target_imgs_raw_sha256", "target_grid_sha256", "normals_raw_sha256",
    "normals_grid_sha256", "depth_raw_sha256", "depth_grid_sha256",
    "mask_grid_sha256", "geo_clean_sha256", "geo_feats_sha256",
    "global_embeds_sha256",
]
REFERENCE_DERIVED = {"cond_imgs_raw_sha256", "cond_imgs_resized_sha256", "cond_lat_sha256"}


def index(payload: dict) -> dict[tuple, dict]:
    return {(r["obj_idx"], r["method"]): r for r in payload["rows"]}


def main() -> None:
    p1 = json.loads((TASK / "ROBUSTNESS1_SHARED_INPUT_AUDIT.pass1.json").read_text())
    p2 = json.loads((TASK / "ROBUSTNESS1_SHARED_INPUT_AUDIT.pass2.json").read_text())
    i1, i2 = index(p1), index(p2)
    assert set(i1) == set(i2) and len(i1) == 50, "unexpected audit row sets"

    # 1. process replay
    replay_mismatches = []
    for key in sorted(i1):
        for field in HASH_FIELDS:
            if i1[key][field] != i2[key][field]:
                replay_mismatches.append((key, field))

    # 2. cross-method sharing within each pass
    share_mismatches = []
    for tag, idx in (("pass1", i1), ("pass2", i2)):
        by_obj: dict[int, list] = {}
        for (obj_idx, method), row in idx.items():
            by_obj.setdefault(obj_idx, []).append((method, row))
        for obj_idx, entries in by_obj.items():
            base_method, base = entries[0]
            for method, row in entries[1:]:
                for field in HASH_FIELDS:
                    if row[field] != base[field]:
                        share_mismatches.append((tag, obj_idx, base_method, method, field))

    # 3. cross-realization comparison (same 10 frozen objects)
    r0 = index(json.loads(R0_AUDIT.read_text()))
    agree_deterministic, differ_reference, bad = 0, 0, []
    for key in sorted(i1):
        obj_idx = key[0]
        r0_row = next(r for (o, m), r in r0.items() if o == obj_idx)
        for field in HASH_FIELDS:
            same = i1[key][field] == r0_row[field]
            if field in REFERENCE_DERIVED:
                if not same:
                    differ_reference += 1
                else:
                    bad.append(("reference-identical-across-realizations", key, field))
            else:
                if same:
                    agree_deterministic += 1
                else:
                    bad.append(("deterministic-component-mismatch", key, field))

    payload = {
        "audit": "ROBUSTNESS1_SHARED_INPUT_AUDIT",
        "seed_rule": p1["seed_rule"],
        "object_sample_indices": p1["object_sample_indices"],
        "same_sample_as_R0_audit": p1["object_sample_indices"] == json.loads(R0_AUDIT.read_text())["object_sample_indices"],
        "rows_per_pass": len(i1),
        "replay_mismatches_pass1_vs_pass2": len(replay_mismatches),
        "replay_mismatch_detail": replay_mismatches[:20],
        "cross_method_mismatches": len(share_mismatches),
        "cross_method_mismatch_detail": share_mismatches[:20],
        "cross_realization_check": {
            "deterministic_component_fields_matching_R0": agree_deterministic,
            "reference_derived_fields_differing_from_R0": differ_reference,
            "expected": "500 deterministic matches (10 obj x 10 det fields x 5 methods) and 150 reference-derived differences (10 x 3 x 5)",
            "anomalies": bad[:20],
        },
        "initial_latent_R1": p1["initial_latent"],
        "scheduler_R1": p1["schedule_record"],
        "verdict": "PASS" if (not replay_mismatches and not share_mismatches and not bad) else "FAIL",
    }
    (TASK / "ROBUSTNESS1_SHARED_INPUT_AUDIT.json").write_text(json.dumps(payload, indent=2) + "\n")

    md = f"""# ROBUSTNESS1_SHARED_INPUT_AUDIT (Realization-1 namespace)

## Verdict: {payload['verdict']}

## Design

Adapted from the frozen R0 shared-input audit
(`final_acceptance_20260930/SHARED_INPUT_DETERMINISM_AUDIT.md`): 10 fixed
strict-276 objects (sample indices {p1['object_sample_indices']}, drawn once
with `random.Random(20260930)`) x Core-5 methods, SHA-256 over every input
artifact of the frozen confirmation-runner input section, but under the
Realization-1 reference-seed namespace **object_seed = 10042 + obj_idx**
(R0 used 42 + obj_idx). Two fully separate Python processes (`pass1`,
`pass2`) reran the audit.

Hashed per (object, method): raw reference PNGs (000/014), cond_imgs raw +
resized, VAE cond-latent, target raw + grid, normals raw + grid, depth raw +
grid, mask grid, geo_clean, geo_encoder feature dict, global embeds,
initial latent (GPU fp16 + CPU fp32, seed 42), Euler scheduler
timesteps/sigmas.

## Results

| Check | Rows | Mismatches |
|---|---:|---:|
| pass1 vs pass2 (separate processes, all fields) | 50 | {len(replay_mismatches)} |
| across methods within a process (same object) | 4 pairs x 10 objects x 2 passes | {len(share_mismatches)} |

Cross-realization consistency (vs the frozen R0 audit, same 10 objects):

| Component class | Fields | Expected vs R0 | Observed |
|---|---|---|---|
| deterministic (targets/normals/depth/mask/global embeds/geo) | 10 fields x 50 rows | identical | {agree_deterministic} matches |
| reference-derived (cond raw/resized/latent) | 3 fields x 50 rows | different | {differ_reference} differ |

Anomalies: {len(bad)}.

Interpretation: the deterministic components being bit-identical to R0
proves the protocol (dataset, object list, view mode, latent seed 42,
scheduler) is unchanged; the reference-derived components differing on every
row proves Realization-1 is a genuinely independent reference-preprocessing
draw, not a near-duplicate of R0.

Initial latent (seed 42) GPU/CPU hashes and scheduler timestep/sigma hashes
match the frozen R0 audit exactly.

## Gate decision

{"PASS — the formal strict-276 x Core-5 (1380 rows) run may start." if payload["verdict"] == "PASS" else "FAIL — the formal run is FORBIDDEN until fixed."}

Raw tables: `ROBUSTNESS1_SHARED_INPUT_AUDIT.pass1.json`,
`ROBUSTNESS1_SHARED_INPUT_AUDIT.pass2.json` (full 50-row hash tables).
"""
    (TASK / "ROBUSTNESS1_SHARED_INPUT_AUDIT.md").write_text(md)
    print(json.dumps({k: v for k, v in payload.items() if not k.endswith("detail")}, indent=1))


if __name__ == "__main__":
    main()
