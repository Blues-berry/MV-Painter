"""Compute paired CAI stage utilities from a stage-ablation CSV.

The utility is a finite difference against fixed_low.  It is intentionally
metric-agnostic: PSNR is the primary objective, while FG-SSIM and LapVar are
reported as constraints/diagnostics rather than collapsed into one score.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def ci95(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(len(values)))
    # t critical values for the small probe sizes used here; normal fallback.
    tcrit = {5: 2.571, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306,
             10: 2.262, 11: 2.228, 12: 2.201, 23: 2.069, 24: 2.069}.get(
                 len(values), 1.96)
    return mean, [mean - tcrit * se, mean + tcrit * se]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()

    rows = list(csv.DictReader(args.csv_path.open()))
    by_object = {}
    for row in rows:
        by_object.setdefault(row['object'], {})[row['schedule']] = row
    required = {'fixed_low', 'early_high', 'mid_high', 'late_high'}
    if not by_object or any(required - set(v) for v in by_object.values()):
        raise SystemExit('CSV must contain all four schedules for every object')

    output = {'source_csv': str(args.csv_path), 'num_objects': len(by_object),
              'baseline': 'fixed_low', 'utilities': {}}
    for stage in ('early', 'middle', 'late'):
        schedule = f'{stage}_high' if stage != 'middle' else 'mid_high'
        result = {}
        for metric in ('psnr', 'fg_ssim', 'fg_lap_var', 'fg_lap_corr', 'fg_mae'):
            delta = np.array([float(v[schedule][metric]) - float(v['fixed_low'][metric])
                              for v in by_object.values()])
            mean, ci = ci95(delta)
            result[metric] = {'mean_delta': mean, 'ci95': ci}
        result['lap_ratio_vs_low'] = float(np.mean([
            float(v[schedule]['fg_lap_var']) / float(v['fixed_low']['fg_lap_var'])
            for v in by_object.values()]))
        output['utilities'][stage] = result

    output_path = args.output or args.csv_path.with_name('stage_utility_analysis.json')
    output_path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
    print(f'Saved: {output_path}')


if __name__ == '__main__':
    main()
