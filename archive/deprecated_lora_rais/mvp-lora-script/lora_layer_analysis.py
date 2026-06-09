"""
Phase 3: LoRA Layer Analysis
Analyze which layers LoRA is applied to and whether this is correct.
"""
import os
import sys
import json
import torch
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline, RefOnlyNoisedUNet, ReferenceOnlyAttnProc
from mvpainter.lora_utils import create_lora_processors
from diffusers import EulerAncestralDiscreteScheduler, UNet2DConditionModel
from diffusers.models.attention_processor import LoRAAttnProcessor2_0


def analyze_unet_attention_layers(unet):
    """Analyze all attention layers in the UNet."""
    print("=" * 60)
    print("UNet ATTENTION LAYER ANALYSIS")
    print("=" * 60)

    layers = []
    for name, module in unet.named_modules():
        if 'attn1' in name or 'attn2' in name:
            if hasattr(module, 'to_q'):
                layer_info = {
                    'name': name,
                    'type': 'attn1' if 'attn1' in name else 'attn2',
                    'hidden_size': module.to_q.in_features,
                    'cross_attn_dim': module.to_k.in_features if 'attn2' in name else None,
                    'has_to_q': hasattr(module, 'to_q'),
                    'has_to_k': hasattr(module, 'to_k'),
                    'has_to_v': hasattr(module, 'to_v'),
                    'has_to_out': hasattr(module, 'to_out'),
                }
                layers.append(layer_info)

    # Count by type
    attn1_count = sum(1 for l in layers if l['type'] == 'attn1')
    attn2_count = sum(1 for l in layers if l['type'] == 'attn2')

    print(f"\nTotal attention layers: {len(layers)}")
    print(f"  Self-attention (attn1): {attn1_count}")
    print(f"  Cross-attention (attn2): {attn2_count}")

    # Group by block
    blocks = defaultdict(lambda: {'attn1': [], 'attn2': []})
    for l in layers:
        # Extract block name (e.g., "down_blocks.0.attentions.0.transformer_blocks.0")
        parts = l['name'].split('.')
        block_name = '.'.join(parts[:4]) if len(parts) > 4 else '.'.join(parts[:3])
        blocks[block_name][l['type']].append(l['name'])

    print(f"\nAttention blocks: {len(blocks)}")
    for block_name, attns in sorted(blocks.items()):
        print(f"  {block_name}:")
        print(f"    attn1: {len(attns['attn1'])} layers")
        print(f"    attn2: {len(attns['attn2'])} layers")

    return layers


def analyze_lora_placement(unet, rank=8, alpha=8):
    """Analyze where LoRA would be placed (without actually creating processors)."""
    print("\n" + "=" * 60)
    print("LoRA PLACEMENT ANALYSIS (Theoretical)")
    print("=" * 60)

    # Analyze each attention processor
    attn1_info = []
    attn2_info = []

    for name, proc in unet.attn_processors.items():
        attn_name = name.replace('.processor', '')
        attn_module = dict(unet.named_modules()).get(attn_name)

        if attn_module is None:
            continue

        hidden_size = attn_module.to_q.in_features if hasattr(attn_module, 'to_q') else None
        cross_attn_dim = attn_module.to_k.in_features if hasattr(attn_module, 'to_k') and 'attn2' in name else None

        info = {
            'name': name,
            'attn_name': attn_name,
            'type': 'attn1' if 'attn1' in name else 'attn2',
            'hidden_size': hidden_size,
            'cross_attn_dim': cross_attn_dim,
            'is_reference': name.endswith("attn1.processor"),
            'processor_type': type(proc).__name__,
        }

        if info['type'] == 'attn1':
            attn1_info.append(info)
        else:
            attn2_info.append(info)

    print(f"\nAttention layers that would get LoRA:")
    print(f"  Self-attention (attn1): {len(attn1_info)} layers")
    print(f"  Cross-attention (attn2): {len(attn2_info)} layers")

    print(f"\nReference attention would be enabled for: {sum(1 for l in attn1_info if l['is_reference'])} attn1 layers")

    # Show sample layers
    print("\nSample attn1 layers:")
    for l in attn1_info[:3]:
        print(f"  {l['name']}:")
        print(f"    Hidden size: {l['hidden_size']}")
        print(f"    Is reference: {l['is_reference']}")
        print(f"    Processor type: {l['processor_type']}")

    print("\nSample attn2 layers:")
    for l in attn2_info[:3]:
        print(f"  {l['name']}:")
        print(f"    Hidden size: {l['hidden_size']}")
        print(f"    Cross-attention dim: {l['cross_attn_dim']}")
        print(f"    Processor type: {l['processor_type']}")

    return attn1_info, attn2_info


