#!/usr/bin/env python3
"""Scheduled alpha-scaling runner for the MVDiffusion depth generator (Phase D).

Reuses the deployed interop runner (scripts/run_mvdiffusion_depth.py) end to
end: same config, checkpoint migration, dataset, seeds, and image writing. The
only addition is an inference-time, weight-frozen residual-scale interface on
the 5 decoder-side CPBlocks (audit: MVDIFFUSION_RESIDUAL_CONTROL_AUDIT.md):

    y_alpha = (1 - alpha) * x + alpha * CPBlock(x)

alpha(point, t) = layer_multiplier(group(point)) * temporal_scale(t), with the
frozen temporal schedules (low=0.75, high=1.00, fixed mean=5/6, boundaries 1/3
and 2/3 of the denoising loop). Global conditions (G-*) omit the layer
multiplier. At alpha = 1 the interpolation is bitwise the original model
(0*x + 1*y), which the identity test verifies.

Classification PARTIAL: encoder-side CPBlocks are outside the transferred
decoder surface and stay at alpha = 1; the latent-concat depth channel and the
correspondence computation are never touched.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "final/round2/mvdiffusion/upstream"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_mvdiffusion_depth as base  # noqa: E402
from geotex.runtime import require_cuda  # noqa: E402

# Frozen schedule constants (identical to the MV-Adapter second-backbone freeze)
LOW, HIGH = 0.75, 1.00
FIXED_MEAN = 5 / 6
BOUNDARIES = (1 / 3, 2 / 3)

# Pre-registered layer mapping (audit section 5): normalized profile,
# weighted mean over the 5 scheduled points = 1.0 with point-count weights 2/1/2.
SOURCE_PROFILE = {"deep": 1.65, "middle": 1.65, "shallow": 0.58}
GROUP_COUNTS = {"deep": 2, "middle": 1, "shallow": 2}
_WEIGHTED_MEAN = (2 * 1.65 + 1 * 1.65 + 2 * 0.58) / 5  # = 1.222
LAYER_MULTIPLIERS = {
    "deep": SOURCE_PROFILE["deep"] / _WEIGHTED_MEAN,      # 1.3502458265122749
    "middle": SOURCE_PROFILE["middle"] / _WEIGHTED_MEAN,  # 1.3502458265122749
    "shallow": SOURCE_PROFILE["shallow"] / _WEIGHTED_MEAN,  # 0.4746317504091673
}
SCHEDULED_GROUPS = {
    "cp_blocks_mid": "deep",
    "cp_blocks_decoder.0": "deep",
    "cp_blocks_decoder.1": "middle",
    "cp_blocks_decoder.2": "shallow",
    "cp_blocks_decoder.3": "shallow",
}

CONDITIONS = {
    # name: (mode, schedule)  — mode "global" omits layer multipliers
    "G-FL": ("global", "FIXED_LOW"),
    "G-LHL": ("global", "LHL"),
    "G-LLH": ("global", "LLH"),
    "L-FIX": ("layer", "FIXED_MEAN"),
    "L-LHL": ("layer", "LHL"),
    "L-LLH": ("layer", "LLH"),
    "IDENTITY": ("global", "ONE"),
}


def temporal_scale(schedule: str, progress: float) -> float:
    if schedule == "ONE":
        return 1.0
    if schedule == "FIXED_MEAN":
        return FIXED_MEAN
    if schedule == "FIXED_LOW":
        return LOW
    early, late = BOUNDARIES
    stage = 0 if progress < early else 1 if progress < late else 2
    pattern = {"LHL": "LHL", "LLH": "LLH"}[schedule]
    return HIGH if pattern[stage] == "H" else LOW


def apply_alpha_interface(model, condition: str, strict_identity: bool) -> dict:
    """Wrap the 5 scheduled decoder-side CPBlocks with the convex interpolation."""
    mode, schedule = CONDITIONS[condition]
    mv = model.mv_base_model
    holder = {"alphas": {name: 1.0 for name in SCHEDULED_GROUPS},
              "first_step_alphas": None, "patched": []}

    def wrap(name: str, module):
        original = module.forward

        def forward(x, reso, cp_package, m):
            y = original(x, reso, cp_package, m)
            alpha = holder["alphas"][name]
            if alpha == 1.0 and not strict_identity:
                return y
            return (1.0 - alpha) * x + alpha * y

        module.forward = forward
        holder["patched"].append(name)

    for name, group in SCHEDULED_GROUPS.items():
        if name == "cp_blocks_mid":
            wrap(name, mv.cp_blocks_mid)
        else:
            index = int(name.split(".")[-1])
            wrap(name, mv.cp_blocks_decoder[index])

    timesteps_cache = {}

    original_forward = mv.forward

    def forward_with_schedule(latents_lr, timestep, prompt_embd, meta):
        t_values = timestep.reshape(-1).tolist()
        key = (len(t_values), int(t_values[0]))
        if key not in timesteps_cache:
            raise RuntimeError(
                f"timestep {t_values[0]} not registered; the runner must register "
                "the scheduler timestep list before inference"
            )
        step_index, num_steps = timesteps_cache[key]
        progress = step_index / max(num_steps - 1, 1)
        temporal = temporal_scale(schedule, progress)
        for name, group in SCHEDULED_GROUPS.items():
            layer_mult = LAYER_MULTIPLIERS[group] if mode == "layer" else 1.0
            holder["alphas"][name] = layer_mult * temporal
        if holder["first_step_alphas"] is None:
            holder["first_step_alphas"] = dict(holder["alphas"])
        return original_forward(latents_lr, timestep, prompt_embd, meta)

    mv.forward = forward_with_schedule

    original_set_timesteps = model.scheduler.set_timesteps

    def set_timesteps_registered(num_inference_steps, *args, **kwargs):
        original_set_timesteps(num_inference_steps, *args, **kwargs)
        timesteps_cache.clear()
        steps = model.scheduler.timesteps
        for i, t in enumerate(steps):
            for m_value in range(1, 64):
                timesteps_cache[(m_value, int(t))] = (i, len(steps))

    model.scheduler.set_timesteps = set_timesteps_registered
    holder["mode"] = mode
    holder["schedule"] = schedule
    return holder


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path,
                        default=base.UPSTREAM / "configs/depth_generation_fix_frames.yaml")
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--object", dest="object_ids", action="append", default=None)
    parser.add_argument("--strict-identity", action="store_true",
                        help="disable the alpha==1 shortcut so the interpolation "
                             "arithmetic itself is exercised (identity test)")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    device = require_cuda(args.device, "MVDiffusion scheduled generation")
    if not args.checkpoint.is_file():
        raise FileNotFoundError(args.checkpoint)

    data_payload = json.loads(args.data_manifest.read_text())
    objects = list(data_payload["objects"])
    by_id = {row["object"]: row for row in objects}
    selected = set(args.object_ids) if args.object_ids else None
    unknown = (selected or set()) - set(by_id)
    if unknown:
        raise ValueError(f"unknown exported objects: {sorted(unknown)}")
    if selected:
        objects = [row for row in objects if row["object"] in selected]

    config = base.load_config(args.config, args.data_root, args.steps)
    if args.model_id is not None:
        model_path = Path(args.model_id)
        config["model"]["model_id"] = (
            str(model_path.resolve()) if model_path.exists() else args.model_id
        )
    config["dataset"]["num_views"] = len(data_payload["view_ids"])
    base.set_seed(args.seed)
    dataset = base.Scannetdataset(config["dataset"], mode="val")
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=1, shuffle=False, num_workers=0, drop_last=False
    )
    model = base.DepthGenerator(config)
    checkpoint_load = base.load_checkpoint(model, args.checkpoint)
    model.to(device).eval()

    holder = apply_alpha_interface(model, args.condition, args.strict_identity)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    completed = []
    started = time.time()
    with torch.inference_mode():
        for batch_index, batch in enumerate(loader):
            scene_id = base.batch_scene_id(batch)
            if scene_id not in {row["object"] for row in objects}:
                continue
            out_dir = args.output_dir / scene_id
            if args.resume and (out_dir / "prediction_shape.json").is_file():
                completed.append(scene_id)
                continue
            base.set_seed(args.seed + batch_index)
            batch = base.move_batch(batch, device)
            images_pred = model.inference_gen(batch)
            images_pred = np.asarray(images_pred)
            if images_pred.ndim != 5 or images_pred.shape[1] != len(data_payload["view_ids"]):
                raise RuntimeError(f"unexpected prediction shape for {scene_id}: {images_pred.shape}")
            out_dir.mkdir(parents=True, exist_ok=True)
            for local_id, source_id in enumerate(data_payload["view_ids"]):
                Image.fromarray(images_pred[0, local_id]).save(
                    out_dir / f"view_{local_id:03d}_source_{source_id:03d}.png"
                )
            (out_dir / "prediction_shape.json").write_text(
                json.dumps({"shape": list(images_pred.shape)}, indent=2) + "\n"
            )
            completed.append(scene_id)
            print(json.dumps({"object": scene_id, "completed": len(completed),
                              "elapsed_sec": round(time.time() - started, 1)}), flush=True)

    missing = sorted({row["object"] for row in objects} - set(completed))
    if missing:
        raise RuntimeError(f"exported objects were not produced: {missing}")

    (args.output_dir / "run_config.json").write_text(json.dumps({
        "protocol": "mvdiffusion-scheduled-alpha-v1",
        "condition": args.condition,
        "condition_definition": {"mode": holder["mode"], "schedule": holder["schedule"]},
        "strict_identity": bool(args.strict_identity),
        "temporal_freeze": {"low": LOW, "high": HIGH, "fixed_mean": FIXED_MEAN,
                            "boundaries": list(BOUNDARIES)},
        "layer_multipliers": LAYER_MULTIPLIERS,
        "scheduled_groups": SCHEDULED_GROUPS,
        "first_step_alphas": holder["first_step_alphas"],
        "patched_modules": holder["patched"],
        "data_manifest": str(args.data_manifest.resolve()),
        "checkpoint": str(args.checkpoint.resolve()),
        "checkpoint_load": checkpoint_load,
        "config": config,
        "base_provenance": base.base_provenance(config["model"]["model_id"]),
        "device": str(device),
        "steps": args.steps,
        "seed": args.seed,
        "objects": completed,
        "runner_sha256": _sha(str(Path(__file__).resolve())),
    }, indent=2, default=str) + "\n")
    print(json.dumps({"status": "complete", "object_count": len(completed)}, indent=2))


def _sha(path: str) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
