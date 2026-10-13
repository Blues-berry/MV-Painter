"""Inspect a FAC checkpoint: LTAG temporal profile + GSG/FSC movement from init.

Usage:
    python geotex/inspect_fac_ckpt.py --checkpoint <path> [--device cpu]

Prints per-adapter LTAG scale at early/mid/late timesteps (the 50-step Euler
eval grid), the GSG weight/bias statistics, and the FSC residual magnitude.
This verifies that the learned modules actually moved and whether LTAG kept
the C3 piecewise shape (mid=2.50 deep/middle, 0.80 shallow) or collapsed.
"""
import argparse
import sys
import os
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from diffusers import EulerDiscreteScheduler
from mvpainter.adaptive_correction import AdaptiveCorrectionController


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint', required=True)
    p.add_argument('--device', default='cpu')
    args = p.parse_args()

    st = torch.load(args.checkpoint, map_location='cpu')
    variant = st.get('variant', '?')
    fac_version = st.get('fac_version', '?')
    warmstart_c3 = st.get('warmstart_c3', '?')
    print(f"checkpoint: {args.checkpoint}")
    print(f"variant={variant} fac_version={fac_version} warmstart_c3={warmstart_c3} step={st.get('step')}")

    # Build controller matching variant
    ctrl = AdaptiveCorrectionController(
        num_adapters=9,
        enable_ltag='ltag' in variant,
        enable_gsg='gsg' in variant,
        enable_fsc='fsc' in variant,
    )
    ctrl.load_state_dict(st['fac_controller'])

    # Per-adapter caps (same depth-group convention as training)
    caps = [3.0, 3.0, 3.0, 3.5, 3.5, 3.5, 0.8, 0.8, 0.8]

    # LTAG profile on the eval grid
    if ctrl.ltag is not None:
        sched = EulerDiscreteScheduler.from_config({
            'beta_start': 0.00085, 'beta_end': 0.012,
            'beta_schedule': 'scaled_linear', 'prediction_type': 'epsilon'})
        sched.set_timesteps(50, device='cpu')
        ts = sched.timesteps.float()
        with torch.no_grad():
            scales = ctrl.ltag(ts)  # (50, 9)
        n = len(ts)
        early = scales[:n//3].mean(0)
        mid = scales[n//3:2*n//3].mean(0)
        late = scales[2*n//3:].mean(0)
        print("\nLTAG scale profile (early / mid / late per adapter, caps shown):")
        print("adapter  cap | early     mid      late")
        for i in range(9):
            print(f"  {i}    {caps[i]:<4} | {early[i]:.3f}    {mid[i]:.3f}    {late[i]:.3f}")
        print(f"\nLTAG mid/early ratio (temporal contrast; C3=2.0 for deep/middle):")
        for i in range(9):
            r = mid[i] / max(early[i], 1e-6)
            print(f"  adapter {i}: mid/early = {r:.2f}")

    # GSG movement
    if ctrl.gsg_modules is not None:
        print("\nGSG gate conv (per adapter: |W|mean, bias):")
        for i, g in enumerate(ctrl.gsg_modules):
            w = g.gate_conv.weight.detach()
            b = g.gate_conv.bias.detach()
            print(f"  adapter {i}: |W|mean={w.abs().mean().item():.4f}  bias={b.item():.4f}  "
                  f"(init 0/0 → gate 1.0)")
        # How much would the gate deviate from 1.0 on a typical geo_feat?
        print("  → tanh(|W|) bound on spatial gate deviation: "
              f"{max(g.gate_conv.weight.detach().abs().max().item() for g in ctrl.gsg_modules):.3f}")

    # FSC movement
    if ctrl.fsc_modules is not None:
        print("\nFSC freq-mask residual (per adapter: |resid|mean, mask mean, mask min/max):")
        for i, f in enumerate(ctrl.fsc_modules):
            r = f.freq_mask_residual.detach()
            m = (f._init_mask + torch.tanh(r)).clamp(0, 1)
            print(f"  adapter {i}: |resid|mean={r.abs().mean().item():.4f}  "
                  f"mask_mean={m.mean().item():.3f}  mask[{m.min().item():.3f},{m.max().item():.3f}] "
                  f"(init near-all-pass)")


if __name__ == '__main__':
    main()
