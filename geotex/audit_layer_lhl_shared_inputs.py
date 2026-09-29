"""Record shared-input hashes for the layer-LHL development ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf

import eval_exploration as ee
from data_utils import collate_batch, prepare_batch
from src.utils.train_util import instantiate_from_config


def digest(value) -> str:
    if isinstance(value, dict):
        h = hashlib.sha256()
        for key in sorted(value):
            h.update(str(key).encode())
            h.update(digest(value[key]).encode())
        return h.hexdigest()
    return hashlib.sha256(value.detach().float().cpu().contiguous().numpy().tobytes()).hexdigest()


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--object-list-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    args = p.parse_args()
    device = torch.device(args.device)
    seed_all(42)
    model = ee.load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(args.object_list_file.resolve())
    dataset = instantiate_from_config(validation)
    rows = []
    for run_seed in args.seeds:
        for object_idx in range(min(24, len(dataset))):
            seed_all(run_seed + object_idx)
            batch = collate_batch(dataset, object_idx, device)
            _, target, _, _, geo_input, _ = prepare_batch(batch, model.img_size, device)
            geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            torch.manual_seed(run_seed + object_idx)
            latent = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
            rows.append({
                "seed": run_seed,
                "object_idx": object_idx,
                "object": f"obj_{object_idx:04d}",
                "object_seed": run_seed + object_idx,
                "target_hash": digest(target),
                "geo_input_hash": digest(geo_input),
                "geo_features_hash": digest(geo_feats),
                "initial_latent_hash": digest(latent),
            })
            del batch, target, geo_input, geo_clean, geo_feats, latent
            torch.cuda.empty_cache()
    result = {
        "protocol": "layer-lhl-shared-input-hash-v1",
        "config": str(args.config),
        "checkpoint": str(args.checkpoint),
        "object_list_file": str(args.object_list_file.resolve()),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "steps": 50,
        "rows": rows,
        "pairing_rule": "within each seed/object row, all six methods reuse the listed hashes; generation resets the object seed before each method",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {len(rows)} shared-input hash rows to {args.output}")


if __name__ == "__main__":
    main()
