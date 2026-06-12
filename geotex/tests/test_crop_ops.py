"""Unit tests for crop_ops.py."""
import sys
import os
import pytest
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from metrics.crop_ops import fg_bbox_crop, normalize_background


class TestFgBboxCrop:
    def test_full_mask(self):
        """Full mask should return full image."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.ones(1, 1, 64, 64)
        cropped_img, cropped_mask = fg_bbox_crop(img, mask)
        assert cropped_img.shape == img.shape

    def test_empty_mask(self):
        """Empty mask should return original image."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        cropped_img, cropped_mask = fg_bbox_crop(img, mask)
        assert cropped_img.shape == img.shape

    def test_centered_fg(self):
        """Centered foreground should crop to center."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 16:48, 16:48] = 1.0
        cropped_img, cropped_mask = fg_bbox_crop(img, mask, padding=0.0)
        # Should be roughly 32x32 (plus possible rounding)
        assert cropped_img.shape[2] <= 40
        assert cropped_img.shape[3] <= 40

    def test_padding(self):
        """Padding should increase crop size."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 24:40, 24:40] = 1.0
        crop_no_pad, _ = fg_bbox_crop(img, mask, padding=0.0)
        crop_with_pad, _ = fg_bbox_crop(img, mask, padding=0.5)
        assert crop_with_pad.shape[2] >= crop_no_pad.shape[2]
        assert crop_with_pad.shape[3] >= crop_no_pad.shape[3]

    def test_bounds_check(self):
        """Crop should not exceed image bounds."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 0:8, 0:8] = 1.0  # Corner foreground
        cropped_img, _ = fg_bbox_crop(img, mask, padding=0.5)
        assert cropped_img.shape[2] <= 64
        assert cropped_img.shape[3] <= 64


class TestNormalizeBackground:
    def test_white_background(self):
        """Background should be set to 1.0 (white)."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 16:48, 16:48] = 1.0
        result = normalize_background(img, mask, bg_value=1.0)
        # Background pixels should be 1.0
        bg = (mask < 0.5).expand_as(img)
        assert (result[bg] == 1.0).all()

    def test_foreground_preserved(self):
        """Foreground pixels should be unchanged."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 16:48, 16:48] = 1.0
        result = normalize_background(img, mask, bg_value=1.0)
        fg = (mask > 0.5).expand_as(img)
        assert torch.equal(result[fg], img[fg])

    def test_black_background(self):
        """Background should be set to 0.0 (black)."""
        img = torch.rand(1, 3, 64, 64)
        mask = torch.zeros(1, 1, 64, 64)
        mask[0, 0, 16:48, 16:48] = 1.0
        result = normalize_background(img, mask, bg_value=0.0)
        bg = (mask < 0.5).expand_as(img)
        assert (result[bg] == 0.0).all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
