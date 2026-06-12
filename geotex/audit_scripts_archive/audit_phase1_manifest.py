#!/usr/bin/env python3
"""
Phase 1: Output Completeness Audit & Manifest Generation
Checks all 3 key output directories for:
- File counts, CSV line counts
- object_idx uniqueness and coverage
- Duplicate objects
- NaN / Inf / empty values
- Anomalous metrics (SSIM > 1, LPIPS < 0, extreme PSNR)
"""

import csv
import json
import os
import math
import hashlib
from pathlib import Path
from collections import Counter

BASE = Path("/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1")

# ──────────────────────────────────────────────
# Directory definitions
# ──────────────────────────────────────────────
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
        "expected_range": None,  # will check from data
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


def safe_float(v):
    """Convert to float, return None if not possible."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def count_files(directory):
    """Count files recursively."""
    total = 0
    for _, _, files in os.walk(directory):
        total += len(files)
    return total


def sha256_file(path):
    """SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_csv(csv_path, expected_objects, expected_range, schema):
    """Audit a single CSV file."""
    result = {
        "csv_path": str(csv_path),
        "exists": csv_path.exists(),
        "sha256": None,
        "total_lines": 0,
        "data_rows": 0,
        "columns": 0,
        "column_names": [],
        "object_idx": {
            "count": 0,
            "unique": 0,
            "duplicates": [],
            "min": None,
            "max": None,
            "missing_from_expected": [],
            "unexpected": [],
        },
        "nan_inf": {},
        "empty_values": {},
        "anomalies": [],
        "status": "OK",
        "issues": [],
    }

    if not csv_path.exists():
        result["status"] = "MISSING"
        result["issues"].append(f"CSV not found: {csv_path}")
        return result

    result["sha256"] = sha256_file(csv_path)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    result["total_lines"] = len(rows) + 1  # +1 for header
    result["data_rows"] = len(rows)
    result["columns"] = len(headers)
    result["column_names"] = headers

    # ── object_idx checks ──
    obj_indices = []
    for row in rows:
        v = safe_float(row.get("object_idx"))
        if v is not None:
            obj_indices.append(int(v))

    counter = Counter(obj_indices)
    duplicates = {k: v for k, v in counter.items() if v > 1}
    result["object_idx"]["count"] = len(obj_indices)
    result["object_idx"]["unique"] = len(set(obj_indices))
    result["object_idx"]["duplicates"] = duplicates
    result["object_idx"]["min"] = min(obj_indices) if obj_indices else None
    result["object_idx"]["max"] = max(obj_indices) if obj_indices else None

    if duplicates:
        result["status"] = "FAIL"
        result["issues"].append(f"Duplicate object_idx: {duplicates}")

    if expected_range:
        expected_set = set(range(expected_range[0], expected_range[1] + 1))
        actual_set = set(obj_indices)
        missing = sorted(expected_set - actual_set)
        unexpected = sorted(actual_set - expected_set)
        result["object_idx"]["missing_from_expected"] = missing
        result["object_idx"]["unexpected"] = unexpected
        if missing:
            result["status"] = "FAIL"
            result["issues"].append(f"Missing {len(missing)} expected object_idx")
        if unexpected:
            result["issues"].append(f"Unexpected {len(unexpected)} object_idx")

    if len(obj_indices) != expected_objects:
        result["issues"].append(
            f"Expected {expected_objects} objects, got {len(obj_indices)}"
        )
        if result["status"] == "OK":
            result["status"] = "WARN"

    # ── NaN / Inf / empty scan ──
    for col in headers:
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
            result["nan_inf"][f"{col}_nan"] = nan_count
        if inf_count > 0:
            result["nan_inf"][f"{col}_inf"] = inf_count
        if empty_count > 0:
            result["empty_values"][col] = empty_count

    if result["nan_inf"]:
        result["status"] = "FAIL"
        result["issues"].append(f"NaN/Inf in {len(result['nan_inf'])} columns")

    # ── Anomalous metrics ──
    anomalies = []
    ssim_cols = [h for h in headers if "ssim" in h.lower() and not h.startswith("delta_")]
    lpips_cols = [h for h in headers if "lpips" in h.lower() and not h.startswith("delta_")]
    psnr_cols = [h for h in headers if "psnr" in h.lower() and not h.startswith("delta_")]

    for col in ssim_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col))
            if v is not None:
                if v > 1.0 + 1e-6:
                    anomalies.append({
                        "type": "ssim_gt_1", "col": col, "row": i,
                        "object_idx": row.get("object_idx"), "value": v
                    })
                elif v < -0.01:
                    anomalies.append({
                        "type": "ssim_lt_0", "col": col, "row": i,
                        "object_idx": row.get("object_idx"), "value": v
                    })

    for col in lpips_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col))
            if v is not None and v < -0.01:
                anomalies.append({
                    "type": "lpips_lt_0", "col": col, "row": i,
                    "object_idx": row.get("object_idx"), "value": v
                })

    for col in psnr_cols:
        for i, row in enumerate(rows):
            v = safe_float(row.get(col))
            if v is not None:
                if v < -10:
                    anomalies.append({
                        "type": "psnr_extreme_low", "col": col, "row": i,
                        "object_idx": row.get("object_idx"), "value": v
                    })
                elif v > 100:
                    anomalies.append({
                        "type": "psnr_extreme_high", "col": col, "row": i,
                        "object_idx": row.get("object_idx"), "value": v
                    })

    result["anomalies"] = anomalies
    if anomalies:
        if result["status"] == "OK":
            result["status"] = "WARN"

    return result


