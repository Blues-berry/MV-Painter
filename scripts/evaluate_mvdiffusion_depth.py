#!/usr/bin/env python3
"""Evaluate MVDiffusion interop outputs on the shared six target views.

The resulting columns are deliberately named ``interop_*``: MVDiffusion is a
text+depth-conditioned perspective generator, while the frozen MVPainter
renders are orthographic and the exported adapter uses an equivalent pinhole
camera.  These numbers are useful for deployment diagnostics and paired
within-MVDiffusion checks, not for pooling absolute backbone scores.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geotex.metrics.image_metrics import compute_psnr, compute_ssim


def read_target(path: Path, size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    rgba = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0
    rgb = rgba[..., :3] * rgba[..., 3:4] + (1.0 - rgba[..., 3:4])
    target = Image.fromarray(np.rint(rgb * 255.0).astype(np.uint8), mode="RGB")
    mask = Image.fromarray(np.rint(rgba[..., 3] * 255.0).astype(np.uint8), mode="L")
    target = np.asarray(target.resize(size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    mask = np.asarray(mask.resize(size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    return target, mask


def edge_mask(mask: np.ndarray) -> np.ndarray:
    binary = (mask > 0.5).astype(np.uint8)
    dilated = cv2.dilate(binary, np.ones((3, 3), np.uint8)) > 0
    eroded = cv2.erode(binary, np.ones((3, 3), np.uint8)) > 0
    edge = dilated & ~eroded
    return edge if edge.any() else binary.astype(bool)


def view_metrics(pred_path: Path, gt_path: Path) -> dict[str, float]:
    pred = np.asarray(Image.open(pred_path).convert("RGB"), dtype=np.float32) / 255.0
    height, width = pred.shape[:2]
    target, mask = read_target(gt_path, (width, height))
    mask_t = torch.from_numpy(mask[None, None]).float()
    pred_t = torch.from_numpy(pred.transpose(2, 0, 1)[None]).float()
    target_t = torch.from_numpy(target.transpose(2, 0, 1)[None]).float()
    edge_t = torch.from_numpy(edge_mask(mask).astype(np.float32)[None, None])
    return {
        "psnr": float(compute_psnr(pred_t, target_t, mask_t)),
        "fg_ssim": float(compute_ssim(pred_t, target_t, mask_t)),
        "edge_ssim": float(compute_ssim(pred_t, target_t, edge_t)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--object", dest="object_ids", action="append", default=None)
    args = parser.parse_args()

    payload = json.loads(args.data_manifest.read_text())
    selected = set(args.object_ids) if args.object_ids else None
    rows = [row for row in payload["objects"] if selected is None or row["object"] in selected]
    if not rows:
        raise ValueError("no objects selected")

    result_rows = []
    for row in rows:
        per_view = []
        for local_id, source_id in zip(row["target_local_indices"], row["target_view_ids"]):
            pred_path = args.output_dir / row["object"] / f"view_{local_id:03d}_source_{source_id:03d}.png"
            gt_path = Path(row["source_render_root"]) / "image" / f"{source_id:03d}.png"
            if not pred_path.is_file():
                raise FileNotFoundError(pred_path)
            if not gt_path.is_file():
                raise FileNotFoundError(gt_path)
            per_view.append(view_metrics(pred_path, gt_path))
        result_rows.append(
            {
                "object": row["object"],
                "source_uid": row.get("source_uid", ""),
                "target_view_count": len(per_view),
                "interop_psnr": float(np.mean([item["psnr"] for item in per_view])),
                "interop_fg_ssim": float(np.mean([item["fg_ssim"] for item in per_view])),
                "interop_edge_ssim": float(np.mean([item["edge_ssim"] for item in per_view])),
                "protocol_role": "MVDiffusion depth/text interop diagnostic",
            }
        )

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(result_rows[0])
    with args.csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result_rows)
    summary = {
        "protocol": payload["protocol"],
        "object_count": len(result_rows),
        "mean": {
            field: float(np.mean([row[field] for row in result_rows]))
            for field in ("interop_psnr", "interop_fg_ssim", "interop_edge_ssim")
        },
        "csv": str(args.csv.resolve()),
        "absolute_score_pooling": "forbidden",
        "target_depth_conditioned": bool(payload.get("target_depth_conditioned", True)),
        "target_rgb_conditioned": bool(payload.get("target_rgb_conditioned", False)),
        "interpretation": "interop diagnostic with target RGB withheld but target depth conditioned",
    }
    (args.csv.parent / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
