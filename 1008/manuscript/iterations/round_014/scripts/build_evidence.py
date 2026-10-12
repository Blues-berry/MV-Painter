"""Recompute completed object-level evidence and build manuscript displays."""
from pathlib import Path
import csv
import hashlib
import json
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRIMARY = DATA / "primary_studies"
SUPPLEMENT = DATA / "completed_supplement013/analysis"
METRICS = ["fg_psnr", "fg_ssim", "fg_lpips", "ciede2000"]
SEEDS = [42, 2026, 31415]


def read(path):
    return json.loads(path.read_text())


def csv_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def close(a, b):
    assert np.isclose(a, b, atol=2e-12, rtol=0), (a, b)


def oriented(records, a, b, metric, value="mean_difference", interval="ci95"):
    matches = [r for r in records if {r["a"], r["b"]} == {a, b} and r["metric"] == metric]
    assert len(matches) == 1, (a, b, metric)
    record = dict(matches[0])
    sign = 1 if record["a"] == a else -1
    lo, hi = record[interval]
    return {"a": a, "b": b, "metric": metric,
            "mean": sign * record[value],
            "ci95": [lo, hi] if sign == 1 else [-hi, -lo],
            "p_raw": record.get("p_raw", record.get("signflip_p")),
            "p_adjusted": record.get("p_holm", record.get("holm_p")),
            "source_record": matches[0]}


def check_holm(records):
    previous = 0
    for i, record in enumerate(sorted(records, key=lambda r: r["p_raw"])):
        previous = max(previous, min(1, (len(records) - i) * record["p_raw"]))
        close(previous, record["p_holm"])


