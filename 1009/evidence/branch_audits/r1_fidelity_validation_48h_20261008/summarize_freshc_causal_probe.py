#!/usr/bin/env python3
"""Join the same-input Fresh C No Adapter/GFL/LLH saved RGB comparisons."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np

from recompute_paired_rgb_metrics import load_csv, write_csv
from summarize_fidelity_cohorts import FAVORABLE_DIRECTION, as_float, paired_summary


HERE = Path(__file__).resolve().parent
METRIC_FIELDS = (
    "fg_ciede2000_rgb",
    "fg_psnr_recorded",
    "fg_lpips_recorded",
    "gt_relative_laplacian_error_rgb",
    "signed_mean_delta_a_star",
    "signed_mean_delta_b_star",
    "color_bias_a_magnitude",
    "color_bias_b_magnitude",
)
CONDITION_CONTRASTS = (
    ("GFL_minus_NoAdapter", "GFL", "NoAdapter", "gfl_minus_no_adapter"),
    ("LLH_minus_GFL", "LLH", "GFL", "llh_minus_gfl"),
    ("LLH_minus_NoAdapter", "LLH", "NoAdapter", "llh_minus_no_adapter"),
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=HERE)
    args = ap.parse_args()
    no_adapter_rows = {r["uid"]: r for r in load_csv(args.out_dir / "C_FRESHC_NOADAPTER_GFL_PAIRED_RGB.csv")}
    paired_rows = {r["uid"]: r for r in load_csv(args.out_dir / "A_COHORT_HETEROGENEITY.csv") if r["cohort"] == "FreshC"}
    condition_rows = {r["uid"]: r for r in load_csv(args.out_dir / "C_APPEARANCE_CONDITION_OBJECT_AUDIT.csv")}
    if set(no_adapter_rows) != set(paired_rows) or set(no_adapter_rows) != set(condition_rows) or len(no_adapter_rows) != 300:
        raise ValueError("Fresh C No Adapter/GFL/LLH/condition UID sets differ")

    joined: list[dict[str, Any]] = []
    for uid in sorted(no_adapter_rows, key=lambda u: int(no_adapter_rows[u]["object_idx"])):
        no_gfl, llh_gfl, cond = no_adapter_rows[uid], paired_rows[uid], condition_rows[uid]
        if not no_gfl["all_model_input_hashes_equal"] or not cond["gfl_llh_input_tensor_hashes_equal"]:
            raise ValueError(f"FreshC/{uid}: same-input gate failed")
        if no_gfl["target_tensor_sha256_logged"] != llh_gfl["target_tensor_sha256_logged"]:
            raise ValueError(f"FreshC/{uid}: target tensor identity differs across conditions")
        row: dict[str, Any] = {
            "cohort": "FreshC",
            "uid": uid,
            "object_idx": no_gfl["object_idx"],
            "object_seed": no_gfl["object_seed"],
            "selected_condition_view": cond["selected_condition_view"],
            "condition_source_png_sha256": cond["condition_source_png_sha256_actual"],
            "condition_tensor_sha256": cond["condition_tensor_sha256_manifest"],
            "global_embedding_tensor_sha256": cond["global_embedding_tensor_sha256_expected"],
            "target_tensor_sha256_logged": no_gfl["target_tensor_sha256_logged"],
            "all_model_input_hashes_equal_across_NoAdapter_GFL_LLH": True,
            "checkpoint_sha256": no_gfl["checkpoint_sha256"],
            "runner_sha256": no_gfl["runner_sha256"],
            "config_sha256": no_gfl["config_sha256"],
            "no_adapter_prediction_png": no_gfl["no_adapter_prediction_png"],
            "no_adapter_prediction_sha256": no_gfl["no_adapter_prediction_sha256"],
            "gfl_prediction_png": no_gfl["gfl_prediction_png"],
            "gfl_prediction_sha256": no_gfl["gfl_prediction_sha256"],
            "llh_prediction_png": llh_gfl["llh_prediction_png"],
            "llh_prediction_sha256": llh_gfl["llh_prediction_sha256"],
            "diagnostic_uid_overlap": llh_gfl["diagnostic_uid_overlap"],
        }
        for field in METRIC_FIELDS:
            if field in ("color_bias_a_magnitude", "color_bias_b_magnitude"):
                side = field.split("_")[2]
                na = abs(as_float(no_gfl[f"no_adapter_signed_mean_delta_{side}_star"]))
                gf = abs(as_float(no_gfl[f"gfl_signed_mean_delta_{side}_star"]))
                ll = as_float(llh_gfl[f"llh_color_bias_{side}_magnitude"])
            elif field in ("signed_mean_delta_a_star", "signed_mean_delta_b_star"):
                na = as_float(no_gfl[f"no_adapter_{field}"])
                gf = as_float(no_gfl[f"gfl_{field}"])
                ll = as_float(llh_gfl[f"llh_{field}"])
            else:
                na = as_float(no_gfl[f"no_adapter_{field}"])
                gf = as_float(no_gfl[f"gfl_{field}"])
                ll = as_float(llh_gfl[f"llh_{field}"])
            row[f"no_adapter_{field}"] = na
            row[f"gfl_{field}"] = gf
            row[f"llh_{field}"] = ll
            row[f"delta_gfl_minus_no_adapter_{field}"] = gf - na
            row[f"delta_llh_minus_gfl_{field}"] = ll - gf
            row[f"delta_llh_minus_no_adapter_{field}"] = ll - na
        joined.append(row)

    stat_rows = []
    seed = 20261008
    for contrast, first, second, contrast_key in CONDITION_CONTRASTS:
        for field in METRIC_FIELDS:
            delta_field = f"delta_{contrast_key}_{field}"
            values = np.asarray([as_float(row[delta_field]) for row in joined])
            stats = paired_summary(values, FAVORABLE_DIRECTION.get(field), seed)
            stat_rows.append({
                "scope": "FreshC_same_input_condition_probe_n300",
                "contrast": f"{first}-{second}",
                "metric": field,
                "direction": FAVORABLE_DIRECTION.get(field, "signed/no scalar preference"),
                "bootstrap_seed": seed,
                "data_availability": "complete",
                **stats,
            })
            seed += 1
    write_csv(args.out_dir / "C_CAUSAL_PROBE_RESULTS.csv", joined)
    write_csv(args.out_dir / "C_CAUSAL_PROBE_STATISTICS.csv", stat_rows)
    print(f"paired Fresh C causal-probe rows={len(joined)}; statistic rows={len(stat_rows)}")


if __name__ == "__main__":
    main()
