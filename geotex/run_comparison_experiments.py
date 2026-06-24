#!/usr/bin/env python3
"""Run comparison experiments: additional scaling strategies for TCAS paper.

Strategies to compare:
1. Linear decay: s linearly decreases from s_max to s_min across denoising
2. Cosine decay: s follows cosine curve from s_max to s_min
3. Inverted C3: early=2.50, mid=1.25, late=2.50 (control experiment)
4. C4 on 300 objects (late-only high scale)
5. Smooth C3: continuous version using sigmoid transitions
"""

import os
import sys
import subprocess
import json

BASE = '/4T/CXY/MV-Painter'
OUTPUT_BASE = f'{BASE}/mvpoutput/geotex_refattn_v1'


def run_experiment(name, schedule, num_objects=50, output_suffix=None):
    """Run a single experiment."""
    out_dir = f'{OUTPUT_BASE}/comparison_{output_suffix or name}_{num_objects}obj'
    if os.path.exists(f'{out_dir}/per_object_metrics.csv'):
        print(f'SKIP {name}: already exists at {out_dir}')
        return out_dir

    cmd = [
        'python', f'{BASE}/geotex/eval_exploration.py',
        '--config', f'{BASE}/mvpoutput/geotex/eval_config_snapshot.yaml',
        '--checkpoint', f'{BASE}/mvpoutput/geotex_checkpoints/geotex_step_0002000.pt',
        '--timestep_schedule', json.dumps(schedule),
        '--num_objects', str(num_objects),
        '--output_dir', out_dir,
        '--seed', '42',
    ]

    print(f'Running: {name} ({num_objects} objects)')
    print(f'  Schedule: {schedule}')
    print(f'  Output: {out_dir}')

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        print(f'  ERROR: {result.stderr[-500:]}')
    else:
        print(f'  DONE')
    return out_dir


if __name__ == '__main__':
    experiments = [
        # Inverted C3 (anti-thesis: high early+late, low mid)
        ('inverted_C3', {'early': 2.50, 'mid': 1.25, 'late': 2.50}, 50),

        # High-early (test if early phase matters)
        ('high_early', {'early': 2.50, 'mid': 2.50, 'late': 1.25}, 50),

        # Uniform mid (test if phase distinction matters vs just lower overall)
        ('uniform_1p75', {'early': 1.75, 'mid': 1.75, 'late': 1.75}, 50),

        # C4 on 50 objects (already have on 24, need 50 for fair comparison)
        ('C4_50obj', {'early': 1.25, 'mid': 1.25, 'late': 2.50}, 50),

        # Gentle C3 (lower mid-scale)
        ('gentle_C3', {'early': 1.25, 'mid': 2.00, 'late': 1.25}, 50),

        # Aggressive C3 (higher mid-scale)
        ('aggressive_C3', {'early': 1.00, 'mid': 3.00, 'late': 1.00}, 50),
    ]

    print(f'Running {len(experiments)} comparison experiments')
    print('=' * 60)

    results = []
    for name, schedule, n_obj in experiments:
        out_dir = run_experiment(name, schedule, n_obj)
        results.append((name, out_dir))

    print()
    print('=' * 60)
    print('All experiments complete. Outputs:')
    for name, out_dir in results:
        exists = os.path.exists(f'{out_dir}/per_object_metrics.csv')
        print(f'  {name}: {"✓" if exists else "✗"} {out_dir}')
