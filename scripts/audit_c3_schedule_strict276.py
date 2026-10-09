#!/usr/bin/env python3
"""Audit the targeted strict-276 schedule-only follow-up."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


SEED = 20260929
RESAMPLES = 10_000
METHODS = ("fixed_low", "C3_TCAS", "HLL_eq", "LLH_eq", "LLH_ramp_eq", "LLH_cosine_eq")
NEW = ("LLH_ramp_eq", "LLH_cosine_eq")
METRICS = (
    ("fg_lpips", "lower"),
    ("psnr", "higher"),
    ("fg_ssim", "higher"),
    ("edge_ssim", "higher"),
    ("fg_mae", "lower"),
    ("fg_lap_var", "diagnostic"),
    ("fg_lap_corr", "diagnostic"),
    ("excess_hf_mean", "diagnostic"),
)


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def bootstrap(values: np.ndarray) -> list[float]:
    rng = np.random.default_rng(SEED)
    index = rng.integers(0, len(values), size=(RESAMPLES, len(values)))
    means = values[index].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def paired(left: dict[str, dict], right: dict[str, dict], metric: str, direction: str) -> dict:
    objects = sorted(set(left) & set(right))
    delta = np.asarray([float(left[obj][metric]) - float(right[obj][metric]) for obj in objects], dtype=np.float64)
    favorable = -delta if direction == "lower" else delta
    return {
        "n": len(objects),
        "mean_raw_delta_left_minus_right": float(delta.mean()),
        "ci95_raw_delta": bootstrap(delta),
        "direction": direction,
        "mean_delta_favoring_left": float(favorable.mean()),
        "ci95_delta_favoring_left": bootstrap(favorable),
        "wins_favoring_left": int(np.sum(favorable > 0.0)),
        "ties": int(np.sum(favorable == 0.0)),
        "win_rate_favoring_left": float(np.mean(favorable > 0.0)),
        "resamples": RESAMPLES,
        "seed": SEED,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    pilot_path = args.pilot.resolve()
    protocol_path = args.protocol.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(pilot_path.read_text())
    results = data.get("results", {})
    errors: list[str] = []
    expected_objects = 276
    if data.get("num_objects") != expected_objects:
        errors.append(f"expected {expected_objects} objects, got {data.get('num_objects')}")
    if data.get("num_steps") != 50 or data.get("seed") != 42:
        errors.append("seed/step configuration mismatch")
    if data.get("skip_calibration") is not True:
        errors.append("strict276 run must declare skip_calibration=true")
    if set(results) != set(METHODS):
        errors.append(f"method set mismatch: {sorted(results)}")

    by_method: dict[str, dict[str, dict]] = {}
    for method in METHODS:
        rows = results.get(method, [])
        if len(rows) != expected_objects:
            errors.append(f"{method}: expected {expected_objects} rows, got {len(rows)}")
        mapping = {row.get("object"): row for row in rows}
        if len(mapping) != len(rows):
            errors.append(f"{method}: duplicate object IDs")
        by_method[method] = mapping
        for row in rows:
            for metric, _ in METRICS:
                try:
                    if not math.isfinite(float(row[metric])):
                        errors.append(f"{method}/{row.get('object')}/{metric}: non-finite")
                except (KeyError, ValueError):
                    errors.append(f"{method}/{row.get('object')}/{metric}: missing/invalid")
    object_sets = {method: set(rows) for method, rows in by_method.items()}
    common = object_sets["C3_TCAS"]
    for method, objects in object_sets.items():
        if objects != common:
            errors.append(f"{method}: object set differs from C3")
    if len(common) != expected_objects:
        errors.append(f"common object count={len(common)}")

    fields = ["object", "method", *[metric for metric, _ in METRICS], "calibration_seconds", "inference_seconds", "controller_total_seconds"]
    csv_path = output_dir / "per_object_metrics.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for method in METHODS:
            for object_id in sorted(common):
                row = by_method[method][object_id]
                writer.writerow({"object": object_id, "method": method, **{field: row.get(field, "") for field in fields[2:]}})

    means = {
        method: {metric: float(np.mean([float(row[metric]) for row in by_method[method].values()])) for metric, _ in METRICS}
        for method in METHODS
    }
    comparisons = {}
    for method in NEW:
        comparisons[method] = {}
        for comparator in ("fixed_low", "C3_TCAS", "LLH_eq"):
            comparisons[method][f"{method}_minus_{comparator}"] = {
                metric: paired(by_method[method], by_method[comparator], metric, direction)
                for metric, direction in METRICS
            }
    gate = {}
    for method in NEW:
        primary = {
            comparator: comparisons[method][f"{method}_minus_{comparator}"]["fg_lpips"]
            for comparator in ("fixed_low", "C3_TCAS")
        }
        gate[method] = {
            "development_gate_recheck": all(item["ci95_raw_delta"][1] < 0.0 for item in primary.values()),
            "against_llh_eq": comparisons[method][f"{method}_minus_LLH_eq"]["fg_lpips"],
            "interpretation": "targeted strict276 follow-up; not original confirmatory selection",
        }

    audit = {
        "audit": "c3-tcas-schedule-followup-strict276-v1",
        "status": "complete" if not errors else "complete_with_errors",
        "pilot": str(pilot_path),
        "pilot_sha256": sha256(pilot_path),
        "protocol": str(protocol_path),
        "protocol_sha256": sha256(protocol_path),
        "objects": len(common),
        "methods": list(METHODS),
        "metrics": [metric for metric, _ in METRICS],
        "means": means,
        "paired_comparisons": comparisons,
        "gate_recheck": gate,
        "integrity": {"passed": not errors, "errors": errors},
        "bootstrap": {"unit": "object-level paired differences", "resamples": RESAMPLES, "seed": SEED, "confidence": 0.95},
        "provenance": {
            "checkpoint": data.get("checkpoint"),
            "checkpoint_sha256": data.get("checkpoint_sha256"),
            "object_list": data.get("object_list_file"),
            "object_list_sha256": data.get("object_list_sha256"),
            "controller": "/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py",
            "controller_sha256": sha256(Path("/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py")),
        },
        "output_csv": str(csv_path),
    }
    (output_dir / "STRICT276_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    (output_dir / "paired_bootstrap.json").write_text(json.dumps(audit, indent=2) + "\n")

    lines = [
        "# C3/TCAS schedule strict-276 follow-up audit",
        "",
        f"Status: **{'COMPLETE' if not errors else 'ERRORS'}**; rows per method: `{len(common)}`.",
        "",
        "This is a targeted post-development follow-up on the already-used clean-v2 strict-276 cohort. It is not relabelled as the original confirmatory protocol and does not alter CAI.",
        "",
        "## Means",
        "",
        "| method | FG-LPIPS ↓ | PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-MAE ↓ |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        lines.append(f"| {method} | {means[method]['fg_lpips']:.6f} | {means[method]['psnr']:.6f} | {means[method]['fg_ssim']:.6f} | {means[method]['edge_ssim']:.6f} | {means[method]['fg_mae']:.6f} |")
    lines += [
        "",
        "## New schedules: paired FG-LPIPS",
        "",
        "Negative candidate-minus-comparator delta is favorable.",
        "",
        "| candidate | comparator | mean delta | 95% CI | win rate |",
        "|---|---|---:|---|---:|",
    ]
    for method in NEW:
        for comparator in ("fixed_low", "C3_TCAS", "LLH_eq"):
            value = comparisons[method][f"{method}_minus_{comparator}"]["fg_lpips"]
            lines.append(f"| {method} | {comparator} | {value['mean_raw_delta_left_minus_right']:+.6f} | [{value['ci95_raw_delta'][0]:+.6f}, {value['ci95_raw_delta'][1]:+.6f}] | {value['win_rate_favoring_left']:.1%} |")
    lines += [
        "",
        "## Boundaries",
        "",
        "- Both candidates were fixed before strict-276 inference; neither is selected from strict-276 outcomes.",
        "- The result is schedule-only evidence for the main adapter. It is not MV-Adapter evidence and does not establish cross-backbone generalization.",
        "- No CIEDE2000 or GT-relative texture error is claimed for this main-adapter runner because those fields are not emitted here.",
        "- No manuscript, response letter, checkpoint, dataset or historical result was modified.",
        "",
    ]
    (output_dir / "C3_TCAS_SCHEDULE_STRICT276_AUDIT_20260929.md").write_text("\n".join(lines))
    print(json.dumps({"status": audit["status"], "objects": len(common), "output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
