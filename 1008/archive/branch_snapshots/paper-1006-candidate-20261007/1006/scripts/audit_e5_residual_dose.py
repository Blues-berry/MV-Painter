#!/usr/bin/env python3
"""Audit numerical gates for the E5 feasibility pilot; no quality metrics."""
from __future__ import annotations

import json
import hashlib
import math
import statistics
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/e5_residual_dose"
RUN = DATA / "runs"
GROUPS = ("deep", "middle", "shallow")
WINDOWS = (1, 3, 5)
ALPHAS = (0.005, 0.01, 0.02)
EXPECTED_PER_OBJECT = {"baseline", "alpha0_noop"} | {
    f"{g}_W{w}_a{a:g}" for g in GROUPS for w in WINDOWS for a in ALPHAS
}


def main() -> None:
    lock = json.loads((DATA / "E5_LOCK.json").read_text())
    pilot_script = ROOT / "1006/scripts/run_e5_residual_dose.py"
    digest = hashlib.sha256(pilot_script.read_bytes()).hexdigest()
    if lock["pilot_script_sha256"] != digest:
        raise RuntimeError("E5 pilot script identity mismatch")
    audit_script = ROOT / "1006/scripts/audit_e5_residual_dose.py"
    if lock["audit_script_sha256"] != hashlib.sha256(audit_script.read_bytes()).hexdigest():
        raise RuntimeError("E5 auditor identity mismatch")
    preflights = {}
    for shard in (0, 1):
        preflight = json.loads((RUN / f"model_preflight_shard{shard}.json").read_text())
        if preflight["protocol_sha256"] != lock["protocol_sha256"]:
            raise RuntimeError(f"shard {shard} preflight protocol hash mismatch")
        if preflight["source_hashes"] != lock["source_hashes"]:
            raise RuntimeError(f"shard {shard} preflight source identity mismatch")
        preflights[shard] = preflight
    if preflights[0]["group_adapter_indices"] != preflights[1]["group_adapter_indices"]:
        raise RuntimeError("adapter-to-group mapping differs between GPU shards")
    rows = []
    for shard in (0, 1):
        manifest = json.loads((RUN / f"shard{shard}_manifest.json").read_text())
        if manifest["status"] != "complete" or manifest["source_hashes"] != lock["source_hashes"]:
            raise RuntimeError(f"shard {shard} completion/source identity failed")
        rows.extend(json.loads((RUN / f"rows_shard{shard}.json").read_text()))
    by_object = {}
    input_hashes_by_object = {}
    for row in rows:
        key = (int(row["object_idx"]), row["condition"])
        if key in by_object:
            raise RuntimeError(f"duplicate object/condition row {key}")
        by_object[key] = row
        prior = input_hashes_by_object.setdefault(int(row["object_idx"]), row["input_hashes"])
        if row["input_hashes"] != prior:
            raise RuntimeError(f"shared-input identity mismatch at object index {row['object_idx']}")
        if row["elapsed_seconds"] < 0 or not math.isfinite(float(row["elapsed_seconds"])):
            raise RuntimeError(f"invalid elapsed value at {key}")
    expected = {(obj["object_idx"], condition) for obj in lock["selected_objects"]
                for condition in EXPECTED_PER_OBJECT}
    if set(by_object) != expected:
        raise RuntimeError(f"coverage mismatch missing={len(expected-set(by_object))} extra={len(set(by_object)-expected)}")
    if len(rows) != 174:
        raise RuntimeError(f"generation count {len(rows)} != 174")
    noop_equal = {}
    for obj in lock["selected_objects"]:
        idx = obj["object_idx"]
        base, noop = by_object[(idx, "baseline")], by_object[(idx, "alpha0_noop")]
        noop_equal[str(idx)] = base["output_tensor_sha256"] == noop["output_tensor_sha256"]
        if not noop_equal[str(idx)] or base["input_hashes"] != noop["input_hashes"]:
            raise RuntimeError(f"baseline/no-op exact equality failed for object index {idx}")
    traces = []
    reference_skips = 0
    for row in rows:
        if row["condition"] in {"baseline", "alpha0_noop"}:
            continue
        obj_idx = int(row["object_idx"])
        shard = obj_idx % 2
        group = row["condition"].split("_W", 1)[0]
        expected_active = int(preflights[shard]["group_wrapper_counts"][group]) * 10
        expected_total_calls = expected_active * 2  # reference-write and target-read forward
        if len(row["traces"]) != expected_total_calls:
            raise RuntimeError(f"wrapper-step coverage mismatch for {row['condition']}/{obj_idx}: {len(row['traces'])} != {expected_total_calls}")
        reference_entries = [e for e in row["traces"] if e.get("status") == "reference_pass_skipped_unchanged"]
        if len(reference_entries) != expected_active or any("realized_delta_l2_after_add" in e for e in reference_entries):
            raise RuntimeError(f"reference-write pass changed or incomplete for {row['condition']}/{obj_idx}")
        window = int(row["condition"].split("_W", 1)[1].split("_", 1)[0])
        alpha = float(row["condition"].rsplit("_a", 1)[1])
        adapter_ids = preflights[shard]["group_adapter_indices"][group]
        expected_trace_keys = {(adapter, step) for adapter in adapter_ids
                               for step in range(10 * (window - 1), 10 * window)}
        reference_keys = {(int(e["adapter_idx"]), int(e["step"])) for e in reference_entries}
        if reference_keys != expected_trace_keys:
            raise RuntimeError(f"reference-write wrapper-step keys are incomplete or duplicated for {row['condition']}/{obj_idx}")
        reference_skips += len(reference_entries)
        active_entries = [e for e in row["traces"] if e.get("status") != "reference_pass_skipped_unchanged"]
        if len(active_entries) != expected_active:
            raise RuntimeError(f"target-read wrapper-step coverage mismatch for {row['condition']}/{obj_idx}")
        active_keys = {(int(e["adapter_idx"]), int(e["step"])) for e in active_entries}
        if active_keys != expected_trace_keys:
            raise RuntimeError(f"target-read wrapper-step keys are incomplete or duplicated for {row['condition']}/{obj_idx}")
        expected_scale = float(lock["baseline_scale"][group])
        expected_cap = float(lock["caps"][group])
        for entry in active_entries:
            if entry.get("group") != group or int(entry.get("window", -1)) != window or float(entry.get("alpha", -1)) != alpha:
                raise RuntimeError(f"intervention identity mismatch inside {row['condition']}/{obj_idx}")
            if entry.get("status") == "finite":
                if float(entry["requested_scale"]) != expected_scale or float(entry["effective_scale"]) != min(expected_scale, expected_cap) or float(entry["cap"]) != expected_cap:
                    raise RuntimeError(f"baseline scale/cap mismatch in {row['condition']}/{obj_idx}")
                for value in entry.values():
                    if isinstance(value, (int, float)) and not math.isfinite(float(value)):
                        raise RuntimeError(f"nonfinite trace value in {row['condition']}/{obj_idx}")
        traces.extend(active_entries)
    if not traces:
        raise RuntimeError("no active-wrapper-step traces were recorded")
    groups = {}
    statuses = {}
    for entry in traces:
        key = (entry.get("group"), float(entry.get("alpha", -1)))
        bucket = groups.setdefault(key, [])
        bucket.append(entry)
        status = entry.get("status", "missing_status")
        statuses[status] = statuses.get(status, 0) + 1
        if status == "finite":
            error = float(entry["relative_target_error"])
            if not math.isfinite(error):
                raise RuntimeError("nonfinite relative target error")
    strata = {}
    all_pass = True
    for group in GROUPS:
        for alpha in ALPHAS:
            entries = groups.get((group, alpha), [])
            values = [float(e["relative_target_error"]) for e in entries if e.get("status") == "finite"]
            good = sum(v <= 0.05 for v in values)
            rate = good / len(entries) if entries else 0.0
            strata[f"{group}/alpha={alpha:g}"] = {
                "active_wrapper_steps": len(entries), "finite_steps": len(values), "within_5_percent": good,
                "pass_fraction": rate,
                "median_relative_error": statistics.median(values) if values else None,
                "max_relative_error": max(values) if values else None,
            }
            all_pass &= bool(entries) and rate >= 0.99
    gate = {
        "status": "PASS" if all_pass and all(noop_equal.values()) else "FAIL",
        "development_only": True, "quality_metrics_computed": False,
        "generations": len(rows), "expected_generations": 174,
        "selected_objects": lock["selected_objects"], "alpha0_exact_output_equal": noop_equal,
        "active_wrapper_step_traces": len(traces), "status_counts": statuses,
        "zero_or_infeasible_or_nonfinite_steps": sum(v for k, v in statuses.items()
                                                       if k not in {"finite", "alpha_zero_noop", "reference_pass_skipped_unchanged"}),
        "reference_pass_skips": reference_skips,
        "reference_write_unchanged": True, "strata": strata,
        "interpretation": "technical feasibility only; does not identify a quality effect or validate a dose-independent mechanism",
    }
    out = DATA / "E5_TECHNICAL_GATE.json"
    out.write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))
    if gate["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
