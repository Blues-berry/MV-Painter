#!/usr/bin/env python
"""Render paired full-grid comparison for the bounded residual gate prototype."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
FREEZE = ARTIFACT / "SAMPLE_FREEZE.json"
PANELS = [
    ("reference.png", "Reference"), ("native_gfl.png", "GFL"),
    ("native_gc3.png", "C3"), ("gen_linear.png", "Generic Linear"),
    ("layer_llh.png", "LLH"), ("c3_feature_gate.png", "C3 + Gate"),
    ("linear_feature_gate.png", "Linear + Gate"),
]


def method_summary() -> dict[str, dict[str, float]]:
    rows = list(csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open()))
    selected = ["GFL", "C3", "Generic Linear", "LLH", "C3 + Feature Gate", "Linear + Feature Gate"]
    result = {}
    for method in selected:
        subset = [r for r in rows if r["method"] == method]
        result[method] = {
            "n": len(subset),
            "ciede": sum(float(r["mean_fg_ciede2000"]) for r in subset) / len(subset),
            "lpips": sum(float(r["fg_lpips"]) for r in subset) / len(subset),
            "psnr": sum(float(r["fg_psnr"]) for r in subset) / len(subset),
            "edge": sum(float(r["edge_ssim"]) for r in subset) / len(subset),
            "flags": sum(r["purple_cast_flag"] == "True" for r in subset),
        }
    return result


def summary_page(pdf: PdfPages, metrics: dict) -> None:
    fig = plt.figure(figsize=(16.54, 11.69))
    fig.text(0.05, 0.94, "Feature-relative residual gate — development comparison", fontsize=23, weight="bold")
    fig.text(0.05, 0.885,
             "Same 26 frozen failure-diagnostic objects, current checkpoint, six target views, and inference protocol.", fontsize=12)
    fig.text(0.05, 0.85,
             "One mechanism, two schedules: C3 + gate and Generic Linear + gate. Thresholds were calibrated from baseline GFL residuals before this run.",
             fontsize=11, wrap=True)
    methods = list(metrics)
    cells = [[m, str(int(metrics[m]["n"])), f"{metrics[m]['ciede']:.2f}", f"{metrics[m]['lpips']:.3f}",
              f"{metrics[m]['psnr']:.2f}", f"{metrics[m]['edge']:.3f}",
              f"{int(metrics[m]['flags'])}/26"] for m in methods]
    ax = fig.add_axes([0.05, 0.49, 0.91, 0.28]); ax.axis("off")
    table = ax.table(cellText=cells,
                     colLabels=["Method", "n", "CIEDE2000 ↓", "FG-LPIPS ↓", "FG-PSNR ↑", "Edge-SSIM ↑", "Lab flags"],
                     loc="center", cellLoc="left", colLoc="left")
    table.auto_set_font_size(False); table.set_fontsize(11); table.scale(1.0, 1.5)
    fig.text(0.05, 0.39,
             "Primary endpoint is equal-weight mean per-view foreground CIEDE2000. Secondary metrics were recomputed from the saved RGB PNGs with the locked metric implementation.",
             fontsize=10, wrap=True)
    fig.text(0.05, 0.33,
             "All 26 cases are previously viewed or failure-enriched development diagnostics; these results are not independent confirmation. Purple threshold flags are shown with continuous color error and visual review.",
             fontsize=10, wrap=True)
    fig.text(0.05, 0.255,
             "The gate uses g=min(1, tau_depth / q), q=RMS(scale-capped residual)/RMS(pre-adapter feature). It adds no trained parameters or network pass.",
             fontsize=10, wrap=True)
    fig.text(0.05, 0.17,
             "Following pages show full 3-row × 2-column RGB grids for each object. No image is cropped or recolored.",
             fontsize=11, weight="bold")
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def visual_page(pdf: PdfPages, group: list[dict], start: int, total: int) -> None:
    fig = plt.figure(figsize=(18, 12))
    fig.text(0.035, 0.96, f"Paired six-view RGB comparison — objects {start + 1}–{start + len(group)} of {total}",
             fontsize=17, weight="bold")
    left, right = 0.105, 0.985
    width = (right - left) / len(PANELS)
    row_bounds = [(0.53, 0.88), (0.10, 0.45)]
    for col, (_, label) in enumerate(PANELS):
        fig.text(left + col * width + width / 2, 0.915, label,
                 ha="center", va="center", fontsize=10, weight="bold")
    for row_index, sample in enumerate(group):
        sid = sample["sample_id"]
        y0, y1 = row_bounds[row_index]
        fig.text(0.025, y1 - 0.02, sid, fontsize=10, weight="bold", va="top")
        for col, (filename, _) in enumerate(PANELS):
            path = ARTIFACT / "raw_rgb" / sid / filename
            ax = fig.add_axes([left + col * width + 0.012, y0, width - 0.024, y1 - y0])
            ax.imshow(Image.open(path).convert("RGB"), interpolation="nearest")
            ax.set_axis_off()
    fig.text(0.035, 0.035,
             "Each panel is an unmodified 512×768 RGB grid containing the same six target views. Full assets and SHA-256 rows are in raw_rgb/ and logs/.",
             fontsize=9)
    pdf.savefig(fig, dpi=160); plt.close(fig)


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    samples = [s for s in freeze["samples"]
               if s["source"] == "01549_fig4_fig6_original_object"] + [
                   s for s in freeze["samples"]
                   if s["source"] != "01549_fig4_fig6_original_object"]
    path = ARTIFACT / "STAGE2_GATE_COMPARISON.pdf"
    with PdfPages(path, metadata={"Title": "Residual gate paired RGB diagnostic comparison"}) as pdf:
        summary_page(pdf, method_summary())
        for offset in range(0, len(samples), 2):
            visual_page(pdf, samples[offset:offset + 2], offset, len(samples))
    print(f"wrote {path} with 1 summary page + {(len(samples) + 1) // 2} visual pages")


if __name__ == "__main__":
    main()
