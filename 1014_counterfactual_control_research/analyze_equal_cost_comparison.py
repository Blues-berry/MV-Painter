#!/usr/bin/env python3
"""Compare two-call view-action feedback with two-call fixed-mean selection."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
ALT_GEN = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/generation_equal_cost_b0_seed43")
ALT_BAKE = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/bake_equal_cost_b0_seed43")
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def mean_ci(values: list[float]) -> tuple[float, float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(20261013)
    samples = rng.choice(x, size=(100_000, len(x)), replace=True).mean(axis=1)
    lo, hi = np.quantile(samples, [0.025, 0.975])
    return float(x.mean()), float(lo), float(hi)


def main() -> None:
    original_gen_rows = read_rows(ROOT / "generation/GENERATION_VIEW_METRICS.csv")
    alternate_gen_rows = read_rows(ALT_GEN / "GENERATION_VIEW_METRICS.csv")
    action_summary = json.loads((ROOT / "ACTION_RESPONSE_SUMMARY.json").read_text())
    original_bake_rows = read_rows(ROOT / "bake/native_egl_unseen/NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv")
    alternate_bake_rows = read_rows(ALT_BAKE / "native_egl_unseen/NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv")

    original_ref = {r["object_uid"]: r for r in original_gen_rows
                    if r["condition"] == "counterfactual_b0" and r["slot"] == "0"}
    alternate_ref = {r["object_uid"]: r for r in alternate_gen_rows if r["slot"] == "0"}
    bake_lpips = {(r["object_uid"], r["method"]): float(r["fg_lpips"])
                  for r in original_bake_rows}
    alternate_fixed_bake = {r["object_uid"]: float(r["fg_lpips"])
                            for r in alternate_bake_rows
                            if r["method"] == "counterfactual_b0_seed43"}
    action_conditions = action_summary["two_candidate_selection"]
    per_action = {}
    for metric, key in (("mae", "mae_selected_conditions"), ("ciede2000", "ciede_selected_conditions")):
        per_action[metric] = action_conditions[key]

    out_rows = []
    for uid in UIDS:
        r42, r43 = original_ref[uid], alternate_ref[uid]
        choices = {}
        for metric, field42, field43 in (
            ("mae", "fg_rgb_mae", "reference_rgb_mae"),
            ("ciede2000", "ciede2000", "reference_ciede2000"),
        ):
            choices[metric] = "seed42" if float(r42[field42]) <= float(r43[field43]) else "seed43"
        chosen_seed = choices["mae"]
        fixed2_lpips = bake_lpips[(uid, "counterfactual_b0")] if chosen_seed == "seed42" else alternate_fixed_bake[uid]
        row = {
            "object_uid": uid,
            "seed42_reference_mae": float(r42["fg_rgb_mae"]),
            "seed43_reference_mae": float(r43["reference_rgb_mae"]),
            "seed42_reference_ciede2000": float(r42["ciede2000"]),
            "seed43_reference_ciede2000": float(r43["reference_ciede2000"]),
            "fixed_mean_mae_selected_seed": choices["mae"],
            "fixed_mean_ciede_selected_seed": choices["ciede2000"],
            "fixed_mean_two_call_selected_bake_lpips": fixed2_lpips,
            "fixed_mean_seed42_bake_lpips": bake_lpips[(uid, "counterfactual_b0")],
            "fixed_mean_seed43_bake_lpips": alternate_fixed_bake[uid],
            "action_mae_selected_condition": per_action["mae"][uid],
            "action_mae_selected_bake_lpips": bake_lpips[(uid, per_action["mae"][uid])],
            "action_ciede_selected_condition": per_action["ciede2000"][uid],
        }
        selected_condition = per_action["ciede2000"][uid]
        row["action_ciede_selected_bake_lpips"] = bake_lpips[(uid, selected_condition)]
        row["action_mae_minus_fixed_mean_two_call_lpips"] = (
            row["action_mae_selected_bake_lpips"] - fixed2_lpips
        )
        row["action_ciede_minus_fixed_mean_two_call_lpips"] = (
            row["action_ciede_selected_bake_lpips"] - fixed2_lpips
        )
        out_rows.append(row)

    output_csv = ROOT / "EQUAL_COST_CANDIDATE_SELECTION_RESULTS.csv"
    with output_csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)

    fixed2 = [r["fixed_mean_two_call_selected_bake_lpips"] for r in out_rows]
    action_mae = [r["action_mae_selected_bake_lpips"] for r in out_rows]
    action_ciede = [r["action_ciede_selected_bake_lpips"] for r in out_rows]
    summary = {
        "status": "COMPLETE_EXPLORATORY_EQUAL_CALL_COMPARISON",
        "objects_as_analysis_units": len(out_rows),
        "per_object_generation_calls": {"view_action_feedback": 2, "fixed_mean_candidate_selection": 2},
        "fixed_mean_candidates": ["latent_seed_42", "latent_seed_43"],
        "fixed_mean_seed43_input_hashes_equal_to_seed42_except_initial_latent": True,
        "selected_fixed_mean_seed_by_reference_signal": {
            "rgb_mae": {r["object_uid"]: r["fixed_mean_mae_selected_seed"] for r in out_rows},
            "ciede2000": {r["object_uid"]: r["fixed_mean_ciede_selected_seed"] for r in out_rows},
        },
        "mean_object_bake_lpips": {
            "fixed_mean_two_call_mae_selected": mean_ci(fixed2),
            "view_action_two_call_mae_selected": mean_ci(action_mae),
            "view_action_two_call_ciede_selected": mean_ci(action_ciede),
        },
        "paired_action_minus_fixed_mean_two_call": {
            "rgb_mae": mean_ci([r["action_mae_minus_fixed_mean_two_call_lpips"] for r in out_rows]),
            "ciede2000": mean_ci([r["action_ciede_minus_fixed_mean_two_call_lpips"] for r in out_rows]),
        },
        "action_beats_fixed_mean_two_call": {
            "rgb_mae": sum(r["action_mae_minus_fixed_mean_two_call_lpips"] < 0 for r in out_rows),
            "ciede2000": sum(r["action_ciede_minus_fixed_mean_two_call_lpips"] < 0 for r in out_rows),
            "n": len(out_rows),
        },
        "interpretation": "Both policies use two full trajectories and choose by the same legal reference metrics. Fixed Mean candidate selection is a simple no-view-budget-control best-of-two baseline.",
        "result_csv": str(output_csv),
    }
    (ROOT / "EQUAL_COST_CANDIDATE_SELECTION_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
