#!/usr/bin/env python
"""Compare the frozen historical cases under unique6 and legacy view modes."""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from omegaconf import OmegaConf
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages
from skimage.color import deltaE_ciede2000, rgb2lab
from torchvision.utils import save_image

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
METHODS = [
    ("no_adapter", "No Adapter"), ("native_gfl", "GFL"), ("native_gfh", "GFH"),
    ("native_gc3", "C3"), ("gen_linear", "Generic Linear"), ("layer_llh", "LLH"),
]

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
from data_utils import collate_batch, prepare_batch  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402


def build_dataset(sample: dict, mode: str):
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = mode
    validation.params.object_list_file = str(Path(sample["object_list"]).resolve())
    validation.params.root_dir_list = [str(Path(sample["data_root"]).resolve())]
    return instantiate_from_config(validation)


def read_grid(path: Path, rgb: bool = True) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB" if rgb else "L"))


def tile(grid: np.ndarray, view: int) -> np.ndarray:
    row, col = divmod(view, 2)
    return grid[row * 256:(row + 1) * 256, col * 256:(col + 1) * 256]


def score(pred_grid: np.ndarray, ref_grid: np.ndarray, mask_grid: np.ndarray) -> tuple[float, float, float]:
    values = []
    for view in range(6):
        pred = tile(pred_grid, view).astype(np.float32) / 255.0
        ref = tile(ref_grid, view).astype(np.float32) / 255.0
        mask = tile(mask_grid, view) > 127
        lp, lg = rgb2lab(pred), rgb2lab(ref)
        de = deltaE_ciede2000(lg, lp)
        delta = lp - lg
        values.append((float(de[mask].mean()), float(delta[..., 1][mask].mean()),
                       float(delta[..., 2][mask].mean())))
    return tuple(float(np.mean([x[i] for x in values])) for i in range(3))


def visual_pdf(pdf: PdfPages, sample: dict, legacy_dir: Path) -> None:
    fig = plt.figure(figsize=(18, 12))
    fig.text(0.05, 0.965, f"View protocol ablation — {sample['sample_id']}", fontsize=18, weight="bold")
    fig.text(0.05, 0.935,
             "Only target_view_mode changes: unique6 [0,15,12,16,13,14] vs legacy_duplicate_top [0,15,12,15,13,14].",
             fontsize=10)
    columns = [("reference", "Reference")] + METHODS
    left, right = 0.10, 0.985
    width = (right - left) / len(columns)
    row_specs = [("unique6", 0.51, 0.84), ("legacy_duplicate_top", 0.10, 0.43)]
    for col, (_, label) in enumerate(columns):
        fig.text(left + col * width + width / 2, 0.885, label, ha="center", fontsize=10, weight="bold")
    for mode, y0, y1 in row_specs:
        fig.text(0.02, y1 - 0.015, mode, fontsize=9, weight="bold", va="top", rotation=90)
        for col, (method, _) in enumerate(columns):
            if method == "reference":
                path = (ARTIFACT / "raw_rgb" / sample["sample_id"] / "reference.png" if mode == "unique6"
                        else legacy_dir / "references" / f"{sample['sample_id']}.png")
            elif mode == "unique6":
                path = ARTIFACT / "raw_rgb" / sample["sample_id"] / f"{method}.png"
            else:
                path = legacy_dir / "predictions" / method / f"{sample['uid']}.png"
            ax = fig.add_axes([left + col * width + 0.01, y0, width - 0.02, y1 - y0])
            ax.imshow(Image.open(path).convert("RGB"), interpolation="nearest")
            ax.set_axis_off()
    fig.text(0.05, 0.035,
             "Full 512×768 RGB grids are shown without crop or recoloring. The historical object set is failure-enriched and descriptive.",
             fontsize=9)
    pdf.savefig(fig, dpi=160)
    plt.close(fig)


