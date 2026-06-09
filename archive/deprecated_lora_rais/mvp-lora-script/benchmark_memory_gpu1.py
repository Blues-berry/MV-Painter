"""
Benchmark training peak GPU memory on GPU 1 (空闲的 GPU):
1. Full fine-tune (all UNet params trainable)
2. Full LoRA (rank=4, attn1+attn2)
3. attn2-only LoRA (rank=4)

Runs actual forward+backward pass on GPU and measures peak memory.
Each config runs in a subprocess to ensure clean GPU memory state.
"""
import os
import sys
import subprocess
import json
import tempfile

OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/benchmark'
GPU_ID = 1  # 使用空闲的 GPU 1


def write_bench_script(config_name, model_target, lora_rank, lora_alpha):
    """Write a standalone benchmark script for one config."""
    lines = []
    lines.append("import os, sys, gc, time, torch, numpy as np")
    lines.append("os.chdir('/4T/CXY/MV-Painter/MVPainter')")
    lines.append("sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')")
    lines.append("import types")
    lines.append("fake = types.ModuleType('mvpainter.controlnet')")
    lines.append("fake.ControlNetModel_Union = None")
    lines.append("sys.modules['mvpainter.controlnet'] = fake")
    lines.append("from diffusers import DDPMScheduler, UNet2DConditionModel")
    lines.append("from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline")
    lines.append(f"DEVICE = 'cuda:{GPU_ID}'")
    lines.append("")

    lines.append("# Load pipeline")
    lines.append("pipeline = MVPainter_Pipeline.from_pretrained(")
    lines.append("    '/4T/CXY/MV-Painter/checkpoints/hf_repo', use_safetensors=True)")
    lines.append("pipeline.scheduler = DDPMScheduler.from_config(pipeline.scheduler.config)")
    lines.append("")

    if model_target == 'full':
        lines.append("# Full fine-tune: wrap UNet, all params trainable")
        lines.append("pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, pipeline.scheduler, pipeline.scheduler)")
        lines.append("unet = pipeline.unet")
        lines.append("unet.enable_gradient_checkpointing()")

    elif model_target == 'full_lora':
        # Keep LoRA processors (don't merge) - same as training
        lines.append("from mvpainter.lora_utils import create_lora_processors")
        lines.append(f"processors = create_lora_processors(pipeline.unet, rank={lora_rank}, network_alpha={lora_alpha})")
        lines.append("pipeline.unet.set_attn_processor(processors)")
        lines.append("pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, pipeline.scheduler, pipeline.scheduler, replace_processors=False)")
        lines.append("unet = pipeline.unet")
        lines.append("unet.enable_gradient_checkpointing()")

    elif model_target == 'attn2_lora':
        # Keep LoRA processors (don't merge) - same as training
        lines.append("from mvpainter.lora_utils_attn2 import create_lora_processors_attn2_only")
        lines.append(f"processors = create_lora_processors_attn2_only(pipeline.unet, rank={lora_rank}, network_alpha={lora_alpha})")
        lines.append("pipeline.unet.set_attn_processor(processors)")
        lines.append("pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, pipeline.scheduler, pipeline.scheduler, replace_processors=False)")
        lines.append("unet = pipeline.unet")
        lines.append("unet.enable_gradient_checkpointing()")

    lines.append("")
    lines.append("# Move to GPU in fp16 (same as mixed-precision training)")
    lines.append("unet.to(DEVICE, dtype=torch.float16)")
    lines.append("pipeline.vae.to(DEVICE, dtype=torch.float16)")
    lines.append("for attr in ['uc_text_emb', 'uc_text_emb_2']:")
    lines.append("    t = getattr(pipeline, attr, None)")
    lines.append("    if t is not None and isinstance(t, torch.Tensor):")
    lines.append("        setattr(pipeline, attr, t.to(DEVICE))")
    lines.append("")

    lines.append("# Freeze/unfreeze")
    lines.append("total_params = sum(p.numel() for p in unet.parameters())")
    if model_target == 'full':
        lines.append("trainable_params = [p for p in unet.parameters()]")
    else:
        lines.append("unet.requires_grad_(False)")
        lines.append("lora_kw = ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']")
        lines.append("trainable_params = []")
        lines.append("for n, p in unet.named_parameters():")
        lines.append("    if any(k in n for k in lora_kw):")
        lines.append("        p.requires_grad = True")
        lines.append("        trainable_params.append(p)")
    lines.append("trainable_count = sum(p.numel() for p in trainable_params)")
    lines.append(f"print('Config: {config_name}')")
    lines.append("print(f'Total UNet params: {total_params:,}')")
    lines.append("print(f'Trainable params: {trainable_count:,} ({trainable_count/total_params*100:.4f}%)')")
    lines.append("")

    lines.append("optimizer = torch.optim.AdamW(trainable_params, lr=1e-5)")
    lines.append("")
    lines.append("# Prepare dummy inputs")
    lines.append("torch.cuda.empty_cache()")
    lines.append("torch.cuda.reset_peak_memory_stats(DEVICE)")
    lines.append("B = 1")
    lines.append("latents = torch.randn(B, 4, 192, 128, device=DEVICE, dtype=torch.float16)")
    lines.append("noise = torch.randn_like(latents)")
    lines.append("timesteps = torch.randint(0, 1000, (B,), device=DEVICE).long()")
    lines.append("global_embeds = torch.randn(B, 1, 2048, device=DEVICE, dtype=torch.float16)")
    lines.append("ramp = pipeline.config.ramping_coefficients")
    lines.append("ramp_t = torch.tensor(ramp, dtype=torch.float16, device=DEVICE).unsqueeze(-1)")
    lines.append("prompt_embeds = pipeline.uc_text_emb.to(DEVICE, dtype=torch.float16) + global_embeds * ramp_t")
    lines.append("add_time_ids = torch.tensor([[1536, 1024, 0, 0, 1536, 1024]], device=DEVICE, dtype=torch.float16)")
    lines.append("added_cond_kwargs = {")
    lines.append("    'text_embeds': pipeline.uc_text_emb_2.to(DEVICE, dtype=torch.float16),")
    lines.append("    'time_ids': add_time_ids")
    lines.append("}")
    lines.append("")
    lines.append("print(f'Memory before training: {torch.cuda.memory_allocated(DEVICE)/(1024**2):.0f} MB')")
    lines.append("print('Running 3 forward+backward steps...')")
    lines.append("")
    lines.append("for step in range(3):")
    lines.append("    optimizer.zero_grad()")
    lines.append("    cond_lat = torch.randn_like(latents)")
    lines.append("    cross_attention_kwargs = dict(cond_lat=cond_lat)")
    lines.append("    # Cast to UNet dtype (fp32)")
    lines.append("    unet_dtype = next(unet.parameters()).dtype")
    lines.append("    noise_pred = unet(")
    lines.append("        latents.to(unet_dtype), timesteps,")
    lines.append("        encoder_hidden_states=prompt_embeds.to(unet_dtype),")
    lines.append("        cross_attention_kwargs=dict(cond_lat=cond_lat.to(unet_dtype)),")
    lines.append("        added_cond_kwargs={k: v.to(unet_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()},")
    lines.append("        return_dict=False, is_training=True,")
    lines.append("    )[0]")
    lines.append("    loss = torch.nn.functional.mse_loss(noise.to(unet_dtype), noise_pred)")
    lines.append("    loss.backward()")
    lines.append("    optimizer.step()")
    lines.append("    peak = torch.cuda.max_memory_allocated(DEVICE) / (1024**2)")
    lines.append("    print(f'  Step {step}: loss={loss.item():.6f}, peak={peak:.0f} MB')")
    lines.append("")
    lines.append("peak_mb = torch.cuda.max_memory_allocated(DEVICE) / (1024**2)")
    lines.append(f"print(f'RESULT|{config_name}|{{total_params}}|{{trainable_count}}|{{peak_mb:.0f}}')")

    return '\n'.join(lines)


