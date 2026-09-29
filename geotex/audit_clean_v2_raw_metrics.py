"""Recompute clean-v2 image metrics from the stored PNGs and source alpha/depth.

This is deliberately an audit utility, not a replacement for the inference
runner.  It reproduces the historical dataset compositing, unique6 ordering,
panel layout, mask handling, and metric implementation without touching the
checkpoint or the evaluation outputs.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from einops import rearrange
from PIL import Image
from torchvision.transforms import v2
from torchvision.transforms.functional import rotate

_HISTORICAL_METRICS_PATH = Path("/tmp/mv_main_rerun/geotex/metrics.py")
_SPEC = importlib.util.spec_from_file_location("historical_geotex_metrics", _HISTORICAL_METRICS_PATH)
_HISTORICAL_METRICS = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_HISTORICAL_METRICS)
compute_edge_mask = _HISTORICAL_METRICS.compute_edge_mask
compute_psnr = _HISTORICAL_METRICS.compute_psnr
compute_ssim = _HISTORICAL_METRICS.compute_ssim


METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
UNIQUE6 = (0, 15, 12, 16, 13, 14)


def read_rgba(path: Path) -> tuple[torch.Tensor, torch.Tensor]:
    raw = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if raw is None:
        raise FileNotFoundError(path)
    raw = cv2.cvtColor(raw, cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255.0
    alpha = raw[:, :, 3:4]
    rgb = raw[:, :, :3] * alpha + (1.0 - alpha)
    return (
        torch.from_numpy(rgb.transpose(2, 0, 1)).float(),
        torch.from_numpy(alpha.transpose(2, 0, 1)).float(),
    )


def panel_views(views: list[torch.Tensor], reverse: bool) -> torch.Tensor:
    selected = list((14, 15, 0, 16, 12, 13) if reverse else UNIQUE6)
    out = []
    for position, view_idx in enumerate(selected):
        item = views[view_idx]
        if reverse and position in (1, 3):
            item = rotate(item, 90)
        out.append(item)
    out = v2.functional.resize(torch.stack(out), 256, interpolation=3, antialias=True)
    return rearrange(out, "(x y) c h w -> c (x h) (y w)", x=3, y=2)


def panel_for_uid(data_root: Path, uid: str) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, bool]:
    root = data_root / uid
    rgb, alpha = zip(*(read_rgba(root / "image" / f"{idx:03d}.png") for idx in range(17)))
    rgb, alpha = list(rgb), list(alpha)
    reverse = bool((alpha[0] == 0).sum() > (alpha[14] == 0).sum())
    target = panel_views(rgb, reverse)
    mask = panel_views(alpha, reverse)

    depth_views = []
    for idx in range(17):
        depth = cv2.imread(str(root / "depth_png" / f"{idx:03d}.png"), cv2.IMREAD_UNCHANGED)
        if depth is None:
            raise FileNotFoundError(root / "depth_png" / f"{idx:03d}.png")
        if depth.ndim == 2:
            depth = depth[:, :, None]
        depth = depth.astype(np.float32) / 65535.0
        depth_views.append(torch.from_numpy(depth.transpose(2, 0, 1)).float())
    depth = panel_views(depth_views, reverse)
    return target, mask, depth, reverse


def load_panel(path: Path) -> torch.Tensor:
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(image.transpose(2, 0, 1)).float()


def lpips_value(fn, pred: torch.Tensor, target: torch.Tensor, mask: torch.Tensor | None) -> float:
    if fn is None:
        return float("nan")
    pred = pred.unsqueeze(0) * 2.0 - 1.0
    target = target.unsqueeze(0) * 2.0 - 1.0
    if mask is not None:
        pred = pred * mask.unsqueeze(0)
        target = target * mask.unsqueeze(0)
    with torch.no_grad():
        return float(fn(pred, target).item())


def lpips_batch(fn, preds: torch.Tensor, target: torch.Tensor, mask: torch.Tensor | None) -> list[float]:
    if fn is None:
        return [float("nan")] * preds.shape[0]
    preds = preds * 2.0 - 1.0
    target = target * 2.0 - 1.0
    if mask is not None:
        preds = preds * mask
        target = target * mask
    with torch.no_grad():
        values = fn(preds, target).reshape(-1).tolist()
    return [float(value) for value in values]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-dir", type=Path, required=True)
    parser.add_argument("--object-list", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--compute-lpips",
        action="store_true",
        help="recompute LPIPS on CPU; otherwise attach the already recorded float-eval LPIPS values",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    uids = [line.strip() for line in args.object_list.read_text().splitlines() if line.strip()]
    if len(uids) != 300:
        raise ValueError(f"expected 300 UIDs, found {len(uids)}")
    lpips_fn = None
    if args.compute_lpips:
        try:
            import lpips

            lpips_fn = lpips.LPIPS(net="alex").to("cpu").eval()
        except Exception as exc:  # the non-LPIPS metrics remain useful offline
            print(f"LPIPS unavailable: {exc}")

    recorded_lpips = {}
    if lpips_fn is None:
        for method in METHODS:
            with (args.eval_dir / f"per_object_{method}.csv").open(newline="") as handle:
                for row in csv.DictReader(handle):
                    recorded_lpips[(method, row["object"])] = {
                        "full_lpips": float(row["full_lpips"]),
                        "fg_lpips": float(row["fg_lpips"]),
                    }

    rows = []
    align_rows = []
    for idx, uid in enumerate(uids):
        object_id = f"obj_{idx:04d}"
        target, mask, depth, reverse = panel_for_uid(args.data_root, uid)
        saved_gt = load_panel(args.eval_dir / "predictions" / "ground_truth" / f"{object_id}.png")
        gt_mae = float((target - saved_gt).abs().mean())
        gt_max = float((target - saved_gt).abs().max())
        inferred_mask = (saved_gt < 0.95).any(dim=0, keepdim=True).float()
        binary_mask = mask > 0.5
        binary_inferred = inferred_mask > 0.5
        intersection = float((binary_mask & binary_inferred).sum())
        union = float((binary_mask | binary_inferred).sum())
        mask_iou = intersection / union if union else 1.0
        align_rows.append({
            "object": object_id,
            "uid": uid,
            "reverse": reverse,
            "gt_reconstruction_mae": gt_mae,
            "gt_reconstruction_max_abs": gt_max,
            "mask_coverage": float(mask.mean()),
            "saved_gt_threshold_mask_iou": mask_iou,
        })

        edge = compute_edge_mask(depth.unsqueeze(0), threshold=0.1)
        row_base = {"object": object_id, "uid": uid, "reverse": reverse}
        for method in METHODS:
            pred = load_panel(args.eval_dir / "predictions" / method / f"{object_id}.png")
            row = {**row_base, "method": method}
            row.update({
                "full_psnr": compute_psnr(pred.unsqueeze(0), target.unsqueeze(0)),
                "fg_psnr": compute_psnr(pred.unsqueeze(0), target.unsqueeze(0), mask.unsqueeze(0)),
                "full_ssim": compute_ssim(pred.unsqueeze(0), target.unsqueeze(0)),
                "fg_ssim": compute_ssim(pred.unsqueeze(0), target.unsqueeze(0), mask.unsqueeze(0)),
                "edge_ssim": compute_ssim(pred.unsqueeze(0), target.unsqueeze(0), edge),
                "full_lpips": float("nan") if lpips_fn is not None else recorded_lpips[(method, object_id)]["full_lpips"],
                "fg_lpips": float("nan") if lpips_fn is not None else recorded_lpips[(method, object_id)]["fg_lpips"],
                "mask_coverage": float(mask.mean()),
            })
            rows.append(row)
        if (idx + 1) % 25 == 0:
            print(f"[{idx + 1}/300]", flush=True)

    # LPIPS is batched because the reference environment has no CUDA device.
    # The other metrics above are already complete and do not depend on this
    # pass.  Keep the row order stable while filling the two LPIPS columns.
    if lpips_fn is not None:
        row_by_key = {(row["object"], row["uid"]): row for row in rows}
        for method in METHODS:
            for start in range(0, len(uids), 8):
                preds, targets, masks, keys = [], [], [], []
                for idx in range(start, min(start + 8, len(uids))):
                    uid = uids[idx]
                    target, mask, _, _ = panel_for_uid(args.data_root, uid)
                    preds.append(load_panel(args.eval_dir / "predictions" / method / f"obj_{idx:04d}.png"))
                    targets.append(target)
                    masks.append(mask)
                    keys.append((f"obj_{idx:04d}", uid))
                pred_batch = torch.stack(preds)
                target_batch = torch.stack(targets)
                mask_batch = torch.stack(masks)
                full_values = lpips_batch(lpips_fn, pred_batch, target_batch, None)
                fg_values = lpips_batch(lpips_fn, pred_batch, target_batch, mask_batch)
                for key, full_value, fg_value in zip(keys, full_values, fg_values):
                    row_by_key[key]["full_lpips"] = full_value
                    row_by_key[key]["fg_lpips"] = fg_value
            print(f"LPIPS complete: {method}", flush=True)

    fields = list(rows[0])
    with (args.output_dir / "raw_metric_recheck_300.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (args.output_dir / "mask_alignment_audit.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(align_rows[0]))
        writer.writeheader()
        writer.writerows(align_rows)

    summary = {"n_objects": 300, "methods": {}, "alignment": {}}
    for method in METHODS:
        method_rows = [r for r in rows if r["method"] == method]
        summary["methods"][method] = {
            key: float(np.mean([r[key] for r in method_rows]))
            for key in ("full_psnr", "fg_psnr", "full_ssim", "fg_ssim", "edge_ssim", "full_lpips", "fg_lpips")
        }
    summary["alignment"] = {
        "mean_gt_reconstruction_mae": float(np.mean([r["gt_reconstruction_mae"] for r in align_rows])),
        "max_gt_reconstruction_mae": float(np.max([r["gt_reconstruction_mae"] for r in align_rows])),
        "mean_gt_reconstruction_max_abs": float(np.mean([r["gt_reconstruction_max_abs"] for r in align_rows])),
        "mean_saved_gt_threshold_mask_iou": float(np.mean([r["saved_gt_threshold_mask_iou"] for r in align_rows])),
        "min_saved_gt_threshold_mask_iou": float(np.min([r["saved_gt_threshold_mask_iou"] for r in align_rows])),
    }
    (args.output_dir / "raw_metric_recheck_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
