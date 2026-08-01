"""Summarize the 4-schedule 300-object evaluation.

Reads summary.json from each schedule output dir and prints a comparison table
plus object-level win rates vs C3 on the shared per-object CSVs.

Usage:
    python scripts/analyze_300obj_schedules.py \
        --dirs mvpoutput/geotex_v2/eval_300_c3:mvpoutput/geotex_v2/eval_300_no_adapter:mvpoutput/geotex_v2/eval_300_fixed_low:mvpoutput/geotex_v2/eval_300_fixed_high
"""
import csv
import json
import argparse
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dirs', type=str, required=True,
                        help='Colon-separated list of output dirs')
    args = parser.parse_args()

    dirs = args.dirs.split(':')
    label = []
    data = []
    for d in dirs:
        with open(f'{d}/summary.json') as f:
            s = json.load(f)
        label.append(s.get('schedule', d.split('/')[-1]))
        data.append(s['metrics'])
    names = [l for l in label]

    # Build the comparison table
    keys = ['full_psnr', 'full_ssim', 'fg_psnr', 'fg_ssim', 'edge_ssim',
            'fg_lpips', 'rgb_std_ratio', 'grad_ratio']
    print(f"{'Metric':<16}", *[f'{n:>12}' for n in names])
    print('-' * (16 + 12 * len(names)))
    for k in keys:
        row = []
        for s in data:
            v = s.get(k, {}).get('mean')
            row.append(f'{v:12.4f}' if v is not None else f'{"--":>12}')
        print(f'{k:<16}', *row)

    # Object-level win rates vs c3
    c3_idx = names.index('c3') if 'c3' in names else 0
    print('\n=== Object-level win rate vs c3 (FG-SSIM / PSNR) ===')
    for i, d in enumerate(dirs):
        if i == c3_idx:
            continue
        per = list(csv.DictReader(open(f'{d}/per_object_metrics.csv')))
        c3 = list(csv.DictReader(open(f'{dirs[c3_idx]}/per_object_metrics.csv')))
        objs = sorted(set(r['object'] for r in c3))
        fg_wins = sum(1 for o in objs
                      if float(dict((r['object'], r) for r in per)[o]['fg_ssim'])
                      < float(dict((r['object'], r) for r in c3)[o]['fg_ssim']))
        psnr_wins = sum(1 for o in objs
                        if float(dict((r['object'], r) for r in per)[o]['full_psnr'])
                        < float(dict((r['object'], r) for r in c3)[o]['full_psnr']))
        print(f"  vs {names[i]:<12} FG-SSIM: {fg_wins}/{len(objs)}  PSNR: {psnr_wins}/{len(objs)}")


if __name__ == '__main__':
    main()