def analyze_reference_attention():
    """Analyze how reference attention works and its interaction with LoRA."""
    print("\n" + "=" * 60)
    print("REFERENCE ATTENTION ANALYSIS")
    print("=" * 60)

    print("""
ReferenceOnlyAttnProc works as follows:

1. During training (mode='w'):
   - Stores encoder_hidden_states in ref_dict[name]
   - This is the "write" phase where reference features are saved

2. During inference (mode='r'):
   - Concatenates encoder_hidden_states with stored ref_dict[name]
   - This is the "read" phase where reference features are used

3. The 'enabled' flag:
   - Only enabled for attn1 (self-attention)
   - attn2 (cross-attention) does NOT use reference attention

4. Key insight:
   - attn1 handles self-attention AND reference attention
   - attn2 handles cross-attention with text/image embeddings

5. Potential issue with LoRA on attn1:
   - LoRA modifies the attention computation
   - If LoRA disrupts the reference feature storage/retrieval,
     the model loses its ability to use condition images
   - This could explain black/noisy outputs
""")


def check_lora_target_modules():
    """Check what modules LoRA should target."""
    print("\n" + "=" * 60)
    print("LoRA TARGET MODULES ANALYSIS")
    print("=" * 60)

    print("""
Current LoRA implementation targets:
  - to_q (query projection)
  - to_k (key projection)
  - to_v (value projection)
  - to_out (output projection)

These are applied to BOTH attn1 and attn2.

Recommendations from literature:
  1. For image generation tasks, LoRA on cross-attention (attn2) is often sufficient
  2. Self-attention (attn1) LoRA can help with style/content control
  3. But in reference attention architectures, attn1 has a special role

For MV-Painter specifically:
  - attn1 stores/retrieves reference features
  - attn2 processes text/image embeddings
  - Modifying attn1 with LoRA may disrupt reference attention

Suggested experiments:
  1. LoRA only on attn2 (cross-attention)
  2. LoRA on both attn1 and attn2 but with different ranks
  3. LoRA on attn1 with lower rank than attn2
""")


