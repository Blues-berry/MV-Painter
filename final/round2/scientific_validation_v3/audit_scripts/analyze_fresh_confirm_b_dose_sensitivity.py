#!/usr/bin/env python3
"""Locked dose-only extraction and sensitivity models for the B A3b map."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
COHORT = V3 / "fresh_confirm_b/fresh_confirm_B_150.txt"
LAYERS = ("deep", "middle", "shallow")
WINDOWS = tuple(range(1, 6))
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
METRICS = ("fg_lpips", "fg_psnr", "full_psnr", "full_lpips", "fg_ssim",
           "edge_ssim", "fg_lap_var", "fg_rgb_std", "fg_grad_mag", "fg_hf_energy")
sys.path.insert(0, str(V3))
sys.path.insert(0, str(V3 / "audit_scripts"))
sys.path.insert(0, str(ROOT))
import analyze_v3  # noqa: E402
from audit_interaction_valid_test import wald_interaction  # noqa: E402


def layer_step_norm(entries: dict, layer: str) -> float:
    values = [float(e["l2"]) for e in entries.values() if e["depth"] == layer]
    if not values:
        raise ValueError(f"No residual wrappers for layer {layer}.")
    return math.sqrt(sum(x * x for x in values))


def interaction_test(frame: pd.DataFrame, metric: str, *, dose_term: str | None = None) -> dict:
    fields = ["object_uid", "layer", "window", f"delta_{metric}"]
    if dose_term:
        fields.append(dose_term)
    data = frame[fields].dropna().copy()
    if not dose_term:
        data["dose_z"] = 0.0
        dose_term = "dose_z"
    formula = f"delta_{metric} ~ C(layer) * C(window) + {dose_term} + C(object_uid)"
    fit = smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data.object_uid})
    design = fit.model.data.design_info
    term = "C(layer):C(window)"
    sl = design.term_name_slices[term]
    indices = list(range(sl.start, sl.stop))
    restriction = np.eye(len(fit.params))[indices]
    test = fit.wald_test(restriction, scalar=True)
    p = float(test.pvalue)
    interaction_df = int(len(indices))

    # Marginal fitted cell means at the same dose and reference-object level;
    # the two-way interaction projection removes both main effects.
    from patsy import build_design_matrices
    first_uid = sorted(data.object_uid.unique())[0]
    mean_dose = float(data[dose_term].mean())
    grid = pd.DataFrame([{"layer": l, "window": f"W{w}", "object_uid": first_uid,
                          dose_term: mean_dose}
                         for l in LAYERS for w in WINDOWS])
    x = np.asarray(build_design_matrices([design], grid)[0])
    cellmeans = (x @ np.asarray(fit.params)).reshape(3, 5)
    component = cellmeans - cellmeans.mean(axis=1, keepdims=True) \
        - cellmeans.mean(axis=0, keepdims=True) + cellmeans.mean()
    beta = float(fit.params[dose_term])
    ci = [float(v) for v in fit.conf_int().loc[dose_term].tolist()]
    return {
        "n_rows": int(len(data)), "n_objects": int(data.object_uid.nunique()),
        "model": formula, "interaction_df": interaction_df,
        "interaction_wald_chi2": float(test.statistic),
        "interaction_p_raw": p if p > 0 else None,
        "interaction_p_upper_bound": None if p > 0 else "<=1e-300",
        "interaction_rmse_per_cell_at_mean_dose": float(np.sqrt(np.mean(component ** 2))),
        "dose_coefficient": beta, "dose_coefficient_ci95": ci,
        "dose_coefficient_p_unadjusted": float(np.asarray(fit.t_test(f"{dose_term}=0").pvalue).squeeze()),
        "full_rank": bool(np.linalg.matrix_rank(np.asarray(fit.model.exog)) == fit.model.exog.shape[1]),
    }


def cell_effect_means(table: pd.DataFrame, baseline_name: str, condition_prefix: str,
                      metric: str) -> dict[str, float]:
    baseline = table[table.condition == baseline_name].set_index("object_uid")[metric]
    if baseline.empty or baseline.index.has_duplicates:
        raise SystemExit(f"Triangulation baseline is missing or duplicated: {baseline_name}.")
    means = {}
    for layer in LAYERS:
        for window in WINDOWS:
            name = f"{condition_prefix}{layer}_W{window}"
            values = table[table.condition == name].set_index("object_uid")[metric]
            if values.index.has_duplicates or set(values.index) != set(baseline.index):
                raise SystemExit(f"Triangulation pairing differs for {name}.")
            means[f"{layer}_W{window}"] = float((values.loc[baseline.index] - baseline).mean())
    return means


def triangulate_maps(current_b: pd.DataFrame) -> dict:
    a2 = pd.read_csv(V3 / "formal/campaign_A2/per_object_metrics.csv")
    a3 = pd.read_csv(V3 / "formal/campaign_A3/per_object_metrics.csv")
    historical = {
        "A2_native_300": (a2, "a_baseline", "a_"),
        "A3_dose_normalized_300": (a3, "a3_baseline", "a3_"),
        "A3b_bounded_B150": (current_b, "a3_baseline", "a3_"),
    }
    deep_identity = {}
    for window in WINDOWS:
        left = a2[a2.condition == f"a_deep_W{window}"].set_index("object_uid")
        right = a3[a3.condition == f"a3_deep_W{window}"].set_index("object_uid")
        deep_identity[f"W{window}"] = (
            set(left.index) == set(right.index)
            and np.array_equal(left.loc[sorted(left.index), ["fg_lpips", "fg_psnr"]].to_numpy(),
                               right.loc[sorted(right.index), ["fg_lpips", "fg_psnr"]].to_numpy())
        )

    output = {"comparison_unit": "15 cell-level mean effects; descriptive only, no inferential p-values",
              "a2_and_a3_share_fresh_confirm_300": True,
              "deep_a2_a3_objectwise_identical_by_window": deep_identity,
              "maps": {}, "pairwise": {}}
    for metric in ("fg_lpips", "fg_psnr"):
        maps = {
            name: cell_effect_means(table, baseline, prefix, metric)
            for name, (table, baseline, prefix) in historical.items()
        }
        output["maps"][metric] = maps
        output["pairwise"][metric] = {}
        names = list(maps)
        for i, left_name in enumerate(names):
            for right_name in names[i + 1:]:
                left = np.asarray(list(maps[left_name].values()), dtype=float)
                right = np.asarray(list(maps[right_name].values()), dtype=float)
                output["pairwise"][metric][f"{left_name}__vs__{right_name}"] = {
                    "pearson_r": float(np.corrcoef(left, right)[0, 1]),
                    "spearman_rho": float(pd.Series(left).corr(pd.Series(right), method="spearman")),
                    "same_sign_cells": int(np.sum(np.sign(left) == np.sign(right))),
                    "n_cells": int(len(left)),
                }
    return output


def write_report(output: dict) -> None:
    def p_text(value, bound=None) -> str:
        return bound if value is None else f"{float(value):.3g}"

    lines = [
        "# Residual-dose sensitivity analysis — FRESH_CONFIRM_B A3b", "",
        "**Evidence class:** post-outcome sensitivity on the already opened FRESH_CONFIRM_B cohort; not an independent or equal-dose confirmation. The A3b map and its frozen 16-test endpoint families remain primary. Dose regressions condition on observed post-treatment residual norms and cannot reconstruct counterfactual equal-dose interventions.", "",
        "The object-cell artifact contains all 150 × 3 layers × 5 windows = 2,250 unique paired rows. For each cell it records active-window integrated post-scale norm, squared correction norm, corresponding baseline dose, net changes, full-window dose, frozen development increment proxy, and metric deltas. Residual logs and manifest scale semantics are authoritative.", "",
        "## Realized dose and overlap", "",
        "| Layer | Mean active integrated norm | Mean active squared norm | Mean net norm change vs baseline | Mean frozen increment proxy | Central 90% active-dose interval |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for layer in LAYERS:
        summary = output["dose_summary_by_layer"][layer]
        lo, hi = output["common_support"]["layer_central_90_intervals"][layer]
        lines.append(
            f"| {layer} | {summary['active_postscale_norm_mean']:,.1f} "
            f"| {summary['active_squared_norm_mean']:,.0f} "
            f"| {summary['net_norm_change_mean']:,.1f} "
            f"| {summary['increment_proxy_mean']:,.1f} "
            f"| [{lo:,.1f}, {hi:,.1f}] |"
        )
    lines += [
        "", "No layer-level central-90 dose overlap exists: deep spans 56,359–79,927, middle 11,421–19,336, and shallow 2,816–5,193. The pre-frozen common-support rule therefore retains 0/2,250 rows; no common-support interaction estimate is available. The cap activation fraction is 0% for all layers; shallow's requested high value equals its native ceiling but was not clipped.", "",
        "## Dose-adjusted interaction models", "",
        "Both models include categorical Layer × Window terms and object fixed effects, with object-cluster robust covariance. The linear model uses centered active-window integrated norm; the nonlinear sensitivity uses log norm. These are conditional associations; dose is post-treatment and the layer dose ranges do not overlap.", "",
        "| Endpoint | Dose term | Interaction Wald (df=8) | Raw p | Holm p, six-slot family | Interaction RMSE per cell | Dose coefficient [95% CI] | Dose p |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        slots = output["six_slot_holm_families_by_metric"][metric]
        for model_key, model_label, slot in (
            ("all_rows_linear_dose", "centered linear norm", "linear_dose"),
            ("all_rows_log_dose", "log norm", "log_dose"),
        ):
            model = output["models"][metric][model_key]
            lo, hi = model["dose_coefficient_ci95"]
            lines.append(
                f"| {label} | {model_label} | W={model['interaction_wald_chi2']:.3f} "
                f"| {p_text(model['interaction_p_raw'], model['interaction_p_upper_bound'])} "
                f"| {slots[slot]['holm_p']:.3g} "
                f"| {model['interaction_rmse_per_cell_at_mean_dose']:.6g} "
                f"| {model['dose_coefficient']:+.4g} [{lo:+.4g}, {hi:+.4g}] "
                f"| {model['dose_coefficient_p_unadjusted']:.3g} |"
            )

    lines += ["", "The Layer × Window test remains significant under both prespecified parametric adjustments. The interaction RMSE is 0.000499/0.000341 FG-LPIPS and 0.0463/0.0402 dB FG-PSNR for linear/log dose, respectively. These fits are extrapolative across the separated layer dose ranges: significance after a linear or log covariate does not establish dose independence.", "", "## Dose-stratified analysis", ""]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        tertiles = output["models"][metric]["dose_tertiles"]
        lines.append(f"For {label}, pooled dose-only tertile cutpoints are {tertiles['cutpoints'][0]:,.1f} and {tertiles['cutpoints'][1]:,.1f}.")
        for tertile, result in tertiles["strata"].items():
            counts = result["cell_counts"]
            layer_counts = {layer: sum(n for key, n in counts.items() if key.startswith(layer + "_"))
                            for layer in LAYERS}
            lines.append(f"- Tertile {tertile}: not estimable as a 3-layer interaction; rows by layer are {layer_counts}.")
    lines += [
        "",
        "Because the pooled tertiles separate layers by their native residual-norm scale, none contains all three layers. This is the same support failure expressed as strata; the planned 3×5 within-tertile interaction cannot be estimated. Non-estimable slots were conservatively assigned p=1 in each six-slot Holm family.",
        "", "## Cross-experiment triangulation", "",
        "Cell-mean directions are compared descriptively across the 15 map cells; no p-values are assigned to these correlations. A2 and A3 both use FRESH_CONFIRM_300, and all five A3 deep cells are objectwise identical to A2. They are not independent replications. A3b uses the disjoint FRESH_CONFIRM_B cohort.", "",
        "| Metric | Map pair | Pearson r | Spearman ρ | Same-sign cells |",
        "|---|---|---:|---:|---:|",
    ]
    triangulation = output["cross_experiment_triangulation"]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        for pair, result in triangulation["pairwise"][metric].items():
            left, right = pair.split("__vs__")
            lines.append(
                f"| {label} | {left} vs {right} | {result['pearson_r']:.3f} "
                f"| {result['spearman_rho']:.3f} | {result['same_sign_cells']}/15 |"
            )
    lines += [
        "", "Against A2's native-dose map, the fresh B bounded map has the same mean-effect sign in 14/15 FG-LPIPS cells and 13/15 FG-PSNR cells, but the magnitudes are much smaller and this 15-cell sign count is descriptive. Against A3's high-dose map, sign agreement is 13/15 for FG-LPIPS and 9/15 for FG-PSNR; the shallow A3 stress regime is especially unlike the bounded map. The direction pattern is partly reproducible at native/bounded scales, while magnitude and some metric responses change with dose regime.", "",
        "## Interpretation", "",
        "The bounded-map interaction survives linear and log dose adjustment, but the actual-dose support is completely separated by layer and the dose-tertile models cannot include all three layers. Therefore dose confounding remains unresolved for a dose-independent Layer × Window mechanism. The model results do not show that actual dose is irrelevant; they show that this cohort cannot identify its independent contribution without extrapolation.",
        "",
        "Do not call A3b equal-dose, do not describe the sensitivity models as causal dose control, and do not tune a new map on FRESH_CONFIRM_B. Whether a third untouched cohort with a directly norm-controlled diagnostic is necessary should be decided only after the full evidence and narrative gate; it must not be run merely to seek a favorable result.",
        "", "## Provenance", "",
        "- Frozen analysis plan: `RESIDUAL_DOSE_SENSITIVITY_ANALYSIS_PLAN_20261005.md`.",
        "- A3b protocol and scale bounds: `A3B_PROTOCOL_LOCK.md` and `A3B_DOSE_FEASIBILITY_AUDIT.md`.",
        "- Full model results: `formal/campaign_FRESH_CONFIRM_B_20261005/RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.json`.",
        "- Per-object × cell dose table: `formal/campaign_FRESH_CONFIRM_B_20261005/RESIDUAL_DOSE_OBJECT_CELL_DATA.csv`.", "",
    ]
    (V3 / "RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    gate = (V3 / "B_FORMAL_INTEGRITY_GATE.md").read_text()
    if "FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS" not in gate:
        raise SystemExit("Main B formal integrity gate is not PASS.")
    uids = [x.strip() for x in COHORT.read_text().splitlines() if x.strip()]
    table = pd.read_csv(RUN / "per_object_metrics.csv")
    manifest = json.loads((RUN / "run_manifest_shard0.json").read_text())
    baseline = table[table.condition == "a3_baseline"].set_index("object_uid")
    if len(uids) != 150 or len(baseline) != 150 or set(baseline.index) != set(uids):
        raise SystemExit("A3b baseline or frozen cohort coverage is not 150/150.")
    spec_path = V3 / "a3b_development_residual_only/A3B_CANDIDATE_HIGHS.json"
    candidate_spec = json.loads(spec_path.read_text())
    spec_sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    if spec_sha != "68125f9ee9645225387ef9d034f934154d6c4c461b29d7162218a224c0cc89a0":
        raise SystemExit("Frozen A3b candidate-spec checksum changed.")
    baseline_trace = manifest["condition_specs"]["a3_baseline"]["scale_trace_requested"]
    if len(baseline_trace) != 50 or any(
        float(step[layer]) != float(candidate_spec["baseline_scales"][layer])
        for layer in LAYERS for step in baseline_trace
    ):
        raise SystemExit("Shared A3b baseline trace differs from the frozen candidate spec.")
    rows = []
    cap_activations = {layer: 0 for layer in LAYERS}
    cap_cells = {layer: 0 for layer in LAYERS}
    requested_trace_summary = {}

    for layer in LAYERS:
        for window in WINDOWS:
            condition = f"a3_{layer}_W{window}"
            condition_spec = manifest["condition_specs"][condition]
            trace = condition_spec["scale_trace_requested"]
            if len(trace) != 50 or condition_spec.get("uncapped"):
                raise SystemExit(f"Unexpected A3b scale or cap semantics in {condition}.")
            base_scale = float(baseline_trace[0][layer])
            high_scale = float(trace[10 * (window - 1)][layer])
            if (base_scale != float(candidate_spec["baseline_scales"][layer])
                    or high_scale != float(candidate_spec["high_values"][layer])):
                raise SystemExit(f"A3b scale differs from frozen candidate spec in {condition}.")
            delta_scale = high_scale - base_scale
            if not (delta_scale > 0 and high_scale <= CAPS[layer]):
                raise SystemExit(f"A3b perturbation is not a bounded positive increment: {condition}.")
            active_start, active_stop = 10 * (window - 1), 10 * window
            for step_idx, step_scales in enumerate(trace):
                for group in LAYERS:
                    expected = (high_scale if group == layer and active_start <= step_idx < active_stop
                                else float(candidate_spec["baseline_scales"][group]))
                    if float(step_scales[group]) != expected:
                        raise SystemExit(f"A3b trace differs from the frozen cell definition: {condition}/{step_idx}/{group}.")
            requested_trace_summary[condition] = {
                "baseline_scale": base_scale, "high_scale": high_scale,
                "requested_delta": delta_scale,
                "requested_integral_by_layer": {
                    g: float(sum(float(s[g]) for s in trace)) for g in LAYERS},
                "applied_integral_by_layer": {
                    g: float(sum(min(float(s[g]), CAPS[g]) for s in trace)) for g in LAYERS},
            }
            cond_rows = table[table.condition == condition].set_index("object_uid")
            if len(cond_rows) != 150 or set(cond_rows.index) != set(uids):
                raise SystemExit(f"A3b cell pairing failure for {condition}.")
            for uid in uids:
                log = json.loads((RUN / "residual_logs" / condition / f"{uid}.json").read_text())
                base_log = json.loads((RUN / "residual_logs" / "a3_baseline" / f"{uid}.json").read_text())
                active_norm, active_sq, baseline_norm, baseline_sq, proxy = 0.0, 0.0, 0.0, 0.0, 0.0
                full_norm = full_sq = 0.0
                for step in range(50):
                    entries = log[str(step)]
                    layer_norm = layer_step_norm(entries, layer)
                    layer_sq = sum(float(e["l2"]) ** 2 for e in entries.values() if e["depth"] == layer)
                    full_norm += layer_norm
                    full_sq += layer_sq
                    for e in entries.values():
                        group = e["depth"]
                        requested = float(e["scale"])
                        effective = min(requested, CAPS[group])
                        if requested != float(trace[step][group]) or float(e["eff_scale"]) != effective:
                            raise ValueError(f"Manifest/residual scale mismatch at {condition}/{uid}/{step}.")
                        cap_cells[group] += 1
                        cap_activations[group] += int(requested > CAPS[group])
                    if active_start <= step < active_stop:
                        base_entries = base_log[str(step)]
                        active_norm += layer_norm
                        active_sq += layer_sq
                        baseline_norm += layer_step_norm(base_entries, layer)
                        baseline_sq += sum(float(e["l2"]) ** 2 for e in base_entries.values()
                                           if e["depth"] == layer)
                        proxy += delta_scale * layer_norm / high_scale
                metric_deltas = {f"delta_{m}": float(cond_rows.loc[uid, m]) - float(baseline.loc[uid, m])
                                 for m in METRICS}
                rows.append({
                    "object_uid": uid, "layer": layer, "window": f"W{window}",
                    "condition": condition, "active_postscale_norm": active_norm,
                    "active_squared_postscale_norm": active_sq,
                    "baseline_active_postscale_norm": baseline_norm,
                    "baseline_active_squared_postscale_norm": baseline_sq,
                    "net_active_postscale_norm_change": active_norm - baseline_norm,
                    "net_active_squared_norm_change": active_sq - baseline_sq,
                    "full_layer_integrated_postscale_norm": full_norm,
                    "full_layer_squared_postscale_norm": full_sq,
                    "increment_proxy_frozen_calibration": proxy,
                    **metric_deltas,
                })

    frame = pd.DataFrame(rows)
    if len(frame) != 2250 or frame.duplicated(["object_uid", "layer", "window"]).any():
        raise SystemExit("A3b dose table is not a unique 150×3×5 map.")
    csv_path = RUN / "RESIDUAL_DOSE_OBJECT_CELL_DATA.csv"
    frame.to_csv(csv_path, index=False)

    layer_summary = {}
    for layer in LAYERS:
        x = frame[frame.layer == layer]
        layer_summary[layer] = {
            "n_rows": int(len(x)),
            "active_postscale_norm_mean": float(x.active_postscale_norm.mean()),
            "active_postscale_norm_median": float(x.active_postscale_norm.median()),
            "active_squared_norm_mean": float(x.active_squared_postscale_norm.mean()),
            "active_squared_norm_median": float(x.active_squared_postscale_norm.median()),
            "net_norm_change_mean": float(x.net_active_postscale_norm_change.mean()),
            "increment_proxy_mean": float(x.increment_proxy_frozen_calibration.mean()),
            "increment_proxy_median": float(x.increment_proxy_frozen_calibration.median()),
        }
    support = {}
    intervals = {}
    for layer in LAYERS:
        vals = frame.loc[frame.layer == layer, "active_postscale_norm"]
        intervals[layer] = [float(vals.quantile(.05)), float(vals.quantile(.95))]
    lower = max(v[0] for v in intervals.values())
    upper = min(v[1] for v in intervals.values())
    support["layer_central_90_intervals"] = intervals
    support["common_support"] = [lower, upper] if lower < upper else None
    support["rule"] = "intersection of each layer's 5th-95th percentile active-window actual post-scale norm"

    models = {m: {} for m in ("fg_lpips", "fg_psnr")}
    p_slots = {m: {"linear_dose": 1.0, "log_dose": 1.0,
                   "common_support_linear_dose": 1.0,
                   **{f"tertile_{i}_interaction": 1.0 for i in range(1, 4)}}
               for m in ("fg_lpips", "fg_psnr")}
    for metric in ("fg_lpips", "fg_psnr"):
        work = frame.copy()
        work["dose_centered"] = work.active_postscale_norm - work.active_postscale_norm.mean()
        work["log_dose"] = np.log(work.active_postscale_norm)
        models[metric]["all_rows_linear_dose"] = interaction_test(work, metric, dose_term="dose_centered")
        models[metric]["all_rows_log_dose"] = interaction_test(work, metric, dose_term="log_dose")
        for key in ("all_rows_linear_dose", "all_rows_log_dose"):
            p_slots[metric]["linear_dose" if key.endswith("linear_dose") else "log_dose"] = (
                models[metric][key]["interaction_p_raw"] or 1e-300)

        if support["common_support"]:
            common = frame[frame.active_postscale_norm.between(lower, upper)].copy()
            per_cell = common.groupby(["layer", "window"]).size().reindex(
                pd.MultiIndex.from_product([LAYERS, [f"W{w}" for w in WINDOWS]]), fill_value=0)
            support["retained_rows_by_layer_window"] = {
                f"{idx[0]}_{idx[1]}": int(n) for idx, n in per_cell.items()}
            support["retained_fraction_overall"] = float(len(common) / len(frame))
            support["retained_fraction_by_layer"] = {
                l: float((common.layer == l).sum() / (150 * len(WINDOWS))) for l in LAYERS}
            if per_cell.min() >= 10 and common.layer.nunique() == 3 and common.window.nunique() == 5:
                common["dose_centered"] = common.active_postscale_norm - common.active_postscale_norm.mean()
                models[metric]["common_support_linear_dose"] = interaction_test(
                    common, metric, dose_term="dose_centered")
                p_slots[metric]["common_support_linear_dose"] = (
                    models[metric]["common_support_linear_dose"]["interaction_p_raw"] or 1e-300)
            else:
                models[metric]["common_support_linear_dose"] = {"status": "not_estimable",
                                                                  "minimum_cell_n": int(per_cell.min())}
        else:
            support["retained_fraction_overall"] = 0.0
            models[metric]["common_support_linear_dose"] = {"status": "no_common_support"}

        vals = frame.active_postscale_norm.to_numpy(dtype=float)
        q1, q2 = [float(q) for q in np.quantile(vals, [1/3, 2/3])]
        frame["dose_tertile"] = np.where(vals <= q1, 1, np.where(vals <= q2, 2, 3))
        models[metric]["dose_tertiles"] = {"cutpoints": [q1, q2], "strata": {}}
        for tertile in (1, 2, 3):
            subset = frame[frame.dose_tertile == tertile].copy()
            counts = subset.groupby(["layer", "window"]).size()
            full_index = pd.MultiIndex.from_product([LAYERS, [f"W{w}" for w in WINDOWS]])
            counts = counts.reindex(full_index, fill_value=0)
            key = f"tertile_{tertile}_interaction"
            if counts.min() >= 10:
                subset["dose_centered"] = subset.active_postscale_norm - subset.active_postscale_norm.mean()
                fitted = interaction_test(subset, metric, dose_term="dose_centered")
                models[metric]["dose_tertiles"]["strata"][str(tertile)] = {
                    **fitted,
                    "cell_counts": {f"{i[0]}_{i[1]}": int(n) for i, n in counts.items()},
                }
                p_slots[metric][key] = fitted["interaction_p_raw"] or 1e-300
            else:
                models[metric]["dose_tertiles"]["strata"][str(tertile)] = {
                    "status": "not_estimable", "cell_counts": {f"{i[0]}_{i[1]}": int(n) for i, n in counts.items()},
                }

    corrected = {metric: analyze_v3.holm(slots) for metric, slots in p_slots.items()}
    output = {
        "cohort": "FRESH_CONFIRM_B", "n_objects": 150,
        "status": "post-outcome dose sensitivity; not dose-balanced confirmation",
        "dose_definition": "wrapper correction tensors are combined by Euclidean norm within layer and step; integrated norm is sum over steps; squared norm is sum of wrapper l2 squared",
        "frozen_conditions": requested_trace_summary,
        "cap_activation_fraction": {layer: cap_activations[layer] / cap_cells[layer] for layer in LAYERS},
        "dose_summary_by_layer": layer_summary,
        "common_support": support,
        "models": models,
        "six_slot_holm_families_by_metric": {
            metric: {slot: {"raw_p": p_slots[metric][slot], "holm_p": corrected[metric][slot],
                            "reject_0.05": bool(corrected[metric][slot] < 0.05)}
                     for slot in p_slots[metric]}
            for metric in p_slots
        },
        "object_cell_csv": str(csv_path),
        "interpretation_limit": "These regressions condition on observed residual norms after treatment; they do not reconstruct a counterfactual equal-dose intervention.",
    }
    output["cross_experiment_triangulation"] = triangulate_maps(table)
    out = RUN / "RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.json"
    out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    write_report(output)
    print(f"Wrote dose-only object-cell table and locked sensitivity results: {out}")


if __name__ == "__main__":
    main()
