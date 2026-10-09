import numpy as np
from skimage.color import lab2rgb

from color_repair import (
    apply_chroma_anchor_to_views,
    estimate_chroma_anchor,
    perturb_foreground_lab,
    source_conditioned_chroma_anchor,
)
from embedding_refresh import replace_cached_embedding
import pytest
import torch


def _solid_rgb(lab, size=32):
    rgb = np.clip(lab2rgb(np.broadcast_to(np.asarray(lab, dtype=float), (size, size, 3))), 0, 1)
    return np.rint(rgb * 255).astype(np.uint8)


def test_identity_and_no_difference_are_byte_exact():
    source = _solid_rgb((60, 14, 22))
    mask = np.ones((32, 32), dtype=np.float32)
    views = [source.copy() for _ in range(6)]
    repaired, estimate = source_conditioned_chroma_anchor(source, mask, views, [mask] * 6)
    assert estimate.applied_delta_ab == (0.0, 0.0)
    assert all(np.array_equal(a, b) for a, b in zip(views, repaired))
    assert np.array_equal(perturb_foreground_lab(source, np.zeros_like(mask), 6, -6), source)


def test_repair_respects_masks_and_preserves_background_bytes():
    source = _solid_rgb((58, 28, 24))
    target = _solid_rgb((58, -22, -18))
    mask = np.zeros((32, 32), dtype=np.float32)
    mask[6:26, 6:26] = 1.0
    mask[5, 8:24] = 0.5
    views = [target.copy() for _ in range(6)]
    repaired = apply_chroma_anchor_to_views(views, [mask] * 6, (4.0, 3.0))
    assert all(np.array_equal(img[mask == 0], target[mask == 0]) for img in repaired)
    assert np.any(repaired[0][mask == 1].astype(int) != target[mask == 1].astype(int))


def test_anchor_caps_each_chroma_component():
    source = _solid_rgb((60, 60, 55))
    generated = _solid_rgb((60, -60, -55))
    mask = np.ones((32, 32), dtype=np.float32)
    result = estimate_chroma_anchor(source, mask, generated, mask, max_abs_delta=6)
    assert abs(result.raw_delta_ab[0]) > 6
    assert abs(result.raw_delta_ab[1]) > 6
    assert result.applied_delta_ab == (6.0, 6.0)


def test_lab_probe_changes_chroma_inside_alpha_and_keeps_zero_alpha():
    source = _solid_rgb((55, 8, -7))
    alpha = np.zeros((32, 32), dtype=np.float32)
    alpha[8:24, 8:24] = 1.0
    changed = perturb_foreground_lab(source, alpha, 6, -6)
    assert np.array_equal(changed[alpha == 0], source[alpha == 0])
    assert np.any(changed[alpha == 1] != source[alpha == 1])


def test_embedding_refresh_is_identity_when_cache_matches_and_keeps_dtype():
    cached = torch.tensor([[[1.25, -0.5]]], dtype=torch.float16)
    updated = replace_cached_embedding(cached, cached.float())
    assert updated.dtype == cached.dtype
    assert updated.device == cached.device
    assert torch.equal(updated, cached)
    assert updated.data_ptr() != cached.data_ptr()


def test_embedding_refresh_uses_current_condition_encoding_without_mutating_cache():
    cached = torch.tensor([[[1.0, 2.0]]], dtype=torch.float16)
    recomputed = torch.tensor([[[3.0, -4.0]]], dtype=torch.float32)
    updated = replace_cached_embedding(cached, recomputed)
    assert torch.equal(updated, recomputed.half())
    assert torch.equal(cached, torch.tensor([[[1.0, 2.0]]], dtype=torch.float16))


def test_embedding_refresh_rejects_shape_or_value_corruption():
    cached = torch.zeros(1, 1, 4)
    with pytest.raises(ValueError, match="identical shapes"):
        replace_cached_embedding(cached, torch.zeros(1, 4))
    bad = torch.tensor([[[float("nan"), 0.0, 0.0, 0.0]]])
    with pytest.raises(ValueError, match="non-finite"):
        replace_cached_embedding(cached, bad)
