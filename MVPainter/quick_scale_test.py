"""
Quick scale sweep: test scale=0.01, 0.05, 0.1, 0.25, 0.5, 1.0 on one sample.
"""
import os, sys, json, torch
from PIL import Image
from safetensors.torch import load_file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.lora_utils import merge_lora_into_unet
from diffusers import EulerAncestralDiscreteScheduler
from pytorch_lightning import seed_everything

PIPELINE_PATH = '../checkpoints/hf_repo'
LORA_R8 = 'logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
OUT = 'scale_sweep_results'

def get_inner(p):
    return p.unet.unet if hasattr(p.unet, 'unet') else p.unet

def reload(p):
    inner = get_inner(p)
    base_ckpt = os.path.join(PIPELINE_PATH, 'unet', 'diffusion_pytorch_model.safetensors')
    inner.load_state_dict(load_file(base_ckpt), strict=False)

def run(p, img, depth, out, seed=42):
    seed_everything(seed)
    os.makedirs(out, exist_ok=True)
    res = p(Image.open(img).convert('RGBA'), depth_image=Image.open(depth), num_inference_steps=50)
    res[0].save(os.path.join(out, 'result_6view.png'))

def verify(p):
    inner = get_inner(p)
    ref_count = sum(1 for n, pr in inner.attn_processors.items() if isinstance(pr, ReferenceOnlyAttnProc))
    total = len(inner.attn_processors)
    print(f"  ReferenceOnlyAttnProc: {ref_count}/{total}")

# Get test sample
with open(os.path.join(TRAIN_DATA, 'clean_objects.txt')) as f:
    obj = [l.strip() for l in f if l.strip()][-1]
img = os.path.join(TRAIN_DATA, obj, 'image', '000.png')
depth = os.path.join(TRAIN_DATA, obj, 'depth_png', '000.png')
print(f"Test sample: {obj}")

# Load config
with open(LORA_R8.replace('.safetensors', '_config.json')) as f:
    cfg = json.load(f)
rank, alpha = cfg['rank'], cfg['alpha']

# Load pipeline
print("Loading pipeline...")
p = MVPainter_Pipeline.from_pretrained(PIPELINE_PATH, torch_dtype=torch.float16)
p.scheduler = EulerAncestralDiscreteScheduler.from_config(p.scheduler.config, timestep_spacing='trailing')
p.prepare()  # Wrap in RefOnlyNoisedUNet with ReferenceOnlyAttnProc
inner = get_inner(p)

scales = [0.0, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0]
for s in scales:
    print(f"\n=== scale={s} ===")
    reload(p)

    if s > 0:
        # Manual merge with custom scale
        lora_state = load_file(LORA_R8)
        eff_scale = (alpha / rank) * s

        # Merge into bare UNet (RefOnlyNoisedUNet.__getattr__ delegates to it)
        from diffusers.models.attention_processor import AttnProcessor2_0
        inner_unet = inner.unet if hasattr(inner, 'unet') else inner

        for proc_name in inner_unet.attn_processors:
            prefix = proc_name.replace('.processor', '').replace('.', '_')
            attn_name = proc_name.replace('.processor', '')
            attn_mod = dict(inner_unet.named_modules()).get(attn_name)
            if attn_mod is None:
                continue

            for proj in ['to_q', 'to_k', 'to_v']:
                dk = f'{prefix}_{proj}_lora_down'
                uk = f'{prefix}_{proj}_lora_up'
                if dk in lora_state and uk in lora_state:
                    layer = getattr(attn_mod, proj)
                    delta = (lora_state[uk] @ lora_state[dk]) * eff_scale
                    layer.weight.data += delta.to(device=layer.weight.device, dtype=layer.weight.dtype)

            dk = f'{prefix}_to_out_lora_down'
            uk = f'{prefix}_to_out_lora_up'
            if dk in lora_state and uk in lora_state:
                delta = (lora_state[uk] @ lora_state[dk]) * eff_scale
                attn_mod.to_out[0].weight.data += delta.to(
                    device=attn_mod.to_out[0].weight.device,
                    dtype=attn_mod.to_out[0].weight.dtype,
                )

        # Preserve ReferenceOnlyAttnProc
        new_procs = {}
        for pn, pc in inner_unet.attn_processors.items():
            if isinstance(pc, ReferenceOnlyAttnProc):
                pc.chained_proc = AttnProcessor2_0()
                new_procs[pn] = pc
            else:
                new_procs[pn] = AttnProcessor2_0()
        inner_unet.set_attn_processor(new_procs)

    verify(p)
    out_dir = os.path.join(OUT, f'scale_{s}')
    run(p, img, depth, out_dir)
    print(f"  Saved to {out_dir}")

print("\nDone! Check results in scale_sweep_results/")
