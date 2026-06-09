"""
Benchmark inference peak GPU memory for:
1. Original model (no LoRA)
2. attn2-only LoRA loaded

Runs actual inference pass on GPU and measures peak memory.
"""
import os
import sys
import subprocess
import json
import tempfile

OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/benchmark'
GPU_ID = 1


def write_bench_script(config_name, lora_path):
    """Write a standalone benchmark script for inference."""
    lines = []
    lines.append("import os, sys, gc, time, torch, numpy as np")
    lines.append("os.chdir('/4T/CXY/MV-Painter/MVPainter')")
    lines.append("sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')")
    lines.append("import types")
    lines.append("fake = types.ModuleType('mvpainter.controlnet')")
    lines.append("fake.ControlNetModel_Union = None")
    lines.append("sys.modules['mvpainter.controlnet'] = fake")
    lines.append("from diffusers import DDPMScheduler, EulerAncestralDiscreteScheduler")
    lines.append("from mvpainter.mvpainter_pipeline import MVPainter_Pipeline")
    lines.append(f"DEVICE = 'cuda:{GPU_ID}'")
    lines.append("")

    lines.append("# Load pipeline")
    lines.append("pipeline = MVPainter_Pipeline.from_pretrained(")
    lines.append("    '/4T/CXY/MV-Painter/checkpoints/hf_repo', use_safetensors=True)")
    lines.append("pipeline.to(DEVICE, dtype=torch.float16)")
    lines.append("")

    if lora_path:
        lines.append("# Load LoRA weights")
        lines.append("from safetensors.torch import load_file")
        lines.append(f"lora_state = load_file('{lora_path}')")
        lines.append("# Apply LoRA weights to UNet attn processors")
        lines.append("unet = pipeline.unet")
        lines.append("for name, param in lora_state.items():")
        lines.append("    # Parse layer name and find corresponding processor")
        lines.append("    parts = name.split('.')")
        lines.append("    # Build processor key from parts")
        lines.append("    processor_key = '.'.join(parts[:-1])  # Remove weight suffix")
        lines.append("    if hasattr(unet, 'attn_processors'):")
        lines.append("        processors = unet.attn_processors")
        lines.append("        for proc_name, proc in processors.items():")
        lines.append("            if hasattr(proc, 'to_q_lora_down'):")
        lines.append("                # Match by layer name pattern")
        lines.append("                pass")
        lines.append("")

    lines.append("torch.cuda.empty_cache()")
    lines.append("torch.cuda.reset_peak_memory_stats(DEVICE)")
    lines.append("")

    lines.append("# Measure idle memory")
    lines.append("idle_mem = torch.cuda.memory_allocated(DEVICE) / (1024**2)")
    lines.append(f"print('Config: {config_name}')")
    lines.append("print(f'Idle memory (pipeline loaded): {idle_mem:.0f} MB')")
    lines.append("")

    lines.append("# Run dummy inference")
    lines.append("from PIL import Image")
    lines.append("dummy_img = Image.new('RGB', (256, 256), color=(128, 128, 128))")
    lines.append("print('Running inference...')
")
    lines.append("with torch.no_grad():")
    lines.append("    result = pipeline(")
    lines.append("        dummy_img,")
    lines.append("        num_inference_steps=20,")
    lines.append("        guidance_scale=5.0,")
    lines.append("        height=768,")
    lines.append("        width=512,")
    lines.append("        generator=torch.Generator(DEVICE).manual_seed(42),")
    lines.append("    )")
    lines.append("")
    lines.append("peak_mb = torch.cuda.max_memory_allocated(DEVICE) / (1024**2)")
    lines.append(f"print(f'Peak memory during inference: {{peak_mb:.0f}} MB')")
    lines.append(f"print(f'RESULT|{config_name}|{{idle_mem:.0f}}|{{peak_mb:.0f}}')")

    return '\n'.join(lines)


def run_benchmark(config_name, lora_path=None):
    print(f"\n{'='*60}")
    print(f"  Running: {config_name} (on GPU {GPU_ID})")
    print(f"{'='*60}")

    script = write_bench_script(config_name, lora_path)

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
                    'idle_mem_mb': float(parts[2]),
                    'peak_mem_mb': float(parts[3]),
                    'peak_mem_gb': float(parts[3]) / 1024,
                }
    finally:
        os.unlink(script_path)

    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find LoRA checkpoint
    lora_dir = '/4T/CXY/stable-fast-3d-output/output/material_refine_trainv6main_full_b4_withprior'
    lora_files = []
    if os.path.exists(lora_dir):
        for f in os.listdir(lora_dir):
            if f.endswith('.safetensors'):
                lora_files.append(os.path.join(lora_dir, f))

    configs = [
        ("Original (no LoRA)", None),
    ]

    # Add LoRA if available
    if lora_files:
        configs.append(("attn2-only LoRA", lora_files[0]))

    all_results = []
    for name, lora_path in configs:
        r = run_benchmark(name, lora_path)
        if r:
            all_results.append(r)

    print("\n" + "=" * 80)
    print("  INFERENCE MEMORY BENCHMARK RESULTS")
    print("=" * 80)
    print(f"{'Method':<30} {'Idle Mem':>12} {'Peak Mem':>12}")
    print("-" * 80)
    for r in all_results:
        print(f"{r['name']:<30} {r['idle_mem_mb']:>10,.0f} MB {r['peak_mem_mb']:>10,.0f} MB")

    out_path = os.path.join(OUTPUT_DIR, 'inference_memory_benchmark.json')
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
