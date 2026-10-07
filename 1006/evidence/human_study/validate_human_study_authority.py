#!/usr/bin/env python3
"""Validate the confirmatory human-study authority chain and gate inputs."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "1006"
HUMAN = PACKAGE / "evidence" / "human_study"
GATES = PACKAGE / "gates"
SOURCE_COMMIT = "f5bad8a1e6ca4265c1823eaa26b2775313de4c96"
SOURCE_DIR = "final/round2/scientific_validation_v3/human_study_results_20261006"
INPUTS = (
    "HUMAN_STUDY_RAW_RESPONSES.csv",
    "HUMAN_STUDY_SLOT_ASSIGNMENT.csv",
    "HUMAN_STUDY_OBJECT_UIDS.csv",
    "HUMAN_STUDY_PAIR_MAPPING.csv",
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    override = json.loads((HUMAN / "HUMAN_STUDY_CLASSIFICATION_OVERRIDE_20261007.json").read_text())
    current = json.loads((HUMAN / "HUMAN_STUDY_CONFIRMATORY_PROVENANCE_20261007.json").read_text())
    historical = json.loads((HUMAN / "HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json").read_text())
    lock = PACKAGE / "evidence" / "protocols" / "HUMAN_STUDY_FINAL_PAIR_LOCK.md"
    result_path = HUMAN / "HUMAN_STUDY_CONFIRMATORY_ENDPOINT_RESULTS_20261007.csv"

    require(override["classification"] == "CONFIRMATORY_HUMAN_PREFERENCE_ANALYSIS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS",
            "Current classification is not confirmatory.")
    require(override["gate_verdict"]["confirmatory_endpoint_analysis"] == "PASS",
            "Endpoint-analysis gate did not pass.")
    require(override["gate_verdict"]["full_protocol_adherence"].startswith("NOT_ESTABLISHED"),
            "Protocol deviations were not retained.")

    lock_hash = sha256(lock.read_bytes())
    require(lock_hash == override["frozen_protocol_sha256"] == current["frozen_pair_lock_sha256"],
            "Frozen protocol hash mismatch.")
    require(current["source_commit"] == historical["source_commit"] == SOURCE_COMMIT,
            "Human response source commit mismatch.")
    for record in override["supersedes_human_classification_records"]:
        rel = record.split(" (")[0]
        require((PACKAGE / rel).is_file(), f"Superseded classification record is missing: {rel}")
    require((HUMAN / override["execution_deviation_audit"].split("/", 2)[-1]).is_file(),
            "Frozen-key execution-deviation audit is missing.")

    for name in INPUTS:
        blob = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{SOURCE_DIR}/{name}"], cwd=ROOT)
        digest = sha256(blob)
        require(digest == current["source_files_sha256"][name], f"Current source hash mismatch: {name}")
        require(digest == historical["source_files_sha256"][name], f"Historical source hash mismatch: {name}")

    endpoints = current["endpoints"]
    with result_path.open(newline="", encoding="utf-8") as f:
        aggregate_rows = list(csv.DictReader(f))
    require(len(endpoints) == len(aggregate_rows) == 8, "Expected all eight endpoints.")
    expected_cells = {(c, q) for c in ("GFL", "GFH", "GC3", "GEN_LINEAR") for q in ("appearance", "texture")}
    require({(r["comparison"], r["question"]) for r in endpoints} == expected_cells,
            "Endpoint provenance does not cover the frozen family.")
    require({(r["comparison"], r["question"]) for r in aggregate_rows} == expected_cells,
            "Aggregate table does not cover the frozen family.")

    by_key = {(r["comparison"], r["question"]): r for r in endpoints}
    historic_by_key = {(r["comparison"], r["question"]): r for r in historical["endpoints"]}
    require(set(historic_by_key) == expected_cells, "Historical analysis snapshot is incomplete.")
    for row in aggregate_rows:
        key = (row["comparison"], row["question"])
        evidence = by_key[key]
        require(int(row["n_valid_participants"]) == 37 and int(row["n_objects"]) == 24 and int(row["n_judgments"]) == 222,
                f"Unexpected sample count for {key}.")
        for field in ("llh_preference_probability", "ci95_low", "ci95_high", "p_unadjusted", "p_holm_8_endpoints"):
            require(float(row[field]) == float(evidence[field]), f"Aggregate/provenance mismatch for {key}, {field}.")
            require(float(evidence[field]) == float(historic_by_key[key][field]),
                    f"Classification update changed a previously computed estimate for {key}, {field}.")
        require(float(row["llh_preference_probability"]) > 0.5, f"Unexpected point-estimate direction for {key}.")
        require(float(row["p_holm_8_endpoints"]) >= 0.05, f"An endpoint passes Holm; verdict text must be reviewed for {key}.")

    rows = current["input_rows"]
    require(rows == {INPUTS[0]: 960, INPUTS[1]: 960, INPUTS[2]: 24, INPUTS[3]: 96},
            "Source input row counts differ from the audited set.")
    checks = current["design_checks"]
    require(checks["all_response_rows_join_to_assignment_and_pair_map"] is True, "Response joins failed.")
    require(checks["valid_participants"] == 37 and checks["object_count"] == 24, "Sample gate failed.")
    require(checks["object_comparison_cells_with_fixed_left_right_orientation_across_participants"] == 96,
            "Recorded side-order deviation changed.")

    schedule = historical["design_checks"]["frozen_assignment_schedule_audit"]
    require(schedule["available"] is True, "Prior frozen-key schedule audit is unavailable.")
    require(schedule["same_numeric_slot_schedule_matches"] == 0 and schedule["uploaded_schedule_matches_any_frozen_slot"] == 0,
            "Recorded frozen-key schedule deviation changed.")
    require(current["design_checks"]["frozen_assignment_schedule_audit"]["available"] is False,
            "Current endpoint provenance must not imply access to the private key.")

    referenced = [
        HUMAN / "HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md",
        HUMAN / "HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md",
        GATES / "HUMAN_STUDY_GATE_VERDICT_20261007.md",
        GATES / "SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md",
        GATES / "FINAL_READINESS_VERDICT_20261007.md",
    ]
    require(all(p.is_file() for p in referenced), "A current human-evidence/gate authority file is missing.")
    disposition = (HUMAN / "HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md").read_text()
    gate = (GATES / "HUMAN_STUDY_GATE_VERDICT_20261007.md").read_text()
    receipt = (HUMAN / "HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md").read_text()
    freeze = (GATES / "SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md").read_text()
    require("确认性人评端点分析" in disposition and "`HUMAN_CONFIRMATORY_ENDPOINT_ANALYSIS = PASS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS`" in gate,
            "Current human disposition or gate verdict is inconsistent.")
    require("现行裁决" in receipt and "当前按预先指定的八端点作确认性分析" in receipt,
            "Historical receipt report does not label its sensitivity status as superseded.")
    require("`HUMAN_CONFIRMATORY_ENDPOINT_ANALYSIS = PASS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS`" in freeze,
            "Scientific freeze verdict does not inherit the human gate.")

    validation = {
        "validation_id": "HUMAN_STUDY_AUTHORITY_GATE_20261007",
        "classification": override["classification"],
        "gate_status": "PASS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS",
        "checks": {
            "source_commit_and_four_input_hashes": "PASS",
            "frozen_protocol_hash": "PASS",
            "960_response_row_joins_and_24_object_map": "PASS",
            "37_valid_participants_meet_36_minimum": "PASS",
            "eight_frozen_endpoints_and_holm_family": "PASS",
            "aggregate_csv_matches_endpoint_provenance": "PASS",
            "all_holm_adjusted_p_values_at_least_0_05": "PASS",
            "classification_update_did_not_change_endpoint_estimates": "PASS",
            "frozen_assignment_deviation_carried_from_hashed_prior_audit": "PASS",
            "new_endpoint_analyzer_does_not_claim_private_key_access": "PASS",
            "current_disposition_and_gates_consistent": "PASS",
        },
        "protocol_conformance": "DEVIATIONS_RECORDED; FULL_ADHERENCE_NOT_ESTABLISHED",
        "separate_open_gates": ["consent_ethics_documentation", "participant_data_governance", "continued_public_availability_review"],
    }
    out = HUMAN / "HUMAN_STUDY_GATE_VALIDATION_20261007.json"
    out.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
