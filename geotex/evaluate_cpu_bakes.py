"""Evaluate CPU-baked unseen renders with object-level and per-view CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from skimage.color import deltaE_ciede2000, rgb2lab


METHODS = ("gt", "no_adapter", "fixed_low", "fixed_high", "c3")
UNSEEN = tuple(range(1, 12))


def load_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0


def resize_rgba(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    if tuple(rgba.shape[1::-1]) == size:
        return rgba
    image = Image.fromarray(np.round(rgba * 255.0).astype(np.uint8), mode="RGBA")
    return np.asarray(image.resize(size, Image.Resampling.BICUBIC), dtype=np.float32) / 255.0


def masked_psnr(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    valid = mask > 0.5
    if not np.any(valid):
        return float("nan")
    mse = float(np.mean((pred[valid] - target[valid]) ** 2))
    return 100.0 if mse < 1e-12 else float(10.0 * math.log10(1.0 / mse))


def masked_ciede2000(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    valid = mask > 0.5
    if not np.any(valid):
        return float("nan")
    return float(deltaE_ciede2000(rgb2lab(pred), rgb2lab(target))[valid].mean())


def silhouette_iou(pred_alpha: np.ndarray, target_alpha: np.ndarray) -> float:
    pred = pred_alpha > 0.5
    target = target_alpha > 0.5
    union = np.logical_or(pred, target).sum()
    return float(np.logical_and(pred, target).sum() / union) if union else 1.0


def build_lpips():
    try:
        import lpips

        model = lpips.LPIPS(net="alex").eval().to("cpu")
        return model, "lpips_alex_cpu"
    except Exception as exc:  # pragma: no cover - environment-dependent
        return None, f"unavailable: {exc!r}"


def build_dists():
    try:
        from DISTS_pytorch import DISTS

        return DISTS().eval().to("cpu"), "dists_cpu"
    except Exception as exc:  # pragma: no cover - environment-dependent
        return None, f"unavailable: {exc!r}"


def learned_batch(model, pred: list[np.ndarray], target: list[np.ndarray], masks: list[np.ndarray]) -> list[float | None]:
    if model is None:
        return [None] * len(pred)
    values = []
    with torch.no_grad():
        for start in range(0, len(pred), 4):
            p = np.stack(pred[start : start + 4])
            t = np.stack(target[start : start + 4])
            m = np.stack(masks[start : start + 4])[:, :, :, None]
            p = torch.from_numpy((p * m).transpose(0, 3, 1, 2)).float() * 2.0 - 1.0
            t = torch.from_numpy((t * m).transpose(0, 3, 1, 2)).float() * 2.0 - 1.0
            values.extend(float(value) for value in model(p, t).reshape(-1).tolist())
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bake-dir", type=Path, required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--objects", required=True)
    parser.add_argument("--methods", default=",".join(METHODS))
    parser.add_argument("--skip-learned", action="store_true")
    args = parser.parse_args()
    bake_dir = args.bake_dir.resolve()
    handoff = json.loads(args.handoff.resolve().read_text())
    requested = [value.strip() for value in args.objects.split(",") if value.strip()]
    requested_methods = [value.strip() for value in args.methods.split(",") if value.strip()]
    invalid_methods = [method for method in requested_methods if method not in METHODS]
    if invalid_methods:
        raise ValueError(f"unsupported methods: {invalid_methods}")
    records = {record["object"]: record for record in handoff["objects"]}
    missing = [object_id for object_id in requested if object_id not in records]
    if missing:
        raise KeyError(f"objects not in handoff: {missing}")

    lpips_model, lpips_status = (None, "skipped") if args.skip_learned else build_lpips()
    dists_model, dists_status = (None, "skipped") if args.skip_learned else build_dists()
    per_view = []
    object_rows = []
    for object_id in requested:
        record = records[object_id]
        for method in requested_methods:
            method_dir = bake_dir / method / object_id
            metadata = json.loads((method_dir / "bake_metadata.json").read_text())
            learned_pred = []
            learned_target = []
            learned_mask = []
            pending = []
            for raw_view in UNSEEN:
                render = load_rgba(method_dir / "unseen_renders" / f"view_{raw_view:03d}.png")
                gt = load_rgba(Path(record["gt_rgba_17"][raw_view]))
                gt = resize_rgba(gt, (render.shape[1], render.shape[0]))
                gt_rgb = gt[:, :, :3] * gt[:, :, 3:4] + (1.0 - gt[:, :, 3:4])
                render_rgb = render[:, :, :3]
                gt_mask = gt[:, :, 3]
                pred_mask = render[:, :, 3]
                learned_pred.append(render_rgb)
                learned_target.append(gt_rgb)
                learned_mask.append(gt_mask)
                pending.append({
                    "object": object_id,
                    "method": method,
                    "raw_view": raw_view,
                    "masked_psnr": masked_psnr(render_rgb, gt_rgb, gt_mask),
                    "ciede2000": masked_ciede2000(render_rgb, gt_rgb, gt_mask),
                    "silhouette_iou": silhouette_iou(pred_mask, gt_mask),
                    "gt_coverage": float((gt_mask > 0.5).mean()),
                    "render_coverage": float((pred_mask > 0.5).mean()),
                    "texture_coverage": metadata["texture_coverage"],
                    "cross_view_texel_variance": metadata["cross_view_texel_variance"],
                    "uv_seam_discontinuity": metadata["uv_seam_discontinuity"],
                    "fg_lpips": None,
                    "dists": None,
                })
            lpips_values = learned_batch(lpips_model, learned_pred, learned_target, learned_mask)
            dists_values = learned_batch(dists_model, learned_pred, learned_target, learned_mask)
            for row, lpips_value, dists_value in zip(pending, lpips_values, dists_values):
                row["fg_lpips"] = lpips_value
                row["dists"] = dists_value
                per_view.append(row)
            numeric_keys = (
                "masked_psnr", "ciede2000", "silhouette_iou", "gt_coverage", "render_coverage",
                "texture_coverage", "cross_view_texel_variance", "uv_seam_discontinuity", "fg_lpips", "dists",
            )
            object_row = {"object": object_id, "method": method, "unseen_views": len(pending)}
            for key in numeric_keys:
                values = [row[key] for row in pending if row[key] is not None and np.isfinite(row[key])]
                object_row[key] = float(np.mean(values)) if values else None
            object_rows.append(object_row)

    fields = list(per_view[0])
    with (bake_dir / "UNSEEN_PER_VIEW_METRICS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(per_view)
    fields = list(object_rows[0])
    with (bake_dir / "UNSEEN_OBJECT_METRICS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(object_rows)
    summary = {
        "protocol": "codex-d-cpu-bake-unseen-evaluation-v1",
        "objects": requested,
        "methods": requested_methods,
        "unseen_views": UNSEEN,
        "lpips": lpips_status,
        "dists": dists_status,
        "object_metric_rows": len(object_rows),
        "per_view_metric_rows": len(per_view),
        "gt_to_gt_sanity_rows": len(requested) if "gt" in requested_methods else 0,
        "note": "GT is a bake implementation sanity check, not a method advantage claim; rows are emitted only when gt is requested.",
    }
    (bake_dir / "UNSEEN_METRICS_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
