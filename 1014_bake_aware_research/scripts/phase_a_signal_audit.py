#!/usr/bin/env python3
"""Recompute object-level Phase A signal checks from frozen bake assets.

This script reads, but never edits, the frozen round-015 bake handoff and
object metrics. It writes only inside the independent BAVGC research folder.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy.stats import spearmanr


ROOT = Path("/4T/CXY/MV-Painter")
HANDOFF = ROOT / "final_paper_20261012/source/data/gap_closure015/BAKE_INPUT_HANDOFF_V3.json"
METRICS = ROOT / "final_paper_20261012/source/data/primary_studies/BAKE10_OBJECT_METRICS.csv"
OUT = ROOT / "1014_bake_aware_research"
BOOTSTRAP_DRAWS = 50_000
BOOTSTRAP_SEED = 20261013


def masked_rgb_mae(reference_path: str, mask_path: str, generated_path: str) -> tuple[float, float]:
    """Return RGB MAE on foreground and a 2-pixel-eroded foreground mask."""
    with Image.open(reference_path) as image:
        ref = image.convert("RGB")
    with Image.open(generated_path) as image:
        pred = image.convert("RGB")
    with Image.open(mask_path) as image:
        mask = image.convert("L")

    if ref.size != mask.size:
        raise ValueError(f"reference/mask size mismatch: {ref.size} vs {mask.size}")
    ref = ref.resize(pred.size, Image.Resampling.BICUBIC)
    mask = mask.resize(pred.size, Image.Resampling.NEAREST)
    ref_rgb = np.asarray(ref, dtype=np.float32) / 255.0
    pred_rgb = np.asarray(pred, dtype=np.float32) / 255.0
    fg = np.asarray(mask, dtype=np.uint8) > 127
    eroded = np.asarray(mask.filter(ImageFilter.MinFilter(5)), dtype=np.uint8) > 127
    if not fg.any() or not eroded.any():
        raise ValueError(f"empty reference foreground mask: {mask_path}")
    delta = np.abs(pred_rgb - ref_rgb).mean(axis=-1)
    return float(delta[fg].mean()), float(delta[eroded].mean())


def load_inputs() -> tuple[list[dict], dict[str, dict[str, float]]]:
    handoff = json.loads(HANDOFF.read_text())
    metric_rows: dict[str, dict[str, float]] = {}
    with METRICS.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["method"] == "gt":
                continue
            metric_rows[(row["object_uid"], row["method"])] = {
                k: float(row[k]) for k in (
                    "fg_lpips", "fg_psnr", "fg_ssim", "ciede2000",
                    "texture_coverage", "cross_view_texel_variance",
                    "uv_seam_discontinuity",
                )
            }

    signal_rows = []
    expected_methods = set(handoff["conditions"])
    for obj in handoff["objects"]:
        mapping = obj["target_view_mapping"][0]
        raw_view = int(mapping["raw_view_index"])
        if mapping["slot"] != 0 or mapping["rotated_ccw_90"]:
            raise ValueError(f"unexpected source-slot mapping for {obj['uid']}: {mapping}")
        if raw_view not in (0, 14):
            raise ValueError(f"unverified source view {raw_view} for {obj['uid']}")
        reference_path = obj["gt_rgba_17"][raw_view]
        mask_path = obj["foreground_masks_17"][raw_view]
        for method, record in obj["generated_conditions"].items():
            if method not in expected_methods:
                raise ValueError(f"unexpected method {method}")
            view = record["target_views"][0]
            if view["slot"] != 0 or int(view["raw_view_index"]) != raw_view:
                raise ValueError(f"generated/source camera mismatch for {obj['uid']}/{method}")
            full_mae, eroded_mae = masked_rgb_mae(reference_path, mask_path, view["path"])
            metric = metric_rows[(obj["uid"], method)]
            signal_rows.append({
                "object_uid": obj["uid"],
                "method": method,
                "source_raw_view": raw_view,
                "source_rgb_mae": full_mae,
                "source_rgb_mae_eroded2px": eroded_mae,
                **metric,
            })
    if len(signal_rows) != len(handoff["objects"]) * len(expected_methods):
        raise ValueError(f"incomplete object×method rows: {len(signal_rows)}")
    return signal_rows, handoff["objects"]


def rank_accuracy(x: np.ndarray, y: np.ndarray) -> float:
    concordant = []
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 or dy == 0:
                continue
            concordant.append(np.sign(dx) == np.sign(dy))
    return float(np.mean(concordant)) if concordant else float("nan")


def target_loss(name: str, value: float) -> float:
    """Orient every endpoint so lower always means better."""
    return -value if name in {"fg_psnr", "fg_ssim"} else value


def object_summary(rows: list[dict], signal: str, target: str) -> list[dict]:
    out = []
    by_object: dict[str, list[dict]] = {}
    for row in rows:
        by_object.setdefault(row["object_uid"], []).append(row)
    for uid, group in sorted(by_object.items()):
        x = np.asarray([r[signal] for r in group], dtype=np.float64)
        y_raw = np.asarray([r[target] for r in group], dtype=np.float64)
        y = np.asarray([target_loss(target, value) for value in y_raw], dtype=np.float64)
        rho = float(spearmanr(x, y).statistic)
        best_signal_i = int(np.argmin(x))
        best_target_i = int(np.argmin(y))
        out.append({
            "object_uid": uid,
            "spearman": rho,
            "pairwise_rank_accuracy": rank_accuracy(x, y),
            "selected_method": group[best_signal_i]["method"],
            "selected_target": float(y_raw[best_signal_i]),
            "oracle_method": group[best_target_i]["method"],
            "oracle_target": float(y_raw[best_target_i]),
            "regret": float(y[best_signal_i] - y[best_target_i]),
            "signal_range": float(np.ptp(x)),
        })
    return out


def cv_rank_predict(rows: list[dict], features: list[str], target: str) -> list[dict]:
    """LOO-object linear rank prediction, training-only within-object centering."""
    objects = sorted({r["object_uid"] for r in rows})
    records = []
    for heldout in objects:
        train = [r for r in rows if r["object_uid"] != heldout]
        test = [r for r in rows if r["object_uid"] == heldout]

        centered_x, centered_y = [], []
        for uid in objects:
            if uid == heldout:
                continue
            group = [r for r in train if r["object_uid"] == uid]
            centered_x.extend([
                [r[k] - np.mean([g[k] for g in group]) for k in features]
                for r in group
            ])
            centered_y.extend([r[target] - np.mean([g[target] for g in group]) for r in group])
        xtrain = np.asarray(centered_x, dtype=np.float64)
        ytrain = np.asarray(centered_y, dtype=np.float64)
        scales = xtrain.std(axis=0, ddof=0)
        scales[scales == 0] = 1.0
        xscaled = xtrain / scales
        coef, *_ = np.linalg.lstsq(xscaled, ytrain, rcond=None)

        xtest_raw = np.asarray([[r[k] for k in features] for r in test], dtype=np.float64)
        xtest = (xtest_raw - xtest_raw.mean(axis=0)) / scales
        pred = xtest @ coef
        ytest_raw = np.asarray([r[target] for r in test], dtype=np.float64)
        ytest = np.asarray([target_loss(target, value) for value in ytest_raw], dtype=np.float64)
        rho = float(spearmanr(pred, ytest).statistic)
        best_i = int(np.argmin(pred))
        oracle_i = int(np.argmin(ytest))
        records.append({
            "object_uid": heldout,
            "spearman": rho,
            "pairwise_rank_accuracy": rank_accuracy(pred, ytest),
            "selected_method": test[best_i]["method"],
            "selected_target": float(ytest_raw[best_i]),
            "oracle_method": test[oracle_i]["method"],
            "oracle_target": float(ytest_raw[oracle_i]),
            "regret": float(ytest[best_i] - ytest[oracle_i]),
            "coefficients_standardized": coef.tolist(),
        })
    return records


def bootstrap_mean_ci(values: list[float], rng: np.random.Generator) -> list[float]:
    vals = np.asarray(values, dtype=np.float64)
    samples = rng.choice(vals, size=(BOOTSTRAP_DRAWS, len(vals)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def summarize(records: list[dict], rng: np.random.Generator) -> dict:
    rhos = [r["spearman"] for r in records]
    pair_acc = [r["pairwise_rank_accuracy"] for r in records]
    regrets = [r["regret"] for r in records]
    positive = sum(v > 0 for v in rhos)
    negative = sum(v < 0 for v in rhos)
    return {
        "n_objects": len(records),
        "mean_object_spearman": float(np.mean(rhos)),
        "median_object_spearman": float(np.median(rhos)),
        "mean_spearman_object_bootstrap_ci95": bootstrap_mean_ci(rhos, rng),
        "objects_positive_rho": positive,
        "objects_negative_rho": negative,
        "mean_object_pairwise_rank_accuracy": float(np.mean(pair_acc)),
        "mean_pairwise_accuracy_object_bootstrap_ci95": bootstrap_mean_ci(pair_acc, rng),
        "mean_best_signal_selection_regret": float(np.mean(regrets)),
        "mean_selection_regret_object_bootstrap_ci95": bootstrap_mean_ci(regrets, rng),
        "selected_method_counts": {
            method: sum(r["selected_method"] == method for r in records)
            for method in sorted({r["selected_method"] for r in records})
        },
        "object_records": records,
    }


def main() -> None:
    rows, _ = load_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "phase_a_signal_rows.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    signals = [
        "cross_view_texel_variance",
        "source_rgb_mae",
        "source_rgb_mae_eroded2px",
    ]
    targets = ["fg_lpips", "fg_psnr", "fg_ssim", "ciede2000"]
    summary: dict = {
        "scope": "10 previously exposed objects × 7 frozen schedule controls; one archived bake seed per object/control",
        "unit_of_inference": "object; all control rows are summarized within object before bootstrap",
        "outcome_direction": {"fg_lpips": "lower better", "fg_psnr": "higher better", "fg_ssim": "higher better", "ciede2000": "lower better"},
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "source_camera_validation": "The generated slot-0 raw view matches target_view_mapping slot 0 and uses raw camera 0 or 14; no rotation was applied. The source RGBA and mask are loaded from the exact frozen handoff paths.",
        "signals": {},
        "loouo_predictions_for_primary_lpips": {},
    }
    for signal in signals:
        summary["signals"][signal] = {}
        for target in targets:
            records = object_summary(rows, signal, target)
            summary["signals"][signal][target] = summarize(records, rng)

    for feature_set, key in [
        (["cross_view_texel_variance"], "uv_only"),
        (["source_rgb_mae"], "reference_rgb_mae_only"),
        (["cross_view_texel_variance", "source_rgb_mae"], "uv_plus_reference_rgb_mae"),
    ]:
        records = cv_rank_predict(rows, feature_set, "fg_lpips")
        summary["loouo_predictions_for_primary_lpips"][key] = summarize(records, rng)
        summary["loouo_predictions_for_primary_lpips"][key]["features"] = feature_set

    (OUT / "phase_a_signal_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({
        "csv": str(csv_path),
        "summary": str(OUT / "phase_a_signal_summary.json"),
        "primary": {
            "uv_vs_lpips": summary["signals"]["cross_view_texel_variance"]["fg_lpips"]["mean_object_spearman"],
            "ref_vs_lpips": summary["signals"]["source_rgb_mae"]["fg_lpips"]["mean_object_spearman"],
            "loouo_ref_prediction": summary["loouo_predictions_for_primary_lpips"]["reference_rgb_mae_only"]["mean_object_spearman"],
            "loouo_uv_ref_prediction": summary["loouo_predictions_for_primary_lpips"]["uv_plus_reference_rgb_mae"]["mean_object_spearman"],
        },
    }, indent=2))


if __name__ == "__main__":
    main()
