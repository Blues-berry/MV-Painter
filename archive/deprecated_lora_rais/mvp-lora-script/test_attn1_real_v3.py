"""
Continuation: push beyond BS=32 to find the true limit.
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


def test_bs(batch_size, pipeline, train_sched, device):
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

    model_path = "/4T/CXY/MV-Painter/checkpoints/hf_repo"
    pipeline = MVPainter_Pipeline.from_pretrained(model_path, use_safetensors=True, torch_dtype=torch.float16)
    pipeline = pipeline.to(device)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing'
    )
    train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)

    base_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024
    reset_gpu()
    print(f"Base model memory: {base_mem:.0f} MB")
    print(f"Available for training: {total_mem - base_mem:.0f} MB")
    print()

    # Test from BS=32 upward
    results = {}
    lo, hi = 32, 128
    max_bs = 0
    max_mem = 0

    while lo <= hi:
        bs = (lo + hi) // 2
        print(f"  BS={bs}...", end=" ", flush=True)
        ok, mem = test_bs(bs, pipeline, train_sched, device)
        if ok:
            print(f"✓ {mem:.0f} MB ({mem/total_mem*100:.1f}%)")
            results[bs] = mem
            max_bs = bs
            max_mem = mem
            lo = bs + 1
        else:
            if mem == -1:
                print("✗ OOM")
            else:
                print(f"✗ {mem}")
            hi = bs - 1

    # Fine-grained around boundary
    print()
    print("Fine-grained around boundary:")
    for bs in range(max(1, max_bs - 4), max_bs + 5):
        if bs not in results and bs <= 128:
            print(f"  BS={bs}...", end=" ", flush=True)
            ok, mem = test_bs(bs, pipeline, train_sched, device)
            if ok:
                print(f"✓ {mem:.0f} MB")
                results[bs] = mem
            else:
                print("✗ OOM" if mem == -1 else f"✗ {mem}")

    # Final summary
    print()
    print("=" * 60)
    print(f"Max batch_size = {max_bs}")
    print(f"Peak memory = {max_mem:.0f} / {total_mem:.0f} MB ({max_mem/total_mem*100:.1f}%)")
    print()
    print("All results:")
    for bs in sorted(results.keys()):
        m = results[bs]
        bar = "█" * int(m / total_mem * 40)
        print(f"  BS={bs:>3}: {m:>6.0f} MB ({m/total_mem*100:>5.1f}%) {bar}")


if __name__ == "__main__":
    main()
