"""
LoRA utilities with attn1-only support.
Applies LoRA ONLY to attn1 (self-attention) for ablation study.
attn2 (cross-attention) keeps original processors.
"""
import json
import os
from typing import Dict, Optional

import torch
from safetensors.torch import save_file, load_file
from diffusers.models.attention_processor import LoRAAttnProcessor2_0, AttnProcessor2_0

from .mvpainter_pipeline import ReferenceOnlyAttnProc


def create_lora_processors_attn1_only(
    unet,
    rank: int = 8,
    network_alpha: Optional[int] = None,
) -> Dict[str, ReferenceOnlyAttnProc]:
    """Create LoRA processors for attn1 only, preserve original processors for attn2.

    This is the reverse of attn2-only: applies LoRA to self-attention (attn1)
    while leaving cross-attention (attn2) untouched. Used for ablation to prove
    that attn1 LoRA is what breaks reference attention.
    """
    processors = {}
    for name, _ in unet.attn_processors.items():
        attn_name = name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_name]
        hidden_size = attn_module.to_q.in_features

        if 'attn2' in name:
            # Cross-attention: preserve original processor (no LoRA)
            default_proc = AttnProcessor2_0()
            processors[name] = ReferenceOnlyAttnProc(
                default_proc,
                enabled=False,  # attn2 doesn't use reference attention
                name=name,
            )
        else:
            # Self-attention: apply LoRA
            cross_attn_dim = attn_module.to_k.in_features if 'attn2' in name else None
            lora_proc = LoRAAttnProcessor2_0(
                hidden_size=hidden_size,
                cross_attention_dim=cross_attn_dim,
                rank=rank,
                network_alpha=network_alpha,
            )
            processors[name] = ReferenceOnlyAttnProc(
                lora_proc,
                enabled=True,  # attn1 uses reference attention
                name=name,
            )

    return processors


def extract_lora_state_dict_attn1_only(processors: Dict) -> Dict[str, torch.Tensor]:
    """Extract LoRA parameters from attn1 processors only."""
    lora_state = {}
    for name, proc in processors.items():
        if 'attn2' in name:
            continue  # Skip attn2

        if not isinstance(proc, ReferenceOnlyAttnProc):
            continue

        lora_proc = proc.chained_proc
        if not isinstance(lora_proc, LoRAAttnProcessor2_0):
            continue

        prefix = name.replace('.processor', '').replace('.', '_')
        for param_name in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']:
            if hasattr(lora_proc, param_name):
                lora_layer = getattr(lora_proc, param_name)
                lora_state[f'{prefix}_{param_name}_down'] = lora_layer.down.weight.data.clone()
                lora_state[f'{prefix}_{param_name}_up'] = lora_layer.up.weight.data.clone()

    return lora_state


def save_lora_weights_attn1_only(
    processors: Dict,
    save_path: str,
    rank: int,
    alpha: int,
):
    """Save LoRA weights for attn1 only."""
    lora_state = extract_lora_state_dict_attn1_only(processors)
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    save_file(lora_state, save_path)

    config_path = save_path.replace('.safetensors', '_config.json')
    config = {
        'rank': rank,
        'alpha': alpha,
        'num_layers': len([k for k in lora_state if k.endswith('_down')]),
        'target': 'attn1_only',
    }
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Saved attn1-only LoRA weights ({len(lora_state)} tensors) to {save_path}")


def merge_lora_into_unet_attn1_only(
    unet,
    lora_path: str,
    rank: int,
    alpha: int,
):
    """Merge LoRA weights into attn1 only, preserve attn2."""
    lora_state = load_file(lora_path)
    scale = alpha / rank

    for proc_name, _ in unet.attn_processors.items():
        if 'attn2' in proc_name:
            continue  # Skip attn2

        prefix = proc_name.replace('.processor', '').replace('.', '_')
        attn_module_name = proc_name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_module_name]

        for proj_name in ['to_q', 'to_k', 'to_v']:
            down_key = f'{prefix}_{proj_name}_lora_down'
            up_key = f'{prefix}_{proj_name}_lora_up'
            if down_key in lora_state and up_key in lora_state:
                proj_layer = getattr(attn_module, proj_name)
                delta = (lora_state[up_key] @ lora_state[down_key]) * scale
                proj_layer.weight.data += delta.to(
                    device=proj_layer.weight.device,
                    dtype=proj_layer.weight.dtype
                )

        down_key = f'{prefix}_to_out_lora_down'
        up_key = f'{prefix}_to_out_lora_up'
        if down_key in lora_state and up_key in lora_state:
            delta = (lora_state[up_key] @ lora_state[down_key]) * scale
            attn_module.to_out[0].weight.data += delta.to(
                device=attn_module.to_out[0].weight.device,
                dtype=attn_module.to_out[0].weight.dtype
            )

    print(f"Merged attn1-only LoRA weights from {lora_path} into UNet")
