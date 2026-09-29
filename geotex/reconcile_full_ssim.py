"""Reconcile original float-eval SSIM with PNG and raw-RGBA rechecks.

This script never regenerates model outputs.  It uses the frozen PNGs and the
recorded per-object float-eval CSVs, so the A/B/C provenance is explicit:

 A: recorded original float-eval Full-SSIM;
 B: original consolidated SSIM implementation on reloaded PNG panels;
 C: current raw-audit SSIM implementation on reloaded prediction PNGs and
    independently reconstructed RGBA/white-background GT panels.

The fixed 12-object subset is the frozen Exact-GLB cohort.  The default run
also evaluates all 300 objects and writes paired summaries and a markdown
report; no correction or fitted offset is applied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from einops import rearrange


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
DATA_ROOT = ROOT / "data/train_data/rendered_full"
OUT_DIR = ROOT / "final/round2/main_adapter_clean_v2/full_ssim_reconciliation"
METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
FIXED12 = (13, 15, 38, 48, 54, 66, 68, 78, 82, 83, 110, 111)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RAW_AUDIT = load_module("clean_v2_raw_audit_for_reconciliation", ROOT / "geotex/audit_clean_v2_raw_metrics.py")
ORIGINAL_METRICS = load_module(
    "original_consolidated_image_metrics_for_reconciliation",
    Path("/tmp/mv_main_rerun/geotex/metrics/image_metrics.py"),
)
png_ssim = ORIGINAL_METRICS.compute_ssim
raw_ssim = RAW_AUDIT.compute_ssim


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def panel_views(panel: torch.Tensor) -> torch.Tensor:
    return rearrange(panel, "c (x h) (y w) -> (x y) c h w", x=3, y=2)


def per_view_mean(fn, prediction: torch.Tensor, target: torch.Tensor) -> float:
    values = [fn(prediction[i : i + 1], target[i : i + 1]) for i in range(prediction.shape[0])]
    return float(np.mean(values))


def gaussian_ssim(pred: torch.Tensor, target: torch.Tensor, window: int = 11, sigma: float = 1.5) -> float:
    """Diagnostic Gaussian SSIM, not used as a replacement metric.

    This is included to document that a Gaussian window is not the source of
    the historical number.  It uses reflect padding, data range 1, and the
    standard C1/C2 constants for L=1.
    """
    coords = torch.arange(window, dtype=pred.dtype, device=pred.device) - (window - 1) / 2
    kernel_1d = torch.exp(-(coords**2) / (2 * sigma**2))
    kernel_1d = kernel_1d / kernel_1d.sum()
    kernel = kernel_1d[:, None] * kernel_1d[None, :]
    channels = pred.shape[1]
    weight = kernel.expand(channels, 1, window, window)
    pad = window // 2

    def blur(value: torch.Tensor) -> torch.Tensor:
        return F.conv2d(F.pad(value, (pad, pad, pad, pad), mode="reflect"), weight, groups=channels)

    c1, c2 = 0.01**2, 0.03**2
    mu1, mu2 = blur(pred), blur(target)
    sigma1 = blur(pred * pred) - mu1 * mu1
    sigma2 = blur(target * target) - mu2 * mu2
    sigma12 = blur(pred * target) - mu1 * mu2
    value = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / (
        (mu1 * mu1 + mu2 * mu2 + c1) * (sigma1 + sigma2 + c2)
    )
    return float(value.clamp(0, 1).mean().item())


def bootstrap_ci(values: np.ndarray, seed: int, n_resamples: int = 10_000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples, dtype=np.float64)
    for start in range(0, n_resamples, 500):
        count = min(500, n_resamples - start)
        sample = rng.integers(0, len(values), size=(count, len(values)))
        means[start : start + count] = values[sample].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def distribution(values: np.ndarray, threshold: float = 0.01) -> dict[str, object]:
    absolute = np.abs(values)
    return {
        "mean": float(values.mean()),
        "mean_abs": float(absolute.mean()),
        "p05": float(np.quantile(values, 0.05)),
        "p50": float(np.quantile(values, 0.50)),
        "p95": float(np.quantile(values, 0.95)),
        "max_abs": float(absolute.max()),
        "over_threshold": int((absolute > threshold).sum()),
        "threshold": threshold,
    }


def paired_summary(rows: list[dict[str, object]], left: str, right: str, representation: str) -> dict[str, object]:
    by_object: dict[str, dict[str, float]] = {}
    for row in rows:
        by_object.setdefault(str(row["object"]), {})[str(row["method"])] = float(row[representation])
    pairs = [(v[left], v[right]) for v in by_object.values() if left in v and right in v]
    deltas = np.asarray([a - b for a, b in pairs], dtype=np.float64)
    ci = bootstrap_ci(deltas, seed=20260928)
    return {
        "n": int(len(deltas)),
        "mean": float(deltas.mean()),
        "ci95": list(ci),
        "win_rate_left_higher": float((deltas > 0).mean()),
        "ties": int((deltas == 0).sum()),
        "representation": representation,
        "left": left,
        "right": right,
    }


def read_original(method: str) -> dict[str, dict[str, float]]:
    with (EVAL_DIR / f"per_object_{method}.csv").open(newline="") as handle:
        return {row["object"]: {"full_ssim": float(row["full_ssim"])} for row in csv.DictReader(handle)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--fixed12-only", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    uids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    if len(uids) != 300:
        raise ValueError(f"expected 300 UIDs, found {len(uids)}")
    selected = set(FIXED12) if args.fixed12_only else set(range(300))
    originals = {method: read_original(method) for method in METHODS}
    rows: list[dict[str, object]] = []

    for index, uid in enumerate(uids):
        if index not in selected:
            continue
        object_id = f"obj_{index:04d}"
        raw_target, _, _, reverse = RAW_AUDIT.panel_for_uid(DATA_ROOT, uid)
        png_target = RAW_AUDIT.load_panel(EVAL_DIR / "predictions/ground_truth" / f"{object_id}.png")
        raw_target_b = raw_target.unsqueeze(0)
        png_target_b = png_target.unsqueeze(0)
        for method in METHODS:
            png_pred = RAW_AUDIT.load_panel(EVAL_DIR / "predictions" / method / f"{object_id}.png")
            png_pred_b = png_pred.unsqueeze(0)
            png_views = panel_views(png_pred)
            png_gt_views = panel_views(png_target)
            raw_views = panel_views(png_pred)
            raw_gt_views = panel_views(raw_target)
            row = {
                "object": object_id,
                "object_idx": index,
                "uid": uid,
                "method": method,
                "fixed12": index in FIXED12,
                "reverse": reverse,
                "original_float_ssim": originals[method][object_id]["full_ssim"],
                "png_original_impl_ssim": float(png_ssim(png_pred_b, png_target_b)),
                "raw_audit_ssim": float(raw_ssim(png_pred_b, raw_target_b)),
                "png_original_impl_per_view_mean": per_view_mean(png_ssim, png_views, png_gt_views),
                "raw_audit_per_view_mean": per_view_mean(raw_ssim, raw_views, raw_gt_views),
                "png_gaussian11_sigma1p5_ssim": gaussian_ssim(png_pred_b, png_target_b),
                "raw_gaussian11_sigma1p5_ssim": gaussian_ssim(png_pred_b, raw_target_b),
            }
            row["delta_png_minus_original"] = row["png_original_impl_ssim"] - row["original_float_ssim"]
            row["delta_raw_minus_png"] = row["raw_audit_ssim"] - row["png_original_impl_ssim"]
            row["delta_raw_minus_original"] = row["raw_audit_ssim"] - row["original_float_ssim"]
            rows.append(row)
        if len(rows) % 48 == 0 or index == max(selected):
            print(f"processed {index + 1}/300", flush=True)

    fields = list(rows[0])
    with (args.output_dir / "full_ssim_comparison.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary: dict[str, object] = {
        "protocol": "clean-v2-full-ssim-reconciliation-v1",
        "provenance": {
            "A": "recorded original float-eval per-object CSV full_ssim",
            "B": "original consolidated metrics/image_metrics.py on reloaded saved PNG panels",
            "C": "current audit_clean_v2_raw_metrics.py SSIM on PNG predictions and raw RGBA/white GT",
            "no_compensation": True,
            "original_metrics_sha256": sha256(Path("/tmp/mv_main_rerun/geotex/metrics/image_metrics.py")),
            "raw_audit_script_sha256": sha256(ROOT / "geotex/audit_clean_v2_raw_metrics.py"),
        },
        "n_objects": len(selected),
        "fixed12_indices": list(FIXED12),
        "representations": {},
        "paired": {},
        "checks": {
            "window": "3x3 box average_pool2d, stride=1, padding=1, count_include_pad=True",
            "gaussian_diagnostic": "11x11 Gaussian sigma=1.5, reflect padding, not used for primary result",
            "constants": "C1=0.01^2, C2=0.03^2, data range implied as [0,1]",
            "clamp": "SSIM map clamp [0,1]",
            "montage": "3x2 panel 768x512 from six 256x256 views",
            "per_view": "mean of six per-view scores, reported as diagnostic only",
            "padding_crop": "no crop; same saved panel dimensions and no montage padding",
        },
    }
    for representation in ("original_float_ssim", "png_original_impl_ssim", "raw_audit_ssim"):
        summary["representations"][representation] = {}
        for method in METHODS:
            values = np.asarray([float(row[representation]) for row in rows if row["method"] == method])
            summary["representations"][representation][method] = {
                "n": int(len(values)),
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)),
                "min": float(values.min()),
                "max": float(values.max()),
            }
    for delta_name, threshold in (("delta_png_minus_original", 0.01), ("delta_raw_minus_png", 0.001), ("delta_raw_minus_original", 0.01)):
        summary["representations"][delta_name] = {}
        for method in METHODS:
            values = np.asarray([float(row[delta_name]) for row in rows if row["method"] == method])
            summary["representations"][delta_name][method] = distribution(values, threshold)
    for representation in ("original_float_ssim", "png_original_impl_ssim", "raw_audit_ssim"):
        summary["paired"][representation] = {
            "c3_vs_fixed_low": paired_summary(rows, "c3", "fixed_low", representation),
            "c3_vs_fixed_high": paired_summary(rows, "c3", "fixed_high", representation),
        }
    summary["subset_summaries"] = {}
    for subset_name, subset_rows in (("all300", rows), ("fixed12", [row for row in rows if row["fixed12"]])):
        subset = {"n_objects": len({row["object"] for row in subset_rows}), "representations": {}, "paired": {}}
        for representation in ("original_float_ssim", "png_original_impl_ssim", "raw_audit_ssim"):
            subset["representations"][representation] = {}
            for method in METHODS:
                values = np.asarray([float(row[representation]) for row in subset_rows if row["method"] == method])
                subset["representations"][representation][method] = {"mean": float(values.mean()), "std": float(values.std(ddof=1))}
            subset["paired"][representation] = {
                "c3_vs_fixed_low": paired_summary(subset_rows, "c3", "fixed_low", representation),
                "c3_vs_fixed_high": paired_summary(subset_rows, "c3", "fixed_high", representation),
            }
        summary["subset_summaries"][subset_name] = subset
    summary["paired_delta_change"] = {}
    for comparison in ("c3_vs_fixed_low", "c3_vs_fixed_high"):
        summary["paired_delta_change"][comparison] = {}
        for left, right in (("original_float_ssim", "png_original_impl_ssim"), ("png_original_impl_ssim", "raw_audit_ssim"), ("original_float_ssim", "raw_audit_ssim")):
            a = summary["paired"][left][comparison]
            b = summary["paired"][right][comparison]
            summary["paired_delta_change"][comparison][f"{right}_minus_{left}"] = {
                "mean_change": float(b["mean"] - a["mean"]),
                "ci95_change": [float(b["ci95"][0] - a["ci95"][1]), float(b["ci95"][1] - a["ci95"][0])],
            }

    (args.output_dir / "full_ssim_reconciliation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_report(args.output_dir / "FULL_SSIM_RECONCILIATION.md", summary)
    print(json.dumps(summary, indent=2))


def write_report(path: Path, summary: dict[str, object]) -> None:
    rep = summary["representations"]
    lines = [
        "# Full-SSIM reconciliation",
        "",
        "Status: completed from the frozen 300-object PNG/eval artifacts; no model inference or metric compensation was performed.",
        "",
        "## A/B/C definitions",
        "",
        "- A: recorded `original_float_ssim` from the original per-object float-eval CSV.",
        "- B: `png_original_impl_ssim`, reloaded PNG prediction and saved GT using the original consolidated 3x3 implementation.",
        "- C: `raw_audit_ssim`, reloaded PNG prediction against independently reconstructed raw RGBA/white-background GT using the current raw audit implementation.",
        "",
        "The CSV contains all per-object values, per-view diagnostics, Gaussian-window diagnostics, and A/B/C deltas.",
        "",
        "## Overall Full-SSIM values",
        "",
        "| representation | no adapter | fixed low | fixed high | C3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, label in (("original_float_ssim", "A original float"), ("png_original_impl_ssim", "B PNG/original impl"), ("raw_audit_ssim", "C PNG/raw GT audit")):
        lines.append("| " + label + " | " + " | ".join(f"{rep[name][m]['mean']:.6f}" for m in METHODS) + " |")
    lines += [
        "",
        "## Fixed 12-object reconciliation subset",
        "",
        "The fixed subset is the frozen Exact-GLB cohort at object indices `13,15,38,48,54,66,68,78,82,83,110,111`; it is a diagnostic subset and was not selected for SSIM performance.",
        "",
        "| representation | no adapter | fixed low | fixed high | C3 |",
        "|---|---:|---:|---:|---:|",
    ]
    fixed = summary["subset_summaries"]["fixed12"]["representations"]
    for name, label in (("original_float_ssim", "A original float"), ("png_original_impl_ssim", "B PNG/original impl"), ("raw_audit_ssim", "C PNG/raw GT audit")):
        lines.append("| " + label + " | " + " | ".join(f"{fixed[name][m]['mean']:.6f}" for m in METHODS) + " |")
    lines += [
        "",
        "| representation | comparison | mean C3-minus-baseline | 95% CI | win rate |",
        "|---|---|---:|---|---:|",
    ]
    for representation, label in (("original_float_ssim", "A"), ("png_original_impl_ssim", "B"), ("raw_audit_ssim", "C")):
        for comparison, value in summary["subset_summaries"]["fixed12"]["paired"][representation].items():
            lines.append(f"| {label} | {comparison} | {value['mean']:.6f} | [{value['ci95'][0]:.6f}, {value['ci95'][1]:.6f}] | {value['win_rate_left_higher']:.3f} |")
    lines += [
        "",
        "## A/B/C error distributions",
        "",
        "| delta | method | mean | mean abs | p05 | median | p95 | max abs | over threshold |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, label in (("delta_png_minus_original", "B-A"), ("delta_raw_minus_png", "C-B"), ("delta_raw_minus_original", "C-A")):
        for method in METHODS:
            value = rep[name][method]
            lines.append(f"| {label} | {method} | {value['mean']:.6f} | {value['mean_abs']:.6f} | {value['p05']:.6f} | {value['p50']:.6f} | {value['p95']:.6f} | {value['max_abs']:.6f} | {value['over_threshold']}/{summary['n_objects']} |")
    lines += [
        "",
        "## Paired C3 differences",
        "",
        "Positive values mean C3 has higher Full-SSIM. Bootstrap is object-level, 10,000 resamples, seed 20260928.",
        "",
        "| representation | comparison | mean C3-minus-baseline | 95% CI | win rate |",
        "|---|---|---:|---|---:|",
    ]
    for representation, label in (("original_float_ssim", "A"), ("png_original_impl_ssim", "B"), ("raw_audit_ssim", "C")):
        for comparison, value in summary["paired"][representation].items():
            lines.append(f"| {label} | {comparison} | {value['mean']:.6f} | [{value['ci95'][0]:.6f}, {value['ci95'][1]:.6f}] | {value['win_rate_left_higher']:.3f} |")
    lines += [
        "",
        "## Reconciliation conclusion",
        "",
        "B and C isolate the PNG/GT preprocessing branch from the SSIM implementation branch. The primary implementation uses a 3x3 box window, padding=1, no Gaussian weighting, C1=0.01^2, C2=0.03^2, [0,1] inputs, map clamp [0,1], and the complete 3x2 montage. Per-view means and an 11x11 Gaussian diagnostic are reported but are not substituted into the primary result.",
        "",
        "If B is close to C while A differs, the remaining discrepancy is between the recorded pre-save float tensors and the reloaded 8-bit PNG panels (including float precision/quantization), not a fitted correction. If B and C differ, the difference is confined to GT reconstruction/preprocessing and is retained as an audit finding.",
        "",
        "Full-SSIM should not be delivered to Codex C as a unified number until the chosen provenance is stated explicitly. No compensation value is applied.",
    ]
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
