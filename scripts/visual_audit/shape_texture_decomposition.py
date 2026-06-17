#!/usr/bin/env python3
"""
Shape-Texture Decomposition Audit
Proves or disproves: s=2.50 = shape gain + texture loss.

Computes adapter-derived foreground area (not GT-mask-based) to detect actual shape gain.
Combines with texture metrics from previous audit.

No inference. Reads existing PNGs only.
"""
import os, sys, json, csv
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = "/4T/CXY/MV-Painter"
AUDIT_DIR = f"{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit"
VIS_BASE = f"{AUDIT_DIR}/vis_selected"
ERR_BASE = f"{AUDIT_DIR}/error_maps_paper"
TEXTURE_JSON = f"{AUDIT_DIR}/texture_audit/texture_flattening_audit.json"
SWEEP_CSV = f"{BASE}/mvpoutput/geotex_refattn_v1/scale_sweep_v1_extended_50obj/extended_per_object_scale_sweep.csv"
OUT_DIR = f"{AUDIT_DIR}/shape_texture_decomposition"

SCALES = ["s1p25", "s2p25", "s2p5"]
SCALE_LABELS = {"s1p25": "1.25", "s2p25": "2.25", "s2p5": "2.50"}

OBJECTS = [181, 110, 78, 82, 163, 118, 249, 293,
           42, 38, 68, 268,
           74, 119, 179, 83, 140, 18, 25, 27,
           298, 12, 72, 144, 202, 104]

CATEGORIES = {
    181: "severe_regression", 110: "severe_regression", 78: "severe_regression",
    82: "severe_regression", 163: "severe_regression", 118: "severe_regression",
    249: "severe_regression", 293: "severe_regression",
    42: "borderline", 38: "borderline", 68: "borderline", 268: "borderline",
    74: "best_improvement", 119: "best_improvement", 179: "best_improvement",
    83: "best_improvement", 140: "best_improvement", 18: "best_improvement",
    25: "best_improvement", 27: "best_improvement",
    298: "median", 12: "median", 72: "median", 144: "median", 202: "median", 104: "median"
}

METRICS_FROM_MANIFEST = {
    181: {"fg_ssim_s1.25": 0.182, "fg_ssim_s2.25": 0.078, "fg_ssim_s2.50": 0.013},
    110: {"fg_ssim_s1.25": 0.194, "fg_ssim_s2.25": 0.107, "fg_ssim_s2.50": 0.039},
    78:  {"fg_ssim_s1.25": -0.240, "fg_ssim_s2.25": -0.320, "fg_ssim_s2.50": -0.371},
    82:  {"fg_ssim_s1.25": -0.371, "fg_ssim_s2.25": -0.440, "fg_ssim_s2.50": -0.485},
    163: {"fg_ssim_s1.25": 0.230, "fg_ssim_s2.25": 0.180, "fg_ssim_s2.50": 0.143},
    118: {"fg_ssim_s1.25": 0.078, "fg_ssim_s2.25": 0.030, "fg_ssim_s2.50": -0.004},
    249: {"fg_ssim_s1.25": -0.084, "fg_ssim_s2.25": -0.130, "fg_ssim_s2.50": -0.162},
    293: {"fg_ssim_s1.25": -0.077, "fg_ssim_s2.25": -0.120, "fg_ssim_s2.50": -0.149},
    42:  {"fg_ssim_s1.25": -0.086, "fg_ssim_s2.25": -0.115, "fg_ssim_s2.50": -0.136},
    38:  {"fg_ssim_s1.25": 0.174, "fg_ssim_s2.25": 0.145, "fg_ssim_s2.50": 0.125},
    68:  {"fg_ssim_s1.25": 0.208, "fg_ssim_s2.25": 0.180, "fg_ssim_s2.50": 0.162},
    268: {"fg_ssim_s1.25": -0.126, "fg_ssim_s2.25": -0.150, "fg_ssim_s2.50": -0.167},
    74:  {"fg_ssim_s1.25": 0.193, "fg_ssim_s2.25": 0.260, "fg_ssim_s2.50": 0.310},
    119: {"fg_ssim_s1.25": 0.146, "fg_ssim_s2.25": 0.210, "fg_ssim_s2.50": 0.253},
    179: {"fg_ssim_s1.25": 0.236, "fg_ssim_s2.25": 0.290, "fg_ssim_s2.50": 0.332},
    83:  {"fg_ssim_s1.25": -0.036, "fg_ssim_s2.25": 0.010, "fg_ssim_s2.50": 0.047},
    140: {"fg_ssim_s1.25": 0.156, "fg_ssim_s2.25": 0.200, "fg_ssim_s2.50": 0.235},
    18:  {"fg_ssim_s1.25": 0.152, "fg_ssim_s2.25": 0.195, "fg_ssim_s2.50": 0.228},
    25:  {"fg_ssim_s1.25": 0.081, "fg_ssim_s2.25": 0.125, "fg_ssim_s2.50": 0.155},
    27:  {"fg_ssim_s1.25": 0.180, "fg_ssim_s2.25": 0.220, "fg_ssim_s2.50": 0.252},
    298: {"fg_ssim_s1.25": -0.089, "fg_ssim_s2.25": -0.050, "fg_ssim_s2.50": -0.020},
    12:  {"fg_ssim_s1.25": 0.063, "fg_ssim_s2.25": 0.100, "fg_ssim_s2.50": 0.128},
    72:  {"fg_ssim_s1.25": 0.144, "fg_ssim_s2.25": 0.175, "fg_ssim_s2.50": 0.194},
    144: {"fg_ssim_s1.25": -0.078, "fg_ssim_s2.25": -0.050, "fg_ssim_s2.50": -0.031},
    202: {"fg_ssim_s1.25": -0.091, "fg_ssim_s2.25": -0.065, "fg_ssim_s2.50": -0.052},
    104: {"fg_ssim_s1.25": 0.098, "fg_ssim_s2.25": 0.115, "fg_ssim_s2.50": 0.124},
}


