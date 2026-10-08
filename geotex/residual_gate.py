"""Inference-time feature-relative bound for geometry residual injection."""
from __future__ import annotations

import math

import torch


def apply_feature_ratio_bound(
    residual: torch.Tensor,
    feature: torch.Tensor,
    *,
    scale: float,
    tau: float,
    eps: float = 1e-8,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    """Scale a residual, then bound its RMS relative to the host feature.

    ``tau`` is a frozen per-depth limit. The returned scalar diagnostics remain
    tensors so callers can defer device synchronization until logs are written.
    """
    if residual.shape != feature.shape:
        raise ValueError(f"residual/feature shape mismatch: {residual.shape} != {feature.shape}")
    if not math.isfinite(scale) or scale < 0:
        raise ValueError(f"scale must be finite and non-negative, got {scale}")
    if not math.isfinite(tau) or tau < 0:
        raise ValueError(f"tau must be finite and non-negative, got {tau}")
    if not math.isfinite(eps) or eps <= 0:
        raise ValueError(f"eps must be finite and positive, got {eps}")

    feature_f = feature.float()
    scaled = residual.float() * scale
    feature_rms = feature_f.square().mean().sqrt()
    residual_rms = scaled.square().mean().sqrt()
    ratio = residual_rms / feature_rms.clamp_min(eps)
    gate = torch.clamp(torch.as_tensor(tau, device=ratio.device) / ratio.clamp_min(eps), max=1.0)
    applied = (scaled * gate).to(dtype=residual.dtype)
    applied_f = applied.float()
    applied_rms = applied_f.square().mean().sqrt()
    diagnostics = {
        "feature_rms": feature_rms.detach(),
        "pre_gate_residual_rms": residual_rms.detach(),
        "pre_gate_ratio": ratio.detach(),
        "gate": gate.detach(),
        "applied_residual_rms": applied_rms.detach(),
        "post_gate_ratio": (applied_rms / feature_rms.clamp_min(eps)).detach(),
        "pre_gate_anomaly_fraction": (scaled.abs() > 0.25 * feature_rms).float().mean().detach(),
        "applied_anomaly_fraction": (applied_f.abs() > 0.25 * feature_rms).float().mean().detach(),
    }
    return applied, diagnostics
