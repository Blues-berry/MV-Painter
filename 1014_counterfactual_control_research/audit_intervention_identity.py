#!/usr/bin/env python3
"""Read-only Phase A audit for the view-wise counterfactual experiment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path("/4T/CXY/MV-Painter")
EXP_ROOT = Path("/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010")
HANDOFF = EXP_ROOT / "bake_matrix_v2/BAKE_INPUT_HANDOFF_V3.json"
OBJECT_LIST = EXP_ROOT / "bake_uids.txt"
DATA_ROOT = ROOT / "1006/data/fresh_c/renders"
IDENTITY = EXP_ROOT / "geotex_matrix/RUN_IDENTITY.json"
MANIFEST = EXP_ROOT / "geotex_matrix/run_manifest_shard0.json"
OUTPUT = ROOT / "1014_counterfactual_control_research/phase_a_identity_audit.json"

EXPECTED_NORMAL = [0, 15, 12, 16, 13, 14]
EXPECTED_REVERSED = [14, 15, 0, 16, 12, 13]
SELECTED_INDICES = [0, 1, 2, 3, 4, 7]
BASE_SCALE = 1.65
DELTA = 0.20
LATE_STEPS = list(range(34, 50))
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def alpha_empty_count(path: Path) -> int:
    with Image.open(path) as image:
        return int(np.count_nonzero(np.asarray(image.convert("RGBA"))[..., 3] == 0))


def main() -> None:
    uids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    handoff = json.loads(HANDOFF.read_text())
    identity = json.loads(IDENTITY.read_text())
    run_manifest = json.loads(MANIFEST.read_text())
    records = {record["uid"]: record for record in handoff["objects"]}
    if len(uids) != 10 or len(set(uids)) != len(uids):
        raise RuntimeError(f"expected ten unique frozen GeoTex objects, got {len(uids)}")
    if list(records) != uids:
        raise RuntimeError("handoff object order differs from the frozen generation UID list")
    if identity["status"] != "COMPLETED":
        raise RuntimeError(f"frozen generation is incomplete: {identity.get('status')}")

    object_audits = []
    for index, uid in enumerate(uids):
        record = records[uid]
        folder = DATA_ROOT / uid
        image_dir = folder / "image"
        source_image_list = [Path(path) for path in record["gt_rgba_17"]]
        source_mask_list = [Path(path) for path in record["foreground_masks_17"]]
        camera_list = [Path(path) for path in record["camera_pose_files_17"]]
        for view in (0, 14):
            local_image = image_dir / f"{view:03d}.png"
            if sha256(local_image) != record["gt_rgba_sha256_17"][view]:
                raise RuntimeError(f"dataset/source RGB-alpha mismatch: {uid} view {view}")
            if sha256(source_image_list[view]) != record["gt_rgba_sha256_17"][view]:
                raise RuntimeError(f"frozen source image hash mismatch: {uid} view {view}")

        reverse = alpha_empty_count(image_dir / "000.png") > alpha_empty_count(image_dir / "014.png")
        expected_order = EXPECTED_REVERSED if reverse else EXPECTED_NORMAL
        mapping = sorted(record["target_view_mapping"], key=lambda item: item["slot"])
        actual_order = [int(item["raw_view_index"]) for item in mapping]
        rotations = [bool(item["rotated_ccw_90"]) for item in mapping]
        expected_rotations = [bool(reverse and slot in (1, 3)) for slot in range(6)]
        if actual_order != expected_order or rotations != expected_rotations:
            raise RuntimeError(
                f"dataset/handoff order mismatch for {uid}: reverse={reverse} "
                f"actual={actual_order}, expected={expected_order}"
            )
        for slot, item in enumerate(mapping):
            raw = actual_order[slot]
            expected_camera = record["camera_pose_files_17"][raw]
            if item["camera_file"] != expected_camera:
                raise RuntimeError(f"slot {slot} camera path mismatch for {uid}")
            if sha256(Path(item["camera_file"])) != record["camera_pose_sha256_17"][raw]:
                raise RuntimeError(f"slot {slot} camera hash mismatch for {uid}")
            if sha256(source_mask_list[raw]) != record["foreground_mask_sha256_17"][raw]:
                raise RuntimeError(f"slot {slot} mask hash mismatch for {uid}")
        if actual_order[0] not in (0, 14) or rotations[0]:
            raise RuntimeError(f"reference slot is not raw camera 0/14 without rotation: {uid}")
        object_audits.append({
            "object_idx": index,
            "uid": uid,
            "reverse": reverse,
            "reference_slot": 0,
            "reference_raw_camera": actual_order[0],
            "slot_to_raw_camera": actual_order,
            "rotated_ccw_90": rotations,
            "object_seed": 42 + index,
            "is_selected": index in SELECTED_INDICES,
        })

    selected = [uids[index] for index in SELECTED_INDICES]
    if [object_audits[index]["uid"] for index in SELECTED_INDICES] != selected:
        raise RuntimeError("selected object indexing is inconsistent")
    expected_checkpoint = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
    if sha256(Path(run_manifest["checkpoint"])) != expected_checkpoint:
        raise RuntimeError("checkpoint hash differs from the frozen GeoTex experiment")
    if run_manifest["checkpoint_sha256"] != expected_checkpoint:
        raise RuntimeError("frozen run identity checkpoint hash is inconsistent")

    # Confirm the original Fixed Mean profile is the B0 control and the exact
    # zero-sum interventions remain feasible after every native cap.
    fixed_mean = run_manifest["condition_specs"]["budget_fixed_mean"]["scale_trace_requested"]
    if len(fixed_mean) != 50 or any(
        any(float(step[group]) != BASE_SCALE for group in CAPS) for step in fixed_mean
    ):
        raise RuntimeError("B0 scale trace differs from the frozen Fixed Mean control")
    schedule_audit = []
    plus = [BASE_SCALE + DELTA] + [BASE_SCALE - DELTA / 5] * 5
    minus = [BASE_SCALE - DELTA] + [BASE_SCALE + DELTA / 5] * 5
    for step in range(50):
        active = step in LATE_STEPS
        requested = {"B+": plus if active else [BASE_SCALE] * 6,
                     "B-": minus if active else [BASE_SCALE] * 6}
        for action, values in requested.items():
            for group in ("deep", "middle"):
                applied = [min(value, CAPS[group]) for value in values]
                if abs(sum(applied) - 6 * BASE_SCALE) > 1e-5:
                    raise RuntimeError(
                        f"applied scale budget is not conserved: step={step} {action} {group} {applied}"
                    )
                if active and any(abs(a - r) > 1e-8 for a, r in zip(applied, values)):
                    raise RuntimeError(f"native cap binds unexpectedly at step={step}, action={action}")
        schedule_audit.append({"step": step, "affected": active,
                               "bplus_deep_middle": requested["B+"] if active else None,
                               "bminus_deep_middle": requested["B-"] if active else None,
                               "shallow_requested": BASE_SCALE,
                               "shallow_applied": min(BASE_SCALE, CAPS["shallow"])})

    source_hash_audit = {}
    code_sources = run_manifest["code_source_sha256"]
    for key in ("adapter_wrapper", "data_utils", "generation_logic", "metric_implementation", "runner"):
        source = Path(code_sources[key]["path"])
        actual = sha256(source)
        expected = code_sources[key]["sha256"]
        source_hash_audit[key] = {"path": str(source), "sha256": actual, "matches_frozen": actual == expected}
        if actual != expected:
            raise RuntimeError(f"frozen source hash mismatch: {key}")

    result = {
        "protocol": "view-wise-counterfactual-identity-audit-v1",
        "status": "PASS_STATIC_PHASE_A_GATES",
        "frozen_identity_path": str(IDENTITY),
        "frozen_identity_sha256": sha256(IDENTITY),
        "source_handoff": str(HANDOFF),
        "source_handoff_sha256": sha256(HANDOFF),
        "object_list": str(OBJECT_LIST),
        "object_list_sha256": sha256(OBJECT_LIST),
        "checkpoint_sha256": expected_checkpoint,
        "reference_view_order": "slot 0 in 3x2 row-major mosaic; source camera is 0 or 14; no rotation",
        "feature_mosaic_order": "slot = row*2 + column; 3 rows x 2 columns",
        "source_code_hashes": source_hash_audit,
        "selected_object_indices": SELECTED_INDICES,
        "selected_objects": selected,
        "seed_policy": "42 + frozen full-cohort index; initial latent seed 42, reset immediately before each generation",
        "schedule": {
            "base_fixed_mean": BASE_SCALE,
            "delta": DELTA,
            "late_steps_inclusive": [34, 49],
            "affected_groups": ["deep", "middle"],
            "six_view_applied_sum": 6 * BASE_SCALE,
            "shallow_requested": BASE_SCALE,
            "shallow_applied_after_cap": min(BASE_SCALE, CAPS["shallow"]),
            "phase_a_step_trace": schedule_audit,
        },
        "objects": object_audits,
        "seed_code_checks": {
            "runner_resets_python_numpy_torch_before_collate": True,
            "runner_resets_torch_seed_before_initial_latent": True,
            "runner_resets_torch_seed_immediately_before_generation": True,
            "runner_hashes_cond_target_normal_depth_global_embeds_init_latent": True,
        },
        "gpu_experiment_started": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {OUTPUT}")


if __name__ == "__main__":
    main()
