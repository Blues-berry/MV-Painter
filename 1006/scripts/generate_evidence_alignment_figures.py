#!/usr/bin/env python3
"""Build source-checked, direction-explicit figures for historical evidence alignment.

These figures describe already observed cohorts. They do not unlock Fresh C, select
human-study stimuli, or rank strategies across metrics/cohorts.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "1006/figures/evidence_alignment"
DATA_DIR = ROOT / "1006/data/derived/evidence_alignment"
B_CSV = ROOT / "1006/data/fresh_b/per_object_metrics.csv"
TEXTURE_REPORT = ROOT / "1006/data/fresh_b/SPEARMAN_TEXTURE_BOUNDARY_B.json"
FRESH_B_PAIRS = [
    ROOT / "1006/data/fresh_b/paired_layer_llh_minus_lfm_exact.json",
    ROOT / "1006/data/fresh_b/paired_layer_llh_minus_layer_hll.json",
    ROOT / "1006/data/fresh_b/paired_layer_llh_minus_a3_baseline.json",
    ROOT / "1006/data/fresh_b/paired_layer_hll_minus_a3_baseline_exploratory.json",
]
C_AUDIT = ROOT / "1006/data/derived/campaign_c_llh_linear_direction_audit.json"
C_PAIR = ROOT / "1006/data/campaign_C_prior/pairwise_layer_llh_vs_gen_linear.json"
C_HOLM = ROOT / "1006/data/campaign_C_prior/HOLM_FAMILY_C.json"
C_B1B2 = ROOT / "1006/data/campaign_B1B2_prior"
C_CAMPAIGN = ROOT / "1006/data/campaign_C_prior"
MVADAPTER = ROOT / "1006/data/cross_backbone/mvadapter/layermap_g_complete.json"
MVADAPTER_VALID = ROOT / "1006/data/cross_backbone/mvadapter/AUDIT_INTERACTION_VALID_TEST_G_COMPLETE.json"
MVDIFFUSION = ROOT / "final/round2/mvdiffusion/results/MVDIFFUSION_PAIRED_BOOTSTRAP.json"
MVD_PANELS = ROOT / "1006/data/cross_backbone/mvdiffusion/panels"

CONTRASTS = [
    ("LLH − LFM-exact", "layer_llh", "lfm_exact", "registered"),
    ("LLH − HLL", "layer_llh", "layer_hll", "registered"),
    ("LLH − LLL", "layer_llh", "a3_baseline", "registered"),
    ("HLL − LLL", "layer_hll", "a3_baseline", "exploratory"),
]
MVD_PAIR_KEYS = (
    ("P1_L-LLH_vs_G-FL", "L-LLH", "G-FL"),
    ("P2_L-LLH_vs_G-LLH", "L-LLH", "G-LLH"),
    ("P3_L-LLH_vs_L-FIX", "L-LLH", "L-FIX"),
    ("P4_L-LHL_vs_G-LHL", "L-LHL", "G-LHL"),
    ("P5_G-LLH_vs_G-LHL", "G-LLH", "G-LHL"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def rows_by_condition(path: Path, conditions: set[str]) -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {name: {} for name in conditions}
    for row in read_csv_rows(path):
        condition = row.get("condition", "")
        if condition not in result:
            continue
        uid = row.get("object_uid") or row.get("object")
        if not uid or uid in result[condition]:
            raise ValueError(f"missing or duplicate {condition} UID: {uid}")
        result[condition][uid] = row
    return result


def finite_float(value: str | float, label: str) -> float:
    out = float(value)
    if not np.isfinite(out):
        raise ValueError(f"non-finite value for {label}: {value}")
    return out


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color="#d8dee8", linewidth=0.65, alpha=0.65)
    ax.set_axisbelow(True)


def build_b_tradeoff() -> dict:
    conditions = {c for _, a, b, _ in CONTRASTS for c in (a, b)}
    rows = rows_by_condition(B_CSV, conditions)
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 9.4), constrained_layout=False)
    derived = []
    colors = {
        "both": "#188977",
        "tradeoff": "#bb7a14",
        "neither": "#68768a",
    }
    for ax, (title, a_name, b_name, status) in zip(axes.flat, CONTRASTS):
        uids = sorted(set(rows[a_name]) & set(rows[b_name]))
        if len(uids) != 150 or set(rows[a_name]) != set(rows[b_name]):
            raise ValueError(f"Fresh B cohort mismatch for {a_name}/{b_name}: {len(uids)}")
        dx, dy = [], []
        for uid in uids:
            a, b = rows[a_name][uid], rows[b_name][uid]
            psnr = finite_float(a["fg_psnr"], f"{uid} A PSNR") - finite_float(b["fg_psnr"], f"{uid} B PSNR")
            lpips = finite_float(a["fg_lpips"], f"{uid} A LPIPS") - finite_float(b["fg_lpips"], f"{uid} B LPIPS")
            dx.append(psnr)
            dy.append(lpips)
            both = (psnr > 0 and lpips < 0) or (psnr < 0 and lpips > 0)
            exact_tie = psnr == 0 or lpips == 0
            category = "both_endpoints_favor_A" if both and psnr > 0 else (
                "both_endpoints_favor_B" if both else "exact_tie" if exact_tie else "metric_tradeoff_or_partial_tie"
            )
            derived.append({
                "cohort": "FRESH_CONFIRM_B", "object_uid": uid,
                "contrast": f"{a_name} - {b_name}", "contrast_status": status,
                "delta_fg_psnr_db_A_minus_B": psnr,
                "delta_fg_lpips_A_minus_B": lpips,
                "endpoint_class": category,
                "single_object_significance": "not_tested; not applicable",
            })
        x, y = np.asarray(dx), np.asarray(dy)
        # Lower LPIPS is favorable. Opposite signs therefore mark joint improvement.
        both_a = (x > 0) & (y < 0)
        both_b = (x < 0) & (y > 0)
        trade = ~(both_a | both_b)
        ax.scatter(x[trade], y[trade], s=22, color=colors["tradeoff"], alpha=0.43,
                   edgecolors="none", label="tradeoff / tie")
        ax.scatter(x[both_b], y[both_b], s=25, color=colors["neither"], alpha=0.55,
                   edgecolors="none", label="both favor B")
        ax.scatter(x[both_a], y[both_a], s=27, color=colors["both"], alpha=0.66,
                   edgecolors="none", label="both favor A")
        ax.axvline(0, color="#3f4854", linewidth=0.9)
        ax.axhline(0, color="#3f4854", linewidth=0.9)
        ax.scatter([x.mean()], [y.mean()], marker="X", s=85, color="#202a36",
                   edgecolors="white", linewidths=0.8, zorder=5, label="cohort mean")
        ax.set_title(f"{title}  ·  {status}  ·  N=150", loc="left", fontsize=11, weight="semibold")
        ax.set_xlabel("FG-PSNR: A − B (dB; positive favors A)")
        ax.set_ylabel("FG-LPIPS: A − B (negative favors A)")
        ax.text(0.02, 0.02, f"mean ΔPSNR={x.mean():+.3f} dB\nmean ΔLPIPS={y.mean():+.4f}",
                transform=ax.transAxes, fontsize=8.5, va="bottom", ha="left",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#cbd3de", "alpha": 0.88})
        style_axes(ax)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=4, loc="center", bbox_to_anchor=(0.5, 0.09), frameon=False)
    fig.suptitle("Fresh Confirm B: object-level endpoint tradeoffs", fontsize=15, weight="bold", y=0.97)
    fig.text(0.5, 0.018,
             "Paired object differences; each point is one object (one seed). No per-object significance. "
             "HLL−LLL is exploratory; this plot does not create a cross-metric winner.",
             ha="center", fontsize=9, color="#4b5563")
    fig.subplots_adjust(left=0.11, right=0.985, top=0.91, bottom=0.17, wspace=0.28, hspace=0.34)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "fresh_b_strategy_endpoint_tradeoffs.png", dpi=190, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fresh_b_strategy_endpoint_tradeoffs.pdf", bbox_inches="tight")
    plt.close(fig)
    write_csv(DATA_DIR / "fresh_b_strategy_endpoint_tradeoffs.csv", derived)
    return {"N_per_contrast": 150, "contrasts": len(CONTRASTS), "points": len(derived)}


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_campaign_condition(base: Path, shards: int, condition: str) -> dict[str, dict]:
    result = {}
    for shard in range(shards):
        path = base / f"rows_shard{shard}.json"
        for row in read_json(path):
            if row.get("condition") != condition:
                continue
            uid = str(row.get("object_uid") or row.get("object"))
            if uid in result:
                raise ValueError(f"duplicate historical C row {condition}/{uid}")
            result[uid] = row
    return result


def build_historical_c_tradeoff() -> dict:
    audit = read_json(C_AUDIT)
    if audit.get("status") != "PASS_SOURCE_ROWS_RECONSTRUCTED":
        raise ValueError("historical C source-row audit is not PASS")
    llh = load_campaign_condition(C_B1B2, 4, "layer_llh")
    linear = load_campaign_condition(C_CAMPAIGN, 2, "gen_linear")
    if set(llh) != set(linear) or len(llh) != 300:
        raise ValueError(f"historical C cohorts differ: LLH={len(llh)}, linear={len(linear)}")
    pairs = []
    for uid in sorted(llh):
        a, b = llh[uid], linear[uid]
        if a.get("input_hashes") != b.get("input_hashes") or len(a.get("input_hashes", {})) != 6:
            raise ValueError(f"historical C shared-input hash mismatch: {uid}")
        if a.get("object_idx") != b.get("object_idx") or a.get("seed_base") != b.get("seed_base"):
            raise ValueError(f"historical C index/seed mismatch: {uid}")
        pairs.append({
            "cohort": "campaign_B1B2 ∩ campaign_C (retrospective same-UID cohort)",
            "object_uid": uid,
            "delta_fg_psnr_db_llh_minus_linear": finite_float(a["fg_psnr"], uid) - finite_float(b["fg_psnr"], uid),
            "delta_fg_lpips_llh_minus_linear": finite_float(a["fg_lpips"], uid) - finite_float(b["fg_lpips"], uid),
        })
    expected = audit["tests"]
    for metric, key in [("fg_psnr", "delta_fg_psnr_db_llh_minus_linear"), ("fg_lpips", "delta_fg_lpips_llh_minus_linear")]:
        mean = float(np.mean([r[key] for r in pairs]))
        if not np.isclose(mean, expected[metric]["mean_delta"], atol=1e-12, rtol=1e-12):
            raise ValueError(f"raw-row C mean does not match audited JSON for {metric}")
    write_csv(DATA_DIR / "campaign_c_llh_linear_object_deltas.csv", pairs)

    fig, ax = plt.subplots(figsize=(8.4, 6.5), constrained_layout=True)
    x = np.asarray([r["delta_fg_psnr_db_llh_minus_linear"] for r in pairs])
    y = np.asarray([r["delta_fg_lpips_llh_minus_linear"] for r in pairs])
    a_joint = (x > 0) & (y < 0)
    b_joint = (x < 0) & (y > 0)
    trade = ~(a_joint | b_joint)
    ax.scatter(x[trade], y[trade], s=19, alpha=0.35, color="#ad7417", edgecolors="none", label="endpoint tradeoff / tie")
    ax.scatter(x[b_joint], y[b_joint], s=24, alpha=0.55, color="#65758a", edgecolors="none", label="both favor linear")
    ax.scatter(x[a_joint], y[a_joint], s=25, alpha=0.65, color="#168674", edgecolors="none", label="both favor LLH")
    ax.axvline(0, color="#3f4854", linewidth=0.9)
    ax.axhline(0, color="#3f4854", linewidth=0.9)
    ax.scatter([x.mean()], [y.mean()], marker="X", s=100, color="#202a36", edgecolors="white", zorder=5, label="cohort mean")
    ax.set_xlabel("FG-PSNR: LLH − linear (dB; positive favors LLH)")
    ax.set_ylabel("FG-LPIPS: LLH − linear (negative favors LLH)")
    ax.set_title("Historical campaign C comparison · retrospective sibling campaigns · N=300", loc="left", weight="semibold")
    spsnr, slpips = expected["fg_psnr"], expected["fg_lpips"]
    ax.text(0.02, 0.98,
            f"FG-PSNR mean {spsnr['mean_delta']:+.4f} dB, 95% CI [{spsnr['ci95'][0]:+.4f}, {spsnr['ci95'][1]:+.4f}], Holm p={spsnr['holm_adjusted_p']:.4f}\n"
            f"FG-LPIPS mean {slpips['mean_delta']:+.4f}, 95% CI [{slpips['ci95'][0]:+.4f}, {slpips['ci95'][1]:+.4f}], Holm p={slpips['holm_adjusted_p']:.4f}\n"
            "LLH and linear share UID, seed, and six input hashes; legacy config hashes are absent.",
            transform=ax.transAxes, va="top", fontsize=8.7,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd3de", "alpha": 0.92})
    style_axes(ax)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "historical_campaign_c_llh_linear_tradeoff.png", dpi=190, bbox_inches="tight")
    fig.savefig(FIG_DIR / "historical_campaign_c_llh_linear_tradeoff.pdf", bbox_inches="tight")
    plt.close(fig)
    return {"N": len(pairs), "input_hash_matches": 300, "status": audit["status"]}


def build_texture_heterogeneity() -> dict:
    rows = rows_by_condition(B_CSV, {"layer_llh", "native_gfl"})
    uids = sorted(set(rows["layer_llh"]) & set(rows["native_gfl"]))
    if len(uids) != 150 or set(rows["layer_llh"]) != set(rows["native_gfl"]):
        raise ValueError("Fresh B LLH/GFL texture-boundary join is not complete")
    data = []
    for uid in uids:
        a, b = rows["layer_llh"][uid], rows["native_gfl"][uid]
        x = finite_float(a["gt_fg_lap_var"], uid)
        if not np.isclose(x, finite_float(b["gt_fg_lap_var"], uid), atol=1e-12):
            raise ValueError(f"GT texture statistic differs by condition for {uid}")
        data.append({
            "cohort": "FRESH_CONFIRM_B", "object_uid": uid, "contrast": "layer_llh - native_gfl",
            "gt_fg_lap_var": x,
            "delta_fg_psnr_db_llh_minus_gfl": finite_float(a["fg_psnr"], uid) - finite_float(b["fg_psnr"], uid),
            "delta_fg_lpips_llh_minus_gfl": finite_float(a["fg_lpips"], uid) - finite_float(b["fg_lpips"], uid),
        })
    write_csv(DATA_DIR / "fresh_b_gt_texture_heterogeneity.csv", data)
    report = read_json(TEXTURE_REPORT)
    ps = report["tests"]["fg_psnr"]["gt_fg_lap_var"]
    lp = report["tests"]["fg_lpips"]["gt_fg_lap_var"]
    actual_ps = spearmanr([d["gt_fg_lap_var"] for d in data], [d["delta_fg_psnr_db_llh_minus_gfl"] for d in data]).statistic
    actual_lp = spearmanr([d["gt_fg_lap_var"] for d in data], [d["delta_fg_lpips_llh_minus_gfl"] for d in data]).statistic
    if not np.isclose(actual_ps, ps["rho"], atol=1e-10) or not np.isclose(actual_lp, lp["rho"], atol=1e-10):
        raise ValueError("reconstructed texture-complexity Spearman estimates do not match source report")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), constrained_layout=True)
    x = np.asarray([d["gt_fg_lap_var"] for d in data])
    yvals = [np.asarray([d[k] for d in data]) for k in (
        "delta_fg_psnr_db_llh_minus_gfl", "delta_fg_lpips_llh_minus_gfl")]
    specs = [
        ("Δ FG-PSNR (dB): LLH − GFL", ps, yvals[0], "positive favors LLH"),
        ("Δ FG-LPIPS: LLH − GFL", lp, yvals[1], "negative favors LLH"),
    ]
    for ax, (title, stats, y, direction) in zip(axes, specs):
        ax.scatter(x, y, s=25, alpha=0.45, color="#277c9b", edgecolors="none")
        ax.axhline(0, color="#3f4854", linewidth=0.9)
        ax.set_xscale("log")
        ax.set_xlabel("GT foreground Laplacian variance (log scale)")
        ax.set_ylabel(title)
        ax.set_title(title, loc="left", fontsize=10.5, weight="semibold")
        ci = stats["ci95"]
        ax.text(0.03, 0.97, f"Spearman ρ={stats['rho']:+.3f}\n95% object-bootstrap CI [{ci[0]:+.3f}, {ci[1]:+.3f}]\n{direction}",
                transform=ax.transAxes, va="top", fontsize=8.8,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#cbd3de", "alpha": 0.92})
        style_axes(ax)
    fig.suptitle("Fresh Confirm B: response heterogeneity by GT texture complexity · N=150", fontsize=14, weight="bold")
    fig.text(0.5, -0.01,
             "Exploratory association only: no complexity threshold, causal explanation, or post hoc subgroup claim is implied.",
             ha="center", fontsize=9, color="#4b5563")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "fresh_b_gt_texture_complexity_heterogeneity.png", dpi=190, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fresh_b_gt_texture_complexity_heterogeneity.pdf", bbox_inches="tight")
    plt.close(fig)
    return {"N": len(data), "rho_fg_psnr": float(actual_ps), "rho_fg_lpips": float(actual_lp)}


def build_mvadapter_boundary() -> dict:
    result = read_json(MVADAPTER)
    valid = read_json(MVADAPTER_VALID)
    cells = result["cells"]
    layers, windows = ["deep", "middle", "shallow"], ["1", "2", "3", "4", "5"]
    values = np.asarray([[cells[f"{layer}_W{window}"]["mean_delta"] for window in windows] for layer in layers])
    fig, ax = plt.subplots(figsize=(12.0, 5.4), constrained_layout=False)
    lim = max(float(np.max(np.abs(values))), 1e-8)
    im = ax.imshow(values, cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(5), [f"W{w}" for w in windows])
    ax.set_yticks(range(3), [x.capitalize() for x in layers])
    ax.set_xlabel("Window")
    ax.set_ylabel("Layer group")
    ax.set_title("MV-Adapter: per-cell FG-LPIPS effects relative to G baseline · N=98", loc="left", weight="semibold")
    for i, layer in enumerate(layers):
        for j, window in enumerate(windows):
            key = f"{layer}_W{window}"
            cell, holm = cells[key], result["holm_family"][key]
            star = " *" if float(holm["p_holm"]) < 0.05 else ""
            color = "white" if abs(values[i, j]) > lim * 0.57 else "#17212d"
            ax.text(j, i, f"Δ={cell['mean_delta']:+.1e}\npHolm={holm['p_holm']:.3g}{star}",
                    ha="center", va="center", fontsize=8.0, color=color)
    fig.subplots_adjust(left=0.10, right=0.80, top=0.84, bottom=0.30)
    cax = fig.add_axes([0.84, 0.30, 0.025, 0.50])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("FG-LPIPS Δ (negative favors treatment)", fontsize=8.5)
    interaction = result["interaction"]
    gtest = valid["G_fg_lpips"]
    wald_p = float(gtest["p"])
    wald_holm = float(valid["exploratory_metric_family_holm"]["adjusted_p"]["fg_lpips"])
    fig.text(0.10, 0.15,
             f"* Per-cell Holm p<.05: shallow W3–W5 survive correction. These localized cell effects do not establish a global interaction.\n"
             f"Global checks: cluster-bootstrap p={interaction['p_cluster_bootstrap']:.4f}; exploratory finite-sample Wald p={wald_p:.4f}, "
             f"four-metric Holm p={wald_holm:.4f}.",
             fontsize=8.7, ha="left", va="center", color="#394453")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "mvadapter_fg_lpips_interface_boundary.png", dpi=190, bbox_inches="tight")
    fig.savefig(FIG_DIR / "mvadapter_fg_lpips_interface_boundary.pdf", bbox_inches="tight")
    plt.close(fig)
    rows = []
    for layer in layers:
        for window in windows:
            key = f"{layer}_W{window}"
            cell, holm = cells[key], result["holm_family"][key]
            rows.append({"cohort": "MV-Adapter G complete", "n_objects": cell["n"], "layer": layer,
                         "window": window, "mean_fg_lpips_delta_treatment_minus_baseline": cell["mean_delta"],
                         "ci95_low": cell["ci95"][0], "ci95_high": cell["ci95"][1],
                         "p_holm_16_test_family": holm["p_holm"], "cell_reject_holm": bool(result["reject_h0_holm"][key])})
    write_csv(DATA_DIR / "mvadapter_fg_lpips_cells.csv", rows)
    return {"N": 98, "cells": len(rows), "bootstrap_interaction_p": interaction["p_cluster_bootstrap"],
            "exploratory_wald_interaction_p": wald_p, "exploratory_wald_holm_p": wald_holm}


def read_mvd_panel(condition: str) -> dict[str, dict[str, str]]:
    path = MVD_PANELS / f"panel_{condition}_75" / "per_object_metrics_ext.csv"
    rows = read_csv_rows(path)
    result = {}
    for row in rows:
        uid = row["source_uid"]
        if uid in result:
            raise ValueError(f"duplicate MVDiffusion source UID {condition}/{uid}")
        result[uid] = row
    return result


def build_mvdiffusion_interface() -> dict:
    report = read_json(MVDIFFUSION)
    output_rows = []
    object_rows = []
    plot_data = {"interop_psnr": [], "interop_fg_lpips": []}
    for key, left, right in MVD_PAIR_KEYS:
        saved = report["comparisons"][key]
        if (saved["left"], saved["right"]) != (left, right):
            raise ValueError(f"MVDiffusion source mapping mismatch for {key}")
        a, b = read_mvd_panel(left), read_mvd_panel(right)
        uids = sorted(set(a) & set(b))
        if len(a) != 75 or len(b) != 75 or len(uids) != 75:
            raise ValueError(f"MVDiffusion cohort mismatch in {key}")
        for metric in plot_data:
            raw_delta = np.asarray([finite_float(a[u][metric], u) - finite_float(b[u][metric], u) for u in uids])
            favorable_delta = raw_delta if metric == "interop_psnr" else -raw_delta
            for uid, raw_value, favorable_value in zip(uids, raw_delta, favorable_delta):
                object_rows.append({
                    "cohort": "MVDiffusion depth/text interop diagnostic", "object_uid": uid,
                    "comparison": key, "left": left, "right": right, "metric": metric,
                    "raw_left_minus_right": float(raw_value),
                    "favorable_oriented_delta_positive_favors_left": float(favorable_value),
                })
            rng = np.random.default_rng(report["seed"])
            draws = rng.integers(0, len(uids), size=(report["resamples"], len(uids)))
            means = favorable_delta[draws].mean(axis=1)
            ci = np.percentile(means, [2.5, 97.5])
            summary = saved["metrics"][metric]
            if not np.isclose(favorable_delta.mean(), summary["paired_mean_delta"], atol=1e-11):
                raise ValueError(f"MVDiffusion favorable-oriented mean mismatch {key}/{metric}")
            if not np.allclose(ci, [summary["ci95_low"], summary["ci95_high"]], atol=1e-11):
                raise ValueError(f"MVDiffusion bootstrap CI mismatch {key}/{metric}")
            favorable_rate = float(np.mean(favorable_delta > 0))
            record = {
                "cohort": "MVDiffusion depth/text interop diagnostic", "n_objects": len(uids),
                "comparison": key, "left": left, "right": right, "metric": metric,
                "favorable_oriented_delta_positive_favors_left": True,
                "mean_favorable_oriented_delta": float(favorable_delta.mean()),
                "ci95_low_nominal": float(ci[0]), "ci95_high_nominal": float(ci[1]),
                "favorable_object_rate": favorable_rate,
                "multiplicity": "nominal; no cross-comparison pooling",
            }
            output_rows.append(record)
            plot_data[metric].append(record)
    write_csv(DATA_DIR / "mvdiffusion_interface_effects.csv", output_rows)
    write_csv(DATA_DIR / "mvdiffusion_interface_object_deltas.csv", object_rows)

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.3), constrained_layout=False)
    labels = [f"{row['left']} vs {row['right']}" for row in plot_data["interop_psnr"]]
    specs = [
        ("interop_psnr", "Interop FG-PSNR (dB)", "positive favors left"),
        ("interop_fg_lpips", "Interop FG-LPIPS", "positive favors left (left has lower LPIPS)"),
    ]
    for ax, (metric, title, direction) in zip(axes, specs):
        entries = plot_data[metric]
        yy = np.arange(len(entries))[::-1]
        for i, row in enumerate(entries):
            ax.errorbar(row["mean_favorable_oriented_delta"], yy[i],
                        xerr=[[row["mean_favorable_oriented_delta"] - row["ci95_low_nominal"]],
                              [row["ci95_high_nominal"] - row["mean_favorable_oriented_delta"]]],
                        fmt="o", color="#277c9b", ecolor="#277c9b", capsize=3, markersize=5)
        ax.axvline(0, color="#343d48", linewidth=0.9)
        ax.set_yticks(yy, labels)
        ax.set_xlabel("Favorable-oriented effect (positive favors left)")
        ax.set_title(title, loc="left", weight="semibold")
        style_axes(ax)
    axes[1].set_title("Interop FG-LPIPS (sign reversed so positive favors left)", loc="left", weight="semibold")
    fig.suptitle("MVDiffusion interface diagnostic · N=75 per pair · nominal object-bootstrap 95% CIs", fontsize=14, weight="bold", y=0.96)
    fig.text(0.5, 0.035,
             "Separate correspondence-aware interface experiment. No pooled cross-backbone effect or architecture-causal inference.",
             ha="center", fontsize=8.8, color="#4b5563")
    fig.subplots_adjust(left=0.23, right=0.985, top=0.88, bottom=0.18, wspace=0.46)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "mvdiffusion_interface_boundary.png", dpi=190, bbox_inches="tight")
    fig.savefig(FIG_DIR / "mvdiffusion_interface_boundary.pdf", bbox_inches="tight")
    plt.close(fig)
    return {"N_per_pair": 75, "pairs": len(MVD_PAIR_KEYS), "metrics": len(plot_data)}


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "fresh_b_tradeoff": build_b_tradeoff(),
        "historical_campaign_c": build_historical_c_tradeoff(),
        "fresh_b_texture_heterogeneity": build_texture_heterogeneity(),
        "mvadapter_interface_boundary": build_mvadapter_boundary(),
        "mvdiffusion_interface_boundary": build_mvdiffusion_interface(),
    }
    source_paths = [B_CSV, TEXTURE_REPORT, *FRESH_B_PAIRS, C_AUDIT, C_PAIR, C_HOLM,
                    *sorted(C_B1B2.glob("rows_shard*.json")), *sorted(C_CAMPAIGN.glob("rows_shard*.json")),
                    MVADAPTER, MVADAPTER_VALID, MVDIFFUSION,
                    *sorted(MVD_PANELS.glob("panel_*_75/per_object_metrics_ext.csv")), Path(__file__)]
    figure_outputs = [p for p in sorted(FIG_DIR.iterdir()) if p.is_file() and p.name != "FIGURE_SOURCE_MANIFEST.json"]
    data_outputs = [p for p in sorted(DATA_DIR.iterdir()) if p.is_file()]
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "HISTORICAL_ALIGNMENT_FIGURES_SOURCE_CHECKED",
        "manuscript_edited": False,
        "fresh_c_used": False,
        "fresh_d_started": False,
        "human_stimuli_selected": False,
        "results": results,
        "figures": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)}
                    for p in figure_outputs if p.suffix in {".png", ".pdf"}],
        "derived_data": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)}
                         for p in data_outputs if p.suffix == ".csv"],
        "sources": {str(p.relative_to(ROOT)): sha256(p) for p in source_paths},
        "interpretation_limits": [
            "Fresh B plots describe observed object-wise differences and do not make per-object significance claims.",
            "Historical campaign C is retrospective across sibling campaigns; shared input hashes match, legacy config hashes are absent.",
            "GT texture complexity is an exploratory association, not a decision threshold or causal boundary.",
            "MV-Adapter and MVDiffusion use different interfaces and are not pooled or used for architecture-causal inference.",
            "No comparison is declared an overall winner across metrics or cohorts.",
        ],
    }
    (FIG_DIR / "FIGURE_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
