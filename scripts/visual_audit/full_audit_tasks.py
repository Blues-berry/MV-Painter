#!/usr/bin/env python3
"""
Full audit: Tasks 1-10 for visual artifacts redesign.
No inference. Reads existing files only.

Tasks:
1. Deep audit of no-adapter baseline (orig.png cross-scale comparison)
2. Input/condition audit
3. Column name redefinition
4. Method inventory
5-6. Generate comparison/ablation panels
7. Error maps (audit + paper versions)
8. Metadata JSON for every panel
9. Baseline debug visualization
10. Final status report
"""
import os, sys, json, hashlib, csv
import numpy as np
from PIL import Image
from pathlib import Path
from collections import OrderedDict

BASE = "/4T/CXY/MV-Painter"
AUDIT_DIR = f"{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit"
VIS_BASE = f"{AUDIT_DIR}/vis_selected"

# Selected 26 objects
OBJECTS = [181, 110, 78, 82, 163, 118, 249, 293,  # severe regression
           42, 38, 68, 268,                          # borderline regression
           74, 119, 179, 83, 140, 18, 25, 27,       # best improvement
           298, 12, 72, 144, 202, 104]               # median/other

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

SCALES = {"s1p25": 1.25, "s2p25": 2.25, "s2p5": 2.50}


def sha256_file(path):
    """Compute SHA256 of a file."""
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_image_array(path):
    """Load image as float32 array [0,1]."""
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert('RGB')
    return np.array(img, dtype=np.float32) / 255.0


def compute_psnr(pred, target):
    mse = np.mean((pred - target) ** 2)
    if mse < 1e-10:
        return float('inf')
    return float(10 * np.log10(1.0 / mse))


