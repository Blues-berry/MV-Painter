"""
GeoTex-Adapter for MV-Painter.
Adds geometry-aware residual adapters to UNet up blocks (and optionally mid block)
without modifying attention mechanisms.

Adapter design:
- Zero-initialized residual: output = x + adapter(geo_features) * gate
- Geometry encoder: Conv-based encoder that processes normal/depth/mask
- Injected after ResnetBlock2D in each up block
"""
import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from torchvision.transforms import v2
from torchvision.utils import make_grid, save_image
from einops import rearrange

from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler, UNet2DConditionModel

from .mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline
from .adaptive_correction import AdaptiveCorrectionController


def scale_latents(latents):
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def scale_image(image):
    return image * 0.5 / 0.8


def unscale_image(image):
    return image / 0.5 * 0.8


# ============================================================
# Loss Utilities
# ============================================================

def compute_ssim_loss(pred, target, mask=None):
    """Compute SSIM loss (1 - SSIM) for training. Expects (B,C,H,W) in [0,1]."""
    C1, C2 = 0.01 ** 2, 0.03 ** 2
    mu1 = F.avg_pool2d(pred, 3, 1, 1)
    mu2 = F.avg_pool2d(target, 3, 1, 1)
    sigma1 = F.avg_pool2d(pred ** 2, 3, 1, 1) - mu1 ** 2
    sigma2 = F.avg_pool2d(target ** 2, 3, 1, 1) - mu2 ** 2
    sigma12 = F.avg_pool2d(pred * target, 3, 1, 1) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1 + sigma2 + C2))
    if mask is not None:
        mask_d = F.max_pool2d(mask, 3, 1, 1)
        # Expand mask to match ssim_map channels
        mask_d = mask_d.expand_as(ssim_map)
        fg = mask_d > 0.5
        if fg.sum() == 0:
            return torch.tensor(0.0, device=pred.device)
        return 1.0 - (ssim_map * mask_d)[fg].mean()
    return 1.0 - ssim_map.mean()


def compute_edge_mask(depth_or_normal, threshold=0.1):
    """Compute edge mask from depth or normal map using Sobel gradients.

    Args:
        depth_or_normal: (B, C, H, W) — depth (C=1) or normal (C=3) map in [0,1]
        threshold: gradient magnitude threshold for edge detection
    Returns:
        edge_mask: (B, 1, H, W) — binary edge mask
    """
    # Convert to grayscale if needed
    if depth_or_normal.shape[1] == 3:
        gray = depth_or_normal.mean(dim=1, keepdim=True)
    else:
        gray = depth_or_normal

    # Sobel kernels
    sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)
    sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                           dtype=gray.dtype, device=gray.device).view(1, 1, 3, 3)

    grad_x = F.conv2d(gray, sobel_x, padding=1)
    grad_y = F.conv2d(gray, sobel_y, padding=1)
    grad_mag = torch.sqrt(grad_x ** 2 + grad_y ** 2 + 1e-8)

    # Normalize to [0, 1]
    grad_mag = grad_mag / (grad_mag.max() + 1e-8)

    return (grad_mag > threshold).float()


# ============================================================
# GeoTex-Adapter Modules
# ============================================================

class GeoTexAdapter(nn.Module):
    """Zero-initialized residual adapter with bottleneck design.

    Takes geometry features and produces a residual correction
    to the UNet hidden state. Starts as identity (zero-init).

    Bottleneck design keeps params low (~1-2M per adapter):
    - geo_proj: geo_channels -> bottleneck (64)
    - gate: bottleneck + channel_stats -> bottleneck
    - expand: bottleneck -> in_channels (zero-init)
    """

    def __init__(self, in_channels, geo_channels=64, bottleneck=64, kernel_size=3):
        super().__init__()
        padding = kernel_size // 2

        # Project geometry features to bottleneck
        self.geo_proj = nn.Sequential(
            nn.Conv2d(geo_channels, bottleneck, kernel_size=kernel_size, padding=padding),
            nn.SiLU(),
            nn.Conv2d(bottleneck, bottleneck, kernel_size=kernel_size, padding=padding),
        )

        # Channel attention: compress in_channels -> bottleneck for gating
        self.channel_compress = nn.AdaptiveAvgPool2d(1)
        self.channel_gate = nn.Sequential(
            nn.Linear(in_channels, bottleneck),
            nn.SiLU(),
            nn.Linear(bottleneck, bottleneck),
            nn.Sigmoid(),
        )

        # Output projection: bottleneck -> in_channels, zero-initialized
        # Zero-init ensures correction starts at exactly 0, preserving base model quality.
        # Encoder gradients flow once output_proj weights become non-zero after first few steps.
        self.output_proj = nn.Conv2d(bottleneck, in_channels, kernel_size=1)
        nn.init.zeros_(self.output_proj.weight)
        nn.init.zeros_(self.output_proj.bias)

    def compute_correction(self, x, geo_feat):
        """Compute the residual correction without adding to x.

        Args:
            x: UNet hidden state (B, C, H, W)
            geo_feat: geometry features (B, geo_channels, H, W)
        Returns:
            Correction tensor (B, C, H, W)
        """
        input_dtype = x.dtype
        x_f32 = x.float()
        geo_f32 = geo_feat.float()

        geo_mapped = self.geo_proj(geo_f32)
        channel_stats = self.channel_compress(x_f32).squeeze(-1).squeeze(-1)
        gate = self.channel_gate(channel_stats).unsqueeze(-1).unsqueeze(-1)
        gated_geo = geo_mapped * gate
        correction = self.output_proj(gated_geo)
        return correction.to(input_dtype)

    def forward(self, x, geo_feat):
        """
        Args:
            x: UNet hidden state (B, C, H, W)
            geo_feat: geometry features (B, geo_channels, H, W)
        Returns:
            Corrected hidden state (B, C, H, W)
        """
        correction = self.compute_correction(x, geo_feat)
        return x + correction


