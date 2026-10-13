#!/usr/bin/env python3
"""Recompute the retrospective 276-ordinal sensitivity statistics from CSV.

No model, image generation, or image scoring. Requires NumPy.
Rows are ordinal-paired, NOT proof of exact actual UID coverage: one logged
load failure substituted the requested obj_0046 through the historical loader.
The reported original 276-ordinal table is preserved; optional exclusion of
obj_0046 is a technical sensitivity analysis, never a pristine confirmation.

Reproduces ORIGINAL276_RETRAIN_AUDIT.json['metrics'/'contrasts'] exactly:
NumPy default_rng(20261012), one 10000 x N integer bootstrap matrix, then
metric-major / comparator-minor order, 100 batches of 2000 Rademacher flips
per contrast, add-one Monte Carlo p, Holm family of all 24 tests.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

METRICS = [
    'full_psnr', 'full_ssim', 'full_lpips', 'fg_psnr', 'fg_ssim',
    'fg_lpips', 'edge_ssim', 'bgwhite_psnr',
]
COMPARATORS = ['fixed_low', 'fixed_high', 'no_adapter']


def analyze(csv_path, exclude=()):
    rows = list(csv.DictReader(csv_path.open()))
    rows = [r for r in rows if r['object'] not in exclude]
    conditions = sorted({r['schedule'] for r in rows})
    objects = sorted({r['object'] for r in rows})
    by = {(r['object'], r['schedule']): r for r in rows}
    if len(by) != len(rows) or not all((o, c) in by for o in objects for c in conditions):
        raise ValueError('CSV has missing or duplicate object-condition pairs')
    rng = np.random.default_rng(20261012)
    bootstrap_indices = rng.integers(0, len(objects), (10000, len(objects)))
    result = {
        'raw_metrics': str(csv_path.resolve()),
        'raw_metrics_sha256': hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        'rows': len(rows), 'objects': len(objects), 'conditions': conditions,
        'excluded_ordinals': list(exclude),
        'rng_seed': 20261012, 'bootstrap_draws': 10000,
        'signflip_draws': 200000, 'signflip_batch_size': 2000,
        'inference_scope': 'Exploratory retrospective ordinal-paired protocol sensitivity; exact actual UID gate fails due to one logged replacement. Pointwise CIs; separate exploratory 24-test Holm family.',
        'metrics': {}, 'contrasts': [],
    }
    for metric in METRICS:
        values = {c: np.array([float(by[o, c][metric]) for o in objects]) for c in conditions}
        result['metrics'][metric] = {c: float(x.mean()) for c, x in values.items()}
        for other in COMPARATORS:
            delta = values['c3'] - values[other]
            ci = np.quantile(delta[bootstrap_indices].mean(axis=1), [.025, .975])
            favorable = delta < 0 if 'lpips' in metric else delta > 0
            exceed = 0
            for _ in range(100):
                signs = rng.integers(0, 2, (2000, len(delta)), dtype=np.int8) * 2 - 1
                exceed += int(np.count_nonzero(abs((signs * delta).mean(axis=1)) >= abs(delta.mean()) - 1e-15))
            result['contrasts'].append({
                'a': 'c3', 'b': other, 'metric': metric,
                'mean_difference': float(delta.mean()),
                'median_difference': float(np.median(delta)),
                'ci95_pointwise_object_bootstrap': ci.tolist(),
                'n': len(delta), 'favorable_objects': int(favorable.sum()),
                'p_raw_signflip_MC200000': (exceed + 1) / 200001,
            })
    pvalues = np.array([x['p_raw_signflip_MC200000'] for x in result['contrasts']])
    order = np.argsort(pvalues)
    adjusted = np.minimum(np.maximum.accumulate(pvalues[order] * (len(pvalues) - np.arange(len(pvalues)))), 1)
    for index, value in zip(order, adjusted):
        result['contrasts'][int(index)]['p_holm_exploratory_24'] = float(value)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=Path(__file__).resolve().parent / 'per_object_metrics.csv')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--exclude-known-replacement', action='store_true')
    parser.add_argument('--verify-against', type=Path)
    args = parser.parse_args()
    result = analyze(args.csv, ['obj_0046'] if args.exclude_known_replacement else [])
    if args.verify_against:
        expected = json.loads(args.verify_against.read_text())
        for key in ['metrics', 'contrasts']:
            if result[key] != expected[key]:
                raise ValueError(f'{key} differs from frozen audit')
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"Verified {result['objects']} ordinal pairs and wrote {args.output}")
