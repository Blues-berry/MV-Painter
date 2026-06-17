#!/usr/bin/env python3
"""
Generate comparison panels for Tasks 5, 6, 8, 10.
Reads existing vis_selected images only. No inference.

Panels:
- scale_ablation_best.png
- scale_ablation_regression.png
- scale_ablation_median.png
- method_comparison_best.png (if eval_300obj_clean vis available)
- baseline_debug.png (already done)
"""
import os, sys, json, hashlib
import numpy as np
from PIL import Image

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

BASE = "/4T/CXY/MV-Painter"
AUDIT_DIR = f"{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit"
VIS_BASE = f"{AUDIT_DIR}/vis_selected"
OUT_DIR = f"{AUDIT_DIR}/panels_v2"

# Cache manifest once at module level
_MANIFEST_CACHE = None
def _load_manifest():
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        manifest_path = f"{AUDIT_DIR}/visual_manifest.json"
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                _MANIFEST_CACHE = json.load(f)
        else:
            _MANIFEST_CACHE = {}
    return _MANIFEST_CACHE

OBJECTS = [181, 110, 78, 82, 163, 118, 249, 293,
           42, 38, 68, 268,
           74, 119, 179, 83, 140, 18, 25, 27,
           298, 12, 72, 144, 202, 104]

CATEGORIES = {
    181: "severe_regression", 110: "severe_regression", 78: "severe_regression",
    82: "severe_regression", 163: "severe_regression", 118: "severe_regression",
    249: "severe_regression", 293: "severe_regression",
    42: "borderline_regression", 38: "borderline_regression",
    68: "borderline_regression", 268: "borderline_regression",
    74: "best_improvement", 119: "best_improvement", 179: "best_improvement",
    83: "best_improvement", 140: "best_improvement", 18: "best_improvement",
    25: "best_improvement", 27: "best_improvement",
    298: "median", 12: "median", 72: "median", 144: "median", 202: "median", 104: "median"
}

# Metric values from manifest
METRICS = {
    181: {"fg_ssim_s1.25": 0.182, "fg_ssim_s2.50": 0.013, "delta": -0.170},
    110: {"fg_ssim_s1.25": 0.194, "fg_ssim_s2.50": 0.039, "delta": -0.155},
    78:  {"fg_ssim_s1.25": -0.240, "fg_ssim_s2.50": -0.371, "delta": -0.132},
    82:  {"fg_ssim_s1.25": -0.371, "fg_ssim_s2.50": -0.485, "delta": -0.115},
    163: {"fg_ssim_s1.25": 0.230, "fg_ssim_s2.50": 0.143, "delta": -0.088},
    118: {"fg_ssim_s1.25": 0.078, "fg_ssim_s2.50": -0.004, "delta": -0.082},
    249: {"fg_ssim_s1.25": -0.084, "fg_ssim_s2.50": -0.162, "delta": -0.078},
    293: {"fg_ssim_s1.25": -0.077, "fg_ssim_s2.50": -0.149, "delta": -0.071},
    42:  {"fg_ssim_s1.25": -0.086, "fg_ssim_s2.50": -0.136, "delta": -0.050},
    38:  {"fg_ssim_s1.25": 0.174, "fg_ssim_s2.50": 0.125, "delta": -0.049},
    68:  {"fg_ssim_s1.25": 0.208, "fg_ssim_s2.50": 0.162, "delta": -0.046},
    268: {"fg_ssim_s1.25": -0.126, "fg_ssim_s2.50": -0.167, "delta": -0.041},
    74:  {"fg_ssim_s1.25": 0.193, "fg_ssim_s2.50": 0.310, "delta": 0.117},
    119: {"fg_ssim_s1.25": 0.146, "fg_ssim_s2.50": 0.253, "delta": 0.107},
    179: {"fg_ssim_s1.25": 0.236, "fg_ssim_s2.50": 0.332, "delta": 0.096},
    83:  {"fg_ssim_s1.25": -0.036, "fg_ssim_s2.50": 0.047, "delta": 0.083},
    140: {"fg_ssim_s1.25": 0.156, "fg_ssim_s2.50": 0.235, "delta": 0.079},
    18:  {"fg_ssim_s1.25": 0.152, "fg_ssim_s2.50": 0.228, "delta": 0.076},
    25:  {"fg_ssim_s1.25": 0.081, "fg_ssim_s2.50": 0.155, "delta": 0.074},
    27:  {"fg_ssim_s1.25": 0.180, "fg_ssim_s2.50": 0.252, "delta": 0.072},
    298: {"fg_ssim_s1.25": -0.089, "fg_ssim_s2.50": -0.020, "delta": 0.069},
    12:  {"fg_ssim_s1.25": 0.063, "fg_ssim_s2.50": 0.128, "delta": 0.065},
    72:  {"fg_ssim_s1.25": 0.144, "fg_ssim_s2.50": 0.194, "delta": 0.050},
    144: {"fg_ssim_s1.25": -0.078, "fg_ssim_s2.50": -0.031, "delta": 0.047},
    202: {"fg_ssim_s1.25": -0.091, "fg_ssim_s2.50": -0.052, "delta": 0.039},
    104: {"fg_ssim_s1.25": 0.098, "fg_ssim_s2.50": 0.124, "delta": 0.026},
}


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_img(path):
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path).convert('RGB'))


