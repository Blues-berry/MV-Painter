#!/usr/bin/env python3
"""Analyze the separately locked same-cohort generic-schedule extension.

Must be run only after B_GENERIC_EXTENSION_INTEGRITY_GATE.md is PASS. Pairwise
H4 tests use the frozen paired-bootstrap implementation and Holm family; the
dose-adjusted model is a secondary within-cohort sensitivity analysis.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
EXT = V3 / "formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005"
CORE = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
COHORT = V3 / "fresh_confirm_b/fresh_confirm_B_150.txt"
SHAPES = ("linear", "cosine_bump", "trapezoid", "gaussian_peak")
CONDITIONS = tuple(f"gen_{s}{suffix}" for s in SHAPES for suffix in ("", "_bm"))
METHODS = ("layer_llh",) + CONDITIONS
LAYERS = ("deep", "middle", "shallow")
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
METRICS = ("fg_psnr", "fg_lpips", "full_psnr", "full_lpips", "fg_ssim", "edge_ssim", "full_ssim")
TEXTURE_COLUMNS = ("ciede2000", "logerr_laplacian_variance", "logerr_rgb_std",
                   "logerr_gradient_magnitude", "logerr_hf_energy")
sys.path.insert(0, str(V3))
import analyze_v3  # noqa: E402


def load_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise SystemExit(f"Required post-gate analysis input is missing: {path}")
    return pd.read_csv(path)


def residual_dose(run_dir: Path, condition: str, uids: list[str], manifest: dict) -> dict:
    spec = manifest["condition_specs"][condition]
    trace = spec["scale_trace_requested"]
    if len(trace) != 50:
        raise ValueError(f"{condition}: manifest does not contain 50 scale steps")
    uncapped = bool(spec.get("uncapped", False))
    out = {}
    for uid in uids:
        log = json.loads((run_dir / "residual_logs" / condition / f"{uid}.json").read_text())
        if set(log) != {str(i) for i in range(50)}:
            raise ValueError(f"{condition}/{uid}: expected 50 residual-log steps")
        layer_sq = {layer: [0.0] * 50 for layer in LAYERS}
        total_sq = [0.0] * 50
        for step in range(50):
            for entry in log[str(step)].values():
                layer = entry["depth"]
                l2 = float(entry["l2"])
                requested = float(entry["scale"])
                if (not math.isfinite(l2) or not math.isfinite(requested)
                        or float(entry["eff_scale"]) != min(requested, CAPS[layer])
                        or requested != float(trace[step][layer])):
                    raise ValueError(f"{condition}/{uid}: residual log differs from manifest")
                layer_sq[layer][step] += l2 * l2
                total_sq[step] += l2 * l2
        by_layer = {
            layer: {
                "integrated_postscale_norm": float(sum(math.sqrt(v) for v in layer_sq[layer])),
                "squared_postscale_norm": float(sum(layer_sq[layer])),
            }
            for layer in LAYERS
        }
        out[uid] = {
            "layers": by_layer,
            "total_integrated_postscale_norm": float(sum(math.sqrt(v) for v in total_sq)),
            "total_squared_postscale_norm": float(sum(total_sq)),
        }
    requested_sums = {layer: float(sum(float(step[layer]) for step in trace)) for layer in LAYERS}
    effective_sums = {
        layer: float(sum(float(step[layer]) if uncapped else min(float(step[layer]), CAPS[layer])
                         for step in trace))
        for layer in LAYERS
    }
    cap_rates = {
        layer: (0.0 if uncapped else
                float(np.mean([float(step[layer]) > CAPS[layer] for step in trace])))
        for layer in LAYERS
    }
    summary = {"requested_scale_integral_50_steps": requested_sums,
               "applied_scale_integral_50_steps": effective_sums,
               "uncapped": uncapped, "cap_activation_fraction_by_step": cap_rates}
    for layer in LAYERS:
        vals = [out[uid]["layers"][layer] for uid in uids]
        for field in ("integrated_postscale_norm", "squared_postscale_norm"):
            a = np.asarray([v[field] for v in vals], dtype=float)
            summary.setdefault("layer_residual_dose", {}).setdefault(layer, {})[field] = {
                "mean": float(a.mean()), "median": float(np.median(a)),
            }
    for field in ("total_integrated_postscale_norm", "total_squared_postscale_norm"):
        a = np.asarray([out[uid][field] for uid in uids], dtype=float)
        summary[field] = {"mean": float(a.mean()), "median": float(np.median(a))}
    return {"per_object": out, "summary": summary}


def paired_summary(a: np.ndarray, b: np.ndarray, metric: str) -> dict:
    delta = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    stat = analyze_v3.paired_bootstrap(delta)
    lower_is_better = (metric in {"fg_lpips", "full_lpips", *TEXTURE_COLUMNS}
                       or metric.startswith("logerr_"))
    stat["favorable_rate"] = float(np.mean(delta < 0 if lower_is_better else delta > 0))
    stat["favorable_direction"] = "lower" if lower_is_better else "higher"
    stat["p_raw_upper_bound"] = f"<={stat['p_bootstrap']:.6g}" if stat["p_bootstrap"] <= 1 / analyze_v3.BOOT_N else stat["p_bootstrap"]
    return stat


def dose_adjusted(metrics: pd.DataFrame, doses: dict[str, dict], metric: str) -> dict:
    frame = metrics[metrics.condition.isin(METHODS)][["object_uid", "condition", metric]].copy()
    frame["dose"] = [doses[c]["per_object"][uid]["total_integrated_postscale_norm"]
                      for uid, c in zip(frame.object_uid, frame.condition)]
    if (frame.dose <= 0).any() or not np.isfinite(frame.dose).all():
        return {"status": "not_estimable_nonpositive_or_nonfinite_dose"}
    intervals = frame.groupby("condition").dose.quantile([0.05, 0.95]).unstack()
    method_intervals = {
        c: {"q05": float(intervals.loc[c, 0.05]), "q95": float(intervals.loc[c, 0.95])}
        for c in METHODS
    }
    lower, upper = float(intervals[0.05].max()), float(intervals[0.95].min())
    support = {"lower": lower, "upper": upper,
               "method_intervals": method_intervals,
               "rule": "intersection of method-specific 5th-95th percentile intervals"}
    if lower >= upper:
        return {"status": "no_common_dose_support", "common_support": support,
                "retained_fraction_by_method": {c: 0.0 for c in METHODS}}
    kept = frame[(frame.dose >= lower) & (frame.dose <= upper)].copy()
    retained = {c: int((kept.condition == c).sum()) for c in METHODS}
    if min(retained.values()) < 20:
        return {"status": "common_support_too_sparse", "common_support": support,
                "retained_rows_by_method": retained,
                "retained_fraction_by_method": {c: retained[c] / 150 for c in METHODS}}
    kept["log_dose"] = np.log(kept.dose)
    model = smf.ols(f"{metric} ~ C(condition) + log_dose + C(object_uid)", data=kept).fit(
        cov_type="cluster", cov_kwds={"groups": kept.object_uid})
    design = model.model.data.design_info
    reference_uid = sorted(kept.object_uid.unique())[0]
    mean_log_dose = float(kept.log_dose.mean())
    grid = pd.DataFrame([{"condition": c, "object_uid": reference_uid,
                          "log_dose": mean_log_dose} for c in METHODS])
    from patsy import build_design_matrices
    x = np.asarray(build_design_matrices([design], grid)[0])
    contrasts = {}
    for condition in CONDITIONS:
        v = x[METHODS.index("layer_llh")] - x[METHODS.index(condition)]
        estimate = float(v @ model.params)
        se = float(np.sqrt(v @ model.cov_params() @ v))
        contrasts[condition] = {"LLH_minus_schedule": estimate,
                                "cluster_robust_ci95": [estimate - 1.96 * se, estimate + 1.96 * se],
                                "p_two_sided_unadjusted": float(model.t_test(v).pvalue)}
    return {
        "status": "fit_on_common_support",
        "model": f"{metric} ~ method + log(total integrated post-scale residual norm) + object fixed effects; object-cluster robust covariance",
        "common_support": support,
        "retained_rows_by_method": retained,
        "retained_fraction_by_method": {c: retained[c] / 150 for c in METHODS},
        "n_objects_in_retained_set": int(kept.object_uid.nunique()),
        "contrasts_at_mean_log_dose": contrasts,
        "limitation": "same-cohort post-lock sensitivity; conditional associations do not identify equal-dose causality",
    }


def pairwise_dose_sensitivity(metrics: pd.DataFrame, doses: dict[str, dict], metric: str) -> dict:
    """Post-outcome sensitivity, uniformly applied to all eight H4 pairs."""
    from patsy import build_design_matrices

    output, family_p = {}, {}
    for condition in CONDITIONS:
        pair = metrics[metrics.condition.isin(("layer_llh", condition))][
            ["object_uid", "condition", metric]].copy()
        pair["dose"] = [doses[c]["per_object"][uid]["total_integrated_postscale_norm"]
                        for uid, c in zip(pair.object_uid, pair.condition)]
        by_condition = pair.groupby("condition").dose
        intervals = {c: [float(by_condition.get_group(c).quantile(.05)),
                         float(by_condition.get_group(c).quantile(.95))]
                     for c in ("layer_llh", condition)}
        lower, upper = max(v[0] for v in intervals.values()), min(v[1] for v in intervals.values())
        raw_p = 1.0
        if lower >= upper:
            output[condition] = {"status": "no_pairwise_common_support",
                                 "method_intervals": intervals,
                                 "common_support": None}
        else:
            selected = pair[pair.dose.between(lower, upper)].copy()
            counts = selected.groupby("condition").object_uid.nunique().to_dict()
            complete = set(selected[selected.condition == "layer_llh"].object_uid) & \
                set(selected[selected.condition == condition].object_uid)
            selected = selected[selected.object_uid.isin(complete)].copy()
            if len(complete) < 20:
                output[condition] = {
                    "status": "common_support_too_sparse", "method_intervals": intervals,
                    "common_support": [lower, upper], "complete_object_count": len(complete),
                    "retained_rows_by_method": {k: int(v) for k, v in counts.items()},
                }
            else:
                selected["log_dose"] = np.log(selected.dose)
                fit = smf.ols(f"{metric} ~ C(condition) + log_dose + C(object_uid)",
                              data=selected).fit(
                    cov_type="cluster", cov_kwds={"groups": selected.object_uid})
                design = fit.model.data.design_info
                reference_uid = sorted(complete)[0]
                mean_log_dose = float(selected.log_dose.mean())
                grid = pd.DataFrame([
                    {"condition": c, "object_uid": reference_uid, "log_dose": mean_log_dose}
                    for c in ("layer_llh", condition)
                ])
                x = np.asarray(build_design_matrices([design], grid)[0])
                contrast = x[0] - x[1]
                estimate = float(contrast @ fit.params)
                se = float(np.sqrt(contrast @ fit.cov_params() @ contrast))
                raw_p = float(np.asarray(fit.t_test(contrast).pvalue).squeeze())
                output[condition] = {
                    "status": "fit_on_pairwise_common_support",
                    "method_intervals": intervals, "common_support": [lower, upper],
                    "complete_object_count": len(complete),
                    "retained_rows_by_method": {"layer_llh": len(complete), condition: len(complete)},
                    "model": f"{metric} ~ method + log(total integrated post-scale norm) + object fixed effects; clustered by object",
                    "LLH_minus_schedule_at_mean_log_dose": estimate,
                    "cluster_robust_ci95": [estimate - 1.96 * se, estimate + 1.96 * se],
                    "p_two_sided_unadjusted": raw_p,
                }
        family_p[condition] = raw_p if raw_p > 0 else 1e-300
    adjusted = analyze_v3.holm(family_p)
    for condition in CONDITIONS:
        output[condition]["p_holm_eight_pairwise_sensitivities"] = adjusted[condition]
    return {
        "status": "post-outcome exploratory sensitivity; not H4 confirmation",
        "family_size": 8,
        "holm_p_by_pair": adjusted,
        "comparisons": output,
        "not_estimable_slots_conservatively_assigned_p_one": True,
    }


def effect_text(stat: dict, digits: int = 3, *, with_win: bool = True) -> str:
    mean = float(stat["mean_delta"])
    lo, hi = map(float, stat["ci95"])
    value = f"{mean:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"
    return value + (f"; {100 * stat['favorable_rate']:.1f}% win" if with_win else "")


def write_report(result: dict) -> None:
    lines = [
        "# Final generic-schedule comparison — FRESH_CONFIRM_B", "",
        "**Evidence class:** post-lock, same-cohort sensitivity; not independent confirmation. The independent pre-outcome Experiment C on FRESH_CONFIRM_300 remains separate and is not pooled with this result.", "",
        "The eight extension conditions were generated for the frozen 150-object B cohort with the same checkpoint, runner, inputs, seed policy, and native cap path as `layer_llh`. The extension passed its integrity gate. The contemporaneous provenance note records one accidental raw-row exposure before that gate and a duplicate runner launch that was stopped during model loading; neither was used to change the locked conditions, analysis family, objects, or rows. See `B_GENERIC_EXTENSION_EARLY_ROW_EXPOSURE_NOTE_20261005.md`.", "",
        "The locked H4 comparison reports LLH minus each generic schedule. Positive FG-PSNR and negative FG-LPIPS favor LLH. Intervals are paired object bootstrap 95% CIs (10,000 draws, seed 20261002); Holm correction is separate across the eight schedules for each metric.", "",
        "## Locked paired H4 comparisons", "",
        "| Schedule | FG-PSNR Δ [95% CI]; win; Holm p | FG-LPIPS Δ [95% CI]; win; Holm p |",
        "|---|---:|---:|",
    ]
    for condition, stats in result["contrasts"].items():
        parts = []
        for metric in ("fg_psnr", "fg_lpips"):
            stat = stats[metric]
            p = stat["p_raw_upper_bound"]
            hp = result["holm_by_metric"][metric][condition]["p_holm_upper_bound"]
            holm = f"≤{hp:.4f}" if isinstance(p, str) and p.startswith("<=") else f"{hp:.4f}"
            parts.append(f"{effect_text(stat, 4)}; Holm {holm}")
        lines.append(f"| `{condition}` | {parts[0]} | {parts[1]} |")

    secondary = ("full_psnr", "full_lpips", "fg_ssim", "edge_ssim", "full_ssim")
    lines += ["", "## Co-reported fidelity and structure outcomes", "",
              "Descriptive, unadjusted paired effects; these metrics are not added to the frozen H4 Holm families.", "",
              "| Schedule | Full-PSNR | Full-LPIPS | FG-SSIM | Edge-SSIM | Full-SSIM |",
              "|---|---:|---:|---:|---:|---:|"]
    for condition, stats in result["contrasts"].items():
        values = [effect_text(stats[m], 4) for m in secondary]
        lines.append("| `" + condition + "` | " + " | ".join(values) + " |")

    texture_cols = ("ciede2000", "logerr_laplacian_variance", "logerr_rgb_std",
                    "logerr_gradient_magnitude", "logerr_hf_energy")
    labels = ("CIEDE2000", "Laplacian log error", "RGB-std log error",
              "Gradient log error", "HF-energy log error")
    lines += ["", "## GT-relative color and texture diagnostics", "",
              "Negative deltas favor LLH because lower color/texture error is better. These remain descriptive and do not substitute for human preference.", "",
              "| Schedule | " + " | ".join(labels) + " |",
              "|---|" + "---:|" * len(labels)]
    for condition in result["contrasts"]:
        vals = [effect_text(result["texture_contrasts"][condition][m], 4)
                for m in texture_cols]
        lines.append("| `" + condition + "` | " + " | ".join(vals) + " |")

    lines += ["", "## Requested scales, caps, and realized residual norms", "",
              "Requested/applied scale entries are sums across the 50 frozen steps, ordered deep/middle/shallow. All nine methods use the native capped forward path; no cap activated in these conditions. Residual norms are measured from the actual post-scale wrapper corrections, summed over steps; squared norm is the sum of wrapper `l2²` values.", "",
              "| Method | Requested = applied scale sums (D/M/S) | Cap activation (D/M/S) | Mean integrated norm | Mean squared norm |",
              "|---|---:|---:|---:|---:|"]
    for condition, summary in result["dose_summaries"].items():
        req = summary["requested_scale_integral_50_steps"]
        app = summary["applied_scale_integral_50_steps"]
        scales = "/".join(f"{req[l]:.2f}" for l in LAYERS)
        if any(abs(req[l] - app[l]) > 1e-9 for l in LAYERS):
            scales += " (applied " + "/".join(f"{app[l]:.2f}" for l in LAYERS) + ")"
        caps = "/".join(f"{100*summary['cap_activation_fraction_by_step'][l]:.0f}%" for l in LAYERS)
        norm = summary["total_integrated_postscale_norm"]["mean"]
        sq = summary["total_squared_postscale_norm"]["mean"]
        lines.append(f"| `{condition}` | {scales} | {caps} | {norm:,.0f} | {sq:,.0f} |")

    dose_sens = result["dose_adjusted"]["fg_psnr"]
    support = dose_sens.get("common_support", {})
    lines += ["", "## Actual-dose sensitivity", "",
              "The all-nine-method central-90% dose intersection is empty: the largest method-specific lower bound is "
              f"{support.get('lower', float('nan')):,.0f}, while the smallest upper bound is "
              f"{support.get('upper', float('nan')):,.0f}. A single dose-adjusted model covering all nine methods is therefore not estimable without extrapolation. The complete method-specific 5th–95th intervals are in the authoritative JSON.", "",
              "A supplemental pairwise common-support model was added after the extension results were opened and is explicitly exploratory. It uses one fixed rule for all eight pairs, complete objects only, log total post-scale norm, object fixed effects, and Holm across all eight pairs per endpoint. The four budget-matched profiles had pairwise support, but none of their conditional contrasts was significant after the eight-slot Holm correction; intervals were wide. The endpoint-matched linear and Gaussian comparisons were too sparse for 20 complete pairs, and cosine/trapezoid endpoint-matched conditions had no dose overlap with LLH. This analysis does not establish that dose explains the raw advantages; it shows the current cohort cannot separate schedule shape from realized dose with adequate precision.", "",
              "## Interpretation", "",
              "1. LLH was not detectably different from endpoint-matched linear warm-up on FG-PSNR (mean −0.037 dB; 95% CI [−0.083, +0.009]); on FG-LPIPS the mean contrast favored linear warm-up by 0.00109 (Holm p=0.0024). This differs in LPIPS direction from the earlier FRESH_CONFIRM_300 Experiment C; the cohorts are not pooled. H4 froze no practical-equivalence margin, so the PSNR null is not an equivalence result.",
              "2. In the locked paired family, LLH had favorable mean FG-PSNR and FG-LPIPS contrasts against all four nominal-budget-matched schedules. The PSNR advantage over budget-matched linear was small (+0.097 dB); effects against cosine, trapezoid, and Gaussian were larger. No cap activated in any of these nine methods.",
              "3. Nominal per-layer requested means do not equalize realized correction dose. The budget-matched schedules had mean integrated total norms about 0.5%–2.1% above LLH, while the endpoint-matched schedules were about 7.0%–25.7% higher. The squared-norm ordering differs slightly. Because the nine-method dose supports do not overlap and the pairwise post-outcome models are imprecise, the B extension does not establish superiority after controlling actual dose.",
              "4. The B extension is post-lock and same-cohort. It is useful as a sensitivity check, not an independent H4 confirmation. The defensible contribution remains allocation characterization; a universal best-schedule claim is not supported by these data.", "",
              "## Provenance", "",
              "- Integrity gate: `B_GENERIC_EXTENSION_INTEGRITY_GATE.md` (PASS; 1,200/1,200 rows).",
              "- Frozen extension: `FRESH_CONFIRM_B_GENERIC_EXTENSION_LOCK_20261005.md`.",
              "- Pairwise and dose results: `formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005/FRESH_CONFIRM_B_GENERIC_EXTENSION_ANALYSIS.json`.",
              "- Analysis choices for the all-nine dose model: `GENERIC_RESIDUAL_DOSE_SENSITIVITY_PLAN_20261005.md`.",
              "- Post-outcome pairwise-dose note: `GENERIC_PAIRWISE_DOSE_SENSITIVITY_NOTE_20261005.md`.",
              "- Early exposure/duplicate launch: `B_GENERIC_EXTENSION_EARLY_ROW_EXPOSURE_NOTE_20261005.md`.", ""]
    (V3 / "FINAL_GENERIC_SCHEDULE_COMPARISON.md").write_text("\n".join(lines))


def main() -> None:
    gate = (V3 / "B_GENERIC_EXTENSION_INTEGRITY_GATE.md").read_text()
    if "FRESH_CONFIRM_B_GENERIC_EXTENSION_INTEGRITY = PASS" not in gate:
        raise SystemExit("Generic extension integrity gate is not PASS.")
    uids = [x.strip() for x in COHORT.read_text().splitlines() if x.strip()]
    ext_metrics = load_csv(EXT / "per_object_metrics.csv")
    core_metrics = load_csv(CORE / "per_object_metrics.csv")
    if set(ext_metrics.condition.unique()) != set(CONDITIONS) or len(ext_metrics) != 1200:
        raise SystemExit("Extension metric rows differ from the frozen 1,200-row family.")
    core_llh = core_metrics[core_metrics.condition == "layer_llh"]
    if len(core_llh) != 150 or set(core_llh.object_uid) != set(uids):
        raise SystemExit("Main-run LLH comparator coverage is not 150/150.")
    metrics = pd.concat([core_llh, ext_metrics], ignore_index=True)
    if metrics.duplicated(["object_uid", "condition"]).any():
        raise SystemExit("Duplicate object-condition rows in analysis inputs.")
    if set(metrics.condition.unique()) != set(METHODS):
        raise SystemExit("Analysis condition registry differs from the frozen nine methods.")
    # GT-relative texture errors use the same per-object extended metrics as
    # the frozen inference runner; CIEDE2000 is separately recomputed below.
    for name, pred_col, gt_col in (
        ("logerr_laplacian_variance", "fg_lap_var", "gt_fg_lap_var"),
        ("logerr_rgb_std", "fg_rgb_std", "gt_fg_rgb_std"),
        ("logerr_gradient_magnitude", "fg_grad_mag", "gt_fg_grad_mag"),
        ("logerr_hf_energy", "fg_hf_energy", "gt_fg_hf_energy"),
    ):
        pred = metrics[pred_col].to_numpy(dtype=float)
        gt = metrics[gt_col].to_numpy(dtype=float)
        if not np.isfinite(pred).all() or not np.isfinite(gt).all() or np.any(pred < 0) or np.any(gt < 0):
            raise SystemExit(f"Invalid texture values in {pred_col}/{gt_col}.")
        metrics[name] = np.abs(np.log((pred + 1e-6) / (gt + 1e-6)))
    manifests = {
        "layer_llh": json.loads((CORE / "run_manifest_shard0.json").read_text()),
        **{c: json.loads((EXT / "run_manifest_shard0.json").read_text()) for c in CONDITIONS},
    }
    doses = {c: residual_dose(CORE if c == "layer_llh" else EXT, c, uids, manifests[c])
             for c in METHODS}

    result = {
        "scope": "post-lock within-cohort sensitivity; not independent confirmation",
        "cohort": "FRESH_CONFIRM_B", "n_objects": 150,
        "bootstrap_draws": analyze_v3.BOOT_N, "bootstrap_seed": analyze_v3.BOOT_SEED,
        "holm_family_size_per_metric": 8,
        "dose_summaries": {c: doses[c]["summary"] for c in METHODS},
        "contrasts": {}, "dose_adjusted": {},
        "pairwise_dose_sensitivity": {},
    }
    family_p = {m: {} for m in ("fg_psnr", "fg_lpips")}
    for condition in CONDITIONS:
        a = metrics[metrics.condition == "layer_llh"].set_index("object_uid").loc[uids]
        b = metrics[metrics.condition == condition].set_index("object_uid").loc[uids]
        result["contrasts"][condition] = {}
        for metric in METRICS:
            stat = paired_summary(a[metric].to_numpy(), b[metric].to_numpy(), metric)
            result["contrasts"][condition][metric] = stat
            if metric in family_p:
                family_p[metric][condition] = float(stat["p_bootstrap"])
    result["holm_by_metric"] = {
        metric: {condition: {"p_holm_upper_bound": float(p),
                             "reject_holm_0.05": bool(p < 0.05)}
                 for condition, p in analyze_v3.holm(values).items()}
        for metric, values in family_p.items()
    }

    texture_ext = load_csv(EXT / "texture_extension_per_object.csv")
    texture_core = load_csv(CORE / "texture_extension_per_object.csv")
    if set(texture_ext.object_uid) != set(uids) or set(texture_core.object_uid) != set(uids):
        raise SystemExit("Texture extension cohort differs from frozen 150 objects.")
    tex = texture_ext.set_index("object_uid").join(texture_core.set_index("object_uid"),
                                                    lsuffix="_ext", rsuffix="_core")
    result["texture_contrasts"] = {}
    for condition in CONDITIONS:
        result["texture_contrasts"][condition] = {}
        for col in TEXTURE_COLUMNS:
            if col == "ciede2000":
                left, right = f"layer_llh:{col}", f"{condition}:{col}"
                if left not in tex or right not in tex:
                    raise SystemExit(f"Texture-extension metric missing: {left} or {right}")
                va, vb = tex.loc[uids, left].to_numpy(dtype=float), tex.loc[uids, right].to_numpy(dtype=float)
            else:
                va = metrics[metrics.condition == "layer_llh"].set_index("object_uid").loc[uids, col].to_numpy(dtype=float)
                vb = metrics[metrics.condition == condition].set_index("object_uid").loc[uids, col].to_numpy(dtype=float)
            result["texture_contrasts"][condition][col] = paired_summary(
                va, vb, col)

    for metric in ("fg_psnr", "fg_lpips"):
        result["dose_adjusted"][metric] = dose_adjusted(metrics, doses, metric)
        result["pairwise_dose_sensitivity"][metric] = pairwise_dose_sensitivity(metrics, doses, metric)
    output = EXT / "FRESH_CONFIRM_B_GENERIC_EXTENSION_ANALYSIS.json"
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    write_report(result)
    print(f"Wrote locked generic-extension analysis: {output}")


if __name__ == "__main__":
    main()
