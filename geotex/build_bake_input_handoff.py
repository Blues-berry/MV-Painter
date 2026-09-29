"""Assemble frozen, byte-preserving inputs for Codex D's baking work."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/main_adapter_baking"
COHORT = ROOT / "final/round2/main_adapter_clean_v2/exact_baking_cohort_manifest.csv"
PRED = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/predictions"
VAL = ROOT / "final/round2/main_adapter_clean_v2/exact_glb_validation"
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
UNIQUE6 = (0, 15, 12, 16, 13, 14)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def camera_record(path: Path) -> dict:
    x = np.load(path, allow_pickle=True).item()
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in x.items()}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    view_out = OUT / "frozen_views"
    mask_out = OUT / "foreground_masks"
    rows = list(csv.DictReader(COHORT.open()))
    blender_audit = json.loads((OUT / "blender_glb_uv_material_audit.json").read_text())
    objects = []
    for row in rows:
        object_id, uid = row["object"], row["uid"]
        glb = Path(row["glb"])
        scene = trimesh.load(glb, force="scene", process=False)
        geoms = list(scene.geometry.values()) if hasattr(scene, "geometry") else [scene]
        blender_record = blender_audit[uid]
        normalization = blender_record["historical_normalization"]
        materials = blender_record["mesh_objects"]

        image_root = VAL / object_id / "image"
        camera_root = VAL / object_id / "camera"
        cameras = [camera_record(camera_root / f"{i:03d}.npy") for i in range(17)]
        alpha_paths = []
        for i in range(17):
            src = image_root / f"{i:03d}.png"
            alpha = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)[:, :, 3]
            mask_path = mask_out / object_id / f"{i:03d}.png"
            mask_path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(alpha).save(mask_path)
            alpha_paths.append(str(mask_path))
        alpha0 = cv2.imread(str(image_root / "000.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
        alpha14 = cv2.imread(str(image_root / "014.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
        reverse = bool((alpha0 == 0).sum() > (alpha14 == 0).sum())
        source_views = list((14, 15, 0, 16, 12, 13) if reverse else UNIQUE6)
        target_view_mapping = []
        for slot, raw_idx in enumerate(source_views):
            rotate = bool(reverse and slot in (1, 3))
            target_view_mapping.append({"slot": slot, "raw_view_index": raw_idx, "camera_file": str(camera_root / f"{raw_idx:03d}.npy"), "rotated_ccw_90": rotate})

        generated = {}
        for method in METHODS:
            panel_path = PRED / method / f"{object_id}.png"
            generated[method] = {"panel": str(panel_path), "panel_sha256": sha256(panel_path), "target_views": []}
            panel = Image.open(panel_path).convert("RGB")
            for slot, mapping in enumerate(target_view_mapping):
                col, row_index = slot % 2, slot // 2
                crop = panel.crop((col * 256, row_index * 256, (col + 1) * 256, (row_index + 1) * 256))
                vp = view_out / object_id / method / f"slot_{slot}_raw_{mapping['raw_view_index']:03d}.png"
                vp.parent.mkdir(parents=True, exist_ok=True)
                crop.save(vp)
                generated[method]["target_views"].append({"slot": slot, "raw_view_index": mapping["raw_view_index"], "path": str(vp), "sha256": sha256(vp)})

        objects.append({
            "object": object_id,
            "source_uid": uid,
            "exact_glb_path": str(glb),
            "exact_glb_sha256": sha256(glb),
            "source_file_identifier": row["source_file_identifier"],
            "source_asset_sha256": row.get("source_asset_sha256", ""),
            "original_uv_required": True,
            "mesh_material_audit": materials,
            "uv_validation_backend": "Blender 4.2.4 native glTF+Draco import; trimesh UV values are not used",
            "normalization": {**normalization, "normalized_world": "scale*(source_world+offset)", "meta_path": str(VAL / object_id / "meta.npy")},
            "camera_poses_17": cameras,
            "camera_pose_files_17": [str(camera_root / f"{i:03d}.npy") for i in range(17)],
            "gt_rgba_17": [str(image_root / f"{i:03d}.png") for i in range(17)],
            "foreground_masks_17": alpha_paths,
            "reverse_dataset_orientation": reverse,
            "target_view_mapping": target_view_mapping,
            "unseen_raw_view_indices": [i for i in range(17) if i not in source_views],
            "generated_conditions": generated,
        })
    handoff = {
        "protocol": "main-adapter-clean-v2-bake-input-handoff-v1",
        "status": "frozen_inputs_only; Codex D owns baking implementation",
        "do_not_modify": ["exact_glb_path bytes", "source UID list", "camera poses", "GT RGBA", "generated PNGs", "checkpoint", "C3"],
        "cohort_manifest": str(COHORT),
        "cohort_count": len(objects),
        "conditions": ["GT", *METHODS],
        "target_view_mode": "unique6",
        "target_views": list(UNIQUE6),
        "unseen_views": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "generation_resolution": {"per_view": [256, 256], "panel": [512, 768]},
        "baking_parameters": {"texture_resolution": 1024, "preserve_original_uv": True, "visibility": "camera-depth/z-buffer visibility required", "blend": "shared across GT/no_adapter/fixed_low/fixed_high/C3; cosine-facing weight may be used only if recorded identically", "inpaint": "must be reported; do not silently fill uncovered texels", "unseen_evaluation": "raw views not in unique6; no generated unseen PNG exists"},
        "objects": objects,
    }
    (OUT / "BAKE_INPUT_HANDOFF.json").write_text(json.dumps(handoff, indent=2) + "\n")
    print(json.dumps({"cohort_count": len(objects), "handoff": str(OUT / "BAKE_INPUT_HANDOFF.json"), "view_files": str(view_out), "mask_files": str(mask_out)}, indent=2))


if __name__ == "__main__":
    main()
