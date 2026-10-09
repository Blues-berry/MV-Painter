"""Conservative, source-only Lab chroma adjustment for six-view outputs.

The module does not read GT colors, GT texture, UV maps, or target RGBs. Masks
are supplied by the caller from source alpha and target geometry silhouettes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import ndimage
from skimage.color import lab2rgb, rgb2lab


@dataclass(frozen=True)
class ChromaAnchorEstimate:
    source_median_ab: tuple[float, float]
    generated_reference_median_ab: tuple[float, float]
    raw_delta_ab: tuple[float, float]
    applied_delta_ab: tuple[float, float]
    source_pixels: int
    reference_pixels: int


def _rgb_float(rgb: np.ndarray) -> np.ndarray:
    arr = np.asarray(rgb)
    if arr.ndim != 3 or arr.shape[-1] != 3:
        raise ValueError(f"RGB image must be HxWx3, got {arr.shape}")
    if arr.dtype == np.uint8:
        return arr.astype(np.float32) / 255.0
    arr = arr.astype(np.float32)
    if not np.isfinite(arr).all() or arr.min() < -1e-5 or arr.max() > 1.00001:
        raise ValueError("floating RGB must be finite and in [0, 1]")
    return np.clip(arr, 0.0, 1.0)


def _mask_float(mask: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    arr = np.asarray(mask, dtype=np.float32)
    if arr.shape != shape:
        raise ValueError(f"mask shape {arr.shape} does not match image {shape}")
    if not np.isfinite(arr).all():
        raise ValueError("mask contains non-finite values")
    return np.clip(arr, 0.0, 1.0)


def perturb_foreground_lab(
    rgb: np.ndarray,
    alpha: np.ndarray,
    delta_a: float,
    delta_b: float,
) -> np.ndarray:
    """Apply a controlled foreground-only Lab chroma intervention.

    Alpha weights the perturbation at antialiased boundaries. Pixels with zero
    alpha are copied byte-for-byte, so the white background cannot drift.
    """
    original = np.asarray(rgb)
    float_rgb = _rgb_float(original)
    mask = _mask_float(alpha, original.shape[:2])
    if delta_a == 0 and delta_b == 0:
        return original.copy()

    lab = rgb2lab(float_rgb)
    lab[..., 1] += np.float32(delta_a) * mask
    lab[..., 2] += np.float32(delta_b) * mask
    changed = np.clip(lab2rgb(lab), 0.0, 1.0)
    if original.dtype == np.uint8:
        result = np.rint(changed * 255.0).astype(np.uint8)
    else:
        result = changed.astype(original.dtype, copy=False)
    result[mask <= 0.0] = original[mask <= 0.0]
    return result


def _median_ab(
    rgb: np.ndarray,
    mask: np.ndarray,
    *,
    erosion_px: int = 3,
    min_pixels: int = 64,
) -> tuple[tuple[float, float], int]:
    float_rgb = _rgb_float(rgb)
    alpha = _mask_float(mask, float_rgb.shape[:2])
    region = alpha >= 0.75
    if erosion_px > 0:
        region = ndimage.binary_erosion(region, iterations=erosion_px, border_value=0)
    count = int(region.sum())
    if count < min_pixels:
        raise ValueError(f"trusted foreground has only {count} pixels; need {min_pixels}")
    lab = rgb2lab(float_rgb)
    ab = np.median(lab[region, 1:3], axis=0)
    return (float(ab[0]), float(ab[1])), count


def estimate_chroma_anchor(
    source_rgb: np.ndarray,
    source_alpha: np.ndarray,
    generated_reference_rgb: np.ndarray,
    generated_reference_mask: np.ndarray,
    *,
    max_abs_delta: float = 6.0,
    erosion_px: int = 3,
    min_pixels: int = 64,
) -> ChromaAnchorEstimate:
    """Estimate a bounded a*/b* offset from source and generated source view."""
    if max_abs_delta < 0:
        raise ValueError("max_abs_delta must be non-negative")
    source_ab, source_count = _median_ab(
        source_rgb, source_alpha, erosion_px=erosion_px, min_pixels=min_pixels
    )
    reference_ab, reference_count = _median_ab(
        generated_reference_rgb,
        generated_reference_mask,
        erosion_px=erosion_px,
        min_pixels=min_pixels,
    )
    raw = np.asarray(source_ab) - np.asarray(reference_ab)
    applied = np.clip(raw, -max_abs_delta, max_abs_delta)
    return ChromaAnchorEstimate(
        source_median_ab=source_ab,
        generated_reference_median_ab=reference_ab,
        raw_delta_ab=(float(raw[0]), float(raw[1])),
        applied_delta_ab=(float(applied[0]), float(applied[1])),
        source_pixels=source_count,
        reference_pixels=reference_count,
    )


def apply_chroma_anchor_to_views(
    views_rgb: Sequence[np.ndarray],
    view_masks: Sequence[np.ndarray],
    delta_ab: tuple[float, float],
) -> list[np.ndarray]:
    """Apply the same bounded chroma vector inside each supplied view mask."""
    if len(views_rgb) != 6 or len(view_masks) != 6:
        raise ValueError("the repair expects exactly six unique target views")
    da, db = (float(delta_ab[0]), float(delta_ab[1]))
    return [
        perturb_foreground_lab(rgb, mask, da, db)
        for rgb, mask in zip(views_rgb, view_masks)
    ]


def source_conditioned_chroma_anchor(
    source_rgb: np.ndarray,
    source_alpha: np.ndarray,
    views_rgb: Sequence[np.ndarray],
    view_masks: Sequence[np.ndarray],
    *,
    max_abs_delta: float = 6.0,
    erosion_px: int = 3,
    min_pixels: int = 64,
) -> tuple[list[np.ndarray], ChromaAnchorEstimate]:
    """Estimate from source RGB + generated view 0, then adjust six views."""
    if len(views_rgb) != 6 or len(view_masks) != 6:
        raise ValueError("the repair expects exactly six unique target views")
    estimate = estimate_chroma_anchor(
        source_rgb,
        source_alpha,
        views_rgb[0],
        view_masks[0],
        max_abs_delta=max_abs_delta,
        erosion_px=erosion_px,
        min_pixels=min_pixels,
    )
    return apply_chroma_anchor_to_views(views_rgb, view_masks, estimate.applied_delta_ab), estimate

