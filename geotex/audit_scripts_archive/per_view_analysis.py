#!/usr/bin/env python3
"""
Phase 8a: Per-View Analysis
Split 512x768 images into 6 views (3 columns x 2 rows of 256x256),
compute per-view PSNR/SSIM from existing eval_300obj_clean visualizations.
"""
import os
import csv
import numpy as np
from pathlib import Path
from PIL import Image

BASE = Path("/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1")
VIS_DIR = BASE / "eval_300obj_clean" / "visualizations"
OUT_DIR = BASE


def pil_to_numpy(img):
    return np.array(img).astype(np.float32) / 255.0


def compute_psnr_np(pred, target):
    mse = np.mean((pred - target) ** 2)
    if mse < 1e-10:
        return 100.0
    return 10 * np.log10(1.0 / mse)


def compute_ssim_np(pred, target, win_size=7):
    """Simple SSIM on numpy arrays."""
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    from scipy.ndimage import uniform_filter
    mu1 = uniform_filter(pred, size=win_size)
    mu2 = uniform_filter(target, size=win_size)
    sigma1_sq = uniform_filter(pred ** 2, size=win_size) - mu1 ** 2
    sigma2_sq = uniform_filter(target ** 2, size=win_size) - mu2 ** 2
    sigma12 = uniform_filter(pred * target, size=win_size) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))
    return float(np.mean(np.clip(ssim_map, 0, 1)))


def split_views(img, n_cols=3, n_rows=2):
    """Split image into n_cols x n_rows tiles."""
    w, h = img.size
    tile_w, tile_h = w // n_cols, h // n_rows
    views = []
    for r in range(n_rows):
        for c in range(n_cols):
            box = (c * tile_w, r * tile_h, (c + 1) * tile_w, (r + 1) * tile_h)
            views.append(img.crop(box))
    return views


def main():
    num_objects = 300
    results = []

    print(f"Per-view analysis: {num_objects} objects, 6 views each")

    for obj_idx in range(num_objects):
        prefix = f"obj_{obj_idx:03d}"
        gt_path = VIS_DIR / f"{prefix}_gt.png"
        adapter_path = VIS_DIR / f"{prefix}_adapter.png"
        orig_path = VIS_DIR / f"{prefix}_original.png"

        if not all(p.exists() for p in [gt_path, adapter_path, orig_path]):
            continue

        gt_img = Image.open(gt_path)
        adapter_img = Image.open(adapter_path)
        orig_img = Image.open(orig_path)

        gt_views = split_views(gt_img)
        adapter_views = split_views(adapter_img)
        orig_views = split_views(orig_img)

        r = {"object_idx": obj_idx}

        for v_idx in range(6):
            gt_np = pil_to_numpy(gt_views[v_idx])
            adapter_np = pil_to_numpy(adapter_views[v_idx])
            orig_np = pil_to_numpy(orig_views[v_idx])

            view_label = f"view_{v_idx}"

            psnr_orig = compute_psnr_np(orig_np, gt_np)
            psnr_adapter = compute_psnr_np(adapter_np, gt_np)
            ssim_orig = compute_ssim_np(orig_np, gt_np)
            ssim_adapter = compute_ssim_np(adapter_np, gt_np)

            r[f"{view_label}_orig_psnr"] = psnr_orig
            r[f"{view_label}_adapter_psnr"] = psnr_adapter
            r[f"{view_label}_delta_psnr"] = psnr_adapter - psnr_orig
            r[f"{view_label}_orig_ssim"] = ssim_orig
            r[f"{view_label}_adapter_ssim"] = ssim_adapter
            r[f"{view_label}_delta_ssim"] = ssim_adapter - ssim_orig

        results.append(r)

        if obj_idx % 50 == 0:
            print(f"  Object {obj_idx}/{num_objects}")

    # Save CSV
    if results:
        fieldnames = list(results[0].keys())
        csv_path = OUT_DIR / "per_view_metrics.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved: {csv_path}")

    # Compute per-view summary
    summary = {}
    for v_idx in range(6):
        for metric in ["delta_psnr", "delta_ssim", "adapter_psnr", "adapter_ssim"]:
            key = f"view_{v_idx}_{metric}"
            vals = [r[key] for r in results if key in r]
            if vals:
                summary[key] = {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)),
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals)),
                }

    # Write report
    report_path = OUT_DIR / "per_view_analysis.md"
    with open(report_path, "w") as f:
        f.write("# Phase 8a: Per-View Analysis\n\n")
        f.write(f"**Date:** 2026-06-11\n")
        f.write(f"**Objects:** {len(results)}\n")
        f.write(f"**View layout:** 3 columns x 2 rows (256x256 each from 512x768)\n\n")

        f.write("## View Layout\n\n")
        f.write("```\n")
        f.write("| View 0 | View 1 | View 2 |\n")
        f.write("| View 3 | View 4 | View 5 |\n")
        f.write("```\n\n")

        f.write("## Per-View Delta Summary (adapter - orig)\n\n")
        f.write("| View | ΔPSNR Mean | ΔPSNR Std | ΔSSIM Mean | ΔSSIM Std |\n")
        f.write("|------|-----------|-----------|-----------|----------|\n")
        for v_idx in range(6):
            dp = summary.get(f"view_{v_idx}_delta_psnr", {})
            ds = summary.get(f"view_{v_idx}_delta_ssim", {})
            f.write(f"| {v_idx} | {dp.get('mean', 0):+.3f} | {dp.get('std', 0):.3f} | "
                    f"{ds.get('mean', 0):+.4f} | {ds.get('std', 0):.4f} |\n")

        f.write("\n## Per-View Absolute Metrics\n\n")
        f.write("| View | Adapter PSNR | Adapter SSIM |\n")
        f.write("|------|-------------|-------------|\n")
        for v_idx in range(6):
            ap = summary.get(f"view_{v_idx}_adapter_psnr", {})
            as_ = summary.get(f"view_{v_idx}_adapter_ssim", {})
            f.write(f"| {v_idx} | {ap.get('mean', 0):.3f} | {as_.get('mean', 0):.4f} |\n")

        f.write("\n## Interpretation\n\n")
        f.write("Views 0-2 are the top row, views 3-5 are the bottom row.\n")
        f.write("Consistent improvement across all views indicates the adapter works uniformly.\n")
        f.write("If certain views show less improvement, it may indicate view-dependent issues.\n")

    print(f"Report: {report_path}")
    return summary


if __name__ == "__main__":
    main()
