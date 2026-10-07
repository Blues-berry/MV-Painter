#!/usr/bin/env python3
"""Recompute the retrospective strict-276 C3 pairs from packaged object rows.

Run from the repository root:
    python 1006/scripts/analyze_strict276_c3_retrospective.py

This is a supplemental, post hoc comparison. It must not be described as a
registered primary contrast, a new independent confirmation, or proof of
bit-identical realizations.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "strict276" / "source_rows"
OUTPUT = ROOT / "data" / "derived"
N_BOOT = 10_000
BOOT_SEED = 20260930
METRICS = (
    ("fg_psnr", "higher"),
    ("fg_ssim", "higher"),
    ("fg_lpips", "lower"),
    ("full_psnr", "higher"),
    ("full_ssim", "higher"),
    ("full_lpips", "lower"),
    ("edge_ssim", "higher"),
)
PAIRS = (("gc3", "gfl"), ("gc3", "gfh"))


def read_rows(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_index = {int(row["object_idx"]): row for row in rows}
    if len(rows) != 276 or len(by_index) != 276:
        raise ValueError(f"{path.name}: expected 276 unique object rows")
    if set(by_index) != set(range(276)):
        raise ValueError(f"{path.name}: object_idx must cover 0..275")
    return by_index


def bootstrap_ci(delta: np.ndarray, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(delta), size=(N_BOOT, len(delta)))
    means = delta[indices].mean(axis=1)
    low, high = np.quantile(means, (0.025, 0.975), method="linear")
    return float(low), float(high)


def main() -> None:
    rows = {name: read_rows(SOURCE / f"{name}.csv") for name in ("gc3", "gfl", "gfh")}
    ids = sorted(rows["gc3"])
    objects = {name: [rows[name][i]["object"] for i in ids] for name in rows}
    if any(objects[name] != objects["gc3"] for name in ("gfl", "gfh")):
        raise ValueError("Object labels do not match across all three conditions")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    delta_path = OUTPUT / "strict276_c3_object_deltas.csv"
    summary_path = OUTPUT / "strict276_c3_paired_summary.csv"

    delta_fields = ["object_idx", "object", "contrast"] + [m for m, _ in METRICS]
    summaries: list[dict[str, object]] = []
    with delta_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=delta_fields)
        writer.writeheader()
        for left, right in PAIRS:
            deltas: dict[str, np.ndarray] = {}
            for metric, _direction in METRICS:
                deltas[metric] = np.asarray(
                    [float(rows[left][i][metric]) - float(rows[right][i][metric]) for i in ids],
                    dtype=np.float64,
                )
            for row_idx, object_idx in enumerate(ids):
                writer.writerow(
                    {
                        "object_idx": object_idx,
                        "object": objects[left][row_idx],
                        "contrast": f"{left}-{right}",
                        **{metric: f"{values[row_idx]:.12g}" for metric, values in deltas.items()},
                    }
                )
            for metric, direction in METRICS:
                delta = deltas[metric]
                low, high = bootstrap_ci(delta, BOOT_SEED)
                favorable = delta > 0 if direction == "higher" else delta < 0
                summaries.append(
                    {
                        "left": left,
                        "right": right,
                        "contrast": f"{left}-{right}",
                        "metric": metric,
                        "direction": direction,
                        "mean_delta_left_minus_right": float(delta.mean()),
                        "ci95_low": low,
                        "ci95_high": high,
                        "favorable_objects": int(favorable.sum()),
                        "unfavorable_objects": int((~favorable & (delta != 0)).sum()),
                        "ties": int((delta == 0).sum()),
                        "n": len(delta),
                        "bootstrap_resamples": N_BOOT,
                        "bootstrap_seed": BOOT_SEED,
                        "multiplicity_adjustment": "none; nominal supplemental intervals",
                    }
                )

    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    print(f"Wrote {summary_path.relative_to(ROOT)} ({len(summaries)} rows)")
    print(f"Wrote {delta_path.relative_to(ROOT)} (552 object-contrast rows)")
    for row in summaries:
        if row["metric"] in {"fg_psnr", "edge_ssim", "full_psnr", "full_ssim"}:
            print(
                f"{row['contrast']} {row['metric']}: "
                f"{row['mean_delta_left_minus_right']:+.6f} "
                f"[{row['ci95_low']:+.6f}, {row['ci95_high']:+.6f}], "
                f"favorable {row['favorable_objects']}/{row['n']}"
            )


if __name__ == "__main__":
    main()
