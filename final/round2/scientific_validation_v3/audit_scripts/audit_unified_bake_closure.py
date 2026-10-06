#!/usr/bin/env python3
"""Reconcile the frozen 2D source outputs with the unified baked 3D cohort."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

V3 = Path(__file__).resolve().parents[1]
BAKE = V3 / "bake_handoff"
CPU = BAKE / "cpu_bake_v3"
SEAM = BAKE / "BAKE_SEAM_AUDIT_V3"
SEED = 20261005
BOOTSTRAPS = 10_000


def paired_summary(a: pd.Series, b: pd.Series) -> dict:
    pair = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna().sort_index()
    delta = (pair["a"] - pair["b"]).to_numpy(dtype=float)
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(delta), size=(BOOTSTRAPS, len(delta)))
    means = delta[draws].mean(axis=1)
    return {
        "n": int(len(delta)),
        "mean_delta": float(delta.mean()),
        "ci95": [float(x) for x in np.quantile(means, [0.025, 0.975])],
        "fraction_delta_positive": float((delta > 0).mean()),
        "mean_a": float(pair["a"].mean()),
        "mean_b": float(pair["b"].mean()),
    }


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_spearman(a: pd.Series, b: pd.Series) -> float | None:
    x, y = pd.Series(a).dropna(), pd.Series(b).dropna()
    shared = x.index.intersection(y.index)
    x, y = x.loc[shared], y.loc[shared]
    if len(shared) < 3 or x.nunique() < 2 or y.nunique() < 2:
        return None
    return float(spearmanr(x, y).statistic)


def main() -> None:
    handoff = json.loads((BAKE / "BAKE_INPUT_HANDOFF_V3.json").read_text())
    excluded = set(json.loads((BAKE / "excluded_uv_missing.json").read_text()))
    declared = {x["object"] for x in handoff["objects"]}
    observed = pd.read_csv(CPU / "UNSEEN_OBJECT_METRICS.csv")
    seam = pd.read_csv(SEAM / "SEAM_AUDIT_PER_OBJECT.csv")
    if len(declared) != 24 or len(excluded) != 4:
        raise SystemExit("Frozen bake cohort/exclusion ledger does not match 24/4.")
    if set(observed["object"]) != declared - excluded:
        raise SystemExit("Baked object set differs from the frozen eligible set.")
    if observed.duplicated(["object", "method"]).any():
        raise SystemExit("Duplicate object/method rows in unseen metrics.")
    methods = {
        "gt", "no_adapter", "native_gfl", "native_gfh", "native_gc3",
        "lfm_exact", "layer_lhl", "layer_llh",
    }
    if set(observed["method"]) != methods or len(observed) != 20 * len(methods):
        raise SystemExit("Unified bake family is incomplete or has unexpected methods.")
    if set(seam["object"]) != declared - excluded or set(seam["condition"]) != methods - {"gt"}:
        raise SystemExit("Seam audit object/condition set differs from baked family.")

    metadata_rows = []
    for row in observed.itertuples(index=False):
        if row.method == "gt":
            continue
        meta_path = CPU / row.method / row.object / "bake_metadata.json"
        metadata = json.loads(meta_path.read_text())
        if metadata["object"] != row.object or metadata["method"] != row.method:
            raise SystemExit(f"Bake metadata identity mismatch: {row.object}/{row.method}.")
        if not np.isclose(metadata["cross_view_texel_variance"], row.cross_view_texel_variance, rtol=0, atol=1e-12, equal_nan=True):
            raise SystemExit(f"Cross-view variance differs from bake metadata: {row.object}/{row.method}.")
        metadata_rows.append({
            "object": row.object,
            "method": row.method,
            "raw_texture_coverage": float(metadata["texture_coverage"]),
            "texture_coverage_after_inpaint": float(metadata["texture_coverage_after_inpaint"]),
            "inpainted_fraction": float(metadata["inpainted_fraction"]),
        })
    metadata_df = pd.DataFrame(metadata_rows)

    b1 = pd.read_csv(V3 / "formal/campaign_B1B2/per_object_metrics.csv")
    b3 = pd.read_csv(V3 / "formal/campaign_B3/per_object_metrics.csv")
    overlap = declared - excluded
    llh2d = b1[(b1.condition == "layer_llh") & b1.object_uid.isin(overlap)].set_index("object_uid")
    gfl2d = b3[(b3.condition == "native_gfl") & b3.object_uid.isin(overlap)].set_index("object_uid")
    if set(llh2d.index) != overlap or set(gfl2d.index) != overlap:
        raise SystemExit("Could not reconstruct exact 20-object image-space pair.")

    manifests = [
        json.loads((V3 / "formal/campaign_B1B2/run_manifest_shard0.json").read_text()),
        json.loads((V3 / "formal/campaign_B3/run_manifest_shard0.json").read_text()),
    ]
    identity_fields = ("checkpoint_sha256", "object_list_sha256", "latent_seed", "reference_seed_policy", "protocol", "realization")
    if any(manifests[0].get(key) != manifests[1].get(key) for key in identity_fields):
        raise SystemExit("Image-space conditions differ on a frozen run identity field.")

    verified_source_files = 0
    expected_view_set = set(handoff["target_views"])
    for obj in handoff["objects"]:
        uid = obj["object"]
        if uid not in overlap:
            continue
        reference_slot_map = None
        for condition, source in obj["generated_conditions"].items():
            panel = Path(source["panel"])
            if not panel.is_file() or digest(panel) != source["panel_sha256"]:
                raise SystemExit(f"Panel SHA verification failed: {uid}/{condition}.")
            verified_source_files += 1
            slot_map = []
            for view in source["target_views"]:
                path = Path(view["path"])
                if not path.is_file() or digest(path) != view["sha256"]:
                    raise SystemExit(f"Target-view SHA verification failed: {uid}/{condition}/{view['slot']}.")
                slot_map.append((int(view["slot"]), int(view["raw_view_index"])))
                verified_source_files += 1
            slot_map = tuple(sorted(slot_map))
            if {view_id for _, view_id in slot_map} != expected_view_set:
                raise SystemExit(f"Target-view selection differs from frozen handoff: {uid}/{condition}.")
            if reference_slot_map is not None and slot_map != reference_slot_map:
                raise SystemExit(f"Target-view slot mapping differs across conditions: {uid}/{condition}.")
            reference_slot_map = slot_map

    metrics = pd.concat(
        [
            observed[observed.method != "gt"].set_index(["object", "method"]),
            metadata_df.set_index(["object", "method"]),
            seam.set_index(["object", "condition"]).rename_axis(index={"condition": "method"}),
        ],
        axis=1,
    ).reset_index()
    if metrics["inpainted_fraction"].isna().any():
        raise SystemExit("Missing per-object inpaint audit values.")
    metrics["seam_excess_vs_2px_control"] = metrics["seam_dE00_mean"] - metrics["control_dE00_mean_2px"]

    metric_names = {
        "masked_psnr": "masked_psnr",
        "fg_lpips": "fg_lpips",
        "ciede2000": "ciede2000",
        "cross_view_texel_variance": "cross_view_texel_variance",
        "raw_texture_coverage": "raw_texture_coverage",
        "texture_coverage_after_inpaint": "texture_coverage_after_inpaint",
        "inpainted_fraction": "inpainted_fraction",
        "seam_dE00_mean": "seam_dE00_mean",
        "control_dE00_mean_2px": "control_dE00_mean_2px",
        "seam_excess_vs_2px_control": "seam_excess_vs_2px_control",
        "seam_dE00_p90": "seam_dE00_p90",
        "seam_dE00_frac_gt10": "seam_dE00_frac_gt10",
    }
    means = {
        method: {
            key: float(metrics.loc[metrics.method == method, col].mean())
            for key, col in metric_names.items()
        }
        for method in sorted(methods - {"gt"})
    }
    contrasts = {}
    for method in sorted(methods - {"gt", "layer_llh"}):
        a = metrics[metrics.method == "layer_llh"].set_index("object")
        b = metrics[metrics.method == method].set_index("object")
        contrasts[f"layer_llh - {method}"] = {
            key: paired_summary(a[col], b[col])
            for key, col in metric_names.items()
        }

    llh = observed[observed.method == "layer_llh"].set_index("object")
    gfl = observed[observed.method == "native_gfl"].set_index("object")
    d2d = llh2d.sort_index()[["fg_psnr", "fg_lpips"]] - gfl2d.sort_index()[["fg_psnr", "fg_lpips"]]
    d3d = llh.sort_index()[["masked_psnr", "fg_lpips", "ciede2000"]] - gfl.sort_index()[["masked_psnr", "fg_lpips", "ciede2000"]]
    closure = {
        "n": int(len(overlap)),
        "2d_delta": {m: paired_summary(llh2d[m], gfl2d[m]) for m in ("fg_psnr", "fg_lpips")},
        "3d_delta": {m: paired_summary(llh[m], gfl[m]) for m in ("masked_psnr", "fg_lpips", "ciede2000")},
        "spearman_2d_vs_3d_delta": {
            "fg_psnr": float(spearmanr(d2d.fg_psnr, d3d.masked_psnr).statistic),
            "fg_lpips": float(spearmanr(d2d.fg_lpips, d3d.fg_lpips).statistic),
        },
    }
    for field in ("inpainted_fraction", "raw_texture_coverage", "cross_view_texel_variance", "seam_dE00_mean", "seam_excess_vs_2px_control", "seam_dE00_p90"):
        a = metrics[metrics.method == "layer_llh"].set_index("object")[field]
        b = metrics[metrics.method == "native_gfl"].set_index("object")[field]
        delta = (a - b).sort_index()
        closure[f"spearman_3d_psnr_delta_vs_{field}"] = safe_spearman(d3d.masked_psnr, delta)

    # The audit ratio is explicitly excluded if its control denominator is near zero.
    ratio = seam["seam_to_control_ratio"].replace([np.inf, -np.inf], np.nan)
    closure["seam_to_control_ratio_invalid_count"] = int((~np.isfinite(ratio) | (ratio.abs() > 1e6)).sum())
    result = {
        "protocol": "post-hoc same-object 2D-to-bake closure audit; descriptive",
        "cohort": {"frozen_n": 24, "technical_uv_exclusions": sorted(excluded), "baked_n": len(overlap), "methods": sorted(methods)},
        "provenance": {
            "checkpoint_sha256": manifests[0]["checkpoint_sha256"],
            "campaign_B1B2_manifest_sha256": digest(V3 / "formal/campaign_B1B2/run_manifest_shard0.json"),
            "campaign_B3_manifest_sha256": digest(V3 / "formal/campaign_B3/run_manifest_shard0.json"),
            "unseen_metrics_sha256": digest(CPU / "UNSEEN_OBJECT_METRICS.csv"),
            "seam_metrics_sha256": digest(SEAM / "SEAM_AUDIT_PER_OBJECT.csv"),
            "verified_source_panel_and_view_file_count": verified_source_files,
        },
        "bootstrap": {"unit": "object", "resamples": BOOTSTRAPS, "seed": SEED, "ci": "percentile 95%"},
        "condition_means": means,
        "paired_llh_minus_comparator": contrasts,
        "2d_to_3d_closure": closure,
    }
    (BAKE / "UNIFIED_BAKE_CLOSURE_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n")

    labels = {
        "masked_psnr": "Unseen masked PSNR (dB)",
        "fg_lpips": "Unseen FG-LPIPS (lower is better)",
        "ciede2000": "Unseen CIEDE2000 (lower is better)",
        "seam_dE00_mean": "UV seam ΔE00 mean",
        "control_dE00_mean_2px": "Local 2px control ΔE00",
        "seam_excess_vs_2px_control": "Seam ΔE00 excess over 2px control",
        "seam_dE00_p90": "UV seam ΔE00 P90",
        "seam_dE00_frac_gt10": "UV seam fraction >10 ΔE00",
        "raw_texture_coverage": "Raw UV coverage",
        "texture_coverage_after_inpaint": "UV coverage after inpainting",
        "inpainted_fraction": "Inpainted UV fraction",
        "cross_view_texel_variance": "Cross-view fused-texel variance",
    }
    lines = [
        "# Final unified 3D validation — same-draw bake audit", "",
        "## Scope and authority", "",
        "This report reconciles the frozen image-space source outputs with the unified bake. It is authoritative only for the 20 technically bakeable objects and these exact 8 conditions. The frozen visualization cohort had 24 objects; four were excluded before generation because their source meshes had no UV layer, so original-UV baking was impossible. No objects were replaced. This 20-object result cannot close a strict all-24 bake requirement or support population-level schedule superiority.", "",
        f"All 20 objects have paired condition outputs. The source LLH and GFL outputs join to the same 20 UIDs in campaigns B1B2 and B3 and match on checkpoint, object-list hash, latent seed, reference policy, protocol, and realization. The handoff's source panel and six target-view SHA256s were reverified ({verified_source_files} files). The bake handoff freezes shared references, camera/view selection, texture resolution, bake implementation, and unseen camera set. `cross_view_texel_variance` is a fused-texel disagreement proxy, not a calibrated color-error measure. The legacy seam/control ratio is excluded because zero or near-zero control values produce extreme unstable ratios.", "",
        "Bootstrap summaries below resample objects (10,000 draws; seed 20261005). These are descriptive closure intervals on the fixed subset; the extra diagnostic correlations are exploratory and have no p-values.", "",
        "## Per-condition evidence (N=20)", "",
        "| Condition | Unseen PSNR | Unseen FG-LPIPS | CIEDE2000 | Seam ΔE00 mean | 2px control | Seam excess* | Seam P90 | Seam tail >10 | Raw UV coverage | Coverage after inpaint | Inpainted fraction | Fused-texel variance |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, label in (("no_adapter", "No adapter"), ("native_gfl", "GFL"), ("native_gfh", "GFH"), ("native_gc3", "GC3"), ("lfm_exact", "LFM-EXACT"), ("layer_lhl", "LHL"), ("layer_llh", "LLH")):
        s = means[method]
        lines.append(f"| {label} | {s['masked_psnr']:.3f} | {s['fg_lpips']:.4f} | {s['ciede2000']:.3f} | {s['seam_dE00_mean']:.2f} | {s['control_dE00_mean_2px']:.2f} | {s['seam_excess_vs_2px_control']:.2f} | {s['seam_dE00_p90']:.2f} | {s['seam_dE00_frac_gt10']:.3f} | {s['raw_texture_coverage']:.3f} | {s['texture_coverage_after_inpaint']:.3f} | {s['inpainted_fraction']:.3f} | {s['cross_view_texel_variance']:.5f} |")

    lines += ["", "## Paired LLH differences", "", "Positive PSNR favors LLH; negative LPIPS/CIEDE/seam values favor LLH. Coverage and fusion differences are diagnostic quantities, not quality scores.", "", "| Comparator | Metric | LLH − comparator [95% object-bootstrap CI] | Favorable objects for LLH |", "|---|---|---:|---:|"]
    for method, label in (("native_gfl", "GFL"), ("native_gfh", "GFH"), ("native_gc3", "GC3"), ("lfm_exact", "LFM-EXACT"), ("layer_lhl", "LHL"), ("no_adapter", "No adapter")):
        row = contrasts[f"layer_llh - {method}"]
        favorable = {
            "masked_psnr": row["masked_psnr"]["fraction_delta_positive"],
            "fg_lpips": 1 - row["fg_lpips"]["fraction_delta_positive"],
            "ciede2000": 1 - row["ciede2000"]["fraction_delta_positive"],
            "seam_dE00_mean": 1 - row["seam_dE00_mean"]["fraction_delta_positive"],
            "seam_excess_vs_2px_control": 1 - row["seam_excess_vs_2px_control"]["fraction_delta_positive"],
            "seam_dE00_p90": 1 - row["seam_dE00_p90"]["fraction_delta_positive"],
            "seam_dE00_frac_gt10": 1 - row["seam_dE00_frac_gt10"]["fraction_delta_positive"],
            "inpainted_fraction": None,
            "raw_texture_coverage": None,
            "texture_coverage_after_inpaint": None,
            "cross_view_texel_variance": None,
        }
        for key in ("masked_psnr", "fg_lpips", "ciede2000", "seam_dE00_mean", "seam_excess_vs_2px_control", "seam_dE00_p90", "seam_dE00_frac_gt10"):
            s = row[key]
            metric_label = labels.get(key, key)
            lines.append(f"| {label} | {metric_label} | {s['mean_delta']:+.4f} [{s['ci95'][0]:+.4f}, {s['ci95'][1]:+.4f}] | {100*favorable[key]:.1f}% |")
        for key in ("control_dE00_mean_2px", "inpainted_fraction", "raw_texture_coverage", "texture_coverage_after_inpaint", "cross_view_texel_variance"):
            s = row[key]
            lines.append(f"| {label} | {labels[key]} | {s['mean_delta']:+.5f} [{s['ci95'][0]:+.5f}, {s['ci95'][1]:+.5f}] | descriptive |")

    c = closure
    lines += ["", "## Image-space to baked-output reconciliation", "", "For the exact same 20 UIDs, 2D condition rows and baked unseen-view rows were joined by object. The 2D comparison comes from the frozen B1B2/B3 source ledgers; it is not a separate resampling or a different cohort.", "", "| Endpoint | 2D LLH−GFL [95% CI] | Baked unseen LLH−GFL [95% CI] |", "|---|---:|---:|"]
    for metric, bake_metric in (("fg_psnr", "masked_psnr"), ("fg_lpips", "fg_lpips")):
        a, b = c["2d_delta"][metric], c["3d_delta"][bake_metric]
        lines.append(f"| {metric} | {a['mean_delta']:+.4f} [{a['ci95'][0]:+.4f}, {a['ci95'][1]:+.4f}] | {b['mean_delta']:+.4f} [{b['ci95'][0]:+.4f}, {b['ci95'][1]:+.4f}] |")
    rho = lambda key: c[f"spearman_3d_psnr_delta_vs_{key}"]
    rho_text = lambda key: "undefined (constant paired values)" if rho(key) is None else f"{rho(key):+.3f}"
    lines += ["", f"The object-level 2D versus baked-delta rank correlations are ρ={c['spearman_2d_vs_3d_delta']['fg_psnr']:+.3f} for PSNR and ρ={c['spearman_2d_vs_3d_delta']['fg_lpips']:+.3f} for LPIPS (descriptive, N=20). Correlations of baked PSNR delta with changes in inpaint fraction, raw coverage, fused-texel variance, seam mean and seam P90 are {rho_text('inpainted_fraction')}, {rho_text('raw_texture_coverage')}, {rho_text('cross_view_texel_variance')}, {rho_text('seam_dE00_mean')}, and {rho_text('seam_dE00_p90')}. These exploratory associations do not identify a failure mechanism.", "", "### What the matched comparison supports", "", "There is no demonstrated 2D-to-bake PSNR mismatch on the same 20 objects: both 2D PSNR (+0.279 dB, 95% CI [−1.074, +1.703]) and baked unseen PSNR (+0.144 dB, [−1.316, +1.653]) are uncertain. This is not an equivalence result. LLH has lower FG-LPIPS in both spaces (2D −0.0100, [−0.0196, −0.0009]; baked −0.0239, [−0.0319, −0.0166]). The larger 150-object FRESH_CONFIRM_B estimate is from a disjoint cohort and must not be presented as the same-sample 2D comparator for this bake. UV seam results also favor LLH against most schedules, but CIEDE2000 does not show a reliable schedule advantage. The available coverage, inpainting, fusion-variance, and seam measures do not identify a causal failure path.", "", "The stored seam audit provides raw seam ΔE00 and a local 2-pixel control ΔE00. This report also computes an exploratory excess value as raw seam mean minus the local-control mean; that subtraction is explicitly defined here, but it was not a frozen endpoint and is not used for a confirmatory claim. The original seam analyzer is absent, so the audit's previously described corrected metric cannot be independently reproduced. The stored seam/control ratio is unstable when the control is near zero. A full 24-object bake using newly generated UVs would change the frozen original-UV bake path and requires a new protocol; no such post-hoc rerun was made.", "", "## Closure verdict", "", "`UNIFIED_BAKE_STATUS = PARTIAL_N20_TECHNICAL_SUBSET; PRIOR_CORRECTED_SEAM_REPRODUCIBILITY = OPEN`. The same-draw 3D outputs are traceable and paired for N=20, including unseen-view fidelity, raw seam and exploratory control-adjusted seam diagnostics, coverage, inpainting, and fused-texel diagnostics. The four no-UV exclusions and missing prior seam analyzer mean this is not a complete closure of the strict 24-object/corrected-seam request. It supports no population-level schedule PSNR claim or causal bake-failure explanation. This report supersedes `UNIFIED_COREDRAW_BAKE_REPORT.md` as the current eligible-N20 results summary; the older file remains provenance/history.", "", "## Provenance", "", "- Frozen input handoff: `bake_handoff/BAKE_INPUT_HANDOFF_V3.json`.", "- Exclusion record: `bake_handoff/excluded_uv_missing.json`.", "- Image-space ledgers: `formal/campaign_B1B2/per_object_metrics.csv`, `formal/campaign_B3/per_object_metrics.csv`.", "- Unseen-view ledger: `bake_handoff/cpu_bake_v3/UNSEEN_OBJECT_METRICS.csv`.", "- Per-object bake metadata: `bake_handoff/cpu_bake_v3/<condition>/<uid>/bake_metadata.json`.", "- Seam audit ledger (generator not present): `bake_handoff/BAKE_SEAM_AUDIT_V3/SEAM_AUDIT_PER_OBJECT.csv`.", "- Machine-readable audit and hashes: `bake_handoff/UNIFIED_BAKE_CLOSURE_AUDIT.json`.", ""]
    (V3 / "FINAL_UNIFIED_3D_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
