"""
Test maximum batch size for attn1 (self-attention with reference attention).

Key memory factors for attn1:
1. Self-attention: Q, K, V all from hidden_states (dim = hidden_size)
2. Reference attention doubles sequence length in "read" mode
3. Forward pass runs TWICE (write + read)
4. Attention matrix: O(seq_len^2 * heads * batch)

SDXL UNet hidden sizes by resolution:
- 32x48 (1024x1536 latent): hidden_size varies by block (640/1280/1920)
- Attention seq_len = spatial_resolution (e.g., 32*48=1536)
- With reference attention: seq_len doubles to 2*1536=3072 in read mode
"""
import torch
import torch.nn as nn
import gc
import sys
import os

# Add project to path
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')


def get_gpu_memory():
    """Return (used, total) in MB for GPU 1 (the free one)."""
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        used = torch.cuda.max_memory_allocated() / 1024 / 1024
        reserved = torch.cuda.max_memory_reserved() / 1024 / 1024
        return used, reserved
    return 0, 0


def reset_gpu_memory():
    """Reset GPU memory tracking."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()


class SimpleSelfAttn(nn.Module):
    """Simulate attn1 (self-attention) with reference attention."""

    def __init__(self, hidden_size, num_heads=20):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        self.to_q = nn.Linear(hidden_size, hidden_size)
        self.to_k = nn.Linear(hidden_size, hidden_size)
        self.to_v = nn.Linear(hidden_size, hidden_size)
        self.to_out = nn.Linear(hidden_size, hidden_size)

    def forward(self, hidden_states, encoder_hidden_states=None, mode="w", ref_kv=None):
        """
        hidden_states: (B, seq_len, hidden_size)
        encoder_hidden_states: (B, seq_len, hidden_size) - same as hidden for self-attn
        mode: "w" = write (store ref), "r" = read (concat ref)
        ref_kv: dict to store/read reference features
        """
        B, seq_len, _ = hidden_states.shape

        # Self-attention: Q from hidden_states, K/V from encoder_hidden_states
        if encoder_hidden_states is None:
            encoder_hidden_states = hidden_states

        q = self.to_q(hidden_states)
        k = self.to_k(encoder_hidden_states)
        v = self.to_v(encoder_hidden_states)

        # Reference attention: in read mode, concat ref features to k, v
        if mode == "r" and ref_kv is not None and "k" in ref_kv:
            k = torch.cat([k, ref_kv["k"]], dim=1)
            v = torch.cat([v, ref_kv["v"]], dim=1)

        # Store reference for write mode
        if mode == "w" and ref_kv is not None:
            ref_kv["k"] = k.detach()
            ref_kv["v"] = v.detach()

        # Reshape for multi-head attention
        q = q.view(B, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, -1, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # Attention computation
        attn = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn = torch.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)

        # Reshape back
        out = out.transpose(1, 2).contiguous().view(B, seq_len, self.hidden_size)
        out = self.to_out(out)

        return out


class UNetBlock(nn.Module):
    """Simulate one UNet transformer block with attn1."""

    def __init__(self, hidden_size, num_heads=20):
        super().__init__()
        self.norm = nn.LayerNorm(hidden_size)
        self.attn1 = SimpleSelfAttn(hidden_size, num_heads)
        self.ff = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size),
        )

    def forward(self, x, mode="w", ref_kv=None):
        h = self.norm(x)
        h = self.attn1(h, mode=mode, ref_kv=ref_kv)
        x = x + h
        x = x + self.ff(self.norm(x))
        return x


def test_batch_size(batch_size, hidden_size=1280, seq_len=1536, num_blocks=4, device="cuda:0"):
    """
    Test if a given batch size can run through attn1 blocks.
    Simulates the double forward pass (write + read) of RefOnlyNoisedUNet.
    """
    try:
        reset_gpu_memory()

        # Create blocks (simulating UNet transformer blocks)
        blocks = nn.ModuleList([
            UNetBlock(hidden_size, num_heads=hidden_size // 64)
            for _ in range(num_blocks)
        ]).to(device).to(torch.float16)

        # Create input: (B, seq_len, hidden_size)
        x = torch.randn(batch_size, seq_len, hidden_size, device=device, dtype=torch.float16)

        # First forward pass: write mode (reference image)
        ref_dict = {}
        h = x
        for block in blocks:
            h = block(h, mode="w", ref_kv=ref_dict)

        # Second forward pass: read mode (target image, concat ref features)
        h2 = x.clone()
        for block in blocks:
            h2 = block(h2, mode="r", ref_kv=ref_dict)

        # Compute loss and backward
        loss = h2.mean()
        loss.backward()

        torch.cuda.synchronize()
        peak_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024

        # Cleanup
        del blocks, x, h, h2, ref_dict, loss
        reset_gpu_memory()

        return True, peak_mem

    except torch.cuda.OutOfMemoryError:
        reset_gpu_memory()
        return False, -1
    except Exception as e:
        reset_gpu_memory()
        return False, str(e)


def test_with_real_model(batch_size, device="cuda:0"):
    """Test with the actual MVPainter model if available."""
    try:
        reset_gpu_memory()

        from diffusers import UNet2DConditionModel, EulerAncestralDiscreteScheduler, DDPMScheduler
        from mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline
        from lora_utils_attn1 import create_lora_processors_attn1_only

        # Try to load the model
        model_path = None
        # Check common paths
        for path in [
            "/4T/CXY/MV-Painter/checkpoints/hf_repo",
            "/4T/CXY/MV-Painter/checkpoints/sdxl",
            "/4T/CXY/MV-Painter/pretrained_models/sdxl",
        ]:
            if os.path.exists(path):
                model_path = path
                break

        if model_path is None:
            print("Cannot find SDXL model, using simulated blocks")
            return None

        print(f"Loading model from {model_path}...")
        pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True).to(device)
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline.scheduler.config, timestep_spacing='trailing'
        )

        # Set up attn1-only LoRA
        lora_processors = create_lora_processors_attn1_only(pipeline.unet, rank=4, network_alpha=4)
        pipeline.unet.set_attn_processor(lora_processors)

        # Wrap in RefOnlyNoisedUNet
        train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)
        pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, train_sched, pipeline.scheduler, replace_processors=False)
        pipeline.unet.enable_gradient_checkpointing()

        # Create dummy inputs
        # Latent shape for SDXL: (B, 4, 128, 192) for 1024x1536
        latent_h, latent_w = 32, 48  # 1024/8 / 2, 1536/8 / 2 (or similar)
        latents = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        cond_lat = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        prompt_embeds = torch.randn(batch_size, 77, 2048, device=device, dtype=torch.float16)
        t = torch.randint(0, 1000, (batch_size,), device=device).long()

        # Added cond kwargs for SDXL
        added_cond_kwargs = {
            "text_embeds": torch.randn(batch_size, 1280, device=device, dtype=torch.float16),
            "time_ids": torch.randn(batch_size, 6, device=device, dtype=torch.float16),
        }

        # Forward pass
        cross_attention_kwargs = dict(cond_lat=cond_lat)
        pred = pipeline.unet(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=True,
        )[0]

        loss = pred.mean()
        loss.backward()

        torch.cuda.synchronize()
        peak_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024

        del pred, loss, latents, cond_lat, prompt_embeds
        reset_gpu_memory()

        return True, peak_mem

    except torch.cuda.OutOfMemoryError:
        reset_gpu_memory()
        return False, -1
    except Exception as e:
        reset_gpu_memory()
        return False, str(e)


def run_tests():
    """Run batch size tests."""
    device = "cuda:0"  # Use first visible GPU (set CUDA_VISIBLE_DEVICES to pick GPU)

    print("=" * 70)
    print("attn1 Batch Size Test")
    print("=" * 70)
    print(f"Device: {device}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024:.0f} MB")
    print()

    # First try with real model
    print("-" * 70)
    print("Phase 1: Testing with real MVPainter model")
    print("-" * 70)

    real_model_works = False
    for bs in [1, 2, 4, 8, 16]:
        print(f"\n  Testing batch_size={bs}...", end=" ", flush=True)
        success, mem = test_with_real_model(bs, device)
        if success:
            print(f"✓ OK, peak memory: {mem:.0f} MB")
            real_model_works = True
        else:
            if mem == -1:
                print(f"✗ OOM")
            else:
                print(f"✗ Error: {mem}")
            break

    if not real_model_works:
        print("\n  Real model not available, using simulated blocks.")

    # Simulated tests with different configurations
    print()
    print("-" * 70)
    print("Phase 2: Simulated attn1 memory tests")
    print("-" * 70)

    configs = [
        # (hidden_size, seq_len, num_blocks, description)
        (640, 1536, 4, "SDXL low-res block (640d, 32x48)"),
        (1280, 384, 4, "SDXL mid-res block (1280d, 16x24)"),
        (1280, 1536, 4, "SDXL full-res block (1280d, 32x48)"),
        (1920, 96, 4, "SDXL high-res block (1920d, 8x12)"),
        (640, 1536, 8, "SDXL low-res 8 blocks (640d, 32x48)"),
        (1280, 384, 8, "SDXL mid-res 8 blocks (1280d, 16x24)"),
    ]

    results = {}

    for hidden_size, seq_len, num_blocks, desc in configs:
        print(f"\n  Config: {desc}")
        print(f"  hidden_size={hidden_size}, seq_len={seq_len}, blocks={num_blocks}")
        print(f"  Reference attention: seq_len doubles to {seq_len*2} in read mode")

        # Binary search for max batch size
        lo, hi = 1, 32
        max_bs = 0
        max_mem = 0

        while lo <= hi:
            mid = (lo + hi) // 2
            print(f"    Testing batch_size={mid}...", end=" ", flush=True)
            success, mem = test_batch_size(mid, hidden_size, seq_len, num_blocks, device)
            if success:
                print(f"✓ {mem:.0f} MB")
                max_bs = mid
                max_mem = mem
                lo = mid + 1
            else:
                if mem == -1:
                    print("✗ OOM")
                else:
                    print(f"✗ {mem}")
                hi = mid - 1

        results[desc] = (max_bs, max_mem)
        print(f"  → Max batch_size: {max_bs} (peak memory: {max_mem:.0f} MB)")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Config':<50} {'Max BS':>8} {'Peak MB':>10}")
    print("-" * 70)
    for desc, (max_bs, max_mem) in results.items():
        print(f"{desc:<50} {max_bs:>8} {max_mem:>10.0f}")

    # Estimate for full UNet
    print()
    print("-" * 70)
    print("Estimated batch sizes for full UNet attn1 training:")
    print("  (Full UNet has ~20+ transformer blocks across all resolutions)")
    print()
    # The bottleneck is typically the highest resolution blocks (largest seq_len)
    # Full forward pass = sum of all blocks' memory
    # But gradient checkpointing means only one block's activations at a time
    print("  With gradient checkpointing (current setup):")
    print("  - Bottleneck: highest resolution self-attention (32x48 = 1536 seq_len)")
    print("  - Reference attention doubles this to 3072 in read mode")
    print("  - Attention matrix per head: (1536 x 3072) x batch_size")
    print()

    # Calculate theoretical memory for attention matrix
    for bs in [1, 2, 4, 8, 16]:
        # For hidden_size=1280, num_heads=20
        heads = 20
        attn_mem = bs * heads * 1536 * 3072 * 2 / 1024 / 1024  # fp16 = 2 bytes
        print(f"  batch_size={bs}: attention matrix alone = {attn_mem:.0f} MB")


if __name__ == "__main__":
    run_tests()
