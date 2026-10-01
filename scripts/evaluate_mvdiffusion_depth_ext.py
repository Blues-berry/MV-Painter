#!/usr/bin/env python3
"""Extended MVDiffusion evaluator: unifies the second-backbone metric set.

Adds FG-LPIPS, CIEDE2000 and GT-relative texture error to the interop
evaluator, reusing the exact geotex functions used by the MV-Adapter runner
(masked_ciede2000, variation_diagnostics/texture_stat_errors, LPIPS). All
columns keep the interop_ prefix; absolute cross-backbone pooling stays
forbidden. Metrics unavailable in a given run are left as NaN, never faked.
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

from geotex.metrics.image_metrics import compute_lpips, compute_psnr, compute_ssim, get_lpips_fn  # noqa: E402
from geotex.round2_texture import masked_ciede2000, texture_stat_errors, variation_diagnostics  # noqa: E402
from scripts.evaluate_mvdiffusion_depth import read_target  # noqa: E402


def edge_mask(mask: np.ndarray) -> np.ndarray:
    binary = (mask > 0.5).astype(np.uint8)
    dilated = cv2.dilate(binary, np.ones((3, 3), np.uint8)) > 0
    eroded = cv2.erode(binary, np.ones((3, 3), np.uint8)) > 0
    edge = dilated & ~eroded
    return edge if edge.any() else binary.astype(bool)


def view_metrics(pred_path: Path, gt_path: Path, lpips_fn, device: str) -> dict[str, float]:
    pred = np.asarray(Image.open(pred_path).convert("RGB"), dtype=np.float32) / 255.0
    height, width = pred.shape[:2]
    target, mask = read_target(gt_path, (width, height))
    mask_t = torch.from_numpy(mask[None, None]).float()
    pred_t = torch.from_numpy(pred.transpose(2, 0, 1)[None]).float()
    target_t = torch.from_numpy(target.transpose(2, 0, 1)[None]).float()
    edge_t = torch.from_numpy(edge_mask(mask).astype(np.float32)[None, None])
    lpips_value = compute_lpips(pred_t, target_t, mask_t, lpips_fn=lpips_fn, device=device)
    # CIEDE2000 and texture statistics follow the MV-Adapter runner semantics:
    # a binarized foreground mask (alpha > 0.5) with erosion, while the legacy
    # interop PSNR/SSIM keep the original continuous-mask behavior so R0 stays
    # byte-comparable with the archived CSV.
    binary_mask = (mask > 0.5).astype(np.float32)
    # Views whose eroded foreground is empty have undefined CIEDE2000 / texture
    # statistics; they are reported as NaN and excluded by nanmean aggregation
    # (never faked), e.g. obj_0029's near-empty GT foreground.
    eroded = cv2.erode((binary_mask > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    if eroded.any():
        pred_stats = variation_diagnostics(pred, binary_mask)
        gt_stats = variation_diagnostics(target, binary_mask)
        errors = texture_stat_errors(pred_stats, gt_stats)["symmetric_log_error"]
        ciede = float(masked_ciede2000(pred, target, binary_mask, erosion_radius=1))
        texture = float(np.mean(list(errors.values())))
    else:
        ciede = float("nan")
        texture = float("nan")
    return {
        "psnr": float(compute_psnr(pred_t, target_t, mask_t)),
        "fg_ssim": float(compute_ssim(pred_t, target_t, mask_t)),
        "edge_ssim": float(compute_ssim(pred_t, target_t, edge_t)),
        "fg_lpips": float(lpips_value) if lpips_value is not None else float("nan"),
        "ciede2000": ciede,
        "gt_relative_texture_error": texture,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--object", dest="object_ids", action="append", default=None)
    args = parser.parse_args()

    payload = json.loads(args.data_manifest.read_text())
    selected = set(args.object_ids) if args.object_ids else None
    rows = [row for row in payload["objects"] if selected is None or row["object"] in selected]
    if not rows:
        raise ValueError("no objects selected")

    device = args.device if torch.cuda.is_available() else "cpu"
    lpips_fn = get_lpips_fn(device)

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
            per_view.append(view_metrics(pred_path, gt_path, lpips_fn, device))
        result_rows.append(
            {
                "object": row["object"],
                "source_uid": row.get("source_uid", ""),
                "target_view_count": len(per_view),
                "interop_psnr": float(np.mean([v["psnr"] for v in per_view])),
                "interop_fg_ssim": float(np.mean([v["fg_ssim"] for v in per_view])),
                "interop_edge_ssim": float(np.mean([v["edge_ssim"] for v in per_view])),
                "interop_fg_lpips": float(np.nanmean([v["fg_lpips"] for v in per_view])),
                "interop_ciede2000": float(np.nanmean([v["ciede2000"] for v in per_view])),
                "interop_gt_relative_texture_error": float(
                    np.nanmean([v["gt_relative_texture_error"] for v in per_view])
                ),
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
            field: float(np.nanmean([row[field] for row in result_rows]))
            for field in fields[3:9]
        },
        "csv": str(args.csv.resolve()),
        "absolute_score_pooling": "forbidden",
        "target_depth_conditioned": bool(payload.get("target_depth_conditioned", True)),
        "interpretation": "interop diagnostic with target RGB withheld but target depth conditioned",
    }
    (args.csv.parent / "summary_ext.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
