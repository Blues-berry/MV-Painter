#!/usr/bin/env python3
"""Analyze the frozen fixed-width stage-boundary sensitivity family."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
COHORT = V3 / "fresh_confirm_b/fresh_confirm_B_150.txt"
sys.path.insert(0, str(V3))
sys.path.insert(0, str(ROOT))
import analyze_v3  # noqa: E402

PROFILES = {
    "20_60_20": ("boundary_late_onset_20_60_20", 40),
    "30_40_30": ("boundary_late_onset_30_40_30", 35),
    "34_32_34": ("boundary_late_onset_34_32_34", 33),
    "40_20_40": ("boundary_late_onset_40_20_40", 30),
}
PRIMARY = "fg_lpips"
METRICS = (
    "fg_lpips", "fg_psnr", "full_psnr", "full_lpips", "fg_ssim", "edge_ssim",
    "ciede2000", "logerr_laplacian_variance", "logerr_rgb_std",
    "logerr_gradient_magnitude", "logerr_hf_energy",
)
LOW = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
HIGH = {"deep": 2.50, "middle": 2.50, "shallow": 0.75}
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}


def validate_protocol(manifest: dict) -> dict:
    specs = manifest["condition_specs"]
    baseline = specs["a3_baseline"]["scale_trace_requested"]
    if len(baseline) != 50 or specs["a3_baseline"].get("uncapped"):
        raise SystemExit("Shared baseline has unexpected step count or cap semantics.")
    if any(float(step[layer]) != LOW[layer] for step in baseline for layer in LOW):
        raise SystemExit("Shared baseline differs from the frozen low profile.")

    summary = {}
    for label, (condition, start) in PROFILES.items():
        spec = specs[condition]
        trace = spec["scale_trace_requested"]
        if len(trace) != 50 or spec.get("uncapped"):
            raise SystemExit(f"{condition}: unexpected step count or cap semantics.")
        for step_idx, step in enumerate(trace):
            expected = HIGH if start <= step_idx < start + 10 else LOW
            if any(float(step[layer]) != expected[layer] for layer in LOW):
                raise SystemExit(f"{condition}: trace differs from frozen 10-step pulse at step {step_idx}.")
        if any(HIGH[layer] > CAPS[layer] for layer in LOW):
            raise SystemExit("Frozen high profile exceeds a native cap.")
        summary[label] = {
            "condition": condition, "onset_step": start,
            "high_steps": [start, start + 9], "duration": 10,
            "requested_scale_integral_by_layer": {
                layer: sum(float(step[layer]) for step in trace) for layer in LOW
            },
            "cap_activation_fraction_by_step": {
                layer: float(np.mean([float(step[layer]) > CAPS[layer] for step in trace]))
                for layer in LOW
            },
        }
    integrals = [x["requested_scale_integral_by_layer"] for x in summary.values()]
    if any(any(abs(integrals[0][layer] - row[layer]) > 1e-10 for layer in LOW)
           for row in integrals[1:]):
        raise SystemExit("Boundary candidates do not have the same nominal per-layer budget.")
    return summary


def metric_values(table: pd.DataFrame, texture: pd.DataFrame, condition: str,
                  metric: str) -> dict[str, float]:
    rows = table[table.condition == condition].set_index("object_uid")
    if metric == "ciede2000":
        key = f"{condition}:ciede2000"
        if key not in texture:
            raise SystemExit(f"Missing boundary texture extension column: {key}.")
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


def contrast(a: dict[str, float], b: dict[str, float], metric: str) -> dict:
    if set(a) != set(b):
        raise SystemExit("Paired boundary contrast has incomplete object overlap.")
    uids = sorted(a)
    delta = np.asarray([a[u] - b[u] for u in uids], dtype=np.float64)
    stat = analyze_v3.paired_bootstrap(delta)
    lower_is_better = metric in {
        "fg_lpips", "full_lpips", "ciede2000", "logerr_laplacian_variance",
        "logerr_rgb_std", "logerr_gradient_magnitude", "logerr_hf_energy",
    }
    stat["favorable_rate"] = float(np.mean(delta < 0 if lower_is_better else delta > 0))
    stat["favorable_direction"] = "lower" if lower_is_better else "higher"
    stat["bootstrap_floor"] = bool(stat["p_bootstrap"] <= 1 / analyze_v3.BOOT_N)
    return stat


def write_report(result: dict) -> None:
    def effect(stat: dict, metric: str) -> str:
        digits = 6 if metric in {"fg_lpips", "full_lpips", "ciede2000"} else 4
        mean = stat["mean_delta"]
        lo, hi = stat["ci95"]
        return f"{mean:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"

    def p_text(stat: dict) -> str:
        value = float(stat["p_bootstrap"])
        return f"≤{value:.4g}" if stat.get("bootstrap_floor") else f"{value:.4g}"

    lines = [
        "# Stage-boundary evidence report — FRESH_CONFIRM_B", "",
        "**Verdict: BOUNDARY-HEURISTIC.** The four frozen profiles share a 10-step high pulse, the same per-layer nominal scale integrals, and the same native cap path; only pulse onset changes. This is a bounded sensitivity check, not an optimization search or evidence for a physical diffusion phase boundary.", "",
        "The integrity gate passed before outcome analysis. Effects use paired objects (n=150), 10,000 percentile-bootstrap resamples, seed 20261002. For the primary FG-LPIPS endpoint, Holm correction is across four profile-versus-baseline contrasts; a separate three-test Holm family compares the 34/32/34 profile with each alternative. Bootstrap p-values at the 1/10,000 resolution floor are reported as upper bounds.", "",
        "## Frozen schedule checks", "",
        "| Profile | Pulse onset | High steps | Per-layer requested integral (D/M/S) | Cap activation (D/M/S) |",
        "|---|---:|---|---:|---:|",
    ]
    for label, info in result["profiles"].items():
        scales = info["requested_scale_integral_by_layer"]
        caps = info["cap_activation_fraction_by_step"]
        lines.append(
            f"| {label.replace('_', '/')} | {info['onset_step']} | {info['high_steps'][0]}–{info['high_steps'][1]} "
            f"| {scales['deep']:.1f}/{scales['middle']:.1f}/{scales['shallow']:.1f} "
            f"| {100*caps['deep']:.0f}%/{100*caps['middle']:.0f}%/{100*caps['shallow']:.0f}% |"
        )
    lines += ["", "## Frozen profiles versus shared low baseline", "",
              "Negative FG-LPIPS and positive FG-PSNR favor the pulse. Holm is applied only to the four primary FG-LPIPS tests; other endpoints are descriptive.", "",
              "| Profile | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ [95% CI] | Favorable objects |",
              "|---|---:|---:|---:|---:|---:|"]
    for label, info in result["baseline_contrasts"].items():
        lp = info["fg_lpips"]
        ps = info["fg_psnr"]
        lines.append(
            f"| {label.replace('_', '/')} | {effect(lp, 'fg_lpips')} | {100*lp['favorable_rate']:.1f}% "
            f"| {p_text({'p_bootstrap': info['holm_p_fg_lpips'], 'bootstrap_floor': lp['bootstrap_floor']})} "
            f"| {effect(ps, 'fg_psnr')} | {100*ps['favorable_rate']:.1f}% |"
        )

    lines += ["", "## 34/32/34 versus the other frozen onsets", "",
              "The three-test Holm family is on FG-LPIPS. FG-PSNR and other endpoints are co-reported without a second confirmatory family.", "",
              "| Contrast (34/32/34 minus comparator) | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ dB [95% CI] | Favorable objects |",
              "|---|---:|---:|---:|---:|---:|"]
    for label, info in result["centered_contrasts"].items():
        lp, ps = info["fg_lpips"], info["fg_psnr"]
        lines.append(
            f"| 34/32/34 − {label.replace('_', '/')} | {effect(lp, 'fg_lpips')} "
            f"| {100*lp['favorable_rate']:.1f}% "
            f"| {p_text({'p_bootstrap': info['holm_p_fg_lpips'], 'bootstrap_floor': lp['bootstrap_floor']})} "
            f"| {effect(ps, 'fg_psnr')} | {100*ps['favorable_rate']:.1f}% |"
        )

    secondary = ("full_psnr", "full_lpips", "fg_ssim", "edge_ssim", "ciede2000",
                 "logerr_laplacian_variance", "logerr_rgb_std",
                 "logerr_gradient_magnitude", "logerr_hf_energy")
    titles = ("Full-PSNR", "Full-LPIPS", "FG-SSIM", "Edge-SSIM", "CIEDE2000",
              "Laplacian log error", "RGB-std log error", "Gradient log error", "HF-energy log error")
    lines += ["", "## Co-reported baseline contrasts", "",
              "Descriptive paired means; CIs and direction-aware win rates are in the analysis JSON.", "",
              "| Profile | " + " | ".join(titles) + " |",
              "|---|" + "---:|" * len(titles)]
    for label, info in result["baseline_contrasts"].items():
        values = [effect(info[metric], metric) for metric in secondary]
        lines.append("| " + label.replace("_", "/") + " | " + " | ".join(values) + " |")

    lines += [
        "", "## Decision", "",
        "Within this frozen family, later pulse onsets show a consistent primary-endpoint ordering: onset 40 (20/60/20) performs best, followed by 35 (30/40/30), then 33 (34/32/34), then 30 (40/20/40). The direct FG-LPIPS contrasts after the predeclared three-test Holm correction favor onset 40 and 35 over 33, while 33 outperforms onset 30. This is evidence that pulse position matters in this family; it does not support the exact one-third boundary as a discovered phase transition or establish onset 40 as a universal optimum.",
        "",
        "The four equal-duration comparisons are bounded evidence about this pulse family only. A non-significant difference would not be an equivalence claim because no equivalence margin was frozen.",
        "",
        "Use thirds as a convenient discretization (`BOUNDARY-HEURISTIC`); the observed onset gradient should be reported as a fixed-family sensitivity result, not used to select or tune a replacement boundary.",
        "", "## Provenance", "",
        "- Frozen design: `STAGE_BOUNDARY_PROTOCOL_LOCK.md`.",
        "- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).",
        "- Complete paired estimates: `formal/campaign_FRESH_CONFIRM_B_20261005/BOUNDARY_SENSITIVITY_ANALYSIS.json`.",
        "- Texture extension: `formal/campaign_FRESH_CONFIRM_B_20261005/boundary_texture_extension_per_object.csv`.", "",
    ]
    (V3 / "STAGE_BOUNDARY_EVIDENCE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    gate = (V3 / "B_FORMAL_INTEGRITY_GATE.md").read_text()
    if "FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS" not in gate:
        raise SystemExit("FRESH_CONFIRM_B integrity gate is not PASS.")
    uids = [x.strip() for x in COHORT.read_text().splitlines() if x.strip()]
    if len(uids) != 150 or len(set(uids)) != 150:
        raise SystemExit("Frozen B cohort list is not 150 unique objects.")
    table = pd.read_csv(RUN / "per_object_metrics.csv")
    if len(table) != 4500 or table.duplicated(["object_uid", "condition"]).any():
        raise SystemExit("B metric table differs from its gated unique 4,500-row inventory.")
    metrics = table[table.condition.isin(["a3_baseline", *(x[0] for x in PROFILES.values())])]
    if set(metrics.object_uid) != set(uids):
        raise SystemExit("Frozen boundary metrics do not cover all B objects.")
    manifest = json.loads((RUN / "run_manifest_shard0.json").read_text())
    profiles = validate_protocol(manifest)
    texture_path = RUN / "boundary_texture_extension_per_object.csv"
    texture = pd.read_csv(texture_path).set_index("object_uid")
    if len(texture) != 150 or set(texture.index) != set(uids):
        raise SystemExit("Boundary texture extension does not pair all 150 objects.")

    values = {condition: {metric: metric_values(table, texture, condition, metric)
                          for metric in METRICS}
              for condition in ("a3_baseline", *(x[0] for x in PROFILES.values()))}
    baseline = {metric: values["a3_baseline"][metric] for metric in METRICS}
    baseline_contrasts, family_p = {}, {}
    for label, (condition, _) in PROFILES.items():
        baseline_contrasts[label] = {
            metric: contrast(values[condition][metric], baseline[metric], metric)
            for metric in METRICS
        }
        family_p[label] = baseline_contrasts[label][PRIMARY]["p_bootstrap"]
    baseline_holm = analyze_v3.holm(family_p)
    for label in PROFILES:
        baseline_contrasts[label]["holm_p_fg_lpips"] = baseline_holm[label]

    center_condition = PROFILES["34_32_34"][0]
    centered_contrasts, center_family_p = {}, {}
    for label, (condition, _) in PROFILES.items():
        if label == "34_32_34":
            continue
        centered_contrasts[label] = {
            metric: contrast(values[center_condition][metric], values[condition][metric], metric)
            for metric in METRICS
        }
        center_family_p[label] = centered_contrasts[label][PRIMARY]["p_bootstrap"]
    center_holm = analyze_v3.holm(center_family_p)
    for label in centered_contrasts:
        centered_contrasts[label]["holm_p_fg_lpips"] = center_holm[label]

    output = {
        "cohort": "FRESH_CONFIRM_B", "n_objects": 150,
        "primary_metric": PRIMARY, "bootstrap_draws": analyze_v3.BOOT_N,
        "bootstrap_seed": analyze_v3.BOOT_SEED,
        "interpretation": "fixed-width onset sensitivity; not boundary optimization or phase discovery",
        "profiles": profiles, "baseline_contrasts": baseline_contrasts,
        "baseline_holm_family_fg_lpips": {k: float(v) for k, v in baseline_holm.items()},
        "centered_contrasts": centered_contrasts,
        "center_holm_family_fg_lpips": {k: float(v) for k, v in center_holm.items()},
    }
    out = RUN / "BOUNDARY_SENSITIVITY_ANALYSIS.json"
    out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_report(output)
    print(f"Wrote frozen boundary sensitivity analysis and report: {out}")


if __name__ == "__main__":
    main()
