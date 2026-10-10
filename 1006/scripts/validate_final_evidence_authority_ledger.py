#!/usr/bin/env python3
"""Validate the final condition-level authority ledger and image-space packet."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261007.json"
AUDIT_OUT = ROOT / "1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_VALIDATION_20261007.json"
DATA = ROOT / "1006/data/fresh_c"
GALLERY = ROOT / "1006/figures/strategy_comparison_gallery/fresh_c_final"
REQUIRED_FIELDS = {
    "run_id", "canonical_condition_name", "historical_aliases",
    "requested_scale_profile", "actually_applied_scale_cap_trace",
    "realized_residual_measurement", "cohort", "n_objects", "seed_policy",
    "checkpoint", "runner_commit_provenance", "input_conditioning_provenance",
    "output_provenance", "metric_implementation_version",
    "protocol_freeze_time_utc", "outcome_exposure_time_utc",
    "outcome_exposure_time_status", "evidence_class", "allowed_claim",
    "prohibited_claim", "superseded_artifacts", "source_artifacts",
}
FRESH_C_CONDITIONS = {
    "1006/data/fresh_c/runs/c3_confirmation":
        {"no_adapter", "native_gfl", "native_gfh", "native_gc3"},
    "1006/data/fresh_c/runs/revision_era_addendum":
        {"layer_llh", "gen_linear"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_path(value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else ROOT / candidate


def check_nested_sources(value: Any, errors: list[str], checked: set[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        path_value = value.get("path")
        expected = value.get("sha256")
        availability = value.get("availability")
        if isinstance(path_value, str) and isinstance(expected, str):
            key = (path_value, expected)
            if key not in checked:
                checked.add(key)
                path = resolve_path(path_value)
                if not path.is_file():
                    errors.append(f"hash-addressed source missing: {path_value}")
                elif sha256(path) != expected:
                    errors.append(f"hash mismatch: {path_value}")
        elif availability == "present" and isinstance(path_value, str):
            errors.append(f"source marked present without SHA-256: {path_value}")
        elif availability == "not recorded or absent" and expected is not None:
            errors.append(f"absent/unrecorded source has a hash: {path_value}")
        for child in value.values():
            check_nested_sources(child, errors, checked)
    elif isinstance(value, list):
        for child in value:
            check_nested_sources(child, errors, checked)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"required file missing: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    ledger = load_json(LEDGER, errors)
    records = ledger.get("condition_records", [])
    if ledger.get("authority_status") != "CANONICAL_RUN_INDEX_WITH_EXPLICIT_PROVENANCE_GAPS":
        errors.append("unexpected authority status")
    if ledger.get("scientific_evidence_freeze") != "YES_BOUNDED_CLAIMS":
        errors.append("current ledger must record scientific_evidence_freeze=YES_BOUNDED_CLAIMS")
    if len(records) != ledger.get("run_condition_record_count"):
        errors.append("condition record count does not match ledger declaration")
    if ledger.get("run_count") != 26 or len(records) != 243:
        errors.append(f"expected 26 runs/243 records, got {ledger.get('run_count')}/{len(records)}")

    run_conditions: dict[str, set[str]] = {}
    for index, record in enumerate(records):
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"condition record {index} missing fields: {sorted(missing)}")
        run_id = record.get("run_id")
        condition = record.get("canonical_condition_name")
        if not run_id or not condition:
            errors.append(f"condition record {index} has no run/condition identity")
            continue
        run_conditions.setdefault(run_id, set()).add(condition)
        if not record.get("allowed_claim") or not record.get("prohibited_claim"):
            errors.append(f"{run_id}/{condition} lacks claim boundaries")
        if record.get("outcome_exposure_time_utc") is None and not record.get("outcome_exposure_time_status"):
            errors.append(f"{run_id}/{condition} has an unexplained null exposure time")
    for run_id, expected in FRESH_C_CONDITIONS.items():
        if run_conditions.get(run_id) != expected:
            errors.append(f"Fresh C condition set mismatch for {run_id}: {run_conditions.get(run_id)}")
    fresh_records = [r for r in records if r.get("run_id") in FRESH_C_CONDITIONS]
    if len(fresh_records) != 6 or any(r.get("n_objects") != 300 for r in fresh_records):
        errors.append("Fresh C primary/addendum must contain six N=300 condition records")

    primary_gate = load_json(DATA / "FRESH_C_INTEGRITY_GATE.json", errors)
    addendum_gate = load_json(DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json", errors)
    primary_analysis = load_json(DATA / "fresh_c_c3_minus_gfl_analysis.json", errors)
    addendum_analysis = load_json(DATA / "FRESH_C_ADDENDUM_ANALYSIS.json", errors)
    sign_audit = load_json(DATA / "FRESH_C_RESULT_DIRECTION_AUDIT.json", errors)
    cohort = load_json(DATA / "FRESH_C_COHORT_MANIFEST.json", errors)
    if primary_gate.get("status") != "PASS" or primary_gate.get("verified_rows") != 1200:
        errors.append("Fresh C primary integrity is not PASS at 1200 rows")
    if addendum_gate.get("status") != "PASS" or addendum_gate.get("verified_rows") != 600:
        errors.append("Fresh C addendum integrity is not PASS at 600 rows")
    if primary_analysis.get("n_objects") != 300 or len(primary_analysis.get("tests", {})) != 7:
        errors.append("Fresh C primary analysis is incomplete")
    if addendum_analysis.get("n_objects") != 300 or len(addendum_analysis.get("tests", [])) != 21:
        errors.append("Fresh C addendum analysis is incomplete")
    checks = sign_audit.get("independent_checks", [])
    if sign_audit.get("status") != "PASS" or len(checks) != 28 or sign_audit.get("errors"):
        errors.append("Fresh C direction/sign audit is not PASS for all 28 checks")
    if sign_audit.get("sign_direction_error") != "0":
        errors.append("SIGN_DIRECTION_ERROR must equal 0")
    if sign_audit.get("row_sources", {}).get("primary_analysis_sha256") != sha256(DATA / "fresh_c_c3_minus_gfl_analysis.json"):
        errors.append("direction audit primary analysis hash is stale")
    if sign_audit.get("row_sources", {}).get("addendum_analysis_sha256") != sha256(DATA / "FRESH_C_ADDENDUM_ANALYSIS.json"):
        errors.append("direction audit addendum analysis hash is stale")
    if cohort.get("status") != "FROZEN_FRESH_C_300" or cohort.get("selected_count") != 300:
        errors.append("Fresh C cohort manifest is not the frozen N=300 manifest")

    gallery_manifest = load_json(GALLERY / "gallery_manifest.json", errors)
    selected = gallery_manifest.get("selected_groups", [])
    group_uids = [group.get("object_uid") for group in selected]
    focal_counts: dict[str, int] = {}
    for group in selected:
        focal_counts[group.get("focal_contrast", "")] = focal_counts.get(group.get("focal_contrast", ""), 0) + 1
        if group.get("per_object_significance") != "not estimated":
            errors.append("gallery contains a per-object significance assertion")
    if len(selected) != 20 or len(set(group_uids)) != 20:
        errors.append("gallery must contain 20 unique object groups")
    if focal_counts != {"C3-GFL": 5, "LLH-C3": 5, "LLH-linear": 5, "C3-linear": 5}:
        errors.append(f"gallery balance mismatch: {focal_counts}")
    if len(gallery_manifest.get("conditions", [])) != 7:
        errors.append("gallery must include shared reference plus all six strategies")

    index_meta = load_json(GALLERY / "six_method_complete_object_index.json", errors)
    index_csv = GALLERY / "six_method_complete_object_index.csv"
    if index_meta.get("status") != "PASS" or index_meta.get("n_objects") != 300 or index_meta.get("rows") != 1800:
        errors.append("six-method object index manifest is incomplete")
    if not index_csv.is_file():
        errors.append("six-method complete object index CSV missing")
    else:
        with index_csv.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != 1800:
            errors.append(f"six-method index has {len(rows)} rows, expected 1800")
        if sha256(index_csv) != index_meta.get("output_sha256"):
            errors.append("six-method index hash mismatch")
        methods = {row.get("condition") for row in rows}
        if methods != {"native_gfl", "native_gfh", "no_adapter", "native_gc3", "layer_llh", "gen_linear"}:
            errors.append(f"six-method index method set mismatch: {methods}")

    manuscript_policy = ledger.get("manuscript_policy", {})
    if manuscript_policy.get("do_not_edit_01549_until_scientific_evidence_freeze") is not True:
        errors.append("manuscript freeze policy changed")

    # Recheck only hash-addressed source objects in the ledger. Repeated references are deduplicated.
    checked_sources: set[tuple[str, str]] = set()
    check_nested_sources(ledger, errors, checked_sources)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "validated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ledger_sha256": sha256(LEDGER) if LEDGER.is_file() else None,
        "run_count": ledger.get("run_count"),
        "condition_record_count": len(records),
        "hash_addressed_sources_checked": len(checked_sources),
        "fresh_c_primary_rows": primary_gate.get("verified_rows"),
        "fresh_c_addendum_rows": addendum_gate.get("verified_rows"),
        "direction_checks": len(checks),
        "sign_direction_error": sign_audit.get("sign_direction_error"),
        "gallery_groups": len(selected),
        "six_method_index_rows": index_meta.get("rows"),
        "scientific_evidence_freeze": ledger.get("scientific_evidence_freeze"),
        "errors": errors,
    }
    AUDIT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
