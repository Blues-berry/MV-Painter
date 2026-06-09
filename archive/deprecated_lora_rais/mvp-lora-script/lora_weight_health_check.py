"""
Phase 4: LoRA Weight Health Check
Check existing LoRA checkpoints for numerical anomalies.
"""
import os
import sys
import json
import numpy as np
import torch
from safetensors.torch import load_file
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_lora_weights(lora_path):
    """Check LoRA weights for anomalies."""
    print("=" * 60)
    print(f"LoRA WEIGHT HEALTH CHECK: {os.path.basename(lora_path)}")
    print("=" * 60)

    # Load weights
    try:
        state = load_file(lora_path)
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        return None

    print(f"\nTotal tensors: {len(state)}")

    # Analyze each tensor
    results = {
        'total_tensors': len(state),
        'nan_count': 0,
        'inf_count': 0,
        'max_abs': 0,
        'mean_abs': 0,
        'std': 0,
        'layers': [],
        'anomalies': [],
    }

    all_values = []
    layer_stats = []

    for name, tensor in state.items():
        t = tensor.float()  # Convert to float32 for analysis

        # Check for NaN/Inf
        nan_count = torch.isnan(t).sum().item()
        inf_count = torch.isinf(t).sum().item()

        if nan_count > 0 or inf_count > 0:
            results['nan_count'] += nan_count
            results['inf_count'] += inf_count
            results['anomalies'].append({
                'name': name,
                'nan': nan_count,
                'inf': inf_count,
            })

        # Compute statistics
        abs_tensor = t.abs()
        max_abs = abs_tensor.max().item()
        mean_abs = abs_tensor.mean().item()
        std = t.std().item()

        layer_stat = {
            'name': name,
            'shape': list(tensor.shape),
            'max_abs': max_abs,
            'mean_abs': mean_abs,
            'std': std,
            'nan': nan_count,
            'inf': inf_count,
        }
        layer_stats.append(layer_stat)

        # Collect values for global stats
        all_values.append(t.flatten())

    # Compute global statistics
    all_values = torch.cat(all_values)
    results['max_abs'] = all_values.abs().max().item()
    results['mean_abs'] = all_values.abs().mean().item()
    results['std'] = all_values.std().item()

    # Find top anomalous layers
    layer_stats.sort(key=lambda x: x['max_abs'], reverse=True)
    results['top_layers'] = layer_stats[:20]

    # Compute delta_norm / weight_norm for each layer pair
    print("\nAnalyzing LoRA layer pairs (down/up)...")
    down_layers = {k: v for k, v in state.items() if '_down' in k}
    up_layers = {k: v for k, v in state.items() if '_up' in k}

    pair_stats = []
    for down_name, down_tensor in down_layers.items():
        up_name = down_name.replace('_down', '_up')
        if up_name in up_layers:
            up_tensor = up_layers[up_name]

            # Compute delta = up @ down
            down_t = down_tensor.float()
            up_t = up_tensor.float()

            if down_t.dim() == 2 and up_t.dim() == 2:
                delta = up_t @ down_t
                delta_norm = delta.norm().item()
                weight_norm = delta_norm  # This is the LoRA contribution

                pair_stat = {
                    'name': down_name.replace('_down', ''),
                    'down_shape': list(down_tensor.shape),
                    'up_shape': list(up_tensor.shape),
                    'delta_norm': delta_norm,
                    'max_delta': delta.abs().max().item(),
                    'mean_delta': delta.abs().mean().item(),
                }
                pair_stats.append(pair_stat)

    pair_stats.sort(key=lambda x: x['delta_norm'], reverse=True)
    results['pair_stats'] = pair_stats[:20]

    return results


def print_results(results):
    """Print analysis results."""
    if results is None:
        return

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal tensors: {results['total_tensors']}")
    print(f"NaN count: {results['nan_count']}")
    print(f"Inf count: {results['inf_count']}")
    print(f"Max absolute value: {results['max_abs']:.6f}")
    print(f"Mean absolute value: {results['mean_abs']:.6f}")
    print(f"Standard deviation: {results['std']:.6f}")

    if results['anomalies']:
        print(f"\n⚠️  ANOMALIES DETECTED:")
        for a in results['anomalies']:
            print(f"  {a['name']}: NaN={a['nan']}, Inf={a['inf']}")

    print(f"\nTop 10 layers by max absolute value:")
    for i, l in enumerate(results['top_layers'][:10]):
        print(f"  {i+1}. {l['name'][-50:]}")
        print(f"     max_abs={l['max_abs']:.6f}, mean={l['mean_abs']:.6f}, std={l['std']:.6f}")

    if results['pair_stats']:
        print(f"\nTop 10 LoRA pairs by delta_norm:")
        for i, p in enumerate(results['pair_stats'][:10]):
            print(f"  {i+1}. {p['name'][-50:]}")
            print(f"     delta_norm={p['delta_norm']:.6f}, max_delta={p['max_delta']:.6f}")


