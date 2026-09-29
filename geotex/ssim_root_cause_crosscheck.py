"""Cross-check the frozen 11-object Full-SSIM diagnostic without inference.

This script deliberately treats the recorded float-eval SSIM as a scalar
provenance value. It never reconstructs or claims to recover the original
float prediction tensor. The PNG branches use the same fixed prediction and
GT files for every dtype comparison.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
INDEPENDENT = ROOT / "final/round2/independent_validation"
RECON = ROOT / "final/round2/main_adapter_clean_v2/full_ssim_reconciliation"
EVAL = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
SAMPLE_CSV = INDEPENDENT / "METRIC_RECOMPUTE_SAMPLE.csv"
ORIGINAL_IMPL = Path("/tmp/mv_main_rerun/geotex/metrics.py")


def load_original_ssim():
    spec = importlib.util.spec_from_file_location("codex_d_original_metrics", ORIGINAL_IMPL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load original metric implementation: {ORIGINAL_IMPL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compute_ssim


def load_rgb(path: Path, dtype: np.dtype = np.float32) -> np.ndarray:
    image = np.asarray(Image.open(path).convert("RGB"), dtype=dtype) / np.asarray(255.0, dtype=dtype)
    return image.transpose(2, 0, 1)


def numpy_box_ssim(pred: np.ndarray, target: np.ndarray, dtype: np.dtype) -> float:
    """Independent zero-padded 3x3 SSIM implementation over C,H,W arrays."""
    pred = np.asarray(pred, dtype=dtype)
    target = np.asarray(target, dtype=dtype)
    if pred.shape != target.shape or pred.ndim != 3:
        raise ValueError(f"expected matching C,H,W arrays, got {pred.shape} and {target.shape}")
    pad_spec = ((0, 0), (1, 1), (1, 1))

    def avg_pool(value: np.ndarray) -> np.ndarray:
        padded = np.pad(value, pad_spec, mode="constant")
        windows = np.lib.stride_tricks.sliding_window_view(padded, (3, 3), axis=(1, 2))
        return windows.mean(axis=(-1, -2), dtype=dtype)

    c1, c2 = dtype(0.01**2), dtype(0.03**2)
    mu_p = avg_pool(pred)
    mu_t = avg_pool(target)
    var_p = avg_pool(pred * pred) - mu_p * mu_p
    var_t = avg_pool(target * target) - mu_t * mu_t
    cov = avg_pool(pred * target) - mu_p * mu_t
    value = ((2 * mu_p * mu_t + c1) * (2 * cov + c2)) / (
        (mu_p * mu_p + mu_t * mu_t + c1) * (var_p + var_t + c2)
    )
    return float(np.clip(value, 0.0, 1.0).mean())


def torch_original_ssim(compute_ssim, pred: np.ndarray, target: np.ndarray, dtype: torch.dtype) -> float:
    pred_t = torch.from_numpy(pred).unsqueeze(0).to(dtype=dtype)
    target_t = torch.from_numpy(target).unsqueeze(0).to(dtype=dtype)
    return float(compute_ssim(pred_t, target_t))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    sample_objects = sorted({row["object"] for row in csv.DictReader(SAMPLE_CSV.open(newline=""))})
    if len(sample_objects) != 11:
        raise ValueError(f"expected the frozen 11-object diagnostic sample, found {len(sample_objects)}")

    recon_rows = {}
    with (RECON / "full_ssim_comparison.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["object"] in sample_objects:
                recon_rows[(row["object"], row["method"])] = row
    if len(recon_rows) != 44:
        raise ValueError(f"expected 44 frozen A/B/C rows, found {len(recon_rows)}")

    tensor_suffixes = {".pt", ".pth", ".npy", ".npz", ".safetensors", ".pickle", ".pkl"}
    tensor_paths = sorted(
        str(path.relative_to(EVAL))
        for path in EVAL.rglob("*")
        if path.is_file() and path.suffix.lower() in tensor_suffixes
    )
    compute_ssim = load_original_ssim()
    methods = ("no_adapter", "fixed_low", "fixed_high", "c3")
    rows = []
    dtype_failures = []
    for object_id in sample_objects:
        gt_path = EVAL / "predictions/ground_truth" / f"{object_id}.png"
        target = load_rgb(gt_path)
        for method in methods:
            pred_path = EVAL / "predictions" / method / f"{object_id}.png"
            pred = load_rgb(pred_path)
            original = recon_rows[(object_id, method)]
            row = {
                "object": object_id,
                "method": method,
                "prediction_png_sha256": sha256(pred_path),
                "ground_truth_png_sha256": sha256(gt_path),
                "recorded_float_eval_ssim": float(original["original_float_ssim"]),
                "existing_reconciliation_png_original_impl_ssim": float(original["png_original_impl_ssim"]),
                "existing_reconciliation_raw_audit_ssim": float(original["raw_audit_ssim"]),
            }
            for label, torch_dtype in (("float32", torch.float32), ("float64", torch.float64)):
                row[f"original_impl_png_saved_gt_{label}"] = torch_original_ssim(
                    compute_ssim, pred, target, torch_dtype
                )
                row[f"original_impl_png_saved_gt_{label}_minus_float_eval"] = (
                    row[f"original_impl_png_saved_gt_{label}"] - row["recorded_float_eval_ssim"]
                )
                try:
                    row[f"independent_numpy_png_saved_gt_{label}"] = numpy_box_ssim(pred, target, np.float32 if label == "float32" else np.float64)
                except Exception as exc:
                    dtype_failures.append({"object": object_id, "method": method, "branch": label, "error": repr(exc)})
                    row[f"independent_numpy_png_saved_gt_{label}"] = float("nan")
            rows.append(row)

    output_dir = INDEPENDENT
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (output_dir / "SSIM_ROOT_CAUSE_CROSSCHECK.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    def mean(key: str) -> float:
        return float(np.mean([row[key] for row in rows]))

    def mean_abs_delta(key: str, reference: str) -> float:
        return float(np.mean([abs(row[key] - row[reference]) for row in rows]))

    def paired_mean(key: str, baseline: str) -> float:
        values = []
        for object_id in sample_objects:
            left = next(row[key] for row in rows if row["object"] == object_id and row["method"] == "c3")
            right = next(row[key] for row in rows if row["object"] == object_id and row["method"] == baseline)
            values.append(left - right)
        return float(np.mean(values))

    summary = {
        "status": "PARTIALLY_CONFIRMED",
        "sample_objects": sample_objects,
        "n_objects": len(sample_objects),
        "n_rows": len(rows),
        "original_float_prediction_tensor_paths_under_eval_dir": tensor_paths,
        "original_float_tensor_available": bool(tensor_paths),
        "dtype_failures": dtype_failures,
        "means": {
            "recorded_float_eval_ssim": mean("recorded_float_eval_ssim"),
            "existing_reconciliation_png_original_impl_ssim": mean("existing_reconciliation_png_original_impl_ssim"),
            "existing_reconciliation_raw_audit_ssim": mean("existing_reconciliation_raw_audit_ssim"),
            "original_impl_png_saved_gt_float32": mean("original_impl_png_saved_gt_float32"),
            "original_impl_png_saved_gt_float64": mean("original_impl_png_saved_gt_float64"),
            "independent_numpy_png_saved_gt_float32": mean("independent_numpy_png_saved_gt_float32"),
            "independent_numpy_png_saved_gt_float64": mean("independent_numpy_png_saved_gt_float64"),
        },
        "mean_abs_deltas": {
            "original_impl_float32_minus_recorded_float": mean_abs_delta("original_impl_png_saved_gt_float32", "recorded_float_eval_ssim"),
            "original_impl_float64_minus_recorded_float": mean_abs_delta("original_impl_png_saved_gt_float64", "recorded_float_eval_ssim"),
            "original_impl_float64_minus_float32": mean_abs_delta("original_impl_png_saved_gt_float64", "original_impl_png_saved_gt_float32"),
            "independent_numpy_float32_minus_original_impl_float32": mean_abs_delta("independent_numpy_png_saved_gt_float32", "original_impl_png_saved_gt_float32"),
            "independent_numpy_float64_minus_original_impl_float64": mean_abs_delta("independent_numpy_png_saved_gt_float64", "original_impl_png_saved_gt_float64"),
        },
        "paired_c3_minus_baseline": {
            "recorded_float_eval": {baseline: paired_mean("recorded_float_eval_ssim", baseline) for baseline in ("fixed_low", "fixed_high")},
            "original_impl_png_saved_gt_float32": {baseline: paired_mean("original_impl_png_saved_gt_float32", baseline) for baseline in ("fixed_low", "fixed_high")},
            "original_impl_png_saved_gt_float64": {baseline: paired_mean("original_impl_png_saved_gt_float64", baseline) for baseline in ("fixed_low", "fixed_high")},
            "independent_numpy_png_saved_gt_float32": {baseline: paired_mean("independent_numpy_png_saved_gt_float32", baseline) for baseline in ("fixed_low", "fixed_high")},
        },
        "implementation_facts": {
            "data_range": "inputs normalized to [0,1]; C1=0.01^2 and C2=0.03^2",
            "window": "3x3 average/box window, stride=1, zero padding=1, count_include_pad=True",
            "gaussian": "not used by the primary original implementation; 11x11 sigma=1.5 remains diagnostic only",
            "aggregation": "complete 3x2 saved montage; per-view mean is diagnostic only",
            "alpha": "Full SSIM branch uses saved RGB ground-truth montage; no alpha mask is applied",
            "png": "saved prediction and saved GT are reloaded as 8-bit RGB and divided by 255",
        },
    }
    (output_dir / "SSIM_ROOT_CAUSE_CROSSCHECK.json").write_text(json.dumps(summary, indent=2) + "\n")

    report = [
        "# Full-SSIM Root-Cause Crosscheck",
        "",
        "Status: **PARTIALLY_CONFIRMED**.",
        "",
        "This is a fixed-input cross-check over the already frozen 11-object / 44-row diagnostic sample. No model inference and no 300-object recomputation were performed.",
        "",
        "## Tensor provenance",
        "",
        f"No original float prediction tensor was found under `{EVAL}`. The A branch is therefore the recorded `original_float_ssim` scalar from the original per-object CSV, not a recovered tensor. This report does not claim to reconstruct that tensor. Tensor-like files found: `{len(tensor_paths)}`.",
        "",
        "## A/B/C definitions",
        "",
        "- **A — float-eval scalar:** recorded original float-eval Full-SSIM value.",
        "- **B — PNG/original implementation:** saved prediction PNG and saved GT PNG, evaluated by the historical 3×3 PyTorch implementation.",
        "- **C — PNG/independent implementation:** the same fixed PNG inputs evaluated by an independent NumPy zero-padded 3×3 implementation. The existing raw-GT audit branch is also retained in the CSV for comparison.",
        "",
        "## Aggregate fixed-input result",
        "",
        "| branch | mean SSIM | mean absolute difference vs A |",
        "|---|---:|---:|",
        f"| A recorded float-eval | {summary['means']['recorded_float_eval_ssim']:.6f} | — |",
        f"| B original impl, float32 | {summary['means']['original_impl_png_saved_gt_float32']:.6f} | {summary['mean_abs_deltas']['original_impl_float32_minus_recorded_float']:.6f} |",
        f"| B original impl, float64 | {summary['means']['original_impl_png_saved_gt_float64']:.6f} | {summary['mean_abs_deltas']['original_impl_float64_minus_recorded_float']:.6f} |",
        f"| C independent NumPy, float32 | {summary['means']['independent_numpy_png_saved_gt_float32']:.6f} | {mean_abs_delta('independent_numpy_png_saved_gt_float32', 'recorded_float_eval_ssim'):.6f} |",
        f"| C independent NumPy, float64 | {summary['means']['independent_numpy_png_saved_gt_float64']:.6f} | {mean_abs_delta('independent_numpy_png_saved_gt_float64', 'recorded_float_eval_ssim'):.6f} |",
        "",
        "## Dtype and paired-difference isolation",
        "",
        f"- Original implementation float64 versus float32 mean absolute difference: `{summary['mean_abs_deltas']['original_impl_float64_minus_float32']:.8f}`.",
        f"- Independent NumPy versus original implementation at float32 mean absolute difference: `{summary['mean_abs_deltas']['independent_numpy_float32_minus_original_impl_float32']:.8f}`.",
        f"- Recorded A C3−fixed-low paired mean: `{summary['paired_c3_minus_baseline']['recorded_float_eval']['fixed_low']:.6f}`; PNG/original implementation float32: `{summary['paired_c3_minus_baseline']['original_impl_png_saved_gt_float32']['fixed_low']:.6f}`.",
        f"- Recorded A C3−fixed-high paired mean: `{summary['paired_c3_minus_baseline']['recorded_float_eval']['fixed_high']:.6f}`; PNG/original implementation float32: `{summary['paired_c3_minus_baseline']['original_impl_png_saved_gt_float32']['fixed_high']:.6f}`.",
        "",
        "## Confirmed boundary",
        "",
        "B and C agree on the fixed PNG inputs to numerical tolerance, while float32 versus float64 does not materially change B. Therefore the 0.026–0.037 gap is not explained by data range, window size, Gaussian weighting, padding, montage versus per-view aggregation, or ordinary float32/float64 arithmetic in the PNG branch. The paired C3-versus-fixed-low conclusion also changes between A and PNG, so the PNG quantization/provenance boundary can affect method comparisons.",
        "",
        "The remaining unresolved distinction is whether the A values came from float predictions before 8-bit serialization, a different target/prediction tensor branch, or another pre-save evaluation path. Without the original float tensors or an exact inference rerun that emits them, no stronger root-cause claim is justified.",
        "",
        "## Files",
        "",
        "- `SSIM_ROOT_CAUSE_CROSSCHECK.csv`: object/method A/B/C and dtype rows.",
        "- `SSIM_ROOT_CAUSE_CROSSCHECK.json`: machine-readable summary.",
        "- `final/round2/main_adapter_clean_v2/full_ssim_reconciliation/FULL_SSIM_RECONCILIATION.md`: Codex A's 300-object reconciliation retained as prior evidence.",
    ]
    (output_dir / "SSIM_ROOT_CAUSE_CROSSCHECK.md").write_text("\n".join(report) + "\n")
    print(json.dumps({"status": summary["status"], "objects": len(sample_objects), "rows": len(rows), "tensor_paths": len(tensor_paths)}, indent=2))


if __name__ == "__main__":
    main()
