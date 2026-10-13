"""Compute object-level win rates for the schedule-comparison supplement.

Reads the per-object CSV produced by eval_schedule_comparison.py and reports
C3 (TCAS) vs each alternative on FG-SSIM and PSNR, matching the format used
in revision_supplement_0707.md Table X.

Usage:
    python scripts/analyze_schedule_winrates.py \
        mvpoutput/revision_schedule_comparison/per_object_results.csv
"""
import sys
import csv
from collections import defaultdict


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else \
        'mvpoutput/revision_schedule_comparison/per_object_results.csv'
    rows = list(csv.DictReader(open(csv_path)))
    per_sched = defaultdict(dict)
    for r in rows:
        per_sched[r['schedule']][r['object']] = {
            'fg_ssim': float(r['fg_ssim']),
            'psnr': float(r['psnr']),
        }

    if 'C3_TCAS' not in per_sched:
        print(f"C3_TCAS not found. Schedules: {sorted(per_sched.keys())}")
        return

    c3 = per_sched['C3_TCAS']
    objs = sorted(c3.keys())
    print(f"Objects: {len(objs)}")
    print()
    print(f"{'C3 vs':<18} {'FG-SSIM wins':>14} {'PSNR wins':>14}")
    print("-" * 48)
    for name in sorted(per_sched.keys()):
        if name == 'C3_TCAS':
            continue
        alt = per_sched[name]
        fg_wins = sum(1 for o in objs if c3[o]['fg_ssim'] > alt[o]['fg_ssim'])
        psnr_wins = sum(1 for o in objs if c3[o]['psnr'] > alt[o]['psnr'])
        print(f"{name:<18} {fg_wins:>5}/{len(objs):<3}({100*fg_wins/len(objs):.0f}%) "
              f"{psnr_wins:>5}/{len(objs):<3}({100*psnr_wins/len(objs):.0f}%)")


if __name__ == '__main__':
    main()
