#!/usr/bin/env python3
"""Positive/negative controls and non-empty audit of the corrected seam metric.

Uses only two temporary synthetic GLBs plus the already-existing 12-object
bake measurements. It does not bake, render, or run inference on real objects.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/coordination/final_evidence_freeze_20261001"
sys.path.insert(0, str(ROOT / "scripts"))
from audit_bake_seams_20261001 import audit_glb  # noqa: E402

SOURCE = ROOT / "final/round2/coordination/BAKE_SEAM_AUDIT_20261001/SEAM_AUDIT_PER_OBJECT.csv"
CONDITIONS = {
    "no_adapter", "fixed_low", "fixed_high", "c3",
    "global_fixed_low", "global_c3", "layer_lhl", "layer_llh",
}


def synthetic_glb(path: Path, split_texture: bool) -> None:
    # Two triangles share one 3-D edge, but chart copies of that edge map to
    # u≈0.1 and u≈0.8. This makes a true detectable UV seam in a tiny fixture.
    vertices = np.asarray([
        [0, 0, 0], [1, 0, 0], [0, 1, 0],
        [0, 0, 0], [1, 0, 0], [1, 1, 0],
    ], dtype=np.float64)
    faces = np.asarray([[0, 1, 2], [3, 5, 4]], dtype=np.int64)
    uv = np.asarray([
        [0.10, 0.45], [0.10, 0.55], [0.20, 0.45],
        [0.80, 0.45], [0.80, 0.55], [0.90, 0.45],
    ], dtype=np.float64)
    if split_texture:
        tex = np.zeros((64, 64, 3), dtype=np.uint8)
        tex[:, :, :] = [128, 128, 128]
        tex[:, :20, :] = [255, 0, 0]
        tex[:, 44:, :] = [0, 0, 255]
    else:
        tex = np.full((64, 64, 3), [128, 128, 128], dtype=np.uint8)
    material = trimesh.visual.material.PBRMaterial(
        baseColorTexture=Image.fromarray(tex, mode="RGB"),
        metallicFactor=0.0,
        roughnessFactor=1.0,
    )
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=material)
    path.write_bytes(mesh.export(file_type="glb"))


def validate_existing_rows() -> tuple[list[dict], dict]:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts: dict[str, int] = {}
    seen: set[tuple[str, str]] = set()
    objects_by_condition: dict[str, set[str]] = {}
    invalid = []
    normalized = []
    for row in rows:
        cond, obj = row["condition"], row["object"]
        key = (cond, obj)
        if key in seen:
            invalid.append(f"duplicate {cond}/{obj}")
        seen.add(key)
        counts[cond] = counts.get(cond, 0) + 1
        objects_by_condition.setdefault(cond, set()).add(obj)
        row_valid = True
        try:
            pairs = int(row["n_seam_edges"])
            mean = float(row["seam_dE00_mean"])
            median = float(row["seam_dE00_median"])
            p90 = float(row["seam_dE00_p90"])
            uv_dist = float(row["seam_uv_dist_median"])
            if pairs <= 0 or not all(math.isfinite(x) for x in (mean, median, p90, uv_dist)):
                raise ValueError("empty/invalid seam set or non-finite metric")
        except (KeyError, TypeError, ValueError) as exc:
            invalid.append(f"{cond}/{obj}: {exc}")
            pairs, mean, median, p90, uv_dist = 0, math.nan, math.nan, math.nan, math.nan
            row_valid = False
        normalized.append({
            "condition": cond,
            "object": obj,
            "n_detected_seams": int(row.get("n_seam_edges") or 0),
            "n_valid_seam_pairs": pairs,
            "seam_sample_footprint_px": "3x3 mean per chart-side UV midpoint",
            "seam_surface_pair_distance": "same 3D edge midpoint (0 surface distance)",
            "interior_control_offset_px": 2,
            "seam_dE00_mean": mean,
            "seam_dE00_median": median,
            "seam_dE00_p90": p90,
            "seam_uv_dist_median": uv_dist,
            "validity": "VALID" if row_valid else "INVALID",
        })
    if any(counts.get(c) != 12 for c in CONDITIONS):
        invalid.append(f"expected 12 objects per condition; observed {counts}")
    if set(objects_by_condition) != CONDITIONS:
        invalid.append(f"condition mismatch expected={sorted(CONDITIONS)} observed={sorted(objects_by_condition)}")
    object_sets = list(objects_by_condition.values())
    if object_sets and any(objects != object_sets[0] for objects in object_sets[1:]):
        invalid.append("the 12-object bake cohort differs across conditions")
    summary = {
        "source_csv": str(SOURCE.relative_to(ROOT)),
        "rows": len(rows),
        "conditions": counts,
        "objects": sorted(next(iter(objects_by_condition.values()))) if objects_by_condition else [],
        "expected_rows": 96,
        "all_rows_have_nonempty_finite_seam_metrics": not invalid,
        "invalid_findings": invalid,
    }
    return normalized, summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="seam-control-") as tmp:
        tmpdir = Path(tmp)
        positive_path = tmpdir / "positive_control.glb"
        negative_path = tmpdir / "negative_control.glb"
        synthetic_glb(positive_path, split_texture=True)
        synthetic_glb(negative_path, split_texture=False)
        positive = audit_glb(positive_path)
        negative = audit_glb(negative_path)

    positive_pass = int(positive.get("n_seam_edges", 0)) > 0 and float(positive["seam_dE00_mean"]) > 20.0
    negative_pass = int(negative.get("n_seam_edges", 0)) > 0 and float(negative["seam_dE00_mean"]) < 0.1
    object_rows, real_summary = validate_existing_rows()
    if not positive_pass:
        real_summary["invalid_findings"].append("positive synthetic seam control failed")
    if not negative_pass:
        real_summary["invalid_findings"].append("negative seam-free control failed")
    real_summary["all_rows_have_nonempty_finite_seam_metrics"] = (
        real_summary["all_rows_have_nonempty_finite_seam_metrics"] and positive_pass and negative_pass
    )

    fields = list(object_rows[0]) if object_rows else []
    with (OUT / "SEAM_METRIC_FINAL_OBJECT_VALIDATION.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(object_rows)
    result = {
        "script": str(Path(__file__).relative_to(ROOT)),
        "controls": {
            "positive_seam_color_split": {k: v for k, v in positive.items() if k != "glb"} | {"fixture": "positive_control.glb", "pass": positive_pass},
            "negative_uniform_seam_free_texture": {k: v for k, v in negative.items() if k != "glb"} | {"fixture": "negative_control.glb", "pass": negative_pass},
            "thresholds": {"positive_mean_dE00_gt": 20.0, "negative_mean_dE00_lt": 0.1},
        },
        "existing_12_object_bakes": real_summary,
        "sampling_semantics": {
            "seam_pair": "CIEDE2000 between 3x3-mean samples at chart-side UV midpoints of the same 3-D edge",
            "seam_surface_distance": "zero; both samples represent the same 3-D edge midpoint",
            "interior_control_offset_px": 2,
            "empty_set": "INVALID; no empty-set-to-zero fallback accepted",
        },
    }
    out_json = OUT / "SEAM_METRIC_FINAL_VALIDATION.json"
    out_json.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "positive": {k: positive.get(k) for k in ("n_seam_edges", "seam_dE00_mean", "seam_dE00_median", "seam_dE00_p90")},
        "positive_pass": positive_pass,
        "negative": {k: negative.get(k) for k in ("n_seam_edges", "seam_dE00_mean", "seam_dE00_median", "seam_dE00_p90")},
        "negative_pass": negative_pass,
        "real_rows": real_summary,
    }, indent=2))
    if not real_summary["all_rows_have_nonempty_finite_seam_metrics"]:
        raise SystemExit("seam metric final validation FAILED")


if __name__ == "__main__":
    main()
