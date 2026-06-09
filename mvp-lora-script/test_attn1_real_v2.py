"""
Test maximum batch size for attn1 using REAL UNet.
LoRA overhead is negligible - the bottleneck is reference attention's double forward pass.
We test with the base UNet + ReferenceOnlyAttnProc to measure the actual memory ceiling.

Run: CUDA_VISIBLE_DEVICES=1 python mvp-lora-script/test_attn1_real_v2.py
"""
import torch
import gc
import sys
import os

sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter/mvpainter')

from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler, UNet2DConditionModel
from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline


def reset_gpu():
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()


def get_peak_mb(device):
    torch.cuda.synchronize()
    return torch.cuda.max_memory_allocated(device) / 1024 / 1024


def test_bs(batch_size, pipeline, train_sched, device):
    """Test one forward+backward with given batch_size."""
    try:
        reset_gpu()

        latent_h, latent_w = 32, 48
        dtype = torch.float16

        latents = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=dtype)
        cond_lat = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=dtype)
        prompt_embeds = torch.randn(batch_size, 77, 2048, device=device, dtype=dtype)
        t = torch.randint(0, 1000, (batch_size,), device=device).long()
        added_cond_kwargs = {
            "text_embeds": torch.randn(batch_size, 1280, device=device, dtype=dtype),
            "time_ids": torch.randn(batch_size, 6, device=device, dtype=dtype),
        }

        cross_attention_kwargs = dict(cond_lat=cond_lat)

        # Wrap UNet in RefOnlyNoisedUNet (double forward pass)
        unet_wrapped = RefOnlyNoisedUNet(
            pipeline.unet, train_sched, pipeline.scheduler, replace_processors=True
        )
        unet_wrapped.enable_gradient_checkpointing()

        pred = unet_wrapped(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=True,
        )[0]

        loss = pred.mean()
        loss.backward()

        peak = get_peak_mb(device)

        del pred, loss, latents, cond_lat, prompt_embeds, added_cond_kwargs, unet_wrapped
        reset_gpu()
        return True, peak

    except torch.cuda.OutOfMemoryError:
        reset_gpu()
        return False, -1
    except Exception as e:
        reset_gpu()
        return False, str(e)


def main():
    device = torch.device("cuda:0")
    print("=" * 70)
    print("attn1 Real UNet Batch Size Test (Reference Attention)")
    print("=" * 70)
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    total_mem = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
    print(f"Total Memory: {total_mem:.0f} MB")
    print()

    model_path = "/4T/CXY/MV-Painter/checkpoints/hf_repo"
    print(f"Loading pipeline from {model_path}...")
    pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True, torch_dtype=torch.float16)
    pipeline = pipeline.to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing'
    )
    train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)

    model_mem = get_peak_mb(device)
    print(f"Model loaded. Base memory: {model_mem:.0f} MB")
    reset_gpu()

    # Print UNet info
    unet = pipeline.unet
    total_params = sum(p.numel() for p in unet.parameters())
    print(f"UNet parameters: {total_params / 1e6:.1f}M")

    # Count attn1 modules
    attn1_count = sum(1 for name in unet.attn_processors if 'attn1' in name)
    attn2_count = sum(1 for name in unet.attn_processors if 'attn2' in name)
    print(f"Attention layers: {attn1_count} attn1 (self-attn), {attn2_count} attn2 (cross-attn)")
    print()

    # Get hidden sizes per block
    print("UNet block hidden sizes:")
    for name, proc in unet.attn_processors.items():
        if 'attn1' in name:
            attn_name = name.replace('.processor', '')
            attn_module = dict(unet.named_modules())[attn_name]
            h = attn_module.to_q.in_features
            heads = attn_module.heads if hasattr(attn_module, 'heads') else '?'
            print(f"  {attn_name}: hidden_size={h}, heads={heads}")
    print()

    # Binary search for max batch size
    print("-" * 70)
    print("Binary search for max batch size...")
    print("-" * 70)

    lo, hi = 1, 32
    max_bs = 0
    max_mem = 0
    results = {}

    while lo <= hi:
        bs = (lo + hi) // 2
        print(f"  batch_size={bs}...", end=" ", flush=True)
        ok, mem = test_bs(bs, pipeline, train_sched, device)
        if ok:
            print(f"✓ {mem:.0f} MB")
            results[bs] = mem
            max_bs = bs
            max_mem = mem
            lo = bs + 1
        else:
            if mem == -1:
                print("✗ OOM")
            else:
                print(f"✗ Error: {mem}")
            hi = bs - 1

    # Fine-grained profiling around the boundary
    print()
    print("-" * 70)
    print("Fine-grained profiling...")
    print("-" * 70)
    for bs in range(max(1, max_bs - 2), max_bs + 3):
        if bs not in results and bs <= 32:
            print(f"  batch_size={bs}...", end=" ", flush=True)
            ok, mem = test_bs(bs, pipeline, train_sched, device)
            if ok:
                print(f"✓ {mem:.0f} MB")
                results[bs] = mem
            else:
                print("✗ OOM" if mem == -1 else f"✗ {mem}")

    # Summary
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"{'Batch Size':>12} {'Peak Memory (MB)':>18} {'% of GPU':>10}")
    print("-" * 42)
    for bs in sorted(results.keys()):
        mem = results[bs]
        pct = mem / total_mem * 100
        marker = " ← MAX" if bs == max_bs else ""
        print(f"{bs:>12} {mem:>18.0f} {pct:>9.1f}%{marker}")

    print()
    print(f"Max batch_size for attn1 training: **{max_bs}**")
    print(f"Peak memory at max BS: {max_mem:.0f} MB / {total_mem:.0f} MB ({max_mem/total_mem*100:.1f}%)")
    print()

    # Theoretical analysis
    print("-" * 70)
    print("Memory breakdown analysis:")
    print("-" * 70)
    # The attention matrix for the largest self-attention block
    # hidden_size=1280, seq_len=32*48=1536, heads=20
    # In read mode: seq_len becomes 1536 + 1536 = 3072
    # Attention matrix: B * heads * q_len * kv_len * 2 bytes (fp16)
    for bs in [1, 2, 4, 8, 16]:
        q_len = 1536
        kv_len = 3072  # doubled by reference attention
        heads = 20
        attn_matrix_mb = bs * heads * q_len * kv_len * 2 / 1024 / 1024
        # Q/K/V projections
        proj_mb = bs * q_len * 1280 * 3 * 2 / 1024 / 1024  # Q, K, V
        print(f"  BS={bs}: attn_matrix={attn_matrix_mb:.0f} MB, QKV_proj={proj_mb:.0f} MB (largest block)")


if __name__ == "__main__":
    main()
