#!/usr/bin/env python3
"""Audit the frozen 24-object schedule-only development pilot."""

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
METHODS = ("fixed_low", "C3_TCAS", "HLL_eq", "LLH_eq", "LLH_ramp_eq", "LLH_cosine_eq")
NEW_METHODS = ("LLH_ramp_eq", "LLH_cosine_eq")


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
    index = rng.integers(0, values.size, size=(RESAMPLES, values.size))
    means = values[index].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def paired(left: dict[str, dict], right: dict[str, dict], metric: str, direction: str) -> dict:
    objects = sorted(set(left) & set(right))
    delta = np.asarray([float(left[obj][metric]) - float(right[obj][metric]) for obj in objects], dtype=np.float64)
    if direction == "lower":
        favorable = -delta
    else:
        favorable = delta
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
    if data.get("protocol") != "strict-trb-development-v2":
        errors.append(f"unexpected protocol={data.get('protocol')}")
    if data.get("num_objects") != 24:
        errors.append(f"expected 24 objects, got {data.get('num_objects')}")
    if data.get("num_steps") != 50 or data.get("seed") != 42:
        errors.append("seed/step configuration mismatch")
    if set(results) != set(METHODS):
        errors.append(f"method set mismatch: {sorted(results)}")

    by_method: dict[str, dict[str, dict]] = {}
    for method in METHODS:
        rows = results.get(method, [])
        if len(rows) != 24:
            errors.append(f"{method}: expected 24 rows, got {len(rows)}")
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
            for field in ("calibration_seconds", "inference_seconds", "controller_total_seconds"):
                try:
                    if not math.isfinite(float(row[field])):
                        errors.append(f"{method}/{row.get('object')}/{field}: non-finite")
                except (KeyError, ValueError):
                    errors.append(f"{method}/{row.get('object')}/{field}: missing/invalid")
    common_ids = set(by_method["C3_TCAS"])
    for method in METHODS:
        if set(by_method[method]) != common_ids:
            errors.append(f"{method}: object set differs from C3")

    fields = ["object", "method", *[metric for metric, _ in METRICS], "calibration_seconds", "inference_seconds", "controller_total_seconds"]
    csv_path = output_dir / "per_object_metrics.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for method in METHODS:
            for object_id in sorted(common_ids):
                row = by_method[method][object_id]
                writer.writerow({"object": object_id, "method": method, **{field: row[field] for field in fields[2:]}})

    means = {
        method: {
            metric: float(np.mean([float(row[metric]) for row in by_method[method].values()]))
            for metric, _ in METRICS
        }
        for method in METHODS
    }
    comparisons = {}
    for method in NEW_METHODS:
        comparisons[method] = {}
        for comparator in ("fixed_low", "C3_TCAS", "LLH_eq"):
            comparisons[method][f"{method}_minus_{comparator}"] = {
                metric: paired(by_method[method], by_method[comparator], metric, direction)
                for metric, direction in METRICS
            }

    gate = {}
    for method in NEW_METHODS:
        primary = {
            comparator: comparisons[method][f"{method}_minus_{comparator}"]["fg_lpips"]
            for comparator in ("fixed_low", "C3_TCAS")
        }
        gate[method] = {
            "rule": "FG-LPIPS paired 95% CI strictly below zero versus fixed_low and C3_TCAS",
            "comparisons": primary,
            "passed": all(item["ci95_raw_delta"][1] < 0.0 for item in primary.values()),
            "decision": "eligible_for_later_validation" if all(item["ci95_raw_delta"][1] < 0.0 for item in primary.values()) and not errors else "do_not_promote",
        }

    summary = {
        "protocol": data.get("protocol"),
        "pilot": str(pilot_path),
        "pilot_sha256": sha256(pilot_path),
        "protocol_file": str(protocol_path),
        "protocol_sha256": sha256(protocol_path),
        "object_count": len(common_ids),
        "methods": list(METHODS),
        "metrics": [metric for metric, _ in METRICS],
        "means": means,
        "paired_comparisons": comparisons,
        "promotion_gate": gate,
        "integrity": {"passed": not errors, "errors": errors},
        "calibration_cost": {
            "mean_seconds_per_object": float(data.get("calibration", {}).get("mean_seconds", float("nan"))),
            "forward_steps_per_object": data.get("calibration", {}).get("forward_steps_per_object"),
            "note": "Calibration is an audit/control pass in the pilot runner; the new schedules themselves do not use adaptive calibration.",
        },
        "implementation": {
            "controller_path": "/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py",
            "controller_sha256": sha256(Path("/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py")),
            "checkpoint": data.get("checkpoint"),
            "checkpoint_sha256": data.get("checkpoint_sha256"),
            "object_list": data.get("object_list_file"),
            "object_list_sha256": data.get("object_list_sha256"),
        },
    }
    (output_dir / "paired_bootstrap.json").write_text(json.dumps(summary, indent=2) + "\n")
    (output_dir / "RUN_AUDIT.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# C3/TCAS schedule follow-up audit",
        "",
        "Status: **development-only; no holdout promotion unless the pre-frozen gate passes**.",
        "",
        f"Integrity: **{'PASS' if not errors else 'FAIL'}**; objects: `{len(common_ids)}/24`; steps: `{data.get('num_steps')}`; seed: `{data.get('seed')}`.",
        "",
        "## Means",
        "",
        "| method | FG-LPIPS ↓ | PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-MAE ↓ | inference s/object |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        inference = float(np.mean([float(row["inference_seconds"]) for row in by_method[method].values()]))
        lines.append(f"| {method} | {means[method]['fg_lpips']:.6f} | {means[method]['psnr']:.6f} | {means[method]['fg_ssim']:.6f} | {means[method]['edge_ssim']:.6f} | {means[method]['fg_mae']:.6f} | {inference:.3f} |")
    lines += [
        "",
        "## New-schedule paired gate",
        "",
        "Raw delta is candidate minus comparator; negative is better for FG-LPIPS.",
        "",
        "| candidate | comparator | mean Δ FG-LPIPS | 95% CI | win rate | gate |",
        "|---|---|---:|---|---:|---|",
    ]
    for method in NEW_METHODS:
        for comparator in ("fixed_low", "C3_TCAS", "LLH_eq"):
            item = comparisons[method][f"{method}_minus_{comparator}"]["fg_lpips"]
            is_gate = comparator in ("fixed_low", "C3_TCAS")
            lines.append(f"| {method} | {comparator} | {item['mean_raw_delta_left_minus_right']:+.6f} | [{item['ci95_raw_delta'][0]:+.6f}, {item['ci95_raw_delta'][1]:+.6f}] | {item['win_rate_favoring_left']:.1%} | {'required' if is_gate else 'diagnostic'} |")
    lines += [
        "",
        "## Decision",
        "",
    ]
    for method in NEW_METHODS:
        lines.append(f"- `{method}`: **{gate[method]['decision']}**.")
    lines += [
        "",
        "The existing LLH-eq condition remains a pre-existing development baseline; neither new schedule is labelled CAI-calibrated. Even a passing development gate would authorize only a separately recorded later validation, not a paper claim or a 276/76 holdout run by itself.",
        "",
        "## Provenance",
        "",
        f"- Pilot SHA-256: `{sha256(pilot_path)}`.",
        f"- Protocol SHA-256: `{sha256(protocol_path)}`.",
        f"- Controller SHA-256: `{summary['implementation']['controller_sha256']}`.",
        f"- Checkpoint SHA-256: `{data.get('checkpoint_sha256')}`.",
        "- No dataset, checkpoint, frozen C3/MV-Adapter result, manuscript or response letter was modified.",
        "",
    ]
    (output_dir / "C3_TCAS_SCHEDULE_FOLLOWUP_AUDIT_20260929.md").write_text("\n".join(lines))
    print(json.dumps({
        "integrity_passed": not errors,
        "objects": len(common_ids),
        "gate": {method: value["decision"] for method, value in gate.items()},
        "output_dir": str(output_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
