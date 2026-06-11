"""Quick progress check for running eval.

Usage: python geotex/check_eval_progress.py --eval_dir mvpoutput/geotex_refattn_v1/eval_300obj_clean
"""
import os
import argparse
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval_dir', required=True)
    parser.add_argument('--total', type=int, default=300)
    args = parser.parse_args()

    vis_dir = os.path.join(args.eval_dir, 'visualizations')
    if not os.path.exists(vis_dir):
        print("No visualizations directory found")
        return

    gt_files = glob.glob(os.path.join(vis_dir, 'obj_*_gt.png'))
    done = len(gt_files)
    pct = 100 * done / args.total

    print(f"Progress: {done}/{args.total} ({pct:.1f}%)")

    # Check for output files
    for fname in ['per_object_metrics.csv', 'summary_metrics.json', 'region_metrics.csv']:
        path = os.path.join(args.eval_dir, fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  {fname}: {size} bytes")

    # Check GPU
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu',
                                '--format=csv,noheader'], capture_output=True, text=True)
        for i, line in enumerate(result.stdout.strip().split('\n')):
            print(f"  GPU {i}: {line}")
    except:
        pass

if __name__ == '__main__':
    main()
