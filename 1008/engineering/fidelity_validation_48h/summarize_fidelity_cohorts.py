#!/usr/bin/env python3
"""Build UID-paired cohort tables, statistics, complexity strata, and log summaries."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from recompute_paired_rgb_metrics import load_csv, write_csv


HERE = Path(__file__).resolve().parent
DIAGNOSTIC_RESULTS = Path(
    "/4T/CXY/MV-Painter-r1color/1008/engineering/color_failure/final_closure/"
    "COLOR_FIDELITY_PAIRED_RESULTS.csv"
)
FRESHC_RUN_ROOT = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/runs")
FRESHB_RUN_ROOT = Path(
    "/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/formal/"
    "campaign_FRESH_CONFIRM_B_20261005"
)

PAIR_FIELDS = (
    "fg_ciede2000_rgb",
    "fg_psnr_recorded",
    "fg_lpips_recorded",
    "fg_ssim_recorded",
    "edge_ssim_recorded",
    "gt_relative_laplacian_error_rgb",
    "signed_mean_delta_a_star",
    "signed_mean_delta_b_star",
)
COMPLEXITY_FIELDS = (
    "gt_fg_rgb_std",
    "gt_fg_grad_mag",
    "gt_fg_lap_var",
    "gt_fg_hf_energy",
    "gt_fg_color_entropy",
    "gt_fg_coverage",
)
FAVORABLE_DIRECTION = {
    "fg_ciede2000_rgb": "lower",
    "fg_psnr_recorded": "higher",
    "fg_lpips_recorded": "lower",
    "fg_ssim_recorded": "higher",
    "edge_ssim_recorded": "higher",
    "gt_relative_laplacian_error_rgb": "lower",
    "color_bias_a_magnitude": "lower",
    "color_bias_b_magnitude": "lower",
}
STAT_FIELDS = tuple(FAVORABLE_DIRECTION) + (
    "signed_mean_delta_a_star",
    "signed_mean_delta_b_star",
)
TEXTURE_FIELDS = (
    "gt_fg_lap_var",
    "gt_fg_hf_energy",
    "gt_fg_rgb_std",
    "gt_fg_grad_mag",
)


def as_float(value: Any) -> float:
    if value in (None, ""):
        return float("nan")
    return float(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_wide_cohort_rows(
    metric_rows: list[dict[str, str]],
    complexity_rows: list[dict[str, str]],
    diagnostic_uids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    complexity = {(r["cohort"], r["uid"]): r for r in complexity_rows}
    grouped: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in metric_rows:
        if row["cohort"] in ("FreshC", "FreshB"):
            grouped[(row["cohort"], row["uid"])][row["condition"]] = row

    wide_rows: list[dict[str, Any]] = []
    for (cohort, uid), conditions in sorted(grouped.items()):
        if set(conditions) != {"native_gfl", "layer_llh"}:
            raise ValueError(f"{cohort}/{uid}: expected one native_gfl and one layer_llh row")
        gfl, llh = conditions["native_gfl"], conditions["layer_llh"]
        target_hash_gfl = gfl.get("target_tensor_sha256_logged", "")
        target_hash_llh = llh.get("target_tensor_sha256_logged", "")
        if not target_hash_gfl or target_hash_gfl != target_hash_llh:
            raise ValueError(f"{cohort}/{uid}: GFL/LLH target tensor hashes differ or are missing")
        row: dict[str, Any] = {
            "cohort": cohort,
            "uid": uid,
            "object_idx": gfl["object_idx"],
            "object_seed": gfl["object_seed"],
            "target_view_ids": gfl["target_view_ids"],
            "reverse_view_rotation": gfl["reverse_view_rotation"],
            "checkpoint_sha256": gfl["checkpoint_sha256"],
            "runner_sha256_gfl": gfl["runner_sha256"],
            "runner_sha256_llh": llh["runner_sha256"],
            "target_tensor_sha256_logged": target_hash_gfl,
            "gfl_prediction_png": gfl["prediction_png"],
            "gfl_prediction_sha256": gfl["prediction_sha256"],
            "llh_prediction_png": llh["prediction_png"],
            "llh_prediction_sha256": llh["prediction_sha256"],
            "gt_render_dir": gfl["gt_render_dir"],
            "gt_selected_source_files_digest_sha256": gfl["gt_selected_source_files_digest_sha256"],
            "diagnostic_uid_overlap": uid in diagnostic_uids,
            "included_in_freshc_uid_excluded_scope": cohort != "FreshC" or uid not in diagnostic_uids,
        }
        for field in PAIR_FIELDS:
            gv, lv = as_float(gfl.get(field)), as_float(llh.get(field))
            row[f"gfl_{field}"] = gv
            row[f"llh_{field}"] = lv
            row[f"delta_llh_minus_gfl_{field}"] = lv - gv
        for side, value in (("a", "signed_mean_delta_a_star"), ("b", "signed_mean_delta_b_star")):
            gv = abs(as_float(gfl[value]))
            lv = abs(as_float(llh[value]))
            row[f"gfl_color_bias_{side}_magnitude"] = gv
            row[f"llh_color_bias_{side}_magnitude"] = lv
            row[f"delta_llh_minus_gfl_color_bias_{side}_magnitude"] = lv - gv

        if cohort == "FreshC":
            gt = complexity[(cohort, uid)]
            for field in COMPLEXITY_FIELDS:
                row[field] = as_float(gt.get(field))
            row["gt_complexity_source_sha256"] = gt["gt_selected_source_files_digest_sha256"]
        else:
            for field in COMPLEXITY_FIELDS:
                row[field] = as_float(gfl.get(field))
            row["gt_complexity_source_sha256"] = gfl["gt_selected_source_files_digest_sha256"]
        if gfl["target_view_ids"] != llh["target_view_ids"] or gfl["gt_selected_source_files_digest_sha256"] != llh["gt_selected_source_files_digest_sha256"]:
            raise ValueError(f"{cohort}/{uid}: target view or source identity differs by condition")
        wide_rows.append(row)

    diagnostic_rows_by_uid: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in metric_rows:
        if row["cohort"] == "diagnostic26":
            diagnostic_rows_by_uid[row["uid"]][row["condition"]] = row
    diagnostic_wide: list[dict[str, Any]] = []
    for uid, conditions in sorted(diagnostic_rows_by_uid.items()):
        if set(conditions) != {"No Adapter", "GFL", "LLH"}:
            raise ValueError(f"diagnostic26/{uid}: expected No Adapter, GFL, LLH")
        row = {"cohort": "diagnostic26", "uid": uid}
        for condition, source in conditions.items():
            key = condition.replace(" ", "")
            for field in PAIR_FIELDS:
                row[f"{key}_{field}"] = as_float(source.get(field))
            for side, field in (("a", "signed_mean_delta_a_star"), ("b", "signed_mean_delta_b_star")):
                row[f"{key}_color_bias_{side}_magnitude"] = abs(as_float(source.get(field)))
            row[f"{key}_prediction_png"] = source.get("prediction_png", "")
            row[f"{key}_prediction_sha256"] = source.get("prediction_sha256", "")
            row[f"{key}_reference_sha256"] = source.get("reference_sha256", "")
            row[f"{key}_mask_sha256"] = source.get("mask_sha256", "")
            row[f"{key}_source"] = source.get("source", "")
        for field in PAIR_FIELDS:
            row[f"GFL_minus_NoAdapter_{field}"] = row[f"GFL_{field}"] - row[f"NoAdapter_{field}"]
            row[f"LLH_minus_GFL_{field}"] = row[f"LLH_{field}"] - row[f"GFL_{field}"]
            row[f"LLH_minus_NoAdapter_{field}"] = row[f"LLH_{field}"] - row[f"NoAdapter_{field}"]
        for side in ("a", "b"):
            for contrast, first, second in (
                ("GFL_minus_NoAdapter", "GFL", "NoAdapter"),
                ("LLH_minus_GFL", "LLH", "GFL"),
                ("LLH_minus_NoAdapter", "LLH", "NoAdapter"),
            ):
                row[f"{contrast}_color_bias_{side}_magnitude"] = row[f"{first}_color_bias_{side}_magnitude"] - row[f"{second}_color_bias_{side}_magnitude"]
        diagnostic_wide.append(row)

    if len(wide_rows) != 450 or sum(r["cohort"] == "FreshC" for r in wide_rows) != 300 or sum(r["cohort"] == "FreshB" for r in wide_rows) != 150:
        raise ValueError(f"Unexpected cohort row counts: total={len(wide_rows)}")
    if len(diagnostic_wide) != 26:
        raise ValueError(f"Unexpected diagnostic count {len(diagnostic_wide)}")
    return wide_rows, diagnostic_wide


def paired_summary(values: np.ndarray, direction: str | None, seed: int) -> dict[str, Any]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    n = int(values.size)
    if not n:
        raise ValueError("Cannot summarize an empty paired vector")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, n, size=(10_000, n))
    bootstrap = values[indices]
    means = bootstrap.mean(axis=1)
    medians = np.median(bootstrap, axis=1)
    favorable = values < 0 if direction == "lower" else values > 0 if direction == "higher" else None
    return {
        "n": n,
        "mean_delta": float(values.mean()),
        "median_delta": float(np.median(values)),
        "mean_ci95_low": float(np.quantile(means, 0.025)),
        "mean_ci95_high": float(np.quantile(means, 0.975)),
        "median_ci95_low": float(np.quantile(medians, 0.025)),
        "median_ci95_high": float(np.quantile(medians, 0.975)),
        "cohen_dz": float(values.mean() / values.std(ddof=1)) if n > 1 and values.std(ddof=1) > 0 else float("nan"),
        "wins": int(favorable.sum()) if favorable is not None else "",
        "losses": int((~favorable & (values != 0)).sum()) if favorable is not None else "",
        "ties": int((values == 0).sum()) if favorable is not None else "",
        "favorable_object_fraction": float(favorable.mean()) if favorable is not None else "",
    }


def build_statistics(wide_rows: list[dict[str, Any]], diagnostic_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seed_counter = 0
    scopes: list[tuple[str, list[dict[str, Any]], str]] = [
        ("FreshC_full_n300", [r for r in wide_rows if r["cohort"] == "FreshC"], "llh_minus_gfl"),
        ("FreshC_diagnostic_UID_excluded_n280", [r for r in wide_rows if r["cohort"] == "FreshC" and r["included_in_freshc_uid_excluded_scope"]], "llh_minus_gfl"),
        ("FreshB_independent_n150", [r for r in wide_rows if r["cohort"] == "FreshB"], "llh_minus_gfl"),
    ]
    diag_contrasts = (
        ("GFL_minus_NoAdapter", "GFL_minus_NoAdapter"),
        ("LLH_minus_GFL", "LLH_minus_GFL"),
        ("LLH_minus_NoAdapter", "LLH_minus_NoAdapter"),
    )
    for scope, rows, contrast in scopes:
        for metric in STAT_FIELDS:
            field = f"delta_{contrast}_{metric}" if contrast == "llh_minus_gfl" else f"{contrast}_{metric}"
            values = np.asarray([as_float(r[field]) for r in rows], dtype=float)
            if not np.isfinite(values).any():
                output.append({"scope": scope, "contrast": "LLH-GFL", "metric": metric, "direction": FAVORABLE_DIRECTION.get(metric, "signed/no scalar preference"), "data_availability": "not present in frozen diagnostic CSV", "n": 0})
                continue
            if not np.isfinite(values).all():
                raise ValueError(f"Partially missing metric {scope}/{metric}")
            direction = FAVORABLE_DIRECTION.get(metric)
            stats = paired_summary(values, direction, 20261008 + seed_counter)
            seed_counter += 1
            output.append({"scope": scope, "contrast": "LLH-GFL", "metric": metric, "direction": direction or "signed/no scalar preference", "data_availability": "complete", "bootstrap_seed": 20261008 + seed_counter - 1, **stats})
    for contrast_name, field_prefix in diag_contrasts:
        for metric in STAT_FIELDS:
            field = f"{field_prefix}_{metric}"
            values = np.asarray([as_float(r[field]) for r in diagnostic_rows], dtype=float)
            if not np.isfinite(values).any():
                output.append({"scope": "diagnostic26_forensic_only", "contrast": contrast_name.replace("_", " "), "metric": metric, "direction": FAVORABLE_DIRECTION.get(metric, "signed/no scalar preference"), "data_availability": "not present in frozen diagnostic CSV", "n": 0})
                continue
            if not np.isfinite(values).all():
                raise ValueError(f"Partially missing metric diagnostic26/{contrast_name}/{metric}")
            direction = FAVORABLE_DIRECTION.get(metric)
            stats = paired_summary(values, direction, 20261008 + seed_counter)
            seed_counter += 1
            output.append({"scope": "diagnostic26_forensic_only", "contrast": contrast_name.replace("_", " "), "metric": metric, "direction": direction or "signed/no scalar preference", "data_availability": "complete", "bootstrap_seed": 20261008 + seed_counter - 1, **stats})
    return output


def build_quartile_tables(wide_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fresh_b = [r for r in wide_rows if r["cohort"] == "FreshB"]
    lap = np.asarray([as_float(r["gt_fg_lap_var"]) for r in fresh_b])
    cutpoints = np.quantile(lap, [0.25, 0.5, 0.75]).tolist()
    for row in wide_rows:
        row["gt_laplacian_quartile_fixed_B_cutpoints"] = int(np.digitize(as_float(row["gt_fg_lap_var"]), cutpoints)) + 1

    outputs = []
    for scope, rows in (
        ("FreshB_own_frozen_cohort_quartiles", fresh_b),
        ("FreshC_fixed_FreshB_cutpoints_all_n300", [r for r in wide_rows if r["cohort"] == "FreshC"]),
        ("FreshC_fixed_FreshB_cutpoints_diagnostic_UID_excluded_n280", [r for r in wide_rows if r["cohort"] == "FreshC" and r["included_in_freshc_uid_excluded_scope"]]),
    ):
        for q in range(1, 5):
            group = [r for r in rows if int(r["gt_laplacian_quartile_fixed_B_cutpoints"]) == q]
            for metric in STAT_FIELDS:
                vals = np.asarray([as_float(r[f"delta_llh_minus_gfl_{metric}"]) for r in group], dtype=float)
                summary = paired_summary(vals, FAVORABLE_DIRECTION.get(metric), 20261008 + q * 53 + len(outputs))
                outputs.append({"scope": scope, "quartile": q, "n": len(group), "gt_lap_var_lower_inclusive": cutpoints[q - 2] if q > 1 else "", "gt_lap_var_upper_exclusive": cutpoints[q - 1] if q < 4 else "", "metric": metric, "direction": FAVORABLE_DIRECTION.get(metric, "signed/no scalar preference"), **summary})
    return outputs, {"fixed_cutpoints_from_FreshB_n150": cutpoints, "FreshB_quartile_counts": [int(np.sum(np.digitize(lap, cutpoints) == q)) for q in range(4)]}


def build_associations(wide_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs = []
    for scope, cohort, predicate in (
        ("FreshC_full_n300_exploratory", "FreshC", lambda row: True),
        ("FreshC_UID_excluded_n280_exploratory", "FreshC", lambda row: row["included_in_freshc_uid_excluded_scope"]),
        ("FreshB_independent_n150", "FreshB", lambda row: True),
    ):
        rows = [r for r in wide_rows if r["cohort"] == cohort and predicate(r)]
        for metric in ("fg_ciede2000_rgb", "fg_psnr_recorded", "fg_lpips_recorded", "gt_relative_laplacian_error_rgb"):
            delta_field = f"delta_llh_minus_gfl_{metric}"
            for texture in TEXTURE_FIELDS:
                x = np.asarray([as_float(r[texture]) for r in rows])
                y = np.asarray([as_float(r[delta_field]) for r in rows])
                rho, p_value = spearmanr(x, y)
                outputs.append({"scope": scope, "n": len(rows), "paired_delta_metric": metric, "texture_field": texture, "spearman_rho": float(rho), "two_sided_p_unadjusted_exploratory": float(p_value)})
    return outputs


def build_uid_overlap_sensitivity(wide_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs = []
    seed = 20261008 + 500
    for label, overlap in (("FreshC_UIDs_overlapping_prior_diagnostic26_n20", True), ("FreshC_UIDs_disjoint_from_prior_diagnostic26_n280", False)):
        rows = [r for r in wide_rows if r["cohort"] == "FreshC" and bool(r["diagnostic_uid_overlap"]) is overlap]
        for metric in STAT_FIELDS:
            field = f"delta_llh_minus_gfl_{metric}"
            values = np.asarray([as_float(r[field]) for r in rows])
            summary = paired_summary(values, FAVORABLE_DIRECTION.get(metric), seed)
            outputs.append({"scope": label, "contrast": "LLH-GFL", "metric": metric, "direction": FAVORABLE_DIRECTION.get(metric, "signed/no scalar preference"), "overlap_definition": "UID overlap only; saved prediction hashes differ from the prior diagnostic instance", "bootstrap_seed": seed, **summary})
            seed += 1
    return outputs


def parse_residual_log(path: Path) -> dict[tuple[int, str], dict[str, float]]:
    with path.open() as stream:
        raw = json.load(stream)
    values: dict[tuple[int, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for step_key, entries in raw.items():
        step = int(step_key)
        for entry in entries.values():
            layer = entry.get("depth")
            if layer not in {"deep", "middle", "shallow"}:
                continue
            values[(step, layer)]["mean_abs"].append(float(entry.get("mean_abs", 0.0)))
            values[(step, layer)]["effective_scale"].append(float(entry.get("eff_scale", entry.get("scale", 0.0))))
            values[(step, layer)]["l2"].append(float(entry.get("l2", 0.0)))
    result: dict[tuple[int, str], dict[str, float]] = {}
    for key, fields in values.items():
        result[key] = {
            "n_modules": float(len(fields["mean_abs"])),
            "mean_abs_module_mean": float(np.mean(fields["mean_abs"])),
            "effective_scale_module_mean": float(np.mean(fields["effective_scale"])),
            "l2_module_mean": float(np.mean(fields["l2"])),
            "l2_module_sum": float(np.sum(fields["l2"])),
        }
    return result


def build_residual_tables(wide_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    identity_rows = []
    step_rows = []
    aggregate: dict[tuple[str, str, int], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in wide_rows:
        cohort, uid = row["cohort"], row["uid"]
        if cohort == "FreshC":
            gfl_path = FRESHC_RUN_ROOT / "c3_confirmation/residual_logs/native_gfl" / f"{uid}.json"
            llh_path = FRESHC_RUN_ROOT / "revision_era_addendum/residual_logs/layer_llh" / f"{uid}.json"
        else:
            gfl_path = FRESHB_RUN_ROOT / "residual_logs/native_gfl" / f"{uid}.json"
            llh_path = FRESHB_RUN_ROOT / "residual_logs/layer_llh" / f"{uid}.json"
        if not gfl_path.is_file() or not llh_path.is_file():
            raise FileNotFoundError(f"Missing paired residual logs for {cohort}/{uid}")
        gfl, llh = parse_residual_log(gfl_path), parse_residual_log(llh_path)
        if set(gfl) != set(llh) or len(gfl) != 150:
            raise ValueError(f"{cohort}/{uid}: residual log grid differs or is not 50×3")
        if row["target_tensor_sha256_logged"] == "":
            raise ValueError(f"{cohort}/{uid}: no paired target tensor identity")
        identity_rows.append({
            "cohort": cohort,
            "uid": uid,
            "target_tensor_sha256_gfl_equals_llh": row["target_tensor_sha256_logged"],
            "gfl_residual_log": str(gfl_path),
            "gfl_residual_log_sha256": sha256_file(gfl_path),
            "llh_residual_log": str(llh_path),
            "llh_residual_log_sha256": sha256_file(llh_path),
            "same_step_layer_grid": True,
            "n_step_layer_cells": len(gfl),
        })
        for (step, layer) in sorted(gfl):
            g, l = gfl[(step, layer)], llh[(step, layer)]
            row_out: dict[str, Any] = {"cohort": cohort, "uid": uid, "step_zero_based": step, "layer": layer, "gfl_n_modules": int(g["n_modules"]), "llh_n_modules": int(l["n_modules"])}
            for field in ("mean_abs_module_mean", "effective_scale_module_mean", "l2_module_mean", "l2_module_sum"):
                row_out[f"gfl_{field}"] = g[field]
                row_out[f"llh_{field}"] = l[field]
                row_out[f"delta_llh_minus_gfl_{field}"] = l[field] - g[field]
                aggregate[(cohort, layer, step)][field].append(l[field] - g[field])
            row_out["target_tensor_sha256"] = row["target_tensor_sha256_logged"]
            step_rows.append(row_out)

    summary_rows = []
    for (cohort, layer, step), fields in sorted(aggregate.items()):
        summary_rows.append({
            "cohort": cohort,
            "layer": layer,
            "step_zero_based": step,
            "n_object_pairs": len(fields["mean_abs_module_mean"]),
            "mean_delta_llh_minus_gfl_mean_abs_module_mean": float(np.mean(fields["mean_abs_module_mean"])),
            "median_delta_llh_minus_gfl_mean_abs_module_mean": float(np.median(fields["mean_abs_module_mean"])),
            "mean_delta_llh_minus_gfl_effective_scale_module_mean": float(np.mean(fields["effective_scale_module_mean"])),
            "mean_delta_llh_minus_gfl_l2_module_mean": float(np.mean(fields["l2_module_mean"])),
            "mean_delta_llh_minus_gfl_l2_module_sum": float(np.mean(fields["l2_module_sum"])),
            "interpretation": "descriptive logged residual difference; not causal evidence",
        })
    return identity_rows, step_rows, summary_rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=HERE / "RGB_RECOMPUTED_CONDITION_METRICS.csv")
    ap.add_argument("--complexity", type=Path, default=HERE / "GT_ONLY_TEXTURE_METRICS_FRESHC.csv")
    ap.add_argument("--out-dir", type=Path, default=HERE)
    args = ap.parse_args()

    metric_rows = load_csv(args.input)
    complexity_rows = load_csv(args.complexity)
    diagnostic_uids = {r["uid"] for r in load_csv(DIAGNOSTIC_RESULTS)}
    wide_rows, diagnostic_rows = build_wide_cohort_rows(metric_rows, complexity_rows, diagnostic_uids)
    stats_rows = build_statistics(wide_rows, diagnostic_rows)
    quartile_rows, quartile_manifest = build_quartile_tables(wide_rows)
    association_rows = build_associations(wide_rows)
    overlap_rows = build_uid_overlap_sensitivity(wide_rows)
    residual_identity, residual_step_pairs, residual_summary_rows = build_residual_tables(wide_rows)

    write_csv(args.out_dir / "A_COHORT_HETEROGENEITY.csv", wide_rows)
    write_csv(args.out_dir / "B_OBJECT_LEVEL_RESULTS.csv", [r for r in wide_rows if r["cohort"] == "FreshB"])
    write_csv(args.out_dir / "DIAGNOSTIC26_REANALYSIS.csv", diagnostic_rows)
    write_csv(args.out_dir / "PAIRED_BOOTSTRAP_STATISTICS.csv", stats_rows)
    write_csv(args.out_dir / "A_QUARTILE_EFFECTS.csv", quartile_rows)
    write_csv(args.out_dir / "A_COMPLEXITY_ASSOCIATIONS.csv", association_rows)
    write_csv(args.out_dir / "A_UID_OVERLAP_SENSITIVITY.csv", overlap_rows)
    write_csv(args.out_dir / "RESIDUAL_LOG_IDENTITY_AUDIT.csv", residual_identity)
    write_csv(args.out_dir / "RESIDUAL_LOG_STEP_PAIRED.csv", residual_step_pairs)
    write_csv(args.out_dir / "RESIDUAL_LOG_STEP_SUMMARY.csv", residual_summary_rows)
    (args.out_dir / "A_QUARTILE_CUTPOINTS.json").write_text(json.dumps(quartile_manifest, indent=2) + "\n")
    print(json.dumps({
        "cohort_rows": len(wide_rows),
        "FreshC": sum(r["cohort"] == "FreshC" for r in wide_rows),
        "FreshC_diagnostic_UID_excluded": sum(r["cohort"] == "FreshC" and r["included_in_freshc_uid_excluded_scope"] for r in wide_rows),
        "FreshB": sum(r["cohort"] == "FreshB" for r in wide_rows),
        "diagnostic26_rows": len(diagnostic_rows),
        "statistics_rows": len(stats_rows),
        "quartile_rows": len(quartile_rows),
        "residual_log_pairs": len(residual_identity),
        "residual_step_pairs": len(residual_step_pairs),
        "residual_step_summary_rows": len(residual_summary_rows),
        "quartile_manifest": quartile_manifest,
        "output_dir": str(args.out_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