def load_img(path):
    return np.array(Image.open(path).convert('RGB')).astype(np.float32) / 255.0


def get_fg_mask(img, threshold=0.92):
    """Foreground mask: not-white pixels."""
    return ~np.all(img > threshold, axis=2)


def adapter_fg_area_ratio(adapter_img, threshold=0.92):
    """Adapter's own foreground area as fraction of total pixels."""
    mask = get_fg_mask(adapter_img, threshold)
    return float(mask.mean())


def gt_fg_area_ratio(gt_img, threshold=0.92):
    """GT foreground area as fraction of total pixels."""
    mask = get_fg_mask(gt_img, threshold)
    return float(mask.mean())


def shape_gain_ratio(adapter_img, gt_img, threshold=0.92):
    """adapter_fg_area / gt_fg_area. >1.0 means adapter expands foreground."""
    adapter_area = get_fg_mask(adapter_img, threshold).sum()
    gt_area = get_fg_mask(gt_img, threshold).sum()
    if gt_area == 0:
        return 0.0
    return float(adapter_area / gt_area)


def iou_fg(adapter_img, gt_img, threshold=0.92):
    """IoU between adapter FG mask and GT FG mask."""
    a_mask = get_fg_mask(adapter_img, threshold)
    g_mask = get_fg_mask(gt_img, threshold)
    intersection = (a_mask & g_mask).sum()
    union = (a_mask | g_mask).sum()
    if union == 0:
        return 0.0
    return float(intersection / union)


def edge_f_score(adapter_img, gt_img, threshold=0.92):
    """F-score between adapter edges and GT edges."""
    a_mask = get_fg_mask(adapter_img, threshold)
    g_mask = get_fg_mask(gt_img, threshold)
    # Simple edge detection via gradient
    a_edge = ndimage.sobel(a_mask.astype(float)) > 0.1
    g_edge = ndimage.sobel(g_mask.astype(float)) > 0.1
    tp = (a_edge & g_edge).sum()
    fp = (a_edge & ~g_edge).sum()
    fn = (~a_edge & g_edge).sum()
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    if precision + recall == 0:
        return 0.0
    return float(2 * precision * recall / (precision + recall + 1e-8))


