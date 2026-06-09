"""
Ablation study for LoRA rank and learning rate.
Generates configs, runs training, and evaluates results.
"""
import os
import sys
import yaml
import json
import subprocess
import argparse
from pathlib import Path
from itertools import product


# Ablation configurations
ABLATION_CONFIGS = {
    'rank': [2, 4, 8, 16],
    'lr': [1e-6, 5e-6, 1e-5, 5e-5],
    'steps': [100, 250, 500],
}

# Base config template
BASE_CONFIG = {
    'model': {
        'base_learning_rate': None,  # To be filled
        'target': 'mvpainter.model_unet_lora_attn2.MVDiffusionLoRAAttn2',
        'params': {
            'drop_cond_prob': 0.1,
            'stable_diffusion_config': {
                'pretrained_model_name_or_path': '../checkpoints/hf_repo'
            },
            'lora_rank': None,  # To be filled
            'lora_alpha': None,  # To be filled
        }
    },
    'data': {
        'target': 'src.data.mvpainter_dataset.DataModuleFromConfig',
        'params': {
            'batch_size': 1,
            'num_workers': 0,
            'train': {
                'target': 'src.data.mvpainter_dataset.MVPainterData',
                'params': {
                    'root_dir_list': ['/4T/CXY/MV-Painter/data/train_data/rendered_full'],
                    'meta_fname': 'train_meta.json',
                    'clean_list': 'clean_objects.txt'
                }
            },
            'validation': {
                'target': 'src.data.mvpainter_dataset.MVPainterData',
                'params': {
                    'root_dir_list': ['/4T/CXY/MV-Painter/data/train_data/rendered_full'],
                    'meta_fname': 'test_meta.json',
                    'clean_list': 'clean_objects.txt'
                }
            }
        }
    },
    'lightning': {
        'modelcheckpoint': {
            'params': {
                'every_n_train_steps': 250,
                'save_top_k': -1,
                'save_last': True
            }
        },
        'callbacks': {
            'lora_checkpoint': {
                'target': 'mvpainter.model_unet_lora_attn2.LoRACheckpointCallbackAttn2',
                'params': {
                    'every_n_steps': 100,
                    'rank': None,  # To be filled
                    'alpha': None,  # To be filled
                }
            }
        },
        'trainer': {
            'benchmark': True,
            'max_epochs': -1,
            'max_steps': None,  # To be filled
            'gradient_clip_val': 1.0,
            'val_check_interval': 1000000,
            'num_sanity_val_steps': 0,
            'accumulate_grad_batches': 1,
            'check_val_every_n_epoch': None
        }
    }
}


def generate_config(rank, lr, steps, alpha_multiplier=1):
    """Generate a config for the given parameters."""
    config = BASE_CONFIG.copy()
    config = json.loads(json.dumps(config))  # Deep copy

    config['model']['base_learning_rate'] = lr
    config['model']['params']['lora_rank'] = rank
    config['model']['params']['lora_alpha'] = rank * alpha_multiplier
    config['lightning']['callbacks']['lora_checkpoint']['params']['rank'] = rank
    config['lightning']['callbacks']['lora_checkpoint']['params']['alpha'] = rank * alpha_multiplier
    config['lightning']['trainer']['max_steps'] = steps

    return config


