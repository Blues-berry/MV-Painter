#!/usr/bin/env python3
"""Test if GeoTexResnetWrapper.forward patching causes baseline difference."""
import os, sys, torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config
from torchvision.transforms import v2
from diffusers import EulerDiscreteScheduler
from eval import load_model, generate_images, collate_batch, prepare_batch
from mvpainter.model_unet_geotex import GeoTexResnetWrapper

BASE = '/4T/CXY/MV-Painter'
DEVICE = torch.device('cuda:1')
CONFIG = f'{BASE}/mvpoutput/geotex/eval_config_snapshot.yaml'
CHECKPOINT = f'{BASE}/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt'
OBJ_IDX = 74

def generate_baseline_no_patch(model, batch, device, wdt, num_steps, init_latents):
    """Generate baseline WITHOUT patching (eval.py style)."""
    return generate_images(model, batch, device, wdt, None, num_steps, init_latents)

def generate_baseline_with_patch(model, batch, device, wdt, num_steps, init_latents, scale=0):
    """Generate baseline WITH patching (eval_scale_inline.py style)."""
    # Patch forward (like eval_scale_inline.py)
    _orig = GeoTexResnetWrapper.forward
    def scaled(self, *a, **kw):
        hs = self.resnet(*a, **kw)
        if self._current_geo_feats is not None:
            gf = self._current_geo_feats.get(self.geo_feat_key)
            if gf is not None:
                if gf.shape[2:] != hs.shape[2:]:
                    gf = torch.nn.functional.interpolate(gf, size=hs.shape[2:], mode='bilinear', align_corners=False)
                c = self.adapter.compute_correction(hs, gf)
                self._last_correction = c
                hs = hs + c * getattr(self, '_adapter_scale', 1.0)
        return hs
    GeoTexResnetWrapper.forward = scaled

    # Set adapter scale (like eval_scale_inline.py)
    for module in model.unet.modules():
        if hasattr(module, 'adapter'):
            module._adapter_scale = scale

    # Generate
    result = generate_images(model, batch, device, wdt, None, num_steps, init_latents)

    # Cleanup
    for module in model.unet.modules():
        if hasattr(module, '_adapter_scale'):
            delattr(module, '_adapter_scale')
    GeoTexResnetWrapper.forward = _orig

    return result

def main():
    print("Loading model...")
    model = load_model(CONFIG, CHECKPOINT, DEVICE)
    config = OmegaConf.load(CONFIG)
    dataset = instantiate_from_config(config.data.params.validation)

    print(f"Generating baselines for object {OBJ_IDX}...")
    batch = collate_batch(dataset, OBJ_IDX, DEVICE)

    latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8

    # Test 1: No patching (eval.py style)
    torch.manual_seed(42)
    shared_latents = torch.randn(1, 4, latent_h, latent_w, device=DEVICE, dtype=torch.float16)
    torch.manual_seed(42)
    img_no_patch = generate_baseline_no_patch(model, batch, DEVICE, torch.float16, 50, shared_latents)

    # Test 2: With patching (eval_scale_inline.py style)
    torch.manual_seed(42)
    shared_latents2 = torch.randn(1, 4, latent_h, latent_w, device=DEVICE, dtype=torch.float16)
    torch.manual_seed(42)
    img_with_patch = generate_baseline_with_patch(model, batch, DEVICE, torch.float16, 50, shared_latents2)

    # Compare
    no_patch = img_no_patch[0].cpu().permute(1, 2, 0).numpy()
    with_patch = img_with_patch[0].cpu().permute(1, 2, 0).numpy()

    no_patch_fg = ~np.all(no_patch > 0.92, axis=2)
    with_patch_fg = ~np.all(with_patch > 0.92, axis=2)

    print(f"\n=== Patching Test (obj_{OBJ_IDX:03d}) ===")
    print(f"No patch (eval.py):          mean={no_patch.mean():.3f}, FG_frac={no_patch_fg.mean():.3f}")
    print(f"With patch (eval_scale):     mean={with_patch.mean():.3f}, FG_frac={with_patch_fg.mean():.3f}")
    print(f"Diff: {np.abs(no_patch - with_patch).mean():.6f}")
    print(f"Are they identical? {np.allclose(no_patch, with_patch, atol=1e-6)}")

if __name__ == '__main__':
    main()