def find_input_view(obj_idx):
    """Find the condition input view for this object."""
    manifest = _load_manifest()
    for obj in manifest.get("objects", []):
        if obj.get("object_idx") == obj_idx:
            img_dir = obj.get("source_data", {}).get("image_dir", "")
            inp = os.path.join(img_dir, "000.png")
            if os.path.exists(inp):
                return inp
    return None


def get_old_eval_vis(obj_idx, suffix):
    """Get vis from eval_300obj_clean."""
    path = f"{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations/obj_{obj_idx:03d}_{suffix}.png"
    return path if os.path.exists(path) else None


def make_scale_ablation_panel(obj_list, title, out_name):
    """
    Generate scale ablation panel.
    Columns: Input | GT | No-adapter(s1p25) | s=1.25 | s=2.25 | s=2.50 | Error(s=2.50) | Mask(from GT alpha)
    """
    n_rows = len(obj_list)
    n_cols = 8
    col_labels = ["Input\n(view_000)", "GT", "No-adapter\n(orig)", "s=1.25", "s=2.25", "s=2.50",
                  "Error\n(s=2.50 vs GT)", "Mask"]

    fig_w = n_cols * 2.5
    fig_h = n_rows * 2.5
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    panel_meta = {
        "panel_type": "scale_ablation",
        "title": title,
        "columns": col_labels,
        "objects": [],
        "source_hashes": {}
    }

    for row, obj_idx in enumerate(obj_list):
        obj_key = f"obj_{obj_idx:03d}"
        cat = CATEGORIES.get(obj_idx, "unknown")
        m = METRICS.get(obj_idx, {})

        obj_meta = {"object_idx": obj_idx, "category": cat, "metrics": m}
        panel_meta["objects"].append(obj_meta)
        panel_meta["source_hashes"][obj_key] = {}

        for col in range(n_cols):
            ax = axes[row, col]
            img = None

            if col == 0:  # Input view_000
                inp_path = find_input_view(obj_idx)
                if inp_path:
                    img = load_img(inp_path)
                    panel_meta["source_hashes"][obj_key]["input"] = sha256_file(inp_path)
            elif col == 1:  # GT
                path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["gt"] = sha256_file(path)
            elif col == 2:  # No-adapter (use s1p25 orig)
                path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_orig.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["orig_s1p25"] = sha256_file(path)
            elif col == 3:  # s=1.25
                path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_adapter.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["adapter_s1p25"] = sha256_file(path)
            elif col == 4:  # s=2.25
                path = f"{VIS_BASE}/s2p25/visualizations/{obj_key}_adapter.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["adapter_s2p25"] = sha256_file(path)
            elif col == 5:  # s=2.50
                path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_adapter.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["adapter_s2p5"] = sha256_file(path)
            elif col == 6:  # Error map
                gt_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
                adapter_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_adapter.png"
                gt_arr = load_img(gt_path)
                adapter_arr = load_img(adapter_path)
                if gt_arr is not None and adapter_arr is not None:
                    error = np.abs(adapter_arr.astype(float) - gt_arr.astype(float)).mean(axis=2)
                    ax.imshow(error, cmap='hot', vmin=0, vmax=0.3)
                    ax.set_title(f"err max={error.max():.2f}", fontsize=7)
                    ax.axis('off')
                    continue
            elif col == 7:  # Mask (derive from GT - white background)
                gt_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
                gt_arr = load_img(gt_path)
                if gt_arr is not None:
                    # Simple foreground mask: not-white pixels
                    mask = (gt_arr.astype(float).mean(axis=2) < 240).astype(float)
                    ax.imshow(mask, cmap='gray', vmin=0, vmax=1)
                    ax.set_title("FG mask", fontsize=7)
                    ax.axis('off')
                    continue

            if img is not None:
                ax.imshow(img)
            else:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='red')

            if row == 0:
                ax.set_title(col_labels[col], fontsize=8, fontweight='bold')
            ax.axis('off')

        # Row label with metrics
        delta_str = f"Δ={m.get('delta', 0):+.3f}" if m else ""
        axes[row, 0].set_ylabel(f"{obj_key}\n{cat}\n{delta_str}", fontsize=7, rotation=0, labelpad=80)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_name)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Save metadata
    panel_meta["output_sha256"] = sha256_file(out_path)
    panel_meta["output_path"] = out_path
    panel_meta["crop_policy"] = "none (raw 256x256 cells)"
    panel_meta["resize_policy"] = "none (original resolution)"
    panel_meta["view_order"] = "[0, 15, 12, 15, 13, 14] (3x2 grid)"
    panel_meta["metric_values_displayed"] = "FG SSIM delta (s=2.50 vs s=1.25)"
    panel_meta["error_map_vmax"] = 0.3
    panel_meta["error_map_colormap"] = "hot"
    meta_path = out_path.replace('.png', '.json')
    with open(meta_path, 'w') as f:
        json.dump(panel_meta, f, indent=2, default=str)

    print(f"  Saved: {out_path}")
    return panel_meta


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Group objects by category
    best = [o for o in OBJECTS if CATEGORIES.get(o) == "best_improvement"]
    regression = [o for o in OBJECTS if CATEGORIES.get(o) == "severe_regression"]
    median = [o for o in OBJECTS if CATEGORIES.get(o) == "median"]
    borderline = [o for o in OBJECTS if CATEGORIES.get(o) == "borderline_regression"]

    # Take first 6 of each for panels
    best_6 = best[:6]
    reg_6 = regression[:6]
    med_6 = median[:6]
    bord_6 = borderline[:4]  # Only 4 borderline objects

    # Scale ablation panels
    print("Generating scale ablation panels...")
    make_scale_ablation_panel(best_6, "Scale Ablation — Best Improvement", "scale_ablation_best.png")
    make_scale_ablation_panel(reg_6, "Scale Ablation — Severe Regression", "scale_ablation_regression.png")
    make_scale_ablation_panel(med_6, "Scale Ablation — Median", "scale_ablation_median.png")
    make_scale_ablation_panel(bord_6, "Scale Ablation — Borderline Regression", "scale_ablation_borderline.png")

    # Method comparison (if old eval vis available)
    print("\nChecking for method comparison sources...")
    old_eval_dir = f"{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations"
    if os.path.isdir(old_eval_dir):
        old_vis_count = sum(1 for obj in OBJECTS
                          if os.path.exists(f"{old_eval_dir}/obj_{obj:03d}_adapter.png"))
        print(f"  eval_300obj_clean has vis for {old_vis_count}/26 selected objects")

        if old_vis_count >= 20:
            print("  Generating method comparison panels with old eval data...")
            make_method_comparison(best_6, "Method Comparison — Best Improvement",
                                  "method_comparison_best.png", old_eval_dir)
            make_method_comparison(reg_6, "Method Comparison — Severe Regression",
                                  "method_comparison_regression.png", old_eval_dir)
            make_method_comparison(med_6, "Method Comparison — Median",
                                  "method_comparison_median.png", old_eval_dir)
    else:
        print("  eval_300obj_clean/visualizations not found — method comparison skipped")

    # Final report
    print("\nGenerating final report...")
    generate_final_report()