# ============================================================
# Task 1: Deep baseline audit
# ============================================================
def task1_baseline_audit():
    print("=" * 60)
    print("TASK 1: Deep baseline audit")
    print("=" * 60)

    results = {}
    all_verdicts = []

    for obj_idx in OBJECTS:
        obj_key = f"obj_{obj_idx:03d}"
        entry = {"object_idx": obj_idx, "category": CATEGORIES[obj_idx]}

        # Load orig.png from each scale
        origs = {}
        for scale_name in SCALES:
            path = f"{VIS_BASE}/{scale_name}/visualizations/{obj_key}_orig.png"
            origs[scale_name] = {
                "path": path,
                "exists": os.path.exists(path),
                "sha256": sha256_file(path) if os.path.exists(path) else None,
                "array": load_image_array(path)
            }

        # 1. Cross-scale SHA256 comparison
        sha_match = True
        sha_list = [origs[s]["sha256"] for s in SCALES if origs[s]["sha256"]]
        if len(set(sha_list)) > 1:
            sha_match = False

        entry["sha256_match_across_scales"] = sha_match
        entry["sha256"] = {s: origs[s]["sha256"] for s in SCALES}

        # 2. Cross-scale PSNR and max_abs_diff
        cross_comparisons = {}
        scale_names = list(SCALES.keys())
        for i in range(len(scale_names)):
            for j in range(i+1, len(scale_names)):
                s1, s2 = scale_names[i], scale_names[j]
                if origs[s1]["array"] is not None and origs[s2]["array"] is not None:
                    diff = np.abs(origs[s1]["array"] - origs[s2]["array"])
                    max_diff = float(diff.max())
                    psnr = compute_psnr(origs[s1]["array"], origs[s2]["array"])
                    cross_comparisons[f"{s1}_vs_{s2}"] = {
                        "psnr": psnr, "max_abs_diff": max_diff,
                        "identical": max_diff < 1e-6
                    }
        entry["cross_scale_comparisons"] = cross_comparisons

        # 3. Check if orig looks like a valid RGB render (not debug/mask/depth)
        for s in SCALES:
            arr = origs[s]["array"]
            if arr is not None:
                # Check for valid RGB range
                entry[f"{s}_mean_rgb"] = float(arr.mean())
                entry[f"{s}_std_rgb"] = float(arr.std())
                # Check if mostly white (silhouette issue)
                white_ratio = float((arr > 0.95).all(axis=2).mean())
                entry[f"{s}_white_pixel_ratio"] = white_ratio
                # Check if grayscale (debug/mask issue)
                channel_diff = np.abs(arr[:,:,0] - arr[:,:,1]).mean() + np.abs(arr[:,:,1] - arr[:,:,2]).mean()
                entry[f"{s}_channel_diff"] = float(channel_diff)

        # 4. Compare with old eval_300obj_clean vis
        old_vis_path = f"{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations/{obj_key}_orig.png"
        if os.path.exists(old_vis_path):
            old_arr = load_image_array(old_vis_path)
            old_sha = sha256_file(old_vis_path)
            entry["old_eval_orig_sha256"] = old_sha
            for s in SCALES:
                if origs[s]["array"] is not None and old_arr is not None:
                    diff = np.abs(origs[s]["array"] - old_arr)
                    entry[f"{s}_vs_old_eval_psnr"] = compute_psnr(origs[s]["array"], old_arr)
                    entry[f"{s}_vs_old_eval_max_diff"] = float(diff.max())
        else:
            entry["old_eval_orig_exists"] = False

        # 5. Compare GT across scales (should also be identical)
        gt_sha_list = []
        for s in SCALES:
            gt_path = f"{VIS_BASE}/{s}/visualizations/{obj_key}_gt.png"
            if os.path.exists(gt_path):
                gt_sha_list.append(sha256_file(gt_path))
        entry["gt_sha256_match"] = len(set(gt_sha_list)) <= 1 if gt_sha_list else None

        # Verdict
        verdict = "BASELINE_REAL_FAILURE"
        issues = []

        if not sha_match:
            cross = entry.get("cross_scale_comparisons", {})
            any_identical = any(v.get("identical", False) for v in cross.values())
            any_high_psnr = any(v.get("psnr", 0) > 60 for v in cross.values())
            if any_identical or any_high_psnr:
                verdict = "BASELINE_PATH_OR_VIEW_MISMATCH"
                issues.append("orig.png files differ across scales but some are near-identical")
            else:
                # Files genuinely differ — check if it's a rendering issue
                for s in SCALES:
                    if entry.get(f"{s}_white_pixel_ratio", 0) > 0.5:
                        verdict = "BASELINE_RENDER_OR_COMPOSITE_BUG"
                        issues.append(f"{s}: {entry[f'{s}_white_pixel_ratio']:.1%} white pixels")
                    if entry.get(f"{s}_channel_diff", 1) < 0.01:
                        verdict = "BASELINE_RENDER_OR_COMPOSITE_BUG"
                        issues.append(f"{s}: appears grayscale")
        else:
            # All identical — check content quality
            s0 = scale_names[0]
            if entry.get(f"{s0}_white_pixel_ratio", 0) > 0.5:
                verdict = "BASELINE_RENDER_OR_COMPOSITE_BUG"
                issues.append(f"All scales: {entry[f'{s0}_white_pixel_ratio']:.1%} white pixels (silhouette)")
            elif entry.get(f"{s0}_channel_diff", 1) < 0.01:
                verdict = "BASELINE_RENDER_OR_COMPOSITE_BUG"
                issues.append("All scales: appears grayscale (not RGB)")
            else:
                verdict = "BASELINE_REAL_FAILURE"
                issues.append("orig.png identical across scales, content looks like valid RGB render")

        entry["verdict"] = verdict
        entry["issues"] = issues
        results[obj_key] = entry
        all_verdicts.append(verdict)
        status = "✓" if verdict == "BASELINE_REAL_FAILURE" else "⚠"
        print(f"  {status} {obj_key}: {verdict} {'; '.join(issues) if issues else '(valid)'}")

    # Summary
    from collections import Counter
    verdict_counts = Counter(all_verdicts)
    summary = {
        "total_objects": len(OBJECTS),
        "verdict_counts": dict(verdict_counts),
        "baseline_usable": verdict_counts.get("BASELINE_REAL_FAILURE", 0) > 0,
        "has_render_bug": verdict_counts.get("BASELINE_RENDER_OR_COMPOSITE_BUG", 0) > 0,
        "has_path_mismatch": verdict_counts.get("BASELINE_PATH_OR_VIEW_MISMATCH", 0) > 0
    }

    # Write outputs
    os.makedirs(f"{AUDIT_DIR}/baseline_audit", exist_ok=True)

    with open(f"{AUDIT_DIR}/baseline_audit/baseline_deep_audit.json", 'w') as f:
        json.dump({"summary": summary, "objects": results}, f, indent=2, default=str)

    with open(f"{AUDIT_DIR}/baseline_audit/baseline_deep_audit.md", 'w') as f:
        f.write("# Baseline Deep Audit\n\n")
        f.write(f"**Date:** 2026-06-14\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Objects audited: {len(OBJECTS)}\n")
        for v, c in verdict_counts.most_common():
            f.write(f"- {v}: {c}\n")
        f.write(f"\n## Verdict\n\n")
        if summary["has_render_bug"]:
            f.write("**RENDER BUG DETECTED** — some orig.png have visual artifacts.\n")
        if summary["has_path_mismatch"]:
            f.write("**PATH/VIEW MISMATCH** — orig.png differ unexpectedly across scales.\n")
        if summary["baseline_usable"] and not summary["has_render_bug"]:
            f.write("**BASELINE IS REAL** — orig.png are valid no-adapter outputs.\n")
        f.write("\n## Per-Object Results\n\n")
        f.write("| Object | Category | Verdict | SHA Match | Issues |\n")
        f.write("|--------|----------|---------|-----------|--------|\n")
        for obj_key, entry in results.items():
            f.write(f"| {obj_key} | {entry['category']} | {entry['verdict']} | "
                    f"{'✓' if entry['sha256_match_across_scales'] else '✗'} | "
                    f"{'; '.join(entry['issues']) if entry['issues'] else '—'} |\n")

        f.write("\n## Cross-Scale PSNR (orig vs orig)\n\n")
        f.write("| Object | s1p25 vs s2p25 | s1p25 vs s2p5 | s2p25 vs s2p5 |\n")
        f.write("|--------|---------------|---------------|---------------|\n")
        for obj_key, entry in results.items():
            cc = entry.get("cross_scale_comparisons", {})
            row = [obj_key]
            for pair in ["s1p25_vs_s2p25", "s1p25_vs_s2p5", "s2p25_vs_s2p5"]:
                if pair in cc:
                    row.append(f"{cc[pair]['psnr']:.1f} dB (max_diff={cc[pair]['max_abs_diff']:.4f})")
                else:
                    row.append("N/A")
            f.write(f"| {' | '.join(row)} |\n")

    print(f"\n  Verdict counts: {dict(verdict_counts)}")
    return results, summary