class GeoTexEncoder(nn.Module):
    """Encodes geometry information (normal, depth, mask) to multi-scale features.

    Input: (B, 5, H, W) - normal(3) + depth(1) + mask(1)
    Output: dict of features at 4 resolution levels, each projected to out_channels.

    Multi-scale feature hierarchy:
      x1: (B, out_channels, H, W)     — high-res edge/detail
      x2: (B, out_channels, H/2, W/2) — mid-res geometry
      x3: (B, out_channels, H/4, W/4) — low-res structure
      x4: (B, out_channels, H/8, W/8) — global/semantic

    UNet block → feature scale mapping (for 256x256 input):
      mid  (32×32, 1280ch) → x4 (H/8)
      up_0 (32×32, 1280ch) → x4 (H/8)
      up_1 (64×64, 640ch)  → x3 (H/4)
      up_2 (128×128, 320ch)→ x2 (H/2)
    """

    def __init__(self, in_channels=5, base_channels=32, out_channels=64):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels

        # Encoder: progressive downsampling (same structure as before)
        self.enc1 = nn.Sequential(
            nn.Conv2d(in_channels, base_channels, 3, 1, 1),
            nn.SiLU(),
            nn.Conv2d(base_channels, base_channels, 3, 1, 1),
            nn.SiLU(),
        )
        self.down1 = nn.Conv2d(base_channels, base_channels * 2, 3, 2, 1)  # /2

        self.enc2 = nn.Sequential(
            nn.Conv2d(base_channels * 2, base_channels * 2, 3, 1, 1),
            nn.SiLU(),
            nn.Conv2d(base_channels * 2, base_channels * 2, 3, 1, 1),
            nn.SiLU(),
        )
        self.down2 = nn.Conv2d(base_channels * 2, base_channels * 4, 3, 2, 1)  # /4

        self.enc3 = nn.Sequential(
            nn.Conv2d(base_channels * 4, base_channels * 4, 3, 1, 1),
            nn.SiLU(),
            nn.Conv2d(base_channels * 4, base_channels * 4, 3, 1, 1),
            nn.SiLU(),
        )
        self.down3 = nn.Conv2d(base_channels * 4, out_channels, 3, 2, 1)  # /8

        self.enc4 = nn.Sequential(
            nn.Conv2d(out_channels, out_channels, 3, 1, 1),
            nn.SiLU(),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1),
            nn.SiLU(),
        )

        # Per-scale projection to normalize channels to out_channels.
        # Each encoder level has different channel counts:
        #   enc1: base_channels (32), enc2: base_channels*2 (64),
        #   enc3: base_channels*4 (128), enc4: out_channels (64)
        # These 1x1 convs project them all to out_channels (64).
        self.proj_x1 = nn.Conv2d(base_channels, out_channels, 1)
        self.proj_x2 = nn.Conv2d(base_channels * 2, out_channels, 1)
        self.proj_x3 = nn.Conv2d(base_channels * 4, out_channels, 1)
        # x4 already has out_channels, no projection needed

    def forward(self, geo_input):
        """
        Args:
            geo_input: (B, 5, H, W) - normal(3) + depth(1) + mask(1)
        Returns:
            dict with keys 'x1'..'x4' and convenience mappings for each UNet block.
        """
        x1 = self.enc1(geo_input)      # (B, base_ch, H, W)
        x2 = self.down1(x1)            # (B, base_ch*2, H/2, W/2)
        x2 = self.enc2(x2)             # (B, base_ch*2, H/2, W/2)
        x3 = self.down2(x2)            # (B, base_ch*4, H/4, W/4)
        x3 = self.enc3(x3)             # (B, base_ch*4, H/4, W/4)
        x4 = self.down3(x3)            # (B, out_ch, H/8, W/8)
        x4 = self.enc4(x4)             # (B, out_ch, H/8, W/8)

        # Project each scale to out_channels
        px1 = self.proj_x1(x1)  # (B, out_ch, H, W)
        px2 = self.proj_x2(x2)  # (B, out_ch, H/2, W/2)
        px3 = self.proj_x3(x3)  # (B, out_ch, H/4, W/4)
        # x4 already has out_channels

        return {
            # Raw scale features (for direct access)
            'x1': px1,   # H — high-res edge/detail
            'x2': px2,   # H/2 — mid-res geometry
            'x3': px3,   # H/4 — low-res structure
            'x4': x4,    # H/8 — global/semantic
            # UNet block → feature mappings
            # mid block: 32×32 for 256 input → H/8
            'mid': x4,
            # up_0: CrossAttnUpBlock2D at 32×32 → H/8
            'up_0': x4,
            # up_1: CrossAttnUpBlock2D at 64×64 → H/4
            'up_1': px3,
            # up_2: UpBlock2D at 128×128 → H/2
            'up_2': px2,
        }


