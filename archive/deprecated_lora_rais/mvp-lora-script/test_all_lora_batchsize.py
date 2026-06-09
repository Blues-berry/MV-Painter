"""
Batch size comparison: attn2-only vs Full LoRA vs attn1-only.
Each config runs as a separate script to ensure clean GPU memory.
Run: python mvp-lora-script/test_all_lora_batchsize.py
"""
import subprocess
import sys
import os
import json
import torch
import tempfile

SCRIPT_TEMPLATE = r'''
import torch
import torch.nn as nn
import gc
import sys
import os
import json

sys.path.insert(0, '/4T/CXY/MV-Painter/MVPainter')

from diffusers import DDPMScheduler, UNet2DConditionModel
from diffusers.models.attention_processor import AttnProcessor2_0
from mvpainter.mvpainter_pipeline import RefOnlyNoisedUNet, ReferenceOnlyAttnProc

CONFIG = "__CONFIG__"


class LoRALinearLayer(nn.Module):
    def __init__(self, in_features, out_features, rank=4, network_alpha=None):
        super().__init__()
        self.down = nn.Linear(in_features, rank, bias=False)
        self.up = nn.Linear(rank, out_features, bias=False)
        self.scale = (network_alpha or rank) / rank
        nn.init.kaiming_uniform_(self.down.weight, a=5**0.5)
        nn.init.zeros_(self.up.weight)
    def forward(self, x):
        return self.up(self.down(x)) * self.scale


class LoRAAttnProcessor2_0(nn.Module):
    def __init__(self, hidden_size, cross_attention_dim=None, rank=4, network_alpha=None):
        super().__init__()
        self.hidden_size = hidden_size
        self.cross_attention_dim = cross_attention_dim or hidden_size
        self.to_q_lora = LoRALinearLayer(hidden_size, hidden_size, rank, network_alpha)
        self.to_k_lora = LoRALinearLayer(self.cross_attention_dim, hidden_size, rank, network_alpha)
        self.to_v_lora = LoRALinearLayer(self.cross_attention_dim, hidden_size, rank, network_alpha)
        self.to_out_lora = LoRALinearLayer(hidden_size, hidden_size, rank, network_alpha)
    def __call__(self, attn, hidden_states, encoder_hidden_states=None, attention_mask=None, temb=None, *a, **kw):
        residual = hidden_states
        if attn.spatial_norm is not None:
            hidden_states = attn.spatial_norm(hidden_states, temb)
        input_ndim = hidden_states.ndim
        if input_ndim == 4:
            b, c, h, w = hidden_states.shape
            hidden_states = hidden_states.view(b, c, h * w).transpose(1, 2)
        seq_len = hidden_states.shape[1] if encoder_hidden_states is None else encoder_hidden_states.shape[1]
        if attention_mask is not None:
            attention_mask = attn.prepare_attention_mask(attention_mask, seq_len, hidden_states.shape[0])
            attention_mask = attention_mask.view(hidden_states.shape[0], attn.heads, -1, attention_mask.shape[-1])
        if attn.group_norm is not None:
            hidden_states = attn.group_norm(hidden_states.transpose(1, 2)).transpose(1, 2)
        query = attn.to_q(hidden_states) + self.to_q_lora(hidden_states)
        if encoder_hidden_states is None:
            encoder_hidden_states = hidden_states
        elif attn.norm_cross:
            encoder_hidden_states = attn.norm_encoder_hidden_states(encoder_hidden_states)
        key = attn.to_k(encoder_hidden_states) + self.to_k_lora(encoder_hidden_states)
        value = attn.to_v(encoder_hidden_states) + self.to_v_lora(encoder_hidden_states)
        inner_dim = key.shape[-1]
        head_dim = inner_dim // attn.heads
        query = query.view(hidden_states.shape[0], -1, attn.heads, head_dim).transpose(1, 2)
        key = key.view(hidden_states.shape[0], -1, attn.heads, head_dim).transpose(1, 2)
        value = value.view(hidden_states.shape[0], -1, attn.heads, head_dim).transpose(1, 2)
        if attn.norm_q is not None: query = attn.norm_q(query)
        if attn.norm_k is not None: key = attn.norm_k(key)
        hidden_states = torch.nn.functional.scaled_dot_product_attention(
            query, key, value, attn_mask=attention_mask, dropout_p=0.0, is_causal=False
        )
        hidden_states = hidden_states.transpose(1, 2).reshape(hidden_states.shape[0], -1, attn.heads * head_dim)
        hidden_states = hidden_states.to(query.dtype)
        hidden_states = attn.to_out[0](hidden_states) + self.to_out_lora(hidden_states)
        hidden_states = attn.to_out[1](hidden_states)
        if input_ndim == 4:
            hidden_states = hidden_states.transpose(-1, -2).reshape(hidden_states.shape[0], c, h, w)
        if attn.residual_connection:
            hidden_states = hidden_states + residual
        return hidden_states / attn.rescale_output_factor


def reset_gpu():
    gc.collect(); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()


def test_bs(batch_size, unet, train_sched, device):
    try:
        reset_gpu()
        dtype = torch.float16
        B = batch_size
        latents = torch.randn(B, 4, 32, 48, device=device, dtype=dtype)
        cond_lat = torch.randn(B, 4, 32, 48, device=device, dtype=dtype)
        prompt_embeds = torch.randn(B, 77, 2048, device=device, dtype=dtype)
        t = torch.randint(0, 1000, (B,), device=device).long()
        added_cond_kwargs = {
            "text_embeds": torch.randn(B, 1280, device=device, dtype=dtype),
            "time_ids": torch.randn(B, 6, device=device, dtype=dtype),
        }
        wrapped = RefOnlyNoisedUNet(unet, train_sched, None, replace_processors=False)
        if hasattr(wrapped, 'enable_gradient_checkpointing'):
            wrapped.enable_gradient_checkpointing()
        pred = wrapped(
            latents, t, encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=dict(cond_lat=cond_lat),
            added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=True,
        )[0]
        loss = pred.mean()
        loss.backward()
        torch.cuda.synchronize()
        peak = torch.cuda.max_memory_allocated(device) / 1024 / 1024
        del pred, loss, latents, cond_lat, prompt_embeds, added_cond_kwargs, wrapped
        reset_gpu()
        return True, peak
    except torch.cuda.OutOfMemoryError:
        reset_gpu()
        return False, -1
    except Exception as e:
        reset_gpu()
        return False, str(e)


def find_max_bs(unet, train_sched, device, lo=1, hi=128):
    max_bs, max_mem, results = 0, 0, {}
    while lo <= hi:
        bs = (lo + hi) // 2
        ok, mem = test_bs(bs, unet, train_sched, device)
        if ok:
            results[bs] = mem
            max_bs = bs
            max_mem = mem
            lo = bs + 1
        else:
            hi = bs - 1
    for bs in range(max(1, max_bs - 2), min(128, max_bs + 3)):
        if bs not in results:
            ok, mem = test_bs(bs, unet, train_sched, device)
            if ok:
                results[bs] = mem
                if bs > max_bs:
                    max_bs = bs
                    max_mem = mem
    return max_bs, max_mem, results


def main():
    device = torch.device("cuda:0")
    total_mem = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
    model_path = "/4T/CXY/MV-Painter/checkpoints/hf_repo"
    unet = UNet2DConditionModel.from_pretrained(
        os.path.join(model_path, "unet"), torch_dtype=torch.float16
    ).to(device)
    train_sched = DDPMScheduler.from_pretrained(model_path, subfolder="scheduler")
    base_mem = torch.cuda.max_memory_allocated(device) / 1024 / 1024
    reset_gpu()

    # Apply LoRA config
    if CONFIG == "attn2-only":
        targets = {n for n in unet.attn_processors if 'attn2' in n}
    elif CONFIG == "full":
        targets = set(unet.attn_processors.keys())
    else:
        targets = {n for n in unet.attn_processors if 'attn1' in n}

    proc_dtype = next(unet.parameters()).dtype
    proc_device = next(unet.parameters()).device
    processors = {}
    for name, _ in unet.attn_processors.items():
        attn_name = name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_name]
        hidden_size = attn_module.to_q.in_features
        cross_attn_dim = attn_module.to_k.in_features if 'attn2' in name else None
        enabled = name.endswith("attn1.processor")
        if name in targets:
            lora_proc = LoRAAttnProcessor2_0(
                hidden_size=hidden_size, cross_attention_dim=cross_attn_dim,
                rank=4, network_alpha=4,
            ).to(device=proc_device, dtype=proc_dtype)
            processors[name] = ReferenceOnlyAttnProc(lora_proc, enabled=enabled, name=name)
        else:
            processors[name] = ReferenceOnlyAttnProc(AttnProcessor2_0(), enabled=enabled, name=name)
    unet.set_attn_processor(processors)

    lora_p = sum(p.numel() for n, p in unet.named_parameters()
                 if any(kw in n for kw in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']))

    max_bs, max_mem, results = find_max_bs(unet, train_sched, device)

    output = {
        "config": CONFIG, "lora_params": lora_p,
        "max_bs": max_bs, "max_mem": max_mem,
        "base_mem": base_mem, "total_mem": total_mem,
        "results": {str(k): v for k, v in results.items()},
    }
    print("RESULT_JSON:" + json.dumps(output))


if __name__ == "__main__":
    main()
'''


