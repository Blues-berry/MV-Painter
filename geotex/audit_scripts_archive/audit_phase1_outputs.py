#!/usr/bin/env python3
"""
Phase 1: Output Completeness Audit
Checks all 3 key eval output directories for completeness and data integrity.
Generates: audit_outputs_manifest.md and audit_outputs_manifest.json
"""

import csv
import json
import os
import math
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path("/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1")

DIRECTORIES = {
    "eval_300obj_clean": {
        "path": BASE / "eval_300obj_clean",
        "csv": "per_object_metrics_fixed.csv",
        "expected_objects": 300,
        "expected_range": (0, 299),
        "schema": "v1_34col",
    },
    "scale_sweep_50obj_scale1p00": {
        "path": BASE / "scale_sweep_50obj" / "scale_1p00",
        "csv": "per_object_metrics.csv",
        "expected_objects": 50,
        "expected_range": None,  # check from data
        "schema": "v2_86col",
    },
    "scale_sweep_50obj_scale0p25": {
        "path": BASE / "scale_sweep_50obj" / "scale_0p25",
        "csv": "per_object_metrics.csv",
        "expected_objects": 50,
        "expected_range": None,
        "schema": "v2_86col",
    },
    "scale_sweep_50obj_scale0p50": {
        "path": BASE / "scale_sweep_50obj" / "scale_0p50",
        "csv": "per_object_metrics.csv",
        "expected_objects": 50,
        "expected_range": None,
        "schema": "v2_86col",
    },
    "scale_sweep_50obj_scale0p75": {
        "path": BASE / "scale_sweep_50obj" / "scale_0p75",
        "csv": "per_object_metrics.csv",
        "expected_objects": 50,
        "expected_range": None,
        "schema": "v2_86col",
    },
    "scale_sweep_50obj_scale1p25": {
        "path": BASE / "scale_sweep_50obj" / "scale_1p25",
        "csv": "per_object_metrics.csv",
        "expected_objects": 50,
        "expected_range": None,
        "schema": "v2_86col",
    },
    "scale_1p25_300obj": {
        "path": BASE / "scale_1p25_300obj",
        "csv": "per_object_metrics.csv",
        "expected_objects": 300,
        "expected_range": (0, 299),
        "schema": "v2_86col",
    },
}


def is_nan_or_inf(val):
    """Check if a float value is NaN or Inf."""
    if isinstance(val, str):
        return False
    return math.isnan(val) or math.isinf(val)


def safe_float(s):
    """Convert string to float, return None if not possible."""
    try:
        v = float(s)
        return v
    except (ValueError, TypeError):
        return None


def count_files_recursive(directory):
    """Count all files recursively."""
    count = 0
    for _, _, files in os.walk(directory):
        count += len(files)
    return count


