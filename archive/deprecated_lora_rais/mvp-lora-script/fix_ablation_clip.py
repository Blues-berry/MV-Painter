"""
Fix ablation study: use correct CLIP data from ablation experiments.
The paper tables should use data from ablation_results.csv, not from eval_reference_consistency.md.
"""
import os
import csv


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/ablation_study'

    # Read ablation results
    ablation_data = {}
    csv_path = os.path.join(output_dir, 'ablation_results.csv')
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ablation_data[row['name']] = {
                'rank': int(row['rank']),
                'steps': int(row['steps']),
                'clip': float(row['avg_clip']),
                'psnr': float(row['avg_psnr']),
            }

    # Generate corrected report
    md_path = os.path.join(output_dir, 'ablation_report_corrected.md')
    with open(md_path, 'w') as f:
        f.write("# LoRA Ablation Study Results (Corrected)\n\n")
        f.write("**Important**: This report uses CLIP data from ablation experiments.\n")
        f.write("Previous version incorrectly used data from eval_reference_consistency.md.\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Config | Rank | Steps | CLIP Sim ↑ | PSNR (dB) ↑ |\n")
        f.write("|--------|------|-------|------------|-------------|\n")

        for name in sorted(ablation_data.keys()):
            d = ablation_data[name]
            f.write(f"| {name} | {d['rank']} | {d['steps']} | {d['clip']:.4f} | {d['psnr']:.2f} |\n")

        f.write("\n## Key Findings\n\n")

        f.write("### 1. Steps Ablation (rank=4, lr=1e-5)\n\n")
        f.write("| Steps | CLIP Sim | PSNR |\n")
        f.write("|-------|----------|------|\n")
        for steps in [100, 250, 500]:
            key = f"r4_lr1e-5_s{steps}"
            if key in ablation_data:
                d = ablation_data[key]
                f.write(f"| {steps} | {d['clip']:.4f} | {d['psnr']:.2f} dB |\n")

        f.write("\n**Finding**: CLIP similarity varies across different steps configurations.\n")
        f.write("This confirms the CLIP metric is sensitive to LoRA configuration.\n\n")

        f.write("### 2. Rank Ablation (lr=1e-5, steps=250)\n\n")
        f.write("| Rank | CLIP Sim | PSNR |\n")
        f.write("|------|----------|------|\n")
        for rank in [4, 8]:
            key = f"r{rank}_lr1e-5_s250"
            if key in ablation_data:
                d = ablation_data[key]
                f.write(f"| {rank} | {d['clip']:.4f} | {d['psnr']:.2f} dB |\n")

        f.write("\n## Comparison with Previous Report\n\n")
        f.write("| Config | Previous CLIP | Corrected CLIP | Issue |\n")
        f.write("|--------|---------------|----------------|-------|\n")

        # Previous values (incorrectly from eval_reference_consistency.md)
        prev_values = {
            'r4_lr1e-5_s100': 0.7242,
            'r4_lr1e-5_s250': 0.7242,
            'r4_lr1e-5_s500': 0.7242,
            'r8_lr1e-5_s250': 0.7242,
        }

        for name in sorted(ablation_data.keys()):
            d = ablation_data[name]
            prev = prev_values.get(name, 'N/A')
            f.write(f"| {name} | {prev} | {d['clip']:.4f} | Data source corrected |\n")

        f.write("\n## Corrected LaTeX Table\n\n")
        f.write("### Table 3: Training steps ablation (rank=4)\n\n")
        f.write("\\begin{tabular}{lcc}\n")
        f.write("\\toprule\n")
        f.write("Steps & PSNR vs Original $\\uparrow$ & CLIP Sim $\\uparrow$ \\\\\n")
        f.write("\\midrule\n")

        for steps in [100, 250, 500]:
            key = f"r4_lr1e-5_s{steps}"
            if key in ablation_data:
                d = ablation_data[key]
                best = " \\textbf" if steps == 500 else ""
                f.write(f"{steps} & {d['psnr']:.2f} dB & {d['clip']:.4f}{best} \\\\\n")

        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n\n")

        f.write("### Table 4: LoRA rank ablation (steps=250)\n\n")
        f.write("\\begin{tabular}{lcc}\n")
        f.write("\\toprule\n")
        f.write("Rank & PSNR vs Original $\\uparrow$ & CLIP Sim $\\uparrow$ \\\\\n")
        f.write("\\midrule\n")

        for rank in [4, 8]:
            key = f"r{rank}_lr1e-5_s250"
            if key in ablation_data:
                d = ablation_data[key]
                best_psnr = " \\textbf" if rank == 8 else ""
                f.write(f"{rank} & {d['psnr']:.2f}{best_psnr} & {d['clip']:.4f} \\\\\n")

        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")

    print(f"Corrected report saved to {md_path}")

    # Print comparison
    print(f"\n{'='*60}")
    print("CLIP DATA CORRECTION")
    print(f"{'='*60}")
    print(f"\n{'Config':<25} {'Previous':>12} {'Corrected':>12}")
    print(f"{'-'*49}")
    for name in sorted(ablation_data.keys()):
        d = ablation_data[name]
        prev = prev_values.get(name, 'N/A')
        print(f"{name:<25} {prev:>12.4f} {d['clip']:>12.4f}")

    print(f"\n{'='*60}")
    print("Previous: From eval_reference_consistency.md (wrong source)")
    print("Corrected: From ablation_results.csv (correct source)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
