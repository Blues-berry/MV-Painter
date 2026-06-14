"""Generate comparison panels from existing eval outputs and source data.

Reads visual_manifest.json. Uses only pre-existing files — does NOT run inference.

Outputs:
- source_data_grid: GT images from source data for selected objects
- metric_comparison_table: per-object metric comparison as image
- error_maps: s=2.50 vs s=1.25 difference maps (where both adapter images exist)

Usage: python scripts/visual_audit/make_comparison_panels.py
"""
import json, os, csv
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

MANIFEST = "mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/visual_manifest.json"
OUTPUT_DIR = "mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/panels"
METRIC_CSV_125 = "mvpoutput/geotex_refattn_v1/scale_1p25_300obj/per_object_metrics.csv"
METRIC_CSV_250 = "mvpoutput/geotex_refattn_v1/eval_300obj_scale_2p50/per_object_metrics.csv"


def load_metrics(csv_path):
    if not os.path.exists(csv_path):
        return {}
    with open(csv_path) as f:
        return {int(r['object_idx']): r for r in csv.DictReader(f)}


def make_metric_table_image(manifest, output_path):
    """Generate a visual metric comparison table as PNG."""
    if not HAS_PIL:
        print("PIL not available, skipping metric table image")
        return

    m125 = load_metrics(METRIC_CSV_125)
    m250 = load_metrics(METRIC_CSV_250)

    objs = manifest['objects']
    cols = ['obj', 'category', 'FG_125', 'FG_250', 'ΔFG', 'NEF_125', 'NEF_250', 'ΔNEF', 'Edge_125', 'Edge_250', 'ΔEdge']
    row_h = 28
    col_w = [50, 150, 70, 70, 70, 70, 70, 70, 70, 70, 70]
    total_w = sum(col_w)
    total_h = (len(objs) + 1) * row_h + 20

    img = Image.new('RGB', (total_w, total_h), 'white')
    draw = ImageDraw.Draw(img)

    # Header
    x = 10
    for i, col in enumerate(cols):
        draw.text((x, 5), col, fill='black')
        x += col_w[i]

    # Rows
    for row_idx, obj_entry in enumerate(objs):
        obj = obj_entry['object_idx']
        y = (row_idx + 1) * row_h + 10
        x = 10

        fg125 = float(m125[obj]['delta_fg_ssim']) if obj in m125 else 0
        fg250 = float(m250[obj]['delta_fg_ssim']) if obj in m250 else 0
        nef125 = float(m125[obj]['delta_nef_ssim']) if obj in m125 else 0
        nef250 = float(m250[obj]['delta_nef_ssim']) if obj in m250 else 0
        edge125 = float(m125[obj]['delta_edge_ssim']) if obj in m125 else 0
        edge250 = float(m250[obj]['delta_edge_ssim']) if obj in m250 else 0

        vals = [
            str(obj), obj_entry['category'][:15],
            f"{fg125:+.3f}", f"{fg250:+.3f}", f"{fg250-fg125:+.3f}",
            f"{nef125:+.3f}", f"{nef250:+.3f}", f"{nef250-nef125:+.3f}",
            f"{edge125:+.3f}", f"{edge250:+.3f}", f"{edge250-edge125:+.3f}",
        ]

        for i, val in enumerate(vals):
            color = 'black'
            if i in [4, 7, 10]:  # delta columns
                try:
                    v = float(val)
                    color = 'green' if v > 0.005 else 'red' if v < -0.005 else 'gray'
                except ValueError:
                    pass
            draw.text((x, y), val, fill=color)
            x += col_w[i]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Saved: {output_path}")


def make_source_data_grid(manifest, output_path):
    """Generate grid of GT source images for selected objects."""
    if not HAS_PIL:
        print("PIL not available, skipping source data grid")
        return

    objects = manifest['objects'][:12]  # Limit to 12 for grid
    if not objects:
        return

    # Check which objects have source images
    valid = []
    for obj_entry in objects:
        img_dir = obj_entry['source_data']['image_dir']
        if os.path.isdir(img_dir):
            imgs = sorted([f for f in os.listdir(img_dir) if f.endswith('.png')])
            if imgs:
                valid.append((obj_entry, imgs[0]))  # First view

    if not valid:
        print("No source images found")
        return

    # Load first image to get size
    sample_path = os.path.join(valid[0][0]['source_data']['image_dir'], valid[0][1])
    sample = Image.open(sample_path)
    img_w, img_h = sample.size

    # Grid: 4 columns
    n_cols = min(4, len(valid))
    n_rows = (len(valid) + n_cols - 1) // n_cols
    pad = 4
    label_h = 30

    grid_w = n_cols * (img_w + pad) + pad
    grid_h = n_rows * (img_h + label_h + pad) + pad

    grid = Image.new('RGB', (grid_w, grid_h), 'white')
    draw = ImageDraw.Draw(grid)

    for idx, (obj_entry, img_file) in enumerate(valid):
        row, col = divmod(idx, n_cols)
        x = pad + col * (img_w + pad)
        y = pad + row * (img_h + label_h + pad)

        img_path = os.path.join(obj_entry['source_data']['image_dir'], img_file)
        img = Image.open(img_path).convert('RGB').resize((img_w, img_h))
        grid.paste(img, (x, y))

        label = f"obj={obj_entry['object_idx']} {obj_entry['category'][:12]}"
        draw.text((x, y + img_h + 2), label, fill='black')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    grid.save(output_path)
    print(f"Saved: {output_path}")


