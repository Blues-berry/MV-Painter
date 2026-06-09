"""
Benchmark inference time and peak GPU memory for three configurations:
1. Original (no LoRA)
2. Full LoRA (merged into all attn layers)
3. attn2-only LoRA (merged into attn2 only)

Usage: python benchmark_inference.py
"""
import os
import sys
import time
import gc
import torch
import numpy as np
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')

from diffusers import EulerAncestralDiscreteScheduler
from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
from mvpainter.lora_utils import merge_lora_into_unet
from mvpainter.lora_utils_attn2 import merge_lora_into_unet_attn2_only

# ── Config ──────────────────────────────────────────────────────────────
CHECKPOINT_PATH = '/4T/CXY/MV-Painter/checkpoints/hf_repo'
DEVICE = 'cuda:0'  # GPU 0 has ~15GB free
DTYPE = torch.float16
NUM_INFERENCE_STEPS = 50  # standard steps
NUM_WARMUP = 1            # warmup runs (not timed)
NUM_RUNS = 3              # timed runs for averaging

# LoRA paths
FULL_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-crash-r8-lr5e4-500-lora-crash-r8-lr5e4-500/lora_checkpoints/lora_step_0000500.safetensors'
FULL_LORA_RANK = 8
FULL_LORA_ALPHA = 8

ATTN2_LORA_PATH = '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-lora-attn2-only-r4-lr1e5-500-lora-attn2-only-r4-lr1e5-500/lora_checkpoints/lora_step_0000500.safetensors'
ATTN2_LORA_RANK = 4
ATTN2_LORA_ALPHA = 4

# Test image
TEST_IMAGE = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcb/image/000.png'


def reset_gpu():
    """Aggressively free GPU memory."""
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(DEVICE)


def get_peak_memory_mb():
    """Return peak GPU memory in MB."""
    return torch.cuda.max_memory_allocated(DEVICE) / (1024 ** 2)


