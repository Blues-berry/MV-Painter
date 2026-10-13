#!/usr/bin/env python3
"""Paired object-level analysis for the frozen retrospective applied-budget study."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MAIN_RUN = HERE / "runs/main_applied_budget_20261010_retrospective"
EXTREMES_RUN = HERE / "runs/main_applied_magnitude_extremes_20261010"
COHORT_UID_LIST = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/fresh_c_objects.txt")
OUTPUT = HERE / "analysis/applied_budget_paired_report.json"
CONDITIONS = {
    "Fixed Low": (EXTREMES_RUN, "budget_fixed_low"),
    "Fixed High": (EXTREMES_RUN, "budget_fixed_high"),
    "Fixed Applied Mean": (MAIN_RUN, "budget_fixed_mean"),
    "Early-high": (MAIN_RUN, "budget_early16"),
    "Middle-high": (MAIN_RUN, "native_gc3"),
    "Late-high": (MAIN_RUN, "budget_late16"),
}
EXPECTED_OBJECTS = 300
ENDPOINTS = ("fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim")
PAIRS = (("Middle-high", "Early-high"), ("Middle-high", "Late-high"),
         ("Early-high", "Late-high"))
BOOTSTRAPS = 10_000
PERMUTATIONS = 20_000
SEED = 2_026_1010


def load_condition(run_dir: Path, condition: str, expected_objects: int) -> dict[str, dict[str, str]]:
    # Prefer the merged export rebuilt from the complete JSON row ledger. A
    # completed worker may leave an older, partial shard CSV beside it.
    merged_path = run_dir / "per_object_metrics.csv"
    paths = [merged_path] if merged_path.is_file() else sorted(
        run_dir.glob("per_object_metrics_shard*.csv")
    )
    if not paths:
        raise FileNotFoundError(f"per-object metric CSVs are missing under {run_dir}")
    rows = []
    for path in paths:
        with path.open(newline="") as handle:
            rows.extend(row for row in csv.DictReader(handle) if row["condition"] == condition)
    by_uid = {row["object_uid"]: row for row in rows}
    if len(rows) != expected_objects or len(by_uid) != expected_objects:
        raise RuntimeError(f"{condition} is incomplete or duplicated: {len(rows)} rows")
    return by_uid


def bootstrap_summary(delta: np.ndarray, rng: np.random.Generator) -> dict:
    n = len(delta)
    samples = rng.integers(0, n, size=(BOOTSTRAPS, n))
    means = delta[samples].mean(axis=1)
    return {
        "n_objects": n,
        "mean_difference": float(delta.mean()),
        "median_difference": float(np.median(delta)),
        "ci95_percentile": [float(x) for x in np.quantile(means, [0.025, 0.975])],
        "objects_positive": int(np.count_nonzero(delta > 0)),
        "objects_tied": int(np.count_nonzero(delta == 0)),
        "win_rate": float(np.mean(delta > 0)),
    }


def sign_flip_p(delta: np.ndarray, rng: np.random.Generator) -> float:
    observed = abs(float(delta.mean()))
    signs = rng.integers(0, 2, size=(PERMUTATIONS, len(delta)), dtype=np.int8) * 2 - 1
    null = np.abs((signs * delta).mean(axis=1))
    return float((1 + np.count_nonzero(null >= observed)) / (PERMUTATIONS + 1))


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    m = len(ordered)
    adjusted = {}
    running = 0.0
    for rank, (name, p_value) in enumerate(ordered):
        running = max(running, min(1.0, (m - rank) * p_value))
        adjusted[name] = running
    return adjusted


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_paired_inputs(expected_objects: int) -> dict:
    identities = {}
    for name, run_dir in (("main", MAIN_RUN), ("fixed_magnitudes", EXTREMES_RUN)):
        path = run_dir / "RUN_IDENTITY.json"
        identities[name] = json.loads(path.read_text())
    main_identity = identities["main"]
    extremes_identity = identities["fixed_magnitudes"]
    frozen_uids = [line.strip() for line in COHORT_UID_LIST.read_text().splitlines() if line.strip()]
    if len(frozen_uids) != expected_objects or len(set(frozen_uids)) != expected_objects:
        raise RuntimeError(f"frozen cohort UID list is incomplete or duplicated: {len(frozen_uids)}")
    if sha256(COHORT_UID_LIST) != main_identity.get("source_hashes", {}).get("cohort_uid_list"):
        raise RuntimeError("current cohort UID list does not match the frozen run identity")
    if main_identity.get("source_hashes") != extremes_identity.get("source_hashes"):
        raise RuntimeError("GeoTex main and fixed-magnitude runs do not share source hashes")
    if (main_identity.get("base_model_tree_sha256") != extremes_identity.get("base_model_tree_sha256")
            or main_identity.get("cohort_n") != expected_objects
            or extremes_identity.get("cohort_n") != expected_objects):
        raise RuntimeError("GeoTex run model identity or cohort size differs")
    expected_row_counts = {
        "main": expected_objects * len(main_identity.get("conditions", [])),
        "fixed_magnitudes": expected_objects * len(extremes_identity.get("conditions", [])),
    }
    for name, identity in identities.items():
        if identity.get("status") != "COMPLETED" or identity.get("row_count") != expected_row_counts[name]:
            raise RuntimeError(f"GeoTex source run is not finalized: {name}")

    raw_rows = []
    raw_files = []
    for run_dir in (MAIN_RUN, EXTREMES_RUN):
        files = sorted(run_dir.glob("rows_shard*.json"))
        if not files:
            raise FileNotFoundError(f"raw inference rows are missing under {run_dir}")
        raw_files.extend(files)
        for path in files:
            raw_rows.extend(json.loads(path.read_text()))
    expected_conditions = {condition for _, condition in CONDITIONS.values()}
    counts: dict[str, int] = {}
    by_uid: dict[str, list[dict]] = {}
    for row in raw_rows:
        condition = row["condition"]
        if condition not in expected_conditions:
            continue
        counts[condition] = counts.get(condition, 0) + 1
        by_uid.setdefault(row["object_uid"], []).append(row)
    if counts != {condition: expected_objects for condition in expected_conditions}:
        raise RuntimeError(f"raw paired condition rows are incomplete: {counts}")
    if len(by_uid) != expected_objects:
        raise RuntimeError(f"expected {expected_objects} paired UIDs, found {len(by_uid)}")
    if set(by_uid) != set(frozen_uids):
        raise RuntimeError("inference rows do not exactly cover the frozen 300-object UID list")

    signatures = {}
    for uid, rows in by_uid.items():
        if len(rows) != len(expected_conditions) or {row["condition"] for row in rows} != expected_conditions:
            raise RuntimeError(f"condition coverage is incomplete for {uid}")
        per_condition = {
            row["condition"]: {
                "seed_base": row["seed_base"],
                "input_hashes": row["input_hashes"],
            }
            for row in rows
        }
        if len({json.dumps(value, sort_keys=True) for value in per_condition.values()}) != 1:
            raise RuntimeError(f"cross-condition input hashes or seeds differ for {uid}")
        signatures[uid] = next(iter(per_condition.values()))
    signature_blob = json.dumps(signatures, sort_keys=True, separators=(",", ":")).encode()
    return {
        "status": "PASS_EXACT_PAIRED_INPUTS",
        "n_objects": expected_objects,
        "condition_counts": counts,
        "object_condition_rows": len(raw_rows),
        "per_object_seed_and_input_hashes_match_across_all_conditions": True,
        "paired_input_signature_sha256": hashlib.sha256(signature_blob).hexdigest(),
        "source_run_identities": {
            name: {
                "path": str((MAIN_RUN if name == "main" else EXTREMES_RUN) / "RUN_IDENTITY.json"),
                "sha256": sha256((MAIN_RUN if name == "main" else EXTREMES_RUN) / "RUN_IDENTITY.json"),
                "status": identity.get("status", "RUN_IDENTITY_RETAINED_WITH_COMPLETION_AUDIT"),
                "source_hashes": identity.get("source_hashes"),
                "base_model_tree_sha256": identity.get("base_model_tree_sha256"),
            }
            for name, identity in identities.items()
        },
        "raw_row_files": [{"path": str(path), "sha256": sha256(path)} for path in raw_files],
    }


def summarize_residual_logs(condition_name: str, expected_objects: int) -> dict:
    run_dir, condition = CONDITIONS[condition_name]
    root = run_dir / "residual_logs" / condition
    files = sorted(root.glob("*.json"))
    if len(files) != expected_objects:
        raise RuntimeError(f"{condition_name} residual logs are incomplete: {len(files)}")
    accum: dict[tuple[int, str], list[dict]] = {}
    for path in files:
        log = json.loads(path.read_text())
        if len(log) != 50:
            raise RuntimeError(f"residual log does not have 50 steps: {path}")
        for raw_step, modules in log.items():
            step = int(raw_step)
            by_depth: dict[str, list[dict]] = {}
            for module in modules.values():
                by_depth.setdefault(module["depth"], []).append(module)
            for depth, entries in by_depth.items():
                key = (step, depth)
                accum.setdefault(key, []).append({
                    "module_count": len(entries),
                    "sum_module_l2": sum(float(item["l2"]) for item in entries),
                    "mean_module_l2": sum(float(item["l2"]) for item in entries) / len(entries),
                    "mean_abs": sum(float(item["mean_abs"]) for item in entries) / len(entries),
                    "requested_scale": float(entries[0]["scale"]),
                    "effective_scale": float(entries[0]["eff_scale"]),
                })
    result = {}
    for (step, depth), items in sorted(accum.items()):
        result.setdefault(str(step), {})[depth] = {
            key: float(np.mean([item[key] for item in items]))
            for key in ("module_count", "sum_module_l2", "mean_module_l2", "mean_abs",
                        "requested_scale", "effective_scale")
        }
    return result


def validate_metric_csvs_against_raw_rows(expected_objects: int) -> dict:
    raw_metric_rows = {}
    for run_dir in (MAIN_RUN, EXTREMES_RUN):
        for path in sorted(run_dir.glob("rows_shard*.json")):
            for row in json.loads(path.read_text()):
                raw_metric_rows[(row["condition"], row["object_uid"])] = row
    comparisons = 0
    for run_dir, condition in CONDITIONS.values():
        metrics = load_condition(run_dir, condition, expected_objects)
        for uid, csv_row in metrics.items():
            raw_row = raw_metric_rows[(condition, uid)]
            for metric in ENDPOINTS:
                if not np.isclose(float(csv_row[metric]), float(raw_row[metric]), rtol=1e-9, atol=1e-9):
                    raise RuntimeError(f"CSV and raw JSON metric differ: {condition}/{uid}/{metric}")
                comparisons += 1
    return {"status": "PASS_CSV_MATCHES_RAW_JSON", "metric_values_compared": comparisons}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--expected-objects", type=int, default=EXPECTED_OBJECTS)
    args = parser.parse_args()
    paired_input_audit = audit_paired_inputs(args.expected_objects)
    data = {label: load_condition(run_dir, condition, args.expected_objects)
            for label, (run_dir, condition) in CONDITIONS.items()}
    metric_export_audit = validate_metric_csvs_against_raw_rows(args.expected_objects)
    uids = set(next(iter(data.values())))
    if len(uids) != args.expected_objects:
        raise RuntimeError(f"expected {args.expected_objects} paired UIDs, found {len(uids)}")
    if any(set(rows) != uids for rows in data.values()):
        raise RuntimeError("condition UID sets differ")
    values = {
        label: {metric: np.asarray([float(rows[uid][metric]) for uid in sorted(uids)])
                for metric in ENDPOINTS}
        for label, rows in data.items()
    }
    if any(not np.isfinite(array).all() for item in values.values() for array in item.values()):
        raise RuntimeError("non-finite metric found")

    rng = np.random.default_rng(SEED)
    primary_delta = values["Middle-high"]["fg_psnr"] - (
        values["Early-high"]["fg_psnr"] + values["Late-high"]["fg_psnr"]
    ) / 2.0
    primary = bootstrap_summary(primary_delta, rng)
    primary["permutation_p_two_sided_unadjusted"] = sign_flip_p(primary_delta, rng)
    primary["object_differences"] = {uid: float(value) for uid, value in zip(sorted(uids), primary_delta)}

    secondary = {}
    raw_p = {}
    for metric in ENDPOINTS:
        for first, second in PAIRS:
            name = f"{first} minus {second} / {metric}"
            delta = values[first][metric] - values[second][metric]
            secondary[name] = bootstrap_summary(delta, rng)
            secondary[name]["object_differences"] = {
                uid: float(value) for uid, value in zip(sorted(uids), delta)
            }
            raw_p[name] = sign_flip_p(delta, rng)
    adjusted = holm_adjust(raw_p)
    for name in secondary:
        secondary[name]["permutation_p_two_sided"] = raw_p[name]
        secondary[name]["holm_adjusted_p"] = adjusted[name]

    condition_means = {
        label: {metric: float(values[label][metric].mean()) for metric in ENDPOINTS}
        for label in values
    }
    residuals = {label: summarize_residual_logs(label, args.expected_objects) for label in CONDITIONS}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    paired_csv_path = args.output.with_name(args.output.stem + "_paired_object_metrics.csv")
    fields = ["object_uid", "condition", *ENDPOINTS]
    with paired_csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for label, rows in data.items():
            for uid in sorted(uids):
                writer.writerow({"object_uid": uid, "condition": label,
                                 **{metric: rows[uid][metric] for metric in ENDPOINTS}})
    report = {
        "status": "COMPLETE_PAIRED_ANALYSIS",
        "evidence_grade": "RETROSPECTIVE",
        "n_objects": len(uids),
        "object_uids": sorted(uids),
        "conditions": {label: {"run_dir": str(run_dir), "condition": condition}
                       for label, (run_dir, condition) in CONDITIONS.items()},
        "paired_input_audit": paired_input_audit,
        "metric_export_audit": metric_export_audit,
        "paired_object_metrics_path": str(paired_csv_path),
        "paired_object_metrics_sha256": sha256(paired_csv_path),
        "seed": SEED,
        "bootstrap_resamples": BOOTSTRAPS,
        "secondary_sign_flip_permutations": PERMUTATIONS,
        "primary_contrast": "Middle-high fg_psnr minus mean(Early-high, Late-high fg_psnr)",
        "primary_fg_psnr": primary,
        "condition_metric_means": condition_means,
        "secondary_pairwise_contrasts": secondary,
        "residual_norm_curves_by_step_and_depth": residuals,
        "ciede2000": "Unavailable in the frozen runner; not inferred from unrelated metrics.",
        "limitations": [
            "The 300-object compatibility cohort and outcomes were already selected or observed; this analysis is retrospective.",
            "All six conditions are drawn from two runs that share the same content-hashed base model, frozen runner, input hashes, and per-object seed.",
            "Equal nominal applied-scale sums do not imply equal realized residual dose.",
            "No independent schedule-selection or automatic schedule rule is tested.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    markdown = [
        "# GeoTex applied-budget paired analysis",
        "",
        f"Status: `{report['status']}`; {len(uids)} paired objects across six conditions.",
        "",
        "This is a retrospective analysis of a technical compatibility cohort. The two source runs share the same frozen model, runner, input hashes, and per-object seed; the paired input audit is recorded in the JSON report.",
        "",
        "## Condition means",
        "",
        "| Condition | FG-PSNR ↑ | FG-LPIPS ↓ | FG-SSIM ↑ | Edge-SSIM ↑ |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, means in condition_means.items():
        markdown.append("| " + label + " | " + " | ".join(f"{means[m]:.4f}" for m in ENDPOINTS) + " |")
    primary_result = report["primary_fg_psnr"]
    markdown += [
        "",
        "## Primary contrast",
        "",
        f"Middle-high FG-PSNR minus the mean of Early-high and Late-high: {primary_result['mean_difference']:.4f} dB (95% object-bootstrap interval {primary_result['ci95_percentile'][0]:.4f} to {primary_result['ci95_percentile'][1]:.4f}; two-sided sign-flip p={primary_result['permutation_p_two_sided_unadjusted']:.4g}).",
        "",
        "The inferential and residual-log details are in the machine-readable JSON report.",
    ]
    args.output.with_suffix(".md").write_text("\n".join(markdown) + "\n")
    print(json.dumps({"status": report["status"], "n_objects": len(uids),
                      "primary_fg_psnr": primary, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
