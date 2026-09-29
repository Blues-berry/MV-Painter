"""Audit clean-v2 results by retained/replacement source group."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from round2_stats import paired_csv_summary


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
PROV = ROOT / "final/round2/main_adapter_clean_v2/clean_v2_provenance_300.csv"
OUT = ROOT / "final/round2/main_adapter_clean_v2"
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
METRICS = ("full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim")
DIRECTION = {m: m not in {"full_lpips", "fg_lpips"} for m in METRICS}


def load_rows(method: str) -> dict[str, dict[str, str]]:
    with (EVAL / f"per_object_{method}.csv").open(newline="") as f:
        return {r["object"]: r for r in csv.DictReader(f)}


def main() -> None:
    provenance = list(csv.DictReader(PROV.open()))
    groups = {"retained_199": [r for r in provenance if r["retained_or_replaced"] == "retained"], "replacement_101": [r for r in provenance if r["retained_or_replaced"] == "replaced"]}
    rows = {m: load_rows(m) for m in METHODS}
    result = {"protocol": "clean-v2-source-stratified-audit-v1", "groups": {}, "set_relations": {}}

    hist = {x.strip() for x in (ROOT / "mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt").read_text().splitlines() if x.strip()}
    pool = {x.strip() for x in (ROOT / "data/train_data/rendered_full/train_objects_1200.txt").read_text().splitlines() if x.strip()}
    replacement = {r["uid"] for r in groups["replacement_101"]}
    clean = {r["uid"] for r in provenance}
    result["set_relations"] = {
        "historical_train_1118_count": len(hist),
        "train_objects_1200_count": len(pool),
        "historical_intersection_candidate_pool_count": len(hist & pool),
        "replacement_101_count": len(replacement),
        "replacement_subset_candidate_pool": replacement <= pool,
        "replacement_intersection_historical_train": len(replacement & hist),
        "clean_v2_count": len(clean),
        "clean_v2_intersection_historical_train": len(clean & hist),
        "clean_v2_decomposition": "199 retained old-eval UIDs + 101 replacement UIDs",
    }

    for name, members in groups.items():
        object_ids = [r["object"] for r in members]
        result["groups"][name] = {"n": len(object_ids), "uids": [r["uid"] for r in members], "objects": object_ids, "means": {}}
        for method in METHODS:
            result["groups"][name]["means"][method] = {m: float(np.mean([float(rows[method][o][m]) for o in object_ids])) for m in METRICS}
        result["groups"][name]["paired_c3_vs"] = {}
        for baseline in ("fixed_low", "fixed_high"):
            result["groups"][name]["paired_c3_vs"][baseline] = paired_csv_summary(
                rows["c3"], rows[baseline], metrics=METRICS, object_ids=object_ids,
                higher_is_better=DIRECTION, seed=20260928, n_resamples=10000,
            )

    (OUT / "source_stratified_results.json").write_text(json.dumps(result, indent=2) + "\n")
    md = ["# Clean-v2 source-stratified results", "", "This is a prespecified source-composition sensitivity audit. It does not remove or select objects.", "", "## Set relations", ""]
    for k, v in result["set_relations"].items(): md.append(f"- `{k}`: `{v}`")
    md += ["", "## Group means", "", "| group | n | condition | Full PSNR | FG PSNR | Full SSIM | FG SSIM | FG-LPIPS | Edge-SSIM |", "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
    for group, data in result["groups"].items():
        for method in METHODS:
            x = data["means"][method]
            md.append(f"| {group} | {data['n']} | {method} | {x['full_psnr']:.3f} | {x['fg_psnr']:.3f} | {x['full_ssim']:.3f} | {x['fg_ssim']:.3f} | {x['fg_lpips']:.3f} | {x['edge_ssim']:.3f} |")
    md += ["", "## Paired C3 differences", "", "The JSON contains 10,000 object-level bootstrap resamples and 95% CIs for C3 versus fixed-low and fixed-high. All pairs use source UIDs mapped to the clean-v2 object IDs; no sequence-number substitution is used.", ""]
    (OUT / "CLEAN_V2_SOURCE_STRATIFIED_RESULTS.md").write_text("\n".join(md))
    print(json.dumps(result["set_relations"], indent=2))


if __name__ == "__main__":
    main()
