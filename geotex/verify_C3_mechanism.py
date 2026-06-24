"""E05 independent statistical reanalysis: C3 mechanism verification.

Reads raw per-object metrics for C3, C4, A_s1p75 and recomputes
paired t-tests, effect sizes, and bootstrap CIs.

Usage:
    python geotex/verify_C3_mechanism.py \
        --c3-csv mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/C3/per_object_metrics.csv \
        --c4-csv mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/C4/per_object_metrics.csv \
        --a-s1p75-csv mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/A_s1p75/per_object_metrics.csv \
        --c3-config mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/C3/config_snapshot.json \
        --c4-config mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/C4/config_snapshot.json \
        --a-s1p75-config mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix/A_s1p75/config_snapshot.json \
        --output-json <path> \
        --output-md <path>
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import math
from datetime import datetime, timezone


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_csv_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def load_json(path):
    with open(path) as f:
        return json.load(f)


def extract_metric(rows, metric_key):
    """Extract a metric as a list of floats, keyed by object_idx."""
    result = {}
    for row in rows:
        obj_id = row["object_idx"]
        val = float(row[metric_key])
        result[obj_id] = val
    return result


def extract_scale_desc(rows):
    """Extract scale_desc from first row."""
    return rows[0].get("scale_desc", "")


def paired_stats(x, y, labels):
    """Compute paired difference statistics.

    x, y: dict of {object_id: value}
    Returns dict with mean_diff, std_diff, t_stat, p_value, cohens_dz, n.
    """
    common = sorted(set(x.keys()) & set(y.keys()))
    n = len(common)
    diffs = [x[k] - y[k] for k in common]
    mean_diff = sum(diffs) / n
    std_diff = (sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)) ** 0.5
    se = std_diff / (n ** 0.5)
    t_stat = mean_diff / se if se > 0 else float("inf")

    # p-value via scipy if available
    try:
        from scipy import stats
        x_arr = [x[k] for k in common]
        y_arr = [y[k] for k in common]
        res = stats.ttest_rel(x_arr, y_arr)
        p_value = float(res.pvalue)
        p_value_source = "scipy.stats.ttest_rel"
    except ImportError:
        # Approximate p-value using t-distribution survival function
        # Using regularized incomplete beta function
        df = n - 1
        t_abs = abs(t_stat)
        # Two-tailed p-value approximation
        p_value = _t_dist_pvalue(t_abs, df)
        p_value_source = "manual_approximation"

    cohens_dz = mean_diff / std_diff if std_diff > 0 else float("inf")

    return {
        "n": n,
        "mean_diff": mean_diff,
        "std_diff": std_diff,
        "se_diff": se,
        "t_stat": t_stat,
        "p_value": p_value,
        "p_value_source": p_value_source,
        "cohens_dz": cohens_dz,
        "labels": labels,
    }


def _t_dist_pvalue(t_abs, df):
    """Two-tailed p-value for t-distribution using incomplete beta function."""
    x = df / (df + t_abs ** 2)
    # Use scipy special if available
    try:
        from scipy import special
        p = special.betainc(df / 2.0, 0.5, x)
        return float(p)
    except ImportError:
        # Fallback: use Python's math for incomplete beta via continued fraction
        # This is less precise but deterministic
        p = _incomplete_beta(df / 2.0, 0.5, x)
        return float(p)


def _incomplete_beta(a, b, x):
    """Regularized incomplete beta function I_x(a,b) via continued fraction."""
    if x < 0 or x > 1:
        return 0.0
    if x == 0:
        return 0.0
    if x == 1:
        return 1.0

    # Use Lentz's continued fraction
    ln_beta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)

    # Series expansion for small x
    if x < (a + 1) / (a + b + 2):
        return _beta_series(a, b, x) * math.exp(ln_beta) / (math.exp(math.lgamma(a) + math.lgamma(b)) / math.exp(math.lgamma(a + b)))
    else:
        return 1.0 - _beta_series(b, a, 1 - x) * math.exp(ln_beta) / (math.exp(math.lgamma(a) + math.lgamma(b)) / math.exp(math.lgamma(a + b)))


def _beta_series(a, b, x, max_iter=200, tol=1e-12):
    """Series expansion for incomplete beta."""
    result = 1.0
    term = 1.0
    for n in range(max_iter):
        term *= x * (a + n) / (a + b + n + 1) / (n + 1) if n > 0 else 1.0
        if n == 0:
            term = 1.0
            continue
        result += term
        if abs(term) < tol * abs(result):
            break
    # Normalize
    ln_coeff = math.lgamma(a + b) - math.lgamma(a + 1) - math.lgamma(b) + (a) * math.log(x) if x > 0 else 0
    return result * math.exp(ln_coeff) / a if a > 0 else 0


def bootstrap_ci(x, y, n_boot=10000, seed=0):
    """Bootstrap 95% CI for mean paired difference."""
    import numpy as np
    rng = np.random.default_rng(seed)
    common = sorted(set(x.keys()) & set(y.keys()))
    n = len(common)
    diffs = np.array([x[k] - y[k] for k in common])
    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(diffs, size=n, replace=True)
        boot_means[i] = sample.mean()
    lo = float(np.percentile(boot_means, 2.5))
    hi = float(np.percentile(boot_means, 97.5))
    return {"ci_95_lo": lo, "ci_95_hi": hi, "n_boot": n_boot, "seed": seed}


def main():
    parser = argparse.ArgumentParser(description="E05 C3 mechanism statistical reanalysis")
    parser.add_argument("--c3-csv", required=True)
    parser.add_argument("--c4-csv", required=True)
    parser.add_argument("--a-s1p75-csv", required=True)
    parser.add_argument("--c3-config", required=True)
    parser.add_argument("--c4-config", required=True)
    parser.add_argument("--a-s1p75-config", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    run_time = datetime.now(timezone.utc).isoformat()

    # Load data
    c3_rows = load_csv_rows(args.c3_csv)
    c4_rows = load_csv_rows(args.c4_csv)
    a_rows = load_csv_rows(args.a_s1p75_csv)

    # Load configs
    c3_cfg = load_json(args.c3_config)
    c4_cfg = load_json(args.c4_config)
    a_cfg = load_json(args.a_s1p75_config)

    # Compute input sha256
    c3_csv_sha = sha256_file(args.c3_csv)
    c4_csv_sha = sha256_file(args.c4_csv)
    a_csv_sha = sha256_file(args.a_s1p75_csv)
    c3_cfg_sha = sha256_file(args.c3_config)
    c4_cfg_sha = sha256_file(args.c4_config)
    a_cfg_sha = sha256_file(args.a_s1p75_config)

    # Script sha256
    script_path = os.path.abspath(__file__)
    script_sha = sha256_file(script_path)

    # Object IDs
    c3_ids = sorted([r["object_idx"] for r in c3_rows])
    c4_ids = sorted([r["object_idx"] for r in c4_rows])
    a_ids = sorted([r["object_idx"] for r in a_rows])

    c3_ids_hash = sha256_str(",".join(c3_ids))
    c4_ids_hash = sha256_str(",".join(c4_ids))
    a_ids_hash = sha256_str(",".join(a_ids))

    # Check alignment
    ids_aligned = (c3_ids == c4_ids == a_ids)
    n_objects = len(c3_ids)

    # Extract metrics
    c3_lap = extract_metric(c3_rows, "delta_fg_lap_var")
    c4_lap = extract_metric(c4_rows, "delta_fg_lap_var")
    a_lap = extract_metric(a_rows, "delta_fg_lap_var")

    c3_ssim = extract_metric(c3_rows, "delta_fg_ssim")
    c4_ssim = extract_metric(c4_rows, "delta_fg_ssim")
    a_ssim = extract_metric(a_rows, "delta_fg_ssim")

    # Scale info
    c3_scale = extract_scale_desc(c3_rows)
    c4_scale = extract_scale_desc(c4_rows)
    a_scale = extract_scale_desc(a_rows)

    # Compute average scale from config
    def avg_scale(cfg):
        ts = cfg.get("timestep_schedule", {})
        if ts:
            return (ts.get("early", 0) + ts.get("mid", 0) + ts.get("late", 0)) / 3
        return cfg.get("scale", None)

    c3_avg_scale = avg_scale(c3_cfg)
    c4_avg_scale = avg_scale(c4_cfg)
    a_avg_scale = avg_scale(a_cfg)

    # Paired tests: C3 vs C4
    lap_c3v4 = paired_stats(c3_lap, c4_lap, ["C3", "C4"])
    boot_c3v4 = bootstrap_ci(c3_lap, c4_lap)

    lap_c3va = paired_stats(c3_lap, a_lap, ["C3", "A_s1p75"])
    boot_c3va = bootstrap_ci(c3_lap, a_lap)

    ssim_c3v4 = paired_stats(c3_ssim, c4_ssim, ["C3", "C4"])
    ssim_c3va = paired_stats(c3_ssim, a_ssim, ["C3", "A_s1p75"])

    # Build result
    result = {
        "audit_time": run_time,
        "script_path": script_path,
        "script_sha256": script_sha,
        "input_files": {
            "c3_csv": {"path": args.c3_csv, "sha256": c3_csv_sha},
            "c4_csv": {"path": args.c4_csv, "sha256": c4_csv_sha},
            "a_s1p75_csv": {"path": args.a_s1p75_csv, "sha256": a_csv_sha},
            "c3_config": {"path": args.c3_config, "sha256": c3_cfg_sha},
            "c4_config": {"path": args.c4_config, "sha256": c4_cfg_sha},
            "a_s1p75_config": {"path": args.a_s1p75_config, "sha256": a_cfg_sha},
        },
        "object_alignment": {
            "c3_count": len(c3_ids),
            "c4_count": len(c4_ids),
            "a_s1p75_count": len(a_ids),
            "all_aligned": ids_aligned,
            "c3_ids_hash": c3_ids_hash,
            "c4_ids_hash": c4_ids_hash,
            "a_s1p75_ids_hash": a_ids_hash,
        },
        "scale_info": {
            "c3_scale_desc": c3_scale,
            "c4_scale_desc": c4_scale,
            "a_s1p75_scale_desc": a_scale,
            "c3_avg_scale": c3_avg_scale,
            "c4_avg_scale": c4_avg_scale,
            "a_s1p75_avg_scale": a_avg_scale,
            "c3_c4_same_avg_scale": abs(c3_avg_scale - c4_avg_scale) < 1e-6,
        },
        "texture_metric": {
            "metric": "delta_fg_lap_var",
            "c3_vs_c4": {**lap_c3v4, "bootstrap_ci": boot_c3v4},
            "c3_vs_a_s1p75": {**lap_c3va, "bootstrap_ci": boot_c3va},
        },
        "shape_metric": {
            "metric": "delta_fg_ssim",
            "c3_vs_c4": ssim_c3v4,
            "c3_vs_a_s1p75": ssim_c3va,
        },
    }

    # Write JSON
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, "w") as f:
        json.dump(result, f, indent=2)

    # Write MD
    md_lines = []
    md_lines.append("# E05 C3 Mechanism Statistical Reanalysis")
    md_lines.append(f"\n**Run time**: {run_time}")
    md_lines.append(f"**Script**: `{script_path}`")
    md_lines.append(f"**Script SHA256**: `{script_sha}`")
    md_lines.append(f"\n## Input Files\n")
    for k, v in result["input_files"].items():
        md_lines.append(f"- `{k}`: `{v['path']}` (sha256: `{v['sha256'][:16]}...`)")
    md_lines.append(f"\n## Object Alignment\n")
    md_lines.append(f"- C3 objects: {len(c3_ids)}")
    md_lines.append(f"- C4 objects: {len(c4_ids)}")
    md_lines.append(f"- A_s1p75 objects: {len(a_ids)}")
    md_lines.append(f"- All aligned: **{ids_aligned}**")
    md_lines.append(f"\n## Scale Info\n")
    md_lines.append(f"- C3 avg scale: {c3_avg_scale}")
    md_lines.append(f"- C4 avg scale: {c4_avg_scale}")
    md_lines.append(f"- A_s1p75 avg scale: {a_avg_scale}")
    md_lines.append(f"- C3 == C4 avg scale: **{abs(c3_avg_scale - c4_avg_scale) < 1e-6}**")
    md_lines.append(f"\n## Texture Metric: delta_fg_lap_var\n")
    md_lines.append("### C3 vs C4\n")
    md_lines.append(f"- n = {lap_c3v4['n']}")
    md_lines.append(f"- mean_diff = {lap_c3v4['mean_diff']:.8f}")
    md_lines.append(f"- std_diff = {lap_c3v4['std_diff']:.8f}")
    md_lines.append(f"- t-stat = {lap_c3v4['t_stat']:.8f}")
    md_lines.append(f"- p-value = {lap_c3v4['p_value']:.8e} (source: {lap_c3v4['p_value_source']})")
    md_lines.append(f"- Cohen's dz = {lap_c3v4['cohens_dz']:.8f}")
    md_lines.append(f"- Bootstrap 95% CI: [{boot_c3v4['ci_95_lo']:.8f}, {boot_c3v4['ci_95_hi']:.8f}]")
    md_lines.append("\n### C3 vs A_s1p75\n")
    md_lines.append(f"- n = {lap_c3va['n']}")
    md_lines.append(f"- mean_diff = {lap_c3va['mean_diff']:.8f}")
    md_lines.append(f"- std_diff = {lap_c3va['std_diff']:.8f}")
    md_lines.append(f"- t-stat = {lap_c3va['t_stat']:.8f}")
    md_lines.append(f"- p-value = {lap_c3va['p_value']:.8e} (source: {lap_c3va['p_value_source']})")
    md_lines.append(f"- Cohen's dz = {lap_c3va['cohens_dz']:.8f}")
    md_lines.append(f"- Bootstrap 95% CI: [{boot_c3va['ci_95_lo']:.8f}, {boot_c3va['ci_95_hi']:.8f}]")
    md_lines.append(f"\n## Shape Metric: delta_fg_ssim\n")
    md_lines.append("### C3 vs C4\n")
    md_lines.append(f"- mean_diff = {ssim_c3v4['mean_diff']:.8f}")
    md_lines.append(f"- t-stat = {ssim_c3v4['t_stat']:.8f}")
    md_lines.append(f"- p-value = {ssim_c3v4['p_value']:.8e}")
    md_lines.append("\n### C3 vs A_s1p75\n")
    md_lines.append(f"- mean_diff = {ssim_c3va['mean_diff']:.8f}")
    md_lines.append(f"- t-stat = {ssim_c3va['t_stat']:.8f}")
    md_lines.append(f"- p-value = {ssim_c3va['p_value']:.8e}")

    with open(args.output_md, "w") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Output JSON: {args.output_json}")
    print(f"Output MD:   {args.output_md}")
    print(f"Object alignment: {ids_aligned}")
    print(f"C3 avg scale: {c3_avg_scale}, C4 avg scale: {c4_avg_scale}")
    print(f"C3 vs C4 lap_var t={lap_c3v4['t_stat']:.4f} p={lap_c3v4['p_value']:.4e}")
    print(f"C3 vs A lap_var t={lap_c3va['t_stat']:.4f} p={lap_c3va['p_value']:.4e}")
    print(f"C3 vs C4 ssim t={ssim_c3v4['t_stat']:.4f} p={ssim_c3v4['p_value']:.4e}")


if __name__ == "__main__":
    main()