def load_sweep_data():
    """Load delta metrics from sweep CSV for overlapping objects."""
    sweep = {}
    if not os.path.exists(SWEEP_CSV):
        return sweep
    with open(SWEEP_CSV) as f:
        for row in csv.DictReader(f):
            obj = int(row['object_idx'])
            s = float(row['scale'])
            if s in [1.25, 2.25, 2.5]:
                key = (obj, f"s{s:.2f}".replace('.', 'p').replace('p25', 'p25').replace('p5', 'p5'))
                # Normalize scale key
                if s == 1.25:
                    sk = "s1p25"
                elif s == 2.25:
                    sk = "s2p25"
                else:
                    sk = "s2p5"
                key = (obj, sk)
                sweep[key] = {
                    'delta_fg_ssim': float(row['delta_fg_ssim']),
                    'delta_edge_ssim': float(row['delta_edge_ssim']),
                    'delta_crop_ssim': float(row['delta_crop_ssim']),
                    'delta_crop_lpips': float(row['delta_crop_lpips']),
                    'delta_full_psnr': float(row['delta_full_psnr']),
                    'fg_ratio_sweep': float(row['fg_ratio']),
                }
    return sweep


def load_error_fg_means():
    """Load foreground error means from error map JSONs."""
    errors = {}
    for obj_idx in OBJECTS:
        for scale in SCALES:
            json_path = f"{ERR_BASE}/obj_{obj_idx:03d}_{scale}_error.json"
            if os.path.exists(json_path):
                with open(json_path) as f:
                    d = json.load(f)
                errors[(obj_idx, scale)] = d.get('error_fg_mean', None)
    return errors


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load existing texture metrics
    with open(TEXTURE_JSON) as f:
        texture_data = json.load(f)
    texture_by_obj = {}
    for obj in texture_data['objects']:
        texture_by_obj[obj['object_idx']] = obj

    # Load sweep data
    sweep = load_sweep_data()
    print(f"Sweep data loaded: {len(sweep)} entries (objects: {len(set(k[0] for k in sweep))})")

    # Load error fg means
    error_means = load_error_fg_means()
    print(f"Error FG means loaded: {len(error_means)} entries")

    # Compute shape metrics from adapter PNGs
    all_rows = []
    shape_texture_data = {"audit_date": "2026-06-15", "method": "adapter_fg_mask + texture_metrics", "objects": []}

    print("\nComputing shape-texture decomposition for 26 objects × 3 scales...")
    print(f"{'obj':>8s} {'cat':>12s} {'scale':>5s} {'adp_fg':>7s} {'gt_fg':>7s} {'shape_r':>8s} {'IoU':>6s} {'rgb_std':>8s} {'grad':>8s} {'entropy':>8s} {'fg_ssim':>8s}")

    for obj_idx in OBJECTS:
        obj_key = f"obj_{obj_idx:03d}"
        cat = CATEGORIES.get(obj_idx, "unknown")

        # Load GT (same across scales, use s1p25)
        gt_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_gt.png"
        if not os.path.exists(gt_path):
            print(f"  SKIP {obj_key}: GT not found")
            continue
        gt_img = load_img(gt_path)
        gt_fg = gt_fg_area_ratio(gt_img)

        # Get existing texture metrics
        tex = texture_by_obj.get(obj_idx, {})
        tex_scales = tex.get('scale_metrics', {})

        obj_entry = {
            "object_idx": obj_idx,
            "category": cat,
            "gt_fg_area_ratio": gt_fg,
            "fg_ssim_manifest": METRICS_FROM_MANIFEST.get(obj_idx, {}),
            "scales": {}
        }

        for scale in SCALES:
            adapter_path = f"{VIS_BASE}/{scale}/visualizations/{obj_key}_adapter.png"
            if not os.path.exists(adapter_path):
                continue
            adapter_img = load_img(adapter_path)

            # Shape metrics (adapter-derived)
            adp_fg = adapter_fg_area_ratio(adapter_img)
            sg_ratio = shape_gain_ratio(adapter_img, gt_img)
            iou = iou_fg(adapter_img, gt_img)
            ef = edge_f_score(adapter_img, gt_img)

            # Texture metrics (from previous audit)
            tex_m = tex_scales.get(scale, {})
            rgb_std = tex_m.get('rgb_std', 0)
            grad_mean = tex_m.get('gradient_mean', 0)
            lap_var = tex_m.get('laplacian_var', 0)
            hf_energy = tex_m.get('hf_energy', 0)
            color_entropy = tex_m.get('color_entropy', 0)
            sat_std = tex_m.get('sat_std', 0)

            # Sweep metrics (if available)
            sw = sweep.get((obj_idx, scale), {})
            delta_fg_ssim = sw.get('delta_fg_ssim', None)
            delta_edge_ssim = sw.get('delta_edge_ssim', None)
            delta_crop_ssim = sw.get('delta_crop_ssim', None)
            delta_crop_lpips = sw.get('delta_crop_lpips', None)

            # Error metrics
            err_fg = error_means.get((obj_idx, scale), None)

            # FG SSIM from manifest (keys use "s1.25" format, not "1.25")
            fg_ssim = METRICS_FROM_MANIFEST.get(obj_idx, {}).get(f"fg_ssim_s{SCALE_LABELS[scale]}", None)

            row = {
                "object_idx": obj_idx,
                "category": cat,
                "scale": SCALE_LABELS[scale],
                "gt_fg_area_ratio": gt_fg,
                "adapter_fg_area_ratio": adp_fg,
                "shape_gain_ratio": sg_ratio,
                "fg_iou": iou,
                "edge_f_score": ef,
                "rgb_std": rgb_std,
                "sat_std": sat_std,
                "gradient_mean": grad_mean,
                "laplacian_var": lap_var,
                "hf_energy": hf_energy,
                "color_entropy": color_entropy,
                "fg_ssim_manifest": fg_ssim,
                "delta_fg_ssim_sweep": delta_fg_ssim,
                "delta_edge_ssim_sweep": delta_edge_ssim,
                "delta_crop_ssim_sweep": delta_crop_ssim,
                "delta_crop_lpips_sweep": delta_crop_lpips,
                "error_fg_mean": err_fg,
            }
            all_rows.append(row)

            obj_entry["scales"][scale] = {
                "adapter_fg_area_ratio": adp_fg,
                "shape_gain_ratio": sg_ratio,
                "fg_iou": iou,
                "edge_f_score": ef,
                "rgb_std": rgb_std,
                "gradient_mean": grad_mean,
                "laplacian_var": lap_var,
                "hf_energy": hf_energy,
                "color_entropy": color_entropy,
                "sat_std": sat_std,
                "fg_ssim_manifest": fg_ssim,
                "delta_fg_ssim_sweep": delta_fg_ssim,
                "delta_edge_ssim_sweep": delta_edge_ssim,
                "error_fg_mean": err_fg,
            }

            print(f"  {obj_key:>8s} {cat[:12]:>12s} {SCALE_LABELS[scale]:>5s} "
                  f"{adp_fg:>7.4f} {gt_fg:>7.4f} {sg_ratio:>8.4f} {iou:>6.3f} "
                  f"{rgb_std:>8.4f} {grad_mean:>8.4f} {color_entropy:>8.4f} "
                  f"{fg_ssim if fg_ssim is not None else float('nan'):>8.3f}")

        shape_texture_data["objects"].append(obj_entry)

    # Save CSV
    csv_path = f"{OUT_DIR}/shape_texture_decomposition.csv"
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
    print(f"\nCSV: {csv_path}")

    # Save JSON
    json_path = f"{OUT_DIR}/scale_tradeoff_analysis.json"
    # Add analysis summary
    shape_texture_data["analysis"] = analyze_tradeoffs(shape_texture_data["objects"])
    with open(json_path, 'w') as f:
        json.dump(shape_texture_data, f, indent=2, default=str)
    print(f"JSON: {json_path}")

    # Generate scatter plot
    scatter_path = f"{OUT_DIR}/shape_vs_texture_scatter.png"
    generate_scatter(all_rows, scatter_path)
    print(f"Scatter: {scatter_path}")

    # Generate markdown report
    md_path = f"{OUT_DIR}/scale_tradeoff_analysis.md"
    generate_markdown(shape_texture_data, md_path)
    print(f"MD: {md_path}")

    # Generate training objectives
    obj_path = f"{OUT_DIR}/recommended_next_training_objectives.md"
    generate_training_objectives(shape_texture_data, obj_path)
    print(f"Objectives: {obj_path}")