def generate_report(results, output_path, lora_path):
    """Generate health check report."""
    if results is None:
        report = f"# LoRA Weight Health Report\n\nError loading checkpoint: {lora_path}\n"
        with open(output_path, 'w') as f:
            f.write(report)
        return

    # Determine health status
    is_healthy = True
    issues = []

    if results['nan_count'] > 0:
        is_healthy = False
        issues.append(f"NaN values detected: {results['nan_count']}")

    if results['inf_count'] > 0:
        is_healthy = False
        issues.append(f"Inf values detected: {results['inf_count']}")

    if results['max_abs'] > 10:
        issues.append(f"Very large weights detected: max_abs={results['max_abs']:.4f}")

    if results['max_abs'] > 100:
        is_healthy = False
        issues.append(f"Extremely large weights: max_abs={results['max_abs']:.4f}")

    report = f"""# LoRA Weight Health Report

## Checkpoint Information

- **File**: {os.path.basename(lora_path)}
- **Path**: {lora_path}
- **Total tensors**: {results['total_tensors']}

## Health Status

**Status**: {'✅ HEALTHY' if is_healthy else '❌ UNHEALTHY'}

"""

    if issues:
        report += "### Issues Found\n\n"
        for issue in issues:
            report += f"- ⚠️ {issue}\n"
        report += "\n"

    report += f"""## Global Statistics

| Metric | Value |
|--------|-------|
| NaN count | {results['nan_count']} |
| Inf count | {results['inf_count']} |
| Max absolute value | {results['max_abs']:.6f} |
| Mean absolute value | {results['mean_abs']:.6f} |
| Standard deviation | {results['std']:.6f} |

## Top 20 Layers by Max Absolute Value

| Rank | Layer Name | Shape | Max Abs | Mean Abs | Std |
|------|------------|-------|---------|----------|-----|
"""

    for i, l in enumerate(results['top_layers']):
        report += f"| {i+1} | {l['name'][-60:]} | {l['shape']} | {l['max_abs']:.6f} | {l['mean_abs']:.6f} | {l['std']:.6f} |\n"

    if results['pair_stats']:
        report += """
## Top 20 LoRA Pairs by Delta Norm

| Rank | Layer Name | Down Shape | Up Shape | Delta Norm | Max Delta | Mean Delta |
|------|------------|------------|----------|------------|-----------|------------|
"""

        for i, p in enumerate(results['pair_stats']):
            report += f"| {i+1} | {p['name'][-60:]} | {p['down_shape']} | {p['up_shape']} | {p['delta_norm']:.6f} | {p['max_delta']:.6f} | {p['mean_delta']:.6f} |\n"

    report += """
## Diagnosis

"""

    if results['nan_count'] > 0 or results['inf_count'] > 0:
        report += """### Training Divergence Detected

The presence of NaN or Inf values indicates that training has diverged. This is typically caused by:
1. Learning rate too high
2. Gradient explosion
3. Numerical instability in the model

**Recommendation**: Reduce learning rate and add gradient clipping.
"""

    elif results['max_abs'] > 10:
        report += """### Large Weight Magnitude

The LoRA weights have very large magnitudes, which suggests:
1. LoRA is overfitting to the training data
2. The LoRA scaling (alpha/rank) may be too aggressive
3. The model is trying to make large corrections

**Recommendation**:
- Reduce learning rate
- Increase LoRA rank (to reduce per-weight magnitude)
- Add weight decay
"""

    else:
        report += """### Weight Magnitude Normal

The LoRA weights appear to have normal magnitudes. The issue may be elsewhere:
1. LoRA layer placement (attn1 vs attn2)
2. Pipeline/processing inconsistency
3. Training data quality

**Recommendation**: Continue debugging other aspects.
"""

    report += """
## Conclusion

"""

    if is_healthy:
        report += "The LoRA weights are numerically healthy. The training failure is likely due to:\n"
        report += "1. LoRA layer placement (modifying reference attention)\n"
        report += "2. Pipeline inconsistency\n"
        report += "3. Data quality issues\n"
    else:
        report += "The LoRA weights show numerical anomalies. The training has likely diverged.\n"
        report += "Recommendations:\n"
        report += "1. Reduce learning rate significantly (1e-5 or lower)\n"
        report += "2. Use attn2-only LoRA to avoid disrupting reference attention\n"
        report += "3. Add gradient clipping\n"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to {output_path}")


if __name__ == '__main__':
    output_dir = '/4T/CXY/MV-Painter/lora_weight_health_report'
    os.makedirs(output_dir, exist_ok=True)

    # Find LoRA checkpoints
    checkpoint_dirs = [
        '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090/lora_checkpoints',
        '/4T/CXY/MV-Painter/MVPainter/logs/mvpainter-train-unet-lora-5090-rank4/lora_checkpoints',
    ]

    for ckpt_dir in checkpoint_dirs:
        if not os.path.exists(ckpt_dir):
            print(f"Directory not found: {ckpt_dir}")
            continue

        for f in os.listdir(ckpt_dir):
            if f.endswith('.safetensors'):
                lora_path = os.path.join(ckpt_dir, f)
                print(f"\n{'='*60}")
                print(f"Checking: {lora_path}")

                results = check_lora_weights(lora_path)
                print_results(results)

                # Generate report
                report_name = f.replace('.safetensors', '_health_report.md')
                report_path = os.path.join(output_dir, report_name)
                generate_report(results, report_path, lora_path)
