"""Prepare paired stage-placement comparisons and a pending-result report."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from round2_stats import paired_csv_summary


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
STAGE = ROOT / "final/round2/stage_placement_276"
OUT = ROOT / "final/round2"
METRICS = ("full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim")
DIRECTION = {m: m not in {"full_lpips", "fg_lpips"} for m in METRICS}


def read(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as f:
        return {r["object"]: r for r in csv.DictReader(f)}


def main() -> None:
    objects = [f"obj_{i:04d}" for i in range(24, 300)]
    c3 = read(BASE / "per_object_c3.csv")
    result = {
        "protocol": "clean-v2-stage-placement-followup-v1",
        "n": 276,
        "bootstrap": {"seed": 20260928, "resamples": 10000, "unit": "object-level paired bootstrap", "ci": 0.95},
        "comparisons": {},
    }
    for baseline in ("fixed_low", "fixed_high"):
        base = read(BASE / f"per_object_{baseline}.csv")
        result["comparisons"][f"c3_vs_{baseline}"] = {"status": "complete", **paired_csv_summary(c3, base, metrics=METRICS, object_ids=objects, higher_is_better=DIRECTION, seed=20260928, n_resamples=10000)}
    for baseline in ("fixed_mean", "hll", "llh"):
        path = STAGE / f"per_object_{baseline}.csv"
        if not path.exists():
            result["comparisons"][f"c3_vs_{baseline}"] = {"status": "pending_formal_cuda_inference", "required_file": str(path)}
        else:
            base = read(path)
            stage_c3 = read(STAGE / "per_object_c3_lhl.csv")
            result["comparisons"][f"c3_vs_{baseline}"] = {"status": "complete", **paired_csv_summary(stage_c3, base, metrics=METRICS, object_ids=objects, higher_is_better=DIRECTION, seed=20260928, n_resamples=10000)}
    (OUT / "paired_stage_comparisons.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Stage-placement results", "", "Status: the protocol and CPU dry-run passed; formal fixed-mean/HLL/LLH inference is pending a CUDA resource handoff. This is a prespecified follow-up after clean-v2 inspection, not a blind experiment.", "", "## Existing comparisons on frozen strict holdout", "", "C3 versus fixed-low and fixed-high are complete with 10,000 object-level paired bootstrap resamples. The machine-readable CIs and win rates are in `paired_stage_comparisons.json`.", "", "- C3 vs fixed-low: C3 is lower on Full PSNR and FG PSNR/FG SSIM in the current clean-v2 table, while it has a small Full-SSIM advantage and similar/better FG-LPIPS.", "- C3 vs fixed-high: C3 is higher on Full PSNR, FG PSNR and FG SSIM, with essentially tied full/foreground perceptual scores.", "", "## Mechanistic conclusion status", "", "No stage-position conclusion is made until fixed-mean, HLL and LLH are run with the same frozen checkpoint, unique6 cameras, 256×256 targets, seed 42 and 50 steps. The final analysis will compare global, foreground, edge and reference-based texture metrics and will report both paired CIs and win rates."]
    (OUT / "STAGE_PLACEMENT_RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: v["status"] for k, v in result["comparisons"].items()}, indent=2))


if __name__ == "__main__":
    main()
