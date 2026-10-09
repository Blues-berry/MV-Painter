#!/usr/bin/env python3
"""Recompute the archived R0/R1 Core-5 stability table from compact CSVs.

This is a CPU-only audit of saved metric rows. It does not run the model or
write outputs. Run from any directory with Python 3.10+:

    python3 1009/evidence/branch_audits/main_backbone_robustness1_20260930/recompute_r0_r1_stability.py
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[3]
R0_DIR = REPO / "1009/evidence/branch_audits/final_evidence_freeze_20261001/inputs"
R1_CSV = PACKAGE / "records/realization1_core5_per_object_metrics.csv"
R1_PROTOCOL = PACKAGE / "records/realization1_protocol_manifest.json"
EXPECTED_TABLE = PACKAGE / "records/R0_R1_DIRECTION_STABILITY.csv"
EXPECTED_SUMMARY = PACKAGE / "records/R0_R1_STABILITY_SUMMARY.json"
EXPECTED_PAIRED = PACKAGE / "records/paired_bootstrap.json"
EXPECTED_AGGREGATE = PACKAGE / "records/aggregate_metrics.csv"

METHODS = (
    "global_fixed_low",
    "global_c3",
    "layer_fixed_mean",
    "layer_lhl",
    "layer_llh",
)
METRICS = (
    "fg_psnr",
    "fg_ssim",
    "fg_lpips",
    "full_psnr",
    "full_ssim",
    "full_lpips",
    "edge_ssim",
)
BETTER = {
    "fg_psnr": 1,
    "fg_ssim": 1,
    "fg_lpips": -1,
    "full_psnr": 1,
    "full_ssim": 1,
    "full_lpips": -1,
    "edge_ssim": 1,
}
COMPARISONS = (
    ("layer_llh", "global_fixed_low"),
    ("layer_llh", "global_c3"),
    ("layer_llh", "layer_fixed_mean"),
    ("layer_llh", "layer_lhl"),
)
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_N = 10_000
EXPECTED_CHECKPOINT = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
EXPECTED_OBJECT_LIST = "a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044"

R0_FILES = {
    "global_fixed_low": R0_DIR / "global_fixed_low/per_object_metrics.csv",
    "global_c3": REPO / "1008/audits/source_evidence/r2/core7/global_c3_per_object_metrics.csv",
    "layer_fixed_mean": R0_DIR / "layer_fixed_mean/per_object_metrics.csv",
    "layer_lhl": R0_DIR / "layer_lhl/per_object_metrics.csv",
    "layer_llh": R0_DIR / "layer_llh/per_object_metrics.csv",
}


def read_metric_rows(path: Path, *, expected_method: str | None = None) -> dict[int, dict[str, str]]:
    if not path.is_file():
        raise RuntimeError(f"missing required metric CSV: {path}")
    rows: dict[int, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            idx = int(row["object_idx"])
            if idx in rows:
                raise RuntimeError(f"duplicate object_idx={idx} in {path}")
            if expected_method is not None and row.get("schedule") not in (None, "", expected_method):
                raise RuntimeError(f"unexpected method {row.get('schedule')} in {path}")
            if row.get("object") != f"obj_{idx + 24:04d}":
                raise RuntimeError(f"object/index mismatch at index {idx} in {path}")
            for metric in METRICS:
                value = float(row[metric])
                if not math.isfinite(value):
                    raise RuntimeError(f"non-finite {metric} at index {idx} in {path}")
            rows[idx] = row
    if set(rows) != set(range(276)):
        raise RuntimeError(f"expected strict-276 indices in {path}; got {len(rows)} rows")
    return rows


def read_r1_rows() -> dict[str, dict[int, dict[str, str]]]:
    if not R1_CSV.is_file():
        raise RuntimeError(f"missing R1 metrics: {R1_CSV}")
    rows = {method: {} for method in METHODS}
    with R1_CSV.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            method = row["schedule"]
            if method not in rows:
                raise RuntimeError(f"unexpected R1 schedule: {method}")
            if int(row["seed_base"]) != 10042:
                raise RuntimeError(f"unexpected R1 seed base for {method}/{row['object_idx']}")
            idx = int(row["object_idx"])
            if idx in rows[method]:
                raise RuntimeError(f"duplicate R1 row: {method}/{idx}")
            rows[method][idx] = row
    for method in METHODS:
        if set(rows[method]) != set(range(276)):
            raise RuntimeError(f"R1 {method}: expected 276 rows, found {len(rows[method])}")
    return rows


def assert_protocol() -> None:
    protocol = json.loads(R1_PROTOCOL.read_text(encoding="utf-8"))
    if protocol.get("checkpoint_sha256") != EXPECTED_CHECKPOINT:
        raise RuntimeError("R1 checkpoint hash does not match the frozen protocol")
    if protocol.get("object_list_sha256") != EXPECTED_OBJECT_LIST:
        raise RuntimeError("R1 object-list hash does not match the frozen protocol")
    if protocol.get("reference_seed_policy", "").find("10042 + object_idx") < 0:
        raise RuntimeError("R1 reference-seed policy is not the expected independent namespace")
    for method, path in R0_FILES.items():
        if not path.is_file():
            raise RuntimeError(f"missing R0 source for {method}: {path}")
        manifest = R0_DIR / method / "protocol_manifest.json"
        if method == "global_c3":
            manifest = R0_DIR / "global_c3/protocol_manifest.json"
        record = json.loads(manifest.read_text(encoding="utf-8"))
        if record.get("checkpoint_sha256") != EXPECTED_CHECKPOINT:
            raise RuntimeError(f"R0 checkpoint mismatch for {method}")
        if record.get("object_list_sha256") != EXPECTED_OBJECT_LIST:
            raise RuntimeError(f"R0 object-list mismatch for {method}")


def paired_delta(
    a: dict[int, dict[str, str]],
    b: dict[int, dict[str, str]],
    metric: str,
    sample_indices: list[list[int]],
) -> dict[str, object]:
    sign = BETTER[metric]
    differences = [sign * (float(a[idx][metric]) - float(b[idx][metric])) for idx in range(276)]
    boots = [sum(differences[index] for index in sample) / 276 for sample in sample_indices]
    boots.sort()
    wins = sum(value > 0 for value in differences)
    losses = sum(value < 0 for value in differences)
    return {
        "mean_diff": sum(differences) / 276,
        "median_diff": statistics.median(differences),
        "ci95": [boots[250], boots[9750]],
        "win_rate": f"{wins}/276",
        "losses": f"{losses}/276",
        "ties": 276 - wins - losses,
        "n": 276,
        "ci_excludes_zero": bool(boots[250] > 0 or boots[9750] < 0),
    }


def classify(r0: dict[str, object], r1: dict[str, object]) -> str:
    same_sign = (float(r0["mean_diff"]) > 0) == (float(r1["mean_diff"]) > 0)
    if not same_sign:
        return "UNSTABLE"
    if bool(r0["ci_excludes_zero"]) and bool(r1["ci_excludes_zero"]):
        return "STABLE_STRONG"
    return "STABLE_DIRECTIONAL"


def main() -> None:
    assert_protocol()
    r0 = {method: read_metric_rows(path, expected_method=method) for method, path in R0_FILES.items()}
    r1 = read_r1_rows()

    r0_ids = {idx: r0["global_fixed_low"][idx]["object"] for idx in range(276)}
    for method in METHODS:
        if any(r1[method][idx]["object"] != r0_ids[idx] for idx in range(276)):
            raise RuntimeError(f"R0/R1 object mapping differs for {method}")

    paired: dict[str, dict[str, dict[str, dict[str, object]]]] = {"R0": {}, "R1": {}}
    table_rows: dict[tuple[str, str], dict[str, str]] = {}
    with EXPECTED_TABLE.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            table_rows[(row["comparison"], row["metric"])] = row
    classifications: dict[str, dict[str, str]] = {}
    table_checks = 0
    for left, right in COMPARISONS:
        comparison = f"{left}_minus_{right}"
        paired["R0"][comparison] = {}
        paired["R1"][comparison] = {}
        classifications[comparison] = {}
        for metric in METRICS:
            rng = random.Random(BOOTSTRAP_SEED)
            # The source analyzer restarts the same RNG for R0 and R1. Build
            # that identical sample sequence once and apply it to both rows.
            samples = [
                [rng.randrange(276) for _ in range(276)]
                for _ in range(BOOTSTRAP_N)
            ]
            p0 = paired_delta(r0[left], r0[right], metric, samples)
            p1 = paired_delta(r1[left], r1[right], metric, samples)
            paired["R0"][comparison][metric] = p0
            paired["R1"][comparison][metric] = p1
            label = classify(p0, p1)
            classifications[comparison][metric] = label

            expected = table_rows.get((comparison, metric))
            if expected is None:
                raise RuntimeError(f"missing archived stability row: {comparison}/{metric}")
            ci0 = f"[{p0['ci95'][0]:.6f},{p0['ci95'][1]:.6f}]"
            ci1 = f"[{p1['ci95'][0]:.6f},{p1['ci95'][1]:.6f}]"
            checks = {
                "r0_mean_delta": str(round(float(p0["mean_diff"]), 6)),
                "r0_ci95": ci0,
                "r0_win_rate": p0["win_rate"],
                "r1_mean_delta": str(round(float(p1["mean_diff"]), 6)),
                "r1_ci95": ci1,
                "r1_win_rate": p1["win_rate"],
                "ci_excludes_zero_R0": str(p0["ci_excludes_zero"]),
                "ci_excludes_zero_R1": str(p1["ci_excludes_zero"]),
                "classification": label,
            }
            for field, value in checks.items():
                if expected[field].lower() != value.lower():
                    raise RuntimeError(
                        f"archived table mismatch {comparison}/{metric}/{field}: "
                        f"computed={value!r}, archived={expected[field]!r}"
                    )
            table_checks += 1

    summary = json.loads(EXPECTED_SUMMARY.read_text(encoding="utf-8"))
    counts = {
        label: sum(value == label for cells in classifications.values() for value in cells.values())
        for label in ("STABLE_STRONG", "STABLE_DIRECTIONAL", "UNSTABLE")
    }
    if counts != summary["classification_counts"]:
        raise RuntimeError(f"classification-count mismatch: {counts}")

    def ranking(rows: dict[str, dict[int, dict[str, str]]]) -> dict[str, list[str]]:
        return {
            metric: sorted(
                METHODS,
                key=lambda method: -BETTER[metric]
                * statistics.mean(float(rows[method][idx][metric]) for idx in range(276)),
            )
            for metric in METRICS
        }

    ranks0 = ranking(r0)
    ranks1 = ranking(r1)
    if ranks0 != summary["ranking_R0"] or ranks1 != summary["ranking_R1"] or ranks0 != ranks1:
        raise RuntimeError("R0/R1 rankings differ from the archived summary")

    aggregate_rows = {}
    with EXPECTED_AGGREGATE.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            aggregate_rows[(row["realization"], row["method"], row["metric"])] = float(row["mean"])
    aggregate_checks = 0
    for realization, rows in (("R0", r0), ("R1", r1)):
        for method in METHODS:
            for metric in METRICS:
                actual = statistics.mean(float(rows[method][idx][metric]) for idx in range(276))
                expected = aggregate_rows[(realization, method, metric)]
                if abs(actual - expected) > 1e-12:
                    raise RuntimeError(f"aggregate mismatch: {realization}/{method}/{metric}")
                aggregate_checks += 1

    archived_paired = json.loads(EXPECTED_PAIRED.read_text(encoding="utf-8"))
    paired_checks = 0
    for realization in ("R0", "R1"):
        for comparison, metrics in paired[realization].items():
            for metric, actual in metrics.items():
                expected = archived_paired[realization][comparison][metric]
                for field in ("mean_diff", "median_diff", "ci95"):
                    actual_values = actual[field] if isinstance(actual[field], list) else [actual[field]]
                    expected_values = expected[field] if isinstance(expected[field], list) else [expected[field]]
                    if len(actual_values) != len(expected_values) or any(
                        abs(float(a) - float(b)) > 1e-12 for a, b in zip(actual_values, expected_values)
                    ):
                        raise RuntimeError(f"paired-output mismatch: {realization}/{comparison}/{metric}/{field}")
                paired_checks += 1

    print("PASS: R1 rows=1,380 (276 x 5); all methods share the same 276 object IDs")
    print(f"PASS: archived 28-cell table exactly matches recomputation ({table_checks}/28)")
    print(f"PASS: aggregate means={aggregate_checks}/70; paired result payloads={paired_checks}/56")
    print(f"PASS: rankings identical across R0/R1 on all {len(METRICS)} metrics")
    print(f"Classification counts: {counts}")
    primary = paired["R1"]["layer_llh_minus_global_fixed_low"]["fg_psnr"]
    print(
        "R1 primary LLH-GFL FG-PSNR: "
        f"{float(primary['mean_diff']):+.6f} dB, 95% CI "
        f"[{float(primary['ci95'][0]):+.6f}, {float(primary['ci95'][1]):+.6f}], "
        f"wins {primary['win_rate']}"
    )


if __name__ == "__main__":
    main()
