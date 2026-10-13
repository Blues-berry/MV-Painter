"""E1: Ablate the LAYER_MAX_SCALES cap to test the "scale semantics" mechanism.

Hypothesis H3 (find.md): the LapVar direction flip between the paper table and
the newer tables is driven by the inference-time per-layer scale cap:
  - Paper eval (uncapped): effective_scale = _adapter_scale  -> s=2.50 hits the
    128x128 shallow texture layer hard -> texture flattening (LapVar drops).
  - Newer eval (capped): effective_scale = min(_adapter_scale, _max_scale),
    shallow capped at 0.8 -> s=2.50 only boosts deep(32x32)/middle(64x64) ->
    coarse residual amplification (LapVar rises).

This script runs the SAME schedule on the SAME checkpoint under both forward
semantics and compares absolute LapVar + per-layer residual norms.

Usage:
    python geotex/explore_cap_ablation.py \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/explore_contradiction/cap_ablation_v2 \
        --num_objects 4 --num_steps 50
"""
import os
import sys
import json
import argparse
import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from mvpainter.model_unet_geotex import GeoTexResnetWrapper

# Reuse the exploration machinery
from explore_contradiction import (load_model, generate_with_schedule,
                                   compute_probes, make_schedules)


def uncapped_forward(self, *args, **kwargs):
    """Paper-style forward: residual applied with NO min(_adapter_scale, cap).

    Mirrors the original GeoTexResnetWrapper.forward but omits the
    min(_adapter_scale, _max_scale) cap. Must keep the _skip_correction guard:
    the RefOnlyNoisedUNet runs a write-pass (reference latents) and a read-pass;
    during write-pass _skip_correction=True so the adapter must NOT be applied,
    otherwise the reference latents are polluted by the adapter and the
    uncapped/capped comparison is confounded by double-application.
    """
    hidden_states = self.resnet(*args, **kwargs)
    if GeoTexResnetWrapper._skip_correction:
        return hidden_states
    if self._current_geo_feats is not None:
        geo_feat = self._current_geo_feats.get(self.geo_feat_key)
        if geo_feat is not None:
            if geo_feat.shape[2:] != hidden_states.shape[2:]:
                geo_feat = F.interpolate(geo_feat, size=hidden_states.shape[2:],
                                         mode='bilinear', align_corners=False)
            correction = self.adapter.compute_correction(hidden_states, geo_feat)
            if hasattr(self, '_adapter_scale'):
                correction = correction * self._adapter_scale      # NO cap
            self._last_correction = correction
            self._last_hidden = hidden_states.detach()
            hidden_states = hidden_states + correction
    return hidden_states


def run_one_mode(model, batch, device, weight_dtype, geo_feats, init_latents,
                 sched_fn, num_steps, capped):
    """Generate under capped (model default) or uncapped (paper) semantics.

    Re-seeds RNG before each generation so capped/uncapped share the same
    stochastic condition latent (VAE sampling) and reference noise (randn_like),
    making the comparison a pure forward-semantics difference.
    """
    if not capped:
        # Swap in uncapped forward, restore after
        orig = GeoTexResnetWrapper.forward
        GeoTexResnetWrapper.forward = uncapped_forward
    try:
        residual_log = {}
        torch.manual_seed(42)
        pred = generate_with_schedule(
            model, batch, device, weight_dtype, geo_feats,
            sched_fn, num_steps, init_latents.clone(), residual_log
        )
    finally:
        if not capped:
            GeoTexResnetWrapper.forward = orig
    return pred, residual_log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_objects', type=int, default=4)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading model...")
    model, config = load_model(args.config, args.checkpoint, device)
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    config_obj = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config_obj.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    SCHEDULES = make_schedules()

    summary = {'checkpoint': args.checkpoint, 'num_objects': num_objects,
               'num_steps': args.num_steps, 'results': {}}
    print(f"Schedule          | capped LapVar | uncapped LapVar | cap-shallow | raw-shallow")
    print("-" * 80)

    for obj_idx in range(num_objects):
        from data_utils import prepare_batch, collate_batch
        batch = collate_batch(dataset, obj_idx, device)
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)
        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for sched_name, sched_fn in SCHEDULES.items():
            caps = {}
            for capped in (True, False):
                pred, res_log = run_one_mode(model, batch, device, weight_dtype,
                                             geo_feats, init_latents, sched_fn,
                                             args.num_steps, capped)
                m = compute_probes(pred, target_imgs, mask)
                caps['capped' if capped else 'uncapped'] = m
                # residual norm mean over steps
                norms = []
                for step_entries in res_log.values():
                    for e in step_entries.values():
                        if e['depth'] == 'shallow':
                            norms.append(e['mean_abs'])
                caps['capped' if capped else 'uncapped']['shallow_resid_mean'] = float(sum(norms) / len(norms)) if norms else 0.0
            key = f"obj_{obj_idx:04d}"
            summary['results'].setdefault(sched_name, {})[key] = caps
            if obj_idx == 0:
                c, u = caps['capped'], caps['uncapped']
                print(f"{sched_name:<16} | {c['fg_lap_var']:>13.5f} | {u['fg_lap_var']:>15.5f} | "
                      f"{c.get('shallow_resid_mean', 0):>12.5f} | {u.get('shallow_resid_mean', 0):>12.5f}")
        torch.cuda.empty_cache()

    # Aggregate
    agg = {}
    for sched_name, objs in summary['results'].items():
        cl = [o['capped']['fg_lap_var'] for o in objs.values()]
        ul = [o['uncapped']['fg_lap_var'] for o in objs.values()]
        agg[sched_name] = {
            'capped_lapvar_mean': float(sum(cl) / len(cl)),
            'uncapped_lapvar_mean': float(sum(ul) / len(ul)),
            'uncapped_minus_capped': float((sum(ul) / len(ul)) - (sum(cl) / len(cl))),
        }
    summary['aggregate'] = agg
    with open(os.path.join(args.output_dir, 'cap_ablation_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print("\nAggregate:")
    for sched_name, a in agg.items():
        print(f"  {sched_name:<12} capped={a['capped_lapvar_mean']:.5f} "
              f"uncapped={a['uncapped_lapvar_mean']:.5f} delta={a['uncapped_minus_capped']:+.5f}")
    print(f"\nSaved: {os.path.join(args.output_dir, 'cap_ablation_summary.json')}")
    print("Done.")


if __name__ == '__main__':
    main()
