"""Unit tests for region_metrics.py."""
import sys
import os
import pytest
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from metrics.region_metrics import compute_all_metrics


class TestComputeAllMetrics:
    def test_returns_dict(self):
        """Should return a dictionary."""
        pred = torch.rand(1, 3, 64, 64)
        target = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        edge_mask = torch.zeros(1, 1, 64, 64)
        result = compute_all_metrics(pred, target, mask, edge_mask)
        assert isinstance(result, dict)

    def test_expected_keys(self):
        """Should contain all expected metric keys."""
        pred = torch.rand(1, 3, 64, 64)
        target = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        edge_mask = torch.zeros(1, 1, 64, 64)
        result = compute_all_metrics(pred, target, mask, edge_mask)

        expected_keys = [
            'full_psnr', 'full_ssim', 'full_lpips',
            'fg_psnr', 'fg_ssim', 'fg_lpips',
            'bg_psnr',
            'edge_psnr', 'edge_ssim',
            'nef_ssim',
            'bgwhite_psnr', 'bgwhite_ssim', 'bgwhite_lpips',
            'crop_psnr', 'crop_ssim', 'crop_lpips', 'crop_area',
        ]
        for erosion in [3, 5, 10]:
            expected_keys.extend([f'fg_psnr_e{erosion}', f'fg_ssim_e{erosion}'])
        for dilation in [3, 5, 10]:
            expected_keys.extend([f'fg_psnr_d{dilation}', f'fg_ssim_d{dilation}'])

        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_no_nan(self):
        """No metric should be NaN."""
        pred = torch.rand(1, 3, 64, 64)
        target = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        edge_mask = torch.zeros(1, 1, 64, 64)
        result = compute_all_metrics(pred, target, mask, edge_mask)
        for key, val in result.items():
            if val is not None:
                assert not (val != val), f"NaN in {key}"  # NaN != NaN

    def test_identical_images(self):
        """Identical images should have PSNR=100 and SSIM~1."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        edge_mask = torch.zeros(1, 1, 64, 64)
        result = compute_all_metrics(img, img, mask, edge_mask)
        assert result['full_psnr'] == 100.0
        assert result['full_ssim'] > 0.99
        assert result['fg_psnr'] == 100.0
        assert result['fg_ssim'] > 0.99

    def test_crop_area(self):
        """Crop area should be between 0 and 1."""
        pred = torch.rand(1, 3, 64, 64)
        target = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        edge_mask = torch.zeros(1, 1, 64, 64)
        result = compute_all_metrics(pred, target, mask, edge_mask)
        assert 0 <= result['crop_area'] <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
