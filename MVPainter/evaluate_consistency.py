"""
Cross-view consistency evaluation for PBR material generation.
Measures whether different views of the same object produce consistent PBR maps.
"""
import os
import numpy as np
from PIL import Image
import argparse


def compute_cross_view_consistency(pred_dir, pbr_types=['albedo', 'normal', 'material']):
    """
    Compute cross-view consistency for a single object.

    For each pair of views, compute the L1 difference of their PBR predictions
    in overlapping regions (where both views have non-background pixels).

    Args:
        pred_dir: directory containing pred_view{N}_{pbr}.png files
        pbr_types: list of PBR types to evaluate

    Returns:
        dict of {pbr_type: consistency_score} where lower is more consistent
    """
    results = {}

    for pbr in pbr_types:
        views = []
        for v in range(4):
            path = os.path.join(pred_dir, f'pred_view{v}_{pbr}.png')
            if os.path.exists(path):
                img = np.array(Image.open(path)).astype(float)
                views.append(img)

        if len(views) < 2:
            continue

        # Compute pairwise L1 differences
        diffs = []
        for i in range(len(views)):
            for j in range(i+1, len(views)):
                diff = np.mean(np.abs(views[i] - views[j]))
                diffs.append(diff)

        results[pbr] = np.mean(diffs)

    return results


def compute_gt_vs_pred_consistency(pred_dir, gt_dir, pbr_types=['albedo', 'normal', 'material']):
    """
    Compute consistency between predicted PBR maps and ground truth.

    Args:
        pred_dir: directory containing pred_view{N}_{pbr}.png files
        gt_dir: directory containing gt_view{N}_{pbr}.png files
        pbr_types: list of PBR types to evaluate

    Returns:
        dict of {pbr_type: {'psnr': ..., 'ssim': ..., 'mae': ...}}
    """
    from PIL import Image

    def compute_psnr(img1, img2):
        mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
        if mse == 0: return float('inf')
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

    results = {}

    for pbr in pbr_types:
        psnr_list, ssim_list, mae_list = [], [], []

        for v in range(4):
            pred_path = os.path.join(pred_dir, f'pred_view{v}_{pbr}.png')
            gt_path = os.path.join(gt_dir, f'gt_view{v}_{pbr}.png')

            if not (os.path.exists(pred_path) and os.path.exists(gt_path)):
                continue

            pred = np.array(Image.open(pred_path))
            gt = np.array(Image.open(gt_path).resize((pred.shape[1], pred.shape[0])))

            psnr_list.append(compute_psnr(gt, pred))
            ssim_list.append(compute_ssim(gt, pred))
            mae_list.append(np.mean(np.abs(gt.astype(float) - pred.astype(float))))

        if psnr_list:
            results[pbr] = {
                'psnr': np.mean(psnr_list),
                'ssim': np.mean(ssim_list),
                'mae': np.mean(mae_list)
            }

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline_dir', type=str, default='PBR/results/baseline-73-final')
    parser.add_argument('--ours_dir', type=str, default='PBR/results/ours-73-final')
    args = parser.parse_args()

    print("=" * 80)
    print("Cross-View Consistency Evaluation")
    print("=" * 80)

    baseline_cv = {}
    ours_cv = {}

    for obj_idx in range(15):
        obj = f'object_{obj_idx}'
        bl_dir = os.path.join(args.baseline_dir, obj)
        ou_dir = os.path.join(args.ours_dir, obj)

        if not (os.path.isdir(bl_dir) and os.path.isdir(ou_dir)):
            continue

        bl_cv = compute_cross_view_consistency(bl_dir)
        ou_cv = compute_cross_view_consistency(ou_dir)

        for pbr in bl_cv:
            if pbr not in baseline_cv:
                baseline_cv[pbr] = []
                ours_cv[pbr] = []
            baseline_cv[pbr].append(bl_cv[pbr])
            ours_cv[pbr].append(ou_cv[pbr])

    print("\n--- Cross-View Consistency (lower = more consistent) ---")
    for pbr in ['albedo', 'normal', 'material']:
        if pbr in baseline_cv:
            bl_mean = np.mean(baseline_cv[pbr])
            ou_mean = np.mean(ours_cv[pbr])
            better = "✓ Ours" if ou_mean < bl_mean else "✗ Baseline"
            diff = (bl_mean - ou_mean) / bl_mean * 100
            print(f"  {pbr:10s}: BL={bl_mean:.2f}, OU={ou_mean:.2f}, diff={diff:+.1f}% {better}")

    print("\n--- Per-View PSNR (higher = better) ---")
    baseline_psnr = {}
    ours_psnr = {}

    for obj_idx in range(15):
        obj = f'object_{obj_idx}'
        bl_dir = os.path.join(args.baseline_dir, obj)
        ou_dir = os.path.join(args.ours_dir, obj)
        gt_dir = bl_dir  # GT is same for both

        if not (os.path.isdir(bl_dir) and os.path.isdir(ou_dir)):
            continue

        bl_metrics = compute_gt_vs_pred_consistency(bl_dir, gt_dir)
        ou_metrics = compute_gt_vs_pred_consistency(ou_dir, gt_dir)

        for pbr in bl_metrics:
            if pbr not in baseline_psnr:
                baseline_psnr[pbr] = []
                ours_psnr[pbr] = []
            baseline_psnr[pbr].append(bl_metrics[pbr]['psnr'])
            ours_psnr[pbr].append(ou_metrics[pbr]['psnr'])

    for pbr in ['albedo', 'normal', 'material']:
        if pbr in baseline_psnr:
            bl_mean = np.mean(baseline_psnr[pbr])
            ou_mean = np.mean(ours_psnr[pbr])
            better = "✓ Ours" if ou_mean > bl_mean else "✗ Baseline"
            diff = (ou_mean - bl_mean) / bl_mean * 100
            print(f"  {pbr:10s}: BL={bl_mean:.2f}, OU={ou_mean:.2f}, diff={diff:+.1f}% {better}")


if __name__ == '__main__':
    main()
