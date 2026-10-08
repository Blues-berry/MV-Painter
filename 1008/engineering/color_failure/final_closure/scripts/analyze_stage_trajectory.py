#!/usr/bin/env python3
"""Measure late denoising snapshots against one frozen, identified Fig. 4 case."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT.parent
UID = "eac4b392b7b448a2b6ec77e8936abe1b"
SAMPLE_ID = "fig4_row1"
TRACE_ROOT = ROOT / "repro/pink_case_stage_trace_py310/traces" / UID
OUTPUT_ROOT = ROOT / "repro/pink_case_stage_trace_py310/run/predictions"
METHODS = {
    "No Adapter": ("no_adapter", "no_adapter.png"),
    "GFL": ("native_gfl", "native_gfl.png"),
    "LLH": ("layer_llh", "layer_llh.png"),
}
STEPS = (25, 33, 40, 45, 49)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, mode: str = "RGB") -> np.ndarray:
    return np.asarray(Image.open(path).convert(mode))


def foreground_metrics(pred: np.ndarray, reference: np.ndarray, mask: np.ndarray) -> dict:
    per_view_de, per_view_da, per_view_db, per_view_mae = [], [], [], []
    for view in range(6):
        row, col = divmod(view, 2)
        ys = slice(row * 256, (row + 1) * 256)
        xs = slice(col * 256, (col + 1) * 256)
        fg = mask[ys, xs]
        ref_tile, pred_tile = reference[ys, xs], pred[ys, xs]
        lab_ref, lab_pred = rgb2lab(ref_tile), rgb2lab(pred_tile)
        delta = lab_pred - lab_ref
        per_view_de.append(float(deltaE_ciede2000(lab_ref, lab_pred)[fg].mean()))
        per_view_da.append(float(delta[..., 1][fg].mean()))
        per_view_db.append(float(delta[..., 2][fg].mean()))
        per_view_mae.append(float(np.abs(pred_tile[fg] - ref_tile[fg]).mean()))
    return {
        "mean_fg_ciede2000": float(np.mean(per_view_de)),
        "mean_delta_a_star": float(np.mean(per_view_da)),
        "mean_delta_b_star": float(np.mean(per_view_db)),
        "mean_fg_rgb_mae_0_1": float(np.mean(per_view_mae)),
        "per_view_ciede2000": per_view_de,
        "per_view_delta_a_star": per_view_da,
        "per_view_delta_b_star": per_view_db,
    }


def main() -> None:
    reference_path = ARTIFACT / "raw_rgb" / SAMPLE_ID / "reference.png"
    mask_path = ARTIFACT / "masks" / f"{SAMPLE_ID}.png"
    reference = load(reference_path).astype(np.float32) / 255.0
    mask = load(mask_path, "L") > 127
    rows = []
    for label, (condition, final_name) in METHODS.items():
        paths = [(step, TRACE_ROOT / f"{condition}_after_step{step:02d}.png") for step in STEPS]
        paths.append(("final_saved_png", OUTPUT_ROOT / condition / f"{UID}.png"))
        for step, image_path in paths:
            pred = load(image_path).astype(np.float32) / 255.0
            metrics = foreground_metrics(pred, reference, mask)
            rows.append({
                "sample_id": SAMPLE_ID,
                "uid": UID,
                "condition": label,
                "step_after_scheduler_update": step,
                "stage": "late" if isinstance(step, int) else "final",
                "runtime": "Python 3.10.20 / torch 2.7.0+cu128 / diffusers 0.20.2",
                "decoded_rgb_path": str(image_path),
                "decoded_rgb_sha256": sha(image_path),
                "reference_sha256": sha(reference_path),
                "mask_sha256": sha(mask_path),
                **metrics,
                "metric_caveat": (
                    "decoded intermediate latent snapshot; descriptive trajectory only, not final quality"
                    if isinstance(step, int) and step < 49 else
                    "final saved RGB; byte-identical to the corresponding frozen P1 raw_rgb output"
                ),
            })

    output = ROOT / "P1_STAGE_TRAJECTORY.csv"
    with output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} step/final rows to {output}")


if __name__ == "__main__":
    main()
