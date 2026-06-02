"""
Gradient analysis: Compare gradient statistics between single-view and multi-view training steps.
This helps understand why MV-Consistency reduces loss spikes.
"""
import os
import re
import numpy as np

def analyze_loss_patterns(log_file, name):
    """Analyze loss patterns to understand spike behavior."""
    with open(log_file) as f:
        content = f.read()

    # Extract step_loss and mv_consistency_loss
    step_losses = [float(x) for x in re.findall(r'step_loss=([0-9.]+)', content)]
    mv_losses = [float(x) for x in re.findall(r'mv_consistency_loss=([0-9.]+)', content)]

    if not step_losses:
        print(f"{name}: No data")
        return

    # Analyze spike patterns
    spikes = [(i, l) for i, l in enumerate(step_losses) if l > 1.0]

    print(f"\n{'='*60}")
    print(f"Loss Analysis: {name}")
    print(f"{'='*60}")
    print(f"Total steps: {len(step_losses)}")
    print(f"Mean loss: {np.mean(step_losses):.4f}")
    print(f"Std loss: {np.std(step_losses):.4f}")
    print(f"Median loss: {np.median(step_losses):.4f}")
    print(f"P95 loss: {np.percentile(step_losses, 95):.4f}")
    print(f"P99 loss: {np.percentile(step_losses, 99):.4f}")
    print(f"Max loss: {max(step_losses):.2f}")
    print(f"Spikes (>1.0): {len(spikes)}")

    if spikes:
        # Analyze spike distribution
        spike_indices = [s[0] for s in spikes]
        spike_values = [s[1] for s in spikes]

        # Check if spikes are clustered
        if len(spike_indices) > 1:
            gaps = np.diff(spike_indices)
            print(f"Mean gap between spikes: {np.mean(gaps):.1f} steps")
            print(f"Min gap: {min(gaps)} steps")
            print(f"Max gap: {max(gaps)} steps")

        # Check loss before/after spikes
        for i, (idx, val) in enumerate(spikes[:5]):  # Show first 5 spikes
            before = step_losses[max(0, idx-1)] if idx > 0 else 0
            after = step_losses[min(len(step_losses)-1, idx+1)] if idx < len(step_losses)-1 else 0
            print(f"  Spike {i+1}: step={idx}, loss={val:.2f}, before={before:.4f}, after={after:.4f}")

    # Analyze multi-view vs single-view loss patterns
    if mv_losses:
        mv_nonzero = [i for i, l in enumerate(mv_losses) if l > 0]
        mv_zero = [i for i, l in enumerate(mv_losses) if l == 0]

        print(f"\nMulti-view steps: {len(mv_nonzero)} ({len(mv_nonzero)/len(step_losses)*100:.0f}%)")
        print(f"Single-view steps: {len(mv_zero)} ({len(mv_zero)/len(step_losses)*100:.0f}%)")

        if mv_nonzero:
            mv_step_losses = [step_losses[i] for i in mv_nonzero]
            sv_step_losses = [step_losses[i] for i in mv_zero if i < len(step_losses)]

            print(f"Mean loss (multi-view): {np.mean(mv_step_losses):.4f}")
            print(f"Mean loss (single-view): {np.mean(sv_step_losses):.4f}")
            print(f"Std loss (multi-view): {np.std(mv_step_losses):.4f}")
            print(f"Std loss (single-view): {np.std(sv_step_losses):.4f}")

            # Check spikes in each mode
            mv_spikes = sum(1 for l in mv_step_losses if l > 1.0)
            sv_spikes = sum(1 for l in sv_step_losses if l > 1.0)
            print(f"Spikes in multi-view: {mv_spikes}")
            print(f"Spikes in single-view: {sv_spikes}")

if __name__ == '__main__':
    base = '/4T/CXY/MV-Painter/MVPainter'

    print("=" * 60)
    print("GRADIENT/LOSS ANALYSIS: Understanding Training Instability")
    print("=" * 60)

    analyze_loss_patterns(f'{base}/logs/baseline_73_final.log', 'Baseline (no consistency)')
    analyze_loss_patterns(f'{base}/logs/ours_73_v2.log', 'Ours (w=0.01, single_view_prob=0.3)')
