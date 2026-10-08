#!/usr/bin/env python
"""Compute locked foreground color endpoints from byte-preserved RGB grids."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
FREEZE = ARTIFACT / "SAMPLE_FREEZE.json"
VISUAL_REVIEW = ARTIFACT / "logs/VISUAL_REVIEW_TAGS.json"
METHODS = [
    ("no_adapter", "No Adapter"),
    ("native_gfl", "GFL"),
    ("native_gfh", "GFH"),
    ("native_gc3", "C3"),
    ("gen_linear", "Generic Linear"),
    ("layer_llh", "LLH"),
    ("c3_feature_gate", "C3 + Feature Gate"),
    ("linear_feature_gate", "Linear + Feature Gate"),
]
BASELINE_METHOD_KEYS = {"no_adapter", "native_gfl", "native_gfh", "native_gc3", "gen_linear", "layer_llh"}


def load_grid(path: Path, rgb: bool = True) -> np.ndarray:
    image = Image.open(path)
    image = image.convert("RGB" if rgb else "L")
    array = np.asarray(image)
    if array.shape[:2] != (768, 512):
        raise ValueError(f"expected 512x768 3x2 grid, got {array.shape}: {path}")
    return array


def get_tile(grid: np.ndarray, view: int) -> np.ndarray:
    row, col = divmod(view, 2)
    return grid[row * 256:(row + 1) * 256, col * 256:(col + 1) * 256]


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    visual_review = json.loads(VISUAL_REVIEW.read_text())
    metric_rows = list(csv.DictReader((ARTIFACT / "logs/RGB_RELOADED_METRICS.csv").open()))
    metric_map = {
        (row["sample_id"], row["method_key"]): {
            key: float(row[key]) for key in ("fg_psnr", "fg_lpips", "edge_ssim")
        }
        for row in metric_rows
    }
    rows = []
    summary_by_method = {label: [] for _, label in METHODS}
    for sample in freeze["samples"]:
        sample_id = sample["sample_id"]
        sample_dir = ARTIFACT / "raw_rgb" / sample_id
        reference_grid = load_grid(sample_dir / "reference.png")
        mask_grid = load_grid(ARTIFACT / "masks" / f"{sample_id}.png", rgb=False)
        for method_key, method_label in METHODS:
            prediction_path = (sample_dir / f"{method_key}.png" if method_key in BASELINE_METHOD_KEYS
                               else ARTIFACT / "runs/feature_ratio_gate/predictions" /
                                    method_key / f"{sample['uid']}.png")
            if not prediction_path.is_file():
                continue
            prediction_grid = load_grid(prediction_path)
            view_de, view_da, view_db, view_fg = [], [], [], []
            for view in range(6):
                ref = get_tile(reference_grid, view).astype(np.float32) / 255.0
                pred = get_tile(prediction_grid, view).astype(np.float32) / 255.0
                mask = get_tile(mask_grid, view) > 127
                if not np.any(mask):
                    raise RuntimeError(f"empty foreground mask: {sample_id}, view {view}")
                lab_ref = rgb2lab(ref)
                lab_pred = rgb2lab(pred)
                lab_delta = lab_pred - lab_ref
                de = deltaE_ciede2000(lab_ref, lab_pred)
                view_de.append(float(de[mask].mean()))
                view_da.append(float(lab_delta[..., 1][mask].mean()))
                view_db.append(float(lab_delta[..., 2][mask].mean()))
                view_fg.append(float(mask.mean()))

            mean_de = float(np.mean(view_de))
            mean_da = float(np.mean(view_da))
            mean_db = float(np.mean(view_db))
            purple = mean_da >= 5.0 and mean_db <= -5.0 and mean_de >= 5.0
            metric_row = metric_map[(sample_id, method_key)]
            review = dict(visual_review["sample_tags"][sample_id]["tags"])
            method_override = visual_review.get("method_overrides", {}).get(method_label, {})
            review.update(method_override.get(sample_id, {}).get("tags", {}))
            review_note = visual_review["sample_tags"][sample_id]["note"]
            if sample_id in method_override:
                review_note += " " + method_override[sample_id]["note"]
            row = {
                "sample_id": sample_id,
                "uid": sample["uid"],
                "source": sample["source"],
                "object_idx": sample.get("object_idx", ""),
                "object_seed": sample.get("object_seed", ""),
                "method": method_label,
                "mean_fg_ciede2000": mean_de,
                "mean_delta_a_star": mean_da,
                "mean_delta_b_star": mean_db,
                "purple_cast_flag": purple,
                "fg_psnr": metric_row.get("fg_psnr", ""),
                "fg_lpips": metric_row.get("fg_lpips", ""),
                "edge_ssim": metric_row.get("edge_ssim", ""),
                "mean_fg_fraction": float(np.mean(view_fg)),
                "view_ciede2000": json.dumps(view_de),
                "view_delta_a_star": json.dumps(view_da),
                "view_delta_b_star": json.dumps(view_db),
                **review,
                "visual_review_note": review_note,
            }
            rows.append(row)
            summary_by_method[method_label].append(row)

    output = ARTIFACT / "OBJECT_FAILURE_TABLE.csv"
    with output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for method, items in summary_by_method.items():
        summary[method] = {
            "n_objects": len(items),
            "mean_object_ciede2000": float(np.mean([r["mean_fg_ciede2000"] for r in items])),
            "median_object_ciede2000": float(np.median([r["mean_fg_ciede2000"] for r in items])),
            "purple_flag_count": int(sum(r["purple_cast_flag"] for r in items)),
            "visual_review_present_counts": {
                field: int(sum(r[field] == "present" for r in items))
                for field in (
                    "visual_purple_cast", "visual_repeated_texture",
                    "visual_fine_detail_loss", "visual_structure_damage",
                )
            },
            "mean_delta_a_star": float(np.mean([r["mean_delta_a_star"] for r in items])),
            "mean_delta_b_star": float(np.mean([r["mean_delta_b_star"] for r in items])),
        }
    (ARTIFACT / "logs/OBJECT_FAILURE_TABLE_SUMMARY.json").write_text(json.dumps({
        "endpoint": "equal-weight mean per-view foreground CIEDE2000; each object contributes one row per method",
        "foreground_mask": "prepared alpha mask thresholded at >0.5, matching frozen FG metric semantics",
        "purple_flag": "object-level mean delta a* >= 5 and delta b* <= -5 and mean CIEDE2000 >= 5",
        "visual_review": str(VISUAL_REVIEW),
                "saved_rgb_secondary_metrics": str(ARTIFACT / "logs/RGB_RELOADED_METRICS.csv"),
        "objects_are_failure_enriched_diagnostics": True,
        "metrics_by_method": summary,
    }, indent=2) + "\n")
    print(f"wrote {output} ({len(rows)} object-method rows)")


if __name__ == "__main__":
    main()
