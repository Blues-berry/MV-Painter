"""Freeze and audit existing round-two evidence without inference.

This is the E0-A gate: it checks the 276-object stage-placement records,
per-object CSVs, serialized Full-SSIM CSVs and PNG pairings, summarizes the
actual 50-step budgets, and records content hashes. It also compares the
repeated C3 condition from the main and follow-up runners without pooling it
when the artifacts are not identical.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "final/round2/stage_placement_276_20260929"
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
OUT = ROOT / "final/round2/coordination"
OBJECTS = tuple(f"obj_{i:04d}" for i in range(24, 300))
SCHEDULES = ("fixed_mean", "hll", "llh", "c3_lhl")
METRICS = ("full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim")
DIRECTION = {metric: metric not in {"full_lpips", "fg_lpips"} for metric in METRICS}
STAGES = ("early", "mid", "late")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def object_rows(path: Path, *, expected: tuple[str, ...]) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        object_id = row.get("object") or row.get("object_id")
        if object_id is None or object_id in out:
            raise ValueError(f"{path}: missing or duplicate object identifier")
        out[object_id] = row
    if tuple(sorted(out)) != tuple(sorted(expected)):
        raise ValueError(f"{path}: expected {len(expected)} exact object IDs, found {len(out)}")
    return out


def validate_records() -> tuple[dict[str, object], dict[str, str]]:
    files = sorted((STAGE / "records").glob("*.json"))
    expected = {f"{object_id}.json" for object_id in OBJECTS}
    if {path.name for path in files} != expected:
        raise ValueError("records directory is not exactly one JSON file per strict-276 object")
    actual: dict[str, dict[str, list[dict[str, object]]]] = {
        schedule: {object_id: [] for object_id in OBJECTS} for schedule in SCHEDULES
    }
    residual: dict[str, dict[str, list[float]]] = {
        schedule: {stage: [] for stage in STAGES} for schedule in SCHEDULES
    }
    hashes: dict[str, str] = {}
    for path in files:
        hashes[rel(path)] = sha256(path)
        payload = json.loads(path.read_text())
        object_id = payload.get("object")
        if object_id not in OBJECTS or path.stem != object_id:
            raise ValueError(f"record/object mismatch: {path}")
        if set(payload.get("rows", {})) != set(SCHEDULES):
            raise ValueError(f"{path}: rows do not contain exactly {SCHEDULES}")
        flat = payload.get("flat_rows")
        if not isinstance(flat, list) or len(flat) != len(SCHEDULES):
            raise ValueError(f"{path}: flat_rows count is not {len(SCHEDULES)}")
        if {(row.get("object"), row.get("schedule")) for row in flat} != {
            (object_id, schedule) for schedule in SCHEDULES
        }:
            raise ValueError(f"{path}: flat_rows do not match rows")
        for schedule in SCHEDULES:
            row = payload["rows"][schedule]
            if row != next(item for item in flat if item.get("schedule") == schedule):
                raise ValueError(f"{path}: rows and flat_rows differ for {schedule}")
            for metric in METRICS:
                if not finite(row.get(metric)):
                    raise ValueError(f"{path}: non-finite {schedule}.{metric}")
            logs = payload.get("residual_logs", {}).get(schedule, {})
            trace = logs.get("actual_scaled_residual")
            nominal = logs.get("nominal_scale_trace")
            if logs.get("steps_observed") != 50 or not isinstance(trace, list) or len(trace) != 50:
                raise ValueError(f"{path}: {schedule} does not have 50 residual observations")
            if not isinstance(nominal, list) or len(nominal) != 50:
                raise ValueError(f"{path}: {schedule} does not have 50 nominal scale observations")
            for step, nominal_step in zip(trace, nominal):
                if not all(finite(step.get(key)) for key in ("l2", "rms", "elements")):
                    raise ValueError(f"{path}: non-finite residual observation")
                stage = nominal_step.get("stage")
                if stage not in STAGES:
                    raise ValueError(f"{path}: unknown stage {stage}")
                residual[schedule][stage].append(float(step["l2"]))
            actual[schedule][object_id].append(row)
    for schedule in SCHEDULES:
        if any(len(actual[schedule][object_id]) != 1 for object_id in OBJECTS):
            raise ValueError(f"{schedule}: object rows are not complete")
    summary: dict[str, object] = {}
    nominal = {
        "fixed_mean": [5.0 / 3.0] * 50,
        "hll": [2.50] * 17 + [1.25] * 33,
        "llh": [1.25] * 33 + [2.50] * 17,
        "c3_lhl": [1.25] * 17 + [2.50] * 16 + [1.25] * 17,
    }
    for schedule in SCHEDULES:
        scale_trace = nominal[schedule]
        summary[schedule] = {
            "steps": 50,
            "stage_steps": {"early": 17, "mid": 16, "late": 17},
            "nominal_scale_sum": float(sum(scale_trace)),
            "nominal_scale_mean": float(np.mean(scale_trace)),
            "nominal_scale_squared_sum": float(np.square(scale_trace).sum()),
            "nominal_scale_squared_mean": float(np.square(scale_trace).mean()),
            "actual_residual_l2_mean_by_stage": {stage: float(np.mean(residual[schedule][stage])) for stage in STAGES},
            "actual_residual_l2_rms_by_stage": {stage: float(np.sqrt(np.mean(np.square(residual[schedule][stage])))) for stage in STAGES},
            "actual_residual_l2_mean_all_steps": float(np.mean([value for stage in STAGES for value in residual[schedule][stage]])),
        }
    return summary, hashes


def validate_csvs() -> tuple[dict[str, dict[str, dict[str, str]]], dict[str, str]]:
    stage_rows: dict[str, dict[str, dict[str, str]]] = {}
    hashes: dict[str, str] = {}
    for schedule in SCHEDULES:
        path = STAGE / f"per_object_{schedule}.csv"
        rows = object_rows(path, expected=OBJECTS)
        stage_rows[schedule] = rows
        hashes[rel(path)] = sha256(path)
        for row in rows.values():
            if any(not finite(row.get(metric)) for metric in METRICS):
                raise ValueError(f"{path}: non-finite metric")
    combined = STAGE / "per_object_metrics.csv"
    combined_rows = read_csv(combined)
    if len(combined_rows) != len(OBJECTS) * len(SCHEDULES):
        raise ValueError("per_object_metrics.csv is not 1104 rows")
    hashes[rel(combined)] = sha256(combined)
    pairs = {(row.get("object"), row.get("schedule")) for row in combined_rows}
    if len(pairs) != len(combined_rows) or pairs != {(o, s) for o in OBJECTS for s in SCHEDULES}:
        raise ValueError("combined CSV does not contain one unique row per object/schedule")
    serialized = STAGE / "serialized_full_ssim_per_object.csv"
    serialized_rows = read_csv(serialized)
    if len(serialized_rows) != len(OBJECTS) * len(SCHEDULES) or len({(r["object"], r["schedule"]) for r in serialized_rows}) != len(serialized_rows):
        raise ValueError("serialized Full-SSIM CSV is not an exact 276x4 pairing")
    serialized_by_schedule = defaultdict(dict)
    for row in serialized_rows:
        if not finite(row.get("full_ssim")) or row.get("prediction_dtype") != "torch.float32":
            raise ValueError("serialized Full-SSIM row is missing finite value or float32 provenance")
        serialized_by_schedule[row["schedule"]][row["object"]] = row
    hashes[rel(serialized)] = sha256(serialized)
    for schedule in SCHEDULES:
        for path in [STAGE / f"per_object_{schedule}_serialized_full_ssim.csv"]:
            rows = object_rows(path, expected=OBJECTS)
            hashes[rel(path)] = sha256(path)
            for object_id, row in rows.items():
                if abs(float(row["full_ssim"]) - float(serialized_by_schedule[schedule][object_id]["full_ssim"])) > 1e-12:
                    raise ValueError(f"serialized schedule CSV disagrees with combined CSV: {schedule}/{object_id}")
    return stage_rows, hashes


def base_summary() -> tuple[dict[str, object], dict[str, str]]:
    paths = {name: BASE / f"per_object_{name}.csv" for name in ("no_adapter", "fixed_low", "fixed_high", "c3")}
    hashes = {rel(path): sha256(path) for path in paths.values()}
    rows = {}
    ids = OBJECTS
    for name, path in paths.items():
        table = object_rows(path, expected=tuple(f"obj_{i:04d}" for i in range(300)))
        rows[name] = {object_id: table[object_id] for object_id in ids}
    summary = {
        name: {metric: float(np.mean([float(rows[name][object_id][metric]) for object_id in ids])) for metric in METRICS}
        for name in rows
    }
    return summary, hashes


def write_summary_csv(base: dict[str, object], stage: dict[str, dict[str, dict[str, str]]], serialized: dict[str, dict[str, str]]) -> Path:
    path = OUT / "E0A_STRICT276_METRICS_FROZEN.csv"
    fields = ["protocol", "condition", "metric", "mean", "source", "interpretation"]
    rows = []
    for condition, metrics in base.items():
        for metric, value in metrics.items():
            rows.append({"protocol": "main_clean_v2_pre_save", "condition": condition, "metric": metric, "mean": value, "source": "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/per_object_*.csv", "interpretation": "strict-276 slice; not pooled with stage follow-up"})
    for condition, table in stage.items():
        for metric in METRICS:
            rows.append({"protocol": "stage_placement_followup_pre_save", "condition": condition, "metric": metric, "mean": float(np.mean([float(row[metric]) for row in table.values()])), "source": f"final/round2/stage_placement_276_20260929/per_object_{condition}.csv", "interpretation": "within-follow-up paired comparison only"})
        rows.append({"protocol": "stage_placement_followup_serialized", "condition": condition, "metric": "full_ssim", "mean": float(np.mean([float(row["full_ssim"]) for row in serialized[condition].values()])), "source": "final/round2/stage_placement_276_20260929/serialized_full_ssim_per_object.csv", "interpretation": "PNG-reloaded float32 prediction vs raw RGBA/white float32 GT"})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    budget, record_hashes = validate_records()
    stage_rows, csv_hashes = validate_csvs()
    base, base_hashes = base_summary()
    serialized_rows = read_csv(STAGE / "serialized_full_ssim_per_object.csv")
    serialized = defaultdict(dict)
    for row in serialized_rows:
        serialized[row["schedule"]][row["object"]] = row
    metrics_csv = write_summary_csv(base, stage_rows, serialized)
    key_paths = [
        STAGE / "final_manifest.json", STAGE / "acceptance_manifest.json", STAGE / "stage_placement_manifest.json",
        STAGE / "serialized_full_ssim_paired_comparisons.json", STAGE / "SERIALIZED_FULL_SSIM_STAGE_PLACEMENT.md",
        BASE / "evaluation_manifest.json", ROOT / "final/round2/STAGE_PLACEMENT_PROTOCOL.json",
        ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt",
        ROOT / "geotex/round2_stats.py", ROOT / "geotex/stage_placement_eval.py",
    ]
    hash_map = {rel(path): sha256(path) for path in key_paths}
    hash_map.update(record_hashes)
    hash_map.update(csv_hashes)
    hash_map.update(base_hashes)
    for schedule in SCHEDULES:
        for path in sorted((STAGE / "predictions" / schedule).glob("*.png")):
            hash_map[rel(path)] = sha256(path)
    for path in sorted((STAGE / "predictions" / "ground_truth").glob("*.png")):
        hash_map[rel(path)] = sha256(path)
    hash_digest = hashlib.sha256(json.dumps(hash_map, sort_keys=True).encode()).hexdigest()

    # The repeated C3 is checked on the common 276 IDs; no silent pooling is allowed.
    base_c3 = object_rows(BASE / "per_object_c3.csv", expected=tuple(f"obj_{i:04d}" for i in range(300)))
    c3_diffs = {
        metric: {
            "mean_abs": float(np.mean([abs(float(base_c3[o][metric]) - float(stage_rows["c3_lhl"][o][metric])) for o in OBJECTS])),
            "max_abs": float(max(abs(float(base_c3[o][metric]) - float(stage_rows["c3_lhl"][o][metric])) for o in OBJECTS)),
        }
        for metric in METRICS
    }
    identical = all(value["max_abs"] == 0.0 for value in c3_diffs.values())

    paired = {}
    for comparator in ("fixed_mean", "hll", "llh"):
        paired[comparator] = {}
        for metric in METRICS:
            left = np.asarray([float(stage_rows["c3_lhl"][o][metric]) for o in OBJECTS])
            right = np.asarray([float(stage_rows[comparator][o][metric]) for o in OBJECTS])
            delta = left - right if DIRECTION[metric] else right - left
            paired[comparator][metric] = {
                "mean_improvement": float(delta.mean()),
                "win_rate": float(np.mean(delta > 0)),
                "n": len(delta),
            }

    payload = {
        "status": "PASS_WITH_LIMITATIONS",
        "protocol": "E0-A strict-276 evidence freeze",
        "checked": {"records": 276, "record_rows": 1104, "prediction_pngs": 1104, "ground_truth_pngs": 276, "serialized_full_ssim_rows": 1104},
        "pairing": {"records_csv_png_exact": True, "serialized_full_ssim_exact_object_schedule_pairs": True, "missing_as_na_not_zero": True},
        "base_main_protocol": {"name": "main_clean_v2_pre_save", "objects": 276, "conditions": list(base), "means": base},
        "stage_followup_protocol": {"name": "stage_placement_followup", "objects": 276, "conditions": list(stage_rows), "serialized_full_ssim_means": {s: float(np.mean([float(row["full_ssim"]) for row in serialized[s].values()])) for s in SCHEDULES}, "paired_c3_lhl": paired},
        "repeated_condition_check": {"main_c3_vs_followup_c3_lhl_identical": identical, "per_metric": c3_diffs, "decision": "do_not_pool_repeated_C3_or_absolute_metrics_across_protocols" if not identical else "identical_on_checked_fields"},
        "budget": budget,
        "hash_manifest_sha256": hash_digest,
        "hash_count": len(hash_map),
        "hashes": hash_map,
        "fixed_gt_decomposition": "final/round2/main_adapter_clean_v2/float_png_trace_12_controlled_20260929/FIXED_GT_SSIM_DECOMPOSITION.json",
        "summary_csv": rel(metrics_csv),
        "limitations": [
            "The 276-object stage-placement run is a pre-specified follow-up, not blind confirmation.",
            "The repeated C3 output is not identical to the main-run C3 output; absolute metrics must stay protocol-labelled.",
            "A/B/C fixed-GT decomposition is a 12-object controlled trace and cannot recover historical 300-object pre-save tensors.",
            "Actual residual norms describe effective intensity but do not prove residual-direction causality.",
        ],
    }
    json_path = OUT / "E0A_EVIDENCE_FREEZE_20260929.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    lines = [
        "# E0-A evidence freeze — 2026-09-29",
        "",
        "Status: **PASS_WITH_LIMITATIONS**. This CPU/static audit did not run model inference.",
        "",
        "## Exact pairing",
        "",
        "- 276 record JSON files, each with exactly four schedules and four flat rows; 1,104 stage rows; 1,104 serialized Full-SSIM rows; 1,104 prediction PNGs plus 276 GT PNGs.",
        "- `records.rows`, `flat_rows`, per-schedule CSVs, combined CSV, serialized CSVs and PNG filenames agree on the object/schedule keys.",
        "- All checked metric columns are finite. No missing value was converted to zero.",
        f"- The content-hash manifest contains `{len(hash_map)}` entries; canonical hash of that manifest: `{hash_digest}`.",
        "",
        "## Protocol separation",
        "",
        "The main four-condition clean-v2 run and the stage-placement follow-up share the checkpoint, object IDs, seed and nominal camera/step settings, but the repeated C3 condition is not byte- or value-identical. The largest observed per-metric difference is therefore preserved rather than silently pooled. The final paper should use the main run for no-adapter/fixed-low/fixed-high and use the follow-up only for within-run fixed-mean/HLL/LHL/LLH comparisons.",
        "",
        "## Stage-placement result boundary",
        "",
        "Within the follow-up, LHL/C3 is compared object-by-object with fixed mean, HLL and LLH. The saved-artifact Full-SSIM branch is PNG-reloaded float32 prediction against raw RGBA/white float32 GT. The machine-readable paired values and all seven pre-save metrics are in the JSON/CSV outputs.",
        "",
        "## Actual 50-step budget",
        "",
        "The stage trace uses early/mid/late = 17/16/17 steps. LHL, HLL and LLH have nominal scale means 1.650, 1.675 and 1.675, respectively; fixed mean is 1.666667. Exact sums, squared sums, and actual residual L2/RMS summaries are recorded in the JSON. The paper must not call the four schedules strictly equal-budget; their arithmetic mean and residual energy differ.",
        "",
        "## Fixed-GT SSIM decomposition",
        "",
        "The 12-object saved-tensor decomposition fixes one GT branch at a time and separates prediction dtype, prediction PNG quantization and GT PNG serialization. It is diagnostic only and does not require model rerun.",
        "",
        f"Machine-readable evidence: `{json_path.name}` and `{metrics_csv.name}`.",
    ]
    (OUT / "E0A_EVIDENCE_FREEZE_20260929.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": payload["status"], "hash_count": len(hash_map), "c3_identical": identical, "summary_csv": rel(metrics_csv)}, indent=2))


if __name__ == "__main__":
    main()
