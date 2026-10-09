#!/usr/bin/env python3
"""Reaggregate bundled paired inputs and compare them with the authority table."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import ttest_1samp


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "1006/evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv"
BOOTSTRAPS = 10_000
METRIC_COLUMNS = (
    "fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim", "full_psnr", "full_lpips", "full_ssim"
)
HIGHER_IS_BETTER = {"fg_psnr", "fg_ssim", "edge_ssim", "full_psnr", "full_ssim"}
ADDENDUM_CONTRASTS = {
    ("layer_llh", "native_gc3"): "LLH-C3",
    ("layer_llh", "gen_linear"): "LLH-linear",
    ("native_gc3", "gen_linear"): "C3-linear",
}
RAW_CONDITIONS = {
    "C3": "native_gc3",
    "C3 (native_gc3)": "native_gc3",
    "GFL": "native_gfl",
    "GFH": "native_gfh",
    "GFH (native_gfh)": "native_gfh",
    "native_gc3": "native_gc3",
    "native_gfh": "native_gfh",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def float_or_none(value: str) -> float | None:
    return float(value) if value not in (None, "") else None


def bootstrap_ci(delta: np.ndarray, seed: int, batched: bool, dtype: Any = None) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    if batched:
        means = np.empty(BOOTSTRAPS, dtype=np.float64)
        for start in range(0, BOOTSTRAPS, 500):
            stop = min(start + 500, BOOTSTRAPS)
            indices = rng.integers(0, len(delta), size=(stop - start, len(delta)))
            means[start:stop] = delta[indices].mean(axis=1)
    else:
        if dtype is None:
            indices = rng.integers(0, len(delta), size=(BOOTSTRAPS, len(delta)))
        else:
            indices = rng.integers(0, len(delta), size=(BOOTSTRAPS, len(delta)), dtype=dtype)
        means = delta[indices].mean(axis=1)
    lower, upper = np.percentile(means, [2.5, 97.5])
    return float(lower), float(upper)


def holm(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=np.float64)
    running = 0.0
    size = len(p_values)
    for rank, index in enumerate(order):
        running = max(running, (size - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def raw_paired_deltas(rows: list[dict[str, str]], uid_key: str, condition_a: str, condition_b: str,
                      metric: str) -> np.ndarray:
    by_condition: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        condition = row.get("condition", "")
        uid = row.get(uid_key, "")
        if uid and condition in {condition_a, condition_b}:
            if uid in by_condition[condition]:
                raise ValueError(f"duplicate {condition}/{uid} row")
            by_condition[condition][uid] = row
    a, b = by_condition[condition_a], by_condition[condition_b]
    if len(a) != len(b) or not a or set(a) != set(b):
        raise ValueError(f"unpaired rows for {condition_a} versus {condition_b}: {len(a)} vs {len(b)}")
    ordered_uids = sorted(a)
    for uid in ordered_uids:
        if a[uid].get("object_idx") != b[uid].get("object_idx"):
            raise ValueError(f"object index mismatch for {uid}")
        if a[uid].get("seed_base") != b[uid].get("seed_base"):
            raise ValueError(f"generation seed mismatch for {uid}")
    return np.asarray([float(a[uid][metric]) - float(b[uid][metric]) for uid in ordered_uids], dtype=np.float64)


def delta_for_row(row: dict[str, str], rows_by_source: dict[str, list[dict[str, str]]]) -> tuple[np.ndarray, int, bool]:
    source = Path(row["source_raw_file"]).name
    metric = row["metric"].lower().replace("-", "_")
    if metric not in METRIC_COLUMNS:
        raise ValueError(f"unsupported authority metric {row['metric']}")
    if source == "fresh_c_c3_minus_gfl_object_deltas.csv":
        rows = rows_by_source[source]
        if len(rows) != 300 or len({r["object_uid"] for r in rows}) != 300:
            raise ValueError("Fresh C primary delta file must contain 300 unique paired objects")
        return np.asarray([float(r[metric]) for r in rows], dtype=np.float64), 20261006, True
    if source == "fresh_c_addendum_object_deltas.csv":
        rows = rows_by_source[source]
        condition_pair = (row["condition_A"], row["condition_B"])
        try:
            contrast = ADDENDUM_CONTRASTS[condition_pair]
        except KeyError as exc:
            raise ValueError(f"unknown addendum contrast {condition_pair}") from exc
        selected = [r for r in rows if r["contrast"] == contrast]
        if len(selected) != 300 or len({r["object_uid"] for r in selected}) != 300:
            raise ValueError(f"Fresh C addendum {contrast} must contain 300 unique objects")
        return np.asarray([float(r[metric]) for r in selected], dtype=np.float64), 20261007, True
    if source in {"fresh_c_c3_confirmation_per_object_metrics.csv", "fresh_b_per_object_metrics.csv"}:
        cohort = row["cohort"]
        condition_a = "native_gc3"
        condition_b = "native_gfh"
        expected_n = 300 if cohort == "FROZEN_FRESH_C" else 150
        rows = rows_by_source[source]
        if row["condition_A"] not in RAW_CONDITIONS or row["condition_B"] not in RAW_CONDITIONS:
            raise ValueError(f"unknown raw condition names: {row['condition_A']}/{row['condition_B']}")
        condition_a = RAW_CONDITIONS[row["condition_A"]]
        condition_b = RAW_CONDITIONS[row["condition_B"]]
        delta = raw_paired_deltas(rows, "object_uid", condition_a, condition_b, metric)
        if len(delta) != expected_n:
            raise ValueError(f"{cohort} expected N={expected_n}, found N={len(delta)}")
        return delta, 20261002, False
    raise ValueError(f"unsupported bundled authority input: {row['source_raw_file']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "1006/evidence/audits/BUNDLED_NUMERICAL_AUTHORITY_REAGGREGATION_20261007.json",
    )
    args = parser.parse_args()

    authority_rows = read_csv(AUTHORITY)
    input_names = {
        "1006/review/numerical_inputs/fresh_c_c3_minus_gfl_object_deltas.csv",
        "1006/review/numerical_inputs/fresh_c_addendum_object_deltas.csv",
        "1006/review/numerical_inputs/fresh_c_c3_confirmation_per_object_metrics.csv",
        "1006/review/numerical_inputs/fresh_b_per_object_metrics.csv",
    }
    rows_by_source: dict[str, list[dict[str, str]]] = {}
    input_hashes: dict[str, str] = {}
    for relative in sorted(input_names):
        path = ROOT / relative
        expected_hashes = {r["source_hash"] for r in authority_rows if r["source_raw_file"] == relative}
        if not expected_hashes or len(expected_hashes) != 1:
            raise ValueError(f"authority table has no unique hash for {relative}")
        actual = sha256(path)
        if actual not in expected_hashes:
            raise ValueError(f"source hash mismatch for {relative}: {actual}")
        input_hashes[relative] = actual
        key = Path(relative).name
        rows_by_source[key] = read_csv(path)

    selected = [r for r in authority_rows if r["source_raw_file"] in input_names]
    analysis_hashes: dict[str, str] = {}
    output_hashes: dict[str, str] = {}
    for row in selected:
        for field, digest_field, record in (
            ("source_analysis_file", "source_analysis_sha256", analysis_hashes),
            ("source_output_file", "source_output_sha256", output_hashes),
        ):
            relative = row.get(field, "")
            expected = row.get(digest_field, "")
            if not relative or not expected:
                continue
            path = ROOT / relative
            observed = sha256(path)
            if observed != expected:
                raise ValueError(f"{field} hash mismatch for {row['claim_id']}: {observed}")
            record[relative] = observed
        relative = row.get("source_output_file", "")
        expected = row.get("source_output_json_sha256", "")
        if relative and expected:
            json_path = ROOT / relative.replace(".csv", ".json")
            if json_path.is_file():
                observed = sha256(json_path)
                if observed != expected:
                    raise ValueError(f"source output JSON hash mismatch for {row['claim_id']}: {observed}")
                output_hashes[str(json_path.relative_to(ROOT))] = observed

    computed: list[dict[str, Any]] = []
    groups: dict[str, list[int]] = defaultdict(list)
    for row in selected:
        delta, seed, batched = delta_for_row(row, rows_by_source)
        mean = float(delta.mean())
        median = float(np.median(delta))
        index_dtype = np.int32 if row["cohort"] == "FROZEN_FRESH_C" else None
        lower, upper = bootstrap_ci(delta, seed, batched, index_dtype)
        direction = "lower" if row["metric"].lower().endswith("lpips") else "higher"
        favorable = delta < 0 if direction == "lower" else delta > 0
        result: dict[str, Any] = {
            "claim_id": row["claim_id"],
            "effect": mean,
            "median": median,
            "CI_lower": lower,
            "CI_upper": upper,
            "favorable_fraction": float(favorable.mean()),
            "N": len(delta),
            "bootstrap_seed": seed,
            "p_raw": float(ttest_1samp(delta, popmean=0.0).pvalue)
            if row["p_raw"] else None,
            "p_adjusted": None,
        }
        computed.append(result)
        if row["p_adjusted"]:
            groups[row["correction_family"]].append(len(computed) - 1)

    for indices in groups.values():
        values = [computed[index]["p_raw"] for index in indices]
        adjusted = holm(values)
        for index, p_value in zip(indices, adjusted):
            computed[index]["p_adjusted"] = p_value

    checks = []
    numeric_fields = ("effect", "median", "CI_lower", "CI_upper", "favorable_fraction", "p_raw", "p_adjusted")
    max_differences = {field: 0.0 for field in numeric_fields}
    tolerance = 2e-10
    for expected, observed in zip(selected, computed):
        differences = {}
        for field in numeric_fields:
            reference = float_or_none(expected[field])
            actual = observed[field]
            if reference is None:
                continue
            if actual is None:
                raise ValueError(f"missing computed {field} for {expected['claim_id']}")
            difference = abs(reference - actual)
            differences[field] = difference
            max_differences[field] = max(max_differences[field], difference)
            if difference > tolerance:
                raise ValueError(
                    f"{expected['claim_id']} {field} differs by {difference:.3g}: "
                    f"authority={reference:.17g}, recomputed={actual:.17g}"
                )
        if expected["favorable_count"]:
            count = int(round(observed["favorable_fraction"] * observed["N"]))
            if count != int(expected["favorable_count"]):
                raise ValueError(f"favorable-object count mismatch for {expected['claim_id']}")
        checks.append({"claim_id": expected["claim_id"], "status": "PASS", "max_abs_difference": differences})

    output = {
        "status": "PASS",
        "scope": "Reaggregation of paired object-level numerical inputs; does not rebuild rendered outputs or rerun generation.",
        "authority_csv": str(AUTHORITY.relative_to(ROOT)),
        "script_sha256": sha256(Path(__file__).resolve()),
        "input_sha256": input_hashes,
        "analysis_output_sha256": {
            "analysis": analysis_hashes,
            "outputs": output_hashes,
        },
        "claim_count": len(checks),
        "tolerance": tolerance,
        "max_abs_differences": max_differences,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: reaggregated {len(checks)} authority rows from four hash-pinned inputs")
    print(f"output={args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}")
    for field, difference in max_differences.items():
        if difference:
            print(f"max_abs_difference[{field}]={difference:.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