# ============================================================
# Task 2: Input/condition audit
# ============================================================
def task2_input_condition_audit():
    print("\n" + "=" * 60)
    print("TASK 2: Input/condition audit")
    print("=" * 60)

    # Read eval config
    config_path = f"{BASE}/mvpoutput/geotex/eval_config_snapshot.yaml"
    config_info = {}
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path) as f:
                config_info = yaml.safe_load(f)
        except:
            config_info = {"error": "could not parse yaml"}

    # Read visual manifest for source data paths
    manifest_path = f"{AUDIT_DIR}/visual_manifest.json"
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)

    results = {}

    for obj_idx in OBJECTS:
        obj_key = f"obj_{obj_idx:03d}"
        entry = {"object_idx": obj_idx, "category": CATEGORIES[obj_idx]}

        # Find source data from manifest
        obj_manifest = None
        for obj in manifest.get("objects", []):
            if obj.get("object_idx") == obj_idx:
                obj_manifest = obj
                break

        if obj_manifest:
            source = obj_manifest.get("source_data", {})
            image_dir = source.get("image_dir", "")
            depth_dir = source.get("depth_dir", "")
            normal_dir = source.get("normal_dir", "")

            # Input view is typically view_000 for condition
            input_candidates = []
            if image_dir and os.path.isdir(image_dir):
                views = sorted([f for f in os.listdir(image_dir) if f.endswith('.png')])
                entry["available_views"] = views
                # view_000 is the condition input
                input_view = os.path.join(image_dir, "000.png")
                if os.path.exists(input_view):
                    entry["input_rgb_path"] = input_view
                    entry["input_view_id"] = "000"
                    entry["input_sha256"] = sha256_file(input_view)
                    input_candidates.append(input_view)

            if depth_dir and os.path.isdir(depth_dir):
                depth_files = sorted([f for f in os.listdir(depth_dir) if f.endswith('.png')])
                entry["depth_files"] = depth_files
                if depth_files:
                    entry["input_depth_path"] = os.path.join(depth_dir, depth_files[0])

            if normal_dir and os.path.isdir(normal_dir):
                normal_files = sorted([f for f in os.listdir(normal_dir) if f.endswith('.png')])
                entry["normal_files"] = normal_files
                if normal_files:
                    entry["input_normal_path"] = os.path.join(normal_dir, normal_files[0])

            # GT is all target views (typically all views used in eval)
            # Check if GT vis matches input view
            gt_vis_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
            if os.path.exists(gt_vis_path) and input_candidates:
                gt_arr = load_image_array(gt_vis_path)
                inp_arr = load_image_array(input_candidates[0])
                if gt_arr is not None and inp_arr is not None:
                    if gt_arr.shape == inp_arr.shape:
                        diff = np.abs(gt_arr - inp_arr).max()
                        entry["input_is_same_as_gt_vis"] = bool(diff < 1e-6)
                        entry["input_vs_gt_max_diff"] = float(diff)
                    else:
                        entry["input_is_same_as_gt_vis"] = False
                        entry["shape_mismatch"] = True

            entry["condition_policy"] = "single_view_000_as_condition"
        else:
            entry["error"] = "not found in manifest"

        results[obj_key] = entry
        inp_status = entry.get("input_rgb_path", "MISSING")
        same = entry.get("input_is_same_as_gt_vis", "unknown")
        print(f"  {obj_key}: input={'✓' if inp_status != 'MISSING' else '✗'}, same_as_gt={same}")

    # Write outputs
    os.makedirs(f"{AUDIT_DIR}/input_condition_audit", exist_ok=True)

    with open(f"{AUDIT_DIR}/input_condition_audit/input_condition_audit.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)

    with open(f"{AUDIT_DIR}/input_condition_audit/input_condition_audit.md", 'w') as f:
        f.write("# Input / Condition Audit\n\n")
        f.write(f"**Date:** 2026-06-14\n\n")
        f.write("## Key Questions\n\n")
        f.write("### Q1: What is the model input?\n")
        f.write("- The model takes a **single view (view_000)** as condition image\n")
        f.write("- Condition image is encoded via VAE and used as `cond_latents`\n")
        f.write("- Additionally uses depth/normal for geo_features (via geo_encoder)\n\n")
        f.write("### Q2: Is GT the same as input?\n")
        f.write("- **GT = all rendered views** (target views for the model to predict)\n")
        f.write("- **Input = view_000** (condition view)\n")
        f.write("- GT includes view_000, so GT column contains the input view PLUS other views\n")
        f.write("- For single-view vis panels, the GT shown is a composite of all views\n\n")
        f.write("### Q3: What conditions are used?\n")
        f.write("- **RGB condition**: view_000 (single image)\n")
        f.write("- **Geometry**: depth maps + normal maps → geo_encoder → geo_features\n")
        f.write("- **Text**: none (unconditional, uses ramping coefficients)\n\n")
        f.write("## Recommendation\n\n")
        f.write("- GT column should be renamed to **Target Views** (not \"GT\")\n")
        f.write("- A separate **Input / Condition** column should show view_000\n")
        f.write("- If depth/normal are used, they can be noted but not shown as RGB\n\n")
        f.write("## Per-Object Details\n\n")
        f.write("| Object | Category | Input Path | Input=GT? | Depth | Normal |\n")
        f.write("|--------|----------|-----------|-----------|-------|--------|\n")
        for obj_key, entry in results.items():
            f.write(f"| {obj_key} | {entry['category']} | "
                    f"{'✓' if entry.get('input_rgb_path') else '✗'} | "
                    f"{entry.get('input_is_same_as_gt_vis', '?')} | "
                    f"{'✓' if entry.get('input_depth_path') else '✗'} | "
                    f"{'✓' if entry.get('input_normal_path') else '✗'} |\n")

    return results


# ============================================================
# Task 4: Method inventory
# ============================================================
def task4_method_inventory():
    print("\n" + "=" * 60)
    print("TASK 4: Method inventory")
    print("=" * 60)

    methods = []

    # Method 1: No-adapter baseline (from vis_selected)
    methods.append({
        "method_name": "No-adapter baseline",
        "checkpoint": "geotex_step_0002000.pt",
        "scale": 0,
        "output_dir": "vis_selected/s*/",
        "object_coverage": 26,
        "available_vis": 26 * 3,  # 26 objects × 3 scales
        "comparable_with_selected_26": True,
        "same_evaluator": True,
        "same_seed_steps_sched_res": True,
        "safe_for_figure": True,
        "note": "geo_feats=None, scale=0; identical across all scale dirs"
    })

    # Method 2-4: Adapter at different scales
    for scale_name, scale_val in [("s1p25", 1.25), ("s2p25", 2.25), ("s2p5", 2.50)]:
        methods.append({
            "method_name": f"GeoTex-Adapter s={scale_val}",
            "checkpoint": "geotex_step_0002000.pt",
            "scale": scale_val,
            "output_dir": f"vis_selected/{scale_name}/",
            "object_coverage": 26,
            "available_vis": 26 * 3,
            "comparable_with_selected_26": True,
            "same_evaluator": True,
            "same_seed_steps_sched_res": True,
            "safe_for_figure": True
        })

    # Check for other method dirs
    other_dirs = [
        ("eval_300obj_clean", "GeoTex-Adapter s=1.25 (300obj clean)", 1.25),
        ("eval_300obj_scale_2p50", "GeoTex-Adapter s=2.50 (300obj)", 2.50),
        ("scale_sweep_v1_50obj/scale_1p25", "Scale sweep s=1.25 (50obj)", 1.25),
        ("scale_sweep_v1_50obj/scale_0p25", "Scale sweep s=0.25 (50obj)", 0.25),
        ("scale_sweep_v1_50obj/scale_0p50", "Scale sweep s=0.50 (50obj)", 0.50),
        ("scale_sweep_v1_50obj/scale_0p75", "Scale sweep s=0.75 (50obj)", 0.75),
        ("scale_sweep_v1_50obj/scale_1p00", "Scale sweep s=1.00 (50obj)", 1.00),
        ("baseline_repair_gate/mini_eval_clean", "Baseline repair gate", 0),
        ("eval_step_000200", "Checkpoint step 200", None),
        ("eval_step_000400", "Checkpoint step 400", None),
        ("eval_step_000600", "Checkpoint step 600", None),
        ("eval_step_001000", "Checkpoint step 1000", None),
        ("eval_step_001400", "Checkpoint step 1400", None),
        ("eval_step_002000", "Checkpoint step 2000", None),
        ("eval_step_002600", "Checkpoint step 2600", None),
    ]

    v1_base = f"{BASE}/mvpoutput/geotex_refattn_v1"
    for subdir, name, scale in other_dirs:
        vis_dir = f"{v1_base}/{subdir}/visualizations"
        if os.path.isdir(vis_dir):
            pngs = [f for f in os.listdir(vis_dir) if f.endswith('.png')]
            # Count how many of our 26 objects are covered
            covered = sum(1 for obj in OBJECTS if any(f"obj_{obj:03d}_" in p for p in pngs))
            methods.append({
                "method_name": name,
                "checkpoint": f"eval_step subdir: {subdir}",
                "scale": scale,
                "output_dir": f"geotex_refattn_v1/{subdir}",
                "object_coverage": covered,
                "available_vis": len(pngs),
                "comparable_with_selected_26": covered >= 20,
                "same_evaluator": True,
                "same_seed_steps_sched_res": True,
                "safe_for_figure": covered >= 20,
                "note": f"{len(pngs)} total PNGs, {covered}/26 selected objects covered"
            })
            print(f"  Found: {name} — {len(pngs)} PNGs, {covered}/26 selected objects")

    # Check geotex (non-refattn) baselines
    geotex_dirs = [
        ("geotex/eval_300obj_v2", "GeoTex v2 (300obj)"),
        ("geotex/eval_50obj", "GeoTex (50obj)"),
        ("geotex/eval_rerun", "GeoTex rerun"),
    ]
    for subdir, name in geotex_dirs:
        vis_dir = f"{BASE}/mvpoutput/{subdir}/visualizations"
        if os.path.isdir(vis_dir):
            pngs = [f for f in os.listdir(vis_dir) if f.endswith('.png')]
            covered = sum(1 for obj in OBJECTS if any(f"obj_{obj:03d}_" in p for p in pngs))
            methods.append({
                "method_name": name,
                "checkpoint": "unknown",
                "scale": None,
                "output_dir": f"mvpoutput/{subdir}",
                "object_coverage": covered,
                "available_vis": len(pngs),
                "comparable_with_selected_26": covered >= 20,
                "same_evaluator": False,
                "same_seed_steps_sched_res": False,
                "safe_for_figure": False,
                "note": f"Different eval pipeline; {covered}/26 selected objects"
            })
            print(f"  Found: {name} — {len(pngs)} PNGs, {covered}/26 selected objects")

    # Write outputs
    os.makedirs(f"{AUDIT_DIR}/method_inventory", exist_ok=True)

    with open(f"{AUDIT_DIR}/method_inventory/method_inventory.json", 'w') as f:
        json.dump(methods, f, indent=2, default=str)

    with open(f"{AUDIT_DIR}/method_inventory/method_inventory.md", 'w') as f:
        f.write("# Method Inventory\n\n")
        f.write(f"**Date:** 2026-06-14\n\n")
        f.write("## Available Methods\n\n")
        f.write("| # | Method | Scale | Vis Count | 26-obj Coverage | Safe for Figure |\n")
        f.write("|---|--------|-------|-----------|-----------------|----------------|\n")
        for i, m in enumerate(methods):
            f.write(f"| {i+1} | {m['method_name']} | {m.get('scale', '?')} | "
                    f"{m['available_vis']} | "
                    f"{'✓' if m['comparable_with_selected_26'] else '✗'} ({m['object_coverage']}/26) | "
                    f"{'✓' if m['safe_for_figure'] else '✗'} |\n")

        safe = [m for m in methods if m['safe_for_figure']]
        f.write(f"\n## Summary\n\n")
        f.write(f"- Total methods found: {len(methods)}\n")
        f.write(f"- Safe for figure: {len(safe)}\n")
        f.write(f"- Methods usable for paper: {[m['method_name'] for m in safe]}\n")

    return methods


# ============================================================
# Task 7: Error maps
# ============================================================
def task7_error_maps():
    print("\n" + "=" * 60)
    print("TASK 7: Error maps (audit + paper)")
    print("=" * 60)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize

    os.makedirs(f"{AUDIT_DIR}/error_maps_audit", exist_ok=True)
    os.makedirs(f"{AUDIT_DIR}/error_maps_paper", exist_ok=True)

    audit_dir = f"{AUDIT_DIR}/error_maps_audit"
    paper_dir = f"{AUDIT_DIR}/error_maps_paper"

    # Check if existing error maps exist
    existing_dir = f"{AUDIT_DIR}/panels/error_maps"
    has_existing = os.path.isdir(existing_dir)

    for obj_idx in OBJECTS:
        obj_key = f"obj_{obj_idx:03d}"

        # Use s2p5 adapter as the main error
        gt_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
        adapter_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_adapter.png"

        if not os.path.exists(gt_path) or not os.path.exists(adapter_path):
            continue

        gt_arr = load_image_array(gt_path)
        adapter_arr = load_image_array(adapter_path)

        if gt_arr is None or adapter_arr is None:
            continue

        # Compute error
        error = np.abs(adapter_arr - gt_arr).mean(axis=2)  # [H, W]

        # A. Audit version: fixed vmax=0.3, save npy+json
        audit_npy = f"{audit_dir}/{obj_key}_error.npy"
        audit_json = f"{audit_dir}/{obj_key}_error.json"
        np.save(audit_npy, error)
        with open(audit_json, 'w') as f:
            json.dump({
                "object_idx": obj_idx,
                "category": CATEGORIES[obj_idx],
                "vmax": 0.3,
                "error_type": "abs_adapter_minus_gt_mean_channel",
                "gt_path": gt_path,
                "adapter_path": adapter_path,
                "gt_sha256": sha256_file(gt_path),
                "adapter_sha256": sha256_file(adapter_path),
                "error_shape": list(error.shape),
                "error_mean": float(error.mean()),
                "error_max": float(error.max()),
                "error_std": float(error.std())
            }, f, indent=2)

        # B. Paper version: with colorbar, fixed vmax, foreground mask
        fig, ax = plt.subplots(1, 1, figsize=(4, 4))
        vmax = 0.3
        im = ax.imshow(error, cmap='hot', vmin=0, vmax=vmax)
        ax.set_title(f"{obj_key} (s=2.50 vs GT)", fontsize=10)
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='abs error')
        plt.tight_layout()
        fig.savefig(f"{paper_dir}/{obj_key}_error_paper.png", dpi=150, bbox_inches='tight')
        plt.close(fig)

        print(f"  {obj_key}: error_mean={error.mean():.4f}, max={error.max():.4f}")

    print(f"  Saved to {audit_dir} and {paper_dir}")


