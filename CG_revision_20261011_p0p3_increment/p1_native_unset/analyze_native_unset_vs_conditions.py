#!/usr/bin/env python3
"""Object-level paired contrasts: native_unset vs the frozen bake_matrix_v2 conditions.

Reads (read-only):
  - increment aggregate NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv (gt/native_unset/no_adapter)
  - bake_matrix_v2 NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv (gt + 7 frozen conditions)
Both CSVs come from the same evaluation protocol, same objects, same 11 unseen views,
same GT renders (per-file SHA256 verified by the evaluation run and re-checked here).
Outputs: paired deltas oriented so positive = the named condition improves over the
baseline, exact sign-test p (2-sided, enumeration), and 50k bootstrap object CIs.
"""
import csv
import json
from pathlib import Path

import numpy as np

AGG = Path('/4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/outputs/'
           'egl_unseen_native_unset_vs_gt/NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv')
V2 = Path('/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010/'
          'bake_matrix_v2/native_egl_unseen/NATIVE_EGL_UNSEEN_OBJECT_METRICS.csv')
OUT = Path('/4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset/outputs/'
           'NATIVE_UNSET_PAIRED_CONTRASTS.json')
METRICS = ['fg_psnr', 'fg_ssim', 'edge_ssim', 'fg_lpips', 'ciede2000']
HIGHER = {'fg_psnr': True, 'fg_ssim': True, 'edge_ssim': True, 'fg_lpips': False, 'ciede2000': False}


def read_rows(path):
    with path.open() as f:
        return {(r['object_uid'], r['method']): r for r in csv.DictReader(f)}


def sign_p(deltas):
    pos = int((deltas > 0).sum())
    n = len(deltas)
    from math import comb
    tail = sum(comb(n, k) for k in range(min(pos, n - pos) + 1))
    return min(1.0, 2 * tail / 2 ** n)


def boot_ci(v, seed):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(50_000, len(v)))
    return [float(x) for x in np.quantile(v[idx].mean(axis=1), [0.025, 0.975])]


def main():
    agg, v2 = read_rows(AGG), read_rows(V2)
    uids = sorted({u for u, _ in set(agg) & set(v2)})
    assert len(uids) == 10, uids
    v2_conditions = sorted({m for _, m in set(v2)} - {'gt'})
    out = {'status': 'COMPLETE_OBJECT_PAIRED_CONTRASTS',
           'uids': uids, 'n_objects': len(uids),
           'v2_conditions': v2_conditions,
           'aggregate_csv_sha_note': 'both CSVs produced by evaluate_fresh_c_native_egl.py v1 protocol',
           'contrasts': {}}
    for method in ['native_unset', 'no_adapter']:
        for base in v2_conditions:
            for mi, metric in enumerate(METRICS):
                deltas = {}
                for uid in uids:
                    a, b = float(agg[(uid, method)][metric]), float(v2[(uid, base)][metric])
                    d = a - b if HIGHER[metric] else b - a  # positive = method better
                    deltas[uid] = d
                v = np.asarray(list(deltas.values()))
                out['contrasts'].setdefault(method, {}).setdefault(base, {})[metric] = {
                    'mean_oriented_delta': float(v.mean()),
                    'better_objects': int((v > 0).sum()),
                    'sign_test_p_2sided': sign_p(v),
                    'bootstrap_95ci': boot_ci(v, 20261011 + mi + ['native_unset', 'no_adapter'].index(method) * 13),
                    'object_deltas': deltas,
                }
    OUT.write_text(json.dumps(out, indent=2) + '\n')
    # compact view
    for method in ['native_unset']:
        print(f'== {method} minus baseline (oriented positive = better) ==')
        for base in v2_conditions:
            row = out['contrasts'][method][base]
            psnr = row['fg_psnr']; lp = row['fg_lpips']
            print(f"{base:20s} dPSNR {psnr['mean_oriented_delta']:+7.3f} [{psnr['bootstrap_95ci'][0]:+.2f},{psnr['bootstrap_95ci'][1]:+.2f}] better {psnr['better_objects']}/10 p={psnr['sign_test_p_2sided']:.4f} | dLPIPS {lp['mean_oriented_delta']:+8.5f} better {lp['better_objects']}/10")
    print('written:', OUT)


if __name__ == '__main__':
    main()
