"""
Benchmark Full fine-tune peak GPU memory (single step only to avoid OOM)
"""
import os
import sys
import subprocess
import json
import tempfile

OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/benchmark'
GPU_ID = 1


def write_bench_script():
    """Write a standalone benchmark script for Full fine-tune (1 step only)."""
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

    lines.append("# Full fine-tune: wrap UNet, all params trainable")
    lines.append("pipeline.unet = RefOnlyNoisedUNet(pipeline.unet, pipeline.scheduler, pipeline.scheduler)")
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

    lines.append("# All params trainable")
    lines.append("trainable_params = [p for p in unet.parameters()]")
    lines.append("total_params = sum(p.numel() for p in unet.parameters())")
    lines.append("trainable_count = sum(p.numel() for p in trainable_params)")
    lines.append("print(f'Config: Full fine-tune (1 step)')")
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
    lines.append("print('Running 1 forward+backward step...')")
    lines.append("")
    lines.append("# Single step only")
    lines.append("optimizer.zero_grad()")
    lines.append("cond_lat = torch.randn_like(latents)")
    lines.append("cross_attention_kwargs = dict(cond_lat=cond_lat)")
    lines.append("unet_dtype = next(unet.parameters()).dtype")
    lines.append("noise_pred = unet(")
    lines.append("    latents.to(unet_dtype), timesteps,")
    lines.append("    encoder_hidden_states=prompt_embeds.to(unet_dtype),")
    lines.append("    cross_attention_kwargs=dict(cond_lat=cond_lat.to(unet_dtype)),")
    lines.append("    added_cond_kwargs={k: v.to(unet_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()},")
    lines.append("    return_dict=False, is_training=True,")
    lines.append(")[0]")
    lines.append("loss = torch.nn.functional.mse_loss(noise.to(unet_dtype), noise_pred)")
    lines.append("loss.backward()")
    lines.append("optimizer.step()")
    lines.append("peak_mb = torch.cuda.max_memory_allocated(DEVICE) / (1024**2)")
    lines.append("print(f'  Step 0: loss={loss.item():.6f}, peak={peak_mb:.0f} MB')")
    lines.append("")
    lines.append(f"print(f'RESULT|Full fine-tune (1 step)|{{total_params}}|{{trainable_count}}|{{peak_mb:.0f}}')")

    return '\n'.join(lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Running: Full fine-tune (1 step) on GPU {GPU_ID}")
    print(f"{'='*60}")

    script = write_bench_script()

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
                print("\n" + "=" * 80)
                print("  FULL FINE-TUNE PEAK MEMORY")
                print("=" * 80)
                print(f"  Total UNet params: {int(parts[1]):,}")
                print(f"  Trainable params: {int(parts[2]):,} ({int(parts[2])/int(parts[1])*100:.2f}%)")
                print(f"  Peak GPU Memory: {float(parts[3])/1024:.2f} GB")
                print("=" * 80)
    finally:
        os.unlink(script_path)


if __name__ == '__main__':
    main()
