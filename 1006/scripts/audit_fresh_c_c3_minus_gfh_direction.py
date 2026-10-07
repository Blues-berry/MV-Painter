#!/usr/bin/env python3
"""Independently recheck signs, endpoint directions, summaries, and wording."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


METRICS = {
    "FG-PSNR": ("fg_psnr", "higher"),
    "FG-SSIM": ("fg_ssim", "higher"),
    "FG-LPIPS": ("fg_lpips", "lower"),
    "Full-PSNR": ("full_psnr", "higher"),
    "Full-SSIM": ("full_ssim", "higher"),
    "Full-LPIPS": ("full_lpips", "lower"),
    "Edge-SSIM": ("edge_ssim", "higher"),
}
N_BOOTSTRAP = 10_000
RNG_SEED = 20261002
TOLERANCE = 1e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path, default=Path(__file__).resolve().parents[1] / "review")
    args = parser.parse_args()
    review_dir = args.review_dir
    integrity_path = review_dir / "R1_4_FRESHC_C3_GFH_SOURCE_INTEGRITY.json"
    results_path = review_dir / "R1_4_FRESHC_C3_minus_GFH_posthoc_results.json"
    markdown_path = review_dir / "R1_4_FRESHC_C3_minus_GFH_posthoc_audit_20261007.md"
    raw_path = args.data_dir / "runs" / "c3_confirmation" / "per_object_metrics.csv"
    output_path = review_dir / "R1_4_SIGN_DIRECTION_AUDIT.json"
    errors: list[dict[str, str]] = []
    checks: list[dict[str, Any]] = []

    required = [integrity_path, results_path, markdown_path, raw_path]
    missing = [str(path) for path in required if not path.is_file()]
    checks.append({"check": "required_inputs_present", "status": "PASS" if not missing else "FAIL", "detail": missing})
    if missing:
        write_json(output_path, {"status": "FAIL", "R1_4_DIRECTION_ERRORS": len(missing), "errors": missing, "checks": checks})
        return 2

    integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
    results = json.loads(results_path.read_text(encoding="utf-8"))
    raw_sha = sha256_file(raw_path)
    hash_ok = integrity.get("status") == "PASS" and integrity.get("source_hashes", {}).get("raw_source_sha256") == raw_sha
    checks.append({
        "check": "raw_source_hash_matches_integrity_gate",
        "status": "PASS" if hash_ok else "FAIL",
        "detail": {"expected": integrity.get("source_hashes", {}).get("raw_source_sha256"), "observed": raw_sha},
    })
    if not hash_ok:
        errors.append({"check": "raw_source_hash_matches_integrity_gate", "detail": "raw source differs from the passing source-integrity record"})

    frame = pd.read_csv(raw_path)
    if frame.duplicated(["condition", "object_uid"]).any():
        errors.append({"check": "paired_key_uniqueness", "detail": "duplicate condition × UID key found"})
    c3 = frame[frame.condition == "native_gc3"].set_index("object_uid").sort_index()
    gfh = frame[frame.condition == "native_gfh"].set_index("object_uid").sort_index()
    uid_match = len(c3) == len(gfh) == 300 and c3.index.equals(gfh.index)
    checks.append({"check": "exact_paired_uids", "status": "PASS" if uid_match else "FAIL", "detail": {"c3_n": len(c3), "gfh_n": len(gfh), "same_index": bool(c3.index.equals(gfh.index))}})
    if not uid_match:
        errors.append({"check": "exact_paired_uids", "detail": "C3 and GFH do not contain the exact same 300 UIDs"})

    result_by_metric = {row["metric"]: row for row in results.get("results", [])}
    rng = np.random.default_rng(RNG_SEED)
    n = min(len(c3), len(gfh))
    bootstrap_indices = rng.integers(0, n, size=(N_BOOTSTRAP, n), dtype=np.int32) if n else np.empty((0, 0), dtype=np.int32)
    audits = []
    for metric, (column, direction) in METRICS.items():
        values_a = pd.to_numeric(c3[column], errors="coerce").to_numpy(dtype=float)
        values_b = pd.to_numeric(gfh[column], errors="coerce").to_numpy(dtype=float)
        differences = values_a - values_b
        finite = bool(np.isfinite(differences).all())
        favorable_a = differences > 0 if direction == "higher" else differences < 0
        unfavorable_b = differences < 0 if direction == "higher" else differences > 0
        ties = differences == 0
        mean = float(differences.mean()) if finite and n else float("nan")
        median = float(np.median(differences)) if finite and n else float("nan")
        if finite and n:
            boot_means = differences[bootstrap_indices].mean(axis=1)
            ci_lower, ci_upper = [float(x) for x in np.percentile(boot_means, [2.5, 97.5])]
        else:
            ci_lower = ci_upper = float("nan")
        recorded = result_by_metric.get(metric, {})
        metric_checks = {
            "mean_matches_results": abs(mean - float(recorded.get("effect_A_minus_B", float("nan")))) <= TOLERANCE,
            "median_matches_results": abs(median - float(recorded.get("median_A_minus_B", float("nan")))) <= TOLERANCE,
            "ci_lower_matches_results": abs(ci_lower - float(recorded.get("ci95_lower", float("nan")))) <= TOLERANCE,
            "ci_upper_matches_results": abs(ci_upper - float(recorded.get("ci95_upper", float("nan")))) <= TOLERANCE,
            "favorable_count_matches_results": int(favorable_a.sum()) == int(recorded.get("favorable_count_for_condition_A", -1)),
            "unfavorable_count_matches_results": int(unfavorable_b.sum()) == int(recorded.get("unfavorable_count_for_condition_B", -1)),
            "tie_count_matches_results": int(ties.sum()) == int(recorded.get("tie_count", -1)),
            "direction_matches_results": recorded.get("direction") == direction,
            "classification_is_posthoc": recorded.get("analysis_classification") == "REVIEWER_REQUESTED_POST_HOC_AUDIT",
            "finite_paired_differences": finite,
        }
        for check_name, passed in metric_checks.items():
            checks.append({"check": f"{metric}:{check_name}", "status": "PASS" if passed else "FAIL"})
            if not passed:
                errors.append({"check": f"{metric}:{check_name}", "detail": "independent raw-data recomputation disagrees with stored result or metadata"})

        if mean == 0:
            mean_favors = "no mean direction"
        elif (mean > 0) == (direction == "higher"):
            mean_favors = "C3"
        else:
            mean_favors = "GFH"
        if median == 0:
            median_favors = "no median direction"
        elif (median > 0) == (direction == "higher"):
            median_favors = "C3"
        else:
            median_favors = "GFH"
        ci_crosses_zero = ci_lower <= 0 <= ci_upper
        wording = (
            f"For {metric} ({direction}-is-better), C3−GFH was {mean:+.6f} "
            f"(95% paired object-bootstrap CI [{ci_lower:+.6f}, {ci_upper:+.6f}]); "
            f"the mean direction favors {mean_favors}, the median direction favors {median_favors}, "
            f"and {int(favorable_a.sum())}/300 objects favor C3 ({100*favorable_a.mean():.1f}%)."
        )
        if metric == "Edge-SSIM" and mean < 0 and direction == "higher":
            wording += " This Edge-SSIM estimate favors GFH."
        audits.append({
            "metric": metric,
            "condition_A_minus_condition_B": "native_gc3 - native_gfh",
            "metric_direction": f"{direction}-is-better",
            "mean_difference": mean,
            "mean_sign": "positive" if mean > 0 else "negative" if mean < 0 else "zero",
            "mean_favors": mean_favors,
            "ci95": [ci_lower, ci_upper],
            "ci_crosses_zero": ci_crosses_zero,
            "median_difference": median,
            "median_favors": median_favors,
            "favorable_count_for_c3": int(favorable_a.sum()),
            "favorable_fraction_for_c3": float(favorable_a.mean()),
            "favorable_count_for_gfh": int(unfavorable_b.sum()),
            "tie_count": int(ties.sum()),
            "reviewer_wording": wording,
            "checks": metric_checks,
        })

    direction_errors = len(errors)
    report = {
        "status": "PASS" if direction_errors == 0 else "FAIL",
        "R1_4_DIRECTION_ERRORS": direction_errors,
        "analysis_classification": "REVIEWER_REQUESTED_POST_HOC_AUDIT",
        "source_raw_sha256": raw_sha,
        "results_json_sha256": sha256_file(results_path),
        "direction_checker_sha256": sha256_file(Path(__file__).resolve()),
        "bootstrap_recomputed": {"resamples": N_BOOTSTRAP, "rng": f"numpy.default_rng({RNG_SEED})"},
        "checks": checks,
        "errors": errors,
        "endpoints": audits,
    }
    write_json(output_path, report)
    print(f"R1_4_DIRECTION_ERRORS = {direction_errors}; wrote {output_path}")
    return 0 if direction_errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
