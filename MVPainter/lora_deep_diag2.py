"""
Deep diagnostic: verify merge is modifying correct attention layers,
and test if LoRA delta is actually the problem.
"""
import os
import sys
import json
import torch
from safetensors.torch import load_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LORA_R8 = 'logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
PIPELINE_PATH = '../checkpoints/hf_repo'


def test_merge_verification():
    """Verify merge modifies correct layers and check delta magnitude vs base weights."""
    from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet
    from diffusers import EulerAncestralDiscreteScheduler

    print("Loading pipeline...")
    pipeline = MVPainter_Pipeline.from_pretrained(PIPELINE_PATH, torch_dtype=torch.float16)
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )
    pipeline.prepare()
    bare_unet = pipeline.unet.unet

    # Load v29 checkpoint
    v29_path = '../checkpoints/v29_25000.safetensors'
    ckpt = load_file(v29_path)
    print(f"v29 checkpoint has {len(ckpt)} tensors")

    # Check: does v29 contain attention layer weights?
    attn_keys = [k for k in ckpt if 'attn1' in k or 'attn2' in k]
    print(f"v29 attention keys: {len(attn_keys)}")
    print(f"  Sample: {attn_keys[:3]}")

    # Load v29 into bare UNet
    missing, unexpected = bare_unet.load_state_dict(ckpt, strict=False)
    print(f"Loaded v29: {len(missing)} missing, {len(unexpected)} unexpected")

    # Now check: do the attention layers have weights?
    for name, module in bare_unet.named_modules():
        if hasattr(module, 'to_q') and hasattr(module.to_q, 'weight'):
            w = module.to_q.weight.data.float()
            print(f"  {name}: to_q shape={list(w.shape)}, norm={w.norm():.4f}")
            break  # Just one

    # Check if v29 has LoRA-like keys (it shouldn't)
    lora_keys = [k for k in ckpt if 'lora' in k]
    print(f"v29 LoRA keys: {len(lora_keys)}")

    # Load LoRA
    config_path = LORA_R8.replace('.safetensors', '_config.json')
    with open(config_path) as f:
        cfg = json.load(f)
    rank = cfg['rank']
    alpha = cfg['alpha']
    scale = alpha / rank
    lora_state = load_file(LORA_R8)

    # Check: do LoRA keys match UNet attention layers?
    print(f"\nLoRA keys: {len(lora_state)}")
    lora_prefixes = set()
    for k in lora_state:
        prefix = k.rsplit('_to_', 1)[0]
        lora_prefixes.add(prefix)

    # Convert LoRA prefix to UNet processor name format
    unet_attn_names = set()
    for name, _ in bare_unet.attn_processors.items():
        attn_name = name.replace('.processor', '').replace('.', '_')
        unet_attn_names.add(attn_name)

    matches = lora_prefixes & unet_attn_names
    print(f"LoRA prefixes matching UNet attn names: {len(matches)}/{len(lora_prefixes)}")
    if len(matches) == 0:
        print("  *** NO MATCHES — LoRA keys don't correspond to UNet layers! ***")
        sample = list(lora_prefixes)[:3]
        unet_sample = list(unet_attn_names)[:3]
        print(f"  LoRA samples: {sample}")
        print(f"  UNet samples: {unet_sample}")

    # Now manually compute delta and check magnitude
    print(f"\nDelta vs base weight magnitude check (scale={scale}):")
    proc_samples = []
    for proc_name, proc in bare_unet.attn_processors.items():
        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(bare_unet.named_modules()).get(attn_module_name)
        if attn_module is None:
            continue
        if hasattr(attn_module, 'to_q'):
            base_w = attn_module.to_q.weight.data.float()
            down_key = f'{prefix}_to_q_lora_down'
            up_key = f'{prefix}_to_q_lora_up'
            if down_key in lora_state and up_key in lora_state:
                delta = (lora_state[up_key].float() @ lora_state[down_key].float()) * scale
                ratio = delta.norm() / (base_w.norm() + 1e-8)
                proc_samples.append((proc_name, base_w.norm(), delta.norm(), ratio))
                if len(proc_samples) >= 5:
                    break

    for name, base_norm, delta_norm, ratio in proc_samples:
        print(f"  {name}: base_norm={base_norm:.4f}, delta_norm={delta_norm:.6f}, ratio={ratio:.6f}")

    # Also check: are the base weights DIFFERENT between v29 and base?
    base_ckpt_path = os.path.join(PIPELINE_PATH, 'unet', 'diffusion_pytorch_model.safetensors')
    base_ckpt = load_file(base_ckpt_path)

    print(f"\nBase vs v29 weight comparison:")
    v29_attn_keys = [k for k in ckpt.keys() if 'attn1.to_q.weight' in k or 'attn2.to_q.weight' in k]
    base_attn_keys = [k for k in base_ckpt.keys() if 'attn1.to_q.weight' in k or 'attn2.to_q.weight' in k]

    common = set(v29_attn_keys) & set(base_attn_keys)
    print(f"  Common attn keys: {len(common)}")
    if common:
        diffs = []
        for k in list(common)[:10]:
            d = (ckpt[k].float() - base_ckpt[k].float())
            diffs.append(d.norm().item())
        print(f"  Weight differences: mean={sum(diffs)/len(diffs):.4f}, max={max(diffs):.4f}")
        if max(diffs) < 0.001:
            print("  v29 and base UNet have IDENTICAL attention weights!")
        else:
            print("  v29 and base UNet have DIFFERENT attention weights — correct!")


if __name__ == '__main__':
    test_merge_verification()
