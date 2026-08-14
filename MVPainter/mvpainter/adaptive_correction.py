"""
Adaptive Correction Modules for GeoTex-Adapter.

Three orthogonal innovations beyond hand-crafted TCAS:

1. LTAG (Learned Timestep-Adaptive Gating):
   - Replaces hand-crafted 3-phase schedule with learned per-layer timestep scaling.
   - MLP: timestep_emb → per-adapter scale factors.
   - Initialized to approximate TCAS for stable warm-start.

2. GSG (Geometry-Conditioned Spatial Gating):
   - Generates spatial attention mask from geometry features.
   - High curvature/edge → strong correction; flat/textured → weak correction.
   - Content-adaptive, solving TCAS's spatially-uniform limitation.

3. FSC (Frequency-Selective Correction):
   - Applies learnable frequency-domain filtering to adapter correction.
   - Preserves low/mid-freq (geometry) while bypassing high-freq (texture).
   - Theoretically grounded: geometry = low-freq structure, texture = high-freq detail.

Combined: correction_final = FSC(correction * LTAG_scale * GSG_gate)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================
# 1. Learned Timestep-Adaptive Gating (LTAG)
# ============================================================

class LearnedTimestepGating(nn.Module):
    """Learns per-adapter scale factors conditioned on denoising timestep.

    Replaces the hand-crafted TCAS 3-phase schedule with a continuous,
    per-layer learned function t → scales.

    Architecture:
        sinusoidal_emb(t) → MLP → sigmoid → [scale_min, scale_max] per adapter

    Parameters: ~2K for 9 adapters (negligible vs 2.2M total).
    """

    def __init__(self, num_adapters=9, emb_dim=64, hidden_dim=32,
                 scale_min=0.0, scale_max=3.0, init_schedule=None):
        """
        Args:
            num_adapters: number of adapter injection points
            emb_dim: timestep embedding dimension
            hidden_dim: MLP hidden dimension
            scale_min: minimum output scale
            scale_max: maximum output scale
            init_schedule: dict with 'early', 'mid', 'late' values for TCAS warm-start
        """
        super().__init__()
        self.num_adapters = num_adapters
        self.emb_dim = emb_dim
        self.scale_min = scale_min
        self.scale_max = scale_max

        # Sinusoidal timestep embedding
        self.time_embed = nn.Sequential(
            nn.Linear(emb_dim, hidden_dim),
            nn.SiLU(),
        )

        # Per-adapter scale prediction
        self.scale_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, num_adapters),
        )

        # Initialize to approximate TCAS if provided
        if init_schedule is not None:
            self._init_from_tcas(init_schedule)

    def _init_from_tcas(self, schedule):
        """Initialize weights so output approximates TCAS at t=0, 0.5, 1.0.

        TCAS: early=1.25, mid=2.50, late=1.25 (default).
        We initialize bias to produce mid-range (average of schedule values)
        so initial behavior is close to TCAS uniform average.

        IMPORTANT: Use small non-zero weights (not zeros) so gradients flow
        through the entire network from step 1.
        """
        avg_scale = (schedule.get('early', 1.25) +
                     schedule.get('mid', 2.50) +
                     schedule.get('late', 1.25)) / 3.0
        # Set final layer bias so sigmoid output maps to avg_scale
        target_sigmoid = (avg_scale - self.scale_min) / (self.scale_max - self.scale_min)
        target_sigmoid = max(0.01, min(0.99, target_sigmoid))
        bias_val = math.log(target_sigmoid / (1 - target_sigmoid))  # inverse sigmoid

        # Small random weights (NOT zeros) to ensure gradient flow from step 1
        nn.init.normal_(self.scale_head[-1].weight, std=0.01)
        nn.init.constant_(self.scale_head[-1].bias, bias_val)

    def get_timestep_embedding(self, timestep, max_period=10000):
        """Sinusoidal timestep embedding (same as diffusion models).

        Args:
            timestep: (B,) or scalar, normalized to [0, 1000]
        Returns:
            (B, emb_dim) embedding
        """
        if isinstance(timestep, (int, float)):
            timestep = torch.tensor([timestep], dtype=torch.float32)
        if timestep.dim() == 0:
            timestep = timestep.unsqueeze(0)

        half_dim = self.emb_dim // 2
        freqs = torch.exp(
            -math.log(max_period) * torch.arange(half_dim, device=timestep.device, dtype=torch.float32) / half_dim
        )
        args = timestep.float().unsqueeze(-1) * freqs.unsqueeze(0)
        embedding = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)

        if self.emb_dim % 2 == 1:
            embedding = F.pad(embedding, (0, 1))

        return embedding

    def forward(self, timestep):
        """Predict per-adapter scales for given timestep.

        Args:
            timestep: scalar or (B,) tensor — current denoising timestep [0, 1000]
        Returns:
            scales: (num_adapters,) or (B, num_adapters) in [scale_min, scale_max]
        """
        emb = self.get_timestep_embedding(timestep)  # (B, emb_dim)
        emb = emb.to(next(self.parameters()).device)
        h = self.time_embed(emb)  # (B, hidden_dim)
        raw = self.scale_head(h)  # (B, num_adapters)
        # Map to [scale_min, scale_max] via sigmoid
        scales = self.scale_min + (self.scale_max - self.scale_min) * torch.sigmoid(raw)

        if scales.shape[0] == 1:
            scales = scales.squeeze(0)  # (num_adapters,)
        return scales


# ============================================================
# 2. Geometry-Conditioned Spatial Gating (GSG)
# ============================================================

class SpatialGeometryGate(nn.Module):
    """Generates spatial residual gate from geometry features.

    Residual form: gate = 1 + tanh(conv(geo_feat)) in [0, 2], neutral 1.0.
    High curvature / edge regions → gate > 1 (amplify correction)
    Flat / texture-rich regions → gate < 1 (attenuate correction, preserve texture)

    The residual parameterization is chosen so that the neutral position is
    exactly 1.0 (identity) and tanh'(0) = 1 keeps a full gradient at init;
    a plain sigmoid with a high bias init saturates and stalls training.

    Architecture:
        geo_feat (B, C, H, W) → 1×1 conv → 1 + tanh → spatial_gate (B, 1, H, W)

    Parameters: ~130 per adapter (64 weights + 1 bias for 1×1 conv).
    """

    def __init__(self, geo_channels=64, init_bias=0.0):
        """
        Args:
            geo_channels: input channels from geometry encoder
            init_bias: initial bias (default 0 → gate = 1 + tanh(0) = 1, identity).
        """
        super().__init__()
        self.gate_conv = nn.Conv2d(geo_channels, 1, kernel_size=1)

        # Zero weights + zero bias → gate = 1 + tanh(0) = 1 everywhere at start.
        # This makes the initial FAC position exactly neutral (no degradation)
        # while keeping a full gradient (tanh'(0) = 1) through the gate.
        nn.init.zeros_(self.gate_conv.weight)
        nn.init.constant_(self.gate_conv.bias, init_bias)

    def forward(self, geo_feat):
        """Compute spatial gate from geometry features.

        Args:
            geo_feat: (B, C, H, W) geometry features from encoder
        Returns:
            gate: (B, 1, H, W) in [0, 2], neutral 1.0
        """
        return 1.0 + torch.tanh(self.gate_conv(geo_feat.float()))


# ============================================================
# 3. Frequency-Selective Correction (FSC)
# ============================================================

class FrequencySelectiveFilter(nn.Module):
    """Applies learnable frequency-domain filtering to adapter correction.

    Filters correction in DCT domain: preserves low/mid frequencies (geometry)
    while attenuating high frequencies (texture details).

    Architecture:
        correction → 2D DCT → element-wise × frequency_mask → IDCT → filtered

    The frequency mask is learnable (per-channel shared spatially), initialized
    as a smooth low-pass filter.

    Parameters: H_dct × W_dct (e.g., 32×32 = 1024 for the smallest resolution).
    Since adapter outputs vary in spatial size, we use a fixed-size mask and
    interpolate to match.
    """

    def __init__(self, mask_size=16, init_cutoff=0.85, init_sharpness=3.0):
        """
        Args:
            mask_size: size of the learnable frequency mask (square)
            init_cutoff: initial normalized cutoff frequency (0=DC only, 1=all pass).
                         Default 0.85 → near-all-pass, only highest 15% of freq attenuated.
                         This ensures minimal degradation before training converges.
            init_sharpness: sharpness of initial low-pass rolloff
        """
        super().__init__()
        self.mask_size = mask_size

        # Residual parameterization in the mask domain:
        #   mask = init_mask + tanh(residual), clamped to [0, 1]
        # The base all-pass mask is a fixed buffer (neutral position), and the
        # learnable residual starts at 0, so the initial FAC position is exactly
        # the near-all-pass filter while tanh'(0) = 1 gives a direct gradient.
        init_mask = torch.sigmoid(self._create_lowpass_init(mask_size, init_cutoff, init_sharpness))
        self.register_buffer('_init_mask', init_mask)
        self.freq_mask_residual = nn.Parameter(torch.zeros_like(init_mask))

    def _create_lowpass_init(self, size, cutoff, sharpness):
        """Create initial low-pass filter mask in logit space.

        Smooth radial falloff: high values (pass) at low freq, low values (block) at high freq.
        """
        # Normalized frequency coordinates [0, 1]
        coords = torch.linspace(0, 1, size)
        fy, fx = torch.meshgrid(coords, coords, indexing='ij')
        # Radial frequency (normalized to [0, 1] at corner)
        freq_radius = torch.sqrt(fx ** 2 + fy ** 2) / math.sqrt(2)

        # Sigmoid-shaped rolloff in logit space
        # logit(sigma(x)) = x, so we set x = sharpness * (cutoff - freq_radius)
        mask_logit = sharpness * (cutoff - freq_radius)
        return mask_logit

    @property
    def freq_mask(self):
        """Get the frequency mask in [0, 1] range."""
        return (self._init_mask + torch.tanh(self.freq_mask_residual)).clamp(0, 1)

    def forward(self, correction):
        """Apply frequency-selective filtering to correction.

        Args:
            correction: (B, C, H, W) adapter correction tensor
        Returns:
            filtered: (B, C, H, W) filtered correction (low/mid freq preserved)
        """
        B, C, H, W = correction.shape
        x = correction.float()

        # 2D DCT via FFT (Type-II DCT approximation using real FFT)
        # torch.fft.rfft2 gives us the frequency representation
        X_freq = torch.fft.rfft2(x, norm='ortho')

        # Get mask and resize to match frequency domain shape
        mask = self.freq_mask.to(x.device)  # (mask_size, mask_size)

        # rfft2 output shape: (B, C, H, W//2+1)
        freq_h, freq_w = X_freq.shape[2], X_freq.shape[3]

        # Interpolate mask to match frequency domain dimensions
        mask_resized = F.interpolate(
            mask.unsqueeze(0).unsqueeze(0),  # (1, 1, ms, ms)
            size=(freq_h, freq_w),
            mode='bilinear',
            align_corners=False,
        ).squeeze(0).squeeze(0)  # (freq_h, freq_w)

        # Apply mask (broadcast across B and C)
        X_filtered = X_freq * mask_resized.unsqueeze(0).unsqueeze(0)

        # Inverse FFT to get filtered correction
        filtered = torch.fft.irfft2(X_filtered, s=(H, W), norm='ortho')

        return filtered.to(correction.dtype)


# ============================================================
# Combined Adaptive Correction Controller
# ============================================================

class AdaptiveCorrectionController(nn.Module):
    """Unified controller for all three adaptive correction modules.

    Manages LTAG + GSG + FSC as a coherent system.
    Supports incremental activation (any subset of modules can be enabled).

    Usage:
        controller = AdaptiveCorrectionController(num_adapters=9, ...)
        controller.set_timestep(t)  # call once per denoising step
        correction = controller.apply(correction, geo_feat, adapter_idx)
    """

    def __init__(self, num_adapters=9, geo_channels=64,
                 enable_ltag=True, enable_gsg=True, enable_fsc=True,
                 ltag_kwargs=None, gsg_kwargs=None, fsc_kwargs=None):
        """
        Args:
            num_adapters: number of adapter injection points
            geo_channels: channels from geometry encoder
            enable_ltag: enable Learned Timestep-Adaptive Gating
            enable_gsg: enable Geometry-Conditioned Spatial Gating
            enable_fsc: enable Frequency-Selective Correction
            ltag_kwargs: extra kwargs for LearnedTimestepGating
            gsg_kwargs: extra kwargs for SpatialGeometryGate
            fsc_kwargs: extra kwargs for FrequencySelectiveFilter
        """
        super().__init__()
        self.num_adapters = num_adapters
        self.enable_ltag = enable_ltag
        self.enable_gsg = enable_gsg
        self.enable_fsc = enable_fsc

        # LTAG: one shared module
        if enable_ltag:
            ltag_kw = ltag_kwargs or {}
            self.ltag = LearnedTimestepGating(num_adapters=num_adapters, **ltag_kw)
        else:
            self.ltag = None

        # GSG: one per adapter
        if enable_gsg:
            gsg_kw = gsg_kwargs or {}
            self.gsg_modules = nn.ModuleList([
                SpatialGeometryGate(geo_channels=geo_channels, **gsg_kw)
                for _ in range(num_adapters)
            ])
        else:
            self.gsg_modules = None

        # FSC: one per adapter
        if enable_fsc:
            fsc_kw = fsc_kwargs or {}
            self.fsc_modules = nn.ModuleList([
                FrequencySelectiveFilter(**fsc_kw)
                for _ in range(num_adapters)
            ])
        else:
            self.fsc_modules = None

        # Cached LTAG scales for current timestep
        self._current_scales = None

    def set_timestep(self, timestep):
        """Pre-compute LTAG scales for current timestep.

        Call once per denoising step before processing all adapters.
        """
        if self.ltag is not None:
            self._current_scales = self.ltag(timestep)
        else:
            self._current_scales = None

    def apply(self, correction, geo_feat, adapter_idx, max_scale=None):
        """Apply adaptive correction pipeline.

        Order: LTAG (temporal) → GSG (spatial) → FSC (frequency)

        Args:
            correction: (B, C, H, W) raw adapter correction
            geo_feat: (B, geo_ch, H, W) geometry features at matching resolution
            adapter_idx: int, index of this adapter (for per-adapter modules)
            max_scale: optional per-adapter cap on the LTAG temporal scale,
                matching the per-layer caps applied to the hand-coded TCAS
                schedule (deep 3.0 / middle 3.5 / shallow 0.8). With this cap,
                an LTAG initialized to the effective C3 schedule reproduces TCAS
                exactly at every layer, so the ablation isolates the learned
                temporal rule rather than a difference in injection limits.
        Returns:
            (B, C, H, W) adaptively modulated correction (same dtype as input)
        """
        input_dtype = correction.dtype
        out = correction

        # 1. LTAG: temporal gating (scalar per adapter), capped to the same
        #    per-layer maximum as the TCAS _adapter_scale path.
        if self._current_scales is not None and self.enable_ltag:
            scale = self._current_scales[adapter_idx]  # scalar
            if max_scale is not None:
                scale = min(scale, max_scale)
            out = out * scale

        # 2. GSG: spatial gating
        if self.gsg_modules is not None and self.enable_gsg:
            gate = self.gsg_modules[adapter_idx](geo_feat)  # (B, 1, H, W)
            out = out * gate

        # 3. FSC: frequency filtering
        if self.fsc_modules is not None and self.enable_fsc:
            out = self.fsc_modules[adapter_idx](out)

        # Preserve input dtype (GSG/FSC compute in float32 internally)
        return out.to(input_dtype)

    def param_count(self):
        """Report parameter counts per module."""
        counts = {}
        if self.ltag is not None:
            counts['ltag'] = sum(p.numel() for p in self.ltag.parameters())
        if self.gsg_modules is not None:
            counts['gsg'] = sum(p.numel() for p in self.gsg_modules.parameters())
        if self.fsc_modules is not None:
            counts['fsc'] = sum(p.numel() for p in self.fsc_modules.parameters())
        counts['total'] = sum(counts.values())
        return counts
