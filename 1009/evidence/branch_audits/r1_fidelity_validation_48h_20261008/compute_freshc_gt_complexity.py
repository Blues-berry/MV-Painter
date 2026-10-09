#!/usr/bin/env python3
"""Compute GT-only complexity fields missing from the revision-era Fresh C CSVs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from recompute_paired_rgb_metrics import load_json, reconstruct_target, write_csv  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def gt_only_metrics(rgb: torch.Tensor, mask: torch.Tensor) -> dict[str, float]:
    """Mirror frozen geotex.metrics_extended GT-stat definitions on CPU."""
    import torch.nn.functional as F

    pred = rgb.unsqueeze(0).float()
    m = mask.unsqueeze(0).float()
    fg = m > 0.5

    pixel_std = pred.std(dim=1, keepdim=True)
    rgb_std = float(pixel_std[fg].mean().item())

    gray = pred.mean(dim=1, keepdim=True)
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=gray.dtype).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=gray.dtype).view(1, 1, 3, 3)
    gx = F.conv2d(gray, sobel_x, padding=1)
    gy = F.conv2d(gray, sobel_y, padding=1)
    grad = torch.sqrt(gx ** 2 + gy ** 2 + 1e-8)
    grad_mag = float(grad[fg].mean().item())

    lap_kernel = torch.tensor([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=gray.dtype).view(1, 1, 3, 3)
    lap = F.conv2d(gray, lap_kernel, padding=1)
    lap_var = float(lap[fg].var().item())

    masked = gray * m
    magnitude = torch.abs(torch.fft.fftshift(torch.fft.fft2(masked)))
    h, w = magnitude.shape[2:]
    cy, cx = h // 2, w // 2
    qh, qw = max(h // 4, 1), max(w // 4, 1)
    total = magnitude.sum()
    low = magnitude[:, :, max(cy - qh, 0):cy + qh, max(cx - qw, 0):cx + qw].sum()
    hf_energy = float((total - low).div(total + 1e-8).item())

    fg_pixels = pred.permute(0, 2, 3, 1)[m.squeeze(1) > 0.5]
    entropy = 0.0
    if fg_pixels.shape[0] >= 10:
        for channel in range(3):
            hist = torch.histc(fg_pixels[:, channel], bins=64, min=0, max=1)
            hist = hist / (hist.sum() + 1e-8)
            hist = hist[hist > 0]
            entropy += float((-(hist * torch.log2(hist + 1e-8)).sum()).item())
    color_entropy = entropy / 3.0

    return {
        "gt_fg_rgb_std": rgb_std,
        "gt_fg_grad_mag": grad_mag,
        "gt_fg_lap_var": lap_var,
        "gt_fg_hf_energy": hf_energy,
        "gt_fg_color_entropy": color_entropy,
        "gt_fg_coverage": float((m > 0.5).float().mean().item()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freshc-root", type=Path, default=Path("/4T/CXY/MV-Painter/1006/data/fresh_c"))
    ap.add_argument("--manifest", type=Path, default=Path("/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/FRESH_C_COHORT_MANIFEST.json"))
    ap.add_argument("--output", type=Path, default=HERE / "GT_ONLY_TEXTURE_METRICS_FRESHC.csv")
    args = ap.parse_args()
    torch.set_num_threads(4)
    manifest = load_json(args.manifest)
    metrics_source = Path(__file__).resolve().parents[3] / "geotex" / "metrics_extended.py"
    if not metrics_source.is_file():
        metrics_source = Path("/4T/CXY/MV-Painter/geotex/metrics_extended.py")
    rows = []
    objects = sorted(manifest["objects"], key=lambda x: int(x["object_index"]))
    for i, obj in enumerate(objects, 1):
        target, mask, views, reverse, source_digest = reconstruct_target(Path(obj["render_dir"]))
        gt_metrics = gt_only_metrics(target, mask)
        rows.append({
            "cohort": "FreshC",
            "uid": obj["uid"],
            "object_idx": obj["object_index"],
            "object_seed": obj["object_seed"],
            "target_view_ids": json.dumps(views),
            "reverse_view_rotation": reverse,
            "gt_render_dir": obj["render_dir"],
            "gt_selected_source_files_digest_sha256": source_digest,
            **gt_metrics,
        })
        if i % 50 == 0:
            print(f"GT-only Fresh C complexity computed: {i}/{len(objects)}", flush=True)
    write_csv(args.output, rows)
    print(json.dumps({
        "n": len(rows),
        "metric_definition_source": str(metrics_source),
        "metric_definition_source_sha256": sha256_file(metrics_source),
        "implementation": "geotex.metrics_extended GT-only definitions mirrored in this script; CPU float32 on reconstructed target panels",
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
