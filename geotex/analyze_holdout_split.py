"""Recompute probe/disjoint-holdout statistics from existing per-object CSVs.

The probe protocol evaluates obj_0000--obj_0023.  This tool explicitly excludes
those objects from the 300-object pool so transfer claims can be reported on a
disjoint 276-object holdout without rerunning inference.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import t


def read_rows(path):
    return {row['object']: row for row in csv.DictReader(path.open())}


def paired_summary(left, right, metric, objects):
    delta = np.asarray([
        float(left[o][metric]) - float(right[o][metric])
        for o in objects
        if left[o].get(metric, '') != '' and right[o].get(metric, '') != ''
    ])
    mean = float(delta.mean())
    ci = t.interval(0.95, len(delta) - 1, loc=mean,
                    scale=float(delta.std(ddof=1) / np.sqrt(len(delta))))
    return {'n': int(len(delta)), 'mean_delta': mean,
            'ci95': [float(ci[0]), float(ci[1])],
            'wins': int((delta > 0).sum())}


def summarize(metrics, objects):
    out = {}
    for name, rows in metrics.items():
        out[name] = {
            metric: float(np.mean([float(rows[o][metric]) for o in objects
                                   if rows[o].get(metric, '') != '']))
            for metric in ('full_psnr', 'fg_ssim', 'edge_ssim', 'fg_lpips')
        }
    comparisons = {}
    for other in ('high', 'low', 'no_adapter'):
        if other not in metrics:
            continue
        comparisons[f'C3_vs_{other}'] = {
            metric: paired_summary(metrics['C3'], metrics[other], metric, objects)
            for metric in ('full_psnr', 'fg_ssim', 'edge_ssim', 'fg_lpips')
        }
    return {'num_objects': len(objects), 'means': out,
            'paired_comparisons': comparisons}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('mvpoutput/geotex_v2'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    file_map = {
        'C3': 'eval300v2_c3/per_object_metrics.csv',
        'low': 'eval300v2_fixed_low/per_object_metrics.csv',
        'high': 'eval300v2_fixed_high/per_object_metrics.csv',
        'no_adapter': 'eval_300_no_adapter/per_object_metrics.csv',
    }
    metrics = {name: read_rows(args.root / rel) for name, rel in file_map.items()}
    common = set.intersection(*(set(rows) for rows in metrics.values()))
    probe = sorted((o for o in common if int(metrics['C3'][o]['obj_idx']) < 24),
                   key=lambda o: int(metrics['C3'][o]['obj_idx']))
    holdout = sorted((o for o in common if int(metrics['C3'][o]['obj_idx']) >= 24),
                     key=lambda o: int(metrics['C3'][o]['obj_idx']))

    # The A2 CSV has all three schedules and uses the same object IDs.
    a2_path = Path('mvpoutput/revision_top2_300/per_object_results.csv')
    a2_rows = list(csv.DictReader(a2_path.open()))
    a2 = {}
    for row in a2_rows:
        if int(row['object'].split('_')[1]) >= 24:
            a2.setdefault(row['object'], {})[row['schedule']] = row
    a2_out = {'num_objects': len(a2), 'means': {}, 'paired_comparisons': {}}
    for schedule in ('C3_TCAS', 'trapezoid', 'gaussian_peak'):
        a2_out['means'][schedule] = {
            metric: float(np.mean([float(row[schedule][metric]) for row in a2.values()]))
            for metric in ('psnr', 'fg_ssim')
        }
    for schedule in ('trapezoid', 'gaussian_peak'):
        values = {o: {'C3': a2[o]['C3_TCAS'], 'other': a2[o][schedule]}
                  for o in a2}
        d = np.asarray([float(v['C3']['psnr']) - float(v['other']['psnr'])
                        for v in values.values()])
        ci = t.interval(0.95, len(d) - 1, loc=float(d.mean()),
                        scale=float(d.std(ddof=1) / np.sqrt(len(d))))
        a2_out['paired_comparisons'][f'C3_vs_{schedule}'] = {
            'n': int(len(d)), 'mean_delta': float(d.mean()),
            'ci95': [float(ci[0]), float(ci[1])],
            'wins': int((d > 0).sum())
        }

    result = {
        'source': {'main_csv_root': str(args.root), 'a2_csv': str(a2_path)},
        'split': {'probe_rule': 'obj_idx < 24', 'holdout_rule': 'obj_idx >= 24',
                  'probe_objects': probe, 'holdout_objects': holdout},
        'probe': summarize(metrics, probe),
        'disjoint_holdout': summarize(metrics, holdout),
        'a2_disjoint_holdout': a2_out,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    print(f'Saved: {args.output}')


if __name__ == '__main__':
    main()
