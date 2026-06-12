#!/usr/bin/env python3
"""
Phase 5: Visual Audit Grid Generator
Generates comparison grids from existing visualization images.
"""
import os
import csv
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path("/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1")
CLEAN_VIS = BASE / "eval_300obj_clean" / "visualizations"
S1P25_VIS = BASE / "scale_1p25_300obj" / "visualizations"
OUT_DIR = BASE / "visual_audit_scale_1p25"


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def sf(v):
    try:
        return float(v)
    except:
        return None


def get_worst_objects(csv_path, metric_col, n=20, ascending=True):
    """Get N worst objects by a metric column. ascending=True means lowest (worst for positive metrics)."""
    rows = load_csv(csv_path)
    scored = []
    for r in rows:
        v = sf(r.get(metric_col))
        if v is not None:
            scored.append((int(float(r["object_idx"])), v))
    scored.sort(key=lambda x: x[1], reverse=not ascending)
    return [s[0] for s in scored[:n]]


def get_regression_objects(n=20):
    """Get objects where scale=1.25 FG SSIM regressed most vs scale=1.0."""
    diff_path = BASE / "scale_1p25_vs_1p00_per_object_diff.csv"
    rows = load_csv(diff_path)
    scored = []
    for r in rows:
        d = sf(r.get("delta_fg_ssim_diff"))
        if d is not None:
            scored.append((int(float(r["object_idx"])), d))
    scored.sort(key=lambda x: x[1])  # worst (most negative) first
    return [s[0] for s in scored[:n]]