# ============================================================
# GeoTex-Adapter Injection
# ============================================================

class GeoTexResnetWrapper(nn.Module):
    """Wraps a ResnetBlock2D with a GeoTexAdapter applied after it.

    The wrapper checks for a _geo_feats attribute on itself (set externally)
    to decide whether to apply the adapter.

    Supports optional AdaptiveCorrectionController for LTAG/GSG/FSC modulation.
    When no controller is set, falls back to legacy behavior (raw correction).
    """

    # Class-level flag: skip adapter correction during reference-write pass
    _skip_correction = False

    # Per-layer scale caps (set by inject_adapters based on depth group)
    LAYER_MAX_SCALES = {
        'deep': 3.0,      # up_0: global structure
        'middle': 3.5,    # up_1: primary shape lever
        'shallow': 0.8,   # up_2: fine texture, minimal intervention
    }

    def __init__(self, resnet, adapter, geo_feat_key='up_0', adapter_idx=0,
                 depth_group='deep'):
        super().__init__()
        self.resnet = resnet
        self.adapter = adapter
        self.geo_feat_key = geo_feat_key
        self.adapter_idx = adapter_idx
        self.depth_group = depth_group
        self._max_scale = self.LAYER_MAX_SCALES.get(depth_group, 3.0)
        self._current_geo_feats = None
        self._last_correction = None  # For residual regularization
        self._last_hidden = None  # For ratio-based regularization
        self._correction_controller = None  # Set externally for adaptive correction

    def set_geo_feats(self, geo_feats):
        """Set geometry features for the current forward pass."""
        self._current_geo_feats = geo_feats

    def clear_geo_feats(self):
        """Clear geometry features after forward pass."""
        self._current_geo_feats = None
        self._last_correction = None
        self._last_correction_raw = None
        self._last_hidden = None

    def forward(self, *args, **kwargs):
        # Run original resnet
        hidden_states = self.resnet(*args, **kwargs)

        # Skip adapter correction during reference-write pass
        if GeoTexResnetWrapper._skip_correction:
            return hidden_states

        # Apply adapter if geo_feats are available
        if self._current_geo_feats is not None:
            geo_feat = self._current_geo_feats.get(self.geo_feat_key)
            if geo_feat is not None:
                # Resize geo_feat to match hidden_states spatial size
                if geo_feat.shape[2:] != hidden_states.shape[2:]:
                    geo_feat = F.interpolate(
                        geo_feat, size=hidden_states.shape[2:],
                        mode='bilinear', align_corners=False
                    )
                # Compute correction and store for regularization
                correction = self.adapter.compute_correction(hidden_states, geo_feat)

                # Apply static _adapter_scale (set during training or inference)
                # For shallow layers this is the primary defense against mode collapse
                if hasattr(self, '_adapter_scale'):
                    effective_scale = min(self._adapter_scale, self._max_scale)
                    correction = correction * effective_scale

                # Apply adaptive correction (GSG/FSC) if controller is set
                if self._correction_controller is not None:
                    correction = self._correction_controller.apply(
                        correction, geo_feat, self.adapter_idx
                    )

                # Store for regularization loss computation
                self._last_correction = correction
                self._last_hidden = hidden_states.detach()
                hidden_states = hidden_states + correction

        return hidden_states