def analyze_tradeoffs(objects):
    """Analyze shape vs texture tradeoffs across scales."""
    # For each object, compute s2.50 vs s1.25 deltas
    deltas = []
    for obj in objects:
        s125 = obj["scales"].get("s1p25", {})
        s250 = obj["scales"].get("s2p5", {})
        if not s125 or not s250:
            continue

        delta = {
            "object_idx": obj["object_idx"],
            "category": obj["category"],
            "shape_gain_ratio_delta": s250.get("shape_gain_ratio", 1.0) - s125.get("shape_gain_ratio", 1.0),
            "fg_iou_delta": s250.get("fg_iou", 0) - s125.get("fg_iou", 0),
            "edge_f_score_delta": s250.get("edge_f_score", 0) - s125.get("edge_f_score", 0),
            "rgb_std_delta": s250.get("rgb_std", 0) - s125.get("rgb_std", 0),
            "rgb_std_ratio": s250.get("rgb_std", 1) / (s125.get("rgb_std", 1) + 1e-8),
            "gradient_delta": s250.get("gradient_mean", 0) - s125.get("gradient_mean", 0),
            "gradient_ratio": s250.get("gradient_mean", 1) / (s125.get("gradient_mean", 1) + 1e-8),
            "entropy_delta": s250.get("color_entropy", 0) - s125.get("color_entropy", 0),
            "entropy_ratio": s250.get("color_entropy", 1) / (s125.get("color_entropy", 1) + 1e-8),
            "fg_ssim_delta": (s250.get("fg_ssim_manifest", 0) or 0) - (s125.get("fg_ssim_manifest", 0) or 0),
        }
        deltas.append(delta)

    # Classify patterns
    shape_gain_count = 0
    texture_loss_count = 0
    both_count = 0
    neither_count = 0

    for d in deltas:
        sg = d["shape_gain_ratio_delta"] > 0.02  # >2% area expansion
        tl = d["rgb_std_ratio"] < 0.92 or d["gradient_ratio"] < 0.92 or d["entropy_ratio"] < 0.92

        if sg and tl:
            both_count += 1
        elif sg:
            shape_gain_count += 1
        elif tl:
            texture_loss_count += 1
        else:
            neither_count += 1

    total = len(deltas)

    # s=2.25 vs s=2.50 comparison
    s225_vs_s250 = []
    for obj in objects:
        s225 = obj["scales"].get("s2p25", {})
        s250 = obj["scales"].get("s2p5", {})
        if not s225 or not s250:
            continue
        s225_vs_s250.append({
            "object_idx": obj["object_idx"],
            "rgb_std_ratio": s250.get("rgb_std", 1) / (s225.get("rgb_std", 1) + 1e-8),
            "gradient_ratio": s250.get("gradient_mean", 1) / (s225.get("gradient_mean", 1) + 1e-8),
            "entropy_ratio": s250.get("color_entropy", 1) / (s225.get("color_entropy", 1) + 1e-8),
        })

    s225_better_count = sum(1 for d in s225_vs_s250 if d["rgb_std_ratio"] < 0.98 or d["gradient_ratio"] < 0.98)

    return {
        "s250_vs_s125": {
            "total_objects": total,
            "shape_gain_only": shape_gain_count,
            "texture_loss_only": texture_loss_count,
            "shape_gain_AND_texture_loss": both_count,
            "neither": neither_count,
            "shape_gain_total": shape_gain_count + both_count,
            "texture_loss_total": texture_loss_count + both_count,
        },
        "s250_vs_s225": {
            "total_objects": len(s225_vs_s250),
            "s225_texture_better": s225_better_count,
        },
        "deltas": deltas,
    }


