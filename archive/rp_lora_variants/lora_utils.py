import json
import os
from typing import Dict, Optional

import torch
from safetensors.torch import save_file, load_file
from diffusers.models.attention_processor import LoRAAttnProcessor2_0, AttnProcessor2_0

from .mvpainter_pipeline import ReferenceOnlyAttnProc


def create_lora_processors(
    unet,
    rank: int = 8,
    network_alpha: Optional[int] = None,
) -> Dict[str, ReferenceOnlyAttnProc]:
    """Create LoRA + ReferenceOnlyAttnProc processors for all attention layers in a UNet."""
    processors = {}
    for name, _ in unet.attn_processors.items():
        # Get the attention module to determine dimensions
        attn_name = name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_name]
        hidden_size = attn_module.to_q.in_features
        cross_attn_dim = attn_module.to_k.in_features if 'attn2' in name else None

        lora_proc = LoRAAttnProcessor2_0(
            hidden_size=hidden_size,
            cross_attention_dim=cross_attn_dim,
            rank=rank,
            network_alpha=network_alpha,
        )
        processors[name] = ReferenceOnlyAttnProc(
            lora_proc,
            enabled=name.endswith("attn1.processor"),
            name=name,
        )
    return processors


def extract_lora_state_dict(processors: Dict) -> Dict[str, torch.Tensor]:
    """Extract LoRA parameters from a processor dict (LoRA wrapped in ReferenceOnlyAttnProc)."""
    lora_state = {}
    for name, proc in processors.items():
        # proc is ReferenceOnlyAttnProc, proc.chained_proc is LoRAAttnProcessor2_0
        lora_proc = proc.chained_proc
        if not isinstance(lora_proc, LoRAAttnProcessor2_0):
            continue
        prefix = name.replace('.processor', '').replace('.', '_')
        for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
            lora_layer = getattr(lora_proc, param_name)
            lora_state[f'{prefix}_{param_name}_down'] = lora_layer.down.weight.data.clone()
            lora_state[f'{prefix}_{param_name}_up'] = lora_layer.up.weight.data.clone()
    return lora_state


def save_lora_weights(
    processors: Dict,
    save_path: str,
    rank: int,
    alpha: int,
):
    """Save LoRA weights to a safetensors file with metadata."""
    lora_state = extract_lora_state_dict(processors)
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    save_file(lora_state, save_path)

    # Save config
    config_path = save_path.replace('.safetensors', '_config.json')
    config = {
        'rank': rank,
        'alpha': alpha,
        'num_layers': len([k for k in lora_state if k.endswith('_down')]),
    }
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Saved LoRA weights ({len(lora_state)} tensors) to {save_path}")


def load_lora_weights(
    unet,
    lora_path: str,
    rank: int,
    alpha: int,
) -> Dict[str, ReferenceOnlyAttnProc]:
    """Load LoRA weights and set processors on a bare UNet. Returns processor dict."""
    processors = create_lora_processors(unet, rank=rank, network_alpha=alpha)
    lora_state = load_file(lora_path)

    for name, proc in processors.items():
        lora_proc = proc.chained_proc
        if not isinstance(lora_proc, LoRAAttnProcessor2_0):
            continue
        prefix = name.replace('.processor', '').replace('.', '_')
        for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
            lora_layer = getattr(lora_proc, param_name)
            down_key = f'{prefix}_{param_name}_down'
            up_key = f'{prefix}_{param_name}_up'
            if down_key in lora_state:
                lora_layer.down.weight.data = lora_state[down_key]
            if up_key in lora_state:
                lora_layer.up.weight.data = lora_state[up_key]

    unet.set_attn_processor(processors)
    return processors


@torch.no_grad()
def merge_lora_into_unet(
    unet,
    lora_path: str,
    rank: int,
    alpha: int,
):
    """Merge LoRA weights into the base UNet linear layers for inference.

    After merging, LoRA overhead is removed but ReferenceOnlyAttnProc wrappers
    are preserved (needed by RefOnlyNoisedUNet for reference attention).
    W_merged = W_base + (alpha / rank) * (up @ down)
    """
    lora_state = load_file(lora_path)
    scale = alpha / rank

    # Iterate through processor names (which match the LoRA state dict key structure)
    for proc_name, _ in unet.attn_processors.items():
        # proc_name: "down_blocks.1.attentions.0.transformer_blocks.0.attn1.processor"
        # state dict prefix: "down_blocks_1_attentions_0_transformer_blocks_0_attn1"
        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_module_name]

        for proj_name in ['to_q', 'to_k', 'to_v']:
            down_key = f'{prefix}_{proj_name}_lora_down'
            up_key = f'{prefix}_{proj_name}_lora_up'
            if down_key in lora_state and up_key in lora_state:
                proj_layer = getattr(attn_module, proj_name)
                delta = (lora_state[up_key] @ lora_state[down_key]) * scale
                proj_layer.weight.data += delta.to(device=proj_layer.weight.device, dtype=proj_layer.weight.dtype)

        # to_out[0]
        down_key = f'{prefix}_to_out_lora_down'
        up_key = f'{prefix}_to_out_lora_up'
        if down_key in lora_state and up_key in lora_state:
            delta = (lora_state[up_key] @ lora_state[down_key]) * scale
            attn_module.to_out[0].weight.data += delta.to(device=attn_module.to_out[0].weight.device, dtype=attn_module.to_out[0].weight.dtype)

    # Replace LoRA processors with standard ones, but PRESERVE ReferenceOnlyAttnProc wrappers
    # (RefOnlyNoisedUNet depends on them for reference attention during inference)
    new_procs = {}
    for proc_name, proc in unet.attn_processors.items():
        if isinstance(proc, ReferenceOnlyAttnProc):
            proc.chained_proc = AttnProcessor2_0()
            new_procs[proc_name] = proc
        else:
            new_procs[proc_name] = AttnProcessor2_0()
    unet.set_attn_processor(new_procs)
    print(f"Merged LoRA weights from {lora_path} into UNet")