def run_benchmark(config_name, model_target, lora_rank, lora_alpha):
    print(f"\n{'='*60}")
    print(f"  Running: {config_name} (on GPU {GPU_ID})")
    print(f"{'='*60}")

    script = write_bench_script(config_name, model_target, lora_rank, lora_alpha)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir='/tmp') as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ['/home/ubuntu/ssd_work/conda_envs/mvpainter/bin/python', script_path],
            capture_output=True, text=True, timeout=600,
        )
        print(result.stdout)
        if result.returncode != 0:
            for line in result.stderr.split('\n'):
                if any(k in line for k in ['Error', 'OOM', 'OutOfMemory', 'Traceback']):
                    print(f"  STDERR: {line}")

        for line in result.stdout.split('\n'):
            if line.startswith('RESULT|'):
                parts = line.split('|')
                return {
                    'name': parts[1],
                    'total_params': int(parts[2]),
                    'trainable_params': int(parts[3]),
                    'trainable_pct': int(parts[3]) / int(parts[2]) * 100,
                    'peak_mem_mb': float(parts[4]),
                    'peak_mem_gb': float(parts[4]) / 1024,
                }
    finally:
        os.unlink(script_path)

    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    configs = [
        ("Full fine-tune", "full", None, None),
        ("Full LoRA (r=4)", "full_lora", 4, 4),
        ("attn2-only LoRA (r=4)", "attn2_lora", 4, 4),
    ]

    all_results = []
    for name, target, rank, alpha in configs:
        r = run_benchmark(name, target, rank, alpha)
        if r:
            all_results.append(r)

    print("\n" + "=" * 80)
    print("  TRAINING MEMORY BENCHMARK RESULTS")
    print("=" * 80)
    print(f"{'Method':<30} {'Trainable':>14} {'% Total':>8} {'Peak Mem':>12}")
    print("-" * 80)
    for r in all_results:
        print(f"{r['name']:<30} {r['trainable_params']:>14,} {r['trainable_pct']:>7.2f}% {r['peak_mem_gb']:>10.2f} GB")

    if len(all_results) >= 2:
        base = all_results[0]
        print(f"\n{'Method':<30} {'Δ Mem (GB)':>12} {'Savings':>10}")
        print("-" * 80)
        for r in all_results:
            dm = r['peak_mem_gb'] - base['peak_mem_gb']
            pct = (1 - r['peak_mem_gb'] / base['peak_mem_gb']) * 100 if base['peak_mem_gb'] > 0 else 0
            print(f"{r['name']:<30} {dm:>+12.2f} {pct:>+9.1f}%")

    out_path = os.path.join(OUTPUT_DIR, 'training_memory_benchmark_gpu1.json')
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
