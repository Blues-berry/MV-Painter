#!/usr/bin/env python3
"""Locked A3b bounded-dose map analysis for FRESH_CONFIRM_B."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
sys.path.insert(0, str(V3))
sys.path.insert(0, str(V3 / "audit_scripts"))
sys.path.insert(0, str(ROOT))
import analyze_v3  # noqa: E402
from audit_interaction_valid_test import wald_interaction  # noqa: E402

LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)
METRICS = ("fg_lpips", "fg_psnr")
METRIC_DIRECTIONS = {
    "full_psnr": "higher", "full_lpips": "lower", "fg_ssim": "higher",
    "edge_ssim": "higher", "ciede2000": "lower",
    "logerr_laplacian_variance": "lower", "logerr_rgb_std": "lower",
    "logerr_gradient_magnitude": "lower", "logerr_hf_energy": "lower",
}


def load_data() -> tuple[pd.DataFrame, dict]:
    gate = (V3 / "B_FORMAL_INTEGRITY_GATE.md").read_text()
    if "FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS" not in gate:
        raise SystemExit("FRESH_CONFIRM_B formal integrity gate is not PASS.")
    table = pd.read_csv(RUN / "per_object_metrics.csv")
    if len(table) != 4500 or table.object_uid.nunique() != 150 or table.condition.nunique() != 30:
        raise SystemExit("FRESH_CONFIRM_B ledger coverage changed after the integrity gate.")
    manifest = json.loads((RUN / "run_manifest_shard0.json").read_text())
    expected = {"a3_baseline"} | {
        f"a3_{layer}_W{window}" for layer in LAYERS for window in WINDOWS
    }
    if not expected.issubset(set(table.condition.unique())):
        raise SystemExit("A3b condition coverage is incomplete.")
    return table, manifest


def cell_deltas(table: pd.DataFrame, metric: str) -> tuple[dict, pd.DataFrame]:
    base = table[table.condition == "a3_baseline"].set_index("object_uid")
    cells = {}
    long_rows = []
    for layer in LAYERS:
        for window in WINDOWS:
            condition = f"a3_{layer}_W{window}"
            cell = table[table.condition == condition].set_index("object_uid")
            if len(cell) != 150 or set(cell.index) != set(base.index):
                raise SystemExit(f"Paired A3b coverage failure for {condition}.")
            delta = np.asarray([float(cell.loc[u, metric]) - float(base.loc[u, metric])
                                for u in sorted(base.index)], dtype=np.float64)
            cells[(layer, window)] = delta
            for uid, value in zip(sorted(base.index), delta):
                long_rows.append({"object_uid": uid, "layer": layer,
                                  "window": f"W{window}", "delta": float(value)})
    return cells, pd.DataFrame(long_rows)


def summarize_cell(delta: np.ndarray, metric: str) -> dict:
    stat = analyze_v3.paired_bootstrap(delta)
    stat["favorable_rate"] = float(np.mean(delta < 0 if metric == "fg_lpips" else delta > 0))
    stat["ties_rate"] = float(np.mean(delta == 0))
    stat["raw_positive_delta_rate"] = float(np.mean(delta > 0))
    return stat


def metric_values(table: pd.DataFrame, texture: pd.DataFrame, condition: str, metric: str) -> dict[str, float]:
    rows = table[table.condition == condition].set_index("object_uid")
    if metric == "ciede2000":
        key = f"{condition}:ciede2000"
        if key not in texture:
            raise SystemExit(f"CIEDE2000 texture extension missing {key}.")
        return {uid: float(texture.loc[uid, key]) for uid in rows.index}
    if metric.startswith("logerr_"):
        source = metric.removeprefix("logerr_")
        pred_col, gt_col = {
            "laplacian_variance": ("fg_lap_var", "gt_fg_lap_var"),
            "rgb_std": ("fg_rgb_std", "gt_fg_rgb_std"),
            "gradient_magnitude": ("fg_grad_mag", "gt_fg_grad_mag"),
            "hf_energy": ("fg_hf_energy", "gt_fg_hf_energy"),
        }[source]
        from geotex.round2_stats import symmetric_log_error
        return {uid: float(symmetric_log_error(float(row[pred_col]), float(row[gt_col])))
                for uid, row in rows.iterrows()}
    return {uid: float(rows.loc[uid, metric]) for uid in rows.index}


def gee_summary(data: pd.DataFrame) -> dict:
    fit = smf.gee("delta ~ C(layer) * C(window)", groups="object_uid", data=data,
                  cov_struct=sm.cov_struct.Exchangeable(),
                  family=sm.families.Gaussian()).fit()
    design = fit.model.data.design_info
    tests = {}
    for term in ("C(layer)", "C(window)", "C(layer):C(window)"):
        sl = design.term_name_slices[term]
        idx = list(range(sl.start, sl.stop))
        restriction = np.eye(len(fit.params))[idx]
        test = fit.wald_test(restriction, scalar=True)
        p = float(test.pvalue)
        tests[term] = {
            "df": len(idx), "wald_chi2": float(test.statistic),
            "p": p if p > 0 else None,
            "p_upper_bound": None if p > 0 else "<=1e-300",
        }
    main = {k: tests[k]["p"] for k in ("C(layer)", "C(window)")}
    if any(p is None for p in main.values()):
        main_adj = None
    else:
        main_adj = analyze_v3.holm(main)
    for key in ("C(layer)", "C(window)"):
        tests[key]["p_holm_two_main_effects"] = (main_adj[key] if main_adj else "<=2e-300")
    return {
        "model": "Gaussian GEE with categorical Layer*Window, object clusters, exchangeable working correlation, robust sandwich covariance",
        "converged": bool(fit.converged),
        "terms": tests,
    }


def write_report(output: dict) -> None:
    def p_text(value: float | None, upper_bound: str | None = None) -> str:
        return upper_bound if value is None else f"{value:.3g}"

    def interval(stat: dict, digits: int) -> str:
        mean = float(stat["mean_delta"])
        lo, hi = map(float, stat["ci95"])
        return f"{mean:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"

    cell_keys = [f"{layer}_W{window}" for layer in LAYERS for window in WINDOWS]
    lines = [
        "# A3b bounded-dose Layer × Window report — FRESH_CONFIRM_B", "",
        "**Classification: bounded local perturbation map, not equal-dose or dose-matched.** The frozen development calibration missed its ±20% dose-balance target: deep −20.01%, middle −20.20%, shallow +98.98%. The candidate scales were retained without outcome-based retuning.", "",
        "The B campaign passed its 4,500/4,500-row integrity gate before this analysis. This report covers the frozen baseline plus 15 layer-by-window interventions on the same 150 objects. Each cell-minus-baseline effect uses paired object bootstrap (10,000 resamples; seed 20261002). Positive FG-PSNR and negative FG-LPIPS are favorable. Holm families contain the 15 cell contrasts plus the 8-df interaction test, separately for each endpoint.", "",
        "## Locked cell contrasts", "",
        "| Intervention | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ dB [95% CI] | Favorable objects | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in cell_keys:
        lp = output["results"]["fg_lpips"]["cell_contrasts"][key]
        ps = output["results"]["fg_psnr"]["cell_contrasts"][key]
        lines.append(
            f"| `{key}` | {interval(lp, 6)} | {100*lp['favorable_rate']:.1f}% | {lp['p_holm_16']:.3g} "
            f"| {interval(ps, 4)} | {100*ps['favorable_rate']:.1f}% | {ps['p_holm_16']:.3g} |"
        )

    lines += [
        "", "## Interaction evidence and magnitude", "",
        "| Endpoint | Object-cluster Wald (df=8) | Holm p, 16-test family | Interaction share of cell-mean variation | Interaction RMSE per cell | GEE interaction Wald (df=8), p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        result = output["results"][metric]
        interaction = result["interaction"]
        gee = result["gee_crosscheck"]["terms"]["C(layer):C(window)"]
        lines.append(
            f"| {label} | W={interaction['W']:.3f}, p={p_text(interaction['p'], interaction['p_upper_bound'])} "
            f"| {interaction['p_holm_16_upper_bound']:.3g} "
            f"| {100*interaction['interaction_ss_share_of_cell_mean_variation']:.1f}% "
            f"| {interaction['interaction_rmse_per_cell']:.6g} "
            f"| W={gee['wald_chi2']:.3f}, p={p_text(gee['p'], gee['p_upper_bound'])} |"
        )

    lines += ["", "The independently formulated object-cluster Wald and Gaussian GEE both detect Layer × Window heterogeneity. The absolute contrast-space interaction RMSE is 0.000342 FG-LPIPS and 0.0205 dB FG-PSNR; the corresponding interaction accounts for 14.0% and 36.0% of variation among the 15 cell means. The large sample-level significance should therefore be read together with these absolute magnitudes and the unequal realized-dose calibration.", "", "### GEE main-effect cross-check", "",
              "| Endpoint | Layer omnibus (df=2), Holm p across two main effects | Window omnibus (df=4), Holm p across two main effects |",
              "|---|---:|---:|"]
    for metric, label in (("fg_lpips", "FG-LPIPS"), ("fg_psnr", "FG-PSNR")):
        terms = output["results"][metric]["gee_crosscheck"]["terms"]
        layer, window = terms["C(layer)"], terms["C(window)"]
        lines.append(
            f"| {label} | W={layer['wald_chi2']:.3f}, p={p_text(layer['p'], layer['p_upper_bound'])}, "
            f"Holm={layer['p_holm_two_main_effects']:.3g} | W={window['wald_chi2']:.3f}, "
            f"p={p_text(window['p'], window['p_upper_bound'])}, Holm={window['p_holm_two_main_effects']:.3g} |"
        )

    lines += ["", "## Co-reported fidelity, structure, and GT-relative texture outcomes", "",
              "These endpoints are descriptive and have no multiplicity correction in this report. Each entry is the cell-minus-baseline mean; paired CIs and favorable-object rates for every entry are available in `formal/campaign_FRESH_CONFIRM_B_20261005/A3B_BOUNDED_MAP_ANALYSIS.json`.", "",
              "| Intervention | Full-PSNR | Full-LPIPS | FG-SSIM | Edge-SSIM | CIEDE2000 | Laplacian log error | RGB-std log error | Gradient log error | HF-energy log error |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    other_metrics = ("full_psnr", "full_lpips", "fg_ssim", "edge_ssim", "ciede2000",
                     "logerr_laplacian_variance", "logerr_rgb_std",
                     "logerr_gradient_magnitude", "logerr_hf_energy")
    for key in cell_keys:
        values = [output["co_reported_metrics"][metric][key]["mean_delta"] for metric in other_metrics]
        lines.append(f"| `{key}` | " + " | ".join(f"{float(value):+.3g}" for value in values) + " |")

    lines += [
        "", "## Interpretation", "",
        "- The frozen bounded intervention produces statistically clear Layer × Window heterogeneity on both FG-LPIPS and FG-PSNR, with agreement between two independent formulations.",
        "- This does not identify an equal-dose or dose-independent mechanism: the shallow scale increment was at the cap and its development proxy was about 1.99× target, while deep and middle were about 20% below target. The interaction may include realized-dose differences.",
        "- The response surface is not uniformly favorable. FG-LPIPS improves across most middle cells but worsens substantially across shallow cells; FG-PSNR has a different pattern, including a positive shallow-W5 mean with wide object-level dispersion. Co-reported color/texture measures also do not move uniformly with the perceptual endpoints.",
        "- Consequently this confirms heterogeneity of the frozen bounded map on FRESH_CONFIRM_B, but does not by itself prove that a dose-controlled 2D allocation law is practically large or universally beneficial. Do not describe A3b as equal-dose, dose-matched, residual-budget controlled, or pure Layer × Time causal proof.",
        "", "## Provenance", "",
        "- Protocol: `A3B_PROTOCOL_LOCK.md`.",
        "- Calibration limits: `A3B_DOSE_FEASIBILITY_AUDIT.md`.",
        "- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).",
        "- Complete paired estimates: `formal/campaign_FRESH_CONFIRM_B_20261005/A3B_BOUNDED_MAP_ANALYSIS.json`.",
        "- Texture extension: `formal/campaign_FRESH_CONFIRM_B_20261005/a3b_texture_extension_per_object.csv`.", "",
    ]
    (V3 / "A3B_BOUNDED_LAYER_TIME_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    table, manifest = load_data()
    texture_path = RUN / "a3b_texture_extension_per_object.csv"
    if not texture_path.is_file():
        raise SystemExit("A3b co-reported CIEDE2000 evidence requires the locked texture extension.")
    texture = pd.read_csv(texture_path).set_index("object_uid")
    output = {
        "cohort": "FRESH_CONFIRM_B",
        "n_objects": 150,
        "protocol_scope": "post-discovery bounded-dose map; not dose-normalized",
        "bootstrap_draws": analyze_v3.BOOT_N,
        "bootstrap_seed": analyze_v3.BOOT_SEED,
        "results": {},
        "co_reported_metrics": {},
    }
    for metric in METRICS:
        cells, long_data = cell_deltas(table, metric)
        tests = {f"{layer}_W{window}": summarize_cell(cells[(layer, window)], metric)
                 for layer in LAYERS for window in WINDOWS}
        matrix = np.vstack([cells[(layer, window)] for layer in LAYERS for window in WINDOWS])
        wald_w, wald_p = wald_interaction(matrix)
        tab = matrix.mean(axis=1).reshape(3, 5)
        grand = float(tab.mean())
        resid = tab - tab.mean(axis=1)[:, None] - tab.mean(axis=0)[None, :] + grand
        ss_interaction = float(np.square(resid).sum())
        ss_total = float(np.square(tab - grand).sum())
        p_for_holm = wald_p if wald_p > 0 else 1e-300
        family = {key: value["p_bootstrap"] for key, value in tests.items()}
        family["layer_window_interaction"] = p_for_holm
        adjusted = analyze_v3.holm(family)
        for key in tests:
            tests[key]["p_holm_16"] = adjusted[key]
        gee = gee_summary(long_data)
        output["results"][metric] = {
            "primary_family_size": 16,
            "cell_contrasts": tests,
            "interaction": {
                "test": "validated orthogonal object-cluster robust Wald test",
                "df": 8,
                "W": float(wald_w),
                "p": float(wald_p) if wald_p > 0 else None,
                "p_upper_bound": None if wald_p > 0 else "<=1e-300",
                "p_holm_16_upper_bound": adjusted["layer_window_interaction"],
                "interaction_ss_share_of_cell_mean_variation": ss_interaction / ss_total if ss_total else 0.0,
                "interaction_rmse_per_cell": math.sqrt(ss_interaction / 15.0),
            },
            "gee_crosscheck": gee,
            "layer_marginal_mean_delta": {
                layer: float(np.mean([cells[(layer, window)].mean() for window in WINDOWS]))
                for layer in LAYERS
            },
            "window_marginal_mean_delta": {
                f"W{window}": float(np.mean([cells[(layer, window)].mean() for layer in LAYERS]))
                for window in WINDOWS
            },
        }

    for metric, direction in METRIC_DIRECTIONS.items():
        baseline_values = metric_values(table, texture, "a3_baseline", metric)
        output["co_reported_metrics"][metric] = {}
        for layer in LAYERS:
            for window in WINDOWS:
                condition = f"a3_{layer}_W{window}"
                values = metric_values(table, texture, condition, metric)
                if set(values) != set(baseline_values):
                    raise SystemExit(f"Co-reported pairing failure for {condition}/{metric}.")
                delta = np.asarray([values[uid] - baseline_values[uid]
                                    for uid in sorted(baseline_values)], dtype=np.float64)
                stat = analyze_v3.paired_bootstrap(delta)
                stat["favorable_rate"] = float(np.mean(delta > 0 if direction == "higher" else delta < 0))
                stat["favorable_direction"] = direction
                output["co_reported_metrics"][metric][f"{layer}_W{window}"] = stat

    output["frozen_condition_scales"] = {
        condition: manifest["condition_specs"][condition]["scale_trace_requested"]
        for condition in sorted(
            c for c in manifest["condition_specs"] if c == "a3_baseline" or c.startswith("a3_")
        )
    }
    path = RUN / "A3B_BOUNDED_MAP_ANALYSIS.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    write_report(output)
    print(json.dumps({m: {"interaction": r["interaction"], "gee": r["gee_crosscheck"]}
                      for m, r in output["results"].items()}, indent=2))


if __name__ == "__main__":
    main()
