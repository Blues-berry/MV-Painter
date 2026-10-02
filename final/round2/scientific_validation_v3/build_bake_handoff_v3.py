#!/usr/bin/env python3
"""Phase III Experiment F - same-draw bake input handoff (fresh cohort).

Adapts geotex/build_bake_input_handoff.py to the FRESH_CONFIRM cohort:
  * objects: the frozen visualization_24 set
  * GLBs: hf-objaverse cache (paths from fresh_confirm_300_manifest.csv)
  * cameras / GT RGBA / alpha masks / meta.npy: the fresh render tree
  * generated panels: byte-frozen prediction PNGs from the formal campaigns
    (same-draw: shared latents and reference draw per object, latent seed 42)
  * panel crop convention identical to the historical handoff
    (512x768 panel, 3 rows x 2 cols, col=slot%2, row=slot//2)

No baking here; this freezes byte-identical inputs for the blender bake.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
FORMAL = V3 / "formal"
RENDER_ROOT = ROOT / "data/fresh_confirm_v3_renders"
VIZ24 = V3 / "visualization_24.txt"
OUT = V3 / "bake_handoff"
UNIQUE6 = (0, 15, 12, 16, 13, 14)

CONDITIONS = ["no_adapter", "native_gfl", "native_gfh", "native_gc3",
              "lfm_exact", "layer_lhl", "layer_llh"]

CAMPAIGN_OF = {
    "no_adapter": "campaign_B3",
    "native_gfl": "campaign_B3",
    "native_gfh": "campaign_B3",
    "native_gc3": "campaign_B3",
    "lfm_exact": "campaign_B1B2",
    "layer_lhl": "campaign_B1B2",
    "layer_llh": "campaign_B1B2",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def camera_record(path):
    x = np.load(str(path), allow_pickle=True).item()
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in x.items()}


def find_panel(uid, condition):
    return FORMAL / CAMPAIGN_OF[condition] / "predictions" / condition / (uid + ".png")


def main():
    viz24 = [l.strip() for l in VIZ24.open() if l.strip()]
    glb_paths = {}
    with (V3 / "fresh_confirm_300_manifest.csv").open() as f:
        for row in csv.DictReader(f):
            glb_paths[row["uid"]] = row["glb_path"]

    view_out = OUT / "frozen_views"
    mask_out = OUT / "foreground_masks"
    objects = []
    missing = 0
    for uid in viz24:
        obj_dir = RENDER_ROOT / uid
        glb = Path(glb_paths[uid])
        scene = trimesh.load(str(glb), force="scene", process=False)
        mesh_material_audit = [
            {"geometry": name,
             "faces": int(len(g.faces)) if hasattr(g, "faces") else 0,
             "has_uv": bool(getattr(g.visual, "uv", None) is not None)}
            for name, g in (scene.geometry.items() if hasattr(scene, "geometry") else [])
        ]

        cameras = [camera_record(obj_dir / "camera" / ("%03d.npy" % i)) for i in range(17)]
        alpha_paths = []
        for i in range(17):
            src = obj_dir / "image" / ("%03d.png" % i)
            alpha = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)[:, :, 3]
            mask_path = mask_out / uid / ("%03d.png" % i)
            mask_path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(alpha).save(mask_path)
            alpha_paths.append(str(mask_path))
        alpha0 = cv2.imread(str(obj_dir / "image" / "000.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
        alpha14 = cv2.imread(str(obj_dir / "image" / "014.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
        reverse = bool((alpha0 == 0).sum() > (alpha14 == 0).sum())
        source_views = list((14, 15, 0, 16, 12, 13) if reverse else UNIQUE6)
        target_view_mapping = []
        for slot, raw_idx in enumerate(source_views):
            rotate = bool(reverse and slot in (1, 3))
            target_view_mapping.append({
                "slot": slot, "raw_view_index": raw_idx,
                "camera_file": str(obj_dir / "camera" / ("%03d.npy" % raw_idx)),
                "rotated_ccw_90": rotate})

        generated = {}
        for cond in CONDITIONS:
            panel_path = find_panel(uid, cond)
            if not panel_path.exists():
                missing += 1
                continue
            generated[cond] = {"panel": str(panel_path), "panel_sha256": sha256(panel_path),
                               "target_views": []}
            panel = Image.open(panel_path).convert("RGB")
            for slot, mapping in enumerate(target_view_mapping):
                col, row_index = slot % 2, slot // 2
                crop = panel.crop((col * 256, row_index * 256,
                                   (col + 1) * 256, (row_index + 1) * 256))
                vp = view_out / uid / cond / ("slot_%d_raw_%03d.png" % (slot, mapping["raw_view_index"]))
                vp.parent.mkdir(parents=True, exist_ok=True)
                crop.save(vp)
                generated[cond]["target_views"].append({
                    "slot": slot, "raw_view_index": mapping["raw_view_index"],
                    "path": str(vp), "sha256": sha256(vp)})

        meta = np.load(str(obj_dir / "meta.npy")).tolist()
        objects.append({
            "object": uid,
            "source_uid": uid,
            "exact_glb_path": str(glb),
            "exact_glb_sha256": sha256(glb),
            "original_uv_required": True,
            "mesh_material_audit": mesh_material_audit,
            "uv_validation_backend": "Blender 4.2.4 native glTF+Draco import",
            "normalization": {"meta_values": meta,
                              "normalized_world": "scale*(source_world+offset)",
                              "meta_path": str(obj_dir / "meta.npy")},
            "camera_poses_17": cameras,
            "camera_pose_files_17": [str(obj_dir / "camera" / ("%03d.npy" % i)) for i in range(17)],
            "gt_rgba_17": [str(obj_dir / "image" / ("%03d.png" % i)) for i in range(17)],
            "foreground_masks_17": alpha_paths,
            "reverse_dataset_orientation": reverse,
            "target_view_mapping": target_view_mapping,
            "unseen_raw_view_indices": [i for i in range(17) if i not in set(source_views)],
            "generated_conditions": generated,
        })

    handoff = {
        "protocol": "validation-v3-unified-samedraw-bake-handoff-v1",
        "status": "frozen_inputs_only",
        "cohort_manifest": str(VIZ24),
        "cohort_count": len(objects),
        "conditions": ["GT"] + CONDITIONS,
        "target_view_mode": "unique6",
        "target_views": list(UNIQUE6),
        "generation_resolution": {"per_view": [256, 256], "panel": [512, 768]},
        "baking_parameters": {
            "texture_resolution": 1024, "preserve_original_uv": True,
            "visibility": "camera-depth/z-buffer visibility required",
            "blend": "shared identically across all conditions incl. GT",
            "inpaint": "must be reported; do not silently fill uncovered texels",
            "unseen_evaluation": "raw views not in unique6",
        },
        "objects": objects,
    }
    out_path = OUT / "BAKE_INPUT_HANDOFF_V3.json"
    OUT.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(handoff, indent=2) + "\n")
    print("wrote %s (%d objects); missing panels: %d" % (out_path, len(objects), missing))


if __name__ == "__main__":
    sys.exit(main())