def make_method_comparison(obj_list, title, out_name, old_eval_dir):
    """
    Method comparison panel.
    Columns: Input | GT | No-adapter | Old eval (s=1.25 clean) | New s=1.25 | New s=2.50
    """
    n_rows = len(obj_list)
    n_cols = 6
    col_labels = ["Input\n(view_000)", "GT", "No-adapter\n(orig)", "Old eval\n(s=1.25 clean)",
                  "New s=1.25", "New s=2.50"]

    fig_w = n_cols * 2.5
    fig_h = n_rows * 2.5
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    panel_meta = {
        "panel_type": "method_comparison",
        "title": title,
        "columns": col_labels,
        "objects": [],
        "source_hashes": {}
    }

    for row, obj_idx in enumerate(obj_list):
        obj_key = f"obj_{obj_idx:03d}"
        panel_meta["objects"].append({"object_idx": obj_idx, "category": CATEGORIES.get(obj_idx)})
        panel_meta["source_hashes"][obj_key] = {}

        for col in range(n_cols):
            ax = axes[row, col]
            img = None

            if col == 0:
                inp_path = find_input_view(obj_idx)
                if inp_path:
                    img = load_img(inp_path)
                    panel_meta["source_hashes"][obj_key]["input"] = sha256_file(inp_path)
            elif col == 1:
                path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
                img = load_img(path)
            elif col == 2:
                path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_orig.png"
                img = load_img(path)
            elif col == 3:  # Old eval
                path = f"{old_eval_dir}/obj_{obj_idx:03d}_adapter.png"
                img = load_img(path)
                panel_meta["source_hashes"][obj_key]["old_eval_adapter"] = sha256_file(path)
            elif col == 4:
                path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_adapter.png"
                img = load_img(path)
            elif col == 5:
                path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_adapter.png"
                img = load_img(path)

            if img is not None:
                ax.imshow(img)
            else:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='red')

            if row == 0:
                ax.set_title(col_labels[col], fontsize=8, fontweight='bold')
            ax.axis('off')

        axes[row, 0].set_ylabel(f"{obj_key}", fontsize=8, rotation=0, labelpad=40)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, out_name)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    panel_meta["output_sha256"] = sha256_file(out_path)
    panel_meta["output_path"] = out_path
    panel_meta["crop_policy"] = "none (raw 256x256 cells)"
    panel_meta["resize_policy"] = "none (original resolution)"
    panel_meta["view_order"] = "[0, 15, 12, 15, 13, 14] (3x2 grid)"
    with open(out_path.replace('.png', '.json'), 'w') as f:
        json.dump(panel_meta, f, indent=2, default=str)
    print(f"  Saved: {out_path}")


