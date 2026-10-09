#!/usr/bin/env python3
"""Compute the pre-locked per-view Lab and magenta-residual readouts for Phase B."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import deltaE_ciede2000, rgb2lab

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/phase_b"
DEV = HERE / "runs/phase_c/dev"
sys.path.insert(0, str(HERE))
import run_chroma_anchor_evaluation as c1  # noqa: E402


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def robust_mask(alpha: np.ndarray) -> np.ndarray:
    return ndimage.binary_erosion(np.asarray(alpha) >= 0.75, iterations=3, border_value=0)


def lab_stats(rgb: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    lab = rgb2lab(np.clip(np.asarray(rgb, dtype=np.float32), 0, 1))
    selected = lab[np.asarray(mask, dtype=bool)]
    if len(selected) < 64:
        raise ValueError(f"robust color region too small: {len(selected)} pixels")
    median_lab = np.median(selected, axis=0)
    chroma = float(np.hypot(median_lab[1], median_lab[2]))
    hue = float(np.degrees(np.arctan2(median_lab[2], median_lab[1])) % 360.0)
    return {
        "median_l_star": float(median_lab[0]),
        "median_a_star": float(median_lab[1]),
        "median_b_star": float(median_lab[2]),
        "median_chroma_c_star": chroma,
        "median_hue_angle_deg": hue,
        "trusted_pixels": int(len(selected)),
    }


def median_ciede(left: dict[str, float], right: dict[str, float]) -> float:
    a = np.array([[left["median_l_star"], left["median_a_star"], left["median_b_star"]]])
    b = np.array([[right["median_l_star"], right["median_a_star"], right["median_b_star"]]])
    return float(deltaE_ciede2000(a, b)[0])


def main() -> None:
    b_rows = rows(RUN / "COLOR_INTERVENTION_RESULTS.csv")
    c_rows = rows(DEV / "C_REPAIR_PAIRED_RESULTS.csv")
    target_identity = {(row["uid"], int(row["view_idx"])): row for row in c_rows}
    if len(b_rows) != 384:
        raise ValueError(f"expected 384 B view rows, found {len(b_rows)}")
    by_uid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in b_rows:
        by_uid[row["uid"]].append(row)
    objects = c1.dev_objects()
    if set(by_uid) != {obj["uid"] for obj in objects}:
        raise ValueError("Phase B outputs do not match the four locked development objects")

    per_view: list[dict] = []
    source_stats: list[dict] = []
    groups: dict[Path, list[dict]] = defaultdict(list)
    for obj in objects:
        groups[Path(obj["root"])].append(obj)

    for root, group in groups.items():
        dataset = c1._load_data(root, [obj["uid"] for obj in group])
        for object_index, spec in enumerate(group):
            uid = spec["uid"]
            source_rgb, source_alpha, targets, masks, item, source_path = c1.load_item(
                dataset, object_index, spec
            )
            object_rows = by_uid[uid]
            current_cond_hash = c1.tensor_sha(item["cond_imgs"])
            expected_cond_hashes = {row["source_condition_tensor_sha256"] for row in object_rows}
            if expected_cond_hashes != {current_cond_hash}:
                raise ValueError(f"{uid}: reconstructed condition tensor SHA mismatch")
            source_index = [i for i, row in enumerate(sorted(
                [r for r in object_rows if r["condition"] == "gfl_baseline"],
                key=lambda r: int(r["target_tile_index"]),
            )) if row["is_source_view"] == "True"]
            if source_index != [0] or int(spec["target_order"][0]) != int(spec["source_view"]):
                raise ValueError(f"{uid}: source view is not target tile zero")

            cond_stats = lab_stats(source_rgb, robust_mask(source_alpha))
            gt_source_stats = lab_stats(targets[0].astype(np.float32) / 255.0, robust_mask(masks[0]))
            if int((np.asarray(masks[0]) >= 0.5).sum()) < 16:
                raise ValueError(f"{uid}: source target mask is empty")

            baseline_row = next(
                row for row in object_rows
                if row["condition"] == "gfl_baseline" and row["target_tile_index"] == "0"
            )
            baseline_path = Path(baseline_row["prediction_png"])
            if sha_bytes(baseline_path.read_bytes()) != baseline_row["prediction_png_sha256"]:
                raise ValueError(f"{uid}: baseline PNG SHA mismatch")
            baseline_tile = c1.grid_tiles(np.asarray(Image.open(baseline_path).convert("RGB")))[0]
            baseline_source_stats = lab_stats(baseline_tile.astype(np.float32) / 255.0,
                                              robust_mask(masks[0]))
            source_stats.append({
                "uid": uid,
                "cohort": spec["cohort"],
                "source_cohort": target_identity[(uid, 0)]["source_cohort"],
                "source_view_id": int(spec["source_view"]),
                "source_path": str(source_path),
                "source_condition_tensor_sha256": current_cond_hash,
                **{f"condition_{k}": v for k, v in cond_stats.items()},
                **{f"gt_source_{k}": v for k, v in gt_source_stats.items()},
                **{f"gfl_source_{k}": v for k, v in baseline_source_stats.items()},
                "condition_to_gt_source_median_ciede2000": median_ciede(cond_stats, gt_source_stats),
                "condition_to_gfl_source_median_ciede2000": median_ciede(cond_stats, baseline_source_stats),
            })

            condition_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in object_rows:
                condition_rows[row["condition"]].append(row)
            for condition, rows_for_condition in sorted(condition_rows.items()):
                rows_for_condition.sort(key=lambda row: int(row["target_tile_index"]))
                if len(rows_for_condition) != 6:
                    raise ValueError(f"{uid}/{condition}: expected six view rows")
                image_path = Path(rows_for_condition[0]["prediction_png"])
                image_sha = rows_for_condition[0]["prediction_png_sha256"]
                if sha_bytes(image_path.read_bytes()) != image_sha:
                    raise ValueError(f"{uid}/{condition}: prediction PNG SHA mismatch")
                tiles = c1.grid_tiles(np.asarray(Image.open(image_path).convert("RGB")))
                for view_index, (row, pred, target, alpha) in enumerate(
                    zip(rows_for_condition, tiles, targets, masks)
                ):
                    if int(row["target_tile_index"]) != view_index:
                        raise ValueError(f"{uid}/{condition}: view order changed")
                    target_row = target_identity[(uid, view_index)]
                    target_sha = sha_bytes(np.ascontiguousarray(target).tobytes())
                    mask_sha = sha_bytes(np.ascontiguousarray(alpha, dtype=np.float32).tobytes())
                    if target_sha != target_row["target_rgb_tile_sha256"]:
                        raise ValueError(f"{uid}/view {view_index}: target RGB SHA mismatch")
                    if mask_sha != target_row["target_silhouette_mask_sha256"]:
                        raise ValueError(f"{uid}/view {view_index}: target mask SHA mismatch")
                    mask = np.asarray(alpha) >= 0.5
                    pred_lab = rgb2lab(pred.astype(np.float32) / 255.0)
                    gt_lab = rgb2lab(target.astype(np.float32) / 255.0)
                    residual = pred_lab[mask] - gt_lab[mask]
                    pink = (residual[:, 1] >= 5.0) & (residual[:, 2] <= -5.0)
                    med = np.median(pred_lab[mask], axis=0)
                    per_view.append({
                        "uid": uid,
                        "cohort": spec["cohort"],
                        "source_cohort": target_row["source_cohort"],
                        "condition": condition,
                        "target_tile_index": view_index,
                        "target_view_id": row["target_view_id"],
                        "is_source_view": row["is_source_view"],
                        "foreground_pixels": int(mask.sum()),
                        "condition_ciede2000_vs_gt_from_runner": float(row["condition_ciede2000_vs_gt"]),
                        "median_residual_l_star": float(np.median(residual[:, 0])),
                        "median_residual_a_star": float(np.median(residual[:, 1])),
                        "median_residual_b_star": float(np.median(residual[:, 2])),
                        "mean_residual_l_star": float(residual[:, 0].mean()),
                        "mean_residual_a_star": float(residual[:, 1].mean()),
                        "mean_residual_b_star": float(residual[:, 2].mean()),
                        "median_output_l_star": float(med[0]),
                        "median_output_a_star": float(med[1]),
                        "median_output_b_star": float(med[2]),
                        "median_output_chroma_c_star": float(np.hypot(med[1], med[2])),
                        "median_output_hue_angle_deg": float(np.degrees(np.arctan2(med[2], med[1])) % 360.0),
                        "magenta_residual_fraction_locked": float(pink.mean()),
                        "output_delta_a_star_vs_gfl": float(row["output_delta_a_star_vs_gfl"]),
                        "output_delta_b_star_vs_gfl": float(row["output_delta_b_star_vs_gfl"]),
                        "prediction_png": str(image_path),
                        "prediction_png_sha256": image_sha,
                        "target_rgb_tile_sha256": target_sha,
                        "target_silhouette_mask_sha256": mask_sha,
                    })

    per_path = RUN / "A_PER_VIEW_COLOR_READOUT.csv"
    source_path = RUN / "A_SOURCE_COLOR_STATISTICS.csv"
    source_by_uid = {row["uid"]: row for row in source_stats}
    object_summary = []
    for uid in sorted(by_uid):
        selected = [row for row in per_view if row["uid"] == uid and row["condition"] == "gfl_baseline"]
        source = next(row for row in selected if row["is_source_view"] == "True")
        unseen = [row for row in selected if row["is_source_view"] == "False"]
        source_colors = source_by_uid[uid]
        object_summary.append({
            "uid": uid,
            "source_cohort": source["source_cohort"],
            "source_view_id": source["target_view_id"],
            "condition_median_a_star": source_colors["condition_median_a_star"],
            "condition_median_b_star": source_colors["condition_median_b_star"],
            "gt_source_median_a_star": source_colors["gt_source_median_a_star"],
            "gt_source_median_b_star": source_colors["gt_source_median_b_star"],
            "gfl_source_median_a_star": source_colors["gfl_source_median_a_star"],
            "gfl_source_median_b_star": source_colors["gfl_source_median_b_star"],
            "condition_to_gt_source_median_ciede2000": source_colors["condition_to_gt_source_median_ciede2000"],
            "condition_to_gfl_source_median_ciede2000": source_colors["condition_to_gfl_source_median_ciede2000"],
            "gfl_source_ciede2000_vs_gt": source["condition_ciede2000_vs_gt_from_runner"],
            "gfl_unseen_mean_ciede2000_vs_gt": mean(row["condition_ciede2000_vs_gt_from_runner"] for row in unseen),
            "gfl_source_median_residual_a_star": source["median_residual_a_star"],
            "gfl_source_median_residual_b_star": source["median_residual_b_star"],
            "gfl_unseen_mean_median_residual_a_star": mean(row["median_residual_a_star"] for row in unseen),
            "gfl_unseen_mean_median_residual_b_star": mean(row["median_residual_b_star"] for row in unseen),
            "gfl_source_magenta_residual_fraction": source["magenta_residual_fraction_locked"],
            "gfl_unseen_mean_magenta_residual_fraction": mean(row["magenta_residual_fraction_locked"] for row in unseen),
            "gfl_unseen_max_magenta_residual_fraction": max(row["magenta_residual_fraction_locked"] for row in unseen),
        })
    object_path = RUN / "A_PER_OBJECT_COLOR_SUMMARY.csv"
    for path, data in ((per_path, per_view), (source_path, source_stats), (object_path, object_summary)):
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    gfl = [row for row in per_view if row["condition"] == "gfl_baseline"]
    source_gfl = [row for row in gfl if row["is_source_view"] == "True"]
    unseen_gfl = [row for row in gfl if row["is_source_view"] == "False"]
    lines = [
        "# Pre-locked Phase A color readouts from Phase B outputs",
        "",
        f"Rows: {len(per_view)} per-view rows across {len(objects)} development objects and {len({row['condition'] for row in per_view})} locked conditions.",
        "The magenta fraction uses the frozen rule Δa* >= +5 and Δb* <= -5 over the target foreground mask >= 0.5. No threshold was selected after viewing outputs.",
        "The robust source condition/GT/output medians use alpha >= 0.75, 3-pixel erosion, and at least 64 pixels; no pixel registration is assumed.",
        "",
        f"GFL source-view mean magenta-residual fraction: {mean(row['magenta_residual_fraction_locked'] for row in source_gfl):.4f}.",
        f"GFL unseen-view mean magenta-residual fraction: {mean(row['magenta_residual_fraction_locked'] for row in unseen_gfl):.4f}.",
        "Per-object GT color errors, Lab residuals, and magenta fractions are in `A_PER_OBJECT_COLOR_SUMMARY.csv`; pixels are not pooled across objects.",
        "",
        f"Per-view CSV SHA-256: `{hashlib.sha256(per_path.read_bytes()).hexdigest()}`.",
        f"Source-statistics CSV SHA-256: `{hashlib.sha256(source_path.read_bytes()).hexdigest()}`.",
        f"Per-object CSV SHA-256: `{hashlib.sha256(object_path.read_bytes()).hexdigest()}`.",
    ]
    (RUN / "A_COLOR_READOUT_SUMMARY.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": "complete", "per_view_rows": len(per_view),
                      "source_objects": len(source_stats), "conditions": len(condition_rows)}, indent=2))


if __name__ == "__main__":
    main()
