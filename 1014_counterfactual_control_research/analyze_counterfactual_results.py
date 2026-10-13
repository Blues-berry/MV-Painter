#!/usr/bin/env python3
"""Summarize the frozen six-object generation and native-bake experiment."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.stats import beta


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
CONDITIONS = ("counterfactual_b0", "counterfactual_bplus", "counterfactual_bminus")
LOWER_IS_BETTER = {"fg_lpips", "ciede2000", "uv_seam_discontinuity", "cross_view_texel_variance"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def bootstrap_mean_ci(values: np.ndarray, seed: int = 20261013) -> list[float]:
    rng = np.random.default_rng(seed)
    sample = values[rng.integers(0, len(values), size=(50_000, len(values)))].mean(axis=1)
    return [float(value) for value in np.quantile(sample, [0.025, 0.975])]


def exact_binomial_ci(successes: int, total: int) -> list[float]:
    low = 0.0 if successes == 0 else float(beta.ppf(0.025, successes, total - successes + 1))
    high = 1.0 if successes == total else float(beta.ppf(0.975, successes + 1, total - successes))
    return [low, high]


def summarize(values: list[float], seed: int) -> dict:
    array = np.asarray(values, dtype=np.float64)
    return {
        "n_objects": int(len(array)),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "sd_object_level": float(array.std(ddof=1)) if len(array) > 1 else 0.0,
        "object_bootstrap_95ci": bootstrap_mean_ci(array, seed),
    }


def main() -> None:
    generation = ROOT / "generation"
    bake = ROOT / "bake"
    view_rows = read_csv(generation / "GENERATION_VIEW_METRICS.csv")
    bake_rows = read_csv(bake / "native_egl_unseen" / "NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv")
    bake_summary = json.loads((bake / "BAKE_RUN_SUMMARY.json").read_text())
    generation_rows = json.loads((generation / "rows_shard0.json").read_text())

    views: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in view_rows:
        views[(row["object_uid"], row["condition"])].append(row)
    gen_run = {(row["object_uid"], row["condition"]): row for row in generation_rows}
    baked = {(row["object_uid"], row["method"]): row for row in bake_rows}
    bake_records = {(row["object"], row["method"]): row for row in bake_summary["records"]}

    uids = sorted({uid for uid, condition in views if condition == "counterfactual_b0"})
    reference_by_object: dict[str, dict[str, dict[str, str]]] = {}
    for uid in uids:
        reference_by_object[uid] = {
            condition: next(row for row in views[(uid, condition)] if row["slot"] == "0")
            for condition in CONDITIONS
        }
        hash_sets = [gen_run[(uid, condition)]["input_hashes"] for condition in CONDITIONS]
        if not (hash_sets[0] == hash_sets[1] == hash_sets[2]):
            raise RuntimeError(f"condition input hashes differ for {uid}")

    rows_out = []
    pairwise = []
    for object_idx, uid in enumerate(uids):
        ref = reference_by_object[uid]
        source_actions = {
            "counterfactual_bplus"
            if float(ref["counterfactual_bplus"][metric]) < float(ref["counterfactual_bminus"][metric])
            else "counterfactual_bminus"
            for metric in ("fg_rgb_mae", "ciede2000")
        }
        mae_action = (
            "counterfactual_bplus"
            if float(ref["counterfactual_bplus"]["fg_rgb_mae"]) < float(ref["counterfactual_bminus"]["fg_rgb_mae"])
            else "counterfactual_bminus"
        )
        ciede_action = (
            "counterfactual_bplus"
            if float(ref["counterfactual_bplus"]["ciede2000"]) < float(ref["counterfactual_bminus"]["ciede2000"])
            else "counterfactual_bminus"
        )

        pair = {"object_idx": int(gen_run[(uid, "counterfactual_b0")]["object_idx"]), "object_uid": uid}
        for metric in ("fg_rgb_mae", "ciede2000"):
            pair[f"{metric}_bplus_minus_bminus"] = (
                float(ref["counterfactual_bplus"][metric]) - float(ref["counterfactual_bminus"][metric])
            )
        pair["bplus_minus_bminus_bake_fg_lpips"] = (
            float(baked[(uid, "counterfactual_bplus")]["fg_lpips"])
            - float(baked[(uid, "counterfactual_bminus")]["fg_lpips"])
        )
        pair["direction_match_mae"] = (
            pair["fg_rgb_mae_bplus_minus_bminus"] * pair["bplus_minus_bminus_bake_fg_lpips"] > 0
        )
        pair["direction_match_ciede2000"] = (
            pair["ciede2000_bplus_minus_bminus"] * pair["bplus_minus_bminus_bake_fg_lpips"] > 0
        )
        pair["mae_selected_condition"] = mae_action
        pair["ciede_selected_condition"] = ciede_action
        pair["mae_selected_bake_delta_vs_b0"] = (
            float(baked[(uid, mae_action)]["fg_lpips"])
            - float(baked[(uid, "counterfactual_b0")]["fg_lpips"])
        )
        pair["ciede_selected_bake_delta_vs_b0"] = (
            float(baked[(uid, ciede_action)]["fg_lpips"])
            - float(baked[(uid, "counterfactual_b0")]["fg_lpips"])
        )
        pairwise.append(pair)

        baseline_panel = np.asarray(
            Image.open(generation / "predictions" / "counterfactual_b0" / f"{uid}.png").convert("RGB"),
            dtype=np.int16,
        )
        for condition in CONDITIONS:
            cur_views = sorted(views[(uid, condition)], key=lambda row: int(row["slot"]))
            if len(cur_views) != 6:
                raise RuntimeError(f"missing per-view metrics for {uid}/{condition}")
            gen_row = gen_run[(uid, condition)]
            bake_row = baked[(uid, condition)]
            bake_record = bake_records[(uid, condition)]
            panel_path = generation / "predictions" / condition / f"{uid}.png"
            panel = np.asarray(Image.open(panel_path).convert("RGB"), dtype=np.int16)
            diff = np.abs(panel - baseline_panel)
            nonref = [row for row in cur_views if row["role"] == "nonreference"]
            ref_row = ref[condition]
            row_out = {
                "object_idx": int(gen_row["object_idx"]),
                "object_uid": uid,
                "condition": condition,
                "reference_raw_camera": ref_row["reference_raw_camera"],
                "reference_fg_rgb_mae": float(ref_row["fg_rgb_mae"]),
                "reference_ciede2000": float(ref_row["ciede2000"]),
                "reference_fg_psnr": float(ref_row["fg_psnr"]),
                "reference_fg_lpips": float(ref_row["fg_lpips"]),
                "reference_fg_ssim": float(ref_row["fg_ssim"]),
                "nonreference_mean_fg_psnr": float(np.mean([float(row["fg_psnr"]) for row in nonref])),
                "nonreference_mean_fg_lpips": float(np.mean([float(row["fg_lpips"]) for row in nonref])),
                "nonreference_mean_fg_ssim": float(np.mean([float(row["fg_ssim"]) for row in nonref])),
                "all_six_mean_fg_psnr": float(np.mean([float(row["fg_psnr"]) for row in cur_views])),
                "all_six_mean_fg_lpips": float(np.mean([float(row["fg_lpips"]) for row in cur_views])),
                "all_six_mean_fg_ssim": float(np.mean([float(row["fg_ssim"]) for row in cur_views])),
                "unseen_11_mean_fg_lpips": float(bake_row["fg_lpips"]),
                "unseen_11_mean_fg_psnr": float(bake_row["fg_psnr"]),
                "unseen_11_mean_fg_ssim": float(bake_row["fg_ssim"]),
                "unseen_11_mean_ciede2000": float(bake_row["ciede2000"]),
                "unseen_11_mean_edge_ssim": float(bake_row["edge_ssim"]),
                "unseen_11_silhouette_iou": float(bake_row["silhouette_iou"]),
                "uv_texture_coverage": float(bake_row["texture_coverage"]),
                "uv_cross_view_texel_variance": float(bake_row["cross_view_texel_variance"]),
                "uv_seam_discontinuity": float(bake_row["uv_seam_discontinuity"]),
                "generation_seconds": float(gen_row["elapsed_seconds"]),
                "panel_rgb_mae_vs_b0": float(diff.mean() / 255.0),
                "panel_changed_channel_fraction_vs_b0": float(np.count_nonzero(diff) / diff.size),
                "selected_by_reference_mae": condition == mae_action if condition != "counterfactual_b0" else False,
                "selected_by_reference_ciede2000": condition == ciede_action if condition != "counterfactual_b0" else False,
                "panel_path": str(panel_path),
                "panel_sha256": sha256(panel_path),
                "baked_texture_path": bake_record["texture_path"],
                "baked_texture_sha256": sha256(Path(bake_record["texture_path"])),
                "textured_glb_path": bake_record["output_textured_glb"],
                "textured_glb_sha256": bake_record["output_textured_glb_sha256"],
            }
            rows_out.append(row_out)

    out_csv = ROOT / "ACTION_RESPONSE_RESULTS.csv"
    with out_csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows_out[0]))
        writer.writeheader()
        writer.writerows(rows_out)

    by_uid = {row["object_uid"]: row for row in pairwise}
    ref_delta_mae = np.asarray([row["fg_rgb_mae_bplus_minus_bminus"] for row in pairwise])
    ref_delta_ciede = np.asarray([row["ciede2000_bplus_minus_bminus"] for row in pairwise])
    baked_delta_pm = np.asarray([row["bplus_minus_bminus_bake_fg_lpips"] for row in pairwise])
    bake_b0 = np.asarray([float(baked[(uid, "counterfactual_b0")]["fg_lpips"]) for uid in uids])
    bake_p = np.asarray([float(baked[(uid, "counterfactual_bplus")]["fg_lpips"]) for uid in uids])
    bake_m = np.asarray([float(baked[(uid, "counterfactual_bminus")]["fg_lpips"]) for uid in uids])
    selected_mae = np.asarray([float(by_uid[uid]["mae_selected_bake_delta_vs_b0"]) for uid in uids])
    selected_ciede = np.asarray([float(by_uid[uid]["ciede_selected_bake_delta_vs_b0"]) for uid in uids])

    summary = {
        "status": "COMPLETE_EXPLORATORY_SIX_OBJECT_COUNTERFACTUAL_TEST",
        "objects_as_analysis_units": uids,
        "n_objects": len(uids),
        "views_and_steps_are_not_independent_samples": True,
        "conditions": list(CONDITIONS),
        "source_error_contrasts_bplus_minus_bminus": {
            "rgb_mae": summarize(ref_delta_mae.tolist(), 20261013),
            "ciede2000": summarize(ref_delta_ciede.tolist(), 20261014),
        },
        "bake_lpips_contrasts_bplus_minus_bminus": summarize(baked_delta_pm.tolist(), 20261015),
        "bake_lpips_contrasts_vs_b0": {
            "bplus_minus_b0": summarize((bake_p - bake_b0).tolist(), 20261016),
            "bminus_minus_b0": summarize((bake_m - bake_b0).tolist(), 20261017),
            "reference_mae_selected_minus_b0": summarize(selected_mae.tolist(), 20261018),
            "reference_ciede_selected_minus_b0": summarize(selected_ciede.tolist(), 20261019),
        },
        "direction_agreement": {
            "rgb_mae": {
                "matches": int(sum(row["direction_match_mae"] for row in pairwise)),
                "n": len(pairwise),
                "exact_binomial_95ci": exact_binomial_ci(int(sum(row["direction_match_mae"] for row in pairwise)), len(pairwise)),
            },
            "ciede2000": {
                "matches": int(sum(row["direction_match_ciede2000"] for row in pairwise)),
                "n": len(pairwise),
                "exact_binomial_95ci": exact_binomial_ci(int(sum(row["direction_match_ciede2000"] for row in pairwise)), len(pairwise)),
            },
        },
        "wins_against_b0": {
            "fixed_bplus": int(np.sum(bake_p < bake_b0)),
            "fixed_bminus": int(np.sum(bake_m < bake_b0)),
            "mae_selected_two_call": int(np.sum(selected_mae < 0)),
            "ciede_selected_two_call": int(np.sum(selected_ciede < 0)),
            "n": len(uids),
        },
        "two_candidate_selection": {
            "mae_selected_conditions": {row["object_uid"]: row["mae_selected_condition"] for row in pairwise},
            "ciede_selected_conditions": {row["object_uid"]: row["ciede_selected_condition"] for row in pairwise},
            "interpretation": "This is post-generation two-candidate selection; it requires both complete B+ and B− trajectories and is not a distinct controller.",
        },
        "per_object_pairs": pairwise,
        "metric_csv": str(out_csv),
    }
    (ROOT / "ACTION_RESPONSE_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({
        "rows": len(rows_out),
        "objects": len(uids),
        "mae_direction_match": summary["direction_agreement"]["rgb_mae"]["matches"],
        "ciede_direction_match": summary["direction_agreement"]["ciede2000"]["matches"],
        "bplus_minus_bminus_mean_lpips": summary["bake_lpips_contrasts_bplus_minus_bminus"]["mean"],
        "results": str(out_csv),
    }, indent=2))


def sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
