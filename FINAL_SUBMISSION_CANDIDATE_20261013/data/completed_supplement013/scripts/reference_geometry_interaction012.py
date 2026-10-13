"""Development candidate: project only the reference-dependent geometry interaction.

Factorial decomposition is algebra, and conflict projection follows known gradient
surgery. Novelty and useful geometry/appearance separation are NOT established.
"""
import torch

def correct_interaction(full_prediction, bare_prediction, guidance_scale=2.0):
    if full_prediction.shape != bare_prediction.shape or full_prediction.shape[0] != 2:
        raise ValueError('Expected matched negative/positive conditional predictions')
    if not torch.isfinite(full_prediction).all() or not torch.isfinite(bare_prediction).all():
        raise ValueError('Nonfinite conditional predictions')
    fu, fc = full_prediction.float().chunk(2)
    bu, bc = bare_prediction.float().chunk(2)
    reference = bc - bu
    common_geometry = fu - bu
    interaction = (fc - fu) - reference
    denom = reference.square().sum().clamp_min(1e-12)
    coefficient = (interaction * reference).sum().clamp(max=0) / denom
    delta_interaction = -coefficient * reference
    delta_guided = float(guidance_scale) * delta_interaction
    # Equal branch shifts alter the final CFG prediction by delta_guided only.
    modified = full_prediction + delta_guided.to(full_prediction.dtype).repeat(2, 1, 1, 1)
    return modified, {'common_geometry': common_geometry, 'reference_difference': reference,
                      'interaction': interaction, 'delta_interaction': delta_interaction}
