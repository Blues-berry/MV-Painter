"""Create a warm-start-only LTAG checkpoint (no training) to test the FAC eval path.

Control experiment: does an LTAG that exactly reproduces the effective C3 schedule
(through the SAME eval_fac_v2.py generation path) recover the baseline eval_300_c3
numbers? If yes → the eval path is sound and the ~3 dB drop of the trained FAC
checkpoints is genuinely learned. If no → the eval path has a protocol bug.

Builds the LTAG targets using the EXACT eval C3 mapping
(step_frac = idx / (n-1), boundaries 1/3 and 2/3), then applies the per-adapter
caps (deep 3.0 / middle 3.5 / shallow 0.8) exactly as the wrapper does.

Usage:
    python geotex/probe_warmstart_ckpt.py \
        --src mvpoutput/fac_v3/ltag/checkpoints/fac_v2_ltag_step_002000.pt \
        --out /tmp/fac_warmstart_probe.pt
    python geotex/eval_fac_v2.py \
        --checkpoint /tmp/fac_warmstart_probe.pt \
        --output_dir mvpoutput/fac_v3/probe_warmstart --num_objects 12 --device cuda:0
"""
import argparse
import sys
import os
import json
import math

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from diffusers import EulerDiscreteScheduler
from mvpainter.adaptive_correction import AdaptiveCorrectionController

CAPS = [3.0, 3.0, 3.0, 3.5, 3.5, 3.5, 0.8, 0.8, 0.8]
N_ADAPTERS = 9


def build_c3_targets(eval_ts, device):
    """Effective C3 schedule on the eval grid, with per-adapter caps.

    Matches schedule_c3(step_frac) in the baseline: s=1.25 for frac<1/3,
    s=2.50 for 1/3<=frac<2/3, s=1.25 for frac>=2/3, then clamp each adapter
    to its depth-group cap (same as min(scale, max_scale) in the wrapper).
    """
    n = len(eval_ts)
    frac = torch.arange(n, device=device, dtype=torch.float32) / max(n - 1, 1)
    targets = torch.full((n, N_ADAPTERS), 1.25, device=device)
    mid = (frac >= 1.0 / 3.0) & (frac < 2.0 / 3.0)
    targets[mid, :] = 2.50
    for idx in range(N_ADAPTERS):
        targets[:, idx] = targets[:, idx].clamp(max=CAPS[idx])
    return targets


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--src', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--fit_steps', type=int, default=2000)
    args = p.parse_args()

    st = torch.load(args.src, map_location='cpu')
    variant = st.get('variant', 'ltag')
    assert 'ltag' in variant, f"src must be LTAG-enabled, got {variant}"
    # A clean warm-start control must have GSG/FSC inactive: if the source checkpoint
    # is a full-FAC variant, its trained GSG/FSC weights would stay active during eval
    # and contaminate the comparison.
    assert 'gsg' not in variant and 'fsc' not in variant, \
        f"src must be LTAG-only for a clean warm-start control (GSG/FSC would stay active), got {variant}"

    # Build the same controller architecture the eval will build
    ctrl = AdaptiveCorrectionController(
        num_adapters=N_ADAPTERS,
        enable_ltag='ltag' in variant,
        enable_gsg='gsg' in variant,
        enable_fsc='fsc' in variant,
    )
    ctrl.load_state_dict(st['fac_controller'])
    ctrl.eval()

    # Build the eval Euler timestep grid using the REAL scheduler config so the fit grid
    # exactly matches eval_fac_v2.py (EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)).
    # checkpoints/hf_repo/scheduler/scheduler_config.json is beta_schedule='linear',
    # timestep_spacing='trailing', steps_offset=1 (NOT the linspace/offset-0 defaults).
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sched_cfg_path = os.path.join(repo_root, 'checkpoints', 'hf_repo', 'scheduler', 'scheduler_config.json')
    with open(sched_cfg_path) as f:
        sched_cfg = json.load(f)
    sched = EulerDiscreteScheduler.from_config(sched_cfg)
    sched.set_timesteps(50, device='cpu')
    eval_ts = sched.timesteps.float()

    # Fit LTAG to the effective C3 targets (exact eval mapping + caps)
    ltag = ctrl.ltag
    dev = next(ltag.parameters()).device
    targets = build_c3_targets(eval_ts, dev)
    t_vals = eval_ts.float().to(dev)
    opt = torch.optim.Adam(ltag.parameters(), lr=1e-2)
    last = 0.0
    for _ in range(args.fit_steps):
        opt.zero_grad()
        pred = ltag(t_vals)
        loss = (pred - targets).pow(2).mean()
        loss.backward()
        opt.step()
        last = loss.item()
    print(f"warm-start fit MSE = {last:.6f}")

    # Verify the fitted profile. C3 boundaries on the eval grid (frac = idx/(n-1),
    # mid on [1/3, 2/3)) are idx = ceil((n-1)/3) .. ceil(2(n-1)/3) - 1; for n=50: 17..32.
    with torch.no_grad():
        scales = ltag(t_vals)
    n = len(scales)
    b1, b2 = math.ceil((n - 1) / 3), math.ceil(2 * (n - 1) / 3)
    early = scales[:b1].mean(0)
    midv = scales[b1:b2].mean(0)
    late = scales[b2:].mean(0)
    print("fitted LTAG (early/mid/late) per adapter:")
    for i in range(N_ADAPTERS):
        print(f"  adapter {i} cap={CAPS[i]:<4}: {early[i]:.3f}  {midv[i]:.3f}  {late[i]:.3f}")

    # Overwrite the controller weights in the checkpoint
    st['fac_controller'] = ctrl.state_dict()
    st['warmstart_only'] = True
    torch.save(st, args.out)
    print(f"warm-start-only checkpoint → {args.out}")


if __name__ == '__main__':
    main()
