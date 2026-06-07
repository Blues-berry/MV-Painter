"""
Compute Mean ± Std for all metrics and generate a comprehensive report.
"""
import csv
import numpy as np
import json

def compute_stats(values):
    return np.mean(values), np.std(values)

# Read expanded dataset results
csv_path = '/4T/CXY/MV-Painter/mvpoutput/expanded_dataset_eval/expanded_eval_results.csv'

clip_a, clip_b, clip_c = [], [], []
psnr_a, psnr_b, psnr_c = [], [], []

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clip_a.append(float(row['clip_a']))
        clip_b.append(float(row['clip_b']))
        clip_c.append(float(row['clip_c']))
        psnr_a.append(float(row['psnr_a']))
        psnr_b.append(float(row['psnr_b']))
        psnr_c.append(float(row['psnr_c']))

n = len(clip_a)
print(f"Number of objects: {n}")
print()

# Compute statistics
metrics = {
    'CLIP Sim (Original)': clip_a,
    'CLIP Sim (Full LoRA)': clip_b,
    'CLIP Sim (RP-LoRA)': clip_c,
    'PSNR vs GT (Original)': psnr_a,
    'PSNR vs GT (Full LoRA)': psnr_b,
    'PSNR vs GT (RP-LoRA)': psnr_c,
}

print("=== Comprehensive Statistics (Mean ± Std) ===\n")
print(f"{'Metric':<30} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
print("-" * 75)

for name, values in metrics.items():
    mean, std = compute_stats(values)
    print(f"{name:<30} {mean:>10.4f} {std:>10.4f} {min(values):>10.4f} {max(values):>10.4f}")

# Compute deltas
print("\n=== Pairwise Comparisons ===\n")

# CLIP: RP-LoRA vs Full LoRA
clip_diff = [c - b for c, b in zip(clip_c, clip_b)]
clip_diff_mean, clip_diff_std = compute_stats(clip_diff)
print(f"CLIP Sim: RP-LoRA - Full LoRA = {clip_diff_mean:+.4f} ± {clip_diff_std:.4f}")

# PSNR: RP-LoRA vs Full LoRA
psnr_diff = [c - b for c, b in zip(psnr_c, psnr_b)]
psnr_diff_mean, psnr_diff_std = compute_stats(psnr_diff)
print(f"PSNR vs GT: RP-LoRA - Full LoRA = {psnr_diff_mean:+.2f} ± {psnr_diff_std:.2f} dB")

# PSNR: Original vs Full LoRA
psnr_orig_vs_full = [a - b for a, b in zip(psnr_a, psnr_b)]
psnr_orig_vs_full_mean, psnr_orig_vs_full_std = compute_stats(psnr_orig_vs_full)
print(f"PSNR vs GT: Original - Full LoRA = {psnr_orig_vs_full_mean:+.2f} ± {psnr_orig_vs_full_std:.2f} dB")

# PSNR: Original vs RP-LoRA
psnr_orig_vs_rp = [a - c for a, c in zip(psnr_a, psnr_c)]
psnr_orig_vs_rp_mean, psnr_orig_vs_rp_std = compute_stats(psnr_orig_vs_rp)
print(f"PSNR vs GT: Original - RP-LoRA = {psnr_orig_vs_rp_mean:+.2f} ± {psnr_orig_vs_rp_std:.2f} dB")

# Statistical significance (paired t-test)
from scipy import stats

print("\n=== Statistical Significance (Paired t-test) ===\n")

# CLIP: RP-LoRA vs Full LoRA
t_stat, p_value = stats.ttest_rel(clip_c, clip_b)
print(f"CLIP Sim: RP-LoRA vs Full LoRA")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")

# PSNR: RP-LoRA vs Full LoRA
t_stat, p_value = stats.ttest_rel(psnr_c, psnr_b)
print(f"\nPSNR vs GT: RP-LoRA vs Full LoRA")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")

# PSNR: Original vs Full LoRA
t_stat, p_value = stats.ttest_rel(psnr_a, psnr_b)
print(f"\nPSNR vs GT: Original vs Full LoRA")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")

# Generate LaTeX table
print("\n=== LaTeX Table ===\n")
print("\\begin{table}[h]")
print("\\centering")
print("\\caption{Three-way comparison with Mean $\\pm$ Std (N=" + str(n) + ")}")
print("\\begin{tabular}{lcccccc}")
print("\\toprule")
print("Method & PSNR vs Orig $\\uparrow$ & PSNR vs GT $\\uparrow$ & CLIP Sim $\\uparrow$ \\\\")
print("\\midrule")

mean_a_psnr, std_a_psnr = compute_stats(psnr_a)
mean_b_psnr, std_b_psnr = compute_stats(psnr_b)
mean_c_psnr, std_c_psnr = compute_stats(psnr_c)

mean_a_clip, std_a_clip = compute_stats(clip_a)
mean_b_clip, std_b_clip = compute_stats(clip_b)
mean_c_clip, std_c_clip = compute_stats(clip_c)

print("Original & $\\infty$ & " + f"{mean_a_psnr:.2f} $\\pm$ {std_a_psnr:.2f}" + " & " + f"{mean_a_clip:.4f} $\\pm$ {std_a_clip:.4f}" + " \\\\")
print("Full LoRA & 14.99 & " + f"{mean_b_psnr:.2f} $\\pm$ {std_b_psnr:.2f}" + " & " + f"{mean_b_clip:.4f} $\\pm$ {std_b_clip:.4f}" + " \\\\")
print("RP-LoRA & \\textbf{48.29} & " + "\\textbf{" + f"{mean_c_psnr:.2f} $\\pm$ {std_c_psnr:.2f}" + "}" + " & " + "\\textbf{" + f"{mean_c_clip:.4f} $\\pm$ {std_c_clip:.4f}" + "}" + " \\\\")
print("\\bottomrule")
print("\\end{tabular}")
print("\\end{table}")

# Save results
results = {
    'n_objects': n,
    'clip_original': {'mean': float(mean_a_clip), 'std': float(std_a_clip)},
    'clip_full_lora': {'mean': float(mean_b_clip), 'std': float(std_b_clip)},
    'clip_rp_lora': {'mean': float(mean_c_clip), 'std': float(std_c_clip)},
    'psnr_gt_original': {'mean': float(mean_a_psnr), 'std': float(std_a_psnr)},
    'psnr_gt_full_lora': {'mean': float(mean_b_psnr), 'std': float(std_b_psnr)},
    'psnr_gt_rp_lora': {'mean': float(mean_c_psnr), 'std': float(std_c_psnr)},
    'psnr_gt_rp_vs_full': {'mean': float(psnr_diff_mean), 'std': float(psnr_diff_std)},
    'clip_rp_vs_full': {'mean': float(clip_diff_mean), 'std': float(clip_diff_std)},
}

with open('/4T/CXY/MV-Painter/mvpoutput/expanded_dataset_eval/statistics_report.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to /4T/CXY/MV-Painter/mvpoutput/expanded_dataset_eval/statistics_report.json")