def inject_adapters(unet, mode='up_only', geo_channels=64):
    """Inject GeoTexAdapter into UNet blocks by wrapping resnet modules.

    Args:
        unet: The UNet model
        mode: 'up_only' or 'mid_up'
        geo_channels: Output channels of GeoTexEncoder

    Returns:
        adapters: nn.ModuleList of all adapters
        encoder: GeoTexEncoder
        adapter_map: dict mapping adapter index to (block_name, geo_feat_key)
    """
    adapters = nn.ModuleList()
    adapter_map = {}

    # Determine which blocks to inject
    block_configs = []

    if mode == 'mid_up':
        # Mid block resnets
        for i, resnet in enumerate(unet.mid_block.resnets):
            in_ch = resnet.conv1.in_channels
            block_configs.append(('mid', i, resnet, in_ch, 'mid'))

    # Up block resnets
    for block_idx, up_block in enumerate(unet.up_blocks):
        for resnet_idx, resnet in enumerate(up_block.resnets):
            in_ch = resnet.conv1.out_channels  # Use output channels
            block_configs.append((f'up_{block_idx}', resnet_idx, resnet, in_ch, f'up_{block_idx}'))

    # Block name -> depth group mapping for per-layer scale caps
    BLOCK_DEPTH_MAP = {
        'mid': 'deep',
        'up_0': 'deep',
        'up_1': 'middle',
        'up_2': 'shallow',
    }

    # Create adapters and wrap resnets
    for block_name, resnet_idx, resnet, in_ch, geo_key in block_configs:
        adapter = GeoTexAdapter(in_channels=in_ch, geo_channels=geo_channels)
        adapters.append(adapter)
        adapter_idx = len(adapters) - 1

        # Determine depth group for per-layer scale cap
        depth_group = BLOCK_DEPTH_MAP.get(block_name, 'deep')

        # Wrap the resnet with the adapter (pass adapter_idx for controller)
        wrapped = GeoTexResnetWrapper(resnet, adapter, geo_feat_key=geo_key,
                                      adapter_idx=adapter_idx,
                                      depth_group=depth_group)

        # Replace the resnet in the UNet
        if block_name == 'mid':
            unet.mid_block.resnets[resnet_idx] = wrapped
        else:
            up_idx = int(block_name.split('_')[1])
            unet.up_blocks[up_idx].resnets[resnet_idx] = wrapped

        adapter_map[adapter_idx] = (block_name, geo_key)

    print(f"Injected {len(adapters)} GeoTex adapters ({mode} mode)")

    # Create encoder
    encoder = GeoTexEncoder(in_channels=5, base_channels=32, out_channels=geo_channels)

    return adapters, encoder, adapter_map


# ============================================================
# Training Model
# ============================================================

class GeoTexCheckpointCallback(pl.Callback):
    """Saves GeoTex-Adapter weights."""

    def __init__(self, save_dir='', every_n_steps=100):
        super().__init__()
        self.save_dir = save_dir
        self.every_n_steps = every_n_steps

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if (trainer.global_step + 1) % self.every_n_steps == 0 and trainer.global_rank == 0:
            save_dir = self.save_dir or os.path.join(trainer.logdir, 'geotex_checkpoints')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f'geotex_step_{trainer.global_step + 1:07d}.pt')
            pl_module.save_geotex_weights(save_path)


