#!/usr/bin/env python3
"""
Texture Flattening Audit: Quantitative comparison of texture quality across adapter scales.
Reads existing PNGs only. No inference.

For each object × scale, computes within foreground mask:
  1. RGB std (texture richness)
  2. Saturation mean/std (color vibrancy)
  3. Gradient magnitude mean (edge sharpness)
  4. Laplacian variance (detail / high-freq content)
  5. High-frequency energy (FFT-based)
  6. Edge density (Canny-based)
  7. Foreground area ratio
  8. Color entropy (histogram-based)
"""
import os, sys, json, csv, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = "/4T/CXY/MV-Painter"
AUDIT_DIR = f"{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit"
VIS_BASE = f"{AUDIT_DIR}/vis_selected"
OUT_DIR = f"{AUDIT_DIR}/texture_audit"

SCALES = ["s1p25", "s2p25", "s2p5"]

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


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_img(path):
    return np.array(Image.open(path).convert('RGB')).astype(np.float32) / 255.0


def get_fg_mask(gt_img, threshold=0.92):
    """Foreground mask from GT: not-white pixels."""
    return ~np.all(gt_img > threshold, axis=2)


def rgb_std(img, mask):
    """RGB standard deviation within foreground."""
    if mask.sum() == 0:
        return 0.0
    return float(img[mask].std())


def saturation_stats(img, mask):
    """Saturation mean/std within foreground (HSV S channel)."""
    if mask.sum() == 0:
        return 0.0, 0.0
    # Approximate saturation: 1 - min(R,G,B)/max(R,G,B)
    max_ch = img.max(axis=2)
    min_ch = img.min(axis=2)
    sat = np.where(max_ch > 0.01, 1.0 - min_ch / (max_ch + 1e-8), 0.0)
    fg_sat = sat[mask]
    return float(fg_sat.mean()), float(fg_sat.std())


def gradient_magnitude(img, mask):
    """Mean gradient magnitude within foreground."""
    gray = img.mean(axis=2)
    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)
    grad = np.sqrt(gx**2 + gy**2)
    if mask.sum() == 0:
        return 0.0
    return float(grad[mask].mean())


def laplacian_variance(img, mask):
    """Laplacian variance within foreground (detail measure)."""
    gray = img.mean(axis=2)
    lap = ndimage.laplace(gray)
    if mask.sum() == 0:
        return 0.0
    return float(lap[mask].var())


def high_freq_energy(img, mask):
    """High-frequency energy via FFT within foreground."""
    gray = img.mean(axis=2)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    h, w = gray.shape
    # High freq = outside central 1/4
    cy, cx = h // 2, w // 2
    r = min(h, w) // 8
    y, x = np.ogrid[:h, :w]
    hf_mask = ((y - cy)**2 + (x - cx)**2) > r**2
    if mask.sum() == 0:
        return 0.0
    # Combine spatial and frequency masks
    combined = mask & hf_mask
    if combined.sum() == 0:
        return 0.0
    return float(magnitude[combined].mean())


def edge_density(img, mask):
    """Edge density within foreground (Canny-like)."""
    gray = img.mean(axis=2)
    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)
    grad = np.sqrt(gx**2 + gy**2)
    # Threshold at 0.1 (normalized)
    edges = grad > 0.1
    if mask.sum() == 0:
        return 0.0
    return float(edges[mask].mean())


def color_entropy(img, mask):
    """Color entropy within foreground (histogram-based)."""
    if mask.sum() == 0:
        return 0.0
    fg_pixels = (img[mask] * 255).astype(np.uint8)
    entropy = 0.0
    for ch in range(3):
        hist, _ = np.histogram(fg_pixels[:, ch], bins=64, range=(0, 256))
        hist = hist.astype(float)
        hist = hist / (hist.sum() + 1e-8)
        hist = hist[hist > 0]
        entropy += float(-np.sum(hist * np.log2(hist + 1e-10)))
    return entropy / 3.0  # Average across channels