def main():
    all_results = {}
    global_issues = []

    for name, cfg in DIRECTORIES.items():
        print(f"\n{'='*60}")
        print(f"Auditing: {name}")
        print(f"{'='*60}")

        dir_path = cfg["path"]
        csv_path = dir_path / cfg["csv"]

        dir_info = {
            "path": str(dir_path),
            "exists": dir_path.exists(),
            "total_files": count_files(dir_path) if dir_path.exists() else 0,
        }

        csv_result = audit_csv(
            csv_path, cfg["expected_objects"],
            cfg.get("expected_range"), cfg["schema"]
        )

        all_results[name] = {
            "directory": dir_info,
            "csv": csv_result,
            "expected_objects": cfg["expected_objects"],
            "schema": cfg["schema"],
        }

        status = csv_result["status"]
        print(f"  Status: {status}")
        print(f"  Files: {dir_info['total_files']}")
        print(f"  CSV rows: {csv_result['data_rows']}")
        print(f"  object_idx: {csv_result['object_idx']['unique']} unique, "
              f"range [{csv_result['object_idx']['min']}, {csv_result['object_idx']['max']}]")
        print(f"  NaN/Inf: {len(csv_result['nan_inf'])} columns")
        print(f"  Anomalies: {len(csv_result['anomalies'])}")

        if csv_result["issues"]:
            for issue in csv_result["issues"]:
                print(f"  ⚠ {issue}")
                global_issues.append(f"[{name}] {issue}")

    # ── Cross-directory consistency ──
    print(f"\n{'='*60}")
    print("Cross-directory consistency checks")
    print(f"{'='*60}")

    cross_checks = {}

    # Check 1: scale_1p25_300obj vs eval_300obj_clean object lists
    s1p25 = all_results.get("scale_1p25_300obj", {})
    clean = all_results.get("eval_300obj_clean", {})

    if s1p25.get("csv", {}).get("exists") and clean.get("csv", {}).get("exists"):
        s1p25_csv = BASE / "scale_1p25_300obj" / "per_object_metrics.csv"
        clean_csv = BASE / "eval_300obj_clean" / "per_object_metrics_fixed.csv"

        with open(s1p25_csv) as f:
            s1p25_objs = set(int(float(r["object_idx"])) for r in csv.DictReader(f))
        with open(clean_csv) as f:
            clean_objs = set(int(float(r["object_idx"])) for r in csv.DictReader(f))

        overlap = s1p25_objs & clean_objs
        only_s1p25 = s1p25_objs - clean_objs
        only_clean = clean_objs - s1p25_objs

        cross_checks["scale_1p25_vs_clean"] = {
            "s1p25_count": len(s1p25_objs),
            "clean_count": len(clean_objs),
            "overlap": len(overlap),
            "only_in_s1p25": sorted(only_s1p25)[:10],
            "only_in_clean": sorted(only_clean)[:10],
            "identical": s1p25_objs == clean_objs,
        }
        print(f"  scale_1p25 vs clean: identical={s1p25_objs == clean_objs}, "
              f"overlap={len(overlap)}")

    # Check 2: scale_sweep_50obj scale_1p00 objects vs first 50 of clean
    sweep_1p00 = all_results.get("scale_sweep_50obj_scale1p00", {})
    if sweep_1p00.get("csv", {}).get("exists") and clean.get("csv", {}).get("exists"):
        sweep_csv = BASE / "scale_sweep_50obj" / "scale_1p00" / "per_object_metrics.csv"
        with open(sweep_csv) as f:
            sweep_objs = set(int(float(r["object_idx"])) for r in csv.DictReader(f))

        clean_sorted = sorted(clean_objs)
        clean_first50 = set(clean_sorted[:50])

        cross_checks["sweep_1p00_vs_clean_first50"] = {
            "sweep_count": len(sweep_objs),
            "clean_first50_count": len(clean_first50),
            "overlap": len(sweep_objs & clean_first50),
            "sweep_objs": sorted(sweep_objs)[:10],
            "clean_first50": sorted(clean_first50)[:10],
            "identical": sweep_objs == clean_first50,
        }
        print(f"  sweep_1p00 vs clean_first50: identical={sweep_objs == clean_first50}, "
              f"overlap={len(sweep_objs & clean_first50)}")

    # ── Summary ──
    overall_status = "OK"
    for name, r in all_results.items():
        s = r["csv"]["status"]
        if s == "FAIL":
            overall_status = "FAIL"
        elif s == "WARN" and overall_status == "OK":
            overall_status = "WARN"

    print(f"\n{'='*60}")
    print(f"OVERALL STATUS: {overall_status}")
    print(f"{'='*60}")

    # ── Write outputs ──
    manifest = {
        "phase": "Phase 1: Output Completeness Audit",
        "overall_status": overall_status,
        "directories": all_results,
        "cross_checks": cross_checks,
        "global_issues": global_issues,
    }

    # JSON
    json_path = BASE / "audit_outputs_manifest.json"
    with open(json_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"\nJSON: {json_path}")

    # Markdown
    md_path = BASE / "audit_outputs_manifest.md"
    with open(md_path, "w") as f:
        f.write("# Phase 1: Output Completeness Audit\n\n")
        f.write(f"**Overall Status: {overall_status}**\n\n")

        for name, r in all_results.items():
            d = r["directory"]
            c = r["csv"]
            f.write(f"## {name}\n\n")
            f.write(f"- Directory: `{d['path']}`\n")
            f.write(f"- Exists: {d['exists']}\n")
            f.write(f"- Total files: {d['total_files']}\n")
            f.write(f"- Schema: {r['schema']}\n")
            f.write(f"- Expected objects: {r['expected_objects']}\n\n")

            f.write(f"### CSV Audit\n\n")
            f.write(f"- Status: **{c['status']}**\n")
            f.write(f"- SHA256: `{c['sha256']}`\n")
            f.write(f"- Data rows: {c['data_rows']}\n")
            f.write(f"- Columns: {c['columns']}\n")
            f.write(f"- object_idx unique: {c['object_idx']['unique']}\n")
            f.write(f"- object_idx range: [{c['object_idx']['min']}, {c['object_idx']['max']}]\n")
            f.write(f"- Duplicates: {c['object_idx']['duplicates']}\n")
            f.write(f"- NaN/Inf columns: {len(c['nan_inf'])}\n")
            f.write(f"- Anomalies: {len(c['anomalies'])}\n\n")

            if c["issues"]:
                f.write("**Issues:**\n")
                for issue in c["issues"]:
                    f.write(f"- ❌ {issue}\n")
                f.write("\n")

            if c["anomalies"]:
                f.write(f"**Anomalous metrics ({len(c['anomalies'])} total):**\n\n")
                for a in c["anomalies"][:20]:
                    f.write(f"- Row {a['row']} (obj {a['object_idx']}): "
                            f"`{a['col']}` = {a['value']:.6f} [{a['type']}]\n")
                if len(c["anomalies"]) > 20:
                    f.write(f"- ... and {len(c['anomalies']) - 20} more\n")
                f.write("\n")

        f.write("## Cross-Directory Consistency\n\n")
        for name, cc in cross_checks.items():
            f.write(f"### {name}\n\n")
            for k, v in cc.items():
                f.write(f"- {k}: {v}\n")
            f.write("\n")

    print(f"Markdown: {md_path}")
    return overall_status


if __name__ == "__main__":
    main()
