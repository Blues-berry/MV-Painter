"""Unit tests for mask_ops.py."""
import sys
import os
import pytest
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from metrics.mask_ops import morph_mask, compute_edge_mask


class TestMorphMask:
    def test_identity_kernel0(self):
        """kernel_size=0 should return identity."""
        mask = torch.rand(1, 1, 32, 32).round()
        result = morph_mask(mask, 0)
        assert torch.equal(result, mask)

    def test_erode_shrinks(self):
        """Erosion should shrink foreground region."""
        mask = torch.zeros(1, 1, 32, 32)
        mask[0, 0, 8:24, 8:24] = 1.0
        eroded = morph_mask(mask, 5, 'erode')
        assert eroded.sum() < mask.sum()

    def test_dilate_grows(self):
        """Dilation should grow foreground region."""
        mask = torch.zeros(1, 1, 32, 32)
        mask[0, 0, 12:20, 12:20] = 1.0
        dilated = morph_mask(mask, 5, 'dilate')
        assert dilated.sum() > mask.sum()

    def test_erode_full_mask(self):
        """Eroding a full mask should return mostly full (boundary pixels eroded due to padding)."""
        mask = torch.ones(1, 1, 32, 32)
        eroded = morph_mask(mask, 5, 'erode')
        # Boundary pixels get eroded due to zero-padding in conv2d
        # Interior should remain 1
        assert eroded[0, 0, 4:28, 4:28].sum() == (24 * 24)

    def test_erode_empty_mask(self):
        """Eroding an empty mask should return an empty mask."""
        mask = torch.zeros(1, 1, 32, 32)
        eroded = morph_mask(mask, 5, 'erode')
        assert eroded.sum() == 0

    def test_output_binary(self):
        """Output should be binary (0 or 1)."""
        mask = torch.rand(1, 1, 32, 32).round()
        result = morph_mask(mask, 5, 'erode')
        assert ((result == 0) | (result == 1)).all()


class TestComputeEdgeMask:
    def test_flat_image(self):
        """Flat image should have no interior edges (boundary edges from padding are expected)."""
        img = torch.ones(1, 1, 64, 64) * 0.5
        edge = compute_edge_mask(img, threshold=0.1)
        # Interior should have no edges (boundary may have edges from zero-padding)
        assert edge[0, 0, 4:60, 4:60].sum() == 0

    def test_checkerboard(self):
        """Checkerboard pattern should have edges."""
        img = torch.zeros(1, 1, 64, 64)
        for i in range(0, 64, 8):
            for j in range(0, 64, 8):
                if (i // 8 + j // 8) % 2 == 0:
                    img[0, 0, i:i + 8, j:j + 8] = 1.0
        edge = compute_edge_mask(img, threshold=0.1)
        assert edge.sum() > 0

    def test_rgb_input(self):
        """RGB input should be converted to grayscale."""
        img = torch.rand(1, 3, 64, 64)
        edge = compute_edge_mask(img, threshold=0.1)
        assert edge.shape == (1, 1, 64, 64)

    def test_output_binary(self):
        """Output should be binary (0 or 1)."""
        img = torch.rand(1, 1, 64, 64)
        edge = compute_edge_mask(img, threshold=0.1)
        assert ((edge == 0) | (edge == 1)).all()

    def test_threshold_effect(self):
        """Higher threshold should produce fewer edges."""
        img = torch.rand(1, 1, 64, 64)
        edge_low = compute_edge_mask(img, threshold=0.01)
        edge_high = compute_edge_mask(img, threshold=0.5)
        assert edge_low.sum() >= edge_high.sum()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
