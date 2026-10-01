"""Smoke analysis for the layer-wise MV-Adapter runs (technical checks only).

Checks, for 3 objects x {L-FIX, L-LHL, L-LLH}:
  1. all rows present and all metrics finite (no NaN/inf);
  2. per-method outputs differ for the same object (PNG SHA pairwise distinct);
  3. cond_encoder norm ratios equal the frozen per-point multipliers;
  4. each object generated all 6 views (grid width = 6 x 512).

Emits layerwise_smoke_result.json and MVADAPTER_LAYERWISE_SMOKE.md.
No quality judgment is made; no parameter may be tuned from this output.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from PIL import Image

METRIC_FIELDS = [
    "psnr", "fg_ssim", "edge_ssim", "fg_lpips", "ciede2000",
    "gt_relative_texture_error",
]
CONDITIONS = ["L-FIX", "L-LHL", "L-LLH"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-dir", type=Path,
                        default=Path("final/round2/mv_adapter/results/layerwise_smoke_3"))
    parser.add_argument("--objects", nargs="+", required=True)
    args = parser.parse_args()

    smoke_dir = args.smoke_dir
    with (smoke_dir / "per_object_metrics.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    expected = {(obj, cond) for obj in args.objects for cond in CONDITIONS}
    present = {(row["object"], row["schedule"]) for row in rows}
    all_rows_present = expected <= present

    finite_by_row = {}
    for row in rows:
        values = [float(row[f]) for f in METRIC_FIELDS]
        finite_by_row[(row["object"], row["schedule"])] = all(
            v == v and abs(v) != float("inf") for v in values
        )
    all_finite = bool(finite_by_row) and all(finite_by_row[k] for k in expected)

    pairwise_distinct = {}
    for obj in args.objects:
        shas = {
            cond: sha256_file(smoke_dir / "images" / cond / f"{obj}.png")
            for cond in CONDITIONS
        }
        pairwise_distinct[obj] = {
            f"{a}_vs_{b}": shas[a] != shas[b]
            for a, b in itertools.combinations(CONDITIONS, 2)
        }
    all_distinct = all(all(v.values()) for v in pairwise_distinct.values())

    config = json.loads((smoke_dir / "run_config.json").read_text())
    diagnostics = config["cond_encoder_diagnostics"]
    multipliers = diagnostics["multipliers"]
    ratios = diagnostics["first_call_norm_ratios"]
    ratios_match = len(ratios) == len(multipliers) == 4 and all(
        abs(r - m) < 1e-4 * max(m, 1.0) for r, m in zip(ratios, multipliers)
    )

    grid_widths_ok = {}
    for obj in args.objects:
        for cond in CONDITIONS:
            arr = np.asarray(Image.open(smoke_dir / "images" / cond / f"{obj}.png"))
            grid_widths_ok[f"{obj}:{cond}"] = arr.shape[1] == 6 * arr.shape[0] == 6 * 512
    all_views = all(grid_widths_ok.values())

    checks = {
        "rows_present_9": all_rows_present,
        "all_metrics_finite": all_finite,
        "methods_pairwise_distinct": all_distinct,
        "norm_ratios_match_frozen_multipliers": ratios_match,
        "all_views_generated": all_views,
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"

    result = {
        "audit": "MVADAPTER_LAYERWISE_SMOKE",
        "verdict": verdict,
        "checks": checks,
        "frozen_multipliers": multipliers,
        "observed_norm_ratios": ratios,
        "pairwise_png_distinct": pairwise_distinct,
        "finite_by_row": {f"{k[0]}:{k[1]}": v for k, v in finite_by_row.items() if k in expected},
        "note": "technical smoke only; no quality judgment, no tuning permitted",
    }
    (smoke_dir / "layerwise_smoke_result.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# MV-Adapter Layer-wise Smoke (technical)",
        "",
        f"Objects: {chr(44).join(args.objects)}. Conditions: {chr(44).join(CONDITIONS)}.",
        "Seed 20260928, 50 steps, low 0.75, high 1.00, frozen layer profile.",
        "",
        f"**SMOKE = {verdict}**",
        "",
        "| check | result |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in checks.items()],
        "",
        f"- frozen multipliers: `{multipliers}`",
        f"- observed norm ratios: `{ratios}`",
        "",
        "No parameter may be changed based on this smoke; formal commands are frozen.",
    ]
    (smoke_dir / "MVADAPTER_LAYERWISE_SMOKE.md").write_text("\n".join(lines) + "\n")
    print(f"SMOKE = {verdict}")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