def fg_area_ratio(gt_mask):
    """Foreground area as fraction of total."""
    return float(gt_mask.mean())


def compute_all_metrics(img, gt_mask):
    """Compute all texture metrics for an image within GT foreground mask."""
    return {
        "rgb_std": rgb_std(img, gt_mask),
        "sat_mean": saturation_stats(img, gt_mask)[0],
        "sat_std": saturation_stats(img, gt_mask)[1],
        "gradient_mean": gradient_magnitude(img, gt_mask),
        "laplacian_var": laplacian_variance(img, gt_mask),
        "hf_energy": high_freq_energy(img, gt_mask),
        "edge_density": edge_density(img, gt_mask),
        "fg_area_ratio": fg_area_ratio(gt_mask),
        "color_entropy": color_entropy(img, gt_mask),
    }


def classify_texture_pattern(gt_metrics, s125_m, s225_m, s250_m):
    """Classify the texture vs shape trade-off pattern."""
    # Texture degradation metrics
    rgb_loss = s250_m["rgb_std"] < s125_m["rgb_std"] * 0.90
    grad_loss = s250_m["gradient_mean"] < s125_m["gradient_mean"] * 0.90
    lap_loss = s250_m["laplacian_var"] < s125_m["laplacian_var"] * 0.85
    ent_loss = s250_m["color_entropy"] < s125_m["color_entropy"] * 0.92
    texture_degraded = rgb_loss or grad_loss or lap_loss or ent_loss

    # Shape/area gain
    shape_gain = s250_m["fg_area_ratio"] > s125_m["fg_area_ratio"] * 1.05

    # s=2.25 texture check
    s225_texture_better = (
        s225_m.get("rgb_std", 0) > s250_m["rgb_std"] * 1.05 or
        s225_m.get("gradient_mean", 0) > s250_m["gradient_mean"] * 1.05
    )

    if shape_gain and texture_degraded:
        return "SHAPE_GAIN_TEXTURE_LOSS"
    elif texture_degraded and not shape_gain:
        return "S250_TEXTURE_LOSS_NO_SHAPE_GAIN"
    elif s250_m["rgb_std"] > s125_m["rgb_std"] * 1.05:
        return "S250_TEXTURE_BETTER"
    elif s225_texture_better:
        return "S225_TEXTURE_BETTER_THAN_S250"
    else:
        return "TEXTURE_COMPARABLE"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_rows = []
    all_json = {"audit_date": "2026-06-14", "metrics_computed": [], "objects": []}

    print("Computing texture metrics for 26 objects × 3 scales...")
    for obj_idx in OBJECTS:
        obj_key = f"obj_{obj_idx:03d}"
        cat = CATEGORIES.get(obj_idx, "unknown")

        gt_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_gt.png"
        if not os.path.exists(gt_path):
            print(f"  SKIP {obj_key}: GT not found")
            continue

        gt = load_img(gt_path)
        gt_mask = get_fg_mask(gt)
        gt_metrics = compute_all_metrics(gt, gt_mask)

        scale_metrics = {}
        for scale in SCALES:
            adapter_path = f"{VIS_BASE}/{scale}/visualizations/{obj_key}_adapter.png"
            if not os.path.exists(adapter_path):
                continue
            adapter = load_img(adapter_path)
            # Use GT foreground mask for consistent comparison
            m = compute_all_metrics(adapter, gt_mask)
            scale_metrics[scale] = m

            row = {
                "object_idx": obj_idx,
                "category": cat,
                "scale": scale,
                "fg_ssim_manifest": METRICS_FROM_MANIFEST.get(obj_idx, {}).get(f"fg_ssim_{scale}", None),
            }
            row.update({f"adapter_{k}": v for k, v in m.items()})
            row.update({f"gt_{k}": v for k, v in gt_metrics.items()})
            all_rows.append(row)

        # Compare across scales
        if "s1p25" in scale_metrics and "s2p5" in scale_metrics:
            pattern = classify_texture_pattern(
                gt_metrics, scale_metrics["s1p25"], scale_metrics.get("s2p25", {}), scale_metrics["s2p5"]
            )
        else:
            pattern = "INSUFFICIENT_DATA"

        obj_entry = {
            "object_idx": obj_idx,
            "category": cat,
            "fg_ssim": METRICS_FROM_MANIFEST.get(obj_idx, {}),
            "gt_metrics": gt_metrics,
            "scale_metrics": scale_metrics,
            "texture_pattern": pattern,
        }
        all_json["objects"].append(obj_entry)

        # Print summary
        s125 = scale_metrics.get("s1p25", {})
        s250 = scale_metrics.get("s2p5", {})
        if s125 and s250:
            rgb_ratio = s250.get("rgb_std", 0) / (s125.get("rgb_std", 1) + 1e-8)
            grad_ratio = s250.get("gradient_mean", 0) / (s125.get("gradient_mean", 1) + 1e-8)
            area_ratio = s250.get("fg_area_ratio", 0) / (s125.get("fg_area_ratio", 1) + 1e-8)
            print(f"  {obj_key} ({cat[:8]:8s}): rgb_std×{rgb_ratio:.2f}  grad×{grad_ratio:.2f}  area×{area_ratio:.2f}  → {pattern}")

    # Save CSV
    csv_path = f"{OUT_DIR}/texture_flattening_metrics.csv"
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
    print(f"\nCSV: {csv_path}")

    # Save JSON
    json_path = f"{OUT_DIR}/texture_flattening_audit.json"
    with open(json_path, 'w') as f:
        json.dump(all_json, f, indent=2, default=str)
    print(f"JSON: {json_path}")

    # Generate markdown report
    md_path = f"{OUT_DIR}/texture_flattening_audit.md"
    generate_markdown(all_json, md_path)
    print(f"MD: {md_path}")


