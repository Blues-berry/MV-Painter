#!/usr/bin/env python3
"""Recompute the retrospective Core-7 C3-versus-GFH PSNR contrasts."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCES = {
    "C3": ROOT / "global_c3_per_object_metrics.csv",
    "GFH": ROOT / "global_fixed_high_per_object_metrics.csv",
}
EXPECTED_SHA256 = {
    "C3": "171e7749edcdfd3ab6fa4b6afc0f27674abdfd7e4987a998e867501e200a12f6",
    "GFH": "cc3f07b8cfa1348ae133c02b2b84dd37006e0dc4ef4f76b775a1fbf116dd029a",
}
OUTPUT = ROOT / "CORE7_C3_GFH_RECALCULATED.csv"
OBJECT_COUNT = 276
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_930
METRICS = ("full_psnr", "fg_psnr")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_condition(name: str, path: Path) -> dict[int, dict[str, str]]:
    actual_hash = sha256(path)
    if actual_hash != EXPECTED_SHA256[name]:
        raise SystemExit(f"{name} source hash mismatch: {actual_hash}")

    indexed: dict[int, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            index = int(row["object_idx"])
            if index in indexed:
                raise SystemExit(f"duplicate {name} object_idx={index}")
            indexed[index] = row

    if set(indexed) != set(range(OBJECT_COUNT)):
        raise SystemExit(f"{name} does not contain exact object_idx 0..275")
    return indexed


def main() -> None:
    rows = {name: read_condition(name, path) for name, path in SOURCES.items()}
    indices = np.arange(OBJECT_COUNT)
    for index in indices:
        if rows["C3"][int(index)]["object"] != rows["GFH"][int(index)]["object"]:
            raise SystemExit(f"object identity mismatch at object_idx={index}")

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_indices = rng.integers(
        0, OBJECT_COUNT, size=(BOOTSTRAP_RESAMPLES, OBJECT_COUNT)
    )
    output_rows = []
    for metric in METRICS:
        differences = np.array(
            [float(rows["C3"][int(i)][metric]) - float(rows["GFH"][int(i)][metric])
             for i in indices],
            dtype=np.float64,
        )
        if not np.isfinite(differences).all():
            raise SystemExit(f"non-finite values in {metric}")
        bootstrap_means = differences[bootstrap_indices].mean(axis=1)
        low, high = np.percentile(bootstrap_means, [2.5, 97.5])
        output_rows.append(
            {
                "contrast": "C3-GFH",
                "metric": metric,
                "mean_difference": format(float(differences.mean()), ".15g"),
                "median_difference": format(float(np.median(differences)), ".15g"),
                "ci95_low": format(float(low), ".15g"),
                "ci95_high": format(float(high), ".15g"),
                "c3_favorable_objects": int(np.count_nonzero(differences > 0)),
                "gfh_favorable_objects": int(np.count_nonzero(differences < 0)),
                "ties": int(np.count_nonzero(differences == 0)),
                "n_objects": OBJECT_COUNT,
                "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "bootstrap_seed": BOOTSTRAP_SEED,
                "inference": "post-hoc descriptive; pointwise percentile CI",
                "c3_source_sha256": EXPECTED_SHA256["C3"],
                "gfh_source_sha256": EXPECTED_SHA256["GFH"],
            }
        )

    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {OUTPUT.name} from {OBJECT_COUNT} object-paired rows.")


if __name__ == "__main__":
    main()
