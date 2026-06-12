"""Unit tests for image_metrics.py."""
import sys
import os
import pytest
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from metrics.image_metrics import compute_psnr, compute_ssim, compute_lpips


class TestComputePsnr:
    def test_identical_images(self):
        """Identical images should return 100.0."""
        img = torch.rand(1, 3, 64, 64)
        assert compute_psnr(img, img) == 100.0

    def test_known_mse(self):
        """PSNR = 10 * log10(1/MSE)."""
        pred = torch.zeros(1, 3, 64, 64)
        target = torch.ones(1, 3, 64, 64) * 0.1  # MSE = 0.01
        psnr = compute_psnr(pred, target)
        expected = 10 * torch.log10(torch.tensor(1.0 / 0.01)).item()
        assert abs(psnr - expected) < 0.01

    def test_empty_mask(self):
        """Empty mask should return 0.0."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        assert compute_psnr(img, img, mask) == 0.0

    def test_full_mask(self):
        """Full mask should give same result as no mask."""
        img1 = torch.rand(1, 3, 64, 64)
        img2 = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        psnr_no_mask = compute_psnr(img1, img2)
        psnr_full_mask = compute_psnr(img1, img2, mask)
        assert abs(psnr_no_mask - psnr_full_mask) < 0.01

    def test_mask_expansion(self):
        """1-channel mask should expand to match 3-channel images."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        psnr = compute_psnr(img, img, mask)
        assert psnr == 100.0


class TestComputeSsim:
    def test_identical_images(self):
        """Identical images should return SSIM close to 1.0."""
        img = torch.rand(1, 3, 64, 64)
        ssim = compute_ssim(img, img)
        assert ssim > 0.99

    def test_clamped_to_01(self):
        """SSIM should be clamped to [0, 1]."""
        img1 = torch.rand(1, 3, 64, 64)
        img2 = torch.rand(1, 3, 64, 64)
        ssim = compute_ssim(img1, img2)
        assert 0 <= ssim <= 1

    def test_empty_mask(self):
        """Empty mask should return 0.0."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        assert compute_ssim(img, img, mask) == 0.0

    def test_full_mask(self):
        """Full mask should give similar result to no mask."""
        img1 = torch.rand(1, 3, 64, 64)
        img2 = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        ssim_no_mask = compute_ssim(img1, img2)
        ssim_full_mask = compute_ssim(img1, img2, mask)
        assert abs(ssim_no_mask - ssim_full_mask) < 0.05

    def test_different_images(self):
        """Different images should have lower SSIM than identical."""
        img1 = torch.rand(1, 3, 64, 64)
        img2 = torch.rand(1, 3, 64, 64)
        ssim = compute_ssim(img1, img2)
        assert ssim < 0.99


class TestComputeLpips:
    def test_identical_images(self):
        """Identical images should return LPIPS close to 0."""
        img = torch.rand(1, 3, 64, 64)
        lpips = compute_lpips(img, img)
        if lpips is not None:  # lpips may not be installed
            assert lpips < 0.01

    def test_input_range_transform(self):
        """LPIPS should handle [0,1] input correctly."""
        img = torch.rand(1, 3, 64, 64)
        lpips = compute_lpips(img, img)
        if lpips is not None:
            assert lpips >= 0

    def test_none_when_unavailable(self):
        """Should return None if lpips_fn is None and lpips not installed."""
        img = torch.rand(1, 3, 64, 64)
        result = compute_lpips(img, img, lpips_fn=None)
        # Either returns a value (if lpips installed) or None
        assert result is None or isinstance(result, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
