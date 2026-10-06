#!/usr/bin/env python3
"""Prospective nine-condition analysis; fails closed without a complete D gate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import ttest_1samp

CONDITIONS = ("no_adapter", "native_gfl", "native_gfh", "native_gc3", "gen_linear",
              "cap_calibrated", "fixed_scale_ablation", "pooled_reference_ablation", "static_target_ablation")
ENDPOINTS = ("fg_psnr", "fg_lpips")
SECONDARY = ("fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim")
INPUT_FIELDS = tuple(f"input_{name}_sha256" for name in
                     ("cond", "target", "normal", "depth", "global_embeds", "init_latent"))
FAMILIES = {"primary": ["native_gc3"],
            "context_baselines": ["native_gfl", "native_gfh", "no_adapter", "gen_linear"],
            "ablations": ["fixed_scale_ablation", "pooled_reference_ablation", "static_target_ablation"]}


def holm(pvalues):
    values = np.asarray(pvalues, dtype=float)
    if not np.isfinite(values).all() or np.any((values < 0) | (values > 1)):
        raise ValueError("invalid p values")
    order = np.argsort(values, kind="stable")
    adjusted = np.empty(len(values))
    adjusted[order] = np.minimum(1, np.maximum.accumulate(values[order] * np.arange(len(values), 0, -1)))
    return adjusted.tolist()


def paired_table(rows, ordered_uids, seed=42):
    expected = {(uid, condition) for uid in ordered_uids for condition in CONDITIONS}
    if len(ordered_uids) != len(set(ordered_uids)):
        raise ValueError("duplicate cohort UID")
    indexed, identity = {}, {}
    for row in rows:
        if int(row["latent_seed"]) != seed:
            raise ValueError("main table must contain one latent seed; analyze sensitivity separately")
        key = row["uid"], row["condition"]
        if key in indexed or key not in expected:
            raise ValueError("duplicate or unexpected object-condition row")
        metrics = np.asarray([float(row[m]) for m in (*ENDPOINTS, *SECONDARY)])
        if not np.isfinite(metrics).all():
            raise ValueError("missing/nonfinite metric")
        hashes = tuple((key, row.get(key, "")) for key in INPUT_FIELDS)
        if any(len(v) != 64 for _, v in hashes):
            raise ValueError("missing complete shared input/latent hash chain")
        if row["uid"] in identity and identity[row["uid"]] != hashes:
            raise ValueError("shared input/latent identity differs")
        identity[row["uid"]] = hashes
        indexed[key] = row
    if set(indexed) != expected:
        raise ValueError("incomplete expected object-condition grid; no pairwise deletion")
    return indexed


def estimate(delta, rng):
    delta = np.asarray(delta, dtype=float)
    if len(delta) < 2 or not np.isfinite(delta).all():
        raise ValueError("at least two finite object-level deltas required")
    means = np.concatenate([delta[rng.integers(0, len(delta), (1000, len(delta)))].mean(axis=1) for _ in range(10)])
    if np.std(delta) == 0:
        p = 1.0 if delta[0] == 0 else 0.0
    else:
        p = float(ttest_1samp(delta, 0).pvalue)
    return {"n_objects": len(delta), "mean": float(delta.mean()), "median": float(np.median(delta)),
            "bootstrap_ci95_nominal": np.quantile(means, [.025, .975]).tolist(),
            "paired_t_p_raw": p, "p_underflow_or_constant_nonzero": p == 0}


def analyze(indexed, uids):
    rng = np.random.default_rng(20261006)
    results, object_deltas = {}, []
    for family, comparators in FAMILIES.items():
        tests = []
        for comparator in comparators:
            for metric in ENDPOINTS:
                delta = [float(indexed[uid, "cap_calibrated"][metric])-float(indexed[uid, comparator][metric]) for uid in uids]
                test = {"comparator": comparator, "endpoint": metric, **estimate(delta, rng)}
                expected = 1 if metric == "fg_psnr" else -1
                test["favorable_object_fraction"] = float(np.mean(np.asarray(delta)*expected > 0))
                test["expected_direction"] = test["mean"]*expected > 0
                tests.append(test)
                object_deltas.extend({"uid": uid, "comparator": comparator, "endpoint": metric, "delta": float(d)} for uid, d in zip(uids, delta))
        for test, adjusted in zip(tests, holm([t["paired_t_p_raw"] for t in tests])):
            test["holm_p"] = adjusted
        results[family] = tests
    secondary = {}
    for metric in SECONDARY:
        delta = [float(indexed[uid, "cap_calibrated"][metric])-float(indexed[uid, "native_gc3"][metric]) for uid in uids]
        summary = estimate(delta, rng)
        summary.pop("paired_t_p_raw")
        summary.pop("p_underflow_or_constant_nonzero")
        summary["descriptive_only"] = True
        secondary[metric] = summary
    condition_means = {c: {m: float(np.mean([float(indexed[uid, c][m]) for uid in uids]))
                          for m in (*ENDPOINTS, *SECONDARY)} for c in CONDITIONS}
    return {"inferential_unit": "object, one primary-seed paired delta per UID",
            "families": results, "joint_primary_improvement": all(t["holm_p"] < .05 and t["expected_direction"] for t in results["primary"]),
            "intervals": "nominal object-bootstrap, not simultaneous or equivalence intervals",
            "object_deltas": object_deltas, "secondary_descriptive_new_minus_c3": secondary,
            "all_condition_core7_means": condition_means}


def analyze_sensitivity(rows, uids):
    seeds = (42, 43, 44)
    if {int(r["latent_seed"]) for r in rows} != set(seeds):
        raise ValueError("sensitivity requires exactly the three fixed seeds")
    by_seed = {seed: paired_table([r for r in rows if int(r["latent_seed"]) == seed], uids, seed) for seed in seeds}
    for uid in uids:
        # View/reference sampling must stay fixed when only latent seed changes.
        signatures = [tuple(by_seed[seed][uid, "native_gc3"][field]
                      for field in INPUT_FIELDS if "init_latent" not in field) for seed in seeds]
        if len(set(signatures)) != 1:
            raise ValueError("seed sensitivity changed object input/reference/view identity")
    rng = np.random.default_rng(20261006)
    families = {}
    for family, comparators in FAMILIES.items():
        tests = []
        for comparator in comparators:
            for metric in ENDPOINTS:
                new = np.array([[float(by_seed[seed][uid, "cap_calibrated"][metric]) for seed in seeds] for uid in uids])
                base = np.array([[float(by_seed[seed][uid, comparator][metric]) for seed in seeds] for uid in uids])
                contrasts = new-base
                averaged = contrasts.mean(axis=1)
                reference_range = float(np.median(np.concatenate([np.ptp(new, axis=1), np.ptp(base, axis=1)])))
                test = {"comparator": comparator, "endpoint": metric, **estimate(averaged, rng),
                        "fixed_seed_means": {str(s): float(contrasts[:, j].mean()) for j, s in enumerate(seeds)},
                        "median_same_condition_seed_range": reference_range,
                        "abs_effect_over_median_same_condition_seed_range": abs(float(averaged.mean()))/reference_range if reference_range else None,
                        "median_paired_contrast_seed_range": float(np.median(np.ptp(contrasts, axis=1))),
                        "expected_direction_in_all_seeds_fraction": float(np.mean(np.all(contrasts*(1 if metric == "fg_psnr" else -1)>0, axis=1)))}
                tests.append(test)
        for test, p in zip(tests, holm([t["paired_t_p_raw"] for t in tests])):
            test["holm_p"] = p
        families[family] = tests
    return {"primary_confirmatory": False, "n_objects": len(uids), "fixed_seeds": list(seeds),
            "inferential_unit": "object after averaging fixed seed deltas; not object x seed",
            "scope": "preselected confirmation subset, conditional on three fixed seeds; not a seed-population CI or replacement primary confirmation",
            "noise_ratio": "descriptive only; not a significance test against realization noise",
            "families": families}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--sensitivity", action="store_true")
    args = parser.parse_args()
    data = args.directory
    lock = json.loads((data / "FRESH_D_METHOD_LOCK.json").read_text())
    gate = json.loads((data / "FRESH_D_INTEGRITY_GATE.json").read_text())
    table = data / ("fresh_d_sensitivity_metrics.csv" if args.sensitivity else "fresh_d_primary_metrics.csv")
    digest = hashlib.sha256(table.read_bytes()).hexdigest()
    table_key = "sensitivity_table_sha256" if args.sensitivity else "primary_table_sha256"
    if gate.get("status") != "PASS" or gate.get(table_key) != digest:
        raise RuntimeError("complete integrity gate and exact reconstructed table are required")
    if gate.get("method_lock_sha256") != hashlib.sha256((data / "FRESH_D_METHOD_LOCK.json").read_bytes()).hexdigest():
        raise RuntimeError("method lock identity mismatch")
    if lock.get("conditions") != list(CONDITIONS) or lock.get("novelty_review_status") != "QUALIFIED_FOR_INDEPENDENT_TEST":
        raise RuntimeError("nine-condition prospective lock and contribution review are required")
    n_objects = len(lock.get("ordered_uids", []))
    if not 300 <= n_objects <= 600 or n_objects != lock.get("planned_n"):
        raise RuntimeError("confirmation must match the pre-output planned N within 300–600")
    if lock.get("analysis_script_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise RuntimeError("analysis code changed after pre-output lock")
    with table.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if args.sensitivity:
        subset = lock.get("sensitivity_uids", [])
        if len(subset) != 48 or len(set(subset)) != 48 or not set(subset).issubset(lock["ordered_uids"]):
            raise RuntimeError("48 sensitivity UIDs must be frozen within the confirmation cohort")
        result = analyze_sensitivity(rows, subset)
    else:
        result = analyze(paired_table(rows, lock["ordered_uids"]), lock["ordered_uids"])
    result[table_key] = digest
    output = "FRESH_D_SENSITIVITY_ANALYSIS.json" if args.sensitivity else "FRESH_D_ANALYSIS.json"
    (data / output).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k != "object_deltas"}, indent=2))


if __name__ == "__main__":
    main()