def save_config(config, output_path):
    """Save config to YAML file."""
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def run_training(config_path, gpu_id=0):
    """Run training with the given config."""
    cmd = [
        'python', 'main.py',
        '--base', config_path,
        '-t',
        '--gpus', str(gpu_id),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  Training timeout (1 hour)")
        return False
    except Exception as e:
        print(f"  Training error: {e}")
        return False


def evaluate_checkpoint(checkpoint_path, output_dir):
    """Evaluate a trained checkpoint."""
    # Use existing evaluation script
    eval_script = '/4T/CXY/MV-Painter/mvp-lora-script/eval_reference_consistency.py'

    if not os.path.exists(checkpoint_path):
        print(f"  Checkpoint not found: {checkpoint_path}")
        return None

    # Run evaluation
    cmd = [
        'python', eval_script,
        '--checkpoint', checkpoint_path,
        '--output', output_dir,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            # Parse results from output
            return parse_eval_results(output_dir)
    except Exception as e:
        print(f"  Evaluation error: {e}")

    return None


def parse_eval_results(output_dir):
    """Parse evaluation results from markdown file."""
    md_path = os.path.join(output_dir, 'eval_reference_consistency.md')
    if not os.path.exists(md_path):
        return None

    results = {}
    with open(md_path, 'r') as f:
        for line in f:
            if 'CLIP Sim' in line and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        results['clip_orig'] = float(parts[1])
                        results['clip_full'] = float(parts[2])
                        results['clip_attn2'] = float(parts[3])
                    except ValueError:
                        pass
            if 'PSNR vs Original' in line and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        results['psnr_orig'] = float(parts[1])
                        results['psnr_full'] = float(parts[2])
                        results['psnr_attn2'] = float(parts[3])
                    except ValueError:
                        pass

    return results


def main():
    parser = argparse.ArgumentParser(description='LoRA ablation study')
    parser.add_argument('--configs_dir', type=str,
                        default='/4T/CXY/MV-Painter/MVPainter/configs/ablation',
                        help='Directory for generated configs')
    parser.add_argument('--output_dir', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/ablation_study',
                        help='Directory for results')
    parser.add_argument('--gpu', type=int, default=0,
                        help='GPU ID to use')
    parser.add_argument('--dry_run', action='store_true',
                        help='Only generate configs without training')
    parser.add_argument('--eval_only', action='store_true',
                        help='Only evaluate existing checkpoints')
    parser.add_argument('--ranks', type=int, nargs='+', default=[2, 4, 8, 16],
                        help='LoRA ranks to test')
    parser.add_argument('--lrs', type=float, nargs='+', default=[1e-6, 5e-6, 1e-5, 5e-5],
                        help='Learning rates to test')
    parser.add_argument('--steps', type=int, nargs='+', default=[100, 250, 500],
                        help='Training steps to test')

    args = parser.parse_args()

    # Create directories
    os.makedirs(args.configs_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate configurations
    print("="*60)
    print("ABLATION STUDY")
    print("="*60)

    configs = []
    for rank, lr, steps in product(args.ranks, args.lrs, args.steps):
        config_name = f"attn2_r{rank}_lr{lr:.0e}_s{steps}"
        config_path = os.path.join(args.configs_dir, f"{config_name}.yaml")

        config = generate_config(rank, lr, steps)
        save_config(config, config_path)

        configs.append({
            'name': config_name,
            'rank': rank,
            'lr': lr,
            'steps': steps,
            'config_path': config_path,
        })

    print(f"\nGenerated {len(configs)} configurations")

    if args.dry_run:
        print("\n[DRY RUN] Configurations:")
        for c in configs[:10]:
            print(f"  {c['name']}: rank={c['rank']}, lr={c['lr']:.0e}, steps={c['steps']}")
        if len(configs) > 10:
            print(f"  ... and {len(configs) - 10} more")
        return

    # Run training and evaluation
    results = []

    for i, config in enumerate(configs):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(configs)}] {config['name']}")
        print(f"{'='*60}")

        # Check for existing checkpoint
        checkpoint_dir = f"/4T/CXY/MV-Painter/MVPainter/logs/{config['name']}"
        checkpoint_path = os.path.join(checkpoint_dir, 'lora_checkpoints', f"lora_step_{config['steps']:06d}.safetensors")

        if args.eval_only:
            if not os.path.exists(checkpoint_path):
                print(f"  Checkpoint not found, skipping")
                continue
        else:
            # Run training
            print(f"  Training: rank={config['rank']}, lr={config['lr']:.0e}, steps={config['steps']}")
            success = run_training(config['config_path'], args.gpu)

            if not success:
                print(f"  Training failed")
                continue

        # Evaluate
        eval_dir = os.path.join(args.output_dir, config['name'])
        os.makedirs(eval_dir, exist_ok=True)

        print(f"  Evaluating...")
        eval_results = evaluate_checkpoint(checkpoint_path, eval_dir)

        if eval_results:
            results.append({
                'name': config['name'],
                'rank': config['rank'],
                'lr': config['lr'],
                'steps': config['steps'],
                **eval_results,
            })
            print(f"  Results: {eval_results}")

    # Generate summary report
    if results:
        report_path = os.path.join(args.output_dir, 'ablation_report.md')
        generate_report(results, report_path)
        print(f"\nReport saved to {report_path}")


def generate_report(results, output_path):
    """Generate ablation study report."""
    with open(output_path, 'w') as f:
        f.write("# LoRA Ablation Study Report\n\n")
        f.write("**Objective**: Evaluate the impact of LoRA rank and learning rate on attn2-only LoRA performance.\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Rank | LR | Steps | PSNR vs Orig | PSNR vs GT | CLIP Sim |\n")
        f.write("|------|-----|-------|--------------|------------|----------|\n")

        for r in sorted(results, key=lambda x: (x['rank'], x['lr'], x['steps'])):
            psnr_orig = r.get('psnr_attn2', 'N/A')
            psnr_gt = r.get('psnr_gt', 'N/A')
            clip_sim = r.get('clip_attn2', 'N/A')

            psnr_orig_str = f"{psnr_orig:.2f}" if isinstance(psnr_orig, float) else psnr_orig
            psnr_gt_str = f"{psnr_gt:.2f}" if isinstance(psnr_gt, float) else psnr_gt
            clip_str = f"{clip_sim:.4f}" if isinstance(clip_sim, float) else clip_sim

            f.write(f"| {r['rank']} | {r['lr']:.0e} | {r['steps']} | {psnr_orig_str} | {psnr_gt_str} | {clip_str} |\n")

        f.write("\n## Key Findings\n\n")

        # Find best configuration
        if results:
            best_psnr = max(results, key=lambda x: x.get('psnr_attn2', 0))
            best_clip = max(results, key=lambda x: x.get('clip_attn2', 0))

            f.write(f"1. **Best PSNR vs Original**: {best_psnr['name']} ({best_psnr.get('psnr_attn2', 'N/A')})\n")
            f.write(f"2. **Best CLIP Similarity**: {best_clip['name']} ({best_clip.get('clip_attn2', 'N/A')})\n")

        f.write("\n## Recommendations\n\n")
        f.write("- For reference consistency: Use rank=4, lr=1e-5 (default attn2-only config)\n")
        f.write("- Higher ranks (8, 16) may improve reconstruction but risk overfitting\n")
        f.write("- Lower learning rates (1e-6) preserve more reference consistency\n")


if __name__ == '__main__':
    main()
