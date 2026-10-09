import cv2
import numpy as np
import pytest

from geotex.round2_texture import (
    masked_ciede2000,
    masked_psnr,
    srgb_to_linear,
    variation_diagnostics,
)


def square_mask(size=32):
    mask = np.zeros((size, size), dtype=np.uint8)
    mask[8:-8, 8:-8] = 1
    return mask


def test_identical_images_have_zero_reference_error_and_roundtrip_color_space():
    image = np.full((32, 32, 3), 0.4, dtype=np.float32)
    mask = square_mask()
    assert masked_psnr(image, image, mask) == 100.0
    assert masked_ciede2000(image, image, mask) == pytest.approx(0.0)
    linear = srgb_to_linear(image)
    assert np.all((linear >= 0) & (linear <= 1))


def test_color_shift_and_spatial_misalignment_are_detected():
    gt = np.zeros((32, 32, 3), dtype=np.float32)
    gt[..., 0] = np.linspace(0, 1, 32)[None, :]
    shifted = np.clip(gt + 0.1, 0, 1)
    misaligned = np.roll(gt, 2, axis=1)
    mask = square_mask()
    assert masked_ciede2000(shifted, gt, mask) > 0
    assert masked_psnr(misaligned, gt, mask) < masked_psnr(gt, gt, mask)


def test_smoothing_reduces_texture_variation_and_noise_increases_laplacian():
    rng = np.random.default_rng(7)
    noisy = rng.random((32, 32, 3), dtype=np.float32)
    smooth = cv2.GaussianBlur(noisy, (7, 7), 0)
    mask = np.ones((32, 32), dtype=np.uint8)
    noisy_stats = variation_diagnostics(noisy, mask)
    smooth_stats = variation_diagnostics(smooth, mask)
    assert smooth_stats["laplacian_variance"] < noisy_stats["laplacian_variance"]


def test_background_noise_does_not_change_eroded_foreground_diagnostics():
    rng = np.random.default_rng(9)
    gt = np.full((32, 32, 3), 0.5, dtype=np.float32)
    pred = gt.copy()
    outside = ~square_mask().astype(bool)
    pred[outside] = rng.random((outside.sum(), 3), dtype=np.float32)
    assert variation_diagnostics(pred, square_mask()) == variation_diagnostics(gt, square_mask())


def test_empty_foreground_and_invalid_values_are_explicit():
    image = np.zeros((8, 8, 3), dtype=np.float32)
    empty = np.zeros((8, 8), dtype=np.uint8)
    assert np.isnan(masked_psnr(image, image, empty))
    assert all(np.isnan(value) for value in variation_diagnostics(image, empty).values())
    invalid = image.copy()
    invalid[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        variation_diagnostics(invalid)
