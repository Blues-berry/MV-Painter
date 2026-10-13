#!/usr/bin/env python3
"""Score the second fixed-mean candidate with the frozen per-view path."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from PIL import Image


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
ALT_RUN = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research/generation_equal_cost_b0_seed43")
WORKTREE = Path("/4T/tmp/MV-Painter-counterfactual")
FINAL_CODE = Path("/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/final_code")
CONFIG = Path("/4T/CXY/MV-Painter-1010/1010/experiments/frozen_sources/clean_holdout.yaml")
OBJECT_LIST = Path("/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/bake_uids.txt")
DATA_ROOT = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/renders")
SELECTED_INDICES = (0, 1, 2, 3, 4, 7)
CONDITION = "counterfactual_b0"

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
    device = torch.device("cuda:0")
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    validation.params.root_dir_list = [str(DATA_ROOT.resolve())]
    dataset = instantiate_from_config(validation)
    uids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    if len(dataset) != len(uids):
        raise RuntimeError("dataset/object-list identity mismatch")
    lpips_fn = generation_metrics.get_lpips_fn(device)
    metric_impl = load_metric_implementations()
    original_rows = json.loads((ROOT / "generation/rows_shard0.json").read_text())
    alternate_rows = json.loads((ALT_RUN / "rows_shard0.json").read_text())
    base = {(int(r["object_idx"]), r["condition"]): r for r in original_rows}
    alt = {(int(r["object_idx"]), r["condition"]): r for r in alternate_rows}

    result_rows = []
    for index in SELECTED_INDICES:
        uid = uids[index]
        row0 = base[(index, "counterfactual_b0")]
        row43 = alt[(index, CONDITION)]
        if row0["object_uid"] != uid or row43["object_uid"] != uid:
            raise RuntimeError(f"object index/UID mismatch for {index}")
        hashes0, hashes43 = row0["input_hashes"], row43["input_hashes"]
        for key in set(hashes0) - {"init_latent"}:
            if hashes0[key] != hashes43[key]:
                raise RuntimeError(f"non-latent input changed for {uid}: {key}")
        if hashes0["init_latent"] == hashes43["init_latent"]:
            raise RuntimeError(f"alternate seed did not change latent for {uid}")

        batch = collate_batch(dataset, index, "cpu")
        _, target, _, _, _, mask = prepare_batch(batch, int(config.model.params.img_size), "cpu")
        target, mask = target.float(), mask.float()
        panel_path = ALT_RUN / "predictions" / CONDITION / f"{uid}.png"
        panel = np.asarray(Image.open(panel_path).convert("RGB"), dtype=np.float32) / 255.0
        if panel.shape != (768, 512, 3):
            raise RuntimeError(f"unexpected saved panel shape {panel.shape}: {panel_path}")

        for slot in range(6):
            tile_row, tile_col = divmod(slot, 2)
            tile = panel[tile_row * 256:(tile_row + 1) * 256, tile_col * 256:(tile_col + 1) * 256]
            pred = torch.from_numpy(tile.copy()).permute(2, 0, 1).unsqueeze(0).to(device)
            gt = target[:, :, tile_row * 256:(tile_row + 1) * 256, tile_col * 256:(tile_col + 1) * 256].to(device)
            fg = (mask[:, :, tile_row * 256:(tile_row + 1) * 256, tile_col * 256:(tile_col + 1) * 256] > 0.5).float().to(device)
            foreground = fg.expand_as(pred) > 0.5
            mae = float((pred - gt).abs()[foreground].mean().item())
            ciede = metric_impl["masked_ciede2000"](
                tile, gt[0].permute(1, 2, 0).cpu().numpy(), fg[0, 0].cpu().numpy(), erosion_radius=1
            )
            result_rows.append({
                "object_idx": index,
                "object_uid": uid,
                "condition": "fixed_mean_latent43",
                "slot": slot,
                "role": "reference" if slot == 0 else "nonreference",
                "reference_rgb_mae": mae,
                "reference_ciede2000": float(ciede),
                "fg_psnr": float(generation_metrics.compute_psnr(pred, gt, fg)),
                "fg_lpips": float(generation_metrics.compute_lpips(pred, gt, fg, lpips_fn=lpips_fn, device=device)),
                "fg_ssim": float(generation_metrics.compute_ssim(pred, gt, fg)),
                "panel_path": str(panel_path),
                "panel_sha256": sha256(panel_path),
                "latent_sha256": hashes43["init_latent"],
            })
        print(f"scored {uid}", flush=True)

    output = ALT_RUN / "GENERATION_VIEW_METRICS.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result_rows[0]))
        writer.writeheader()
        writer.writerows(result_rows)
    metadata = {
        "status": "COMPLETE",
        "objects_as_analysis_units": len(SELECTED_INDICES),
        "views_per_object": 6,
        "alternate_latent_seed": 43,
        "paired_fixed_mean_input_hashes_equal_except_init_latent": True,
        "generation_call_count": 6,
        "elapsed_seconds": time.time() - started,
        "metric_csv_sha256": sha256(output),
        "ground_truth_use": "offline source and generated-view evaluation only; no control parameter choice",
    }
    (ALT_RUN / "GENERATION_VIEW_METRICS_MANIFEST.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
