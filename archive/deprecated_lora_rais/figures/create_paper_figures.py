"""
Generate comparison figures for paper from existing inference results.
"""
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_comparison_figure(result_dirs, names, output_path, pbr='albedo', num_objects=10):
    """Create a comparison figure showing GT, predictions from different methods."""
    common_objs = None
    for d in result_dirs:
        if os.path.isdir(d):
            objs = set(os.listdir(d))
            if common_objs is None:
                common_objs = objs
            else:
                common_objs &= objs

    if common_objs is None:
        print("No common objects found")
        return

    objs = sorted([o for o in common_objs if o.startswith('object_')])[:num_objects]
    n_cols = 2 + len(result_dirs)  # Input + GT + each method
    n_rows = len(objs)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.5 * n_cols, 3.5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for row, obj in enumerate(objs):
        # Input image
        input_path = os.path.join(result_dirs[0], obj, 'input_view_0.png')
        if os.path.exists(input_path):
            axes[row, 0].imshow(Image.open(input_path))
        axes[row, 0].set_title('Input' if row == 0 else '', fontsize=10)
        axes[row, 0].axis('off')

        # GT
        gt_path = os.path.join(result_dirs[0], obj, f'gt_view0_{pbr}.png')
        if os.path.exists(gt_path):
            axes[row, 1].imshow(Image.open(gt_path))
        axes[row, 1].set_title('GT' if row == 0 else '', fontsize=10)
        axes[row, 1].axis('off')

        # Predictions
        for col, (d, name) in enumerate(zip(result_dirs, names)):
            pred_path = os.path.join(d, obj, f'pred_view0_{pbr}.png')
            if os.path.exists(pred_path):
                axes[row, col + 2].imshow(Image.open(pred_path))
            axes[row, col + 2].set_title(name if row == 0 else '', fontsize=10)
            axes[row, col + 2].axis('off')

    plt.suptitle(f'{pbr.capitalize()} Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f'Saved: {output_path}')
    plt.close()


def create_error_map_figure(result_dirs, names, output_path, pbr='albedo', num_objects=5):
    """Create error map visualization."""
    common_objs = None
    for d in result_dirs:
        if os.path.isdir(d):
            objs = set(os.listdir(d))
            if common_objs is None:
                common_objs = objs
            else:
                common_objs &= objs

    objs = sorted([o for o in common_objs if o.startswith('object_')])[:num_objects]
    n_cols = 1 + len(result_dirs)  # GT + error maps
    n_rows = len(objs)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.5 * n_cols, 3.5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for row, obj in enumerate(objs):
        gt_path = os.path.join(result_dirs[0], obj, f'gt_view0_{pbr}.png')
        if os.path.exists(gt_path):
            axes[row, 0].imshow(Image.open(gt_path))
        axes[row, 0].set_title('GT' if row == 0 else '', fontsize=10)
        axes[row, 0].axis('off')

        gt = np.array(Image.open(gt_path)).astype(float) if os.path.exists(gt_path) else None
        for col, (d, name) in enumerate(zip(result_dirs, names)):
            pred_path = os.path.join(d, obj, f'pred_view0_{pbr}.png')
            if os.path.exists(pred_path) and gt is not None:
                pred = np.array(Image.open(pred_path).resize((gt.shape[1], gt.shape[0]))).astype(float)
                error = np.mean(np.abs(gt - pred), axis=2) / 255.0
                axes[row, col + 1].imshow(error, cmap='hot', vmin=0, vmax=0.3)
                axes[row, col + 1].set_title(f'{name} Error' if row == 0 else '', fontsize=10)
            axes[row, col + 1].axis('off')

    plt.suptitle(f'{pbr.capitalize()} Error Maps', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f'Saved: {output_path}')
    plt.close()


def create_cross_view_figure(result_dirs, names, output_path, obj_idx=0, pbr='albedo'):
    """Create cross-view comparison for a single object."""
    obj = f'object_{obj_idx}'
    n_views = 4
    n_cols = 1 + len(result_dirs)  # GT + each method
    n_rows = n_views

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(3.5 * n_cols, 3.5 * n_rows))

    for row in range(n_views):
        # GT
        gt_path = os.path.join(result_dirs[0], obj, f'gt_view{row}_{pbr}.png')
        if os.path.exists(gt_path):
            axes[row, 0].imshow(Image.open(gt_path))
        axes[row, 0].set_title(f'GT View {row}' if row == 0 else f'View {row}', fontsize=10)
        axes[row, 0].axis('off')

        # Predictions
        for col, (d, name) in enumerate(zip(result_dirs, names)):
            pred_path = os.path.join(d, obj, f'pred_view{row}_{pbr}.png')
            if os.path.exists(pred_path):
                axes[row, col + 1].imshow(Image.open(pred_path))
            axes[row, col + 1].set_title(name if row == 0 else '', fontsize=10)
            axes[row, col + 1].axis('off')

    plt.suptitle(f'{obj}: Cross-View {pbr.capitalize()} Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f'Saved: {output_path}')
    plt.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=str, default='PBR/results/baseline-73-final')
    parser.add_argument('--ours', type=str, default='PBR/results/ours-73-v2')
    parser.add_argument('--output_dir', type=str, default='PBR/figures')
    parser.add_argument('--num_objects', type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    dirs = [args.baseline, args.ours]
    names = ['Baseline', 'Ours (MV-Cons)']

    for pbr in ['albedo', 'normal', 'material']:
        create_comparison_figure(dirs, names,
            os.path.join(args.output_dir, f'comparison_{pbr}.png'),
            pbr=pbr, num_objects=args.num_objects)
        create_error_map_figure(dirs, names,
            os.path.join(args.output_dir, f'error_map_{pbr}.png'),
            pbr=pbr, num_objects=5)

    # Cross-view for first object
    create_cross_view_figure(dirs, names,
        os.path.join(args.output_dir, 'cross_view_comparison.png'),
        obj_idx=0, pbr='albedo')

    print(f'\nAll figures saved to {args.output_dir}/')