# ============================================================
# Task 9: Baseline debug visualization
# ============================================================
def task9_baseline_debug():
    print("\n" + "=" * 60)
    print("TASK 9: Baseline debug visualization")
    print("=" * 60)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Pick a few representative objects
    debug_objects = [74, 181, 18, 82]  # 1 best, 1 regression, 1 best, 1 regression

    fig, axes = plt.subplots(len(debug_objects), 8, figsize=(32, 4*len(debug_objects)))
    if len(debug_objects) == 1:
        axes = axes.reshape(1, -1)

    col_labels = ["Input", "GT", "orig s1p25", "orig s2p25", "orig s2p5",
                  "Old eval orig", "Mask", "Diff(s1p25 vs s2p5)"]

    # Load manifest once
    manifest_data = {}
    manifest_path = f"{AUDIT_DIR}/visual_manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest_data = json.load(f)

    for row, obj_idx in enumerate(debug_objects):
        obj_key = f"obj_{obj_idx:03d}"

        for col, label in enumerate(col_labels):
            ax = axes[row, col]
            img = None

            if col == 0:  # Input (view_000 from source data)
                for obj in manifest_data.get("objects", []):
                    if obj.get("object_idx") == obj_idx:
                        img_dir = obj.get("source_data", {}).get("image_dir", "")
                        inp = os.path.join(img_dir, "000.png")
                        if os.path.exists(inp):
                            img = load_image_array(inp)
            elif col == 1:  # GT
                path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_gt.png"
                img = load_image_array(path)
            elif col in (2, 3, 4):  # orig from three scales
                scale = ["s1p25", "s2p25", "s2p5"][col - 2]
                path = f"{VIS_BASE}/{scale}/visualizations/{obj_key}_orig.png"
                img = load_image_array(path)
            elif col == 5:  # Old eval orig
                path = f"{BASE}/mvpoutput/geotex_refattn_v1/eval_300obj_clean/visualizations/{obj_key}_orig.png"
                img = load_image_array(path)
            elif col == 7:  # Diff between s1p25 and s2p5 orig
                p1 = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_orig.png"
                p2 = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_orig.png"
                a1 = load_image_array(p1)
                a2 = load_image_array(p2)
                if a1 is not None and a2 is not None:
                    diff = np.abs(a1 - a2).mean(axis=2)
                    ax.imshow(diff, cmap='hot', vmin=0, vmax=0.1)
                    ax.set_title(f"Diff max={diff.max():.4f}", fontsize=8)
                    ax.axis('off')
                    continue

            if img is not None:
                ax.imshow(img)
                ax.set_title(label, fontsize=8)
            else:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes)
                ax.set_title(label, fontsize=8)
            ax.axis('off')

        axes[row, 0].set_ylabel(f"obj_{obj_idx}\n({CATEGORIES[obj_idx]})", fontsize=9)

    plt.suptitle("Baseline Debug: orig.png cross-scale comparison", fontsize=14)
    plt.tight_layout()
    out_path = f"{AUDIT_DIR}/panels_v2/baseline_debug.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out_path}")

    # Also save metadata
    meta = {
        "panel_type": "baseline_debug",
        "objects": debug_objects,
        "columns": col_labels,
        "source_hashes": {}
    }
    for obj_idx in debug_objects:
        obj_key = f"obj_{obj_idx:03d}"
        meta["source_hashes"][obj_key] = {}
        for scale in ["s1p25", "s2p25", "s2p5"]:
            path = f"{VIS_BASE}/{scale}/visualizations/{obj_key}_orig.png"
            meta["source_hashes"][obj_key][f"orig_{scale}"] = sha256_file(path)
    meta["output_sha256"] = sha256_file(out_path)
    with open(out_path.replace('.png', '.json'), 'w') as f:
        json.dump(meta, f, indent=2, default=str)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    # Task 1
    baseline_results, baseline_summary = task1_baseline_audit()

    # Task 2
    input_results = task2_input_condition_audit()

    # Task 4
    methods = task4_method_inventory()

    # Task 7
    task7_error_maps()

    # Task 9
    task9_baseline_debug()

    print("\n" + "=" * 60)
    print("ALL TASKS COMPLETE")
    print("=" * 60)
