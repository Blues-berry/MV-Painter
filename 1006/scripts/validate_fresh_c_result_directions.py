#!/usr/bin/env python3
"""Independently audit Fresh C effect signs, intervals, favorable fractions and Holm families."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import ttest_rel

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
PRIMARY = DATA / "runs/c3_confirmation/per_object_metrics.csv"
ADDENDUM = DATA / "runs/revision_era_addendum/per_object_metrics.csv"
PRIMARY_ANALYSIS = DATA / "fresh_c_c3_minus_gfl_analysis.json"
ADDENDUM_ANALYSIS = DATA / "FRESH_C_ADDENDUM_ANALYSIS.json"
OUT = DATA / "FRESH_C_RESULT_DIRECTION_AUDIT.json"
METRICS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")
HIGHER = {"fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim"}
FAMILY_SIZES = {
    "single registered secondary family": 6,
    "six primary endpoint-contrast tests": 6,
    "15 secondary Core-7 endpoint-contrast tests": 15,
}
CONTRASTS = {
    "C3-GFL": ("native_gc3", "native_gfl"),
    "LLH-C3": ("layer_llh", "native_gc3"),
    "LLH-linear": ("layer_llh", "gen_linear"),
    "C3-linear": ("native_gc3", "gen_linear"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, *, p_value: bool = False) -> bool:
    if p_value:
        return actual == expected or abs(actual - expected) <= max(abs(expected) * 1e-10, 1e-300)
    return bool(np.isclose(actual, expected, rtol=1e-10, atol=1e-12))


def holm(values: list[float]) -> list[float]:
    order = np.argsort(values)
    adjusted = np.empty(len(values), dtype=np.float64)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def bootstrap_ci(delta: np.ndarray, seed: int) -> list[float]:
    """Match the locked 10,000-draw, 500-draw-chunk percentile bootstrap."""
    rng = np.random.default_rng(seed)
    means = np.empty(10_000, dtype=np.float64)
    for start in range(0, len(means), 500):
        stop = min(start + 500, len(means))
        indices = rng.integers(0, len(delta), size=(stop - start, len(delta)))
        means[start:stop] = delta[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975], method="linear")
    return [float(low), float(high)]


def paired_delta(by_key: dict[tuple[str, str], dict[str, str]], uids: list[str],
                 contrast: str, metric: str) -> tuple[np.ndarray, float]:
    left, right = CONTRASTS[contrast]
    a = np.asarray([float(by_key[(uid, left)][metric]) for uid in uids], dtype=np.float64)
    b = np.asarray([float(by_key[(uid, right)][metric]) for uid in uids], dtype=np.float64)
    return a - b, float(ttest_rel(a, b, alternative="two-sided", nan_policy="raise").pvalue)


def audit_row(contrast: str, metric: str, delta: np.ndarray, p_raw: float,
              reported: dict[str, object], *, family: str, adjusted_p: float | None,
              direction_field: str, favorable_field: str, seed: int,
              errors: list[str]) -> dict[str, object]:
    higher = metric in HIGHER
    expected_direction = "higher" if higher else "lower"
    favorable = float(np.mean(delta > 0 if higher else delta < 0))
    ci = bootstrap_ci(delta, seed)
    ci_reported = [float(v) for v in reported["bootstrap_ci95"]]
    mean = float(delta.mean())
    median = float(np.median(delta))
    p_reported = float(reported["paired_t_p_raw"])
    fraction_reported = float(reported[favorable_field])
    direction_reported = str(reported[direction_field])
    item: dict[str, object] = {
        "contrast": contrast,
        "metric": metric,
        "n": len(delta),
        "mean_delta_recomputed": mean,
        "mean_delta_reported": float(reported["mean"]),
        "median_delta_recomputed": median,
        "median_delta_reported": float(reported["median"]),
        "ci95_recomputed": ci,
        "ci95_reported": ci_reported,
        "p_raw_recomputed": p_raw,
        "p_raw_reported": p_reported,
        "p_holm_recomputed": adjusted_p,
        "p_holm_reported": reported.get("holm_adjusted_p"),
        "favorable_object_fraction_recomputed": favorable,
        "favorable_object_fraction_reported": fraction_reported,
        "expected_favorable_direction": expected_direction,
        "reported_favorable_direction": direction_reported,
        "ci_directional_support_recomputed": bool(ci[0] > 0 if higher else ci[1] < 0),
        "multiplicity_family": family,
    }
    for name, actual, expected in (
        ("mean", mean, float(reported["mean"])),
        ("median", median, float(reported["median"])),
        ("favorable-object fraction", favorable, fraction_reported),
    ):
        if not close(actual, expected):
            errors.append(f"{contrast}/{metric}: {name} mismatch")
    if any(not close(actual, expected) for actual, expected in zip(ci, ci_reported)):
        errors.append(f"{contrast}/{metric}: bootstrap CI mismatch")
    if not close(p_raw, p_reported, p_value=True):
        errors.append(f"{contrast}/{metric}: raw paired p mismatch")
    if direction_reported != expected_direction:
        errors.append(f"{contrast}/{metric}: favorable direction label mismatch")
    if adjusted_p is not None:
        p_holm_reported = reported.get("holm_adjusted_p")
        if p_holm_reported is None or not close(adjusted_p, float(p_holm_reported), p_value=True):
            errors.append(f"{contrast}/{metric}: Holm p mismatch")
    if contrast == "LLH-linear" and metric in {"fg_lpips", "full_lpips"}:
        item["positive_delta_favors_by_metric_convention"] = "generic linear"
        item["lpips_direction_rule_applied"] = True
    else:
        item["lpips_direction_rule_applied"] = metric.endswith("lpips")
    return item


def main() -> None:
    for gate in (DATA / "FRESH_C_INTEGRITY_GATE.json", DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"):
        if not gate.is_file() or json.loads(gate.read_text()).get("status") != "PASS":
            raise RuntimeError(f"refusing direction audit before PASS integrity gate: {gate}")
    primary_rows, addendum_rows = load(PRIMARY), load(ADDENDUM)
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in primary_rows + addendum_rows:
        key = (row["object_uid"], row["condition"])
        if key in by_key:
            raise RuntimeError(f"duplicate condition/UID row across Fresh C namespaces: {key}")
        by_key[key] = row
    uids = sorted({uid for uid, _ in by_key})
    primary = json.loads(PRIMARY_ANALYSIS.read_text())
    addendum = json.loads(ADDENDUM_ANALYSIS.read_text())
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    # Original primary run: one unadjusted FG-PSNR primary and one six-test secondary family.
    primary_raw: dict[str, tuple[np.ndarray, float]] = {}
    for metric in METRICS:
        delta, p_raw = paired_delta(by_key, uids, "C3-GFL", metric)
        primary_raw[metric] = (delta, p_raw)
    secondary_metrics = [m for m in METRICS if m != "fg_psnr"]
    primary_adjusted = dict(zip(secondary_metrics, holm([primary_raw[m][1] for m in secondary_metrics])))
    for metric in METRICS:
        reported = primary["tests"][metric]
        family = ("single predeclared primary endpoint; no adjustment" if metric == "fg_psnr"
                  else "single registered secondary family")
        checks.append(audit_row(
            "C3-GFL", metric, primary_raw[metric][0], primary_raw[metric][1], reported,
            family=family, adjusted_p=None if metric == "fg_psnr" else primary_adjusted[metric],
            direction_field="favorable_direction", favorable_field="favorable_object_fraction",
            seed=int(reported["bootstrap_seed"]), errors=errors))

    # Addendum: recompute all 21 named contrasts, then each frozen Holm family.
    raw: dict[tuple[str, str], tuple[np.ndarray, float]] = {}
    for contrast in ("LLH-C3", "LLH-linear", "C3-linear"):
        for metric in METRICS:
            raw[(contrast, metric)] = paired_delta(by_key, uids, contrast, metric)
    reported_tests = {(r["contrast"], r["metric"]): r for r in addendum["tests"]}
    if len(reported_tests) != 21:
        errors.append(f"addendum contains {len(reported_tests)} tests; expected 21")
    adjusted_by_key: dict[tuple[str, str], float] = {}
    for family_name, expected_size in FAMILY_SIZES.items():
        if family_name == "single registered secondary family":
            continue
        keys = [key for key, row in reported_tests.items() if row["multiplicity_family"] == family_name]
        if len(keys) != expected_size:
            errors.append(f"{family_name} has {len(keys)} tests, expected {expected_size}")
            continue
        values = holm([raw[key][1] for key in keys])
        adjusted_by_key.update(zip(keys, values))
    for key, (delta, p_raw) in raw.items():
        reported = reported_tests.get(key)
        if reported is None:
            errors.append(f"missing addendum test {key}")
            continue
        family = str(reported["multiplicity_family"])
        checks.append(audit_row(
            key[0], key[1], delta, p_raw, reported, family=family,
            adjusted_p=adjusted_by_key.get(key), direction_field="favorable_direction_for_a",
            favorable_field="favorable_object_fraction_for_a",
            seed=int(reported["bootstrap_seed"]), errors=errors))

    if len(checks) != 28:
        errors.append(f"independent check count {len(checks)}; expected 28")
    result = {
        "status": "PASS" if not errors else "FAIL",
        "n_objects": len(uids),
        "row_sources": {
            "primary_csv_sha256": sha256(PRIMARY),
            "addendum_csv_sha256": sha256(ADDENDUM),
            "primary_analysis_sha256": sha256(PRIMARY_ANALYSIS),
            "addendum_analysis_sha256": sha256(ADDENDUM_ANALYSIS),
        },
        "delta_convention": "condition A minus condition B",
        "lpips_convention": "lower is better; positive LLH−linear therefore favors generic linear, negative favors LLH",
        "ci_method": "10,000 paired object-bootstrap draws; seed recorded in each frozen analysis; percentile 95% CI",
        "checks_cover": ["mean", "median", "95% object-bootstrap CI", "paired p", "Holm p", "favorable-object fraction", "direction label", "multiplicity family"],
        "sign_direction_error": "0" if not errors else str(len(errors)),
        "sign_direction_error_count": len(errors),
        "independent_checks": checks,
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(checks),
                      "SIGN_DIRECTION_ERROR": result["sign_direction_error"],
                      "errors": errors, "output": str(OUT)}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
