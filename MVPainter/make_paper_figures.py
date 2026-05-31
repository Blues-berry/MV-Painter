"""
Generate paper-quality comparison figures from fixed_comparison_results.

Creates:
1. Per-sample comparison: zeroshot vs LoRA-r4 vs LoRA-r8 (3 columns)
2. Scale sweep figure: 5 scales x 2 ranks (grid)
3. Combined figure for paper

Usage:
    python make_paper_figures.py
"""
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

RESULTS_DIR = 'fixed_comparison_results'
OUTPUT_DIR = 'paper_figures'

# Test samples
SAMPLES = [
    'd6a5427888b8413fbfcbcaad14353af8',
    'e3f35d4cfbb14410bf96a4ffa28235a1',
    'f0ef4adc17ee4929b40e894c608061ea',
    'f63daf968be34047bc513feb756b5828',
]

SCALES = [0.0, 0.1, 0.25, 0.5, 1.0]


def load_result(path):
    """Load result image from directory."""
    img_path = os.path.join(path, 'result_6view.png')
    if os.path.exists(img_path):
        return Image.open(img_path)
    return None


def create_sample_comparison():
    """Create per-sample comparison: zeroshot vs r4 vs r8."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for sample in SAMPLES:
        zeroshot = load_result(os.path.join(RESULTS_DIR, f'{sample}_zeroshot'))
        r4 = load_result(os.path.join(RESULTS_DIR, f'{sample}_lora_r4'))
        r8 = load_result(os.path.join(RESULTS_DIR, f'{sample}_lora_r8'))

        if any(img is None for img in [zeroshot, r4, r8]):
            print(f'Skip {sample}: missing results')
            continue

        fig, axes = plt.subplots(1, 3, figsize=(18, 10))

        for ax, img, title in zip(
            axes,
            [zeroshot, r4, r8],
            ['Zero-shot (Baseline)', 'LoRA rank=4', 'LoRA rank=8']
        ):
            ax.imshow(np.array(img))
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.axis('off')

        plt.tight_layout()
        out_path = os.path.join(OUTPUT_DIR, f'comparison_{sample[:8]}.png')
        plt.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'Saved: {out_path}')


def create_scale_sweep_figure():
    """Create scale sweep grid: scales x ranks."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sample = SAMPLES[0]  # Use first sample

    fig, axes = plt.subplots(2, len(SCALES), figsize=(25, 10))

    for row, rank_label in enumerate(['r4', 'r8']):
        for col, scale in enumerate(SCALES):
            dir_name = f'sweep_{sample}_{rank_label}_s{scale}'
            img = load_result(os.path.join(RESULTS_DIR, dir_name))

            ax = axes[row, col]
            if img is not None:
                ax.imshow(np.array(img))
            ax.set_title(f'{rank_label.upper()}, scale={scale}', fontsize=11)
            ax.axis('off')

    plt.suptitle('Scale Sweep: LoRA-r4 (top) vs LoRA-r8 (bottom)', fontsize=14, fontweight='bold')
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, 'scale_sweep.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {out_path}')


def create_combined_figure():
    """Create a combined figure for the paper: 4 samples x 3 conditions."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig = plt.figure(figsize=(20, 22))
    gs = GridSpec(4, 3, figure=fig, hspace=0.15, wspace=0.05)

    conditions = ['zeroshot', 'lora_r4', 'lora_r8']
    cond_labels = ['Zero-shot', 'LoRA rank=4', 'LoRA rank=8']

    for row, sample in enumerate(SAMPLES):
        for col, (cond, label) in enumerate(zip(conditions, cond_labels)):
            img = load_result(os.path.join(RESULTS_DIR, f'{sample}_{cond}'))

            ax = fig.add_subplot(gs[row, col])
            if img is not None:
                ax.imshow(np.array(img))

            if row == 0:
                ax.set_title(label, fontsize=13, fontweight='bold', pad=10)
            if col == 0:
                short_id = sample[:8]
                ax.set_ylabel(f'Sample {row+1}\n({short_id})', fontsize=10, rotation=0, labelpad=80, va='center')
            ax.set_xticks([])
            ax.set_yticks([])

    plt.suptitle('LoRA Fine-tuning Comparison (Fixed Merge)', fontsize=16, fontweight='bold', y=0.98)
    out_path = os.path.join(OUTPUT_DIR, 'combined_comparison.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    print('Creating sample comparisons...')
    create_sample_comparison()

    print('\nCreating scale sweep figure...')
    create_scale_sweep_figure()

    print('\nCreating combined figure...')
    create_combined_figure()

    print(f'\nDone! Figures in {OUTPUT_DIR}/')
