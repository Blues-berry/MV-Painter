"""Shared-input ablation for layer-wise stage-aware adapter scaling.

Each object is loaded and preprocessed once. Every schedule then reuses the
same batch, geometry features, and initial latent; the generation seed is reset
before each method so condition-VAE sampling is also paired. This is a
development ablation and does not overwrite the formal clean-v2 tables.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

import eval_exploration as ee
import explore_contradiction as exp
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from src.utils.train_util import instantiate_from_config


METHODS = (
    "fixed_low",
    "c3_lhl",
    "layer_fixed_low",
    "layer_fixed_mean",
    "layer_lhl",
    "layer_llh",
)


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def stage(progress: float, early: float, middle: float, late: float) -> float:
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def method_schedule(name: str, progress: float) -> float | dict[str, float]:
    if name == "fixed_low":
        return 1.25
    if name == "c3_lhl":
        return stage(progress, 1.25, 2.50, 1.25)
    if name == "layer_fixed_low":
        return {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
    if name == "layer_fixed_mean":
        # Exact means under the 17/16/17 partition used by the runner.
        return {"deep": 1.65, "middle": 1.65, "shallow": 0.58}
    if name == "layer_lhl":
        return {
            "deep": stage(progress, 1.25, 2.50, 1.25),
            "middle": stage(progress, 1.25, 2.50, 1.25),
            "shallow": stage(progress, 0.50, 0.75, 0.50),
        }
    if name == "layer_llh":
        return {
            "deep": stage(progress, 1.25, 1.25, 2.50),
            "middle": stage(progress, 1.25, 1.25, 2.50),
            "shallow": stage(progress, 0.50, 0.50, 0.75),
        }
    raise KeyError(name)


def output_row(method: str, object_idx: int, seed: int, metrics: dict[str, float], elapsed: float) -> dict[str, object]:
    return {"method": method, "object_idx": object_idx, "seed": seed, "elapsed_sec": elapsed, **metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--object-list-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--num-objects", type=int, default=24)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for method in METHODS:
        (args.output_dir / "predictions" / method).mkdir(parents=True, exist_ok=True)
    rows_path = args.output_dir / "per_object_metrics.csv"
    existing = []
    if rows_path.exists():
        with rows_path.open(newline="") as handle:
            existing = list(csv.DictReader(handle))
    completed = {(row["method"], int(row["object_idx"]), int(row["seed"])) for row in existing}

    device = torch.device(args.device)
    dtype = torch.float16
    seed_all(args.seed)
    model = ee.load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(args.object_list_file.resolve())
    dataset = instantiate_from_config(validation)
    if getattr(dataset, "target_view_mode", None) != "unique6":
        raise RuntimeError("dataset did not instantiate with unique6 views")
    lpips_fn = ee.get_lpips_fn(device)
    num_objects = min(args.num_objects, len(dataset))

    print(f"shared-input ablation: objects={num_objects}, seed={args.seed}, methods={METHODS}", flush=True)
    for object_idx in range(num_objects):
        key_prefix = [(method, object_idx, args.seed) for method in METHODS]
        if all(key in completed for key in key_prefix):
            continue
        object_seed = args.seed + object_idx
        seed_all(object_seed)
        batch = collate_batch(dataset, object_idx, device)
        _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        edge = compute_edge_mask(real_depth.float(), threshold=0.1)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(object_seed)
        shared_latent = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)

        for method in METHODS:
            if (method, object_idx, args.seed) in completed:
                continue
            # generate_with_schedule samples the condition VAE internally.
            # Resetting here pairs that stochastic path across methods.
            torch.manual_seed(object_seed)
            residual_log = {}
            started = time.time()
            prediction = exp.generate_with_schedule(
                model, batch, device, dtype, geo_feats,
                lambda progress, name=method: method_schedule(name, progress),
                args.steps, shared_latent.clone(), residual_log,
            )
            elapsed = time.time() - started
            metrics = ee.compute_metrics(prediction, target, mask, edge, lpips_fn, device)
            row = output_row(method, object_idx, args.seed, metrics, elapsed)
            existing.append(row)
            save_image(prediction, args.output_dir / "predictions" / method / f"obj_{object_idx:04d}.png")
            if object_idx == 0 and method == METHODS[0]:
                save_image(target, args.output_dir / "predictions" / "ground_truth_obj_0000.png")
            print(f"[{object_idx + 1}/{num_objects}] {method} fg_lpips={metrics['fg_lpips']:.6f} fg_psnr={metrics['fg_psnr']:.4f}", flush=True)
            del prediction
            torch.cuda.empty_cache()

        with rows_path.open("w", newline="") as handle:
            fields = list(existing[0])
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(existing)
        del batch, target, real_depth, geo_input, mask, geo_clean, geo_feats, edge, shared_latent
        torch.cuda.empty_cache()

    manifest = {
        "protocol": "layer-lhl-shared-input-ablation-v1",
        "checkpoint": str(args.checkpoint),
        "object_list_file": str(args.object_list_file.resolve()),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "steps": args.steps,
        "seed_argument": args.seed,
        "object_seed": "seed_argument + object_idx",
        "methods": list(METHODS),
        "layer_fixed_mean": {"deep": 1.65, "middle": 1.65, "shallow": 0.58},
        "layer_llh_definition": {
            "deep_middle": [1.25, 1.25, 2.50],
            "shallow": [0.50, 0.50, 0.75],
        },
        "shared_inputs": ["single collated batch", "geo features", "initial latent"],
        "condition_vae_seed_reset_per_method": True,
    }
    (args.output_dir / "evaluation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"saved {len(existing)} rows to {rows_path}", flush=True)


if __name__ == "__main__":
    main()