def main():
    matched = read(PRIMARY / "MATCHED300_STATISTICS.json")
    native = read(PRIMARY / "MVADAPTER_STATISTICS.json")
    bake10 = read(PRIMARY / "BAKE_STATISTICS.json")
    reference = read(PRIMARY / "REFERENCE_PROTOCOL50_PAIRED_NATIVE_ANALYSIS.json")
    temporal = read(SUPPLEMENT / "TEMPORAL100_COMPARISONS.json")
    bake20 = read(SUPPLEMENT / "BAKE20_COMPARISONS.json")
    validation = {}

    # All six controls are complete and every contrast uses common object IDs.
    rows = csv_rows(PRIMARY / "MATCHED300_OBJECT_METRICS.csv")
    table = {(r["object_uid"], r["condition"]): r for r in rows}
    assert len(rows) == len(table) == 1800
    uids = matched["object_uids"]
    assert len(uids) == len(set(uids)) == 300
    for c, means in matched["means"].items():
        for m, mean in means.items():
            close(np.mean([float(table[u, c][m]) for u in uids]), mean)
    for r in matched["contrasts"]:
        ds = np.array([float(table[u, r["a"]][r["metric"]]) - float(table[u, r["b"]][r["metric"]]) for u in uids])
        close(ds.mean(), r["mean_difference"])
    check_holm([r for r in matched["contrasts"] if r["family"] == "secondary"])
    validation["matched300"] = {"objects": 300, "rows": 1800, "all_means_and_60_contrasts": "PASS"}

    # Retain the original primary without inventing a new confidence interval.
    fresh = csv_rows(PRIMARY / "fresh_c_c3_minus_gfl_object_deltas.csv")
    assert {r["object_uid"] for r in fresh} == set(uids)
    fresh_mean = float(np.mean([float(r["fg_psnr"]) for r in fresh]))
    close(fresh_mean, matched["means"]["Middle-high"]["fg_psnr"] - matched["means"]["Fixed Low"]["fg_psnr"])
    addendum = csv_rows(PRIMARY / "fresh_c_addendum_object_deltas.csv")
    linear_delta = {r["object_uid"]: r for r in addendum if r["contrast"] == "C3-linear"}
    assert set(linear_delta) == set(uids)
    linear_means = {
        m: float(np.mean([float(table[u, "Middle-high"][m]) - float(linear_delta[u][m]) for u in uids]))
        for m in ["fg_psnr", "fg_lpips", "fg_ssim", "edge_ssim"]
    }
    validation["fresh_primary_and_linear"] = {
        "primary_mean": fresh_mean, "linear_means": linear_means,
        "ci_scope": "Original retained primary intervals; no newly chosen bootstrap rule."
    }
    linear_manifest = PRIMARY / "GENERIC_LINEAR_SOURCE_MANIFEST_shard0.json"
    assert hashlib.sha256(linear_manifest.read_bytes()).hexdigest() == "d4bf9eb9a0995d70429a39e5e8bf1f8bb9f1e56c9193abd6ec9c6560884eb7e3"
    profile = read(linear_manifest)["condition_specs"]["gen_linear"]
    requests = profile["scale_trace_requested"]
    assert len(requests) == 50 and profile["spec"]["shape"] == "linear"
    caps = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
    linear_budget = {g:sum(min(float(s[g]),caps[g]) for s in requests) for g in caps}
    for g, expected in {"deep":93.75, "middle":93.75, "shallow":31.25}.items():
        close(linear_budget[g], expected)
    validation["generic_linear_implemented_profile"] = {
        "source_manifest_sha256":hashlib.sha256(linear_manifest.read_bytes()).hexdigest(),
        "spec":profile["spec"], "applied_group_sums":linear_budget,
        "status":"PASS_EXACT_ORIGINAL_MANIFEST_IDENTITY"}

    native_rows = csv_rows(PRIMARY / "MVADAPTER50_per_object_metrics.csv")
    ni = {(r["object_uid"], r["condition"]): r for r in native_rows}
    assert len(ni) == len(native_rows) == 350
    for r in native["contrasts"]:
        ds = [float(ni[u, r["a"]][r["metric"]]) - float(ni[u, r["b"]][r["metric"]]) for u in native["object_uids"]]
        close(np.mean(ds), r["mean_difference"])
    check_holm([r for r in native["contrasts"] if r["family"] == "secondary"])
    validation["native50"] = {"objects": 50, "rows": 350, "all105_contrasts": "PASS"}

    br = csv_rows(PRIMARY / "BAKE10_OBJECT_METRICS.csv")
    bi = {(r["object_uid"], r["method"]): r for r in br}
    assert len(bi) == len(br) == 80  # Seven generated controls and one GT bake.
    for r in bake10["contrasts"]:
        ds = [float(bi[u, r["a"]][r["metric"]]) - float(bi[u, r["b"]][r["metric"]]) for u in bake10["object_uids"]]
        close(np.mean(ds), r["mean_difference"])
    check_holm([r for r in bake10["contrasts"] if r["family"] == "secondary"])
    validation["bake10"] = {"objects": 10, "generated_rows": 70, "GT_rows": 10, "all105_contrasts": "PASS"}

    # Independent reconstruction from all delivered image-view rows.
    raw = csv_rows(DATA / "final_supplement_audit013/ALL_GSO100_VIEW_METRICS.csv")
    cells = {}
    for r in raw:
        key = r["uid"], int(r["seed"]), r["condition"]
        cells.setdefault(key, []).append(r)
    assert len(raw) == 21600 and len(cells) == 3600
    values = {}
    for key, views in cells.items():
        assert sorted(int(r["view"]) for r in views) == list(range(6))
        values[key] = {
            "all": {m: float(np.mean([float(v[m]) for v in views])) for m in METRICS},
            "nonref": {m: float(np.mean([float(v[m]) for v in views if int(v["view"]) != 1])) for m in METRICS},
        }
    guids = read(DATA / "GSO100_UID_ORDER.json")
    assert len(guids) == len(set(guids)) == 100
    for family, scope in [("all_six_comparisons", "all"), ("nonreference_lpips_Holm21", "nonref")]:
        for r in temporal[family]:
            ds = [np.mean([values[u, s, r["a"]][scope][r["metric"]] - values[u, s, r["b"]][scope][r["metric"]] for s in SEEDS]) for u in guids]
            close(np.mean(ds), r["mean_difference"])
    check_holm([r for r in temporal["all_six_comparisons"] if "p_holm" in r])
    check_holm(temporal["nonreference_lpips_Holm21"])
    validation["GSO100"] = {"objects": 100, "cells": 3600, "view_rows": 21600, "all84_and_nonref21_contrasts": "PASS"}

    raw_bake = csv_rows(SUPPLEMENT / "BAKE_VIEW_METRICS.csv")
    bcell = {}
    for r in raw_bake:
        key = r["uid"], int(r["seed"]), r["condition"]
        bcell.setdefault(key, []).append(r)
    assert len(raw_bake) == 8140 and len(bcell) == 740
    bv = {}
    for key, views in bcell.items():
        assert sorted(int(r["view"]) for r in views) == list(range(11))
        bv[key] = {m: float(np.mean([float(v[m]) for v in views])) for m in METRICS}
    for row in bake20["rows"]:
        for m in METRICS:
            close(bv[row["uid"], row["seed"], row["condition"]][m], row["mean_unseen"][m])
    for family in ["original_Holm16_family", "schedule_all84_Holm_family"]:
        for r in bake20[family]:
            ds = [np.mean([bv[u, s, r["a"]][r["metric"]] - bv[u, s, r["b"]][r["metric"]] for s in SEEDS]) for u in guids[:20]]
            close(np.mean(ds), r["mean_difference"])
    check_holm([r for r in bake20["original_Holm16_family"] if "p_holm" in r])
    check_holm(bake20["schedule_all84_Holm_family"])
    validation["GSO20"] = {"objects": 20, "bakes": 740, "view_rows": 8140, "all148_contrasts": "PASS"}

    # Key intervals/tests use their original frozen analysis, not posthoc choices.
    facts = {
        "fresh_primary": {"mean": fresh_mean, "ci95": [.404, .641], "interval_precision": "Parent's rounded original primary interval"},
        "matched_middle_mean": oriented(matched["contrasts"], "Middle-high", "Fixed Applied Mean", "fg_psnr"),
        "matched_middle_late": oriented(matched["contrasts"], "Middle-high", "Late-high", "fg_psnr"),
        "native50_middle_mean": oriented(native["contrasts"], "budget_middle16", "fixed_mean_0p83", "fg_psnr"),
        "GSO100_middle_mean": oriented(temporal["all_six_comparisons"], "middle_high", "fixed_mean", "fg_psnr", interval="ci95_pointwise"),
        "GSO100_late_mean_psnr": oriented(temporal["all_six_comparisons"], "late_high", "fixed_mean", "fg_psnr", interval="ci95_pointwise"),
        "GSO100_late_mean_ssim": oriented(temporal["all_six_comparisons"], "late_high", "fixed_mean", "fg_ssim", interval="ci95_pointwise"),
        "GSO100_late_mean_nonref_lpips": oriented(temporal["nonreference_lpips_Holm21"], "late_high", "fixed_mean", "fg_lpips", interval="ci95_pointwise"),
        "bake10_late_mean": oriented(bake10["contrasts"], "budget_late16", "budget_fixed_mean", "fg_lpips"),
        "bake20_late_mean": oriented(bake20["original_Holm16_family"], "late_high", "fixed_mean", "fg_lpips", interval="ci95_pointwise"),
        "reference50_late_mean_psnr": oriented(reference["secondary"], "budget_late16", "budget_fixed_mean", "fg_psnr", value="difference_a_minus_b"),
        "reference50_late_mean_lpips": oriented(reference["primary"], "budget_late16", "budget_fixed_mean", "fg_lpips", value="difference_a_minus_b"),
        "GSO20_rank": {"mean": bake20["ranking_mean"], "ci95": bake20["ranking_object_ci95"], "scope": "All12 methods"},
        "GSO20_coverage": float(np.mean([np.mean(v) for v in bake20["coverage"].values()])),
    }
    for r in reference["primary"] + reference["secondary"]:
        if {r["a"], r["b"]} == {"budget_late16", "budget_fixed_mean"}:
            rr = read(PRIMARY / "REFERENCE_PROTOCOL50_scores_budget_fixed_mean_budget_late16.json")["rows"]
            idx = {(x["uid"], x["condition"]): x for x in rr}
            ds = [idx[u, r["a"]]["nonreference_mean"][r["metric"]] - idx[u, r["b"]]["nonreference_mean"][r["metric"]] for u in {x["uid"] for x in rr}]
            close(np.mean(ds), r["difference_a_minus_b"])
    validation["reference50_named_contrasts"] = "PASS_RAW_NONREFERENCE_MEANS"

    # A descriptive seven-schedule sensitivity: all20 objects retained.
    schedules = list(temporal["means"])
    rank_records = []
    for r in bake20["ranking_rows"]:
        ii = [r["conditions"].index(c) for c in schedules]
        x = np.array(r["image_lpips"])[ii]
        y = np.array(r["baked_lpips"])[ii]
        rank_records.append({"uid": r["uid"], "rho": float(spearmanr(x, y).statistic),
                             "image_winner": schedules[int(x.argmin())], "bake_winner": schedules[int(y.argmin())]})
    rho = np.array([r["rho"] for r in rank_records])
    rng = np.random.default_rng(131313)
    ci = np.quantile(rho[rng.integers(0, 20, (20000, 20))].mean(1), [.025, .975]).tolist()
    facts["GSO20_schedule_rank"] = {"mean": float(rho.mean()), "ci95": ci,
        "winner_changes": sum(r["image_winner"] != r["bake_winner"] for r in rank_records),
        "n": 20, "scope": "Posthoc descriptive7-schedule sensitivity; no resolved-winner claim", "objects": rank_records}

    inputs = [linear_manifest, PRIMARY / "MATCHED300_STATISTICS.json", PRIMARY / "MATCHED300_OBJECT_METRICS.csv",
              PRIMARY / "MVADAPTER_STATISTICS.json", PRIMARY / "BAKE_STATISTICS.json",
              SUPPLEMENT / "TEMPORAL100_COMPARISONS.json", SUPPLEMENT / "BAKE20_COMPARISONS.json",
              DATA / "final_supplement_audit013/ALL_GSO100_VIEW_METRICS.csv", SUPPLEMENT / "BAKE_VIEW_METRICS.csv"]
    (DATA / "FACTS_round_014.json").write_text(json.dumps({"facts": facts, "validation": validation,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}},
        indent=2) + "\n")

    labels = {
        "Fixed Low": "Fixed Low", "Fixed High": "Fixed High", "Fixed Applied Mean": "Fixed Mean",
        "Early-high": "Early-high", "Middle-high": "C3 / Middle-high", "Late-high": "Late-high",
    }
    lines = []
    for c in ["Fixed Low", "Fixed High", "Fixed Applied Mean", "Early-high", "Middle-high", "Late-high"]:
        m = matched["means"][c]
        budget = "62.5" if c == "Fixed Low" else "125.0" if c == "Fixed High" else "82.5"
        lines.append(f'{labels[c]} & {budget} & 40 & {m["fg_psnr"]:.2f} & {m["fg_lpips"]:.4f} & {m["fg_ssim"]:.4f} & {m["edge_ssim"]:.4f} ' + r"\\")
    m = linear_means
    lines.append(f'Generic Linear$^\\dagger$ & 93.75 & 31.25 & {m["fg_psnr"]:.2f} & {m["fg_lpips"]:.4f} & {m["fg_ssim"]:.4f} & {m["edge_ssim"]:.4f} ' + r"\\")
    (ROOT / "tables/matched_controls014.tex").write_text("\n".join(lines) + "\n")

    rows = [
        ("Native MV-Adapter50", facts["native50_middle_mean"], "Middle--Mean", "FG-PSNR", "P"),
        ("GSO100", facts["GSO100_middle_mean"], "Middle--Mean", "FG-PSNR", "P"),
        ("GSO100", facts["GSO100_late_mean_psnr"], "Late--Mean", "FG-PSNR", "S"),
        ("GSO100", facts["GSO100_late_mean_nonref_lpips"], "Late--Mean", "Nonref LPIPS", "S"),
        ("Reference-protocol50", facts["reference50_late_mean_psnr"], "Late--Mean", "Nonref PSNR", "S"),
    ]
    lines = []
    for cohort, r, contrast, metric, kind in rows:
        digits = 6 if "LPIPS" in metric else 3
        p = r["p_raw"] if kind == "P" else r["p_adjusted"]
        pstr = "$<0.0001$" if p < .0001 else f"{p:.3f}"
        lines.append(f'{cohort} & {contrast} & {metric} & {r["mean"]:+.{digits}f} & [{r["ci95"][0]:+.{digits}f},{r["ci95"][1]:+.{digits}f}] & {kind} & {pstr} ' + r"\\")
    (ROOT / "tables/interface_effects014.tex").write_text("\n".join(lines) + "\n")

    fig, axs = plt.subplots(1, 2, figsize=(11.2, 3.9), gridspec_kw={"width_ratios": [1.4, 1]})
    image = [
        ("GeoTex300: Middle – Mean", facts["matched_middle_mean"]),
        ("MV-Adapter50: Middle – Mean", facts["native50_middle_mean"]),
        ("GSO100: Middle – Mean", facts["GSO100_middle_mean"]),
        ("GSO100: Late – Mean (secondary)", facts["GSO100_late_mean_psnr"]),
        ("Reference protocol50: Late – Mean", facts["reference50_late_mean_psnr"]),
    ]
    for ax, records, title, xlabel in [
        (axs[0], image, "(a) Generated-view FG-PSNR", "Paired difference (dB); higher favors first"),
        (axs[1], [("GeoTex10: Late – Mean", facts["bake10_late_mean"]),
                  ("GSO20: Late – Mean", facts["bake20_late_mean"])],
         "(b) Baked unseen-view FG-LPIPS", "Paired difference; lower favors first"),
    ]:
        for i, (label, r) in enumerate(records):
            lo, hi = r["ci95"]
            ax.errorbar(r["mean"], i, xerr=[[r["mean"]-lo], [hi-r["mean"]]], fmt="o",
                        capsize=3, color="#275977", markersize=4)
        ax.axvline(0, color="#777777", lw=.8, linestyle="--")
        ax.set_yticks(range(len(records)), [x[0] for x in records], fontsize=8)
        ax.invert_yaxis()
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_xlabel(xlabel, fontsize=8)
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(axis="x", alpha=.15)
        ax.spines[["top", "right"]].set_visible(False)
    axs[1].ticklabel_format(axis="x", style="sci", scilimits=(-3, -3))
    fig.tight_layout(w_pad=2.0)
    fig.savefig(ROOT / "figures/fig_allocation_effects014.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "figures/fig_allocation_effects014.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("PASS: object-level means, paired contrasts and original Holm families; evidence displays generated.")


if __name__ == "__main__":
    main()