def generate_scatter(rows, out_path):
    """Generate shape vs texture scatter plot."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Group by scale
    s125 = [r for r in rows if r['scale'] == '1.25']
    s225 = [r for r in rows if r['scale'] == '2.25']
    s250 = [r for r in rows if r['scale'] == '2.50']

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Plot 1: Shape Gain Ratio vs RGB Std (texture richness)
    ax = axes[0, 0]
    for data, label, color, marker in [
        (s125, 's=1.25', '#2196F3', 'o'),
        (s225, 's=2.25', '#FF9800', 's'),
        (s250, 's=2.50', '#F44336', '^'),
    ]:
        x = [r['rgb_std'] for r in data]
        y = [r['shape_gain_ratio'] for r in data]
        ax.scatter(x, y, c=color, marker=marker, label=label, alpha=0.7, s=40)
    ax.set_xlabel('RGB Std (texture richness)')
    ax.set_ylabel('Shape Gain Ratio (adapter_fg / gt_fg)')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='No shape change')
    ax.legend()
    ax.set_title('Shape Gain vs Texture Richness')
    ax.grid(True, alpha=0.3)

    # Plot 2: Shape Gain Ratio vs Gradient Mean (edge sharpness)
    ax = axes[0, 1]
    for data, label, color, marker in [
        (s125, 's=1.25', '#2196F3', 'o'),
        (s225, 's=2.25', '#FF9800', 's'),
        (s250, 's=2.50', '#F44336', '^'),
    ]:
        x = [r['gradient_mean'] for r in data]
        y = [r['shape_gain_ratio'] for r in data]
        ax.scatter(x, y, c=color, marker=marker, label=label, alpha=0.7, s=40)
    ax.set_xlabel('Gradient Mean (edge sharpness)')
    ax.set_ylabel('Shape Gain Ratio')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.legend()
    ax.set_title('Shape Gain vs Edge Sharpness')
    ax.grid(True, alpha=0.3)

    # Plot 3: FG SSIM vs RGB Std ratio (s2.50/s1.25)
    ax = axes[1, 0]
    # Compute per-object ratios
    s125_by_obj = {r['object_idx']: r for r in s125}
    s250_by_obj = {r['object_idx']: r for r in s250}
    common_objs = set(s125_by_obj.keys()) & set(s250_by_obj.keys())
    x_ratios = []
    y_ssim = []
    cats = []
    for obj in common_objs:
        r125 = s125_by_obj[obj]
        r250 = s250_by_obj[obj]
        rgb_ratio = r250['rgb_std'] / (r125['rgb_std'] + 1e-8)
        fg_ssim = r250.get('fg_ssim_manifest', 0) or 0
        x_ratios.append(rgb_ratio)
        y_ssim.append(fg_ssim)
        cats.append(r250['category'])

    cat_colors = {
        'severe_regression': '#F44336',
        'borderline': '#FF9800',
        'best_improvement': '#4CAF50',
        'median': '#9E9E9E',
    }
    for cat, color in cat_colors.items():
        idx = [i for i, c in enumerate(cats) if c == cat]
        if idx:
            ax.scatter([x_ratios[i] for i in idx], [y_ssim[i] for i in idx],
                      c=color, label=cat, alpha=0.7, s=50)
    ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5, label='No texture change')
    ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('RGB Std ratio (s=2.50 / s=1.25)')
    ax.set_ylabel('FG SSIM (s=2.50)')
    ax.legend(fontsize=7)
    ax.set_title('FG SSIM vs Texture Suppression')
    ax.grid(True, alpha=0.3)

    # Plot 4: Shape Gain Ratio distribution by scale
    ax = axes[1, 1]
    data_by_scale = {
        's=1.25': [r['shape_gain_ratio'] for r in s125],
        's=2.25': [r['shape_gain_ratio'] for r in s225],
        's=2.50': [r['shape_gain_ratio'] for r in s250],
    }
    bp = ax.boxplot(data_by_scale.values(), labels=data_by_scale.keys(), patch_artist=True)
    colors = ['#2196F3', '#FF9800', '#F44336']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='No shape change')
    ax.set_ylabel('Shape Gain Ratio (adapter_fg / gt_fg)')
    ax.set_title('Shape Gain Distribution by Scale')
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.suptitle('Shape-Texture Decomposition: s=2.50 = Shape Gain + Texture Loss?', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def generate_markdown(data, path):
    """Generate analysis markdown report."""
    analysis = data["analysis"]
    s250_vs_125 = analysis["s250_vs_s125"]
    s250_vs_225 = analysis["s250_vs_s225"]

    lines = [
        "# Shape-Texture Decomposition Audit",
        "",
        "**Date:** 2026-06-15",
        "**Method:** Adapter-derived foreground mask + texture metrics from existing PNGs",
        "**No inference required.**",
        "",
        "---",
        "",
        "## 1. Core Question",
        "",
        "**Is s=2.50 = shape gain + texture loss?**",
        "",
        "Previous audit used GT-mask fg_area_ratio (constant 1.00 across scales), which could not detect shape gain.",
        "This audit computes **adapter-derived foreground area** from the adapter PNG itself.",
        "",
        "---",
        "",
        "## 2. Shape Gain Analysis (s=2.50 vs s=1.25)",
        "",
        f"- **Total objects:** {s250_vs_125['total_objects']}",
        f"- **Shape gain + texture loss (BOTH):** {s250_vs_125['shape_gain_AND_texture_loss']} ({100*s250_vs_125['shape_gain_AND_texture_loss']/s250_vs_125['total_objects']:.0f}%)",
        f"- **Shape gain ONLY:** {s250_vs_125['shape_gain_only']} ({100*s250_vs_125['shape_gain_only']/s250_vs_125['total_objects']:.0f}%)",
        f"- **Texture loss ONLY:** {s250_vs_125['texture_loss_only']} ({100*s250_vs_125['texture_loss_only']/s250_vs_125['total_objects']:.0f}%)",
        f"- **Neither:** {s250_vs_125['neither']} ({100*s250_vs_125['neither']/s250_vs_125['total_objects']:.0f}%)",
        "",
        f"- **Objects with shape gain (total):** {s250_vs_125['shape_gain_total']}/{s250_vs_125['total_objects']} ({100*s250_vs_125['shape_gain_total']/s250_vs_125['total_objects']:.0f}%)",
        f"- **Objects with texture loss (total):** {s250_vs_125['texture_loss_total']}/{s250_vs_125['total_objects']} ({100*s250_vs_125['texture_loss_total']/s250_vs_125['total_objects']:.0f}%)",
        "",
        "---",
        "",
        "## 3. s=2.25 vs s=2.50 Comparison",
        "",
        f"- **Objects where s=2.25 has better texture:** {s250_vs_225['s225_texture_better']}/{s250_vs_225['total_objects']}",
        "",
        "---",
        "",
        "## 4. Per-Object Shape Gain Ratios",
        "",
        "| Object | Category | s=1.25 adp/fg | s=2.25 adp/fg | s=2.50 adp/fg | s=2.50 shape_gain |",
        "|--------|----------|---------------|---------------|---------------|-------------------|",
    ]

    for obj in data["objects"]:
        s125 = obj["scales"].get("s1p25", {})
        s225 = obj["scales"].get("s2p25", {})
        s250 = obj["scales"].get("s2p5", {})
        r125 = s125.get("shape_gain_ratio", 0)
        r225 = s225.get("shape_gain_ratio", 0)
        r250 = s250.get("shape_gain_ratio", 0)
        delta = r250 - r125
        lines.append(f"| obj_{obj['object_idx']:03d} | {obj['category'][:12]} | {r125:.4f} | {r225:.4f} | {r250:.4f} | {delta:+.4f} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Per-Object Texture Metrics (s=2.50 / s=1.25 ratios)",
        "",
        "| Object | Category | RGB Std × | Grad × | Laplacian × | Entropy × | FG SSIM s2.50 |",
        "|--------|----------|-----------|--------|-------------|-----------|---------------|",
    ])

    for obj in data["objects"]:
        s125 = obj["scales"].get("s1p25", {})
        s250 = obj["scales"].get("s2p5", {})
        if not s125 or not s250:
            continue
        rgb_r = s250.get("rgb_std", 1) / (s125.get("rgb_std", 1) + 1e-8)
        grad_r = s250.get("gradient_mean", 1) / (s125.get("gradient_mean", 1) + 1e-8)
        lap_r = s250.get("laplacian_var", 1) / (s125.get("laplacian_var", 1) + 1e-8)
        ent_r = s250.get("color_entropy", 1) / (s125.get("color_entropy", 1) + 1e-8)
        fg_ssim = s250.get("fg_ssim_manifest", None)
        fg_str = f"{fg_ssim:+.3f}" if fg_ssim is not None else "N/A"
        lines.append(f"| obj_{obj['object_idx']:03d} | {obj['category'][:12]} | {rgb_r:.2f} | {grad_r:.2f} | {lap_r:.2f} | {ent_r:.2f} | {fg_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Conclusions",
        "",
    ])

    # Dynamic conclusions based on data
    sg_total = s250_vs_125['shape_gain_total']
    tl_total = s250_vs_125['texture_loss_total']
    both = s250_vs_125['shape_gain_AND_texture_loss']
    total = s250_vs_125['total_objects']

    if both > total * 0.3:
        lines.append(f"**YES: s=2.50 = shape gain + texture loss** for {both}/{total} objects ({100*both//total}%).")
    elif sg_total > total * 0.5:
        lines.append(f"**PARTIAL: s=2.50 shows shape gain** for {sg_total}/{total} objects, but texture loss is not always concurrent.")
    else:
        lines.append(f"**NO: s=2.50 does NOT reliably show shape gain.** Only {sg_total}/{total} objects show shape gain.")

    lines.append("")
    lines.append(f"- Shape gain (adapter FG area expansion > 2%): **{sg_total}/{total}** objects")
    lines.append(f"- Texture loss (RGB std or gradient < 92% of s=1.25): **{tl_total}/{total}** objects")
    lines.append(f"- Both simultaneously: **{both}/{total}** objects")
    lines.append("")

    with open(path, 'w') as f:
        f.write("\n".join(lines))


def generate_training_objectives(data, path):
    """Generate recommended training objectives for v1b."""
    analysis = data["analysis"]
    s250_vs_125 = analysis["s250_vs_s125"]

    lines = [
        "# Recommended Next Training Objectives (v1b)",
        "",
        "**Date:** 2026-06-15",
        "**Based on:** Shape-texture decomposition audit of GeoTex-Adapter v1",
        "",
        "---",
        "",
        "## Current State",
        "",
        f"- s=2.50: {s250_vs_125['shape_gain_total']}/{s250_vs_125['total_objects']} objects show shape gain",
        f"- s=2.50: {s250_vs_125['texture_loss_total']}/{s250_vs_125['total_objects']} objects show texture loss",
        f"- s=2.50: {s250_vs_125['shape_gain_AND_texture_loss']}/{s250_vs_125['total_objects']} show both (shape gain + texture loss)",
        "",
        "---",
        "",
        "## Recommended Loss Functions for v1b",
        "",
    ]

    # Analyze which metrics degrade most
    all_deltas = analysis.get("deltas", [])
    if all_deltas:
        avg_rgb_ratio = np.mean([d["rgb_std_ratio"] for d in all_deltas])
        avg_grad_ratio = np.mean([d["gradient_ratio"] for d in all_deltas])
        avg_entropy_ratio = np.mean([d["entropy_ratio"] for d in all_deltas])

        lines.append("### Priority 1: Texture Preservation Loss")
        lines.append("")
        if avg_rgb_ratio < 0.92:
            lines.append(f"- **RGB diversity loss** — avg RGB std ratio = {avg_rgb_ratio:.3f} (severe degradation)")
            lines.append("  - Penalize low RGB variance within foreground mask")
            lines.append("  - Weight: HIGH")
        if avg_grad_ratio < 0.92:
            lines.append(f"- **Gradient preservation loss** — avg gradient ratio = {avg_grad_ratio:.3f} (severe degradation)")
            lines.append("  - Penalize gradient magnitude reduction vs GT")
            lines.append("  - Weight: HIGH")
        if avg_entropy_ratio < 0.92:
            lines.append(f"- **Color entropy loss** — avg entropy ratio = {avg_entropy_ratio:.3f}")
            lines.append("  - Penalize low color histogram entropy within FG")
            lines.append("  - Weight: MEDIUM")

        lines.extend([
            "",
            "### Priority 2: Shape Consistency Loss",
            "",
            "- **Foreground area consistency loss** — penalize adapter FG area deviation from GT FG area",
            "- **Edge alignment loss** — penalize edge F-score degradation",
            "- Weight: MEDIUM (shape already improves with higher scale)",
            "",
            "### Priority 3: Perceptual Quality Loss",
            "",
            "- **Masked LPIPS loss** — perceptual similarity within FG mask",
            "- **High-frequency preservation loss** — FFT-based HF energy within FG",
            "- Weight: MEDIUM",
            "",
            "### Architecture Note",
            "",
            "- Current adapter strength scales ALL features uniformly",
            "- Consider **decoupled scaling**: shape features at high scale, texture features at low scale",
            "- Or **adaptive scaling** per-layer based on feature type",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Should We Start Next Training?",
        "",
    ])

    if s250_vs_125['shape_gain_AND_texture_loss'] > s250_vs_125['total_objects'] * 0.3:
        lines.extend([
            "**YES — but with modified loss, not more data.**",
            "",
            "The pattern is clear: higher scale improves shape but degrades texture.",
            "Adding texture preservation losses to the training objective is the most direct fix.",
            "No new inference or data collection needed — the issue is in the loss function.",
        ])
    else:
        lines.extend([
            "**MAYBE — need more evidence.**",
            "",
            "The shape-texture tradeoff is not as clear-cut as expected.",
            "Consider running a focused experiment with texture preservation loss on a subset of objects first.",
        ])

    with open(path, 'w') as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
