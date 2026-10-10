#!/usr/bin/env python3
"""Audit the post hoc native-GC3 versus native-GFL pair in FRESH_CONFIRM_B.

FRESH_CONFIRM_B's confirmatory families did not register this B3 pair; its
outcomes were already unblinded when this supplemental analysis was added.
The output is therefore a retrospective, disjoint-object-cohort comparison,
not a preregistered independent confirmation.

Run from the repository root:
    python 1006/scripts/analyze_fresh_b_c3_gfl_posthoc.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "fresh_b" / "per_object_metrics.csv"
OUTPUT = ROOT / "data" / "derived"
N_BOOT = 10_000
SEED = 20261002  # same paired-bootstrap implementation as the B audit
LEFT = "native_gc3"
RIGHT = "native_gfl"
METRICS = (
    ("fg_psnr", "higher"),
    ("fg_ssim", "higher"),
    ("fg_lpips", "lower"),
    ("full_psnr", "higher"),
    ("full_ssim", "higher"),
    ("full_lpips", "lower"),
    ("edge_ssim", "higher"),
)


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = np.ones(len(p_values), dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))
    rows = {LEFT: {}, RIGHT: {}}
    for row in all_rows:
        if row["condition"] in rows:
            uid = row["object_uid"]
            if uid in rows[row["condition"]]:
                raise ValueError(f"duplicate row for {uid}/{row['condition']}")
            rows[row["condition"]][uid] = row
    if len(rows[LEFT]) != 150 or len(rows[RIGHT]) != 150 or set(rows[LEFT]) != set(rows[RIGHT]):
        raise ValueError(f"paired coverage failed: {LEFT}={len(rows[LEFT])}, {RIGHT}={len(rows[RIGHT])}")

    uids = sorted(rows[LEFT])
    summary = []
    delta_fields = ["object_uid", "object_idx", "contrast"] + [metric for metric, _ in METRICS]
    deltas_by_metric: dict[str, np.ndarray] = {}
    metrics_output = []
    for metric, direction in METRICS:
        delta = np.asarray(
            [float(rows[LEFT][uid][metric]) - float(rows[RIGHT][uid][metric]) for uid in uids],
            dtype=np.float64,
        )
        deltas_by_metric[metric] = delta
        rng = np.random.default_rng(SEED)
        sample_indices = rng.integers(0, len(delta), size=(N_BOOT, len(delta)))
        bootstrap_means = delta[sample_indices].mean(axis=1)
        p_raw = max(
            2.0 * min(float(np.mean(bootstrap_means <= 0)), float(np.mean(bootstrap_means >= 0))),
            1.0 / N_BOOT,
        )
        low, high = np.percentile(bootstrap_means, [2.5, 97.5])
        favorable = delta > 0 if direction == "higher" else delta < 0
        summary.append(
            {
                "cohort": "FRESH_CONFIRM_B",
                "analysis_status": "post-hoc; outcomes previously unblinded; B3 descriptive condition pair",
                "left": LEFT,
                "right": RIGHT,
                "contrast": f"{LEFT}-{RIGHT}",
                "metric": metric,
                "favorable_direction": direction,
                "mean_delta_left_minus_right": float(delta.mean()),
                "median_delta_left_minus_right": float(np.median(delta)),
                "ci95_low_nominal": float(low),
                "ci95_high_nominal": float(high),
                "favorable_objects": int(favorable.sum()),
                "unfavorable_objects": int((~favorable & (delta != 0)).sum()),
                "ties": int((delta == 0).sum()),
                "n_objects": len(delta),
                "p_bootstrap_raw": p_raw,
                "bootstrap_resamples": N_BOOT,
                "bootstrap_seed": SEED,
                "p_method": "two-sided paired-bootstrap sign-crossing; minimum 1/10000",
                "multiplicity_family": "post-hoc Holm across seven Core-7 endpoints; not a registered confirmatory family",
            }
        )
        metrics_output.append(p_raw)

    for row, adjusted in zip(summary, holm_adjust(metrics_output)):
        row["p_holm_posthoc_7_endpoints"] = adjusted

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "fresh_b_c3_minus_gfl_posthoc.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    with (OUTPUT / "fresh_b_c3_minus_gfl_object_deltas.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=delta_fields)
        writer.writeheader()
        for i, uid in enumerate(uids):
            writer.writerow(
                {
                    "object_uid": uid,
                    "object_idx": rows[LEFT][uid]["object_idx"],
                    "contrast": f"{LEFT}-{RIGHT}",
                    **{metric: f"{values[i]:.12g}" for metric, values in deltas_by_metric.items()},
                }
            )

    print(f"Wrote 7 endpoint rows and {len(uids)} object-paired rows under {OUTPUT.relative_to(ROOT)}")
    for row in summary:
        print(
            f"{row['metric']}: {row['mean_delta_left_minus_right']:+.6f} "
            f"[{row['ci95_low_nominal']:+.6f}, {row['ci95_high_nominal']:+.6f}], "
            f"favorable {row['favorable_objects']}/{row['n_objects']}, "
            f"post-hoc Holm p={row['p_holm_posthoc_7_endpoints']:.4g}"
        )


if __name__ == "__main__":
    main()
