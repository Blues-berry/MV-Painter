#!/usr/bin/env python3
"""Verify and serialize full model-input-hash equality for paired cohorts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from recompute_paired_rgb_metrics import load_json, load_runner_rows, write_csv


HERE = Path(__file__).resolve().parent
FRESHC = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/runs")
FRESHB = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/formal/campaign_FRESH_CONFIRM_B_20261005")
INPUT_KEYS = ("cond", "target", "normal", "depth", "global_embeds", "init_latent")


def run_metadata(run_dir: Path) -> dict[str, Any]:
    manifest = load_json(run_dir / "run_manifest_shard0.json")
    return {
        "checkpoint_sha256": manifest.get("checkpoint_sha256", ""),
        "runner_sha256": manifest.get("runner_script_sha256", ""),
        "config_sha256": manifest.get("config_sha256", ""),
        "object_list_sha256": manifest.get("object_list_sha256", ""),
    }


def main() -> None:
    c_gfl_dir = FRESHC / "c3_confirmation"
    c_llh_dir = FRESHC / "revision_era_addendum"
    c_gfl = load_runner_rows(c_gfl_dir)
    c_llh = load_runner_rows(c_llh_dir)
    b_dir = FRESHB
    b_rows = load_runner_rows(b_dir)
    pairs = []

    for cohort, gfl_rows, llh_rows, condition_rows, meta_gfl, meta_llh in (
        ("FreshC", c_gfl, c_llh, ("no_adapter", "native_gfl", "layer_llh"), run_metadata(c_gfl_dir), run_metadata(c_llh_dir)),
        ("FreshB", b_rows, b_rows, ("native_gfl", "layer_llh"), run_metadata(b_dir), run_metadata(b_dir)),
    ):
        uids = sorted(uid for uid, cond in (gfl_rows if cohort == "FreshC" else b_rows) if cond == "native_gfl")
        for uid in uids:
            if cohort == "FreshC":
                rows = {
                    "no_adapter": gfl_rows[(uid, "no_adapter")],
                    "native_gfl": gfl_rows[(uid, "native_gfl")],
                    "layer_llh": llh_rows[(uid, "layer_llh")],
                }
            else:
                rows = {
                    "native_gfl": b_rows[(uid, "native_gfl")],
                    "layer_llh": b_rows[(uid, "layer_llh")],
                }
            refs = list(rows.values())
            first_hashes = refs[0]["input_hashes"]
            equal = all(row["input_hashes"] == first_hashes for row in refs[1:])
            if not equal:
                raise ValueError(f"{cohort}/{uid}: model input tensor hashes differ across conditions")
            indices = {int(row["object_idx"]) for row in refs}
            seeds = {int(row["seed_base"]) for row in refs}
            if len(indices) != 1 or len(seeds) != 1:
                raise ValueError(f"{cohort}/{uid}: object index or seed base differs across conditions")
            if meta_gfl != meta_llh:
                raise ValueError(f"{cohort}: GFL/LLH run manifests differ: {meta_gfl} / {meta_llh}")
            out = {
                "cohort": cohort,
                "uid": uid,
                "object_idx": next(iter(indices)),
                "seed_base": next(iter(seeds)),
                "object_seed_policy": "42 + object_idx",
                "condition_set": ";".join(condition_rows),
                "all_condition_input_hashes_equal": True,
                **meta_gfl,
            }
            for key in INPUT_KEYS:
                out[f"input_{key}_sha256"] = first_hashes[key]
            pairs.append(out)

    if sum(row["cohort"] == "FreshC" for row in pairs) != 300 or sum(row["cohort"] == "FreshB" for row in pairs) != 150:
        raise ValueError("Unexpected object count in paired input audit")
    output = HERE / "ALL_COHORT_INPUT_PAIR_AUDIT.csv"
    write_csv(output, pairs)
    print(json.dumps({
        "rows": len(pairs),
        "FreshC_n": sum(row["cohort"] == "FreshC" for row in pairs),
        "FreshB_n": sum(row["cohort"] == "FreshB" for row in pairs),
        "all_model_input_hash_pairs_equal": sum(bool(row["all_condition_input_hashes_equal"]) for row in pairs),
        "input_tensor_fields": list(INPUT_KEYS),
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
