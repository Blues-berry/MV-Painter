#!/usr/bin/env python3
"""Score saved six-view panels per tile with the frozen GeoTex metrics."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from PIL import Image


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
WORKTREE = Path("/4T/tmp/MV-Painter-counterfactual")
FINAL_CODE = Path(
    "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/final_code"
)
CONFIG = Path(
    "/4T/CXY/MV-Painter-1010/1010/experiments/frozen_sources/clean_holdout.yaml"
)
CHECKPOINT_SHA256 = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
OBJECT_LIST = Path(
    "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/bake_uids.txt"
)
DATA_ROOT = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/renders")
CONDITIONS = ("counterfactual_b0", "counterfactual_bplus", "counterfactual_bminus")
SELECTED_INDICES = (0, 1, 2, 3, 4, 7)

sys.path[:0] = [str(FINAL_CODE), str(WORKTREE), str(WORKTREE / "geotex"), str(WORKTREE / "MVPainter")]
import geotex.eval_exploration as generation_metrics  # noqa: E402
from data_utils import collate_batch, prepare_batch  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402
from evaluate_fresh_c_native_egl import load_metric_implementations  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    started = time.time()
    device = torch.device(os.environ.get("MVP_METRIC_DEVICE", "cuda:0"))
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    validation.params.root_dir_list = [str(DATA_ROOT.resolve())]
    dataset = instantiate_from_config(validation)
    uids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    if len(dataset) != len(uids):
        raise RuntimeError(f"dataset/list length mismatch: {len(dataset)} vs {len(uids)}")

    metric_impl = load_metric_implementations()
    lpips_fn = generation_metrics.get_lpips_fn(device)
    if lpips_fn is None:
        raise RuntimeError("LPIPS is unavailable; refusing to produce incomplete per-view metrics")
    all_rows = []
    generation = ROOT / "generation"
    bake_handoff = json.loads(Path(
        "/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/"
        "bake_matrix_v2/BAKE_INPUT_HANDOFF_V3.json"
    ).read_text())
    frozen_records = {row["object"]: row for row in bake_handoff["objects"]}
    rows = json.loads((generation / "rows_shard0.json").read_text())
    by_key = {(int(row["object_idx"]), row["condition"]): row for row in rows}

    for index in SELECTED_INDICES:
        uid = uids[index]
        batch = collate_batch(dataset, index, "cpu")
        _, target, _, _, _, mask = prepare_batch(batch, int(config.model.params.img_size), "cpu")
        target = target.float()
        mask = mask.float()
        expected_hashes = None
        for condition in CONDITIONS:
            run_row = by_key[(index, condition)]
            if run_row["object_uid"] != uid:
                raise RuntimeError(f"object list order mismatch at index {index}")
            if expected_hashes is None:
                expected_hashes = run_row["input_hashes"]
            elif run_row["input_hashes"] != expected_hashes:
                raise RuntimeError(f"shared-input hash mismatch for {uid}")

            panel_path = generation / "predictions" / condition / f"{uid}.png"
            panel = np.asarray(Image.open(panel_path).convert("RGB"), dtype=np.float32) / 255.0
            if panel.shape != (768, 512, 3):
                raise RuntimeError(f"unexpected panel shape for {condition}/{uid}: {panel.shape}")
            for slot in range(6):
                y, x = divmod(slot, 2)
                tile = panel[y * 256:(y + 1) * 256, x * 256:(x + 1) * 256]
                pred = torch.from_numpy(tile.copy()).permute(2, 0, 1).unsqueeze(0).to(device)
                gt = target[:, :, y * 256:(y + 1) * 256, x * 256:(x + 1) * 256].to(device)
                fg = (mask[:, :, y * 256:(y + 1) * 256, x * 256:(x + 1) * 256] > 0.5).float().to(device)
                fg_rgb = fg.expand_as(pred) > 0.5
                rgb_mae = float((pred - gt).abs()[fg_rgb].mean().item()) if fg_rgb.any() else float("nan")
                gt_rgb = gt[0].permute(1, 2, 0).detach().cpu().numpy()
                ciede = float(metric_impl["masked_ciede2000"](
                    tile, gt_rgb, fg[0, 0].detach().cpu().numpy(), erosion_radius=1
                ))
                values = {
                    "fg_rgb_mae": rgb_mae,
                    "ciede2000": ciede,
                    "fg_psnr": float(generation_metrics.compute_psnr(pred, gt, fg)),
                    "fg_lpips": float(generation_metrics.compute_lpips(
                        pred, gt, fg, lpips_fn=lpips_fn, device=device
                    )),
                    "fg_ssim": float(generation_metrics.compute_ssim(pred, gt, fg)),
                }
                reference_raw_camera = next(
                    int(mapping["raw_view_index"])
                    for mapping in frozen_records[uid]["target_view_mapping"]
                    if int(mapping["slot"]) == 0
                )
                all_rows.append({
                    "object_idx": index,
                    "object_uid": uid,
                    "condition": condition,
                    "slot": slot,
                    "role": "reference" if slot == 0 else "nonreference",
                    "reference_raw_camera": reference_raw_camera,
                    "output_path": str(panel_path),
                    "output_sha256": sha256(panel_path),
                    **values,
                })
        print(f"scored {uid}", flush=True)

    output = ROOT / "generation" / "GENERATION_VIEW_METRICS.csv"
    fields = list(all_rows[0])
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    metadata = {
        "status": "COMPLETE",
        "elapsed_seconds": time.time() - started,
        "objects_as_analysis_units": len(SELECTED_INDICES),
        "conditions": list(CONDITIONS),
        "views_per_object_condition": 6,
        "metric_source_hashes": metric_impl["source_hashes"],
        "config_sha256": sha256(CONFIG),
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "metric_csv_sha256": sha256(output),
        "reference_rgb_mae": "foreground masked mean absolute RGB error in [0,1]",
        "ciede2000": "frozen masked CIEDE2000 implementation, erosion_radius=1",
        "ground_truth_use": "metrics only; no condition selection or control parameter choice",
    }
    (generation / "GENERATION_VIEW_METRICS_MANIFEST.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
