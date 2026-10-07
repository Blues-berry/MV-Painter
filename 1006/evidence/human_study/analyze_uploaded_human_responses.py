#!/usr/bin/env python3
"""Historical first-pass analysis of the uploaded human-response export.

The sensitivity-only classification emitted by this script on 2026-10-06 was
superseded on 2026-10-07 after the study owner confirmed the confirmatory
endpoint family. The row checks, numeric estimates, and execution-deviation
audit remain archival evidence; this script's classification/status output is
not current authority. Use ``analyze_confirmatory_human_study_20261007.py``
and ``validate_human_study_authority.py`` for current analysis and gate status.

This script deliberately does not modify or call the frozen coordinator
analyzer. It reads the exact Git commit named below and applies the locked
equal-object, two-way participant/object bootstrap estimator to the re-keyed
export.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE_COMMIT = "f5bad8a1e6ca4265c1823eaa26b2775313de4c96"
SOURCE_DIR = "final/round2/scientific_validation_v3/human_study_results_20261006"
BOOTSTRAPS = 10_000
BOOT_SEED = 20261005
MIN_VALID = 36
COMPARISONS = ("GFL", "GFH", "GC3", "GEN_LINEAR")
QUESTIONS = (("appearance", "q1_fidelity"), ("texture", "q2_naturalness"))


def git_blob(commit: str, relpath: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{relpath}"], cwd=ROOT)


def parse_csv(blob: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def normalized_label(value: str) -> str:
    return value.strip().upper().replace("-", "_")


def holm(p_values: list[float]) -> list[float]:
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def estimate(matrix: np.ndarray, rng: np.random.Generator) -> dict[str, float]:
    point = float(np.nanmean(matrix, axis=0).mean())
    n_people, n_objects = matrix.shape
    draws = np.empty(BOOTSTRAPS, dtype=float)
    made = attempts = 0
    while made < BOOTSTRAPS:
        attempts += 1
        if attempts > BOOTSTRAPS * 5:
            raise RuntimeError("Too many empty participant/object bootstrap draws.")
        people = rng.integers(0, n_people, size=n_people)
        objects = rng.integers(0, n_objects, size=n_objects)
        sampled = matrix[np.ix_(people, objects)]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            means = np.nanmean(sampled, axis=0)
        if np.isnan(means).any():
            continue
        draws[made] = means.mean()
        made += 1
    low, high = np.quantile(draws, [0.025, 0.975])
    extreme = np.count_nonzero(np.abs(draws - point) >= abs(point - 0.5))
    p = (int(extreme) + 1) / (BOOTSTRAPS + 1)
    return {"estimate": point, "ci_low": float(low), "ci_high": float(high), "p_raw": float(p)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", default=SOURCE_COMMIT)
    args = parser.parse_args()
    input_names = (
        "HUMAN_STUDY_RAW_RESPONSES.csv",
        "HUMAN_STUDY_SLOT_ASSIGNMENT.csv",
        "HUMAN_STUDY_OBJECT_UIDS.csv",
        "HUMAN_STUDY_PAIR_MAPPING.csv",
    )
    blobs = {name: git_blob(args.source_commit, f"{SOURCE_DIR}/{name}") for name in input_names}
    raw = parse_csv(blobs[input_names[0]])
    assignments = parse_csv(blobs[input_names[1]])
    object_rows = parse_csv(blobs[input_names[2]])
    pair_rows = parse_csv(blobs[input_names[3]])

    if not all((raw, assignments, object_rows, pair_rows)):
        raise ValueError("One or more frozen input tables are empty.")
    uid_by_object = {r["object_id"]: r["frozen_object_uid"] for r in object_rows}
    if len(uid_by_object) != 24 or len(set(uid_by_object.values())) != 24:
        raise ValueError("Object map must contain 24 unique object/UID rows.")
    if len(raw) != 40 * 24 or len(assignments) != 40 * 24 or len(pair_rows) != 24 * 4:
        raise ValueError("Input row counts differ from the frozen 40x24 / 24x4 design.")

    pair_by_id = {r["pair_id"]: r for r in pair_rows}
    if len(pair_by_id) != len(pair_rows):
        raise ValueError("Pair mapping contains duplicate pair IDs.")
    for row in pair_rows:
        comp = normalized_label(row["comparator"])
        methods = {normalized_label(row["left_method"]), normalized_label(row["right_method"])}
        if comp not in COMPARISONS or "LLH" not in methods or len(methods) != 2:
            raise ValueError("Pair mapping contains a method pair outside the lock.")
        if methods != {"LLH", comp}:
            raise ValueError("Pair mapping method labels disagree with the locked comparison.")

    assignment_by_task = {(r["participant_id"], r["slot_id"], r["trial_id"]): r for r in assignments}
    if len(assignment_by_task) != len(assignments):
        raise ValueError("Assignment table has duplicate participant/slot/trial keys.")
    object_pair_exposure = Counter()
    orientation_by_cell = defaultdict(set)
    participants = defaultdict(list)
    for row in raw:
        pair = pair_by_id.get(row["pair_id"])
        assignment = assignment_by_task.get((row["participant_id"], row["slot_id"], row["trial_id"]))
        if pair is None or assignment is None:
            raise ValueError("A response row cannot be joined to both frozen source maps.")
        comp = normalized_label(pair["comparator"])
        if (row["object_id"] != pair["object_id"] or
                row["left_stimulus_id"] != pair["left_stimulus_id"] or
                row["right_stimulus_id"] != pair["right_stimulus_id"] or
                assignment["object_id"] != row["object_id"] or
                normalized_label(assignment["comparator"]) != comp):
            raise ValueError("Response, assignment and pair-map rows disagree.")
        if row["object_id"] not in uid_by_object:
            raise ValueError("Response object is absent from the UID table.")
        if row["q1_fidelity"] not in {"LEFT", "RIGHT", "TIE", ""}:
            raise ValueError("Invalid appearance choice code.")
        if row["q2_naturalness"] not in {"LEFT", "RIGHT", "TIE", ""}:
            raise ValueError("Invalid texture choice code.")
        if row["completed"] not in {"0", "1"} or row["comprehension_pass"] not in {"0", "1"}:
            raise ValueError("Completion/comprehension flags must be binary.")
        participants[row["participant_id"]].append(row)
        object_pair_exposure[(row["object_id"], comp)] += 1
        orientation_by_cell[(row["object_id"], comp)].add(
            (row["left_stimulus_id"], row["right_stimulus_id"])
        )

    if len(participants) != 40 or len({r["slot_id"] for r in raw}) != 40:
        raise ValueError("The export must represent all 40 assigned participant slots.")
    if set(normalized_label(r["comparator"]) for r in assignments) != set(COMPARISONS):
        raise ValueError("Assignment file does not contain all four locked comparisons.")
    for participant_id, rows in participants.items():
        if len(rows) != 24 or len({r["trial_id"] for r in rows}) != 24:
            raise ValueError("Participant row count or unique trial count is not 24.")
        if len({r["object_id"] for r in rows}) != 24:
            raise ValueError("Participant does not see 24 unique objects.")
        if Counter(normalized_label(pair_by_id[r["pair_id"]]["comparator"]) for r in rows) != Counter({c: 6 for c in COMPARISONS}):
            raise ValueError("Participant is not balanced at six trials per comparison.")
    if len(object_pair_exposure) != 96 or set(object_pair_exposure.values()) != {10}:
        raise ValueError("Each object/comparison cell must be assigned exactly ten times.")

    valid = []
    exclusion_counts = Counter()
    for participant_id, rows in participants.items():
        complete = all(r["completed"] == "1" and r["q1_fidelity"] and r["q2_naturalness"] for r in rows)
        comprehension = all(r["comprehension_pass"] == "1" for r in rows)
        if not complete:
            exclusion_counts["incomplete_or_missing_choice"] += 1
        if not comprehension:
            exclusion_counts["failed_comprehension_check"] += 1
        if complete and comprehension:
            valid.append((participant_id, rows))
    if len(valid) < MIN_VALID:
        raise ValueError(f"Only {len(valid)} valid respondents; frozen minimum is {MIN_VALID}.")

    object_ids = sorted(uid_by_object, key=lambda oid: uid_by_object[oid])
    object_index = {oid: i for i, oid in enumerate(object_ids)}
    pair_method = {
        pid: (row["left_method"], row["right_method"]) for pid, row in pair_by_id.items()
    }
    rng = np.random.default_rng(BOOT_SEED)
    endpoint_rows = []
    for comparison in COMPARISONS:
        for question_name, field in QUESTIONS:
            matrix = np.full((len(valid), len(object_ids)), np.nan, dtype=float)
            raw_counts = Counter()
            exposure = Counter()
            for pi, (_, rows) in enumerate(valid):
                for row in rows:
                    pair = pair_by_id[row["pair_id"]]
                    if normalized_label(pair["comparator"]) != comparison:
                        continue
                    answer = row[field]
                    raw_counts[answer] += 1
                    exposure[row["object_id"]] += 1
                    if answer == "TIE":
                        score = 0.5
                    else:
                        selected_method = pair_method[row["pair_id"]][0 if answer == "LEFT" else 1]
                        score = float(normalized_label(selected_method) == "LLH")
                    matrix[pi, object_index[row["object_id"]]] = score
            if np.isnan(matrix).all(axis=0).any():
                raise ValueError("At least one frozen object lacks a valid judgment for an endpoint.")
            result = estimate(matrix, rng)
            object_means = np.nanmean(matrix, axis=0)
            endpoint_rows.append({
                "comparison": comparison,
                "question": question_name,
                "n_valid_participants": len(valid),
                "n_objects": len(object_ids),
                "n_judgments": int(np.isfinite(matrix).sum()),
                "llh_choice_count": int(sum(
                    1 for _, rows in valid for row in rows
                    if normalized_label(pair_by_id[row["pair_id"]]["comparator"]) == comparison
                    and row[field] != "TIE"
                    and normalized_label(pair_method[row["pair_id"]][0 if row[field] == "LEFT" else 1]) == "LLH"
                )),
                "comparator_choice_count": int(sum(
                    1 for _, rows in valid for row in rows
                    if normalized_label(pair_by_id[row["pair_id"]]["comparator"]) == comparison
                    and row[field] != "TIE"
                    and normalized_label(pair_method[row["pair_id"]][0 if row[field] == "LEFT" else 1]) != "LLH"
                )),
                "tie_count": int(raw_counts["TIE"]),
                "llh_preference_probability": result["estimate"],
                "ci95_low": result["ci_low"],
                "ci95_high": result["ci_high"],
                "p_unadjusted": result["p_raw"],
                "median_object_share": float(np.median(object_means)),
                "fraction_objects_llh_share_gt_0_5": float(np.mean(object_means > 0.5)),
                "direction_vs_0_5": "LLH_higher" if result["estimate"] > 0.5 else "comparator_higher" if result["estimate"] < 0.5 else "equal",
            })
    adjusted = holm([r["p_unadjusted"] for r in endpoint_rows])
    for row, p_adjusted in zip(endpoint_rows, adjusted):
        row["p_holm_8_endpoints"] = p_adjusted

    side_by_comparison = {}
    for comparison in COMPARISONS:
        sides = Counter()
        for pair in pair_rows:
            if normalized_label(pair["comparator"]) != comparison:
                continue
            sides["LLH_left" if normalized_label(pair["left_method"]) == "LLH" else "LLH_right"] += 1
        side_by_comparison[comparison] = dict(sides)

    result_csv = OUT / "HUMAN_STUDY_ENDPOINT_RESULTS_20261006.csv"
    fields = list(endpoint_rows[0])
    with result_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(endpoint_rows)

    source_hashes = {name: digest(blob) for name, blob in blobs.items()}
    lock_blob = git_blob(args.source_commit, "final/round2/scientific_validation_v3/HUMAN_STUDY_FINAL_PAIR_LOCK.md")
    frozen_schedule_audit = {"available": False}
    private_key_path = ROOT / "final/round2/scientific_validation_v3/human_study_site/coordinator_private/blinded_key.json"
    if private_key_path.is_file():
        private_bytes = private_key_path.read_bytes()
        private_key = json.loads(private_bytes)
        expected_by_slot = {
            str(assignment["slot"]): {
                (private_key["tasks"][t["task_id"]]["uid"], normalized_label(private_key["tasks"][t["task_id"]]["comparison"]))
                for t in assignment["trials"]
            }
            for assignment in private_key["participant_assignments"].values()
        }
        observed_by_slot = defaultdict(set)
        for row in assignments:
            slot = row["slot_id"]
            if slot.startswith("S") and slot[1:].isdigit():
                slot = str(int(slot[1:]))
            observed_by_slot[slot].add((uid_by_object[row["object_id"]], normalized_label(row["comparator"])))
        same_slot_matches = sum(observed_by_slot.get(slot) == cells for slot, cells in expected_by_slot.items())
        any_slot_matches = sum(any(cells == expected for expected in expected_by_slot.values()) for cells in observed_by_slot.values())
        frozen_schedule_audit = {
            "available": True,
            "private_key_sha256": digest(private_bytes),
            "same_numeric_slot_schedule_matches": same_slot_matches,
            "uploaded_schedule_matches_any_frozen_slot": any_slot_matches,
            "interpretation": "Slot task assignments do not reproduce the frozen package schedule; anonymized IDs alone cannot explain this mismatch.",
        }

    manifest = {
        "classification": "PROTOCOL_DEVIATION_SENSITIVITY_ANALYSIS_NOT_CONFIRMATORY",
        "source_commit": args.source_commit,
        "source_files_sha256": source_hashes,
        "frozen_pair_lock_sha256": digest(lock_blob),
        "input_rows": {input_names[0]: len(raw), input_names[1]: len(assignments), input_names[2]: len(object_rows), input_names[3]: len(pair_rows)},
        "design_checks": {
            "participants": len(participants),
            "represented_slots": len({r["slot_id"] for r in raw}),
            "valid_participants": len(valid),
            "excluded_participants_by_reason": dict(exclusion_counts),
            "object_count": len(object_ids),
            "each_participant_has_24_unique_objects_and_6_per_comparison": True,
            "each_object_comparison_cell_has_10_assignments": True,
            "all_response_rows_join_to_assignment_and_pair_map": True,
            "object_comparison_cells_with_fixed_left_right_orientation_across_participants": sum(len(v) == 1 for v in orientation_by_cell.values()),
            "object_comparison_cells_total": len(orientation_by_cell),
            "question_order_recorded": False,
            "randomization_seed_recorded": False,
            "raw_comprehension_answer_recorded": False,
            "frozen_stimulus_asset_hash_crosswalk_provided": False,
            "frozen_assignment_schedule_audit": frozen_schedule_audit,
        },
        "llh_left_right_cell_balance": side_by_comparison,
        "analysis": {
            "score": "LLH choice=1, comparator choice=0, tie=0.5; object means equally weighted",
            "bootstrap": "two-way participant/object cluster bootstrap, 10,000 resamples, seed 20261005",
            "ci": "pointwise 95% percentile intervals",
            "test": "frozen two-sided tail rule with plus-one correction against 0.5",
            "multiplicity": "Holm across all eight comparison-by-question endpoints",
            "status": "Sensitivity analysis; output cannot close confirmatory human-fidelity gate because exact frozen assignments/stimulus assets are not verified.",
        },
        "endpoints": endpoint_rows,
    }
    (OUT / "HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        labels = [f"{r['comparison']} · {r['question']}" for r in endpoint_rows]
        y = np.arange(len(endpoint_rows))
        x = np.array([r["llh_preference_probability"] for r in endpoint_rows])
        lo = np.array([r["ci95_low"] for r in endpoint_rows])
        hi = np.array([r["ci95_high"] for r in endpoint_rows])
        fig, ax = plt.subplots(figsize=(8.8, 5.2), constrained_layout=True)
        ax.errorbar(x, y, xerr=[x - lo, hi - x], fmt="o", color="#24536b", ecolor="#7894a3", capsize=3)
        ax.axvline(0.5, color="#555555", linestyle="--", linewidth=1)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_xlim(0.2, 0.8)
        ax.set_xlabel("Equal-object LLH preference probability (ties = 0.5)")
        ax.set_title("Protocol-deviation sensitivity analysis · not confirmatory")
        ax.grid(axis="x", alpha=0.2)
        fig.savefig(OUT / "HUMAN_STUDY_SENSITIVITY_FORESTPLOT_20261006.png", dpi=180)
        plt.close(fig)
    except ImportError:
        pass

    print(json.dumps({
        "classification": manifest["classification"],
        "n_valid": len(valid),
        "exclusions": dict(exclusion_counts),
        "outputs": [str(result_csv), str(OUT / "HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json")],
        "endpoint_results": endpoint_rows,
    }, indent=2))


if __name__ == "__main__":
    main()
