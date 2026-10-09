#!/usr/bin/env python3
"""Recompute the registered Fresh C primary estimate from paired object deltas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_N = 300
EXPECTED_MEAN = 0.5223522384961446
EXPECTED_CI = (0.404160, 0.640669)
BOOTSTRAP_SEED = 20261006
BOOTSTRAP_DRAWS = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    default = Path(__file__).parents[1] / "fresh_c/fresh_c_c3_minus_gfl_object_deltas.csv"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=default)
    args = parser.parse_args()

    with args.csv_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    uids = [row["object_uid"] for row in rows]
    delta = np.asarray([float(row["fg_psnr"]) for row in rows], dtype=np.float64)
    if len(rows) != EXPECTED_N or len(set(uids)) != EXPECTED_N:
        raise SystemExit(f"expected {EXPECTED_N} unique paired object rows; found {len(rows)}")
    if not np.isfinite(delta).all():
        raise SystemExit("non-finite FG-PSNR delta found")

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    means = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for start in range(0, BOOTSTRAP_DRAWS, 500):
        stop = min(start + 500, BOOTSTRAP_DRAWS)
        indices = rng.integers(0, len(delta), size=(stop - start, len(delta)))
        means[start:stop] = delta[indices].mean(axis=1)
    ci = np.quantile(means, [0.025, 0.975], method="linear")
    result = {
        "n_objects": len(delta),
        "contrast": "C3 - GFL",
        "primary_endpoint": "FG-PSNR (dB)",
        "mean_delta_db": float(delta.mean()),
        "median_delta_db": float(np.median(delta)),
        "percentile_bootstrap_95_ci_db": [float(ci[0]), float(ci[1])],
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "positive_fraction": float(np.mean(delta > 0)),
        "csv_sha256": sha256(args.csv_path),
    }
    if abs(result["mean_delta_db"] - EXPECTED_MEAN) > 1e-12:
        raise SystemExit("mean differs from the frozen manuscript value")
    if any(abs(float(actual) - target) > 1e-6 for actual, target in zip(ci, EXPECTED_CI)):
        raise SystemExit("bootstrap interval differs from the frozen manuscript value")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
