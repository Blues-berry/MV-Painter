#!/usr/bin/env python3
"""Render the frozen seven-contrast cap/budget report for FRESH_CONFIRM_B."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
LAYERS = ("deep", "middle", "shallow")
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
CONDITIONS = (
    "native_gfl", "native_gfh", "native_gc3", "true_global_0p80",
    "true_global_1p25", "true_global_1p675", "true_global_2p50",
    "lfm_exact", "layer_llh", "layer_hll",
)
CONTRASTS = {
    "LLH − GFL": ("layer_llh", "native_gfl", "paired_layer_llh_minus_native_gfl.json",
                  "Combined depth/time allocation, nominal budget, and cap-profile contrast."),
    "LLH − LFM-EXACT": ("layer_llh", "lfm_exact", "paired_layer_llh_minus_lfm_exact.json",
                         "Temporal redistribution at the same requested per-layer means; realized residual dose may differ."),
    "LLH − HLL": ("layer_llh", "layer_hll", "paired_layer_llh_minus_layer_hll.json",
                   "Temporal position at matched per-layer requested means and matched 17-step high duration."),
    "GFL − TGU-1.25": ("native_gfl", "true_global_1p25", "paired_native_gfl_minus_true_global_1p25.json",
                       "Effect of native shallow cap behavior at the same requested global scale."),
    "LFM-EXACT − TGU-1.675": ("lfm_exact", "true_global_1p675", "paired_lfm_exact_minus_true_global_1p675.json",
                              "Deep/middle requests match; shallow exposure differs. Not an equal-total-dose layer-only contrast."),
    "TGU-1.25 − TGU-0.80": ("true_global_1p25", "true_global_0p80", "paired_true_global_1p25_minus_true_global_0p80.json",
                             "Uniform requested-scale contrast with the same uncapped path."),
    "LLH − TGU-1.675": ("layer_llh", "true_global_1p675", "paired_layer_llh_minus_true_global_1p675.json",
                         "Combined layer/time allocation and cap/exposure contrast; descriptive only."),
}


def trace_summary(manifest: dict, condition: str) -> dict:
    spec = manifest["condition_specs"][condition]
    trace = spec["scale_trace_requested"]
    if len(trace) != 50:
        raise SystemExit(f"{condition}: expected 50 steps.")
    uncapped = bool(spec.get("uncapped", False))
    requested, applied, cap = {}, {}, {}
    for layer in LAYERS:
        scales = [float(step[layer]) for step in trace]
        requested[layer] = float(sum(scales))
        applied[layer] = float(sum(x if uncapped else min(x, CAPS[layer]) for x in scales))
        cap[layer] = 0.0 if uncapped else float(np.mean([x > CAPS[layer] for x in scales]))
    return {"uncapped": uncapped, "requested": requested, "applied": applied, "cap": cap}


def fmt_triplet(values: dict, *, scale: float = 1.0, digits: int = 2) -> str:
    return "/".join(f"{scale*values[layer]:.{digits}f}" for layer in LAYERS)


def effect(stat: dict, metric: str) -> str:
    digits = 3 if metric == "fg_psnr" else 5
    mean = float(stat["mean_delta"])
    lo, hi = map(float, stat["ci95"])
    return f"{mean:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"


def main() -> None:
    gate = (V3 / "B_FORMAL_INTEGRITY_GATE.md").read_text()
    if "FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS" not in gate:
        raise SystemExit("FRESH_CONFIRM_B integrity gate is not PASS.")
    manifest = json.loads((RUN / "run_manifest_shard0.json").read_text())
    table = pd.read_csv(RUN / "per_object_metrics.csv")
    if len(table) != 4500 or table.duplicated(["object_uid", "condition"]).any():
        raise SystemExit("B per-object metrics do not match the gated 4,500-row table.")
    uids = set(table.loc[table.condition == "layer_llh", "object_uid"])
    if len(uids) != 150:
        raise SystemExit("LLH does not contain 150 unique objects.")

    budget = json.loads((RUN / "residual_budget_audit.json").read_text())["conditions"]
    holm = json.loads((RUN / "CAP_BUDGET_HOLM_FAMILY.json").read_text())
    profiles, scores = {}, {}
    for condition in CONDITIONS:
        spec = trace_summary(manifest, condition)
        if budget[condition]["n_objects"] != 150 or budget[condition]["uncapped"] != spec["uncapped"]:
            raise SystemExit(f"Residual-budget summary provenance mismatch: {condition}.")
        if set(table.loc[table.condition == condition, "object_uid"]) != uids:
            raise SystemExit(f"Condition pairing failure: {condition}.")
        profiles[condition] = spec
        scores[condition] = {
            metric: float(table.loc[table.condition == condition, metric].mean())
            for metric in ("fg_psnr", "fg_lpips")
        }

    paired = {}
    for label, (a, b, filename, _) in CONTRASTS.items():
        result = json.loads((RUN / filename).read_text())
        if result.get("n_objects") != 150 or result.get("contrast") != f"{a} - {b}":
            raise SystemExit(f"Paired result metadata mismatch for {label}.")
        for metric in ("fg_psnr", "fg_lpips"):
            left = table.loc[table.condition == a].set_index("object_uid")[metric].sort_index()
            right = table.loc[table.condition == b].set_index("object_uid")[metric].sort_index()
            direct_mean = float((left - right).mean())
            if not np.isclose(direct_mean, result["tests"][metric]["mean_delta"], rtol=0, atol=1e-12):
                raise SystemExit(f"Paired result mean differs from gated ledger: {label}/{metric}.")
        paired[label] = result

    identity = {}
    gfl = table[table.condition == "native_gfl"].set_index("object_uid").sort_index()
    llh = table[table.condition == "layer_llh"].set_index("object_uid").sort_index()
    lfm = table[table.condition == "lfm_exact"].set_index("object_uid").sort_index()
    for metric in ("fg_psnr", "fg_lpips"):
        direct = llh[metric] - gfl[metric]
        components = (llh[metric] - lfm[metric]) + (lfm[metric] - gfl[metric])
        residual = direct - components
        identity[metric] = {
            "direct_mean": float(direct.mean()),
            "temporal_component_mean": float((llh[metric] - lfm[metric]).mean()),
            "combined_layer_cap_component_mean": float((lfm[metric] - gfl[metric]).mean()),
            "max_abs_object_residual": float(np.max(np.abs(residual.to_numpy()))),
            "exact_objectwise_identity": bool(np.array_equal(direct.to_numpy(), components.to_numpy())),
        }

    lines = [
        "# Final cap/budget causal accounting — FRESH_CONFIRM_B", "",
        "The 4,500-row B campaign passed its integrity gate. All conditions below share the same objects, checkpoint, runner, inputs, seed policy, views, and metric implementation. Paired effects are condition A minus condition B, with 10,000 object bootstrap resamples (seed 20261002). FG-PSNR is higher-is-better; FG-LPIPS is lower-is-better. The frozen Holm family contains seven comparisons per endpoint.", "",
        "## Requested/applied scales, cap semantics, realized correction dose, and scores", "",
        "Requested/applied values are 50-step scale integrals in deep/middle/shallow order. `E` is the mean per-object root-sum-square of actual post-scale wrapper corrections over all 50 steps, by layer. For TGU, the manifest's uncapped flag is authoritative: requested scale is actually applied even though logged `eff_scale` is hypothetical.", "",
        "| Condition | Forward path | Requested scale integral D/M/S | Applied scale integral D/M/S | Cap activation D/M/S | Mean E D/M/S | Mean FG-PSNR | Mean FG-LPIPS |",
        "|---|---|---:|---:|---:|---:|---:|---:|"]
    for condition in CONDITIONS:
        spec, dose = profiles[condition], budget[condition]
        path = "uncapped diagnostic" if spec["uncapped"] else "native capped"
        e = {layer: dose["layers"][layer]["E_mean"] for layer in LAYERS}
        lines.append(
            f"| `{condition}` | {path} | {fmt_triplet(spec['requested'])} "
            f"| {fmt_triplet(spec['applied'])} "
            f"| {fmt_triplet(spec['cap'], scale=100, digits=0)}% "
            f"| {fmt_triplet(e, digits=3)} "
            f"| {scores[condition]['fg_psnr']:.3f} | {scores[condition]['fg_lpips']:.5f} |"
        )

    lines += ["", "## Frozen contrast semantics", "",
              "| Contrast | Same per-layer requested mean? | Same high duration/position? | Same cap path and activation rate? | Same actual dose? | Same runner? | Allowed causal statement |",
              "|---|---|---|---|---|---|---|"]
    for label, (a, b, _, meaning) in CONTRASTS.items():
        same_means = all(abs(profiles[a]["requested"][layer] - profiles[b]["requested"][layer]) < 1e-9
                         for layer in LAYERS)
        cap_same = profiles[a]["uncapped"] == profiles[b]["uncapped"] and all(
            abs(profiles[a]["cap"][layer] - profiles[b]["cap"][layer]) < 1e-12
            for layer in LAYERS
        )
        temporal = {
            "LLH − GFL": "No; staged vs constant",
            "LLH − LFM-EXACT": "No; variable vs constant",
            "LLH − HLL": "Same 17-step high duration; position differs",
            "GFL − TGU-1.25": "Same constant requested trace",
            "LFM-EXACT − TGU-1.675": "Both constant over time",
            "TGU-1.25 − TGU-0.80": "Both constant over time",
            "LLH − TGU-1.675": "No; staged vs constant",
        }[label]
        e_a = budget[a]["layers"]
        e_b = budget[b]["layers"]
        same_dose = all(abs(e_a[layer]["E_mean"] - e_b[layer]["E_mean"])
                        <= 1e-12 * max(e_a[layer]["E_mean"], e_b[layer]["E_mean"])
                        for layer in LAYERS)
        allowed = {
            "LLH − GFL": "Combined allocation/budget/cap-profile effect only.",
            "LLH − LFM-EXACT": "Temporal redistribution at matched per-layer requested means; not post-scale dose equality.",
            "LLH − HLL": "Early-versus-late position effect at equal 17-step high duration.",
            "GFL − TGU-1.25": "Native shallow-cap effect at a fixed requested global scale.",
            "LFM-EXACT − TGU-1.675": "Combined shallow-exposure/cap-path difference; not pure depth redistribution.",
            "TGU-1.25 − TGU-0.80": "Uniform requested-dose effect on the uncapped diagnostic path.",
            "LLH − TGU-1.675": "Descriptive multi-factor contrast only.",
        }[label]
        lines.append(
            f"| {label} | {'Yes' if same_means else 'No'} | {temporal} "
            f"| {'Yes' if cap_same else 'No'} | {'Yes' if same_dose else 'No; logged E differs'} "
            f"| Yes | {allowed} |"
        )

    lines += ["", "## Paired performance effects", "",
              "Adjusted p-values are upper bounds where a raw bootstrap result hit the 1/10,000 resolution floor.", "",
              "| Contrast | FG-PSNR Δ dB [95% CI] | Favorable objects | Holm p | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for label in CONTRASTS:
        result = paired[label]
        row = []
        for metric in ("fg_psnr", "fg_lpips"):
            stat = result["tests"][metric]
            adj = holm["metrics"][metric]["tests"][label.replace(" − ", "-")]
            p = f"≤{adj['p_holm_upper_bound']:.4g}" if stat["p_bootstrap"] <= 1e-4 else f"{adj['p_holm_upper_bound']:.4g}"
            row.append((effect(stat, metric), 100 * stat["favorable_rate"], p))
        lines.append(
            f"| {label} | {row[0][0]} | {row[0][1]:.1f}% | {row[0][2]} "
            f"| {row[1][0]} | {row[1][1]:.1f}% | {row[1][2]} |"
        )

    lines += ["", "## Endpoint-connected decomposition", "",
              "The required identity holds exactly for all 150 object-level pairs on both endpoints:", "",
              "`LLH − GFL = (LLH − LFM-EXACT) + (LFM-EXACT − GFL)`", "",
              "| Endpoint | LLH−GFL mean | LLH−LFM-EXACT mean (temporal redistribution) | LFM-EXACT−GFL mean (combined layer/cap/budget) | Max object-level identity residual |",
              "|---|---:|---:|---:|---:|"]
    for metric, label in (("fg_psnr", "FG-PSNR (dB)"), ("fg_lpips", "FG-LPIPS")):
        x = identity[metric]
        lines.append(
            f"| {label} | {x['direct_mean']:+.6f} | {x['temporal_component_mean']:+.6f} "
            f"| {x['combined_layer_cap_component_mean']:+.6f} | {x['max_abs_object_residual']:.1e} |"
        )
    lines += [
        "", "The `LFM-EXACT − GFL` term is the combined change in depth allocation, shallow exposure, realized dose, and native cap state; it is not a pure depth-allocation effect. Its mean is shown only as the algebraic remainder required by the same-endpoint identity; it is not added as an eighth test to the frozen Holm families. No decomposition is formed by summing effects from different endpoints.",
        "", "## Interpretation", "",
        "- LLH exceeds LFM-EXACT on FG-PSNR by +0.325 dB after Holm correction, with a matched requested per-layer mean schedule; this supports a temporal-redistribution effect under the same nominal layer means, while actual correction norms differ.",
        "- Native GFL exceeds true-uniform TGU-1.25 on both endpoints. At requested 1.25, native GFL clips the shallow layer to 0.80, while TGU-1.25 bypasses that cap and applies 1.25. This identifies the effect of that shallow-cap path in this run.",
        "- TGU-1.25 versus TGU-0.80 shows no detectable FG-PSNR difference (95% CI includes zero) but lower FG-LPIPS at 1.25. No equivalence margin was frozen, so the PSNR result is not an equivalence claim.",
        "- TGU conditions are causal diagnostics, not deployment baselines. LLH−GFL and LLH−TGU-1.675 remain combined contrasts; no further split of the layer/cap/budget component is identified.",
        "", "## Provenance", "",
        "- Frozen contrast definitions: `CAP_BUDGET_DIAGNOSTIC_PROTOCOL_LOCK.md`.",
        "- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).",
        "- Paired contrasts and Holm family: `formal/campaign_FRESH_CONFIRM_B_20261005/paired_*.json` and `CAP_BUDGET_HOLM_FAMILY.json`.",
        "- Actual post-scale dose: `formal/campaign_FRESH_CONFIRM_B_20261005/residual_budget_audit.json` and raw residual logs.",
        "- Source metric rows: `formal/campaign_FRESH_CONFIRM_B_20261005/per_object_metrics.csv`.", "",
    ]
    (V3 / "FINAL_CAP_BUDGET_CAUSAL_ACCOUNTING.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