def csv_sha256(filepath):
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_directory(name, config):
    """Audit a single output directory."""
    result = {"name": name, "status": "OK", "issues": [], "warnings": []}
    path = config["path"]
    csv_name = config["csv"]
    csv_path = path / csv_name

    # 1. Directory existence
    if not path.exists():
        result["status"] = "MISSING"
        result["issues"].append(f"Directory does not exist: {path}")
        return result

    # 2. File count
    result["total_files"] = count_files_recursive(path)

    # 3. CSV existence and line count
    if not csv_path.exists():
        result["status"] = "MISSING"
        result["issues"].append(f"CSV not found: {csv_path}")
        return result

    result["csv_sha256"] = csv_sha256(csv_path)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    result["csv_total_lines"] = len(rows) + 1  # including header
    result["csv_data_rows"] = len(rows)
    result["csv_columns"] = len(headers)
    result["csv_column_names"] = headers

    # 4. Expected object count
    expected = config["expected_objects"]
    if len(rows) != expected:
        result["issues"].append(
            f"Expected {expected} data rows, got {len(rows)}"
        )
        result["status"] = "WARN"

    # 5. object_idx analysis
    obj_indices = []
    for row in rows:
        val = safe_float(row.get("object_idx", ""))
        if val is not None:
            obj_indices.append(val)

    result["object_idx_count"] = len(obj_indices)
    result["object_idx_unique"] = len(set(obj_indices))
    result["object_idx_min"] = min(obj_indices) if obj_indices else None
    result["object_idx_max"] = max(obj_indices) if obj_indices else None

    # Check uniqueness
    if len(obj_indices) != len(set(obj_indices)):
        counter = Counter(obj_indices)
        dupes = {k: v for k, v in counter.items() if v > 1}
        result["issues"].append(f"Duplicate object_idx values: {dupes}")
        result["status"] = "FAIL"

    # Check expected range
    if config["expected_range"]:
        exp_min, exp_max = config["expected_range"]
        expected_set = set(range(exp_min, exp_max + 1))
        actual_set = set(int(x) for x in obj_indices)
        missing = expected_set - actual_set
        extra = actual_set - expected_set
        if missing:
            result["issues"].append(f"Missing object_idx values: {sorted(missing)[:20]}...")
            result["status"] = "FAIL"
        if extra:
            result["warnings"].append(f"Extra object_idx values: {sorted(extra)[:20]}...")

    # 6. NaN / Inf / empty value scan
    nan_inf_counts = {}
    empty_counts = {}
    numeric_columns = [h for h in headers if h != "object_idx"]

    for col in numeric_columns:
        nan_count = 0
        inf_count = 0
        empty_count = 0
        for row in rows:
            raw = row.get(col, "")
            if raw.strip() == "":
                empty_count += 1
                continue
            v = safe_float(raw)
            if v is not None:
                if math.isnan(v):
                    nan_count += 1
                elif math.isinf(v):
                    inf_count += 1
        if nan_count > 0:
            nan_inf_counts[f"{col}_nan"] = nan_count
        if inf_count > 0:
            nan_inf_counts[f"{col}_inf"] = inf_count
        if empty_count > 0:
            empty_counts[col] = empty_count

    result["nan_inf_counts"] = nan_inf_counts
    result["empty_value_counts"] = empty_counts

    if nan_inf_counts:
        result["issues"].append(f"NaN/Inf values found: {len(nan_inf_counts)} column-conditions")
        result["status"] = "FAIL" if result["status"] != "MISSING" else "MISSING"
    if empty_counts:
        result["issues"].append(f"Empty values found in {len(empty_counts)} columns")
        result["status"] = "WARN"

    # 7. Anomalous metric scan (only raw columns, not delta columns)
    anomalies = []

    # SSIM should be in [0, 1] — skip delta columns (negative deltas are expected)
    ssim_cols = [h for h in headers if "ssim" in h.lower() and not h.startswith("delta_")]
    for col in ssim_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col, ""))
            if v is not None:
                if v > 1.0 + 1e-6:
                    anomalies.append(f"SSIM > 1: {col}={v:.6f} at row {i} (object_idx={row.get('object_idx','?')})")
                elif v < -0.01:
                    anomalies.append(f"SSIM < 0: {col}={v:.6f} at row {i} (object_idx={row.get('object_idx','?')})")

    # LPIPS should be >= 0 (typically [0, 1]) — skip delta columns
    lpips_cols = [h for h in headers if "lpips" in h.lower() and not h.startswith("delta_")]
    for col in lpips_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col, ""))
            if v is not None:
                if v < -0.01:
                    anomalies.append(f"LPIPS < 0: {col}={v:.6f} at row {i} (object_idx={row.get('object_idx','?')})")
                elif v > 2.0:
                    anomalies.append(f"LPIPS > 2: {col}={v:.6f} at row {i} (object_idx={row.get('object_idx','?')})")

    # PSNR: check for extreme values (negative or > 100) — skip delta columns
    psnr_cols = [h for h in headers if "psnr" in h.lower() and not h.startswith("delta_")]
    for col in psnr_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col, ""))
            if v is not None:
                if v < -10:
                    anomalies.append(f"PSNR < -10: {col}={v:.4f} at row {i} (object_idx={row.get('object_idx','?')})")
                elif v > 100 and v != 100.0:
                    anomalies.append(f"PSNR > 100: {col}={v:.4f} at row {i} (object_idx={row.get('object_idx','?')})")

    result["anomalies"] = anomalies
    if anomalies:
        result["warnings"].append(f"{len(anomalies)} anomalous metric values found")

    # 8. Key summary statistics
    stats = {}
    key_cols = [
        "delta_fg_ssim", "delta_edge_ssim", "delta_full_psnr",
        "delta_fg_psnr", "delta_nef_ssim",
        "adapter_full_psnr", "adapter_full_ssim",
        "orig_full_psnr", "orig_full_ssim",
        "full_adapter_psnr", "full_adapter_ssim",
        "full_orig_psnr", "full_orig_ssim",
        "foreground_adapter_ssim", "foreground_orig_ssim",
        "edge_adapter_ssim", "edge_orig_ssim",
    ]
    for col in key_cols:
        if col not in headers:
            continue
        vals = [safe_float(row.get(col, "")) for row in rows]
        vals = [v for v in vals if v is not None and not math.isnan(v)]
        if vals:
            stats[col] = {
                "count": len(vals),
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
            }

    result["key_statistics"] = stats

    return result


