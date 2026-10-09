#!/usr/bin/env python3
"""Reaggregate the compact, paired 300-object texture-boundary table."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

BOOTSTRAPS = 10_000
SEED = 20261002
METRICS = ("fg_psnr", "fg_lpips")
PREDICTORS = (
    "gt_fg_lap_var",
    "gt_fg_rgb_std",
    "gt_fg_grad_mag",
    "gt_fg_hf_energy",
    "coverage",
)


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    starts = np.r_[0, np.flatnonzero(np.diff(sorted_values) != 0) + 1]
    ends = np.r_[starts[1:], len(values)]
    group_ranks = (starts + ends - 1) / 2.0
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.repeat(group_ranks, ends - starts)
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = average_ranks(x)
    ry = average_ranks(y)
    rx -= rx.mean()
    ry -= ry.mean()
    return float(np.dot(rx, ry) / np.sqrt(np.dot(rx, rx) * np.dot(ry, ry)))


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted: dict[str, float] = {}
    running = 0.0
    size = len(ordered)
    for index, name in enumerate(ordered):
        running = max(running, (size - index) * p_values[name])
        adjusted[name] = min(1.0, running)
    return adjusted


def read_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 300:
        raise ValueError(f"expected 300 rows, got {len(rows)}")
    uids = [row["object_uid"] for row in rows]
    if len(set(uids)) != len(uids):
        raise ValueError("object_uid values are not unique")
    return sorted(rows, key=lambda row: row["object_uid"])


def paired_bootstrap(deltas: np.ndarray) -> dict:
    rng = np.random.default_rng(SEED)
    indices = rng.integers(0, len(deltas), size=(BOOTSTRAPS, len(deltas)))
    means = deltas[indices].mean(axis=1)
    below = int((means <= 0).sum())
    above = int((means >= 0).sum())
    p_value = min(1.0, 2.0 * min((below + 1) / (BOOTSTRAPS + 1),
                                (above + 1) / (BOOTSTRAPS + 1)))
    return {
        "mean_delta": float(deltas.mean()),
        "median_delta": float(np.median(deltas)),
        "ci95": [float(value) for value in np.percentile(means, [2.5, 97.5])],
        "positive_delta_rate": float((deltas > 0).mean()),
        "negative_delta_rate": float((deltas < 0).mean()),
        "bootstrap_sign_tail_p_plus_one": p_value,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    rows = read_table(args.table)
    result = {
        "n": len(rows),
        "input_sha256": hashlib.sha256(args.table.read_bytes()).hexdigest(),
        "bootstrap_resamples": BOOTSTRAPS,
        "bootstrap_seed": SEED,
        "spearman_method": "average-rank Spearman; paired-object percentile bootstrap",
        "holm_family_size": len(METRICS) * len(PREDICTORS),
        "paired": {},
        "spearman": {},
        "quartiles_by_gt_fg_lap_var": {},
    }
    p_values: dict[str, float] = {}
    deltas: dict[str, np.ndarray] = {}
    predictor_values = {
        name: np.array([float(row[name]) for row in rows])
        for name in PREDICTORS
    }

    for metric in METRICS:
        delta = np.array([float(row[f"delta_{metric}"]) for row in rows])
        deltas[metric] = delta
        paired = paired_bootstrap(delta)
        if metric == "fg_psnr":
            paired["llh_better_rate"] = paired["positive_delta_rate"]
        else:
            paired["llh_better_rate"] = paired["negative_delta_rate"]
        result["paired"][metric] = paired
        result["spearman"][metric] = {}

        for predictor in PREDICTORS:
            values = predictor_values[predictor]
            rho = spearman(delta, values)
            rng = np.random.default_rng(SEED)
            estimates = np.empty(BOOTSTRAPS, dtype=float)
            for index in range(BOOTSTRAPS):
                sample = rng.integers(0, len(delta), len(delta))
                estimates[index] = spearman(delta[sample], values[sample])
            lo, hi = np.percentile(estimates, [2.5, 97.5])
            below = int((estimates <= 0).sum())
            above = int((estimates >= 0).sum())
            p_value = min(1.0, 2.0 * min((below + 1) / (BOOTSTRAPS + 1),
                                        (above + 1) / (BOOTSTRAPS + 1)))
            key = f"{metric}:{predictor}"
            p_values[key] = p_value
            result["spearman"][metric][predictor] = {
                "rho": rho,
                "ci95": [float(lo), float(hi)],
                "bootstrap_sign_tail_p_plus_one": p_value,
            }

    adjusted = holm_adjust(p_values)
    for key, p_value in p_values.items():
        metric, predictor = key.split(":", 1)
        entry = result["spearman"][metric][predictor]
        entry["p_holm"] = adjusted[key]
        entry["reject_holm_0p05"] = adjusted[key] < 0.05
    result["holm_rejections"] = sum(value < 0.05 for value in adjusted.values())

    values = predictor_values["gt_fg_lap_var"]
    labels = np.digitize(values, np.quantile(values, [0.25, 0.5, 0.75]))
    for metric, delta in deltas.items():
        quartiles = {}
        for quartile in range(4):
            mask = labels == quartile
            positive = float((delta[mask] > 0).mean())
            negative = float((delta[mask] < 0).mean())
            quartiles[f"Q{quartile + 1}"] = {
                "n": int(mask.sum()),
                "mean_delta": float(delta[mask].mean()),
                "positive_delta_rate": positive,
                "llh_better_rate": positive if metric == "fg_psnr" else negative,
            }
        result["quartiles_by_gt_fg_lap_var"][metric] = quartiles

    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "n": result["n"],
        "holm_rejections": result["holm_rejections"],
        "fg_psnr_mean_delta": result["paired"]["fg_psnr"]["mean_delta"],
        "fg_psnr_hf_energy_rho": result["spearman"]["fg_psnr"]["gt_fg_hf_energy"]["rho"],
        "fg_psnr_quartiles": result["quartiles_by_gt_fg_lap_var"]["fg_psnr"],
    }, indent=2))


if __name__ == "__main__":
    main()
