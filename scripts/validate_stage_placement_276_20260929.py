#!/usr/bin/env python
"""One-shot acceptance gate for the independent A-2 stage-placement run.

This script intentionally does not inspect records while the runner is active.
It is called at a scheduled checkpoint, and writes a durable handoff marker for
the next coordination turn instead of editing the paper.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/stage_placement_276_20260929"
STATUS = OUT / "status.json"
FINAL = OUT / "final_manifest.json"
ACCEPTANCE = OUT / "acceptance_manifest.json"
NEXT_READY = OUT / "NEXT_ITERATION_READY.json"
NEXT_BLOCKED = OUT / "NEXT_ITERATION_BLOCKED.json"
EXPECTED_OBJECTS = tuple(f"obj_{i:04d}" for i in range(24, 300))
SCHEDULES = ("fixed_mean", "hll", "llh", "c3_lhl")
METRICS = ("full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim")
DIRECTION = {metric: metric not in {"full_lpips", "fg_lpips"} for metric in METRICS}
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"

sys.path.insert(0, str(ROOT / "geotex"))
from round2_stats import paired_csv_summary  # noqa: E402


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def write_blocked(reasons: list[str], *, phase: str) -> int:
    payload = {
        "run_id": "stage_placement_276_20260929_resume_v2",
        "checked_at": stamp(),
        "status": "blocked",
        "phase": phase,
        "reasons": reasons,
        "paper_edit_allowed": False,
    }
    atomic_json(NEXT_BLOCKED, payload)
    atomic_json(ACCEPTANCE, payload)
    return 2 if phase == "running" else 1


def finite_number(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def object_csv(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get("object") or row.get("object_id")
        if not key:
            raise ValueError(f"{path}: missing object identifier")
        if key in result:
            raise ValueError(f"{path}: duplicate object {key}")
        result[key] = row
    return result


def validate_records() -> tuple[list[str], dict[str, dict[str, float]]]:
    reasons: list[str] = []
    record_dir = OUT / "records"
    if not record_dir.is_dir():
        return [f"missing record directory: {record_dir}"], {}
    files = sorted(record_dir.glob("*.json"))
    expected_names = {f"{object_id}.json" for object_id in EXPECTED_OBJECTS}
    actual_names = {path.name for path in files}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        if missing:
            reasons.append(f"missing record files: {len(missing)}")
        if extra:
            reasons.append(f"unexpected record files: {extra[:5]}")

    residual_sum: dict[str, dict[str, float]] = {
        schedule: {"count": 0.0, "l2_sum": 0.0, "rms_sum": 0.0, "min_l2": float("inf"), "max_l2": 0.0, "min_rms": float("inf"), "max_rms": 0.0}
        for schedule in SCHEDULES
    }
    for path in files:
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            reasons.append(f"invalid JSON {path.name}: {exc}")
            continue
        object_id = payload.get("object")
        if object_id not in EXPECTED_OBJECTS or path.name != f"{object_id}.json":
            reasons.append(f"object/file mismatch: {path.name} -> {object_id}")
        rows = payload.get("rows")
        flat_rows = payload.get("flat_rows")
        residual_logs = payload.get("residual_logs")
        if not isinstance(rows, dict) or set(rows) != set(SCHEDULES):
            reasons.append(f"{path.name}: schedule rows are not exactly {SCHEDULES}")
            continue
        if not isinstance(flat_rows, list) or len(flat_rows) != len(SCHEDULES):
            reasons.append(f"{path.name}: flat_rows count is not {len(SCHEDULES)}")
        if not isinstance(residual_logs, dict) or set(residual_logs) != set(SCHEDULES):
            reasons.append(f"{path.name}: residual log schedules are incomplete")
            continue
        for schedule in SCHEDULES:
            row = rows[schedule]
            if row.get("object") != object_id or row.get("schedule") != schedule:
                reasons.append(f"{path.name}: malformed row for {schedule}")
            for metric in METRICS:
                if metric not in row or not finite_number(row[metric]):
                    reasons.append(f"{path.name}: non-finite or missing {schedule}.{metric}")
            log = residual_logs[schedule]
            trace = log.get("actual_scaled_residual") if isinstance(log, dict) else None
            if not isinstance(trace, list) or len(trace) != 50 or log.get("steps_observed") != 50:
                reasons.append(f"{path.name}: {schedule} does not contain 50 actual residual steps")
                continue
            for step in trace:
                if not isinstance(step, dict) or any(not finite_number(step.get(key)) for key in ("l2", "rms", "elements")):
                    reasons.append(f"{path.name}: non-finite residual in {schedule}")
                    break
                if float(step["l2"]) < 0 or float(step["rms"]) < 0 or float(step["elements"]) <= 0:
                    reasons.append(f"{path.name}: invalid residual norm in {schedule}")
                    break
                summary = residual_sum[schedule]
                l2 = float(step["l2"])
                rms = float(step["rms"])
                summary["count"] += 1
                summary["l2_sum"] += l2
                summary["rms_sum"] += rms
                summary["min_l2"] = min(summary["min_l2"], l2)
                summary["max_l2"] = max(summary["max_l2"], l2)
                summary["min_rms"] = min(summary["min_rms"], rms)
                summary["max_rms"] = max(summary["max_rms"], rms)
    for summary in residual_sum.values():
        count = summary["count"]
        if count:
            summary["mean_l2"] = summary.pop("l2_sum") / count
            summary["mean_rms"] = summary.pop("rms_sum") / count
        else:
            summary.pop("l2_sum")
            summary.pop("rms_sum")
    return reasons, residual_sum


def validate_csvs() -> tuple[list[str], dict[str, object]]:
    reasons: list[str] = []
    summaries: dict[str, object] = {}
    all_ids = set(EXPECTED_OBJECTS)
    for schedule in SCHEDULES:
        path = OUT / f"per_object_{schedule}.csv"
        if not path.is_file():
            reasons.append(f"missing {path.name}")
            continue
        rows = object_csv(path)
        if set(rows) != all_ids:
            reasons.append(f"{path.name}: expected 276 unique object rows, got {len(rows)}")
        for object_id, row in rows.items():
            for metric in METRICS:
                if metric not in row or not finite_number(row[metric]):
                    reasons.append(f"{path.name}: non-finite or missing {object_id}.{metric}")
        summaries[schedule] = rows
    combined = OUT / "per_object_metrics.csv"
    if not combined.is_file():
        reasons.append("missing per_object_metrics.csv")
    else:
        combined_rows = read_csv(combined)
        if len(combined_rows) != 276 * len(SCHEDULES):
            reasons.append(f"per_object_metrics.csv: expected {276 * len(SCHEDULES)} rows, got {len(combined_rows)}")
    return reasons, summaries


def compute_comparisons(stage_rows: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    c3 = stage_rows["c3_lhl"]
    for baseline in ("fixed_mean", "hll", "llh"):
        result[f"c3_lhl_vs_{baseline}"] = paired_csv_summary(
            c3,
            stage_rows[baseline],
            metrics=METRICS,
            object_ids=EXPECTED_OBJECTS,
            higher_is_better=DIRECTION,
            seed=20260928,
            n_resamples=10000,
        )
    if all((BASE / f"per_object_{name}.csv").is_file() for name in ("c3", "fixed_low", "fixed_high")):
        historical_c3 = object_csv(BASE / "per_object_c3.csv")
        for baseline in ("fixed_low", "fixed_high"):
            result[f"historical_c3_vs_{baseline}"] = paired_csv_summary(
                historical_c3,
                object_csv(BASE / f"per_object_{baseline}.csv"),
                metrics=METRICS,
                object_ids=EXPECTED_OBJECTS,
                higher_is_better=DIRECTION,
                seed=20260928,
                n_resamples=10000,
            )
    return result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not STATUS.is_file():
        return write_blocked([f"missing {STATUS}"], phase="missing_status")
    status = json.loads(STATUS.read_text())
    if status.get("phase") == "running":
        return write_blocked(["A-2 is still running; no intermediate records were inspected"], phase="running")
    if not FINAL.is_file():
        return write_blocked([f"missing terminal manifest {FINAL}"], phase="missing_terminal_manifest")
    final = json.loads(FINAL.read_text())
    if final.get("phase") != "completed" or final.get("exit_code") != 0:
        return write_blocked([f"terminal run is not successful: phase={final.get('phase')} exit_code={final.get('exit_code')}"], phase="failed")
    if final.get("record_count") != 276 or final.get("error_count") != 0:
        return write_blocked([f"manifest counts failed: records={final.get('record_count')} errors={final.get('error_count')}"], phase="failed")

    reasons, residual_summary = validate_records()
    csv_reasons, stage_rows = validate_csvs()
    reasons.extend(csv_reasons)
    if reasons:
        return write_blocked(reasons[:100], phase="acceptance_failed")
    comparisons = compute_comparisons(stage_rows)
    payload = {
        "run_id": final.get("run_id"),
        "checked_at": stamp(),
        "status": "accepted",
        "acceptance": {
            "objects": 276,
            "schedules": list(SCHEDULES),
            "records": 276,
            "rows": 276 * len(SCHEDULES),
            "errors": 0,
            "finite_metrics": True,
            "actual_residual_steps_per_object_schedule": 50,
            "paired_bootstrap": {"seed": 20260928, "resamples": 10000, "unit": "object-level paired bootstrap", "ci": 0.95},
        },
        "residual_summary": residual_summary,
        "comparisons": comparisons,
        "paper_edit_allowed": False,
        "next_gate": "E G2-G4 evidence review, then explicit C paper-release decision",
    }
    atomic_json(ACCEPTANCE, payload)
    NEXT_BLOCKED.unlink(missing_ok=True)
    atomic_json(NEXT_READY, {
        "created_at": payload["checked_at"],
        "status": "ready_for_next_iteration",
        "source": str(ACCEPTANCE),
        "next_action": "Run E evidence review and decide whether Codex C may edit the manuscript; do not edit paper automatically.",
        "paper_edit_allowed": False,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