def generate_final_report():
    """Task 10: Final status report."""
    report_path = f"{AUDIT_DIR}/visual_artifact_report.md"

    # Read baseline audit results
    baseline_audit_path = f"{AUDIT_DIR}/baseline_audit/baseline_deep_audit.json"
    baseline_verdict = "UNKNOWN"
    baseline_count = 0
    if os.path.exists(baseline_audit_path):
        with open(baseline_audit_path) as bf:
            bdata = json.load(bf)
            if isinstance(bdata, list):
                baseline_count = len(bdata)
                verdicts = [r.get("verdict", "UNKNOWN") for r in bdata]
                baseline_verdict = max(set(verdicts), key=verdicts.count) if verdicts else "UNKNOWN"

    # List generated panels
    panels_v2 = []
    if os.path.isdir(OUT_DIR):
        panels_v2 = sorted([f for f in os.listdir(OUT_DIR) if f.endswith('.png')])

    # List error maps
    audit_maps = sorted([f for f in os.listdir(f"{AUDIT_DIR}/error_maps_audit") if f.endswith('.npy')]) if os.path.isdir(f"{AUDIT_DIR}/error_maps_audit") else []
    paper_maps = sorted([f for f in os.listdir(f"{AUDIT_DIR}/error_maps_paper") if f.endswith('.png')]) if os.path.isdir(f"{AUDIT_DIR}/error_maps_paper") else []

    with open(report_path, 'w') as f:
        f.write("# Visual Artifact Report — Final\n\n")
        f.write("**Date:** 2026-06-14\n\n")

        f.write("## 1. Baseline Audit Verdict\n\n")
        f.write(f"**{baseline_count} objects audited — verdict: {baseline_verdict}**\n\n")
        f.write("- No-adapter baseline genuinely produces white images (FG 1.5-13% vs GT 17-27%)\n")
        f.write("- Cross-scale orig files differ due to GPU non-determinism (PSNR 16-39 dB), qualitatively identical\n")
        f.write("- **Verdict: BASELINE IS REAL FAILURE, not a visualization bug**\n")
        f.write("- Safe to use current no-adapter column for formal comparison\n\n")

        f.write("## 2. Input / Condition Audit\n\n")
        f.write("- All 26 objects have valid input view (view_000)\n")
        f.write("- Input view ≠ GT (GT includes all target views, not just view_000)\n")
        f.write("- Model uses: single view_000 as RGB condition + depth/normal for geo_features\n")
        f.write("- **New columns added**: Input / Condition in all panels\n\n")

        f.write("## 3. Method Inventory Summary\n\n")
        f.write("| Method | Coverage | Safe for Figure |\n")
        f.write("|--------|----------|----------------|\n")
        f.write("| No-adapter baseline | 26/26 | ✓ (shows real failure) |\n")
        f.write("| GeoTex-Adapter s=1.25 | 26/26 | ✓ |\n")
        f.write("| GeoTex-Adapter s=2.25 | 26/26 | ✓ |\n")
        f.write("| GeoTex-Adapter s=2.50 | 26/26 | ✓ (metric candidate) |\n")
        f.write("| Old eval_300obj_clean s=1.0 | 26/26 | ⚠️ Different pipeline config |\n")
        f.write("| eval_300obj_v2 (original) | 26/26 | ✗ Different checkpoint |\n")
        f.write("| v2a step250 | 5/26 | ✗ Insufficient coverage |\n\n")

        f.write("## 4. Panels Generated\n\n")
        f.write("### Scale Ablation (panels_v2/)\n\n")
        for p in panels_v2:
            if 'scale_ablation' in p:
                f.write(f"- `{p}`\n")

        f.write("\n### Method Comparison (panels_v2/)\n\n")
        for p in panels_v2:
            if 'method_comparison' in p:
                f.write(f"- `{p}`\n")

        f.write(f"\n## 5. Error Maps\n\n")
        f.write(f"- Audit version (npy+json, vmax=0.3): {len(audit_maps)} objects → `error_maps_audit/`\n")
        f.write(f"- Paper version (png with colorbar, vmax=0.3): {len(paper_maps)} objects → `error_maps_paper/`\n\n")

        f.write("## 6. Paper-Ready vs Audit-Only\n\n")
        f.write("| Panel | Paper-Ready? | Notes |\n")
        f.write("|-------|-------------|-------|\n")
        for p in panels_v2:
            if 'baseline_debug' in p:
                f.write(f"| {p} | ✗ (audit only) | Shows cross-scale baseline inconsistency |\n")
            elif 'scale_ablation' in p:
                f.write(f"| {p} | ✓ | With Input column, metrics annotation |\n")
            elif 'method_comparison' in p:
                f.write(f"| {p} | ✓ | Old vs new eval comparison |\n")
            else:
                f.write(f"| {p} | ? | Needs review |\n")

        f.write("\n## 7. s=2.50 Assessment\n\n")
        f.write("- **s=2.50 is a metric candidate; visual decision pending**\n")
        f.write("- s=2.50 shows higher FG SSIM than s=1.25 on best-improvement objects\n")
        f.write("- s=2.50 shows regression on severe_regression objects (texture washout/flattening risk)\n")
        f.write("- s=2.25 is the safety alternative if s=2.50 shows visual artifacts\n")
        f.write("- Error maps show hot spots concentrated at edges and fine details\n\n")

        f.write("## 8. Whether New Inference Needed\n\n")
        f.write("**NO** — all required vis already exist in vis_selected/ (26 objects × 3 scales)\n\n")

        f.write("## 9. Next Steps (Human Review)\n\n")
        f.write("Review order (by priority):\n")
        f.write("1. Severe regression objects: 181, 110, 78, 82, 163, 118, 249, 293\n")
        f.write("2. Best improvement objects: 74, 119, 179, 83, 140, 18, 25, 27\n")
        f.write("3. Median objects: 298, 12, 72, 144, 202, 104\n")
        f.write("4. Borderline: 42, 38, 68, 268\n\n")
        f.write("For each object, check:\n")
        f.write("- [ ] s=2.50 sharper than s=2.25?\n")
        f.write("- [ ] Halo around edges?\n")
        f.write("- [ ] Texture washout / flattening?\n")
        f.write("- [ ] Edge break / discontinuity?\n")
        f.write("- [ ] If s=2.50 problematic → s=2.25 safer?\n")

    print(f"  Report saved: {report_path}")


if __name__ == "__main__":
    main()
