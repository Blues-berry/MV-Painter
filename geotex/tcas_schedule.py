"""TCAS v2 Schedule — 5-phase per-layer temporal control.

Shared between train_v2.py and eval_unified_300.py to ensure consistency.

Schedule design rationale:
  - Deep layers (up_0, 32x32): global structure, moderate correction
  - Middle layers (up_1, 64x64): PRIMARY shape lever, highest peak scale
  - Shallow layers (up_2, 128x128): fine texture, minimal intervention to avoid damage

Phases (by denoising progress fraction):
  Phase 1 (0-15%):  Very early — light touch, structure forming
  Phase 2 (15-35%): Main structure formation
  Phase 3 (35-65%): Peak adapter influence for shape refinement
  Phase 4 (65-85%): Moderate correction, detail refinement
  Phase 5 (85-100%): Fine detail, minimal adapter (protect texture)
"""

# Block depth group assignment
BLOCK_DEPTH_MAP = {
    'mid': 'deep',
    'up_0': 'deep',
    'up_1': 'middle',
    'up_2': 'shallow',
}

# 5-phase scale values per layer group
TCAS_V2_SCHEDULES = {
    'deep':    [0.75, 1.50, 2.25, 1.25, 0.50],
    'middle':  [1.00, 2.00, 3.00, 1.75, 0.75],
    'shallow': [0.25, 0.50, 0.75, 0.40, 0.20],
}

# Phase boundary fractions (5 phases → 6 boundaries)
PHASE_BOUNDARIES = [0.0, 0.15, 0.35, 0.65, 0.85, 1.0]


def get_tcas_v2_scale(step_frac, layer_group='middle'):
    """Get TCAS v2 scale for a given denoising progress fraction and layer group.

    Args:
        step_frac: float in [0, 1], where 0=start of denoising (full noise),
                   1=end of denoising (clean image)
        layer_group: 'deep', 'middle', or 'shallow'

    Returns:
        float: scale value with smooth interpolation between phases
    """
    schedule = TCAS_V2_SCHEDULES.get(layer_group, TCAS_V2_SCHEDULES['middle'])

    # Find which phase and interpolate for smooth transitions
    for i in range(len(PHASE_BOUNDARIES) - 1):
        if step_frac <= PHASE_BOUNDARIES[i + 1]:
            phase_start = PHASE_BOUNDARIES[i]
            phase_end = PHASE_BOUNDARIES[i + 1]
            local_frac = (step_frac - phase_start) / (phase_end - phase_start)

            if i < len(schedule) - 1:
                val_curr = schedule[i]
                val_next = schedule[i + 1]
                # Gentle blend toward next phase (30% transition)
                return val_curr + (val_next - val_curr) * local_frac * 0.3
            return schedule[i]
    return schedule[-1]


def get_scale_for_timestep(timestep, num_timesteps=1000, layer_group='middle'):
    """Convert diffusion timestep to TCAS v2 scale.

    In diffusion models:
      - High timestep (t→T) = early denoising (more noise) → step_frac near 0
      - Low timestep (t→0) = late denoising (less noise) → step_frac near 1

    Args:
        timestep: int or float, current diffusion timestep [0, num_timesteps)
        num_timesteps: total timesteps in the schedule
        layer_group: 'deep', 'middle', or 'shallow'
    """
    step_frac = 1.0 - (timestep / num_timesteps)
    return get_tcas_v2_scale(step_frac, layer_group)


def get_scale_for_step_idx(step_idx, total_steps, layer_group='middle'):
    """Convert scheduler step index to TCAS v2 scale.

    For inference: step_idx counts from 0 (first denoising step) to total_steps-1 (last).
    step_idx=0 → step_frac=0 (start), step_idx=total_steps-1 → step_frac=1 (end).
    """
    step_frac = step_idx / max(total_steps - 1, 1)
    return get_tcas_v2_scale(step_frac, layer_group)


# ============================================================
# Simple uniform schedules (shared across all eval scripts)
# Each takes denoising progress in [0,1] and returns a float scale.
# ============================================================

def schedule_c3(progress, s_low=1.25, s_high=2.50):
    """C3: piecewise constant low-high-low with 1/3 boundaries."""
    if progress < 1.0 / 3.0:
        return s_low
    elif progress < 2.0 / 3.0:
        return s_high
    else:
        return s_low


def schedule_fixed(progress, scale_value=1.25):
    """Fixed uniform scale throughout denoising."""
    return scale_value


def schedule_no_adapter(progress):
    """s=0 everywhere: base pipeline without geometric adapter."""
    return 0.0