def make_error_maps(manifest, output_dir):
    """Generate error maps between s=1.25 and s=2.50 adapter outputs (where available)."""
    if not HAS_PIL:
        print("PIL not available, skipping error maps")
        return

    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for obj_entry in manifest['objects']:
        obj = obj_entry['object_idx']

        # Check if both adapter images exist
        vis_125 = obj_entry['eval_outputs'].get('s1.25_300obj', {}).get('vis', {}).get('adapter')
        vis_250 = obj_entry['eval_outputs'].get('s2.50_300obj', {}).get('vis', {}).get('adapter')

        if not (vis_125 and vis_250 and os.path.exists(vis_125) and os.path.exists(vis_250)):
            continue

        img_125 = np.array(Image.open(vis_125).convert('RGB')).astype(float) / 255.0
        img_250 = np.array(Image.open(vis_250).convert('RGB')).astype(float) / 255.0

        if img_125.shape != img_250.shape:
            continue

        # Absolute difference
        diff = np.abs(img_250 - img_125)
        diff_mean = diff.mean(axis=2)  # Average over RGB

        # Fixed vmax for consistent coloring
        vmax = 0.3
        diff_norm = np.clip(diff_mean / vmax, 0, 1)

        # Save raw error
        np.save(f"{output_dir}/obj_{obj:03d}_error.npy", diff_mean)

        # Save visualization
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(img_125)
        axes[0].set_title(f's=1.25 adapter')
        axes[0].axis('off')
        axes[1].imshow(img_250)
        axes[1].set_title(f's=2.50 adapter')
        axes[1].axis('off')
        im = axes[2].imshow(diff_norm, cmap='hot', vmin=0, vmax=1)
        axes[2].set_title(f'|Δ| (vmax={vmax})')
        axes[2].axis('off')
        plt.colorbar(im, ax=axes[2], fraction=0.046)
        plt.suptitle(f'Object {obj} — {obj_entry["category"]}')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/obj_{obj:03d}_error.png", dpi=100)
        plt.close()

        # Save metadata
        meta = {
            'object_idx': obj,
            'source_125': vis_125,
            'source_250': vis_250,
            'vmax': vmax,
            'mean_error': float(diff_mean.mean()),
            'max_error': float(diff_mean.max()),
        }
        with open(f"{output_dir}/obj_{obj:03d}_error.json", 'w') as f:
            json.dump(meta, f, indent=2)

        count += 1

    print(f"Generated {count} error maps in {output_dir}")


def main():
    with open(MANIFEST) as f:
        manifest = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Metric comparison table
    make_metric_table_image(manifest, f"{OUTPUT_DIR}/metric_comparison_table.png")

    # 2. Source data grid
    make_source_data_grid(manifest, f"{OUTPUT_DIR}/source_data_grid.png")

    # 3. Error maps
    make_error_maps(manifest, f"{OUTPUT_DIR}/error_maps")

    # 4. Report what's missing
    print(f"\n=== Asset Status ===")
    total_vis = 0
    missing_vis = 0
    for obj in manifest['objects']:
        for eval_name, eval_data in obj['eval_outputs'].items():
            for suffix, path in eval_data['vis'].items():
                total_vis += 1
                if path is None or not os.path.exists(path or ''):
                    missing_vis += 1

    print(f"Total vis slots: {total_vis}")
    print(f"Missing vis: {missing_vis}")
    print(f"Available vis: {total_vis - missing_vis}")
    print(f"\nNOTE: Adapter visualizations for selected objects require targeted eval.")
    print(f"Run: python scripts/visual_audit/generate_selected_vis.py --device cuda:0")


if __name__ == '__main__':
    main()