def generate_report(output_path, attn1_info, attn2_info):
    """Generate LoRA layer analysis report."""
    report = f"""# LoRA Layer Analysis Report

## Summary

| Metric | Value |
|--------|-------|
| Total attn1 (self-attention) layers | {len(attn1_info)} |
| Total attn2 (cross-attention) layers | {len(attn2_info)} |
| Reference attention enabled for attn1 | {sum(1 for l in attn1_info if l['is_reference'])} |

## Detailed Layer Information

### Self-Attention (attn1) Layers

| Layer Name | Hidden Size | Is Reference | Processor Type |
|------------|-------------|--------------|----------------|
"""

    for l in attn1_info[:20]:  # Show first 20
        report += f"| {l['name'][-60:]} | {l['hidden_size']} | {l['is_reference']} | {l['processor_type']} |\n"

    if len(attn1_info) > 20:
        report += f"| ... and {len(attn1_info) - 20} more layers | | | |\n"

    report += f"""
### Cross-Attention (attn2) Layers

| Layer Name | Hidden Size | Cross-Attn Dim | Processor Type |
|------------|-------------|----------------|----------------|
"""

    for l in attn2_info[:20]:  # Show first 20
        report += f"| {l['name'][-60:]} | {l['hidden_size']} | {l['cross_attn_dim']} | {l['processor_type']} |\n"

    if len(attn2_info) > 20:
        report += f"| ... and {len(attn2_info) - 20} more layers | | | |\n"

    report += """
## Critical Analysis

### Problem: LoRA on attn1 Disrupts Reference Attention

MV-Painter uses a reference attention mechanism where:
1. **attn1 (self-attention)** stores condition image features during the "write" phase
2. **attn1 (self-attention)** retrieves these features during the "read" phase
3. **attn2 (cross-attention)** processes text/image embeddings normally

When LoRA is applied to attn1:
- The attention computation is modified by LoRA weights
- This can disrupt the reference feature storage/retrieval
- The model may lose its ability to use condition images
- Result: black or noisy outputs

### Evidence

1. The reference attention mechanism (`ReferenceOnlyAttnProc`) only enables for attn1
2. LoRA modifies the same attn1 layers that handle reference features
3. Black/noisy outputs suggest the model is not receiving condition information

## Recommendations

### Option 1: LoRA Only on attn2 (RECOMMENDED)

```python
# Modify create_lora_processors to only target attn2
for name, _ in unet.attn_processors.items():
    if 'attn2' not in name:
        continue  # Skip attn1
    # ... create LoRA processor for attn2 only
```

**Pros:**
- Preserves reference attention mechanism
- Cross-attention is often sufficient for style/content control
- Lower risk of catastrophic failure

**Cons:**
- May have less capacity for learning new patterns

### Option 2: LoRA on Both with Different Ranks

```python
# Use lower rank for attn1, higher for attn2
attn1_rank = 2
attn2_rank = 8
```

**Pros:**
- Can still modify self-attention if needed
- Lower rank on attn1 reduces risk of disrupting reference attention

**Cons:**
- More complex implementation
- Still has some risk

### Option 3: LoRA on attn1 Only for Non-Reference Layers

```python
# Only apply LoRA to attn1 layers that don't have reference attention
for name, proc in processors.items():
    if 'attn1' in name and proc.enabled:
        continue  # Skip reference attention layers
    # ... create LoRA processor
```

**Pros:**
- Preserves reference attention
- Can still modify some self-attention layers

**Cons:**
- Complex logic to identify which layers have reference attention

## Conclusion

**The most likely cause of LoRA training failure is applying LoRA to attn1 layers that handle reference attention.**

The reference attention mechanism is critical for MV-Painter's ability to use condition images. Modifying these layers with LoRA disrupts this mechanism, leading to black or noisy outputs.

**Immediate action: Create a new LoRA configuration that only targets attn2 (cross-attention) layers.**
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {output_path}")


if __name__ == '__main__':
    output_dir = '/4T/CXY/MV-Painter/lora_layer_report'
    os.makedirs(output_dir, exist_ok=True)

    # Load pipeline
    print("Loading pipeline...")
    pipeline = MVPainter_Pipeline.from_pretrained(
        '../checkpoints/hf_repo',
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
        pipeline.scheduler.config, timestep_spacing='trailing',
    )

    # Wrap in RefOnlyNoisedUNet
    train_sched = None  # Not needed for analysis
    unet = RefOnlyNoisedUNet(pipeline.unet, train_sched, pipeline.scheduler)

    # Analyze
    layers = analyze_unet_attention_layers(unet.unet)
    attn1_info, attn2_info = analyze_lora_placement(unet.unet, rank=8, alpha=8)
    analyze_reference_attention()
    check_lora_target_modules()

    # Generate report
    generate_report(os.path.join(output_dir, 'lora_layer_report.md'), attn1_info, attn2_info)
