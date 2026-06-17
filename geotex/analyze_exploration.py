"""Phase 4: Analyze exploration results.

Reads all variant results from inference_matrix/ and answers the 7 key questions.

Usage:
    python geotex/analyze_exploration.py
"""
import os, sys, csv, json
import numpy as np
from datetime import datetime

MATRIX_DIR = "mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix"
OUT_DIR = "mvpoutput/geotex_refattn_v1/exploration_v1"


def load_variant(name):
    """Load a variant's results."""
    path = os.path.join(MATRIX_DIR, name)
    csv_path = os.path.join(path, "per_object_metrics.csv")
    summary_path = os.path.join(path, "summary_metrics.json")
    if not os.path.exists(csv_path):
        return None
    rows = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rows.append(row)
    summary = {}
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)
    return {"name": name, "rows": rows, "summary": summary}


def load_probe_set():
    path = os.path.join(OUT_DIR, "probe_set.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def analyze():
    # Load all variants
    variants = {}
    if not os.path.exists(MATRIX_DIR):
        print("No inference_matrix directory found. Run experiments first.")
        return

    for name in sorted(os.listdir(MATRIX_DIR)):
        if name.startswith("_"):
            continue
        v = load_variant(name)
        if v and v["rows"]:
            variants[name] = v

    if not variants:
        print("No variant results found.")
        return

    probe = load_probe_set()
    probe_by_idx = {p["object_idx"]: p for p in probe}

    print(f"Loaded {len(variants)} variants, {len(probe)} probe objects")

    # ============================================================
    # Question 1: Which variants improve shape metrics?
    # ============================================================
    shape_analysis = {}
    for name, v in variants.items():
        deltas = []
        for row in v["rows"]:
            d_fg = safe_float(row.get("delta_fg_ssim"))
            d_edge = safe_float(row.get("delta_edge_ssim"))
            d_es = safe_float(row.get("delta_edge_fscore"))
            deltas.append({"fg_ssim": d_fg, "edge_ssim": d_edge, "edge_fscore": d_es})
        arr = np.array([[d["fg_ssim"], d["edge_ssim"], d["edge_fscore"]] for d in deltas])
        shape_analysis[name] = {
            "mean_fg_ssim": float(arr[:, 0].mean()),
            "mean_edge_ssim": float(arr[:, 1].mean()),
            "mean_edge_fscore": float(arr[:, 2].mean()),
            "positive_fg_ssim": int((arr[:, 0] > 0).sum()),
            "total": len(deltas),
        }

    # ============================================================
    # Question 2: Which variants lose texture metrics?
    # ============================================================
    texture_analysis = {}
    for name, v in variants.items():
        deltas = []
        for row in v["rows"]:
            d_lap = safe_float(row.get("delta_fg_lap_var"))
            d_rgb = safe_float(row.get("delta_fg_rgb_std"))
            d_grad = safe_float(row.get("delta_fg_grad_mag"))
            d_hf = safe_float(row.get("delta_fg_hf_energy"))
            d_entropy = safe_float(row.get("delta_fg_color_entropy"))
            deltas.append({"lap_var": d_lap, "rgb_std": d_rgb, "grad_mag": d_grad,
                           "hf_energy": d_hf, "color_entropy": d_entropy})
        arr = np.array([[d["lap_var"], d["rgb_std"], d["grad_mag"], d["hf_energy"], d["color_entropy"]]
                        for d in deltas])
        texture_analysis[name] = {
            "mean_lap_var": float(arr[:, 0].mean()),
            "mean_rgb_std": float(arr[:, 1].mean()),
            "mean_grad_mag": float(arr[:, 2].mean()),
            "mean_hf_energy": float(arr[:, 3].mean()),
            "mean_color_entropy": float(arr[:, 4].mean()),
            "negative_lap_var": int((arr[:, 0] < 0).sum()),
            "negative_rgb_std": int((arr[:, 1] < 0).sum()),
        }

    # ============================================================
    # Question 3: Better shape/texture trade-off than s=2.50?
    # ============================================================
    # Reference: s=2.50 shape gain, s=1.25 texture preservation
    ref_shape = shape_analysis.get("A_s2p50", {}).get("mean_fg_ssim", 0)
    ref_texture_125 = texture_analysis.get("A_s1p25", {}).get("mean_lap_var", 0)
    ref_texture_250 = texture_analysis.get("A_s2p50", {}).get("mean_lap_var", 0)

    tradeoff_analysis = {}
    for name in variants:
        s = shape_analysis.get(name, {})
        t = texture_analysis.get(name, {})
        shape_gain = s.get("mean_fg_ssim", 0)
        texture_loss = t.get("mean_lap_var", 0)

        # PROMISING: shape gain >= 80% of s=2.50, texture loss <= 80% of s=1.25
        is_promising = (shape_gain >= 0.8 * ref_shape and
                        (abs(texture_loss) <= 0.8 * abs(ref_texture_125) if ref_texture_125 != 0 else True))

        # METRIC_TRAP: fg_ssim improves but lap_var drops > 30%
        is_trap = (shape_gain > 0 and
                   (texture_loss < -0.3 * abs(ref_texture_250) if ref_texture_250 != 0 else False))

        tradeoff_analysis[name] = {
            "shape_gain": shape_gain,
            "texture_loss": texture_loss,
            "shape_ratio_vs_250": shape_gain / ref_shape if ref_shape > 0 else 0,
            "is_promising": is_promising,
            "is_metric_trap": is_trap,
        }

    # ============================================================
    # Question 4: Safer than s=2.25 but stronger shape?
    # ============================================================
    ref_225_shape = shape_analysis.get("A_s2p25", {}).get("mean_fg_ssim", 0)

    safer_analysis = {}
    for name in variants:
        s = shape_analysis.get(name, {}).get("mean_fg_ssim", 0)
        # Safer = fewer severe regressions
        severe_count = 0
        for row in variants[name]["rows"]:
            d = safe_float(row.get("delta_fg_ssim"))
            if d < -0.1:
                severe_count += 1
        safer_analysis[name] = {
            "shape_gain": s,
            "severe_regression_count": severe_count,
            "is_safer_and_stronger": (s > ref_225_shape and severe_count <= 2),
        }

    # ============================================================
    # Question 5: Which object buckets benefit most?
    # ============================================================
    bucket_analysis = {}
    for name, v in variants.items():
        buckets = {}
        for row in v["rows"]:
            obj_idx = int(row.get("object_idx", 0))
            p = probe_by_idx.get(obj_idx, {})
            cat = p.get("category", "unknown")
            d_fg = safe_float(row.get("delta_fg_ssim"))
            d_lap = safe_float(row.get("delta_fg_lap_var"))
            buckets.setdefault(cat, []).append({"fg_ssim": d_fg, "lap_var": d_lap})
        bucket_summary = {}
        for cat, items in buckets.items():
            arr_fg = np.array([i["fg_ssim"] for i in items])
            arr_lap = np.array([i["lap_var"] for i in items])
            bucket_summary[cat] = {
                "mean_fg_ssim": float(arr_fg.mean()),
                "mean_lap_var": float(arr_lap.mean()),
                "count": len(items),
            }
        bucket_analysis[name] = bucket_summary

    # ============================================================
    # Question 6: Which buckets are most susceptible to texture flattening?
    # ============================================================
    # Aggregate across all variants
    bucket_flattening = {}
    for name, v in variants.items():
        for row in v["rows"]:
            obj_idx = int(row.get("object_idx", 0))
            p = probe_by_idx.get(obj_idx, {})
            cat = p.get("category", "unknown")
            d_lap = safe_float(row.get("delta_fg_lap_var"))
            d_rgb = safe_float(row.get("delta_fg_rgb_std"))
            bucket_flattening.setdefault(cat, []).append({"lap_var": d_lap, "rgb_std": d_rgb})

    flattening_summary = {}
    for cat, items in bucket_flattening.items():
        arr_lap = np.array([i["lap_var"] for i in items])
        arr_rgb = np.array([i["rgb_std"] for i in items])
        flattening_summary[cat] = {
            "mean_lap_var_delta": float(arr_lap.mean()),
            "mean_rgb_std_delta": float(arr_rgb.mean()),
            "negative_lap_count": int((arr_lap < 0).sum()),
            "total_measurements": len(items),
        }

    # ============================================================
    # Question 7: Layer-wise vs timestep-wise vs global
    # ============================================================
    type_comparison = {"global": [], "layer_wise": [], "timestep_wise": []}
    for name, v in variants.items():
        variant_type = "global" if name.startswith("A_") else \
                       "layer_wise" if name.startswith("B") else "timestep_wise"
        for row in v["rows"]:
            d_fg = safe_float(row.get("delta_fg_ssim"))
            d_lap = safe_float(row.get("delta_fg_lap_var"))
            type_comparison[variant_type].append({"fg_ssim": d_fg, "lap_var": d_lap})

    type_summary = {}
    for vtype, items in type_comparison.items():
        if not items:
            continue
        arr_fg = np.array([i["fg_ssim"] for i in items])
        arr_lap = np.array([i["lap_var"] for i in items])
        type_summary[vtype] = {
            "mean_fg_ssim": float(arr_fg.mean()),
            "mean_lap_var": float(arr_lap.mean()),
            "std_fg_ssim": float(arr_fg.std()),
            "count": len(items),
        }

    # ============================================================
    # Compile results
    # ============================================================
    results = {
        "timestamp": datetime.now().isoformat(),
        "num_variants": len(variants),
        "num_probe_objects": len(probe),
        "variants": list(variants.keys()),
        "q1_shape_improvement": shape_analysis,
        "q2_texture_loss": texture_analysis,
        "q3_tradeoff": tradeoff_analysis,
        "q4_safer_than_225": safer_analysis,
        "q5_bucket_benefit": bucket_analysis,
        "q6_bucket_flattening": flattening_summary,
        "q7_type_comparison": type_summary,
        "best_global_scale": max(
            [(n, shape_analysis.get(n, {}).get("mean_fg_ssim", 0))
             for n in variants if n.startswith("A_")],
            key=lambda x: x[1], default=("none", 0)
        )[0],
        "best_layer_variant": max(
            [(n, shape_analysis.get(n, {}).get("mean_fg_ssim", 0))
             for n in variants if n.startswith("B")],
            key=lambda x: x[1], default=("none", 0)
        )[0],
        "best_timestep_variant": max(
            [(n, shape_analysis.get(n, {}).get("mean_fg_ssim", 0))
             for n in variants if n.startswith("C")],
            key=lambda x: x[1], default=("none", 0)
        )[0],
        "promising_variants": [n for n, t in tradeoff_analysis.items() if t.get("is_promising")],
        "metric_trap_variants": [n for n, t in tradeoff_analysis.items() if t.get("is_metric_trap")],
    }

    # Save JSON
    with open(os.path.join(OUT_DIR, "inference_matrix_summary.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Generate markdown
    md = generate_markdown(results, variants, shape_analysis, texture_analysis,
                           tradeoff_analysis, safer_analysis, bucket_analysis,
                           flattening_summary, type_summary)
    with open(os.path.join(OUT_DIR, "inference_matrix_summary.md"), "w") as f:
        f.write(md)

    print(f"Analysis complete. Output: {OUT_DIR}/inference_matrix_summary.json/md")


def generate_markdown(results, variants, shape, texture, tradeoff, safer,
                      buckets, flattening, type_comp):
    lines = [
        "# Exploration V1: Inference Matrix Analysis",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Variants: {results['num_variants']}, Objects: {results['num_probe_objects']}",
        "",
        "---",
        "",
        "## Q1: Shape Improvement by Variant",
        "",
        "| Variant | FG SSIM Δ | Edge SSIM Δ | Edge F-score Δ | Positive % |",
        "|---------|-----------|-------------|----------------|------------|",
    ]
    for name in sorted(shape.keys()):
        s = shape[name]
        pct = 100 * s["positive_fg_ssim"] / max(s["total"], 1)
        lines.append(f"| {name} | {s['mean_fg_ssim']:+.4f} | {s['mean_edge_ssim']:+.4f} | "
                     f"{s['mean_edge_fscore']:+.4f} | {pct:.0f}% |")

    lines.extend([
        "",
        "## Q2: Texture Loss by Variant",
        "",
        "| Variant | Lap Var Δ | RGB Std Δ | Grad Mag Δ | HF Energy Δ | Neg Lap % |",
        "|---------|-----------|-----------|------------|-------------|-----------|",
    ])
    for name in sorted(texture.keys()):
        t = texture[name]
        neg_pct = 100 * t["negative_lap_var"] / max(variants[name]["summary"].get("num_objects", 24), 1)
        lines.append(f"| {name} | {t['mean_lap_var']:+.4f} | {t['mean_rgb_std']:+.4f} | "
                     f"{t['mean_grad_mag']:+.4f} | {t['mean_hf_energy']:+.4f} | {neg_pct:.0f}% |")

    lines.extend([
        "",
        "## Q3: Shape/Texture Trade-off",
        "",
        "| Variant | Shape Gain | Texture Loss | vs s=2.50 | Status |",
        "|---------|------------|--------------|-----------|--------|",
    ])
    for name in sorted(tradeoff.keys()):
        t = tradeoff[name]
        status = "PROMISING" if t["is_promising"] else "TRAP" if t["is_metric_trap"] else "OK"
        lines.append(f"| {name} | {t['shape_gain']:+.4f} | {t['texture_loss']:+.4f} | "
                     f"{t['shape_ratio_vs_250']:.2f}x | {status} |")

    lines.extend([
        "",
        "## Q4: Safer Than s=2.25 But Stronger Shape",
        "",
        "| Variant | Shape Gain | Severe Regressions | Safer+Stronger |",
        "|---------|------------|-------------------|----------------|",
    ])
    for name in sorted(safer.keys()):
        s = safer[name]
        marker = "✓" if s["is_safer_and_stronger"] else "✗"
        lines.append(f"| {name} | {s['shape_gain']:+.4f} | {s['severe_regression_count']} | {marker} |")

    lines.extend([
        "",
        "## Q5: Bucket Benefit (best variant per bucket)",
        "",
        "See inference_matrix_summary.json for full bucket breakdown.",
        "",
        "## Q6: Texture Flattening by Object Bucket",
        "",
        "| Bucket | Lap Var Δ | RGB Std Δ | Neg Lap Count | Total |",
        "|--------|-----------|-----------|---------------|-------|",
    ])
    for cat in sorted(flattening.keys()):
        f = flattening[cat]
        lines.append(f"| {cat} | {f['mean_lap_var_delta']:+.4f} | {f['mean_rgb_std_delta']:+.4f} | "
                     f"{f['negative_lap_count']} | {f['total_measurements']} |")

    lines.extend([
        "",
        "## Q7: Global vs Layer-wise vs Timestep-wise",
        "",
        "| Type | Mean FG SSIM Δ | Mean Lap Var Δ | Std FG SSIM | Count |",
        "|------|----------------|----------------|-------------|-------|",
    ])
    for vtype in ["global", "layer_wise", "timestep_wise"]:
        if vtype in type_comp:
            t = type_comp[vtype]
            lines.append(f"| {vtype} | {t['mean_fg_ssim']:+.4f} | {t['mean_lap_var']:+.4f} | "
                         f"{t['std_fg_ssim']:.4f} | {t['count']} |")

    lines.extend([
        "",
        "## Key Findings",
        "",
        f"- Best global scale: **{results['best_global_scale']}**",
        f"- Best layer-wise variant: **{results['best_layer_variant']}**",
        f"- Best timestep-wise variant: **{results['best_timestep_variant']}**",
        f"- Promising variants: {', '.join(results['promising_variants']) or 'none'}",
        f"- Metric trap variants: {', '.join(results['metric_trap_variants']) or 'none'}",
        "",
        "## Phase 5 Recommendation",
        "",
        "See inference_matrix_summary.json for micro-training config recommendations.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    analyze()
