#!/usr/bin/env python3
"""Audit the pre-specified strict TRB development pilot.

This is deliberately a read-only audit of an already completed pilot.  It
checks protocol provenance, paired-object completeness, calibration-cost
accounting, and a conservative primary-metric gate before a holdout run can
be considered eligible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


PRIMARY = "fg_lpips"
METHODS = ("fixed_low", "C3_TCAS", "HLL_eq", "LLH_eq", "TRB_TCAS")
METRICS = {
    "fg_lpips": ("lower", "FG-LPIPS"),
    "psnr": ("higher", "normalized-image PSNR (not FG-PSNR)"),
    "fg_ssim": ("higher", "FG-SSIM"),
    "edge_ssim": ("higher", "Edge-SSIM"),
    "fg_mae": ("lower", "foreground colour-error proxy (MAE)"),
    "fg_lap_var": ("diagnostic", "foreground Laplacian variance"),
    "fg_lap_corr": ("diagnostic", "foreground Laplacian correlation"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bootstrap_ci(values: np.ndarray, seed: int, reps: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(reps, len(values)))
    means = values[indices].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def direction_aware_win_rate(values: np.ndarray, direction: str) -> float | None:
    if direction == "lower":
        return float(np.mean(values < 0.0))
    if direction == "higher":
        return float(np.mean(values > 0.0))
    return None


def finite_rows(rows: list[dict], fields: list[str]) -> list[str]:
    errors = []
    for index, row in enumerate(rows):
        for field in fields:
            value = row.get(field)
            if value is None or not np.isfinite(float(value)):
                errors.append(f"row {index} field {field} is not finite")
    return errors


def audit(args: argparse.Namespace) -> dict:
    results_path = Path(args.pilot_results).resolve()
    data = json.loads(results_path.read_text())
    output_dir = results_path.parent
    expected_objects = int(data["num_objects"])
    expected_methods = list(data["methods"])
    checks: dict[str, object] = {}
    errors: list[str] = []

    checks["protocol"] = data.get("protocol") == "strict-trb-development-v2"
    checks["primary_metric"] = data.get("primary_metric") == PRIMARY
    checks["lpips_direction"] = data.get("lpips_direction") == "lower_is_better"
    checks["target_view_mode"] = data.get("target_view_mode") == "unique6"
    checks["num_steps"] = int(data.get("num_steps", -1)) == 50
    checks["seed"] = int(data.get("seed", -1)) == 42
    checks["methods"] = set(expected_methods) == set(METHODS)
    if not all(checks.values()):
        errors.extend(name for name, passed in checks.items() if not passed)

    object_list_path = Path(data["object_list_file"]).resolve()
    checkpoint_path = Path(data["checkpoint"]).resolve()
    for label, path, expected_hash in (
        ("object_list", object_list_path, data.get("object_list_sha256")),
        ("checkpoint", checkpoint_path, data.get("checkpoint_sha256")),
    ):
        exists = path.is_file()
        hash_matches = exists and expected_hash == sha256_file(path)
        checks[f"{label}_exists"] = exists
        checks[f"{label}_sha256"] = hash_matches
        if not exists:
            errors.append(f"{label} missing: {path}")
        elif not hash_matches:
            errors.append(f"{label} sha256 mismatch: {path}")

    object_ids = []
    if object_list_path.is_file():
        object_ids = [line.strip() for line in object_list_path.read_text().splitlines()
                      if line.strip() and not line.lstrip().startswith("#")]
    checks["object_list_count"] = len(object_ids) == expected_objects
    checks["object_list_unique"] = len(set(object_ids)) == len(object_ids)
    if not checks["object_list_count"]:
        errors.append(f"object list count={len(object_ids)}, expected={expected_objects}")
    if not checks["object_list_unique"]:
        errors.append("object list contains duplicate IDs")

    results = data["results"]
    by_method: dict[str, dict[str, dict]] = {}
    object_sets = {}
    required_fields = list(METRICS) + [
        "calibration_seconds", "inference_seconds", "controller_total_seconds"
    ]
    for method in expected_methods:
        rows = results.get(method, [])
        ids = [row.get("object") for row in rows]
        object_sets[method] = ids
        by_method[method] = {row["object"]: row for row in rows if "object" in row}
        if len(rows) != expected_objects:
            errors.append(f"{method} row count={len(rows)}, expected={expected_objects}")
        errors.extend(f"{method}: {message}" for message in finite_rows(rows, required_fields))
    common_ids = set(object_sets.get("TRB_TCAS", []))
    for method in expected_methods:
        if set(object_sets[method]) != common_ids:
            errors.append(f"{method} does not share the TRB object set")
    checks["paired_object_sets"] = not any("object set" in error for error in errors)

    calibration = data.get("calibration", {})
    calibration_records = calibration.get("per_object", [])
    checks["calibration_records"] = len(calibration_records) == expected_objects
    checks["calibration_forward_steps"] = (
        calibration.get("forward_steps_per_object") == int(data["num_steps"])
    )
    if not checks["calibration_records"]:
        errors.append("calibration record count does not match the object count")
    if not checks["calibration_forward_steps"]:
        errors.append("calibration forward-step count is not the configured step count")

    for object_id in common_ids:
        per_method = [by_method[method][object_id] for method in expected_methods]
        calibration_values = [float(row["calibration_seconds"]) for row in per_method]
        if not np.allclose(calibration_values, calibration_values[0], rtol=0.0, atol=1e-6):
            errors.append(f"calibration time differs across methods for {object_id}")
        trb = by_method["TRB_TCAS"][object_id]
        if not np.isclose(
            float(trb["controller_total_seconds"]),
            float(trb["calibration_seconds"]) + float(trb["inference_seconds"]),
            rtol=0.0,
            atol=1e-5,
        ):
            errors.append(f"TRB cost does not include calibration for {object_id}")
    checks["calibration_cost_accounted"] = not any(
        "calibration" in error or "TRB cost" in error for error in errors
    )

    maps = output_dir / "maps"
    map_count = len(list(maps.glob("*.png"))) if maps.is_dir() else 0
    budget_count = len(list(output_dir.glob("obj_*_budget.json")))
    expected_map_count = expected_objects * (len(expected_methods) + 2)
    checks["map_count"] = map_count == expected_map_count
    checks["budget_count"] = budget_count == expected_objects
    if not checks["map_count"]:
        errors.append(f"map count={map_count}, expected={expected_map_count}")
    if not checks["budget_count"]:
        errors.append(f"budget count={budget_count}, expected={expected_objects}")

    summary = {}
    for method in expected_methods:
        rows = results[method]
        summary[method] = {}
        for metric in METRICS:
            value = float(np.mean([float(row[metric]) for row in rows]))
            recorded = float(data["summary"][method][metric])
            summary[method][metric] = value
            if not np.isclose(value, recorded, rtol=0.0, atol=1e-7):
                errors.append(f"summary mismatch: {method}/{metric}")
        for timing_field in ("inference_seconds", "controller_total_seconds"):
            summary[method][f"{timing_field}_mean"] = float(
                np.mean([float(row[timing_field]) for row in rows])
            )

    comparisons = {}
    bootstrap_seed = int(args.bootstrap_seed)
    for comparator_index, comparator in enumerate(("fixed_low", "C3_TCAS")):
        comparator_result = {"comparator": comparator, "metrics": {}}
        for metric, (direction, label) in METRICS.items():
            if direction == "diagnostic":
                continue
            deltas = np.asarray([
                float(by_method["TRB_TCAS"][object_id][metric])
                - float(by_method[comparator][object_id][metric])
                for object_id in sorted(common_ids)
            ])
            ci_low, ci_high = bootstrap_ci(
                deltas, bootstrap_seed + comparator_index * 1000, int(args.bootstrap_reps)
            )
            comparator_result["metrics"][metric] = {
                "label": label,
                "direction": direction,
                "n": int(len(deltas)),
                "mean_raw_delta_trb_minus_comparator": float(deltas.mean()),
                "ci95_raw_delta": [ci_low, ci_high],
                "direction_aware_win_rate": direction_aware_win_rate(deltas, direction),
                "primary_gate_improvement": bool(
                    ci_high < 0.0 if direction == "lower" else ci_low > 0.0
                ) if metric == PRIMARY else None,
            }
        comparisons[comparator] = comparator_result

    primary_gate = {
        "metric": PRIMARY,
        "rule": "TRB must have a paired 95% bootstrap CI strictly better than both fixed-low and C3_TCAS",
        "fixed_low": comparisons["fixed_low"]["metrics"][PRIMARY],
        "C3_TCAS": comparisons["C3_TCAS"]["metrics"][PRIMARY],
    }
    primary_gate["passed"] = bool(
        primary_gate["fixed_low"]["primary_gate_improvement"]
        and primary_gate["C3_TCAS"]["primary_gate_improvement"]
    )

    cost_summary = {
        "calibration_seconds_mean": float(calibration.get("mean_seconds", np.nan)),
        "fixed_low_inference_seconds_mean": summary["fixed_low"].get("inference_seconds_mean"),
        "C3_TCAS_inference_seconds_mean": summary["C3_TCAS"].get("inference_seconds_mean"),
        "TRB_inference_seconds_mean": summary["TRB_TCAS"].get("inference_seconds_mean"),
        "TRB_total_seconds_mean": summary["TRB_TCAS"].get("controller_total_seconds_mean"),
    }
    if cost_summary["fixed_low_inference_seconds_mean"]:
        cost_summary["TRB_total_over_fixed_low_inference"] = (
            cost_summary["TRB_total_seconds_mean"]
            / cost_summary["fixed_low_inference_seconds_mean"]
        )

    passed_integrity = not errors
    decision = "eligible_for_one_locked_holdout" if passed_integrity and primary_gate["passed"] else "do_not_promote"
    report = {
        "audit": "strict-trb-development-v2",
        "pilot_results": str(results_path),
        "integrity": {
            "passed": passed_integrity,
            "checks": checks,
            "errors": errors,
            "map_count": map_count,
            "expected_map_count": expected_map_count,
            "budget_count": budget_count,
        },
        "summary": summary,
        "comparisons": comparisons,
        "primary_gate": primary_gate,
        "cost": cost_summary,
        "secondary_metric_caveat": (
            "The pilot's psnr field is the normalized-image PSNR emitted by "
            "compute_probes, not a foreground-masked FG-PSNR; it was not used "
            "for the promotion gate."
        ),
        "decision": decision,
        "bootstrap": {
            "seed": bootstrap_seed,
            "repetitions": int(args.bootstrap_reps),
            "unit": "object-level paired differences",
        },
    }
    return report


def markdown(report: dict) -> str:
    status = "PASS — eligible for one locked holdout" if report["decision"].startswith("eligible") else "NOT PROMOTED — no holdout authorized"
    lines = [
        "# Strict TRB development audit",
        "",
        f"Status: **{status}**.",
        "",
        f"Pilot: `{report['pilot_results']}`",
        "Protocol: clean-v2 24-object development set, unique6, 50 steps, shared object latent, paired object bootstrap.",
        "The audit is an evidence gate; it does not turn this development pilot into a paper result.",
        "",
        "## Integrity",
        "",
        f"- Integrity checks: **{'PASS' if report['integrity']['passed'] else 'FAIL'}**.",
        f"- Maps: `{report['integrity']['map_count']}/{report['integrity']['expected_map_count']}`; budgets: `{report['integrity']['budget_count']}/24`.",
        f"- Checkpoint/object-list hashes and shared object sets: **{'verified' if report['integrity']['passed'] else 'see errors'}**.",
        "",
        "## Method means",
        "",
        "| condition | FG-LPIPS ↓ | PSNR (normalized) | FG-SSIM | Edge-SSIM | FG-MAE ↓ | inference s | total s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, values in report["summary"].items():
        lines.append(
            f"| {method} | {values['fg_lpips']:.6f} | {values['psnr']:.3f} | "
            f"{values['fg_ssim']:.6f} | {values['edge_ssim']:.6f} | {values['fg_mae']:.6f} | "
            f"{values.get('inference_seconds_mean', float('nan')):.3f} | "
            f"{values.get('controller_total_seconds_mean', float('nan')):.3f} |"
        )
    lines += [
        "",
        "## Primary paired gate",
        "",
        "Raw delta is `TRB − comparator`; negative is better for FG-LPIPS.",
        "",
        "| comparator | mean Δ FG-LPIPS | 95% CI | win rate | stable improvement |",
        "|---|---:|---:|---:|---|",
    ]
    for comparator in ("fixed_low", "C3_TCAS"):
        item = report["comparisons"][comparator]["metrics"][PRIMARY]
        lines.append(
            f"| {comparator} | {item['mean_raw_delta_trb_minus_comparator']:+.6f} | "
            f"[{item['ci95_raw_delta'][0]:+.6f}, {item['ci95_raw_delta'][1]:+.6f}] | "
            f"{item['direction_aware_win_rate']:.1%} | "
            f"{'yes' if item['primary_gate_improvement'] else 'no'} |"
        )
    lines += [
        "",
        f"Gate decision: **{'pass' if report['primary_gate']['passed'] else 'fail'}**. "
        "A CI crossing zero is treated as uncertainty, not equivalence.",
        "",
        "## Calibration cost",
        "",
        f"Mean calibration time: `{report['cost']['calibration_seconds_mean']:.3f}` s/object. "
        f"TRB total mean: `{report['cost']['TRB_total_seconds_mean']:.3f}` s/object; "
        f"fixed-low inference mean: `{report['cost']['fixed_low_inference_seconds_mean']:.3f}` s/object; "
        f"ratio: `{report['cost'].get('TRB_total_over_fixed_low_inference', float('nan')):.2f}×`.",
        "",
        f"Secondary-metric caveat: {report['secondary_metric_caveat']}",
        "",
        "## Interpretation",
        "",
        "The development result is a method-screening result. It can authorize at most one locked holdout only when the integrity checks pass and the primary FG-LPIPS CI is strictly better than both fixed-low and C3_TCAS. It does not establish a universal backbone-transfer claim or a CAI winner.",
    ]
    if report["integrity"]["errors"]:
        lines += ["", "Integrity errors:", ""]
        lines.extend(f"- {error}" for error in report["integrity"]["errors"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-results", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--bootstrap-seed", type=int, default=20260929)
    parser.add_argument("--bootstrap-reps", type=int, default=10000)
    args = parser.parse_args()
    report = audit(args)
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    Path(args.output_md).write_text(markdown(report))
    print(json.dumps({
        "decision": report["decision"],
        "integrity_passed": report["integrity"]["passed"],
        "primary_gate_passed": report["primary_gate"]["passed"],
        "output_json": str(Path(args.output_json).resolve()),
        "output_md": str(Path(args.output_md).resolve()),
    }, indent=2))


if __name__ == "__main__":
    main()
