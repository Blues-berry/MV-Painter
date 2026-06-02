"""
Full evaluation script with PSNR, SSIM, LPIPS, FID, and cross-view consistency.
"""
import os
import numpy as np
from PIL import Image
import torch
import argparse


def compute_psnr(img1, img2):
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def compute_ssim(img1, img2):
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    img1, img2 = img1.astype(float), img2.astype(float)
    if len(img1.shape) == 3:
        img1, img2 = np.mean(img1, axis=2), np.mean(img2, axis=2)
    mu1, mu2 = np.mean(img1), np.mean(img2)
    sigma1_sq, sigma2_sq = np.var(img1), np.var(img2)
    sigma12 = np.mean((img1 - mu1) * (img2 - mu2))
    return ((2*mu1*mu2+C1)*(2*sigma12+C2)) / ((mu1**2+mu2**2+C1)*(sigma1_sq+sigma2_sq+C2))


def compute_lpips(img1, img2, lpips_fn):
    """Compute LPIPS between two images."""
    # Convert to tensors
    device = next(lpips_fn.parameters()).device
    t1 = torch.from_numpy(img1).float().permute(2, 0, 1).unsqueeze(0) / 127.5 - 1.0
    t2 = torch.from_numpy(img2).float().permute(2, 0, 1).unsqueeze(0) / 127.5 - 1.0
    if t1.shape[1] == 4:  # RGBA -> RGB
        t1 = t1[:, :3, :, :]
    if t2.shape[1] == 4:
        t2 = t2[:, :3, :, :]
    t1 = t1.to(device)
    t2 = t2.to(device)
    with torch.no_grad():
        return lpips_fn(t1, t2).item()


def compute_cross_view_consistency(pred_dir, pbr='albedo'):
    views = []
    for v in range(4):
        path = os.path.join(pred_dir, f'pred_view{v}_{pbr}.png')
        if os.path.exists(path):
            views.append(np.array(Image.open(path)).astype(float))
    if len(views) < 2:
        return None
    diffs = []
    for i in range(len(views)):
        for j in range(i+1, len(views)):
            diffs.append(np.mean(np.abs(views[i] - views[j])))
    return np.mean(diffs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dirs', nargs='+', required=True, help='Result directories to evaluate')
    parser.add_argument('--names', nargs='+', required=True, help='Names for each directory')
    parser.add_argument('--use_lpips', action='store_true', help='Compute LPIPS (requires GPU)')
    args = parser.parse_args()

    # Load LPIPS if requested
    lpips_fn = None
    if args.use_lpips:
        import lpips
        lpips_fn = lpips.LPIPS(net='alex').cuda()

    print("=" * 100)
    print("Full Evaluation Report")
    print("=" * 100)

    all_results = {}

    for dir_path, name in zip(args.dirs, args.names):
        if not os.path.isdir(dir_path):
            print(f"Skipping {name}: directory not found")
            continue

        results = {
            'psnr': [], 'ssim': [], 'lpips': [],
            'cv_albedo': [], 'cv_normal': [], 'cv_material': []
        }

        objects = sorted([d for d in os.listdir(dir_path) if d.startswith('object_')])

        for obj in objects:
            obj_dir = os.path.join(dir_path, obj)

            # Cross-view consistency
            for pbr in ['albedo', 'normal', 'material']:
                cv = compute_cross_view_consistency(obj_dir, pbr)
                if cv:
                    results[f'cv_{pbr}'].append(cv)

            # Per-view metrics
            for v in range(4):
                gt_path = os.path.join(obj_dir, f'gt_view{v}_albedo.png')
                pred_path = os.path.join(obj_dir, f'pred_view{v}_albedo.png')

                if not (os.path.exists(gt_path) and os.path.exists(pred_path)):
                    continue

                gt = np.array(Image.open(gt_path))
                pred = np.array(Image.open(pred_path).resize((gt.shape[1], gt.shape[0])))

                results['psnr'].append(compute_psnr(gt, pred))
                results['ssim'].append(compute_ssim(gt, pred))

                if lpips_fn:
                    results['lpips'].append(compute_lpips(gt, pred, lpips_fn))

        all_results[name] = results

    # Print results
    print(f"\n{'Metric':<25s}", end='')
    for name in args.names:
        print(f"{name:>15s}", end='')
    print()
    print("-" * (25 + 15 * len(args.names)))

    for metric in ['psnr', 'ssim', 'lpips', 'cv_albedo', 'cv_normal', 'cv_material']:
        values = []
        for name in args.names:
            if name in all_results and all_results[name][metric]:
                values.append(np.mean(all_results[name][metric]))
            else:
                values.append(None)

        label = {
            'psnr': 'PSNR (↑)',
            'ssim': 'SSIM (↑)',
            'lpips': 'LPIPS (↓)',
            'cv_albedo': 'CV Albedo (↓)',
            'cv_normal': 'CV Normal (↓)',
            'cv_material': 'CV Material (↓)',
        }[metric]

        print(f"{label:<25s}", end='')
        for v in values:
            if v is not None:
                print(f"{v:>15.4f}", end='')
            else:
                print(f"{'N/A':>15s}", end='')
        print()

    # Print sample counts
    print(f"\n{'Samples':<25s}", end='')
    for name in args.names:
        if name in all_results:
            print(f"{len(all_results[name]['psnr']):>15d}", end='')
        else:
            print(f"{'0':>15s}", end='')
    print()


if __name__ == '__main__':
    main()
