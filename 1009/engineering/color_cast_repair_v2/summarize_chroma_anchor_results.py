#!/usr/bin/env python3
"""Object-paired bootstrap analysis for frozen C1 development/validation rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
D_LOCK = HERE / "protocol/D_VALIDATION_LOCK.json"
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 20261009
Q4_THRESHOLD = 0.03139245230704546


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty object-level results: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bootstrap_summary(values: np.ndarray, *, lower_is_better: bool) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    n = int(values.size)
    if n == 0:
        raise ValueError("no finite object-level values for bootstrap")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = rng.integers(0, n, size=(BOOTSTRAP_N, n))
    boot_means = values[samples].mean(axis=1)
    boot_medians = np.median(values[samples], axis=1)
    wins = int(np.sum(values < 0 if lower_is_better else values > 0))
    losses = int(np.sum(values > 0 if lower_is_better else values < 0))
    ties = n - wins - losses
    sd = float(values.std(ddof=1)) if n > 1 else float("nan")
    return {
        "n_objects": n,
        "mean_delta": float(values.mean()),
        "median_delta": float(np.median(values)),
        "mean_delta_95_ci": [float(x) for x in np.percentile(boot_means, [2.5, 97.5])],
        "median_delta_95_ci": [float(x) for x in np.percentile(boot_medians, [2.5, 97.5])],
        "paired_effect_dz": float(values.mean() / sd) if sd > 0 else None,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": wins / n,
        "direction": "lower is better" if lower_is_better else "higher is better",
        "bootstrap_draws": BOOTSTRAP_N,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def object_level(rows: list[dict[str, str]]) -> list[dict]:
    by_uid: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_uid.setdefault(row["uid"], []).append(row)
    summaries = []
    for uid, view_rows in sorted(by_uid.items(), key=lambda item: int(item[1][0]["object_idx"] or 0)):
        view_rows.sort(key=lambda r: int(r["view_idx"]))
        if len(view_rows) != 6 or [int(r["view_idx"]) for r in view_rows] != list(range(6)):
            raise ValueError(f"{uid}: expected six ordered unique6 view rows")
        if len({r["baseline_png_sha256"] for r in view_rows}) != 1:
            raise ValueError(f"{uid}: inconsistent baseline image identities across views")
        if len({r["candidate_png_sha256"] for r in view_rows}) != 1:
            raise ValueError(f"{uid}: inconsistent candidate image identities across views")
        source = view_rows[0]
        unseen = view_rows[1:]

        def mean(field: str, selected=unseen) -> float:
            values = np.asarray([float(r[field]) for r in selected], dtype=np.float64)
            return float(values.mean())

        record = {
            "uid": uid,
            "cohort": source["cohort"],
            "source_cohort": source.get("source_cohort", ""),
            "object_idx": source["object_idx"],
            "object_seed": source["object_seed"],
            "target_view_ids": ";".join(r["target_view_id"] for r in view_rows),
            "source_view_id": source["target_view_id"],
            "gt_fg_lap_var": source.get("gt_fg_lap_var", ""),
            "gt_texture_quartile": source.get("gt_texture_quartile", ""),
            "source_condition_tensor_sha256": source["source_condition_tensor_sha256"],
            "source_alpha_sha256": source["source_alpha_sha256"],
            "baseline_png": source["baseline_png"],
            "baseline_png_sha256": source["baseline_png_sha256"],
            "candidate_png": source["candidate_png"],
            "candidate_png_sha256": source["candidate_png_sha256"],
            "candidate_method_lock_sha256": source["repair_method_lock_sha256"],
            "candidate_code_sha256": source["repair_code_sha256"],
            "baseline_generation_manifest_sha256": source["baseline_generation_manifest_sha256"],
            "applied_delta_a_star": source["applied_delta_a_star"],
            "applied_delta_b_star": source["applied_delta_b_star"],
        }
        for name, field in (
            ("unseen_fg_ciede2000", "delta_fg_ciede2000_candidate"),
            ("unseen_fg_psnr", "delta_fg_psnr_candidate"),
            ("unseen_fg_lpips", "delta_fg_lpips"),
            ("unseen_lstar_ssim_to_gt", "delta_foreground_lstar_ssim_to_gt"),
            ("unseen_gt_laplacian_error", "delta_gt_laplacian_error"),
            ("unseen_lstar_ssim_vs_gfl", "delta_lstar_ssim_vs_gfl"),
        ):
            record[f"delta_{name}"] = mean(field)
        for name, before, after in (
            ("unseen_fg_ciede2000", "gfl_fg_ciede2000_gfl", "candidate_fg_ciede2000_candidate"),
            ("unseen_fg_psnr", "gfl_fg_psnr_gfl", "candidate_fg_psnr_candidate"),
            ("unseen_fg_lpips", "candidate_fg_lpips_gfl", "candidate_fg_lpips_candidate"),
        ):
            record[f"gfl_{name}"] = mean(before)
            record[f"candidate_{name}"] = mean(after)
        record["source_delta_fg_ciede2000"] = float(source["delta_fg_ciede2000_candidate"])
        record["source_delta_fg_psnr"] = float(source["delta_fg_psnr_candidate"])
        record["source_delta_fg_lpips"] = float(source["delta_fg_lpips"])
        record["source_delta_lstar_ssim_to_gt"] = float(source["delta_foreground_lstar_ssim_to_gt"])
        record["source_lstar_ssim_vs_gfl"] = float(source["delta_lstar_ssim_vs_gfl"])
        record["source_background_changed_fraction"] = float(source["background_changed_fraction_candidate"])
        summaries.append(record)
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=("dev", "holdout"), required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    if args.cohort == "dev":
        input_path = args.input or HERE / "runs/phase_c/dev/C_REPAIR_PAIRED_RESULTS.csv"
        out_dir = args.out_dir or HERE / "runs/phase_c/dev"
    else:
        input_path = args.input or HERE / "runs/phase_d/freshb/C_REPAIR_PAIRED_RESULTS.csv"
        out_dir = args.out_dir or HERE / "runs/phase_d/freshb"
    out_dir.mkdir(parents=True, exist_ok=True)
    per_view = read_rows(input_path)
    objects = object_level(per_view)
    write_rows(out_dir / "COLOR_REPAIR_VALIDATION.csv", objects)

    lower_metrics = {
        "unseen_fg_ciede2000": ("delta_unseen_fg_ciede2000", True),
        "unseen_fg_lpips": ("delta_unseen_fg_lpips", True),
        "unseen_gt_laplacian_error": ("delta_unseen_gt_laplacian_error", True),
        "source_fg_ciede2000": ("source_delta_fg_ciede2000", True),
        "source_fg_lpips": ("source_delta_fg_lpips", True),
    }
    higher_metrics = {
        "unseen_fg_psnr": ("delta_unseen_fg_psnr", False),
        "unseen_lstar_ssim_to_gt": ("delta_unseen_lstar_ssim_to_gt", False),
        "source_fg_psnr": ("source_delta_fg_psnr", False),
        "source_lstar_ssim_to_gt": ("source_delta_lstar_ssim_to_gt", False),
    }
    statistics = {
        "cohort": args.cohort,
        "n_objects": len(objects),
        "unit": "object; equal average over the five non-source views",
        "paired_bootstrap": {name: bootstrap_summary(np.asarray([r[column] for r in objects], dtype=float),
                                                       lower_is_better=direction)
                             for name, (column, direction) in {**lower_metrics, **higher_metrics}.items()},
    }

    if args.cohort == "dev":
        if len(objects) != 4:
            raise ValueError(f"development gate is frozen for exactly four objects, found {len(objects)}")
        s = statistics["paired_bootstrap"]
        dev_checks = {
            "at_least_three_of_four_unseen_ciede_improve": s["unseen_fg_ciede2000"]["wins"] >= 3,
            "mean_unseen_ciede_delta_le_minus_1": s["unseen_fg_ciede2000"]["mean_delta"] <= -1.0,
            "mean_unseen_psnr_delta_above_minus_0p5_db": s["unseen_fg_psnr"]["mean_delta"] > -0.50,
            "mean_unseen_lpips_delta_below_plus_0p010": s["unseen_fg_lpips"]["mean_delta"] < 0.010,
            "mean_unseen_lstar_ssim_delta_above_minus_0p010": (
                s["unseen_lstar_ssim_to_gt"]["mean_delta"] > -0.010
            ),
        }
        dev_checks["all_numeric_development_criteria"] = all(dev_checks.values())
        manual_path = out_dir / "C1_DEV_MANUAL_REVIEW.json"
        manual = json.loads(manual_path.read_text()) if manual_path.exists() else {}
        manual_uids = {row.get("uid") for row in manual.get("images", [])}
        expected_uids = {row["uid"] for row in objects}
        review_complete = bool(manual.get("reviewed_at_utc")) and manual_uids == expected_uids
        dev_checks["visual_failure_cases_reviewed"] = review_complete
        dev_checks["normal_and_high_texture_reviewed"] = review_complete
        dev_checks["both_failure_cases_visibly_improved_without_new_cast"] = (
            review_complete and manual.get("failure_case_gate_pass") is True
        )
        dev_checks["normal_and_high_texture_quality_preserved"] = (
            review_complete and manual.get("normal_high_texture_quality_pass") is True
        )
        dev_checks["all_development_criteria_pass"] = (
            dev_checks["all_numeric_development_criteria"]
            and dev_checks["both_failure_cases_visibly_improved_without_new_cast"]
            and dev_checks["normal_and_high_texture_quality_preserved"]
        )
        if review_complete:
            statistics["manual_review"] = {
                "path": str(manual_path.resolve()),
                "sha256": sha_file(manual_path),
                "failure_case_gate_pass": manual.get("failure_case_gate_pass"),
                "normal_high_texture_quality_pass": manual.get("normal_high_texture_quality_pass"),
            }
        statistics["development_gate"] = dev_checks

    if args.cohort == "holdout":
        lock = json.loads(D_LOCK.read_text())
        cut = float(lock["texture_strata"]["cutpoints"][2])
        q4 = [r for r in objects if float(r["gt_fg_lap_var"]) >= cut]
        if len(objects) != 150 or len(q4) != 38:
            raise ValueError(f"holdout identity/texture strata mismatch: n={len(objects)}, Q4={len(q4)}")
        statistics["q4_threshold"] = cut
        statistics["q4_n"] = len(q4)
        statistics["q4_paired_bootstrap"] = {
            name: bootstrap_summary(np.asarray([r[column] for r in q4], dtype=float),
                                    lower_is_better=direction)
            for name, (column, direction) in {
                "q4_unseen_fg_ciede2000": ("delta_unseen_fg_ciede2000", True),
                "q4_unseen_fg_psnr": ("delta_unseen_fg_psnr", False),
                "q4_unseen_fg_lpips": ("delta_unseen_fg_lpips", True),
            }.items()
        }
        s = statistics["paired_bootstrap"]
        q = statistics["q4_paired_bootstrap"]
        checks = {
            "unseen_view_color_improved": (
                s["unseen_fg_ciede2000"]["mean_delta"] <= -1.0
                and s["unseen_fg_ciede2000"]["mean_delta_95_ci"][1] < 0
                and s["unseen_fg_ciede2000"]["wins"] > 0.5 * len(objects)
            ),
            "q4_no_major_color_regression": (
                q["q4_unseen_fg_ciede2000"]["mean_delta"] <= 1.0
                and q["q4_unseen_fg_ciede2000"]["mean_delta_95_ci"][1] < 2.0
            ),
            "q4_psnr_preserved": q["q4_unseen_fg_psnr"]["mean_delta_95_ci"][0] > -0.75,
            "q4_lpips_preserved": q["q4_unseen_fg_lpips"]["mean_delta_95_ci"][1] < 0.015,
            "overall_psnr_preserved": s["unseen_fg_psnr"]["mean_delta_95_ci"][0] > -0.50,
            "overall_lpips_preserved": s["unseen_fg_lpips"]["mean_delta_95_ci"][1] < 0.010,
            "foreground_lstar_ssim_preserved": s["unseen_lstar_ssim_to_gt"]["mean_delta_95_ci"][0] > -0.010,
            "source_view_not_traded_away": s["source_fg_ciede2000"]["mean_delta"] <= 0.5,
            "not_extreme_sample_driven": (
                s["unseen_fg_ciede2000"]["median_delta"] < 0
                and s["unseen_fg_ciede2000"]["wins"] >= 0.5 * len(objects)
            ),
        }
        checks["all_numeric_success_criteria"] = all(checks.values())
        statistics["success_checks"] = checks

    (out_dir / "COLOR_REPAIR_PAIRED_STATISTICS.json").write_text(json.dumps(statistics, indent=2) + "\n")
    lines = [
        f"# C1 {args.cohort} paired results",
        "",
        f"Objects: {len(objects)}. Primary unit: object, with the five non-source views averaged equally.",
        "Confidence intervals are 10,000 paired object bootstrap percentile intervals; wins are oriented so favorable change counts as a win.",
        "",
        "| Endpoint | n | Mean Δ | 95% CI | Median Δ | Wins / losses / ties | dz |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in statistics["paired_bootstrap"].items():
        ci = result["mean_delta_95_ci"]
        lines.append(
            f"| {name} ({result['direction']}) | {result['n_objects']} | {result['mean_delta']:.5f} | "
            f"[{ci[0]:.5f}, {ci[1]:.5f}] | {result['median_delta']:.5f} | "
            f"{result['wins']} / {result['losses']} / {result['ties']} | "
            f"{result['paired_effect_dz'] if result['paired_effect_dz'] is not None else float('nan'):.3f} |"
        )
    if args.cohort == "holdout":
        lines.extend(["", "## Frozen criteria", ""])
        lines.extend(f"- `{key}`: {'PASS' if value else 'FAIL'}" for key, value in statistics["success_checks"].items())
        lines.append("\nVisual review and failure-case inspection must also pass before `COLOR_FIX_VALIDATED=YES`.")
    else:
        lines.extend(["", "## Frozen development gate", ""])
        lines.extend(f"- `{key}`: {'PASS' if value else 'FAIL'}" for key, value in statistics["development_gate"].items())
        lines.append("\nVisual failure-case review and normal/high-texture inspection remain manual gates.")
    (out_dir / "COLOR_REPAIR_PAIRED_STATISTICS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": "complete", "cohort": args.cohort, "n_objects": len(objects),
                      "object_csv": str((out_dir / "COLOR_REPAIR_VALIDATION.csv").resolve()),
                      "statistics": str((out_dir / "COLOR_REPAIR_PAIRED_STATISTICS.json").resolve())}, indent=2))


if __name__ == "__main__":
    main()
