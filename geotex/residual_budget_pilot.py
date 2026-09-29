"""Pilot a self-calibrated residual-budget controller.

The controller is deliberately test-time and input-only: a short C3 pass
measures the adapter residual energy for the current object, then the actual
pass allocates the same per-stage residual-energy budget while reacting to the
new residual magnitude.  The stability variant additionally gates corrections
whose direction is poorly aligned with the current hidden state.

This is a method pilot, not a paper result.  It reports the calibration pass,
the applied scales, and the same probes used by explore_contradiction.py so a
later holdout run can be audited without changing the main worktree.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import torch
import torch.nn.functional as F
from diffusers import EulerDiscreteScheduler
from torchvision.transforms import v2

sys.path.insert(0, os.path.dirname(__file__))
import explore_contradiction as ec
from mvpainter.model_unet_geotex import GeoTexResnetWrapper


def stage_name(progress):
    if progress < 1.0 / 3.0:
        return "early"
    if progress < 2.0 / 3.0:
        return "mid"
    return "late"


def schedule_value(name, progress):
    if name == "no_adapter":
        return 0.0
    if name == "fixed_low":
        return 1.25
    if name == "C3_TCAS":
        return 2.50 if stage_name(progress) == "mid" else 1.25
    # For 50 denoising steps, the thirds contain 17/16/17 steps.  Using
    # 2.426470588 in the 17-step high segment makes HLL/LLH have the same
    # total scale sum as C3's 16-step high segment (82.5 over 50 steps).
    if name == "HLL_eq":
        return 2.426470588 if stage_name(progress) == "early" else 1.25
    if name == "LLH_eq":
        return 2.426470588 if stage_name(progress) == "late" else 1.25
    raise ValueError(name)


class ResidualBudgetController:
    """Allocate an input-calibrated residual-energy budget at runtime."""

    def __init__(self, targets, variant):
        self.targets = targets
        self.variant = variant
        self.progress = 0.0
        self.scales = []
        self.raw_energy = []
        self.alignment = []

    def set_progress(self, progress):
        self.progress = float(progress)

    @staticmethod
    def _rms(x):
        return float(x.detach().float().pow(2).mean().sqrt().item())

    @staticmethod
    def _alignment(a, b):
        a = a.detach().float().flatten()
        b = b.detach().float().flatten()
        denom = a.norm() * b.norm() + 1e-8
        return float((a @ b / denom).item())

    def __call__(self, correction, hidden_states, geo_feat, module):
        depth = module.depth_group
        stage = stage_name(self.progress)
        raw = self._rms(correction)
        target = float(self.targets.get(depth, {}).get(stage, 0.0))
        # Equalize the *injected residual energy*, rather than normalize each
        # layer to a free-running scale.  The square-root dampening prevents a
        # single noisy step from swinging to the layer cap.
        scale = 0.0 if raw < 1e-8 else (max(target, 0.0) / raw) ** 0.75

        if self.variant == "trust":
            # Trust-region form: preserve the proven fixed-low floor and only
            # shrink an over-energetic C3 mid-stage intervention.  This avoids
            # the texture washout observed when unrestricted normalization
            # lowered late/early scales below fixed-low.
            base = schedule_value("C3_TCAS", self.progress)
            scale = min(max(scale, 1.25), base)

        align = self._alignment(correction, hidden_states)
        if self.variant == "stable":
            # A negative/weak direction agreement is treated as low confidence
            # but never hard-disabled; this keeps the controller measurable.
            gate = 0.60 + 0.40 * float(torch.sigmoid(torch.tensor(5.0 * (align - 0.05))))
            scale *= gate

        scale = min(max(scale, 0.0), float(module._max_scale))
        self.scales.append({"depth": depth, "stage": stage, "scale": scale})
        self.raw_energy.append({"depth": depth, "stage": stage, "raw_rms": raw})
        self.alignment.append({"depth": depth, "stage": stage, "cosine": align})
        return scale


@torch.no_grad()
def generate(model, batch, device, weight_dtype, geo_feats, num_steps,
             init_latents, schedule_name=None, controller=None):
    """Generate once, optionally using the runtime controller."""
    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size,
                                     interpolation=3, antialias=True).clamp(0, 1)
    bsz = cond_imgs.shape[0]
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(bsz, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    prompt_embeds = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype) + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
    added = model.pipeline.get_added_cond_kwargs_train(bsz, is_drop=False)
    added = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
             for k, v in added.items()}
    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)
    latents = init_latents * scheduler.init_noise_sigma
    sigmas = scheduler.sigmas.cpu().numpy()
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)
    logs = {"residual": {}, "raw": {}, "controller": []}
    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            progress = step_idx / max(num_steps - 1, 1)
            if controller is not None:
                controller.set_progress(progress)
            for module in model.unet.modules():
                if isinstance(module, GeoTexResnetWrapper):
                    if controller is not None:
                        module._runtime_scale_controller = controller
                    else:
                        module._adapter_scale = schedule_value(schedule_name, progress)
            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
            raw_step, scaled_step = {}, {}
            for module in model.unet.modules():
                if not isinstance(module, GeoTexResnetWrapper):
                    continue
                raw = module._last_raw_correction
                scaled = module._last_correction
                if raw is not None:
                    raw_step[module.adapter_idx] = {
                        "depth": module.depth_group,
                        "rms": float(raw.detach().float().pow(2).mean().sqrt().item()),
                    }
                if scaled is not None:
                    scaled_f = scaled.detach().float()
                    if controller is not None:
                        applied_scale = getattr(module, "_runtime_effective_scale", 0.0)
                    else:
                        applied_scale = min(float(getattr(module, "_adapter_scale", 0.0)),
                                            float(module._max_scale))
                    scaled_step[module.adapter_idx] = {
                        "depth": module.depth_group,
                        "mean_abs": float(scaled_f.abs().mean().item()),
                        "rms": float(scaled_f.pow(2).mean().sqrt().item()),
                        "scale": float(applied_scale),
                    }
            logs["raw"][step_idx] = raw_step
            logs["residual"][step_idx] = scaled_step
        if controller is not None:
            logs["controller"] = {
                "scales": controller.scales,
                "raw_energy": controller.raw_energy,
                "alignment": controller.alignment,
            }
    finally:
        model._clear_geo_feats_on_wrappers()
        for module in model.unet.modules():
            if isinstance(module, GeoTexResnetWrapper):
                module._runtime_scale_controller = None
                if hasattr(module, "_adapter_scale"):
                    delattr(module, "_adapter_scale")
                if hasattr(module, "_runtime_effective_scale"):
                    delattr(module, "_runtime_effective_scale")
    decoded = model.pipeline.vae.decode(
        ec.unscale_latents(latents) / model.pipeline.vae.config.scaling_factor,
        return_dict=False)[0]
    return (ec.unscale_image(decoded) * 0.5 + 0.5).clamp(0, 1), logs


def calibrate_targets(logs, num_steps):
    """Convert a C3 raw-residual trace into per-depth/stage budgets."""
    sums, counts = {}, {}
    for step, entries in logs["raw"].items():
        progress = int(step) / max(num_steps - 1, 1)
        stage = stage_name(progress)
        for entry in entries.values():
            depth = entry["depth"]
            key = (depth, stage)
            sums[key] = sums.get(key, 0.0) + entry["rms"] * schedule_value("C3_TCAS", progress)
            counts[key] = counts.get(key, 0) + 1
    targets = {d: {} for d in ("deep", "middle", "shallow")}
    for (depth, stage), total in sums.items():
        targets[depth][stage] = total / max(counts[(depth, stage)], 1)
    return targets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--num_objects", type=int, default=2)
    ap.add_argument("--num_steps", type=int, default=20)
    ap.add_argument("--save_maps", type=int, default=1)
    ap.add_argument("--methods", default=None,
                    help="comma-separated subset; default runs all baselines and controllers")
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device(args.device)
    dtype = torch.float16
    model, config = ec.load_model(args.config, args.checkpoint, device)
    dataset = ec.instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    methods = ["no_adapter", "fixed_low", "C3_TCAS", "HLL_eq", "LLH_eq",
               "RB_TCAS", "SRB_TCAS", "TRB_TCAS"]
    if args.methods:
        requested = [m.strip() for m in args.methods.split(",") if m.strip()]
        unknown = sorted(set(requested) - set(methods))
        if unknown:
            raise ValueError(f"Unknown methods: {unknown}; choices={methods}")
        methods = requested
    results = {m: [] for m in methods}
    trace = {m: [] for m in methods}

    for obj_idx in range(num_objects):
        batch = ec.collate_batch(dataset, obj_idx, device)
        _, target, _, _, geo_input, mask = ec.prepare_batch(batch, model.img_size, device)
        geo_input = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input)
        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)

        # Input-only calibration pass. Its output is discarded; it supplies a
        # per-object residual-energy budget for the adaptive method.
        _, calib_log = generate(model, batch, device, dtype, geo_feats,
                                args.num_steps, init.clone(), schedule_name="C3_TCAS")
        targets = calibrate_targets(calib_log, args.num_steps)
        with open(os.path.join(args.output_dir, f"obj_{obj_idx:04d}_budget.json"), "w") as f:
            json.dump(targets, f, indent=2)

        for method in methods:
            controller = None
            schedule = None
            if method == "RB_TCAS":
                controller = ResidualBudgetController(targets, "budget")
            elif method == "SRB_TCAS":
                controller = ResidualBudgetController(targets, "stable")
            elif method == "TRB_TCAS":
                controller = ResidualBudgetController(targets, "trust")
            elif method != "no_adapter":
                schedule = method
            if method == "no_adapter":
                # An explicit zero schedule uses the same generation path.
                schedule = "no_adapter"
                pred, log = generate(model, batch, device, dtype, geo_feats,
                                     args.num_steps, init.clone(), schedule_name=schedule)
            else:
                pred, log = generate(model, batch, device, dtype, geo_feats,
                                     args.num_steps, init.clone(),
                                     schedule_name=schedule, controller=controller)
            metric = ec.compute_probes(pred, target, mask)
            metric["object"] = f"obj_{obj_idx:04d}"
            results[method].append(metric)
            trace[method].append(log)
            if obj_idx < args.save_maps:
                save_dir = os.path.join(args.output_dir, "maps")
                os.makedirs(save_dir, exist_ok=True)
                ec.save_image(pred, os.path.join(save_dir, f"obj{obj_idx:02d}_{method}_pred.png"))
                ec.save_image(target, os.path.join(save_dir, f"obj{obj_idx:02d}_gt.png"))
                ec.save_image(mask[:, :1], os.path.join(save_dir, f"obj{obj_idx:02d}_mask.png"))
        print(f"[{obj_idx + 1}/{num_objects}] finished {methods}")
        torch.cuda.empty_cache()

    summary = {}
    for method in methods:
        rows = results[method]
        summary[method] = {
            "n": len(rows),
            "fg_ssim": float(np.mean([r["fg_ssim"] for r in rows])),
            "psnr": float(np.mean([r["psnr"] for r in rows])),
            "fg_lap_var": float(np.mean([r["fg_lap_var"] for r in rows])),
            "fg_lap_corr": float(np.nanmean([r["fg_lap_corr"] for r in rows])),
            "fg_mae": float(np.mean([r["fg_mae"] for r in rows])),
            "excess_hf_mean": float(np.mean([r["excess_hf_mean"] for r in rows])),
        }
    with open(os.path.join(args.output_dir, "pilot_results.json"), "w") as f:
        json.dump({"methods": methods, "summary": summary, "results": results,
                   "trace": trace, "num_steps": args.num_steps,
                   "num_objects": num_objects, "checkpoint": args.checkpoint}, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