class MVDiffusionGeoTex(pl.LightningModule):
    """MV-Painter with GeoTex-Adapter.

    Freezes the original UNet and trains only the geometry-aware adapters.
    """

    def __init__(
        self,
        stable_diffusion_config,
        drop_cond_prob=0.1,
        adapter_mode='up_only',  # 'up_only' or 'mid_up'
        geo_channels=64,
        foreground_loss_weight=0.1,
        ssim_loss_weight=0.05,
        edge_loss_weight=0.02,
        adapter_reg_weight=1e-4,
        img_size=256,
        # Adaptive Correction (FAC) settings
        enable_ltag=False,
        enable_gsg=False,
        enable_fsc=False,
        ltag_init_schedule=None,  # dict: {'early': 1.25, 'mid': 2.50, 'late': 1.25}
    ):
        super().__init__()

        self.drop_cond_prob = drop_cond_prob
        self.adapter_mode = adapter_mode
        self.geo_channels = geo_channels
        self.foreground_loss_weight = foreground_loss_weight
        self.ssim_loss_weight = ssim_loss_weight
        self.edge_loss_weight = edge_loss_weight
        self.adapter_reg_weight = adapter_reg_weight
        self.img_size = img_size
        self._lr = None
        self.enable_ltag = enable_ltag
        self.enable_gsg = enable_gsg
        self.enable_fsc = enable_fsc
        self.ltag_init_schedule = ltag_init_schedule

        self.register_schedule()

        # Load pipeline
        print("Loading MV-Painter pipeline...")
        pipeline = MVPainter_Pipeline.from_pretrained(
            stable_diffusion_config['pretrained_model_name_or_path'],
            use_safetensors=True,
        ).to(self.device)
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline.scheduler.config, timestep_spacing='trailing',
        )
        self.pipeline = pipeline

        # Wrap UNet
        train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)
        if isinstance(pipeline.unet, UNet2DConditionModel) or True:
            pipeline.unet = RefOnlyNoisedUNet(
                pipeline.unet, train_sched, pipeline.scheduler, replace_processors=True,
            )

        self.train_scheduler = train_sched
        self.unet = pipeline.unet

        # Note: Gradient checkpointing is DISABLED for GeoTex-Adapter because
        # the adapter wrapper changes the computation graph, causing checkpoint
        # mismatch errors. The adapter params are small (~2M), so the memory
        # overhead is manageable.
        print("Gradient checkpointing DISABLED for GeoTex-Adapter compatibility")

        # Inject GeoTex adapters
        self.adapters, self.geo_encoder, self.adapter_map = inject_adapters(
            self.unet, mode=adapter_mode, geo_channels=geo_channels
        )

        # Initialize Adaptive Correction Controller (FAC)
        num_adapters = len(self.adapters)
        if enable_ltag or enable_gsg or enable_fsc:
            ltag_kwargs = {}
            if ltag_init_schedule:
                ltag_kwargs['init_schedule'] = ltag_init_schedule
            self.correction_controller = AdaptiveCorrectionController(
                num_adapters=num_adapters,
                geo_channels=geo_channels,
                enable_ltag=enable_ltag,
                enable_gsg=enable_gsg,
                enable_fsc=enable_fsc,
                ltag_kwargs=ltag_kwargs,
            )
            # Register controller on all wrappers
            for name, module in self.unet.unet.named_modules():
                if isinstance(module, GeoTexResnetWrapper):
                    module._correction_controller = self.correction_controller
            fac_params = self.correction_controller.param_count()
            print(f"FAC (Adaptive Correction) enabled: LTAG={enable_ltag}, GSG={enable_gsg}, FSC={enable_fsc}")
            print(f"  FAC params: {fac_params}")
        else:
            self.correction_controller = None
            print("FAC disabled — using legacy static scaling")

        # Count parameters
        adapter_params = sum(p.numel() for p in self.adapters.parameters())
        encoder_params = sum(p.numel() for p in self.geo_encoder.parameters())
        fac_total = sum(p.numel() for p in self.correction_controller.parameters()) if self.correction_controller else 0
        total_trainable = adapter_params + encoder_params + fac_total
        unet_params = sum(p.numel() for p in self.unet.parameters())
        print(f"GeoTex adapter params: {adapter_params / 1e6:.2f}M")
        print(f"GeoTex encoder params: {encoder_params / 1e6:.2f}M")
        if fac_total > 0:
            print(f"FAC controller params: {fac_total / 1e6:.4f}M")
        print(f"Total trainable: {total_trainable / 1e6:.2f}M / {unet_params / 1e6:.2f}M UNet ({100 * total_trainable / unet_params:.2f}%)")

        self.validation_step_outputs = []

    def register_schedule(self):
        self.num_timesteps = 1000
        beta_start = 0.00085
        beta_end = 0.0120
        betas = torch.linspace(beta_start, beta_end, 1000, dtype=torch.float32)

        alphas = 1. - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        alphas_cumprod_prev = torch.cat([torch.ones(1, dtype=torch.float64), alphas_cumprod[:-1]], 0)

        self.register_buffer('betas', betas.float())
        self.register_buffer('alphas_cumprod', alphas_cumprod.float())
        self.register_buffer('alphas_cumprod_prev', alphas_cumprod_prev.float())

        self.register_buffer('sqrt_alphas_cumprod', torch.sqrt(alphas_cumprod).float())
        self.register_buffer('sqrt_one_minus_alphas_cumprod', torch.sqrt(1 - alphas_cumprod).float())

        self.register_buffer('sqrt_recip_alphas_cumprod', torch.sqrt(1. / alphas_cumprod).float())
        self.register_buffer('sqrt_recipm1_alphas_cumprod', torch.sqrt(1. / alphas_cumprod - 1).float())

    def on_fit_start(self):
        device = torch.device(f'cuda:{self.global_rank}')
        print(f"on_fit_start: device={device}")
        self.pipeline.to('cpu')
        self.unet.to(device)  # This moves wrapped resnets too
        self.pipeline.vae.to(device)
        self.adapters.to(device)
        self.geo_encoder.to(device)
        if self.correction_controller is not None:
            self.correction_controller.to(device)
        self.pipeline.vision_encoder.to('cpu')
        self.pipeline.vision_encoder_2.to('cpu')

        # Verify adapters are on correct device
        for i, adapter in enumerate(self.adapters):
            dev = next(adapter.parameters()).device
            print(f"  Adapter {i} on device: {dev}")

        if self.global_rank == 0:
            os.makedirs(os.path.join(self.logdir, 'images'), exist_ok=True)
            os.makedirs(os.path.join(self.logdir, 'images_val'), exist_ok=True)

    def prepare_batch_data(self, batch, device=None):
        """Prepare batch data including geometry information."""
        if device is None:
            device = self.device
        cond_imgs = batch['cond_imgs']
        cond_imgs = cond_imgs.to(device)
        cond_imgs = v2.functional.resize(cond_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)

        target_imgs = batch['target_imgs']
        target_imgs = v2.functional.resize(target_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        target_imgs = rearrange(target_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        target_imgs = target_imgs.to(device)

        # Normal maps (stored as 'depth_imgs' in dataset, confusingly)
        normal_imgs = batch['depth_imgs']
        normal_imgs = v2.functional.resize(normal_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        normal_imgs = rearrange(normal_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        normal_imgs = normal_imgs.to(device)

        # Real depth maps
        real_depth_imgs = batch['real_depth_imgs']
        real_depth_imgs = v2.functional.resize(real_depth_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        real_depth_imgs = rearrange(real_depth_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        real_depth_imgs = real_depth_imgs.to(device)

        # Alpha mask from dataset (if available) or compute from target
        if 'alpha_masks' in batch:
            alpha_masks = batch['alpha_masks']  # (B, 6, H, W) or (B, 6, 1, H, W)
            if alpha_masks.dim() == 4:
                alpha_masks = alpha_masks.unsqueeze(2)  # (B, 6, 1, H, W)
            # Resize each view's mask
            B, N, C, H, W = alpha_masks.shape
            alpha_masks = alpha_masks.reshape(B * N, C, H, W)
            alpha_masks = v2.functional.resize(alpha_masks, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
            alpha_masks = alpha_masks.reshape(B, N, C, self.img_size, self.img_size)
            alpha_masks = rearrange(alpha_masks, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
            mask = alpha_masks.to(device)
        else:
            mask = self._compute_mask_from_target(target_imgs)

        # Build geometry input: normal(3) + depth(1) + mask(1) = 5 channels
        # Use depth channel (first channel of real_depth)
        depth_single = real_depth_imgs[:, :1, :, :]  # (B, 1, 3H, 2W)
        geo_input = torch.cat([normal_imgs, depth_single, mask], dim=1)  # (B, 5, 3H, 2W)

        return cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask

    def _compute_mask_from_target(self, target_imgs):
        """Fallback: compute foreground mask from target images."""
        is_not_white = (target_imgs < 0.95).any(dim=1, keepdim=True)
        mask = is_not_white.float()
        return mask

    @torch.no_grad()
    def encode_condition_image(self, images):
        dtype = next(self.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = self.pipeline.feature_extractor_vae(images=image_pil, return_tensors="pt").pixel_values
        image_pt = image_pt.to(device=self.device, dtype=dtype)
        latents = self.pipeline.vae.encode(image_pt).latent_dist.sample()
        return latents

    @torch.no_grad()
    def encode_target_images(self, images):
        dtype = next(self.pipeline.vae.parameters()).dtype
        images = (images - 0.5) / 0.8
        posterior = self.pipeline.vae.encode(images.to(dtype)).latent_dist
        latents = posterior.sample() * self.pipeline.vae.config.scaling_factor
        latents = scale_latents(latents)
        return latents

    def _set_geo_feats_on_wrappers(self, geo_feats):
        """Set geometry features on all wrapped resnet modules."""
        for name, module in self.unet.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                module.set_geo_feats(geo_feats)

    def _clear_geo_feats_on_wrappers(self):
        """Clear geometry features from all wrapped resnet modules."""
        for name, module in self.unet.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                module.clear_geo_feats()

    def forward_unet(self, latents, t, prompt_embeds, cond_latents, depth_imgs,
                     added_cond_kwargs, is_training, depth_imgs_2, geo_feats=None):
        dtype = next(self.pipeline.unet.parameters()).dtype
        latents = latents.to(dtype)
        prompt_embeds = prompt_embeds.to(dtype)
        cond_latents = cond_latents.to(dtype)
        cross_attention_kwargs = dict(cond_lat=cond_latents)

        # Set geo_feats on wrapped resnets BEFORE calling UNet forward.
        # Note: We do NOT clear geo_feats here to avoid gradient checkpointing
        # mismatch. The RefOnlyNoisedUNet calls unet forward twice (write + read),
        # and geo_feats must be consistently available for both calls.
        # Clear is done externally after forward_unet returns.
        if geo_feats is not None:
            self._set_geo_feats_on_wrappers(geo_feats)

        pred_noise = self.pipeline.unet(
            latents,
            t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=is_training,
        )[0]

        return pred_noise

    def training_step(self, batch, batch_idx):
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = self.prepare_batch_data(batch)

        B = cond_imgs.shape[0]
        t = torch.randint(0, self.num_timesteps, size=(B,)).long().to(self.device)

        with torch.no_grad():
            weight_dtype = torch.float16

            if np.random.rand() > self.drop_cond_prob:
                if 'global_embeds' in batch:
                    global_embeds = batch['global_embeds'].to(self.device, dtype=weight_dtype)
                    global_embeds = global_embeds.view(B, 1, -1)
                    ramp = global_embeds.new_tensor(self.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
                    uc_text_emb = self.pipeline.uc_text_emb.to(self.device, dtype=weight_dtype)
                    prompt_embeds = uc_text_emb + global_embeds * ramp
                else:
                    prompt_embeds = self.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=False)
                cond_latents = self.encode_condition_image(cond_imgs).to(weight_dtype)
                added_cond_kwargs = self.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
                added_cond_kwargs = {k: v.to(self.device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()}
            else:
                if 'global_embeds' in batch:
                    prompt_embeds = torch.zeros((B, 77, 2048), device=self.device, dtype=weight_dtype)
                else:
                    prompt_embeds = self.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=True)
                cond_latents = self.encode_condition_image(torch.zeros_like(cond_imgs)).to(weight_dtype)
                added_cond_kwargs = self.pipeline.get_added_cond_kwargs_train(B, is_drop=True)
                added_cond_kwargs = {k: v.to(self.device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()}

        latents = self.encode_target_images(target_imgs).to(weight_dtype)

        noise = torch.randn_like(latents)
        latents_noisy = self.train_scheduler.add_noise(latents, noise, t)

        # Encode geometry features
        geo_feats = self.geo_encoder(geo_input.to(weight_dtype))

        # Set LTAG timestep before forward pass (uses first sample's timestep)
        if self.correction_controller is not None:
            self.correction_controller.set_timestep(t[0])

        noise_pred = self.forward_unet(
            latents_noisy, t, prompt_embeds, cond_latents,
            depth_imgs=None, depth_imgs_2=None,
            added_cond_kwargs=added_cond_kwargs, is_training=True,
            geo_feats=geo_feats,
        )
        # Clear geo_feats after forward to avoid memory leak
        self._clear_geo_feats_on_wrappers()

        # Compute loss
        loss, loss_dict = self.compute_loss(
            noise_pred, noise, target_imgs, mask, weight_dtype,
            depth_imgs=real_depth_imgs, normal_imgs=normal_imgs,
        )

        self.log_dict(loss_dict, prog_bar=True, logger=True, on_step=True, on_epoch=True)
        self.log("global_step", self.global_step, prog_bar=True, logger=True, on_step=True, on_epoch=False)
        lr = self.optimizers().param_groups[0]['lr']
        self.log('lr_abs', lr, prog_bar=True, logger=True, on_step=True, on_epoch=False)

        return loss

    def compute_loss(self, noise_pred, noise_gt, target_imgs=None, mask=None,
                     weight_dtype=torch.float16, depth_imgs=None, normal_imgs=None):
        """Compute combined loss: MSE + foreground + SSIM + edge + regularization.

        All losses are in latent space (noise prediction).

        Args:
            noise_pred: predicted noise (B, 4, H/8, W/8)
            noise_gt: ground truth noise (B, 4, H/8, W/8)
            target_imgs: target images (B, 3, 3H, 2W) — unused (kept for API compat)
            mask: foreground mask (B, 1, 3H, 2W) — for foreground weighting
            depth_imgs: depth map (B, 1, 3H, 2W) — for edge weighting
            normal_imgs: normal map (B, 3, 3H, 2W) — for edge weighting
        """
        loss_dict = {}
        latent_h, latent_w = noise_pred.shape[2], noise_pred.shape[3]
        base_mse = F.mse_loss(noise_pred, noise_gt, reduction='none')  # (B, 4, H, W)

        # Build spatial weight map: foreground_boost * edge_boost
        spatial_weight = torch.ones_like(base_mse)

        # Foreground boost: foreground_loss_weight controls how much more we weight foreground
        # E.g., 0.3 means foreground gets 1.3x weight, background gets 1.0x
        if mask is not None and self.foreground_loss_weight > 0:
            mask_latent = F.interpolate(mask, size=(latent_h, latent_w), mode='bilinear', align_corners=False)
            fg_boost = 1.0 + self.foreground_loss_weight * mask_latent
            spatial_weight = spatial_weight * fg_boost.expand_as(noise_pred)

        # Edge boost: edge_loss_weight controls how much more we weight edges
        if self.edge_loss_weight > 0 and (depth_imgs is not None or normal_imgs is not None):
            edge_source = depth_imgs.float() if depth_imgs is not None else normal_imgs.float()
            edge_mask = compute_edge_mask(edge_source, threshold=0.1)
            edge_latent = F.interpolate(edge_mask, size=(latent_h, latent_w), mode='bilinear', align_corners=False)
            edge_boost = 1.0 + self.edge_loss_weight * edge_latent
            spatial_weight = spatial_weight * edge_boost.expand_as(noise_pred)

        # Combined noise loss
        noise_loss = (base_mse * spatial_weight).mean()
        loss_dict['train/noise_loss'] = noise_loss
        total_loss = noise_loss

        # SSIM loss in latent space
        if self.ssim_loss_weight > 0:
            mask_latent_for_ssim = None
            if mask is not None:
                mask_latent_for_ssim = F.interpolate(mask, size=(latent_h, latent_w),
                                                      mode='bilinear', align_corners=False)
            ssim_loss = compute_ssim_loss(noise_pred.float(), noise_gt.float(), mask_latent_for_ssim)
            loss_dict['train/ssim_loss'] = ssim_loss
            total_loss = total_loss + self.ssim_loss_weight * ssim_loss

        # Adapter residual regularization
        if self.adapter_reg_weight > 0:
            reg_loss = torch.tensor(0.0, device=noise_pred.device)
            count = 0
            for name, module in self.unet.named_modules():
                if isinstance(module, GeoTexResnetWrapper) and module._last_correction is not None:
                    reg_loss = reg_loss + module._last_correction.pow(2).mean()
                    count += 1
            if count > 0:
                reg_loss = reg_loss / count
                loss_dict['train/reg_loss'] = reg_loss
                total_loss = total_loss + self.adapter_reg_weight * reg_loss

        loss_dict['train/loss'] = total_loss
        return total_loss, loss_dict

    def on_after_backward(self):
        valid_gradients = True
        for name, param in self.named_parameters():
            if param.grad is not None:
                valid_gradients = not (torch.isnan(param.grad).any() or torch.isinf(param.grad).any())
                if not valid_gradients:
                    break
        if not valid_gradients:
            print('!!!!!! detected inf or nan values in gradients. not updating model parameters !!!!!!!')
            self.zero_grad()
        return super().on_after_backward()

    @torch.no_grad()
    def validation_step(self, batch, batch_idx):
        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = self.prepare_batch_data(batch)
        images_pil = [v2.functional.to_pil_image(cond_imgs[i]) for i in range(cond_imgs.shape[0])]

        outputs = []
        for cond_img in images_pil:
            latent = self.pipeline(cond_img, depth_image=None, num_inference_steps=75, output_type='latent').images
            image = unscale_image(self.pipeline.vae.decode(latent / self.pipeline.vae.config.scaling_factor, return_dict=False)[0])
            image = (image * 0.5 + 0.5).clamp(0, 1)
            outputs.append(image)
        outputs = torch.cat(outputs, dim=0).to(self.device)
        images = torch.cat([target_imgs, outputs], dim=-2)
        self.validation_step_outputs.append(images)

    @torch.no_grad()
    def on_validation_epoch_end(self):
        images = torch.cat(self.validation_step_outputs, dim=0)
        all_images = self.all_gather(images)
        all_images = rearrange(all_images, 'r b c h w -> (r b) c h w')

        if self.global_rank == 0:
            grid = make_grid(all_images, nrow=8, normalize=True, value_range=(0, 1))
            save_image(grid, os.path.join(self.logdir, 'images_val', f'val_{self.global_step:07d}.png'))

        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        lr = getattr(self, 'learning_rate', None) or self._lr or 1e-4

        # Freeze everything
        self.unet.requires_grad_(False)

        # Collect trainable parameters from adapters (inside UNet wrappers) and encoder
        trainable_params = []

        # Find adapter parameters inside wrapped resnets
        for name, module in self.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                for p in module.adapter.parameters():
                    p.requires_grad = True
                    trainable_params.append(p)

        # Add encoder parameters
        for p in self.geo_encoder.parameters():
            p.requires_grad = True
            trainable_params.append(p)

        # Add FAC controller parameters
        if self.correction_controller is not None:
            for p in self.correction_controller.parameters():
                p.requires_grad = True
                trainable_params.append(p)

        total_trainable = sum(p.numel() for p in trainable_params)
        print(f"GeoTex trainable parameters: {total_trainable / 1e6:.2f}M")

        try:
            from deepspeed.ops.adam import DeepSpeedCPUAdam
            optimizer = DeepSpeedCPUAdam(trainable_params, lr=lr)
            print("Using DeepSpeed CPUAdam optimizer")
        except ImportError:
            try:
                import bitsandbytes as bnb
                optimizer = bnb.optim.AdamW8bit(trainable_params, lr=lr)
                print("Using 8-bit AdamW optimizer")
            except ImportError:
                optimizer = torch.optim.AdamW(trainable_params, lr=lr)
                print("Using standard AdamW optimizer")

        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, 3000, eta_min=lr / 4)
        return {'optimizer': optimizer, 'lr_scheduler': scheduler}

    def save_geotex_weights(self, save_path):
        """Save adapter, encoder, and FAC controller weights."""
        # Collect adapter state dicts from wrapped resnets
        adapter_states = []
        for name, module in self.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                adapter_states.append(module.adapter.state_dict())

        state = {
            'adapters': adapter_states,
            'encoder': self.geo_encoder.state_dict(),
        }

        # Save FAC controller if present
        if self.correction_controller is not None:
            state['fac_controller'] = self.correction_controller.state_dict()

        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        torch.save(state, save_path)
        print(f"Saved GeoTex weights to {save_path}")

    def load_geotex_weights(self, load_path):
        """Load adapter, encoder, and FAC controller weights."""
        state = torch.load(load_path, map_location='cpu')

        # Load adapter state dicts into wrapped resnets
        adapter_modules = []
        for name, module in self.unet.named_modules():
            if isinstance(module, GeoTexResnetWrapper):
                adapter_modules.append(module.adapter)

        if len(adapter_modules) == len(state['adapters']):
            for adapter, s in zip(adapter_modules, state['adapters']):
                adapter.load_state_dict(s)
        else:
            # Fallback: try loading from self.adapters
            for i, s in enumerate(state['adapters']):
                if i < len(self.adapters):
                    self.adapters[i].load_state_dict(s)

        self.geo_encoder.load_state_dict(state['encoder'])

        # Load FAC controller if present in checkpoint and model has one
        if self.correction_controller is not None and 'fac_controller' in state:
            self.correction_controller.load_state_dict(state['fac_controller'])
            print(f"  Loaded FAC controller weights")
        elif self.correction_controller is not None:
            print(f"  FAC controller enabled but not in checkpoint — using initialized weights")

        print(f"Loaded GeoTex weights from {load_path}")
