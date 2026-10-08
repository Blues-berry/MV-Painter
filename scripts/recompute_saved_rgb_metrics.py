#!/usr/bin/env python
"""Recompute the locked image metrics from the exact RGB PNG assets."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torchvision
from omegaconf import OmegaConf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
BASE = Path("/4T/CXY/MV-Painter")
CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
BASELINE_METHODS = ["no_adapter", "native_gfl", "native_gfh", "native_gc3", "gen_linear", "layer_llh"]
GATE_METHODS = ["c3_feature_gate", "linear_feature_gate"]
RUNNER_SHA = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
from data_utils import collate_batch, prepare_batch  # noqa: E402
from eval_exploration import compute_metrics, get_lpips_fn  # noqa: E402
from metrics import compute_edge_mask  # noqa: E402
from src.utils.train_util import instantiate_from_config  # noqa: E402


def load_grid(path: Path, device: torch.device) -> torch.Tensor:
    image = Image.open(path).convert("RGB")
    array = np.asarray(image, dtype=np.uint8).copy()
    return torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0).to(device).float() / 255.0


def build_dataset(sample: dict):
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(Path(sample["object_list"]).resolve())
    validation.params.root_dir_list = [str(Path(sample["data_root"]).resolve())]
    return instantiate_from_config(validation)


def main() -> None:
    freeze = json.loads((ARTIFACT / "SAMPLE_FREEZE.json").read_text())
    device = torch.device("cuda:1" if torch.cuda.is_available() and torch.cuda.device_count() > 1
                          else "cuda:0" if torch.cuda.is_available() else "cpu")
    lpips_fn = get_lpips_fn(device)
    if lpips_fn is None:
        raise RuntimeError("LPIPS is required for the locked secondary metrics but is unavailable")
    import lpips
    lpips_weights = Path(lpips.__file__).resolve().parent / "weights/v0.1/alex.pth"
    metric_script_sha = sha_file(Path(__file__).resolve())
    freeze_json_sha = sha_file(ARTIFACT / "SAMPLE_FREEZE.json")
    config_sha = sha_file(CONFIG)

    datasets = {}
    rows = []
    for sample in freeze["samples"]:
        source = sample["source"]
        if source not in datasets:
            datasets[source] = build_dataset(sample)
        seed = int(sample["object_seed"])
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        batch = collate_batch(datasets[source], int(sample["object_idx"]), "cpu")
        _, _, _, real_depth, _, mask = prepare_batch(batch, 256, "cpu")
        mask_path = ARTIFACT / "masks" / f"{sample['sample_id']}.png"
        mask_png = np.asarray(Image.open(mask_path).convert("L")) > 127
        batch_mask = mask[0, 0].numpy() > 0.5
        if batch_mask.shape != mask_png.shape or not np.array_equal(batch_mask, mask_png):
            raise RuntimeError(f"frozen mask differs from reloaded dataset mask: {sample['sample_id']}")
        edge = compute_edge_mask(real_depth.float(), threshold=0.1).to(device)
        mask = mask.to(device)

        methods = list(BASELINE_METHODS)
        if (ARTIFACT / "runs/feature_ratio_gate/predictions").is_dir():
            methods.extend(GATE_METHODS)
        for method in methods:
            sample_dir = ARTIFACT / "raw_rgb" / sample["sample_id"]
            if method in BASELINE_METHODS:
                prediction_path = sample_dir / f"{method}.png"
            else:
                prediction_path = (ARTIFACT / "runs/feature_ratio_gate/predictions" /
                                   method / f"{sample['uid']}.png")
            reference_path = sample_dir / "reference.png"
            prediction = load_grid(prediction_path, device)
            target = load_grid(reference_path, device)
            values = compute_metrics(prediction, target, mask, edge, lpips_fn, device)
            rows.append({
                "sample_id": sample["sample_id"],
                "uid": sample["uid"],
                "object_idx": sample.get("object_idx", ""),
                "object_seed": sample.get("object_seed", ""),
                "method_key": method,
                "fg_psnr": values["fg_psnr"],
                "fg_lpips": values["fg_lpips"],
                "edge_ssim": values["edge_ssim"],
                "prediction_png": str(prediction_path),
                "prediction_sha256": sha_file(prediction_path),
                "reference_png": str(reference_path),
                "reference_sha256": sha_file(reference_path),
                "mask_png": str(mask_path),
                "mask_sha256": sha_file(mask_path),
                "sample_freeze_json_sha256": freeze_json_sha,
                "config_sha256": config_sha,
                "runner_sha256": RUNNER_SHA,
                "metric_script_sha256": metric_script_sha,
                "metric_runtime_python": sys.version.split()[0],
                "metric_runtime_torch": torch.__version__,
                "metric_runtime_torchvision": torchvision.__version__,
                "metric_runtime_device": str(device),
                "metric_runtime_platform": platform.platform(),
                "lpips_weights_sha256": sha_file(lpips_weights),
                "source_assets": "saved_rgb_pngs; foreground/edge masks from frozen validation inputs",
            })

    output = ARTIFACT / "logs/RGB_RELOADED_METRICS.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} paired RGB metric rows to {output} on {device}")


if __name__ == "__main__":
    main()
