"""Decompose the controlled PNG Full-SSIM trace with one GT at a time.

The controlled trace stores A/B/C prediction tensors and both the original
float GT and the PNG-reloaded GT.  This CPU-only audit evaluates every
prediction/GT combination without model inference, so prediction quantization,
GT serialization and arithmetic dtype are not confounded in one comparison.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "final/round2/main_adapter_clean_v2/float_png_trace_12_controlled_20260929"
TENSORS = TRACE / "tensors"
OBJECTS = (13, 15, 38, 48, 54, 66, 68, 78, 82, 83, 110, 111)
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
PREDICTIONS = ("A_fp16", "A_fp32", "B_fp16", "B_fp32", "C_fp32")
GROUND_TRUTHS = ("gt_float32", "gt_png_float32")

sys.path.insert(0, str(ROOT / "geotex"))
from audit_clean_v2_raw_metrics import compute_ssim  # noqa: E402


def load(name: str) -> torch.Tensor:
    return torch.load(TENSORS / name, map_location="cpu", weights_only=True)


def prediction_tensor(object_id: str, method: str, variant: str) -> torch.Tensor:
    if variant.startswith("A_"):
        value = load(f"{object_id}_{method}_A_float_eval.pt")
    elif variant.startswith("B_"):
        value = load(f"{object_id}_{method}_B_pre_encoder.pt")
    else:
        value = load(f"{object_id}_{method}_C_png_reload.pt")
    return value.to(torch.float16 if variant.endswith("fp16") else torch.float32)


def main() -> None:
    rows: list[dict[str, object]] = []
    for index in OBJECTS:
        object_id = f"obj_{index:04d}"
        gt_float = load(f"{object_id}_gt_float_eval.pt").to(torch.float32)
        gt_png = load(f"{object_id}_gt_png_reload.pt").to(torch.float32)
        for method in METHODS:
            a = load(f"{object_id}_{method}_A_float_eval.pt")
            b = load(f"{object_id}_{method}_B_pre_encoder.pt")
            ab_max = float((a.float() - b.float()).abs().max())
            if ab_max != 0.0:
                raise ValueError(f"A/B mismatch for {object_id}/{method}: {ab_max}")
            for prediction in PREDICTIONS:
                pred = prediction_tensor(object_id, method, prediction)
                for gt_name, gt in (("gt_float32", gt_float), ("gt_png_float32", gt_png)):
                    rows.append({
                        "object": object_id,
                        "method": method,
                        "prediction": prediction,
                        "ground_truth": gt_name,
                        "ssim": float(compute_ssim(pred, gt)),
                        "a_b_max_abs": ab_max,
                    })

    fields = list(rows[0])
    output_csv = TRACE / "FIXED_GT_SSIM_DECOMPOSITION.csv"
    with output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    def values(prediction: str, gt: str, method: str) -> np.ndarray:
        return np.asarray([
            float(row["ssim"])
            for row in rows
            if row["prediction"] == prediction
            and row["ground_truth"] == gt
            and row["method"] == method
        ])

    def mean(prediction: str, gt: str, method: str) -> float:
        return float(values(prediction, gt, method).mean())

    def paired(prediction: str, gt: str, left: str, right: str) -> float:
        return float((values(prediction, gt, left) - values(prediction, gt, right)).mean())

    combinations = {
        f"{prediction}__{gt}": {
            method: mean(prediction, gt, method)
            for method in METHODS
        }
        for prediction in ("A_fp16", "A_fp32", "C_fp32")
        for gt in GROUND_TRUTHS
    }
    decomposition = {
        "dtype_A_fp16_minus_A_fp32_fixed_float_gt": float(
            np.mean([
                mean("A_fp16", "gt_float32", method)
                - mean("A_fp32", "gt_float32", method)
                for method in METHODS
            ])
        ),
        "prediction_png_quantization_C_minus_A_fixed_float_gt": float(
            np.mean([
                mean("C_fp32", "gt_float32", method)
                - mean("A_fp32", "gt_float32", method)
                for method in METHODS
            ])
        ),
        "gt_png_serialization_fixed_A_fp32": float(
            np.mean([
                mean("A_fp32", "gt_png_float32", method)
                - mean("A_fp32", "gt_float32", method)
                for method in METHODS
            ])
        ),
        "full_observed_C_png_prediction_and_gt": float(
            np.mean([
                mean("C_fp32", "gt_png_float32", method)
                - mean("A_fp32", "gt_float32", method)
                for method in METHODS
            ])
        ),
    }
    paired_differences = {
        f"{prediction}__{gt}": {
            "c3_minus_fixed_low": paired(prediction, gt, "c3", "fixed_low"),
            "c3_minus_fixed_high": paired(prediction, gt, "c3", "fixed_high"),
        }
        for prediction in ("A_fp16", "A_fp32", "C_fp32")
        for gt in GROUND_TRUTHS
    }
    summary = {
        "status": "complete",
        "objects": len(OBJECTS),
        "methods": list(METHODS),
        "prediction_variants": list(PREDICTIONS),
        "ground_truth_variants": list(GROUND_TRUTHS),
        "same_generation": True,
        "a_b_max_abs": max(float(row["a_b_max_abs"]) for row in rows),
        "combinations_mean_ssim": combinations,
        "decomposition_mean_effects": decomposition,
        "paired_c3_differences": paired_differences,
        "source_trace": str((TRACE / "float_png_serialization_manifest.json").resolve()),
        "source_csv": str(output_csv.resolve()),
        "no_model_inference": True,
    }
    (TRACE / "FIXED_GT_SSIM_DECOMPOSITION.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# Fixed-GT Full-SSIM decomposition",
        "",
        "CPU-only decomposition of the saved 12-object controlled trace; no model inference was run.",
        "",
        f"- Objects: {len(OBJECTS)}; methods: {', '.join(METHODS)}; rows: {len(rows)}.",
        f"- A/B maximum absolute difference: `{summary['a_b_max_abs']:.8g}`.",
        "- `A_fp16`/`A_fp32` are the same saved pre-serialization prediction evaluated at two arithmetic dtypes.",
        "- `C_fp32` is the saved PNG-reloaded prediction; `gt_float32` is the saved original GT tensor and `gt_png_float32` is the saved PNG-reloaded GT.",
        "",
        "## Mean decomposition effects",
        "",
        "| isolated effect | mean SSIM change |",
        "|---|---:|",
        f"| A fp16 → fp32, fixed original GT | {decomposition['dtype_A_fp16_minus_A_fp32_fixed_float_gt']:+.8f} |",
        f"| A fp32 → C fp32, fixed original GT (prediction PNG quantization) | {decomposition['prediction_png_quantization_C_minus_A_fixed_float_gt']:+.8f} |",
        f"| original GT → PNG GT, fixed A fp32 (GT serialization) | {decomposition['gt_png_serialization_fixed_A_fp32']:+.8f} |",
        f"| A/original GT → C/PNG GT (observed combined path) | {decomposition['full_observed_C_png_prediction_and_gt']:+.8f} |",
        "",
        "The paired C3-minus-baseline values are provided in the JSON for each fixed-GT/prediction branch. The 12-object trace is diagnostic evidence for the serialization boundary; it is not a replacement for the 276-object stage-placement result.",
        "",
        f"Machine-readable outputs: `{output_csv.name}` and `FIXED_GT_SSIM_DECOMPOSITION.json`.",
    ]
    (TRACE / "FIXED_GT_SSIM_DECOMPOSITION.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
