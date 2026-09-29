"""Create pooled/probe/strict tables from the raw PNG metric recheck."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "final/round2/main_adapter_clean_v2/raw_metric_audit/raw_metric_recheck_300.csv"
OUT = ROOT / "final/round2/main_adapter_clean_v2"
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
METRICS = ("full_psnr", "fg_psnr", "full_ssim", "fg_ssim", "full_lpips", "fg_lpips", "edge_ssim")


def main() -> None:
    with AUDIT.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for split, lo, hi in (("probe24", 0, 24), ("strict276", 24, 300), ("pooled300", 0, 300)):
        out = []
        for method in METHODS:
            method_rows = [r for r in rows if r["object"] in {f"obj_{i:04d}" for i in range(lo, hi)} and r["object"] and r["reverse"] is not None]
            # The audit row does not carry a method column; rows are in method blocks
            method_rows = [r for i, r in enumerate(rows) if i % 4 == METHODS.index(method) and lo <= i // 4 < hi]
            out.append({"condition": method, "n": hi - lo, **{m: float(np.mean([float(r[m]) for r in method_rows])) for m in METRICS}})
        with (OUT / f"raw_metric_recheck_{split}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(out[0]))
            writer.writeheader()
            writer.writerows(out)
    print("wrote raw split tables")


if __name__ == "__main__":
    main()
