#!/usr/bin/env python3
"""Recompute the post-hoc Core-7 C3-minus-GFL FG-PSNR contrast."""
from __future__ import annotations
import csv, hashlib
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCES = {"C3": ROOT / "global_c3_per_object_metrics.csv", "GFL": ROOT / "global_fixed_low_per_object_metrics.csv"}
EXPECTED = {"C3": "171e7749edcdfd3ab6fa4b6afc0f27674abdfd7e4987a998e867501e200a12f6", "GFL": "7a8be06cd4f3ea3f102d1fcd0199404fb3e4dd7c4739a26c8e73c0abdf9f5624"}
OUT = ROOT / "CORE7_C3_GFL_RECALCULATED.csv"
N, RESAMPLES, SEED = 276, 10_000, 20260930

def load(name: str) -> dict[int, dict[str, str]]:
    path = SOURCES[name]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED[name]:
        raise SystemExit(f"{name} SHA mismatch: {digest}")
    with path.open(newline="", encoding="utf-8") as f:
        rows = {int(r["object_idx"]): r for r in csv.DictReader(f)}
    if set(rows) != set(range(N)):
        raise SystemExit(f"{name} is not the exact 0..275 cohort")
    return rows

def main() -> None:
    c3, gfl = load("C3"), load("GFL")
    for i in range(N):
        if c3[i]["object"] != gfl[i]["object"]:
            raise SystemExit(f"object mismatch at index {i}")
    d = np.asarray([float(c3[i]["fg_psnr"]) - float(gfl[i]["fg_psnr"]) for i in range(N)], dtype=np.float64)
    if not np.isfinite(d).all():
        raise SystemExit("non-finite paired value")
    rng = np.random.default_rng(SEED)
    samples = d[rng.integers(0, N, size=(RESAMPLES, N))].mean(axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    row = {"contrast":"C3-GFL", "metric":"fg_psnr", "mean_difference":format(float(d.mean()),".15g"), "median_difference":format(float(np.median(d)),".15g"), "ci95_low":format(float(low),".15g"), "ci95_high":format(float(high),".15g"), "c3_favorable_objects":int((d>0).sum()), "gfl_favorable_objects":int((d<0).sum()), "ties":int((d==0).sum()), "n_objects":N, "bootstrap_resamples":RESAMPLES, "bootstrap_seed":SEED, "inference":"post-hoc descriptive; pointwise percentile CI", "c3_source_sha256":EXPECTED["C3"], "gfl_source_sha256":EXPECTED["GFL"]}
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row), lineterminator="\n")
        writer.writeheader(); writer.writerow(row)
    print(f"PASS: wrote {OUT.name}: mean={d.mean():.9f}, CI=[{low:.9f}, {high:.9f}], wins={(d>0).sum()}/{N}")

if __name__ == "__main__":
    main()
