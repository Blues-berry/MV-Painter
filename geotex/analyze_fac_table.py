"""Build the real tab:fac rows + win-rate + paired significance for FAC v3.

Merges per-object metrics from the canonical TCAS baseline
(mvpoutput/geotex_v2/eval_300_c3) with the three FAC v3 evals
(mvpoutput/fac_v3/{ltag,full,ltag_gsg}/eval_300). Protocols are identical
(50 Euler steps, seed 42, shared init latents, normalize_bg=True), so
per-object pairing by obj_idx is valid.

Outputs:
    mvpoutput/fac_v3/tab_fac_summary.json  (rows, deltas, win-rates, p-values)
    mvpoutput/fac_v3/tab_fac_rows.tex      (LaTeX table body)
"""
import argparse
import csv
import json
import os
import sys

import numpy as np


def load_per_object(path):
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            idx = int(r['obj_idx'])
            rows[idx] = {
                'full_psnr': float(r['full_psnr']),
                'full_ssim': float(r['full_ssim']),
                'fg_psnr': float(r['fg_psnr']),
                'fg_ssim': float(r['fg_ssim']),
            }
    return rows


def wilcoxon_p(a, b):
    """Paired Wilcoxon signed-rank test (scipy if available, else normal-approx)."""
    try:
        from scipy.stats import wilcoxon
        return wilcoxon(a, b).pvalue
    except ImportError:
        d = np.array(a) - np.array(b)
        d = d[d != 0]
        n = len(d)
        if n == 0:
            return 1.0
        ranks = np.argsort(np.abs(d))
        r = np.empty(n)
        r[ranks] = np.arange(1, n + 1)
        # tie correction (naive)
        s = np.sum(np.where(d > 0, r, 0.0))
        mu = n * (n + 1) / 4
        var = n * (n + 1) * (2 * n + 1) / 24
        z = (s - mu) / np.sqrt(var)
        from scipy.special import erfc
        return erfc(abs(z) / np.sqrt(2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', default='mvpoutput/geotex_v2/eval_300_c3/per_object_metrics.csv')
    p.add_argument('--evals', default='mvpoutput/fac_v3')
    p.add_argument('--out', default='mvpoutput/fac_v3/tab_fac_summary.json')
    args = p.parse_args()

    base = load_per_object(args.baseline)
    variants = {
        'ltag': ('LTAG only', 'ltag'),
        'ltag_gsg': ('LTAG + GSG', 'ltag_gsg'),
        'ltag_gsg_fsc': ('Full FAC', 'full'),
    }
    metric_names = ['full_psnr', 'full_ssim', 'fg_psnr', 'fg_ssim']
    col_labels = {'full_psnr': 'PSNR', 'full_ssim': 'SSIM', 'fg_psnr': 'FG-PSNR', 'fg_ssim': 'FG-SSIM'}

    results = {}
    # baseline row
    b = base
    results['TCAS'] = {
        'label': 'TCAS (baseline)',
        'mean': {m: float(np.mean([b[i][m] for i in b])) for m in metric_names},
    }

    for vkey, (label, evdir) in variants.items():
        csv_path = os.path.join(args.evals, evdir, 'eval_300', 'per_object_metrics.csv')
        if not os.path.exists(csv_path):
            print(f"MISSING {csv_path}")
            continue
        rows = load_per_object(csv_path)
        common = sorted(set(b) & set(rows))
        means = {m: float(np.mean([rows[i][m] for i in rows])) for m in metric_names}
        results[vkey] = {
            'label': label,
            'mean': means,
            'n': len(rows),
        }
        # paired win-rate + p vs TCAS baseline (on common objects)
        winrate = {}
        pvals = {}
        for m in metric_names:
            a = np.array([rows[i][m] for i in common])
            bb = np.array([b[i][m] for i in common])
            winrate[m] = float(np.mean(a > bb))
            pvals[m] = float(wilcoxon_p(a, bb))
        results[vkey]['winrate_vs_tcas'] = winrate
        results[vkey]['p_vs_tcas'] = pvals
        results[vkey]['delta_vs_tcas'] = {m: means[m] - results['TCAS']['mean'][m] for m in metric_names}

    # LaTeX rows
    lines = []
    for key in ['TCAS', 'ltag', 'ltag_gsg', 'ltag_gsg_fsc']:
        if key not in results:
            continue
        r = results[key]
        cells = [r['mean'][m] for m in metric_names]
        row = f"{r['label']} & {cells[0]:.2f} & {cells[1]:.4f} & {cells[2]:.2f} & {cells[3]:.4f} \\\\"
        lines.append(row)
    # bold winners
    for m in metric_names:
        vals = [results[k]['mean'][m] for k in ['TCAS', 'ltag', 'ltag_gsg', 'ltag_gsg_fsc'] if k in results]
        print(f"  {m}: max = {max(vals):.4f} among {vals}")

    with open(args.out, 'w') as f:
        json.dump(results, f, indent=2)
    with open(os.path.join(args.evals, 'tab_fac_rows.tex'), 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"\n=== tab:fac (REAL v3 data) ===")
    print(f"{'variant':<16}{'PSNR':>8}{'SSIM':>9}{'FG-PSNR':>10}{'FG-SSIM':>10}")
    for key in ['TCAS', 'ltag', 'ltag_gsg', 'ltag_gsg_fsc']:
        if key not in results:
            continue
        r = results[key]
        print(f"{r['label']:<16}{r['mean']['full_psnr']:>8.2f}{r['mean']['full_ssim']:>9.4f}"
              f"{r['mean']['fg_psnr']:>10.2f}{r['mean']['fg_ssim']:>10.4f}")
    if 'ltag_gsg_fsc' in results:
        rr = results['ltag_gsg_fsc']
        print(f"\nFull FAC vs TCAS:")
        for m in metric_names:
            print(f"  {col_labels[m]:>8}: delta={rr['delta_vs_tcas'][m]:+.4f}  "
                  f"win-rate={rr['winrate_vs_tcas'][m]*100:.1f}%  p={rr['p_vs_tcas'][m]:.2e}")
    if 'ltag' in results:
        rr = results['ltag']
        print(f"\nLTAG vs TCAS:")
        for m in metric_names:
            print(f"  {col_labels[m]:>8}: delta={rr['delta_vs_tcas'][m]:+.4f}  "
                  f"win-rate={rr['winrate_vs_tcas'][m]*100:.1f}%  p={rr['p_vs_tcas'][m]:.2e}")
    print(f"\nSaved summary → {args.out}")


if __name__ == '__main__':
    main()
