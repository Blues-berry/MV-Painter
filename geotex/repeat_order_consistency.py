"""Small GPU-only repeat/reverse-order audit for the revised inference entrypoint.

The audit intentionally does not recompute the main table.  For two fixed
objects it reuses one prepared batch, geometry features, and initial latent,
then runs fixed-low and C3 in A order, B (reversed) order, and A order again.
It records hashes and max/mean absolute differences for the shared inputs and
the method outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf

from data_utils import collate_batch, prepare_batch
from eval_exploration import generate, load_model
from round2_main_eval import SCHEDULES


def tensor_hash(tensor: torch.Tensor | dict) -> str:
    """Hash a tensor or the deterministic key/tensor leaves of a feature dict."""
    if isinstance(tensor, dict):
        digest = hashlib.sha256()
        for key in sorted(tensor):
            digest.update(str(key).encode())
            digest.update(tensor_hash(tensor[key]).encode())
        return digest.hexdigest()
    data = tensor.detach().float().cpu().contiguous().numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def run_schedule(model, batch, device, geo_feats, latent, name: str, steps: int):
    spec = SCHEDULES[name]
    seed_all(42)
    return generate(
        model, batch, device, torch.float16,
        geo_feats, spec["scale"], steps, latent,
        timestep_schedule=spec["timestep_schedule"],
    ).detach().float().cpu()


def compare(a: torch.Tensor, b: torch.Tensor) -> dict[str, float | bool]:
    diff = (a - b).abs()
    return {"exact": bool(torch.equal(a, b)), "max_abs": float(diff.max()), "mean_abs": float(diff.mean())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--object-list-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=50)
    args = parser.parse_args()

    seed_all(42)
    device = torch.device(args.device)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(args.object_list_file.resolve())
    dataset = __import__("src.utils.train_util", fromlist=["instantiate_from_config"]).instantiate_from_config(validation)
    if getattr(dataset, "target_view_mode", None) != "unique6":
        raise RuntimeError("dataset did not instantiate with unique6 views")

    rows = []
    for object_idx in range(min(2, len(dataset))):
        seed_all(42 + object_idx)
        batch = collate_batch(dataset, object_idx, device)
        _, target, normal, depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
        geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_clean)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        torch.manual_seed(42)
        latent = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        shared = {
            "target": tensor_hash(target),
            "geo_input": tensor_hash(geo_input),
            "geo_features": tensor_hash(geo_feats),
            "initial_latent": tensor_hash(latent),
        }
        a_fixed = run_schedule(model, batch, device, geo_feats, latent, "fixed_low", args.steps)
        a_c3 = run_schedule(model, batch, device, geo_feats, latent, "c3", args.steps)
        b_c3 = run_schedule(model, batch, device, geo_feats, latent, "c3", args.steps)
        b_fixed = run_schedule(model, batch, device, geo_feats, latent, "fixed_low", args.steps)
        repeat_fixed = run_schedule(model, batch, device, geo_feats, latent, "fixed_low", args.steps)
        repeat_c3 = run_schedule(model, batch, device, geo_feats, latent, "c3", args.steps)
        rows.append({
            "object_index": object_idx,
            "object_id": f"obj_{object_idx:04d}",
            "shared_input_hashes": shared,
            "fixed_low_repeat": compare(a_fixed, repeat_fixed),
            "c3_repeat": compare(a_c3, repeat_c3),
            "fixed_low_order_reversal": compare(a_fixed, b_fixed),
            "c3_order_reversal": compare(a_c3, b_c3),
            "fixed_low_output_hash": tensor_hash(a_fixed),
            "c3_output_hash": tensor_hash(a_c3),
        })
        del batch, target, normal, depth, geo_input, mask, geo_clean, geo_feats, latent
        torch.cuda.empty_cache()

    result = {
        "protocol": "round2-repeat-reverse-order-v1",
        "config": str(args.config),
        "checkpoint": str(args.checkpoint),
        "object_list_file": str(args.object_list_file.resolve()),
        "steps": args.steps,
        "device": args.device,
        "schedules": ["fixed_low", "c3"],
        "rows": rows,
        "pass_criteria": "all exact flags true and max_abs <= 0.0 for repeated and reversed outputs",
        "passed": all(
            item[key]["exact"] and item[key]["max_abs"] == 0.0
            for item in rows
            for key in ("fixed_low_repeat", "c3_repeat", "fixed_low_order_reversal", "c3_order_reversal")
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