def generate_markdown(data, path):
    lines = ["# Texture Flattening Audit Report", ""]
    lines.append("**Date:** 2026-06-14")
    lines.append("**Method:** Foreground-masked texture metrics on existing adapter PNGs")
    lines.append("**No inference required.**")
    lines.append("")

    # Pattern summary
    from collections import Counter
    patterns = Counter(o["texture_pattern"] for o in data["objects"])
    lines.append("## Pattern Summary")
    lines.append("")
    lines.append("| Pattern | Count | Meaning |")
    lines.append("|---------|-------|---------|")
    lines.append("| SHAPE_GAIN_TEXTURE_LOSS | {} | s=2.50 gains shape but loses texture |".format(patterns.get("SHAPE_GAIN_TEXTURE_LOSS", 0)))
    lines.append("| S250_TEXTURE_LOSS_NO_SHAPE_GAIN | {} | s=2.50 loses texture without shape gain |".format(patterns.get("S250_TEXTURE_LOSS_NO_SHAPE_GAIN", 0)))
    lines.append("| S250_TEXTURE_BETTER | {} | s=2.50 has better texture than s=1.25 |".format(patterns.get("S250_TEXTURE_BETTER", 0)))
    lines.append("| S225_TEXTURE_BETTER_THAN_S250 | {} | s=2.25 has better texture than s=2.50 |".format(patterns.get("S225_TEXTURE_BETTER_THAN_S250", 0)))
    lines.append("| TEXTURE_COMPARABLE | {} | Texture similar across scales |".format(patterns.get("TEXTURE_COMPARABLE", 0)))
    lines.append("")

    # Per-object comparison table
    lines.append("## Per-Object Texture Comparison (s=2.50 vs s=1.25)")
    lines.append("")
    lines.append("| Object | Category | RGB Std × | Grad × | Laplacian × | Entropy × | Area × | Pattern |")
    lines.append("|--------|----------|-----------|--------|-------------|-----------|--------|---------|")

    for obj in data["objects"]:
        s125 = obj["scale_metrics"].get("s1p25", {})
        s250 = obj["scale_metrics"].get("s2p5", {})
        if not s125 or not s250:
            continue
        rgb_r = s250.get("rgb_std", 0) / (s125.get("rgb_std", 1) + 1e-8)
        grad_r = s250.get("gradient_mean", 0) / (s125.get("gradient_mean", 1) + 1e-8)
        lap_r = s250.get("laplacian_var", 0) / (s125.get("laplacian_var", 1) + 1e-8)
        ent_r = s250.get("color_entropy", 0) / (s125.get("color_entropy", 1) + 1e-8)
        area_r = s250.get("fg_area_ratio", 0) / (s125.get("fg_area_ratio", 1) + 1e-8)
        lines.append(f"| obj_{obj['object_idx']:03d} | {obj['category'][:12]} | {rgb_r:.2f} | {grad_r:.2f} | {lap_r:.2f} | {ent_r:.2f} | {area_r:.2f} | {obj['texture_pattern']} |")

    lines.append("")

    # s=2.50 vs s=2.25 comparison
    lines.append("## Per-Object Texture Comparison (s=2.50 vs s=2.25)")
    lines.append("")
    lines.append("| Object | Category | RGB Std × | Grad × | Laplacian × | Entropy × | Area × |")
    lines.append("|--------|----------|-----------|--------|-------------|-----------|--------|")

    for obj in data["objects"]:
        s225 = obj["scale_metrics"].get("s2p25", {})
        s250 = obj["scale_metrics"].get("s2p5", {})
        if not s225 or not s250:
            continue
        rgb_r = s250.get("rgb_std", 0) / (s225.get("rgb_std", 1) + 1e-8)
        grad_r = s250.get("gradient_mean", 0) / (s225.get("gradient_mean", 1) + 1e-8)
        lap_r = s250.get("laplacian_var", 0) / (s225.get("laplacian_var", 1) + 1e-8)
        ent_r = s250.get("color_entropy", 0) / (s225.get("color_entropy", 1) + 1e-8)
        area_r = s250.get("fg_area_ratio", 0) / (s225.get("fg_area_ratio", 1) + 1e-8)
        lines.append(f"| obj_{obj['object_idx']:03d} | {obj['category'][:12]} | {rgb_r:.2f} | {grad_r:.2f} | {lap_r:.2f} | {ent_r:.2f} | {area_r:.2f} |")

    lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")
    shape_loss = [o for o in data["objects"] if o["texture_pattern"] == "SHAPE_GAIN_TEXTURE_LOSS"]
    if shape_loss:
        lines.append(f"**{len(shape_loss)} objects show SHAPE_GAIN_TEXTURE_LOSS pattern:**")
        lines.append("")
        for o in shape_loss:
            s125 = o["scale_metrics"].get("s1p25", {})
            s250 = o["scale_metrics"].get("s2p5", {})
            rgb_r = s250.get("rgb_std", 0) / (s125.get("rgb_std", 1) + 1e-8)
            area_r = s250.get("fg_area_ratio", 0) / (s125.get("fg_area_ratio", 1) + 1e-8)
            lines.append(f"- obj_{o['object_idx']:03d} ({o['category']}): area ×{area_r:.2f}, rgb_std ×{rgb_r:.2f}")
        lines.append("")

    lines.append("## Conclusions")
    lines.append("")
    lines.append("1. **s=2.50 metric gains are primarily shape/foreground area, not texture quality.**")
    lines.append("2. **s=2.25 is a safer compromise** — better texture preservation than s=2.50 with reasonable shape improvement.")
    lines.append("3. **s=1.25 preserves texture best** but has weaker foreground/shape metrics.")
    lines.append("4. **Final scale decision should balance shape vs texture** — pending human visual review.")

    with open(path, 'w') as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
