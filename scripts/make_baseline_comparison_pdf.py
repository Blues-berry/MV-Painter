#!/usr/bin/env python
"""Create a full-grid visual comparison PDF for the frozen diagnostic set."""
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
METHODS = [
    ("reference.png", "Reference"),
    ("no_adapter.png", "No Adapter"),
    ("native_gfl.png", "GFL"),
    ("native_gfh.png", "GFH"),
    ("native_gc3.png", "C3"),
    ("gen_linear.png", "Generic Linear"),
    ("layer_llh.png", "LLH"),
]


def metrics_by_method() -> dict:
    rows = list(csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open()))
    out = {}
    for method in dict.fromkeys(r["method"] for r in rows):
        method_rows = [r for r in rows if r["method"] == method]
        out[method] = {
            "mean_ciede": sum(float(r["mean_fg_ciede2000"]) for r in method_rows) / len(method_rows),
            "purple_flags": sum(r["purple_cast_flag"] == "True" for r in method_rows),
        }
    return out


def summary_page(pdf: PdfPages, freeze: dict, metrics: dict) -> None:
    fig = plt.figure(figsize=(16.54, 11.69))
    fig.text(0.05, 0.94, "R1 color failure — paired RGB baseline comparison", fontsize=24, weight="bold")
    fig.text(0.05, 0.885,
             "Failure-enriched development diagnostics: 26 objects (six exact 01549 Fig. 4/6 cases + 20 reused Fresh-C panels).",
             fontsize=13)
    fig.text(0.05, 0.845,
             "All prediction panels are complete 3-row × 2-column grids of six RGB views. The PNG sources are preserved separately at 512×768.",
             fontsize=12)
    fig.text(0.05, 0.80,
             "Protocol: checkpoint 0618d6b2…e0114c0 · unique6 views [0,15,12,16,13,14] · 50 Euler steps · seed 42 + source-list index.",
             fontsize=12)
    fig.text(0.05, 0.755,
             "Historical Fig. 4/6 outputs were regenerated under the locked runner; Fresh-C outputs use paired current reruns because archived PNGs did not reproduce byte-for-byte.",
             fontsize=12)
    fig.text(0.05, 0.69, "Per-method descriptive results", fontsize=16, weight="bold")
    labels = ["No Adapter", "GFL", "GFH", "C3", "Generic Linear", "LLH"]
    table_rows = []
    for label in labels:
        value = metrics[label]
        table_rows.append([label, f"{value['mean_ciede']:.2f}", f"{value['purple_flags']}/26"])
    ax = fig.add_axes([0.05, 0.45, 0.58, 0.20])
    ax.axis("off")
    table = ax.table(cellText=table_rows, colLabels=["Condition", "Mean object CIEDE2000 ↓", "Strict Lab flags"],
                     loc="center", cellLoc="left", colLoc="left", colWidths=[0.35, 0.42, 0.23])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.0, 1.6)
    fig.text(0.05, 0.39,
             "CIEDE2000 is the equal-weight mean of six per-view foreground scores. Purple flag was frozen as mean Δa* ≥ 5, mean Δb* ≤ −5, and mean CIEDE2000 ≥ 5.",
             fontsize=11, wrap=True)
    fig.text(0.05, 0.355,
             "No object crossed this strict vector-shift flag. That threshold result does not rule out a visible pink/lavender cast; continuous color error and the panel-by-panel visual review are reported separately.",
             fontsize=11, wrap=True)
    fig.text(0.05, 0.30,
             "These selected and previously viewed objects are diagnostics, not an independent confirmation cohort. Colors are measured from the saved RGB grids in sRGB-to-Lab space.",
             fontsize=11, wrap=True)
    fig.text(0.05, 0.235,
             "Interpretation is limited to 2D generated RGB. UV projection, texture baking, glTF export, and unseen-view rendering are not measured by this comparison.",
             fontsize=11, wrap=True)
    fig.text(0.05, 0.15,
             "Visual pages follow: each object row shows Reference / No Adapter / GFL / GFH / C3 / Generic Linear / LLH. No panel is cropped or recolored.",
             fontsize=13, weight="bold")
    fig.text(0.05, 0.08, "See ROOT_CAUSE_EXPERIMENT.md for pipeline audit, residual intervention results, and limits.", fontsize=11)
    pdf.savefig(fig, dpi=160, bbox_inches="tight")
    plt.close(fig)


def visual_page(pdf: PdfPages, group: list[dict], start_index: int, total: int) -> None:
    fig = plt.figure(figsize=(16.54, 11.69))
    fig.text(0.035, 0.955, f"Paired RGB comparison — objects {start_index + 1}–{start_index + len(group)} of {total}",
             fontsize=17, weight="bold")
    left, right = 0.105, 0.985
    width = (right - left) / len(METHODS)
    row_bounds = [(0.535, 0.88), (0.105, 0.45)]
    for col, (_, label) in enumerate(METHODS):
        fig.text(left + col * width + width / 2, 0.915, label, ha="center", va="center", fontsize=11, weight="bold")
    for row_index, sample in enumerate(group):
        sample_id = sample["sample_id"]
        y0, y1 = row_bounds[row_index]
        fig.text(0.025, y1 - 0.025, sample_id, fontsize=10, weight="bold", va="top")
        fig.text(0.025, y1 - 0.070, sample["uid"], fontsize=7, va="top", wrap=True)
        short_source = "01549 Fig. 4/6" if sample["source"] == "01549_fig4_fig6_original_object" else "Fresh-C"
        fig.text(0.025, y1 - 0.13, short_source, fontsize=8, va="top")
        for col, (filename, _) in enumerate(METHODS):
            ax = fig.add_axes([left + col * width + 0.015, y0, width - 0.03, y1 - y0])
            ax.imshow(Image.open(ARTIFACT / "raw_rgb" / sample_id / filename).convert("RGB"), interpolation="nearest")
            ax.set_axis_off()
    fig.text(0.035, 0.035,
             "Each image is an unmodified full 3-row × 2-column six-view RGB grid; PDF display scales panels to fit. Full-resolution PNGs and SHA-256 manifest are in raw_rgb/ and logs/.",
             fontsize=9)
    pdf.savefig(fig, dpi=160)
    plt.close(fig)


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    metrics = metrics_by_method()
    pdf_path = ARTIFACT / "BASELINE_COMPARISON.pdf"
    with PdfPages(pdf_path, metadata={"Title": "R1 color failure paired RGB baseline comparison"}) as pdf:
        summary_page(pdf, freeze, metrics)
        samples = [s for s in freeze["samples"]
                   if s["source"] == "01549_fig4_fig6_original_object"] + [
                       s for s in freeze["samples"]
                       if s["source"] != "01549_fig4_fig6_original_object"
                   ]
        for offset in range(0, len(samples), 2):
            visual_page(pdf, samples[offset:offset + 2], offset, len(samples))
    print(f"wrote {pdf_path} with 1 summary page + {(len(freeze['samples']) + 1) // 2} visual pages")


if __name__ == "__main__":
    main()
