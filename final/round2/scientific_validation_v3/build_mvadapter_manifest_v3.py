#!/usr/bin/env python3
"""Build the Experiment-G MV-Adapter manifest for the FRESH_CONFIRM cohort.

Mirrors final/round2/mv_adapter/data_manifest.json fields that the runner
consumes (object, source_uid, render_root, mesh_path, reference_image,
gt_images_{round2,official}_order, camera ids, availability flags).

N subset (default 100) is drawn deterministically from the frozen cohort
(seed 20261002, sorted UIDs) BEFORE any G outcome exists.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
RENDER_ROOT = RENDER_ROOT = ROOT / "data/fresh_confirm_v3_renders"
GLB_ROOT = Path("/home/ubuntu/.objaverse/hf-objaverse-v1/glbs")
SEED = 20261002
DEFAULT_N = 100

ROUND2_ORDER = [0, 15, 12, 16, 13, 14]
OFFICIAL_ORDER = [14, 0, 12, 13, 15, 16]
CAMERA_IDS_ROUND2 = [0, 15, 12, 16, 13, 14]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def find_glb(uid):
    for shard in sorted(GLB_ROOT.iterdir()):
        p = shard / (uid + ".glb")
        if p.exists():
            return p
    return None


def main():
    cohort = Path(sys.argv[1]) if len(sys.argv) > 1 else V3 / "fresh_confirm_300.txt"
    n_target = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_N
    uids = [l.strip() for l in cohort.open() if l.strip()]
    rng = np.random.default_rng(SEED)
    pick = sorted(rng.permutation(len(uids))[:n_target].tolist())
    subset = [uids[i] for i in pick]

    objects = []
    for pos, uid in enumerate(subset):
        obj_dir = RENDER_ROOT / uid
        glb = find_glb(uid)
        row = {
            "object": "g_%04d" % pos,
            "source_uid": uid,
            "render_root": str(obj_dir),
            "mesh_path": str(glb) if glb else None,
            "mesh_available": glb is not None,
            "render_available": all(
                (obj_dir / "image" / ("%03d.png" % v)).exists() for v in range(17)),
            "reference_image": str(obj_dir / "image" / "000.png"),
            "gt_images_round2_order": [str(obj_dir / "image" / ("%03d.png" % v)) for v in ROUND2_ORDER],
            "gt_images_official_order": [str(obj_dir / "image" / ("%03d.png" % v)) for v in OFFICIAL_ORDER],
            "camera_ids_round2_order": CAMERA_IDS_ROUND2,
            "camera_ids_official_order": OFFICIAL_ORDER,
            "glb_sha256": sha256(glb) if glb else None,
        }
        if not row["mesh_available"] or not row["render_available"]:
            raise RuntimeError("incomplete object: " + uid)
        objects.append(row)

    manifest = {
        "protocol": "validation-v3-mvadapter-g-cohort-v1",
        "source_uid_file": str(cohort),
        "source_uid_file_sha256": sha256(cohort),
        "render_root": str(RENDER_ROOT),
        "glb_root": str(GLB_ROOT),
        "object_count": len(objects),
        "calibration_objects": [],
        "holdout_objects": [o["object"] for o in objects],
        "round2_camera_ids": CAMERA_IDS_ROUND2,
        "official_camera_ids_in_output_order": OFFICIAL_ORDER,
        "seed": SEED,
        "n_target": n_target,
        "objects": objects,
    }
    out = V3 / "mvadapter_manifest_v3.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print("wrote %s (%d objects)" % (out, len(objects)))


if __name__ == "__main__":
    sys.exit(main())
