"""
Test maximum batch size for attn1 using the REAL MVPainter UNet.
Run with: CUDA_VISIBLE_DEVICES=1 python mvp-lora-script/test_attn1_real_model.py
"""
import torch
import torch.nn as nn
import gc
import sys
import os

# Add project paths
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter/mvpainter')

from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler, UNet2DConditionModel
from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline
from mvpainter.lora_utils_attn1 import create_lora_processors_attn1_only


def reset_gpu():
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()


def test_real_model(batch_size, device="cuda:0"):
    """Test with actual MVPainter UNet + attn1 LoRA + reference attention."""
    try:
        reset_gpu()

        model_path = "/4T/CXY/MV-Painter/checkpoints/hf_repo"
        print(f"  Loading pipeline from {model_path}...")

        pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True)
        pipeline = pipeline.to(device)
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline.scheduler.config, timestep_spacing='trailing'
        )

        # Set up attn1-only LoRA (rank=4, matching training config)
        lora_processors = create_lora_processors_attn1_only(pipeline.unet, rank=4, network_alpha=4)
        pipeline.unet.set_attn_processor(lora_processors)

        # Wrap in RefOnlyNoisedUNet (replace_processors=False since we already set them)
        train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)
        pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, train_sched, pipeline.scheduler, replace_processors=False)

        # Enable gradient checkpointing (same as training)
        if hasattr(pipeline.unet, 'enable_gradient_checkpointing'):
            pipeline.unet.enable_gradient_checkpointing()

        print(f"  Model loaded. Creating batch_size={batch_size} inputs...")

        # Create dummy inputs matching training data format
        # Latent shape for SDXL: (B, 4, H/8, W/8)
        # img_size=256, target images are 3x2 grid of 256x256 = 768x512
        # After VAE encode: ~96x64, but let's use typical 32x48
        latent_h, latent_w = 32, 48
        latents = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        cond_lat = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        prompt_embeds = torch.randn(batch_size, 77, 2048, device=device, dtype=torch.float16)
        t = torch.randint(0, 1000, (batch_size,), device=device).long()

        # SDXL added_cond_kwargs
        added_cond_kwargs = {
            "text_embeds": torch.randn(batch_size, 1280, device=device, dtype=torch.float16),
            "time_ids": torch.randn(batch_size, 6, device=device, dtype=torch.float16),
        }

        # Forward pass (double forward: write + read)
        cross_attention_kwargs = dict(cond_lat=cond_lat)
        print(f"  Running forward pass (write + read mode)...")
        pred = pipeline.unet(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=True,
        )[0]

        # Backward pass
        print(f"  Running backward pass...")
        loss = pred.mean()
        loss.backward()

        torch.cuda.synchronize()
        peak_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024

        # Cleanup
        del pred, loss, latents, cond_lat, prompt_embeds, added_cond_kwargs
        del pipeline
        reset_gpu()

        return True, peak_mem

    except torch.cuda.OutOfMemoryError:
        reset_gpu()
        try:
            del pipeline
        except:
            pass
        reset_gpu()
        return False, -1
    except Exception as e:
        reset_gpu()
        try:
            del pipeline
        except:
            pass
        reset_gpu()
        return False, str(e)


def main():
    device = "cuda:0"

    print("=" * 70)
    print("attn1 Real Model Batch Size Test")
    print("=" * 70)
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024:.0f} MB")
    print(f"Model: MVPainter (SDXL-based) + attn1-only LoRA (rank=4)")
    print(f"Reference attention: enabled on attn1 (double forward pass)")
    print()

    # Binary search for max batch size
    lo, hi = 1, 16
    max_bs = 0
    max_mem = 0

    while lo <= hi:
        bs = (lo + hi) // 2
        print(f"Testing batch_size={bs}...")
        success, mem = test_real_model(bs, device)
        if success:
            print(f"  ✓ OK, peak memory: {mem:.0f} MB")
            max_bs = bs
            max_mem = mem
            lo = bs + 1
        else:
            if mem == -1:
                print(f"  ✗ OOM")
            else:
                print(f"  ✗ Error: {mem}")
            hi = bs - 1

    print()
    print("=" * 70)
    print(f"RESULT: Max batch_size for attn1 training = {max_bs}")
    print(f"Peak GPU memory at max batch_size: {max_mem:.0f} MB")
    print(f"Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024:.0f} MB")
    print("=" * 70)

    # Also test a few specific sizes for detailed profiling
    print()
    print("Detailed profiling:")
    for bs in [1, 2, 4, 8]:
        if bs <= max_bs + 2:
            print(f"  batch_size={bs}...", end=" ", flush=True)
            success, mem = test_real_model(bs, device)
            if success:
                print(f"✓ {mem:.0f} MB")
            else:
                print(f"✗ OOM")


if __name__ == "__main__":
    main()