def run_config(config, gpu_id):
    """Run a single config as a separate script file."""
    code = SCRIPT_TEMPLATE.replace("__CONFIG__", config)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=600,
            env=env,
        )
        for line in result.stdout.split("\n"):
            if line.startswith("RESULT_JSON:"):
                return json.loads(line.split("RESULT_JSON:", 1)[1])
        if result.stderr:
            print(f"  STDERR (last 300): {result.stderr[-300:]}")
        return None
    finally:
        os.unlink(tmp_path)


def main():
    # Pick GPU with most free memory
    best_gpu, best_free = 0, 0
    for i in range(torch.cuda.device_count()):
        free = torch.cuda.mem_get_info(i)[0] / 1024 / 1024
        total = torch.cuda.mem_get_info(i)[1] / 1024 / 1024
        print(f"  GPU {i}: {total - free:.0f} MB used, {free:.0f} MB free")
        if free > best_free:
            best_gpu, best_free = i, free
    print(f"  -> Using GPU {best_gpu}\n")

    configs = ["attn2-only", "full", "attn1-only"]
    all_results = {}

    for config in configs:
        print(f"{'~' * 60}")
        print(f"  Testing: {config}")
        print(f"{'~' * 60}")
        result = run_config(config, best_gpu)
        if result:
            all_results[config] = result
            print(f"  LoRA params: {result['lora_params'] / 1e6:.2f}M")
            print(f"  Max BS = {result['max_bs']}, Peak = {result['max_mem']:.0f} MB\n")
        else:
            all_results[config] = None
            print(f"  FAILED\n")

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Config':<16} {'LoRA Params':>12} {'Max BS':>8} {'Peak MB':>10} {'% GPU':>8}")
    print("-" * 56)
    for config in configs:
        r = all_results.get(config)
        if r:
            pct = r['max_mem'] / r['total_mem'] * 100
            print(f"{config:<16} {r['lora_params']/1e6:>10.2f}M {r['max_bs']:>8} {r['max_mem']:>10.0f} {pct:>7.1f}%")
        else:
            print(f"{config:<16} {'FAILED':>12}")

    # Epoch calculation
    n_objects, n_views, steps = 1200, 17, 250
    total_samples = n_objects * n_views
    print(f"\n{'=' * 60}")
    print("EPOCH CALCULATION")
    print(f"{'=' * 60}")
    print(f"Objects: {n_objects}, Views: {n_views}, Samples: {total_samples}, Steps: {steps}\n")
    print(f"{'Config':<16} {'Max BS':>8} {'Steps/Epoch':>12} {'Epochs':>10}")
    print("-" * 48)
    for config in configs:
        r = all_results.get(config)
        if r and r['max_bs'] > 0:
            spe = total_samples / r['max_bs']
            epochs = steps / spe
            print(f"{config:<16} {r['max_bs']:>8} {spe:>12.1f} {epochs:>10.2f}")
        else:
            print(f"{config:<16} {'OOM':>8} {'N/A':>12} {'N/A':>10}")


if __name__ == "__main__":
    main()