def main():
    all_results = {}
    for name, config in DIRECTORIES.items():
        print(f"Auditing: {name}...")
        all_results[name] = audit_directory(name, config)

    # Cross-directory consistency check
    cross_checks = {}

    # Check: scale_sweep_50obj scale=1.00 vs eval_300obj_clean (first 50 objects)
    sweep_1p00 = all_results.get("scale_sweep_50obj_scale1p00", {})
    clean = all_results.get("eval_300obj_clean", {})

    if sweep_1p00.get("status") != "MISSING" and clean.get("status") != "MISSING":
        sweep_csv = BASE / "scale_sweep_50obj" / "scale_1p00" / "per_object_metrics.csv"
        clean_csv = BASE / "eval_300obj_clean" / "per_object_metrics_fixed.csv"

        if sweep_csv.exists() and clean_csv.exists():
            with open(sweep_csv) as f:
                sweep_rows = list(csv.DictReader(f))
            with open(clean_csv) as f:
                clean_rows = list(csv.DictReader(f))

            sweep_objs = set(int(float(r["object_idx"])) for r in sweep_rows)
            clean_objs = set(int(float(r["object_idx"])) for r in clean_rows[:50])

            cross_checks["sweep_1p00_vs_clean_first50"] = {
                "sweep_objects": sorted(sweep_objs),
                "clean_first50_objects": sorted(clean_objs),
                "overlap": len(sweep_objs & clean_objs),
                "sweep_only": sorted(sweep_objs - clean_objs),
                "clean_only": sorted(clean_objs - sweep_objs),
            }

    # Check: scale_1p25_300obj objects vs eval_300obj_clean objects
    s1p25 = all_results.get("scale_1p25_300obj", {})
    if s1p25.get("status") != "MISSING" and clean.get("status") != "MISSING":
        s1p25_csv = BASE / "scale_1p25_300obj" / "per_object_metrics.csv"
        if s1p25_csv.exists() and clean_csv.exists():
            with open(s1p25_csv) as f:
                s1p25_rows = list(csv.DictReader(f))

            s1p25_objs = set(int(float(r["object_idx"])) for r in s1p25_rows)
            clean_all_objs = set(int(float(r["object_idx"])) for r in clean_rows)

            cross_checks["scale_1p25_300obj_vs_clean"] = {
                "s1p25_object_count": len(s1p25_objs),
                "clean_object_count": len(clean_all_objs),
                "overlap": len(s1p25_objs & clean_all_objs),
                "s1p25_only": sorted(s1p25_objs - clean_all_objs),
                "clean_only": sorted(clean_all_objs - s1p25_objs),
            }

    # Summary judgment
    overall_status = "OK"
    critical_issues = []
    for name, r in all_results.items():
        if r["status"] == "FAIL":
            overall_status = "FAIL"
            critical_issues.append(f"{name}: {r['issues']}")
        elif r["status"] == "WARN" and overall_status == "OK":
            overall_status = "WARN"

    # Build output
    output = {
        "audit_phase": "Phase 1: Output Completeness",
        "overall_status": overall_status,
        "directories": all_results,
        "cross_checks": cross_checks,
        "critical_issues": critical_issues,
    }

    # Write JSON
    json_path = BASE / "audit_outputs_manifest.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nJSON manifest: {json_path}")

    # Write Markdown
    md_path = BASE / "audit_outputs_manifest.md"
    with open(md_path, "w") as f:
        f.write("# Phase 1: Output Completeness Audit\n\n")
        f.write(f"**Overall Status: {overall_status}**\n\n")

        for name, r in all_results.items():
            f.write(f"## {name}\n\n")
            f.write(f"- **Status**: {r['status']}\n")
            f.write(f"- **Total files**: {r.get('total_files', 'N/A')}\n")
            f.write(f"- **CSV data rows**: {r.get('csv_data_rows', 'N/A')}\n")
            f.write(f"- **CSV columns**: {r.get('csv_columns', 'N/A')}\n")
            f.write(f"- **CSV SHA256**: `{r.get('csv_sha256', 'N/A')}`\n")
            f.write(f"- **object_idx count**: {r.get('object_idx_count', 'N/A')}\n")
            f.write(f"- **object_idx unique**: {r.get('object_idx_unique', 'N/A')}\n")
            f.write(f"- **object_idx range**: [{r.get('object_idx_min', 'N/A')}, {r.get('object_idx_max', 'N/A')}]\n")

            if r.get("issues"):
                f.write(f"\n### Issues\n")
                for issue in r["issues"]:
                    f.write(f"- ❌ {issue}\n")

            if r.get("warnings"):
                f.write(f"\n### Warnings\n")
                for warn in r["warnings"]:
                    f.write(f"- ⚠️ {warn}\n")

            if r.get("nan_inf_counts"):
                f.write(f"\n### NaN/Inf Values\n")
                for k, v in r["nan_inf_counts"].items():
                    f.write(f"- {k}: {v}\n")

            if r.get("empty_value_counts"):
                f.write(f"\n### Empty Values\n")
                for k, v in r["empty_value_counts"].items():
                    f.write(f"- {k}: {v}\n")

            if r.get("anomalies"):
                f.write(f"\n### Anomalous Metrics ({len(r['anomalies'])} found)\n")
                for a in r["anomalies"][:50]:  # cap at 50
                    f.write(f"- {a}\n")
                if len(r["anomalies"]) > 50:
                    f.write(f"- ... and {len(r['anomalies']) - 50} more\n")

            if r.get("key_statistics"):
                f.write(f"\n### Key Statistics\n\n")
                f.write("| Column | Count | Mean | Min | Max |\n")
                f.write("|--------|-------|------|-----|-----|\n")
                for col, s in r["key_statistics"].items():
                    f.write(f"| {col} | {s['count']} | {s['mean']:.4f} | {s['min']:.4f} | {s['max']:.4f} |\n")

            f.write("\n")

        if cross_checks:
            f.write("## Cross-Directory Consistency\n\n")
            for check_name, check_data in cross_checks.items():
                f.write(f"### {check_name}\n\n")
                for k, v in check_data.items():
                    f.write(f"- **{k}**: {v}\n")
                f.write("\n")

    print(f"Markdown report: {md_path}")
    print(f"\n=== Overall Status: {overall_status} ===")
    if critical_issues:
        print("Critical issues:")
        for issue in critical_issues:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