def make_grid(images_dict, title, cell_w=256, cell_h=384):
    """
    Create a comparison grid.
    images_dict: {col_header: {row_label: PIL.Image}}
    Returns PIL.Image grid.
    """
    col_headers = list(images_dict.keys())
    row_labels = list(next(iter(images_dict.values())).keys())
    n_cols = len(col_headers)
    n_rows = len(row_labels)

    label_w = 60
    header_h = 30
    gap = 2
    total_w = label_w + n_cols * (cell_w + gap) + gap
    total_h = header_h + n_rows * (cell_h + gap) + gap

    grid = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(grid)

    # Draw column headers
    for j, hdr in enumerate(col_headers):
        x = label_w + j * (cell_w + gap) + gap + cell_w // 2
        draw.text((x, 5), hdr, fill=(0, 0, 0), anchor="mt")

    # Draw row labels and images
    for i, label in enumerate(row_labels):
        y = header_h + i * (cell_h + gap) + gap
        draw.text((5, y + cell_h // 2), label, fill=(0, 0, 0), anchor="lm")
        for j, hdr in enumerate(col_headers):
            x = label_w + j * (cell_w + gap) + gap
            img = images_dict[hdr].get(label)
            if img is not None:
                resized = img.resize((cell_w, cell_h), Image.LANCZOS)
                grid.paste(resized, (x, y))
            else:
                draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(200, 200, 200))
                draw.text((x + cell_w // 2, y + cell_h // 2), "N/A", fill=(150, 150, 150), anchor="mm")

    return grid


def load_vis(vis_dir, obj_idx, suffix_map):
    """Load visualization images for an object. Returns {name: PIL.Image}."""
    prefix = f"obj_{obj_idx:03d}"
    result = {}
    for name, suffix in suffix_map.items():
        path = vis_dir / f"{prefix}_{suffix}.png"
        if path.exists():
            result[name] = Image.open(path)
    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    clean_csv = BASE / "eval_300obj_clean" / "per_object_metrics_fixed.csv"
    s1p25_csv = BASE / "scale_1p25_300obj" / "per_object_metrics.csv"

    # Identify worst cases
    print("Identifying worst cases...")
    worst_fg_ssim = get_worst_objects(clean_csv, "foreground_adapter_ssim", 20, ascending=True)
    worst_edge_ssim = get_worst_objects(clean_csv, "edge_adapter_ssim", 20, ascending=True)
    worst_fg_psnr = get_worst_objects(clean_csv, "foreground_adapter_psnr", 20, ascending=True)
    regression_objs = get_regression_objects(20)

    # Also get scale=1.25 worst
    worst_fg_ssim_1p25 = get_worst_objects(s1p25_csv, "adapter_fg_ssim", 20, ascending=True)

    summary_lines = []
    summary_lines.append("# Phase 5: Visual Audit Summary\n")
    summary_lines.append(f"**Date:** 2026-06-11\n")
    summary_lines.append(f"**Limitation:** scale=1.25 visualizations only available for objects 0-4.\n")
    summary_lines.append(f"Cross-scale comparison grids limited to those 5 objects.\n\n")

    # === Grid 1: Cross-scale comparison for objects 0-4 (both scales available) ===
    print("Generating cross-scale comparison grid for objects 0-4...")
    shared_objs = [0, 1, 2, 3, 4]

    clean_suffix = {"GT": "gt", "Official": "original", "Adapter 1.0": "adapter",
                    "Mask": "mask", "Edge": "edge_mask"}
    s1p25_suffix = {"GT": "gt", "Official": "orig", "Adapter 1.25": "adapter"}

    # Build grid: rows = objects, columns = GT, Official, Adapter 1.0, Adapter 1.25, Mask, Edge
    grid_data = {}
    for col in ["GT", "Official", "Adapter 1.0", "Adapter 1.25", "Mask", "Edge"]:
        grid_data[col] = {}

    for obj in shared_objs:
        clean_imgs = load_vis(CLEAN_VIS, obj, clean_suffix)
        s1p25_imgs = load_vis(S1P25_VIS, obj, s1p25_suffix)

        label = f"obj_{obj:03d}"
        grid_data["GT"][label] = clean_imgs.get("GT") or s1p25_imgs.get("GT")
        grid_data["Official"][label] = clean_imgs.get("Official") or s1p25_imgs.get("Official")
        grid_data["Adapter 1.0"][label] = clean_imgs.get("Adapter 1.0")
        grid_data["Adapter 1.25"][label] = s1p25_imgs.get("Adapter 1.25")
        grid_data["Mask"][label] = clean_imgs.get("Mask")
        grid_data["Edge"][label] = clean_imgs.get("Edge")

    grid = make_grid(grid_data, "Cross-Scale Comparison", cell_w=170, cell_h=256)
    out_path = OUT_DIR / "cross_scale_objects_0to4.png"
    grid.save(out_path)
    print(f"  Saved: {out_path}")
    summary_lines.append(f"## Cross-Scale Comparison (Objects 0-4)\n\n")
    summary_lines.append(f"![Cross-scale comparison](cross_scale_objects_0to4.png)\n\n")

    # === Grid 2: Worst FG SSIM objects (scale=1.0 only, from eval_300obj_clean) ===
    print("Generating worst FG SSIM grid (scale=1.0)...")
    grid_data = {}
    for col in ["GT", "Official", "Adapter 1.0", "Error Official", "Error Adapter", "Mask"]:
        grid_data[col] = {}

    for obj in worst_fg_ssim[:10]:
        imgs = load_vis(CLEAN_VIS, obj, {
            "GT": "gt", "Official": "original", "Adapter 1.0": "adapter",
            "Error Official": "original_error", "Error Adapter": "adapter_error",
            "Mask": "mask"
        })
        label = f"obj_{obj:03d}"
        for col in grid_data:
            grid_data[col][label] = imgs.get(col)

    grid = make_grid(grid_data, "Worst FG SSIM (scale=1.0)", cell_w=170, cell_h=256)
    out_path = OUT_DIR / "worst_fg_ssim_scale1p0.png"
    grid.save(out_path)
    print(f"  Saved: {out_path}")
    summary_lines.append(f"## Worst FG SSIM Objects (scale=1.0)\n\n")
    summary_lines.append(f"Objects: {worst_fg_ssim[:10]}\n\n")
    summary_lines.append(f"![Worst FG SSIM](worst_fg_ssim_scale1p0.png)\n\n")

    # === Grid 3: Worst Edge SSIM objects ===
    print("Generating worst Edge SSIM grid...")
    grid_data = {}
    for col in ["GT", "Official", "Adapter 1.0", "Edge", "Error Adapter"]:
        grid_data[col] = {}

    for obj in worst_edge_ssim[:10]:
        imgs = load_vis(CLEAN_VIS, obj, {
            "GT": "gt", "Official": "original", "Adapter 1.0": "adapter",
            "Edge": "edge_mask", "Error Adapter": "adapter_error"
        })
        label = f"obj_{obj:03d}"
        for col in grid_data:
            grid_data[col][label] = imgs.get(col)

    grid = make_grid(grid_data, "Worst Edge SSIM (scale=1.0)", cell_w=170, cell_h=256)
    out_path = OUT_DIR / "worst_edge_ssim_scale1p0.png"
    grid.save(out_path)
    print(f"  Saved: {out_path}")
    summary_lines.append(f"## Worst Edge SSIM Objects (scale=1.0)\n\n")
    summary_lines.append(f"Objects: {worst_edge_ssim[:10]}\n\n")
    summary_lines.append(f"![Worst Edge SSIM](worst_edge_ssim_scale1p0.png)\n\n")

    # === Grid 4: Regression objects (scale=1.25 worse than 1.0) ===
    print("Generating regression cases grid...")
    # For regression objects, we can only show scale=1.0 images (scale=1.25 vis not available for these)
    grid_data = {}
    for col in ["GT", "Official", "Adapter 1.0", "Error Adapter", "Mask"]:
        grid_data[col] = {}

    for obj in regression_objs[:10]:
        imgs = load_vis(CLEAN_VIS, obj, {
            "GT": "gt", "Official": "original", "Adapter 1.0": "adapter",
            "Error Adapter": "adapter_error", "Mask": "mask"
        })
        label = f"obj_{obj:03d}"
        for col in grid_data:
            grid_data[col][label] = imgs.get(col)

    grid = make_grid(grid_data, "FG SSIM Regression Cases (scale=1.25 vs 1.0)", cell_w=170, cell_h=256)
    out_path = OUT_DIR / "regression_cases.png"
    grid.save(out_path)
    print(f"  Saved: {out_path}")
    summary_lines.append(f"## FG SSIM Regression Cases (scale=1.25 vs scale=1.0)\n\n")
    summary_lines.append(f"Objects: {regression_objs[:10]}\n\n")
    summary_lines.append(f"**Note:** scale=1.25 visualizations not available for these objects.\n")
    summary_lines.append(f"Showing scale=1.0 images only. See per-object diff CSV for metrics.\n\n")
    summary_lines.append(f"![Regression cases](regression_cases.png)\n\n")

    # === Grid 5: Best improvements ===
    print("Generating best improvement cases...")
    diff_path = BASE / "scale_1p25_vs_1p00_per_object_diff.csv"
    diff_rows = load_csv(diff_path)
    best_objs = []
    for r in diff_rows:
        d = sf(r.get("delta_fg_ssim_diff"))
        if d is not None:
            best_objs.append((int(float(r["object_idx"])), d))
    best_objs.sort(key=lambda x: x[1], reverse=True)
    best_objs = [b[0] for b in best_objs[:10]]

    grid_data = {}
    for col in ["GT", "Official", "Adapter 1.0", "Error Adapter", "Mask"]:
        grid_data[col] = {}

    for obj in best_objs:
        imgs = load_vis(CLEAN_VIS, obj, {
            "GT": "gt", "Official": "original", "Adapter 1.0": "adapter",
            "Error Adapter": "adapter_error", "Mask": "mask"
        })
        label = f"obj_{obj:03d}"
        for col in grid_data:
            grid_data[col][label] = imgs.get(col)

    grid = make_grid(grid_data, "Best FG SSIM Improvement (scale=1.25 vs 1.0)", cell_w=170, cell_h=256)
    out_path = OUT_DIR / "best_improvements.png"
    grid.save(out_path)
    print(f"  Saved: {out_path}")
    summary_lines.append(f"## Best FG SSIM Improvement Cases\n\n")
    summary_lines.append(f"Objects: {best_objs}\n\n")
    summary_lines.append(f"![Best improvements](best_improvements.png)\n\n")

    # === Summary statistics ===
    summary_lines.append("## Summary Statistics\n\n")
    summary_lines.append(f"- Worst FG SSIM (scale=1.0): objects {worst_fg_ssim[:5]}\n")
    summary_lines.append(f"- Worst Edge SSIM (scale=1.0): objects {worst_edge_ssim[:5]}\n")
    summary_lines.append(f"- Worst FG PSNR (scale=1.0): objects {worst_fg_psnr[:5]}\n")
    summary_lines.append(f"- Worst FG SSIM (scale=1.25): objects {worst_fg_ssim_1p25[:5]}\n")
    summary_lines.append(f"- Most regressed (1.25 vs 1.0): objects {regression_objs[:5]}\n")
    summary_lines.append(f"- Most improved (1.25 vs 1.0): objects {best_objs[:5]}\n\n")

    summary_lines.append("## Limitations\n\n")
    summary_lines.append("1. scale=1.25 visualizations only saved for objects 0-4 (5 of 300).\n")
    summary_lines.append("2. Cross-scale comparison grids limited to objects 0-4.\n")
    summary_lines.append("3. For full visual audit of worst cases, re-run eval_scale_inline.py with --save_vis_all flag.\n")
    summary_lines.append("4. Error maps only available in eval_300obj_clean (scale=1.0).\n")

    # Write summary
    with open(OUT_DIR / "visual_audit_scale_1p25_summary.md", "w") as f:
        f.write("\n".join(summary_lines))
    print(f"\nSummary: {OUT_DIR / 'visual_audit_scale_1p25_summary.md'}")

    # List generated files
    print(f"\nGenerated files:")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
