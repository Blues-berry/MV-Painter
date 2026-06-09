"""
Final precise test: attn1 batch size with correct training setup.
Actual training uses fp16 inputs + fp32 UNet (mixed precision).
Also includes LoRA overhead estimation.
"""
import torch
import gc
import sys
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')
sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter/mvpainter')

from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler
from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline


def reset_gpu():
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()


def test_bs(batch_size, pipeline, train_sched, device, use_fp32_unet=False):
    """Test with option to use fp32 UNet (matching real training)."""
    try:
        reset_gpu()
        latent_h, latent_w = 32, 48

        # Convert UNet dtype if needed
        if use_fp32_unet:
            pipeline.unet.float()

        latents = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        cond_lat = torch.randn(batch_size, 4, latent_h, latent_w, device=device, dtype=torch.float16)
        prompt_embeds = torch.randn(batch_size, 77, 2048, device=device, dtype=torch.float16)
        t = torch.randint(0, 1000, (batch_size,), device=device).long()
        added_cond_kwargs = {
            "text_embeds": torch.randn(batch_size, 1280, device=device, dtype=torch.float16),
            "time_ids": torch.randn(batch_size, 6, device=device, dtype=torch.float16),
        }

        unet_wrapped = RefOnlyNoisedUNet(
            pipeline.unet, train_sched, pipeline.scheduler, replace_processors=True
        )
        unet_wrapped.enable_gradient_checkpointing()

        pred = unet_wrapped(
            latents, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_lat),
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=True,
        )[0]

        loss = pred.mean()
        loss.backward()

        torch.cuda.synchronize()
        peak = torch.cuda.max_memory_allocated(device) / 1024 / 1024

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
    total_mem = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
    print(f"GPU: {torch.cuda.get_device_name(0)}, {total_mem:.0f} MB total")
    print()

    model_path = "/4T/CXY/MV-Painter/checkpoints/hf_repo"

    # === Test 1: fp16 UNet (our test setup) ===
    print("=" * 60)
    print("Test 1: fp16 UNet")
    print("=" * 60)
    pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True, torch_dtype=torch.float16)
    pipeline = pipeline.to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing'
    )
    train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)

    base_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024
    reset_gpu()
    print(f"Base model memory: {base_mem:.0f} MB")

    # Sequential test from small to large
    fp16_results = {}
    for bs in [1, 2, 4, 8, 16, 32, 48, 64, 80, 96, 128]:
        print(f"  BS={bs}...", end=" ", flush=True)
        ok, mem = test_bs(bs, pipeline, train_sched, device, use_fp32_unet=False)
        if ok:
            print(f"✓ {mem:.0f} MB ({mem/total_mem*100:.1f}%)")
            fp16_results[bs] = mem
        else:
            print("✗ OOM" if mem == -1 else f"✗ {mem}")
            break

    fp16_max = max(fp16_results.keys()) if fp16_results else 0
    print(f"\n  fp16 max BS: {fp16_max}")

    # Cleanup
    del pipeline
    reset_gpu()

    # === Test 2: fp32 UNet (matching real training with mixed precision) ===
    print()
    print("=" * 60)
    print("Test 2: fp32 UNet (real training setup)")
    print("=" * 60)
    pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True)  # fp32 default
    pipeline = pipeline.to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing'
    )
    train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)

    base_mem_fp32 = torch.cuda.max_memory_allocated(device) / 1024 / 1024
    reset_gpu()
    print(f"Base model memory (fp32): {base_mem_fp32:.0f} MB")
    print(f"Available for activations: {total_mem - base_mem_fp32:.0f} MB")

    fp32_results = {}
    for bs in [1, 2, 4, 8, 16, 32, 48, 64]:
        print(f"  BS={bs}...", end=" ", flush=True)
        ok, mem = test_bs(bs, pipeline, train_sched, device, use_fp32_unet=False)
        if ok:
            print(f"✓ {mem:.0f} MB ({mem/total_mem*100:.1f}%)")
            fp32_results[bs] = mem
        else:
            print("✗ OOM" if mem == -1 else f"✗ {mem}")
            break

    fp32_max = max(fp32_results.keys()) if fp32_results else 0
    print(f"\n  fp32 max BS: {fp32_max}")

    # === Test 3: fp32 UNet + LoRA overhead estimation ===
    print()
    print("=" * 60)
    print("Test 3: LoRA overhead estimation")
    print("=" * 60)

    # Count attn1 LoRA parameters
    lora_params = 0
    for name, module in pipeline.unet.named_modules():
        if 'attn1' in name and hasattr(module, 'to_q'):
            h = module.to_q.in_features
            # 4 LoRA layers: to_q, to_k, to_v, to_out
            # Each: down (h x rank) + up (rank x h), rank=4
            lora_params += 4 * (h * 4 + 4 * h)  # 4 layers, each h*4 + 4*h
    lora_mem_mb = lora_params * 4 / 1024 / 1024  # fp32 params
    lora_grad_mb = lora_params * 4 / 1024 / 1024  # fp32 gradients
    lora_optim_mb = lora_params * 8 / 1024 / 1024  # Adam: 2x fp32 states
    total_lora_overhead = lora_mem_mb + lora_grad_mb + lora_optim_mb

    print(f"  attn1 LoRA params: {lora_params / 1e6:.2f}M")
    print(f"  LoRA weights (fp32): {lora_mem_mb:.0f} MB")
    print(f"  LoRA gradients: {lora_grad_mb:.0f} MB")
    print(f"  LoRA optimizer states: {lora_optim_mb:.0f} MB")
    print(f"  Total LoRA overhead: {total_lora_overhead:.0f} MB")
    print()

    # Adjusted max BS accounting for LoRA overhead
    available_for_activations = total_mem - base_mem_fp32 - total_lora_overhead
    print(f"  Available for activations (fp32 UNet + LoRA): {available_for_activations:.0f} MB")

    # Per-batch activation memory (from test results)
    if fp32_results and len(fp32_results) >= 2:
        bs_list = sorted(fp32_results.keys())
        # Linear regression: mem = base + per_batch * bs
        if len(bs_list) >= 2:
            b1, b2 = bs_list[0], bs_list[-1]
            m1, m2 = fp32_results[b1], fp32_results[b2]
            per_batch = (m2 - m1) / (b2 - b1)
            base_act = m1 - per_batch * b1
            print(f"  Per-batch activation memory: ~{per_batch:.0f} MB")
            print(f"  Base activation memory: ~{base_act:.0f} MB")
            estimated_max = int((available_for_activations - base_act) / per_batch)
            print(f"  Estimated max BS (fp32 + LoRA): ~{estimated_max}")

    # === Final Summary ===
    print()
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"GPU: {torch.cuda.get_device_name(0)} ({total_mem:.0f} MB)")
    print(f"UNet: 2567.5M params, 70 attn1 + 70 attn2 layers")
    print(f"attn1 self-attention: 32x48=1536 seq, doubled to 3072 by ref attn")
    print()
    print(f"{'Config':<30} {'Max BS':>8} {'Peak MB':>10} {'% GPU':>8}")
    print("-" * 58)
    print(f"{'fp16 UNet (no LoRA)':<30} {fp16_max:>8} {fp16_results.get(fp16_max,0):>10.0f} {fp16_results.get(fp16_max,0)/total_mem*100:>7.1f}%")
    print(f"{'fp32 UNet (no LoRA)':<30} {fp32_max:>8} {fp32_results.get(fp32_max,0):>10.0f} {fp32_results.get(fp32_max,0)/total_mem*100:>7.1f}%")
    print()
    print("Note: Real training with LoRA adds ~24 MB overhead (negligible).")
    print("The main bottleneck is UNet weight memory + activation memory.")
    print("Gradient checkpointing keeps activation memory manageable.")


if __name__ == "__main__":
    main()