def load_base_pipeline():
    """Load base pipeline without any LoRA."""
    pipeline = MVPainter_Pipeline.from_pretrained(
        CHECKPOINT_PATH, torch_dtype=DTYPE, use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    return pipeline.to(DEVICE)


def run_inference(pipeline, image, seed=42):
    """Run single inference, return elapsed seconds."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)

    torch.cuda.synchronize(DEVICE)
    t0 = time.perf_counter()

    with torch.no_grad(), torch.amp.autocast('cuda'):
        output = pipeline(
            image,
            num_inference_steps=NUM_INFERENCE_STEPS,
            output_type='latent',  # skip VAE decode to save memory; VAE is same for all configs
        )

    torch.cuda.synchronize(DEVICE)
    elapsed = time.perf_counter() - t0
    return elapsed


def benchmark_config(name, load_fn, image):
    """Benchmark a single configuration."""
    print(f"\n{'='*60}")
    print(f"  Benchmarking: {name}")
    print(f"{'='*60}")

    reset_gpu()

    # Load pipeline
    t_load_start = time.perf_counter()
    pipeline = load_fn()
    torch.cuda.synchronize(DEVICE)
    t_load = time.perf_counter() - t_load_start
    mem_after_load = torch.cuda.memory_allocated(DEVICE) / (1024 ** 2)
    print(f"  Load time: {t_load:.2f}s | Memory after load: {mem_after_load:.0f} MB")

    # Warmup
    print(f"  Warmup ({NUM_WARMUP} run)...")
    for _ in range(NUM_WARMUP):
        run_inference(pipeline, image, seed=0)

    # Reset peak memory stats before timed runs
    torch.cuda.reset_peak_memory_stats(DEVICE)

    # Timed runs
    print(f"  Timed runs ({NUM_RUNS} runs, {NUM_INFERENCE_STEPS} steps each)...")
    times = []
    for i in range(NUM_RUNS):
        t = run_inference(pipeline, image, seed=42 + i)
        times.append(t)
        torch.cuda.empty_cache()  # clear inter-run fragmentation
        print(f"    Run {i+1}: {t:.3f}s")

    peak_mem = get_peak_memory_mb()

    # Cleanup
    del pipeline
    reset_gpu()

    result = {
        'name': name,
        'load_time': t_load,
        'mean_time': np.mean(times),
        'std_time': np.std(times),
        'min_time': np.min(times),
        'max_time': np.max(times),
        'peak_memory_mb': peak_mem,
        'mem_after_load_mb': mem_after_load,
        'all_times': times,
    }
    return result


def main():
    print("=" * 60)
    print("  MV-Painter Inference Benchmark")
    print(f"  Device: {DEVICE} ({torch.cuda.get_device_name(DEVICE)})")
    print(f"  dtype: {DTYPE}")
    print(f"  Steps: {NUM_INFERENCE_STEPS}")
    print(f"  Warmup: {NUM_WARMUP} | Timed runs: {NUM_RUNS}")
    print("=" * 60)

    # Check test image
    if not os.path.exists(TEST_IMAGE):
        print(f"ERROR: Test image not found: {TEST_IMAGE}")
        # Try alternative
        alt = '/4T/CXY/MV-Painter/data/train_data/rendered_full/00603cadc4474dafb78cdb55278568f2/image/000.png'
        if os.path.exists(alt):
            print(f"Using alternative: {alt}")
            image = Image.open(alt).convert('RGBA')
        else:
            print("No test image available. Exiting.")
            return
    else:
        image = Image.open(TEST_IMAGE).convert('RGBA')

    print(f"  Test image: {TEST_IMAGE}")
    print(f"  Image size: {image.size}")

    results = []

    # ── 1. Original (no LoRA) ───────────────────────────────────────────
    def load_original():
        return load_base_pipeline()

    results.append(benchmark_config("Original (no LoRA)", load_original, image))

    # ── 2. Full LoRA ────────────────────────────────────────────────────
    def load_full_lora():
        pipeline = load_base_pipeline()
        merge_lora_into_unet(pipeline.unet, FULL_LORA_PATH, FULL_LORA_RANK, FULL_LORA_ALPHA)
        return pipeline

    results.append(benchmark_config("Full LoRA (attn1+attn2)", load_full_lora, image))

    # ── 3. attn2-only LoRA ──────────────────────────────────────────────
    def load_attn2_lora():
        pipeline = load_base_pipeline()
        merge_lora_into_unet_attn2_only(pipeline.unet, ATTN2_LORA_PATH, ATTN2_LORA_RANK, ATTN2_LORA_ALPHA)
        return pipeline

    results.append(benchmark_config("attn2-only LoRA", load_attn2_lora, image))

    # ── Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("  RESULTS SUMMARY")
    print("=" * 78)
    print(f"{'Method':<30} {'Time (s)':>10} {'± std':>8} {'Peak Mem (MB)':>15} {'Load (s)':>10}")
    print("-" * 78)
    for r in results:
        print(f"{r['name']:<30} {r['mean_time']:>10.2f} {r['std_time']:>8.2f} {r['peak_memory_mb']:>15.0f} {r['load_time']:>10.2f}")

    # Delta table
    base_time = results[0]['mean_time']
    base_mem = results[0]['peak_memory_mb']
    print(f"\n{'Method':<30} {'Δ Time (s)':>12} {'Δ Time (%)':>12} {'Δ Mem (MB)':>12} {'Δ Mem (%)':>12}")
    print("-" * 78)
    for r in results:
        dt = r['mean_time'] - base_time
        dp = (r['mean_time'] / base_time - 1) * 100 if base_time > 0 else 0
        dm = r['peak_memory_mb'] - base_mem
        dmp = (r['peak_memory_mb'] / base_mem - 1) * 100 if base_mem > 0 else 0
        print(f"{r['name']:<30} {dt:>+12.2f} {dp:>+11.1f}% {dm:>+12.0f} {dmp:>+11.1f}%")

    # Save raw results
    import json
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/benchmark'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'inference_benchmark.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nRaw results saved to {output_path}")


if __name__ == '__main__':
    main()
