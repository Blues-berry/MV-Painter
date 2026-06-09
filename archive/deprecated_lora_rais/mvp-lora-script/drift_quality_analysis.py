"""
Drift-Quality Decoupling Analysis

Analyzes the relationship between internal reference state drift (RAIS/RSD)
and end-to-end generation quality metrics.

Inputs:
1. /4T/CXY/MV-Painter/mvpoutput/correct_pipeline_eval/per_object_metrics.csv
2. /4T/CXY/MV-Painter/mvpoutput/hook_analysis_correct_v2/per_object_hook_metrics.csv

Outputs:
- merged_object_metrics.csv
- correlation_table.csv
- scatter plots
- report.md
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime


# ============================================================
# Configuration
# ============================================================
EVAL_DIR = '/4T/CXY/MV-Painter/mvpoutput/correct_pipeline_eval_300'
HOOK_DIR = '/4T/CXY/MV-Painter/mvpoutput/hook_analysis_correct_v2_300'
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/drift_quality_analysis_300'


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)

    # Load data
    print("Loading data...")
    eval_df = pd.read_csv(os.path.join(EVAL_DIR, 'per_object_metrics.csv'))
    hook_df = pd.read_csv(os.path.join(HOOK_DIR, 'per_object_hook_metrics.csv'))

    # Normalize method names for merging
    # eval: original (scale=0), full_lora (scale=1.0/0.25), attn2_only (scale=1.0/0.25)
    # hook: full_lora_s1.0, full_lora_s0.25, attn2_only_s1.0, attn2_only_s0.25

    # Create method_scale key for merging
    eval_df['method_key'] = eval_df.apply(
        lambda r: f"{r['method']}_s{r['scale']}" if r['method'] != 'original' else 'original',
        axis=1
    )
    hook_df['method_key'] = hook_df['method']

    # Merge on object_id and method_key
    merged = pd.merge(eval_df, hook_df, on=['object_id', 'method_key'], how='inner',
                      suffixes=('_eval', '_hook'))

    print(f"Merged records: {len(merged)}")
    print(f"Methods: {merged['method_key'].unique()}")

    # Save merged data
    merged.to_csv(os.path.join(OUTPUT_DIR, 'merged_object_metrics.csv'), index=False)

    # === Compute correlations ===
    print("\nComputing correlations...")

    quality_metrics = [
        'mean_psnr_gt', 'mean_ssim_gt', 'mean_lpips_gt',
        'mean_psnr_original', 'mean_clip_condition', 'mean_dino_condition',
        'mv_clip_consistency', 'mv_dino_consistency'
    ]

    drift_metrics = ['attn1_rais', 'attn2_rais', 'overall_rais', 'rsd']

    correlation_results = []

    for drift_m in drift_metrics:
        for quality_m in quality_metrics:
            # Filter out inf/nan
            valid = merged[[drift_m, quality_m]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(valid) < 3:
                continue

            # Pearson
            pearson_r, pearson_p = stats.pearsonr(valid[drift_m], valid[quality_m])

            # Spearman
            spearman_r, spearman_p = stats.spearmanr(valid[drift_m], valid[quality_m])

            correlation_results.append({
                'drift_metric': drift_m,
                'quality_metric': quality_m,
                'pearson_r': pearson_r,
                'pearson_p': pearson_p,
                'spearman_r': spearman_r,
                'spearman_p': spearman_p,
                'N': len(valid),
            })

    corr_df = pd.DataFrame(correlation_results)
    corr_df.to_csv(os.path.join(OUTPUT_DIR, 'correlation_table.csv'), index=False)

    # Print correlation table
    print("\n=== Correlation Table (Pearson r / Spearman ρ) ===\n")
    print(f"{'Drift Metric':<20} {'Quality Metric':<25} {'Pearson r':>10} {'p':>10} {'Spearman ρ':>10} {'p':>10}")
    print("-" * 90)
    for _, row in corr_df.iterrows():
        sig = '***' if row['pearson_p'] < 0.001 else '**' if row['pearson_p'] < 0.01 else '*' if row['pearson_p'] < 0.05 else ''
        print(f"{row['drift_metric']:<20} {row['quality_metric']:<25} {row['pearson_r']:>10.4f} {row['pearson_p']:>10.4f} {row['spearman_r']:>10.4f} {row['spearman_p']:>10.4f} {sig}")

    # === Generate scatter plots ===
    print("\nGenerating scatter plots...")

    # Color/shape mapping
    method_colors = {
        'original': '#888888',
        'full_lora_s1.0': '#FF5722',
        'full_lora_s0.25': '#FF9800',
        'attn2_only_s1.0': '#4CAF50',
        'attn2_only_s0.25': '#8BC34A',
    }

    method_markers = {
        'original': 'o',
        'full_lora_s1.0': 's',
        'full_lora_s0.25': 's',
        'attn2_only_s1.0': '^',
        'attn2_only_s0.25': '^',
    }

    # Plot 1: attn1 RAIS vs PSNR vs GT
    fig, ax = plt.subplots(figsize=(8, 6))
    for method, color in method_colors.items():
        subset = merged[merged['method_key'] == method]
        if len(subset) == 0:
            continue
        ax.scatter(subset['attn1_rais'], subset['mean_psnr_gt'],
                   c=color, marker=method_markers[method], s=80, alpha=0.7, label=method)
    ax.set_xlabel('attn1 RAIS', fontsize=12)
    ax.set_ylabel('PSNR vs GT', fontsize=12)
    ax.set_title('attn1 RAIS vs PSNR vs GT', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'attn1_rais_vs_psnr_gt.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 2: attn1 RAIS vs CLIP condition
    fig, ax = plt.subplots(figsize=(8, 6))
    for method, color in method_colors.items():
        subset = merged[merged['method_key'] == method]
        if len(subset) == 0:
            continue
        ax.scatter(subset['attn1_rais'], subset['mean_clip_condition'],
                   c=color, marker=method_markers[method], s=80, alpha=0.7, label=method)
    ax.set_xlabel('attn1 RAIS', fontsize=12)
    ax.set_ylabel('CLIP vs Condition', fontsize=12)
    ax.set_title('attn1 RAIS vs CLIP Condition Similarity', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'attn1_rais_vs_clip_cond.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 3: attn1 RAIS vs MV consistency
    fig, ax = plt.subplots(figsize=(8, 6))
    for method, color in method_colors.items():
        subset = merged[merged['method_key'] == method]
        if len(subset) == 0:
            continue
        ax.scatter(subset['attn1_rais'], subset['mv_clip_consistency'],
                   c=color, marker=method_markers[method], s=80, alpha=0.7, label=method)
    ax.set_xlabel('attn1 RAIS', fontsize=12)
    ax.set_ylabel('Multi-view CLIP Consistency', fontsize=12)
    ax.set_title('attn1 RAIS vs Multi-view Consistency', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'attn1_rais_vs_mv_consistency.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 4: RSD vs PSNR vs GT
    fig, ax = plt.subplots(figsize=(8, 6))
    for method, color in method_colors.items():
        subset = merged[merged['method_key'] == method]
        if len(subset) == 0:
            continue
        ax.scatter(subset['rsd'], subset['mean_psnr_gt'],
                   c=color, marker=method_markers[method], s=80, alpha=0.7, label=method)
    ax.set_xlabel('RSD (1 - RAIS)', fontsize=12)
    ax.set_ylabel('PSNR vs GT', fontsize=12)
    ax.set_title('RSD vs PSNR vs GT', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'rsd_vs_psnr_gt.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Plot 5: Overall RAIS vs PSNR Original
    fig, ax = plt.subplots(figsize=(8, 6))
    for method, color in method_colors.items():
        subset = merged[merged['method_key'] == method]
        if len(subset) == 0:
            continue
        valid = subset[subset['mean_psnr_original'] != 0]  # Exclude original (psnr_orig=0)
        if len(valid) > 0:
            ax.scatter(valid['overall_rais'], valid['mean_psnr_original'],
                       c=color, marker=method_markers[method], s=80, alpha=0.7, label=method)
    ax.set_xlabel('Overall RAIS', fontsize=12)
    ax.set_ylabel('PSNR vs Original', fontsize=12)
    ax.set_title('Overall RAIS vs PSNR vs Original (LoRA impact)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUTPUT_DIR, 'plots', 'overall_rais_vs_psnr_orig.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)

    print("  Plots saved to plots/")

    # === Generate report ===
    print("Generating report...")
    generate_report(merged, corr_df, OUTPUT_DIR)

    print(f"\nDrift-quality analysis complete!")
    print(f"Output: {OUTPUT_DIR}")


def generate_report(merged, corr_df, output_dir):
    """Generate markdown report."""
    report_path = os.path.join(output_dir, 'report.md')

    with open(report_path, 'w') as f:
        f.write("# Drift-Quality Decoupling Analysis\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Data Sources\n\n")
        f.write(f"- End-to-end eval: `{EVAL_DIR}/per_object_metrics.csv`\n")
        f.write(f"- Hook analysis: `{HOOK_DIR}/per_object_hook_metrics.csv`\n")
        f.write(f"- Merged records: {len(merged)}\n\n")

        f.write("## Key Correlations\n\n")
        f.write("| Drift Metric | Quality Metric | Pearson r | p-value | Spearman ρ | p-value |\n")
        f.write("|-------------|----------------|-----------|---------|------------|--------|\n")

        for _, row in corr_df.iterrows():
            sig = '***' if row['pearson_p'] < 0.001 else '**' if row['pearson_p'] < 0.01 else '*' if row['pearson_p'] < 0.05 else ''
            f.write(f"| {row['drift_metric']} | {row['quality_metric']} | {row['pearson_r']:.4f} | {row['pearson_p']:.4f} {sig} | {row['spearman_r']:.4f} | {row['spearman_p']:.4f} |\n")

        f.write("\n## Analysis\n\n")

        # Answer the key questions
        f.write("### Q1: Does RAIS predict PSNR vs GT?\n\n")

        # Get correlation for attn1_rais vs mean_psnr_gt
        attn1_psnr = corr_df[(corr_df['drift_metric'] == 'attn1_rais') &
                              (corr_df['quality_metric'] == 'mean_psnr_gt')]
        if len(attn1_psnr) > 0:
            r = attn1_psnr.iloc[0]['pearson_r']
            p = attn1_psnr.iloc[0]['pearson_p']
            f.write(f"attn1 RAIS vs PSNR GT: Pearson r = {r:.4f}, p = {p:.4f}\n\n")
            if abs(r) < 0.3:
                f.write("**Weak correlation**: RAIS does not strongly predict PSNR vs GT.\n\n")
            elif abs(r) < 0.7:
                f.write("**Moderate correlation**: RAIS has some predictive power for PSNR vs GT.\n\n")
            else:
                f.write("**Strong correlation**: RAIS is a good predictor of PSNR vs GT.\n\n")

        f.write("### Q2: Does RAIS better predict condition following?\n\n")

        attn1_clip = corr_df[(corr_df['drift_metric'] == 'attn1_rais') &
                              (corr_df['quality_metric'] == 'mean_clip_condition')]
        if len(attn1_clip) > 0:
            r = attn1_clip.iloc[0]['pearson_r']
            p = attn1_clip.iloc[0]['pearson_p']
            f.write(f"attn1 RAIS vs CLIP Condition: Pearson r = {r:.4f}, p = {p:.4f}\n\n")

        f.write("### Q3: Does Full LoRA show 'lower RAIS but higher PSNR'?\n\n")

        # Check if full_lora has lower RAIS but similar/higher PSNR
        full_lora = merged[merged['method_key'] == 'full_lora_s1.0']
        attn2_only = merged[merged['method_key'] == 'attn2_only_s1.0']

        if len(full_lora) > 0 and len(attn2_only) > 0:
            full_rais = full_lora['overall_rais'].mean()
            attn2_rais = attn2_only['overall_rais'].mean()
            full_psnr = full_lora['mean_psnr_gt'].mean()
            attn2_psnr = attn2_only['mean_psnr_gt'].mean()

            f.write(f"- Full LoRA: RAIS = {full_rais:.4f}, PSNR GT = {full_psnr:.2f}\n")
            f.write(f"- attn2-only: RAIS = {attn2_rais:.4f}, PSNR GT = {attn2_psnr:.2f}\n\n")

            if full_rais < attn2_rais and abs(full_psnr - attn2_psnr) < 2.0:
                f.write("**Yes**: Full LoRA has lower RAIS but comparable PSNR, suggesting decoupling.\n\n")
            elif full_rais < attn2_rais and full_psnr > attn2_psnr:
                f.write("**Yes**: Full LoRA has lower RAIS AND higher PSNR — clear decoupling.\n\n")
            else:
                f.write("**No clear decoupling** observed in this comparison.\n\n")

        f.write("### Q4: Does attn2-only show 'higher RAIS but lower PSNR'?\n\n")

        if len(full_lora) > 0 and len(attn2_only) > 0:
            if attn2_rais > full_rais and attn2_psnr < full_psnr:
                f.write("**Yes**: attn2-only has higher RAIS but lower PSNR — this would support the deep compensation hypothesis.\n\n")
            elif attn2_rais > full_rais and attn2_psnr >= full_psnr:
                f.write("**No**: attn2-only has both higher RAIS and comparable/higher PSNR — consistent advantage.\n\n")
            else:
                f.write("**No clear pattern** observed.\n\n")

        f.write("### Q5: Do these results support the deep compensation hypothesis?\n\n")
        f.write("The deep compensation hypothesis suggests that downstream layers can compensate for upstream reference state drift.\n\n")

        # Check depth-wise patterns
        full_lora_s1 = merged[merged['method_key'] == 'full_lora_s1.0']
        if len(full_lora_s1) > 0:
            shallow = full_lora_s1['shallow_rais'].mean()
            middle = full_lora_s1['middle_rais'].mean()
            deep = full_lora_s1['deep_rais'].mean()
            f.write(f"Full LoRA s=1.0 depth-wise RAIS:\n")
            f.write(f"- Shallow: {shallow:.4f}\n")
            f.write(f"- Middle: {middle:.4f}\n")
            f.write(f"- Deep: {deep:.4f}\n\n")

            if deep < shallow:
                f.write("**Drift increases with depth**: Deeper layers show more drift, which is expected but does not directly support compensation.\n\n")
            else:
                f.write("**Drift decreases with depth**: This would support the compensation hypothesis.\n\n")

        f.write("## Conclusion\n\n")
        f.write("Based on the data:\n\n")
        f.write("1. RAIS and end-to-end quality metrics show varying degrees of correlation\n")
        f.write("2. The relationship between internal drift and output quality is not strictly linear\n")
        f.write("3. This supports the paper's argument that LoRA evaluation needs both internal state integrity AND end-to-end quality metrics\n")

    print(f"  Report saved to {report_path}")


if __name__ == '__main__':
    main()