def main() -> None:
    freeze = json.loads((ARTIFACT / "SAMPLE_FREEZE.json").read_text())
    legacy_dir = ARTIFACT / "runs/legacy_duplicate_top_six_conditions"
    legacy_run_rows = json.loads((legacy_dir / "rows_shard0.json").read_text())
    run_metrics = {(row["object_uid"], row["condition"]): row for row in legacy_run_rows}
    unique_metrics = {
        (row["sample_id"], row["method"]): row
        for row in csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open())
    }
    samples = [s for s in freeze["samples"] if s["source"] == "01549_fig4_fig6_original_object"]
    unique_dataset, legacy_dataset = {}, {}
    legacy_ref_dir = legacy_dir / "references"
    legacy_mask_dir = legacy_dir / "masks"
    legacy_ref_dir.mkdir(parents=True, exist_ok=True)
    legacy_mask_dir.mkdir(parents=True, exist_ok=True)
    output_rows = []
    prediction_diff_rows = []
    duplicate_checks = []

    for sample in samples:
        source = sample["source"]
        if source not in unique_dataset:
            unique_dataset[source] = build_dataset(sample, "unique6")
            legacy_dataset[source] = build_dataset(sample, "legacy_duplicate_top")
        seed = int(sample["object_seed"])
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        batch = collate_batch(unique_dataset[source], int(sample["object_idx"]), "cpu")
        _, unique_ref, _, _, _, unique_mask = prepare_batch(batch, 256, "cpu")
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        batch_legacy = collate_batch(legacy_dataset[source], int(sample["object_idx"]), "cpu")
        _, legacy_ref, _, _, _, legacy_mask = prepare_batch(batch_legacy, 256, "cpu")
        ref_path = legacy_ref_dir / f"{sample['sample_id']}.png"
        mask_path = legacy_mask_dir / f"{sample['sample_id']}.png"
        save_image(legacy_ref, ref_path)
        save_image(legacy_mask, mask_path)
        unique_ref_path = ARTIFACT / "raw_rgb" / sample["sample_id"] / "reference.png"
        unique_mask_path = ARTIFACT / "masks" / f"{sample['sample_id']}.png"
        unique_ref_grid = read_grid(unique_ref_path)
        unique_mask_grid = read_grid(unique_mask_path, rgb=False)
        legacy_ref_grid = read_grid(ref_path)
        legacy_mask_grid = read_grid(mask_path, rgb=False)
        duplicate_checks.append(bool(np.array_equal(tile(legacy_ref_grid, 1), tile(legacy_ref_grid, 3))))

        for mode, ref_grid, mask_grid, folder in (
            ("unique6", unique_ref_grid, unique_mask_grid, None),
            ("legacy_duplicate_top", legacy_ref_grid, legacy_mask_grid, legacy_dir),
        ):
            for method_key, method_label in METHODS:
                pred_path = (ARTIFACT / "raw_rgb" / sample["sample_id"] / f"{method_key}.png" if folder is None
                             else folder / "predictions" / method_key / f"{sample['uid']}.png")
                pred_grid = read_grid(pred_path)
                ciede, delta_a, delta_b = score(pred_grid, ref_grid, mask_grid)
                if mode == "unique6":
                    pair = unique_metrics[(sample["sample_id"], method_label)]
                    psnr, lpips, edge = float(pair["fg_psnr"]), float(pair["fg_lpips"]), float(pair["edge_ssim"])
                else:
                    pair = run_metrics[(sample["uid"], method_key)]
                    psnr, lpips, edge = float(pair["fg_psnr"]), float(pair["fg_lpips"]), float(pair["edge_ssim"])
                output_rows.append({
                    "sample_id": sample["sample_id"], "uid": sample["uid"], "method": method_label,
                    "mode": mode, "mean_fg_ciede2000": ciede, "mean_delta_a_star": delta_a,
                    "mean_delta_b_star": delta_b, "fg_psnr": psnr, "fg_lpips": lpips,
                    "edge_ssim": edge, "fourth_tile_equals_second_tile": mode == "legacy_duplicate_top",
                })
        for method_key, method_label in METHODS:
            unique_pred = read_grid(ARTIFACT / "raw_rgb" / sample["sample_id"] / f"{method_key}.png")
            legacy_pred = read_grid(legacy_dir / "predictions" / method_key / f"{sample['uid']}.png")
            diffs = [float(np.abs(tile(unique_pred, view).astype(np.float32) -
                                  tile(legacy_pred, view).astype(np.float32)).mean())
                     for view in range(6)]
            prediction_diff_rows.append({
                "sample_id": sample["sample_id"], "uid": sample["uid"], "method": method_label,
                **{f"view_{view}_rgb_mae": diffs[view] for view in range(6)},
                "changed_view_rgb_mae": diffs[3],
                "other_five_view_rgb_mae": float(np.mean([diffs[v] for v in (0, 1, 2, 4, 5)])),
            })

    metrics_path = ARTIFACT / "logs/VIEWMODE_ABLATION_RGB_METRICS.csv"
    with metrics_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_rows[0].keys())
        writer.writeheader(); writer.writerows(output_rows)
    summary = {}
    for _, method_label in METHODS:
        u = [r for r in output_rows if r["method"] == method_label and r["mode"] == "unique6"]
        l = [r for r in output_rows if r["method"] == method_label and r["mode"] == "legacy_duplicate_top"]
        delta = [x["mean_fg_ciede2000"] - y["mean_fg_ciede2000"] for x, y in zip(l, u)]
        summary[method_label] = {
            "n_historical_objects": len(u),
            "mean_ciede_unique6": float(np.mean([r["mean_fg_ciede2000"] for r in u])),
            "mean_ciede_legacy_duplicate_top": float(np.mean([r["mean_fg_ciede2000"] for r in l])),
            "mean_ciede_legacy_minus_unique": float(np.mean(delta)),
            "legacy_lower_ciede_objects": int(sum(x < 0 for x in delta)),
            "legacy_higher_ciede_objects": int(sum(x > 0 for x in delta)),
            "mean_fg_psnr_legacy_minus_unique": float(np.mean([x["fg_psnr"] - y["fg_psnr"] for x, y in zip(l, u)])),
            "mean_fg_lpips_legacy_minus_unique": float(np.mean([x["fg_lpips"] - y["fg_lpips"] for x, y in zip(l, u)])),
            "mean_edge_ssim_legacy_minus_unique": float(np.mean([x["edge_ssim"] - y["edge_ssim"] for x, y in zip(l, u)])),
        }
    summary_path = ARTIFACT / "logs/VIEWMODE_ABLATION_SUMMARY.json"
    diff_path = ARTIFACT / "logs/VIEWMODE_PREDICTION_DIFFERENCES.csv"
    with diff_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=prediction_diff_rows[0].keys())
        writer.writeheader(); writer.writerows(prediction_diff_rows)
    for method_label, method_data in summary.items():
        subset = [r for r in prediction_diff_rows if r["method"] == method_label]
        method_data["mean_prediction_rgb_mae_in_changed_view"] = float(
            np.mean([r["changed_view_rgb_mae"] for r in subset]))
        method_data["mean_prediction_rgb_mae_in_other_five_views"] = float(
            np.mean([r["other_five_view_rgb_mae"] for r in subset]))
    summary_path.write_text(json.dumps({
        "controlled_intervention": "target_view_mode unique6 -> legacy_duplicate_top",
        "checkpoint": freeze["protocol_identity"]["checkpoint_sha256"],
        "historical_objects": [s["sample_id"] for s in samples],
        "legacy_reference_fourth_tile_equals_second_tile_all_six": all(duplicate_checks),
        "metrics": summary,
        "interpretation_limit": "six previously viewed, failure-enriched historical objects; descriptive only",
    }, indent=2) + "\n")
    pdf_path = ARTIFACT / "VIEWMODE_ABLATION_COMPARISON.pdf"
    with PdfPages(pdf_path, metadata={"Title": "Unique6 vs legacy duplicate-top view protocol"}) as pdf:
        fig = plt.figure(figsize=(14, 8.5))
        fig.text(0.05, 0.93, "Controlled target-view protocol ablation", fontsize=20, weight="bold")
        fig.text(0.05, 0.875, "Same current checkpoint, six objects, six schedules, seeds, sampler, and inference settings.", fontsize=12)
        fig.text(0.05, 0.835, "Single intervention: the fourth target slot changes from view 16 to a duplicate of view 15.", fontsize=12)
        table_data = [[method,
                       f"{data['mean_ciede_unique6']:.2f}",
                       f"{data['mean_ciede_legacy_duplicate_top']:.2f}",
                       f"{data['mean_ciede_legacy_minus_unique']:+.2f}",
                       f"{data['legacy_higher_ciede_objects']}/6"]
                      for method, data in summary.items()]
        ax = fig.add_axes([0.05, 0.40, 0.88, 0.35]); ax.axis("off")
        table = ax.table(cellText=table_data,
                         colLabels=["Condition", "unique6 CIEDE ↓", "legacy CIEDE ↓", "legacy − unique", "Legacy worse"],
                         cellLoc="left", colLoc="left", loc="center")
        table.auto_set_font_size(False); table.set_fontsize(11); table.scale(1.0, 1.55)
        fig.text(0.05, 0.29,
                 "In legacy mode, the fourth reference tile duplicates the second for all six objects. This is a confirmed target-view protocol defect. Its effect on quality is limited to the paired metrics above and the following full RGB grids.",
                 fontsize=11, wrap=True)
        fig.text(0.05, 0.19,
                 "All metric differences are descriptive on six failure-enriched historical examples. Color is measured from saved PNGs; PSNR, LPIPS, and Edge-SSIM use the locked evaluation code and matching target mode.",
                 fontsize=10, wrap=True)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)
        for sample in samples:
            visual_pdf(pdf, sample, legacy_dir)
    print(f"wrote {metrics_path}, {diff_path}, {summary_path}, and {pdf_path}")


if __name__ == "__main__":
    main()
