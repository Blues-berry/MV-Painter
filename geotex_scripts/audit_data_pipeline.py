"""
GeoTex-Adapter: Data Pipeline Audit
验证 RGB / normal / depth / alpha mask 的 view 顺序一致性
输出 3 个对象的可视化网格
"""
import os
import sys
import random
import numpy as np
import cv2
import torch
import torchvision
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'mvpoutput', 'geotex_audit')
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATA_ROOT = '/4T/CXY/MV-Painter/data/train_data/rendered_full'

# 6 target views (normal order)
TARGET_ORDER_NORMAL = [0, 15, 12, 15, 13, 14]
# 6 target views (reverse order)
TARGET_ORDER_REVERSE = [14, 15, 0, 15, 12, 13]


def load_image(path):
    """Load RGB image with alpha, return (H,W,3) float [0,1] and alpha mask."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    alpha = img[:, :, 3:].astype(np.float32) / 255.0
    rgb = img[:, :, :3].astype(np.float32) / 255.0
    # Apply alpha: white background
    rgb = rgb * alpha + (1 - alpha)
    return rgb, alpha[:, :, 0]


def load_normal(path):
    """Load normal map (uint16, RGB), return (H,W,3) float [0,1]."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img.astype(np.float32) / 65535.0


def load_depth(path):
    """Load depth map (uint16, grayscale), return (H,W) float [0,1]."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {path}")
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    depth = img.astype(np.float32) / 65535.0
    return depth


def determine_view_order(obj_path):
    """Determine if object uses normal or reverse view order."""
    img_path = os.path.join(obj_path, 'image')
    first_img = cv2.imread(os.path.join(img_path, '000.png'), cv2.IMREAD_UNCHANGED)
    fourth_img = cv2.imread(os.path.join(img_path, '014.png'), cv2.IMREAD_UNCHANGED)

    if first_img is None or fourth_img is None:
        return TARGET_ORDER_NORMAL, False

    first_alpha = (first_img[:, :, 3] == 0).sum() if first_img.shape[2] == 4 else 0
    fourth_alpha = (fourth_img[:, :, 3] == 0).sum() if fourth_img.shape[2] == 4 else 0

    if first_alpha > fourth_alpha:
        return TARGET_ORDER_REVERSE, True
    else:
        return TARGET_ORDER_NORMAL, False


def audit_single_object(obj_path, obj_name):
    """Audit one object: check view consistency across modalities."""
    report = {
        'name': obj_name,
        'view_order': None,
        'is_reverse': None,
        'views_ok': True,
        'mask_stats': {},
        'depth_stats': {},
        'normal_stats': {},
        'issues': [],
    }

    # 1. Determine view order
    view_order, is_reverse = determine_view_order(obj_path)
    report['view_order'] = view_order
    report['is_reverse'] = is_reverse

    # 2. Check all target views exist across all modalities
    modalities = {
        'image': os.path.join(obj_path, 'image'),
        'normal': os.path.join(obj_path, 'normal'),
        'depth': os.path.join(obj_path, 'depth_png'),
    }

    for mod_name, mod_path in modalities.items():
        if not os.path.exists(mod_path):
            report['issues'].append(f"Missing directory: {mod_path}")
            report['views_ok'] = False
            continue

        for view_idx in view_order:
            fname = f'{view_idx:03d}.png'
            fpath = os.path.join(mod_path, fname)
            if not os.path.exists(fpath):
                report['issues'].append(f"Missing file: {fpath}")
                report['views_ok'] = False

    # 3. Load and check data for each target view
    for i, view_idx in enumerate(view_order):
        try:
            rgb, alpha = load_image(os.path.join(modalities['image'], f'{view_idx:03d}.png'))
            normal = load_normal(os.path.join(modalities['normal'], f'{view_idx:03d}.png'))
            depth = load_depth(os.path.join(modalities['depth'], f'{view_idx:03d}.png'))

            # Check shapes match
            h, w = rgb.shape[:2]
            assert normal.shape[:2] == (h, w), f"Normal shape mismatch at view {view_idx}: {normal.shape} vs {(h, w)}"
            assert depth.shape == (h, w), f"Depth shape mismatch at view {view_idx}: {depth.shape} vs {(h, w)}"
            assert alpha.shape == (h, w), f"Alpha shape mismatch at view {view_idx}: {alpha.shape} vs {(h, w)}"

            # Stats
            fg_mask = alpha > 0.5
            fg_ratio = fg_mask.sum() / (h * w)

            report['mask_stats'][f'view_{view_idx:03d}'] = {
                'fg_ratio': float(fg_ratio),
                'alpha_min': float(alpha.min()),
                'alpha_max': float(alpha.max()),
                'alpha_mean': float(alpha.mean()),
            }

            if fg_ratio < 0.01:
                report['issues'].append(f"View {view_idx}: very low foreground ratio ({fg_ratio:.4f})")

            report['depth_stats'][f'view_{view_idx:03d}'] = {
                'min': float(depth.min()),
                'max': float(depth.max()),
                'mean': float(depth[fg_mask].mean()) if fg_mask.any() else 0,
            }

            report['normal_stats'][f'view_{view_idx:03d}'] = {
                'min': float(normal.min()),
                'max': float(normal.max()),
                'mean': float(normal[fg_mask].mean()) if fg_mask.any() else 0,
            }

        except Exception as e:
            report['issues'].append(f"Error loading view {view_idx}: {e}")
            report['views_ok'] = False

    return report


def create_visualization_grid(obj_path, obj_name, view_order, is_reverse):
    """Create a visualization grid: rows=modalities, cols=6 target views."""
    modalities = {
        'RGB': os.path.join(obj_path, 'image'),
        'Normal': os.path.join(obj_path, 'normal'),
        'Depth': os.path.join(obj_path, 'depth_png'),
    }

    grid_images = []

    for mod_name, mod_path in modalities.items():
        row_images = []
        for view_idx in view_order:
            fpath = os.path.join(mod_path, f'{view_idx:03d}.png')

            if mod_name == 'RGB':
                img, alpha = load_image(fpath)
                img = (img * 255).astype(np.uint8)
            elif mod_name == 'Normal':
                img = load_normal(fpath)
                img = (img * 255).astype(np.uint8)
            elif mod_name == 'Depth':
                depth = load_depth(fpath)
                # Colorize depth for visualization
                depth_u8 = (depth * 255).astype(np.uint8)
                img = cv2.applyColorMap(depth_u8, cv2.COLORMAP_INFERNO)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Resize to 128x128 for grid
            img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
            row_images.append(img)

        # Add label
        label = np.ones((128, 32, 3), dtype=np.uint8) * 255
        # Put text vertically
        for j, char in enumerate(mod_name):
            if j < 16:
                cv2.putText(label, char, (5, 20 + j * 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)

        row = np.concatenate([label] + row_images, axis=1)
        grid_images.append(row)

    grid = np.concatenate(grid_images, axis=0)

    # Add header
    header = np.ones((32, 32 + 128 * 6, 3), dtype=np.uint8) * 255
    for i, view_idx in enumerate(view_order):
        x = 32 + i * 128 + 48
        cv2.putText(header, f'V{view_idx:02d}', (x, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    order_str = "REVERSE" if is_reverse else "NORMAL"
    cv2.putText(header, f'{obj_name} ({order_str})', (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)

    grid = np.concatenate([header, grid], axis=0)

    return grid


def main():
    print("=" * 60)
    print("GeoTex-Adapter Data Pipeline Audit")
    print("=" * 60)

    # Get all objects
    all_objects = sorted(os.listdir(DATA_ROOT))
    all_objects = [o for o in all_objects if os.path.isdir(os.path.join(DATA_ROOT, o))]

    # Filter to objects with clean_objects.txt
    clean_list_path = os.path.join(DATA_ROOT, 'clean_objects.txt')
    if os.path.exists(clean_list_path):
        with open(clean_list_path) as f:
            clean_names = [l.strip() for l in f if l.strip()]
        all_objects = [o for o in all_objects if o in clean_names]

    print(f"Total clean objects: {len(all_objects)}")

    # Select 3 random objects for audit
    random.seed(42)
    audit_objects = random.sample(all_objects, min(3, len(all_objects)))

    reports = []
    grids = []

    for obj_name in audit_objects:
        obj_path = os.path.join(DATA_ROOT, obj_name)
        print(f"\n--- Auditing: {obj_name} ---")

        report = audit_single_object(obj_path, obj_name)
        reports.append(report)

        # Print report
        print(f"  View order: {report['view_order']} ({'REVERSE' if report['is_reverse'] else 'NORMAL'})")
        print(f"  Views OK: {report['views_ok']}")
        if report['issues']:
            print(f"  Issues: {len(report['issues'])}")
            for issue in report['issues']:
                print(f"    - {issue}")

        # Mask stats
        print(f"  Mask stats (foreground ratio):")
        for view_key, stats in report['mask_stats'].items():
            print(f"    {view_key}: fg_ratio={stats['fg_ratio']:.3f}, alpha_range=[{stats['alpha_min']:.2f}, {stats['alpha_max']:.2f}]")

        # Create visualization
        view_order, is_reverse = report['view_order'], report['is_reverse']
        grid = create_visualization_grid(obj_path, obj_name, view_order, is_reverse)
        grids.append(grid)

        # Save individual grid
        grid_path = os.path.join(OUTPUT_DIR, f'audit_{obj_name}.png')
        cv2.imwrite(grid_path, cv2.cvtColor(grid, cv2.COLOR_RGB2BGR))
        print(f"  Saved grid: {grid_path}")

    # Save combined grid
    if grids:
        max_width = max(g.shape[1] for g in grids)
        padded_grids = []
        for g in grids:
            if g.shape[1] < max_width:
                pad = np.ones((g.shape[0], max_width - g.shape[1], 3), dtype=np.uint8) * 255
                g = np.concatenate([g, pad], axis=1)
            padded_grids.append(g)
        combined = np.concatenate(padded_grids, axis=0)
        combined_path = os.path.join(OUTPUT_DIR, 'audit_combined.png')
        cv2.imwrite(combined_path, cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))
        print(f"\nCombined grid saved: {combined_path}")

    # Summary report
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)

    all_ok = all(r['views_ok'] for r in reports)
    print(f"All views consistent: {'YES' if all_ok else 'NO'}")

    # Check view order consistency
    orders = [r['view_order'] for r in reports]
    print(f"View orders seen: {set(tuple(o) for o in orders)}")

    # Check mask usability
    all_fg_ratios = []
    for r in reports:
        for stats in r['mask_stats'].values():
            all_fg_ratios.append(stats['fg_ratio'])
    if all_fg_ratios:
        print(f"Foreground ratio: min={min(all_fg_ratios):.3f}, max={max(all_fg_ratios):.3f}, mean={np.mean(all_fg_ratios):.3f}")
        print(f"Alpha mask usable for foreground-only metrics: {'YES' if min(all_fg_ratios) > 0.01 else 'CAUTION - some views have very low fg'}")

    # Save text report
    report_path = os.path.join(OUTPUT_DIR, 'audit_report.txt')
    with open(report_path, 'w') as f:
        f.write("GeoTex-Adapter Data Pipeline Audit Report\n")
        f.write("=" * 60 + "\n\n")
        for r in reports:
            f.write(f"Object: {r['name']}\n")
            f.write(f"  View order: {r['view_order']} ({'REVERSE' if r['is_reverse'] else 'NORMAL'})\n")
            f.write(f"  Views OK: {r['views_ok']}\n")
            f.write(f"  Issues: {r['issues']}\n")
            f.write(f"  Mask stats: {r['mask_stats']}\n")
            f.write(f"  Depth stats: {r['depth_stats']}\n")
            f.write(f"  Normal stats: {r['normal_stats']}\n\n")
        f.write(f"\nAll views consistent: {all_ok}\n")
        f.write(f"Foreground ratio range: [{min(all_fg_ratios):.3f}, {max(all_fg_ratios):.3f}]\n")
    print(f"\nReport saved: {report_path}")


if __name__ == '__main__':
    main()
