"""Identity-safe replacement of a cached appearance feature at inference."""

from __future__ import annotations

import torch


def replace_cached_embedding(
    cached_embedding: torch.Tensor,
    embedding_from_current_condition: torch.Tensor,
) -> torch.Tensor:
    """Replace a stale feature with the same runner's encoding of its current input.

    This helper uses no target RGB, target metric, or learned parameters. It
    preserves the cached tensor's shape, device and dtype so the surrounding
    GFL/LLH code keeps its existing interface.
    """
    if cached_embedding.shape != embedding_from_current_condition.shape:
        raise ValueError(
            "cached and recomputed embeddings must have identical shapes: "
            f"{tuple(cached_embedding.shape)} != {tuple(embedding_from_current_condition.shape)}"
        )
    if not torch.isfinite(embedding_from_current_condition).all():
        raise ValueError("recomputed embedding contains non-finite values")
    return embedding_from_current_condition.to(
        device=cached_embedding.device, dtype=cached_embedding.dtype
    ).clone()

