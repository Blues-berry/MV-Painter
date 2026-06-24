"""Generate publication-ready comparison figures.

Creates professional paper-quality comparison grids with:
- GT / Baseline / Ours columns
- Zoom-in crops with red boxes highlighting improvements
- Error maps as supplementary evidence
- Multi-view strips for texture consistency

Layout options:
- Standard: 3-column (GT | Baseline | Ours) × N rows
- Extended: 5-column (Reference | Geometry | GT | Baseline | Ours)
- Ablation: (Reference | w/o feature | w/ feature | GT)
- With zooms: Same as above but with zoom-in crops below each row

Usage:
    python geotex/generate_paper_comparison.py \
        --input_dir mvpoutput/quality_showcase_enhanced \
        --output_dir mvpoutput/paper_figures_final \
        --objects 79,72,209,43,32 \
        --layout standard_with_zooms \
        --zoom_regions auto
"""
import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import cv2
except ImportError:
    print("Install: pip install Pillow opencv-python")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Image utilities
# ---------------------------------------------------------------------------

def load_img(path, size=None):
    """Load image, optionally resize."""
    img = Image.open(path).convert('RGB')
    if size:
        img = img.resize(size, Image.LANCZOS)
    return np.array(img)


def find_zoom_regions(ours, baseline, gt, mask=None, num_crops=2, crop_size=128):
    """Automatically find regions where ours is most different from baseline.

    Strategy: find regions where |ours - gt| < |baseline - gt| by the largest margin.
    These are the regions where our method shows the clearest improvement.
    """
    # Convert to float
    ours_f = ours.astype(np.float32) / 255.0
    baseline_f = baseline.astype(np.float32) / 255.0
    gt_f = gt.astype(np.float32) / 255.0

    # Compute improvement map: where ours is closer to GT than baseline
    err_baseline = np.abs(baseline_f - gt_f).mean(axis=2)
    err_ours = np.abs(ours_f - gt_f).mean(axis=2)
    improvement = err_baseline - err_ours  # positive = ours is better

    # Apply mask if available
    if mask is not None:
        improvement[~mask] = 0

    # Smooth to find regions (not single pixels)
    improvement_smooth = cv2.GaussianBlur(improvement, (15, 15), 5.0)

    H, W = improvement_smooth.shape
    half = crop_size // 2
    regions = []

    for _ in range(num_crops):
        # Find max improvement location
        y, x = np.unravel_index(improvement_smooth.argmax(), improvement_smooth.shape)

        # Clamp to valid region
        y = max(half, min(H - half, y))
        x = max(half, min(W - half, x))

        regions.append((y - half, x - half, y + half, x + half))

        # Zero out this region to find next best
        y1, x1, y2, x2 = max(0, y - crop_size), max(0, x - crop_size), \
                          min(H, y + crop_size), min(W, x + crop_size)
        improvement_smooth[y1:y2, x1:x2] = 0

    return regions


def draw_zoom_box(img, region, color=(255, 0, 0), thickness=2):
    """Draw a colored rectangle on image."""
    result = img.copy()
    y1, x1, y2, x2 = region
    cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)
    return result


def extract_crop(img, region, target_size=None):
    """Extract a crop from image, optionally resize."""
    y1, x1, y2, x2 = region
    crop = img[y1:y2, x1:x2]
    if target_size:
        crop = cv2.resize(crop, target_size, interpolation=cv2.INTER_LANCZOS4)
    return crop


def add_border(img, width=2, color=(200, 200, 200)):
    """Add a thin border around image."""
    h, w = img.shape[:2]
    bordered = np.full((h + 2*width, w + 2*width, 3), color, dtype=np.uint8)
    bordered[width:width+h, width:width+w] = img
    return bordered


def add_label(img, text, position='top', font_size=14, color=(0, 0, 0)):
    """Add text label to image."""
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if position == 'top':
        x = (img.shape[1] - text_w) // 2
        y = 4
    elif position == 'bottom':
        x = (img.shape[1] - text_w) // 2
        y = img.shape[0] - text_h - 6

    draw.text((x, y), text, fill=color, font=font)
    return np.array(pil_img)


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------

def make_comparison_grid(objects_data, layout='standard_with_zooms',
                         cell_size=(256, 384), zoom_crop_size=96,
                         zoom_display_size=128, gap=4, label_height=24):
    """Create a multi-row comparison grid.

    Args:
        objects_data: list of dicts with keys: gt, baseline, ours, reference, mask, normal
        layout: 'standard' | 'standard_with_zooms' | 'extended' | 'ablation'
        cell_size: (width, height) for each cell
        zoom_crop_size: size of crop in original image
        zoom_display_size: displayed size of zoom crop
    """
    cell_w, cell_h = cell_size
    n_objects = len(objects_data)

    if layout == 'standard':
        columns = ['GT', 'Baseline', 'Ours']
        col_keys = ['gt', 'baseline', 'ours']
    elif layout == 'standard_with_zooms':
        columns = ['GT', 'Baseline', 'Ours']
        col_keys = ['gt', 'baseline', 'ours']
    elif layout == 'extended':
        columns = ['Reference', 'Geometry', 'GT', 'Baseline', 'Ours']
        col_keys = ['reference', 'normal', 'gt', 'baseline', 'ours']
    elif layout == 'ablation':
        columns = ['Reference', 'w/o Adapter', 'w/ Adapter', 'GT']
        col_keys = ['reference', 'baseline', 'ours', 'gt']

    n_cols = len(columns)

    # Calculate canvas size
    row_height = cell_h + gap
    if 'zoom' in layout:
        row_height += zoom_display_size + gap

    total_w = n_cols * (cell_w + gap) - gap + 2 * gap  # extra padding
    total_h = label_height + n_objects * row_height + gap

    # Create white canvas
    canvas = np.ones((total_h, total_w, 3), dtype=np.uint8) * 255

    # Draw column headers
    header_img = np.ones((label_height, total_w, 3), dtype=np.uint8) * 255
    for col_idx, col_name in enumerate(columns):
        x = gap + col_idx * (cell_w + gap)
        # Create header cell
        header_cell = np.ones((label_height, cell_w, 3), dtype=np.uint8) * 255
        header_cell = add_label(header_cell, col_name, position='top', font_size=12)
        canvas[0:label_height, x:x+cell_w] = header_cell

    # Draw each object row
    for row_idx, obj in enumerate(objects_data):
        y_base = label_height + row_idx * row_height

        # Load and resize images
        images = {}
        for key in col_keys:
            if key in obj and obj[key] is not None and os.path.exists(str(obj[key])):
                img = load_img(str(obj[key]))
                # Handle multi-view grids (512x768 = 2x3 grid of 256x256)
                # Resize maintaining aspect ratio to fit cell
                h, w = img.shape[:2]
                scale = min(cell_w / w, cell_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
                img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                # Center in cell
                cell_img = np.ones((cell_h, cell_w, 3), dtype=np.uint8) * 255
                y_off = (cell_h - new_h) // 2
                x_off = (cell_w - new_w) // 2
                cell_img[y_off:y_off+new_h, x_off:x_off+new_w] = img_resized
                images[key] = cell_img
            else:
                images[key] = np.ones((cell_h, cell_w, 3), dtype=np.uint8) * 240

        # Find zoom regions
        zoom_regions = []
        if 'zoom' in layout and 'ours' in images and 'baseline' in images and 'gt' in images:
            mask = None
            if 'mask' in obj and obj['mask'] and os.path.exists(str(obj['mask'])):
                mask_img = Image.open(str(obj['mask'])).convert('L')
                mask_img = mask_img.resize((cell_w, cell_h), Image.NEAREST)
                mask = np.array(mask_img) > 128

            zoom_regions = find_zoom_regions(
                images['ours'], images['baseline'], images['gt'],
                mask=mask, num_crops=2, crop_size=zoom_crop_size
            )

        # Place images in grid
        for col_idx, key in enumerate(col_keys):
            x = gap + col_idx * (cell_w + gap)
            img = images[key]

            # Draw zoom boxes on main images
            if zoom_regions and key in ('gt', 'baseline', 'ours'):
                colors = [(255, 50, 50), (50, 200, 50)]  # Red, Green
                for region, color in zip(zoom_regions, colors):
                    img = draw_zoom_box(img, region, color=color, thickness=2)

            canvas[y_base:y_base+cell_h, x:x+cell_w] = img

        # Draw zoom crops below
        if zoom_regions and 'zoom' in layout:
            y_zoom = y_base + cell_h + gap
            colors = [(255, 50, 50), (50, 200, 50)]

            for crop_idx, (region, color) in enumerate(zip(zoom_regions, colors)):
                for col_idx, key in enumerate(col_keys):
                    if key not in ('gt', 'baseline', 'ours'):
                        continue

                    x = gap + col_idx * (cell_w + gap)
                    crop = extract_crop(images[key], region, (zoom_display_size, zoom_display_size))
                    crop = add_border(crop, width=2, color=color)

                    # Position crops within the cell width
                    crop_x = x + crop_idx * (zoom_display_size + gap + 4)
                    crop_h, crop_w = crop.shape[:2]

                    if crop_x + crop_w <= total_w and y_zoom + crop_h <= total_h:
                        canvas[y_zoom:y_zoom+crop_h, crop_x:crop_x+crop_w] = crop

    return canvas


def make_single_comparison(gt_path, baseline_path, ours_path, mask_path=None,
                           reference_path=None, output_path=None,
                           with_zooms=True, with_error=False):
    """Create a single object comparison figure.

    Returns: comparison image as numpy array
    """
    gt = load_img(gt_path)
    baseline = load_img(baseline_path)
    ours = load_img(ours_path)

    h, w = gt.shape[:2]

    # Build columns
    columns = [gt, baseline, ours]
    labels = ['GT', 'Baseline (No Adapter)', 'Ours (GeoTex-Adapter)']

    if reference_path and os.path.exists(reference_path):
        ref = load_img(reference_path)
        if ref.shape[:2] != (h, w):
            ref = cv2.resize(ref, (w, h), interpolation=cv2.INTER_LANCZOS4)
        columns.insert(0, ref)
        labels.insert(0, 'Reference')

    if with_error:
        err_baseline = np.abs(baseline.astype(np.float32) - gt.astype(np.float32))
        err_ours = np.abs(ours.astype(np.float32) - gt.astype(np.float32))
        # Amplify error for visibility
        err_baseline = np.clip(err_baseline * 3, 0, 255).astype(np.uint8)
        err_ours = np.clip(err_ours * 3, 0, 255).astype(np.uint8)
        columns.extend([err_baseline, err_ours])
        labels.extend(['Error (Baseline)', 'Error (Ours)'])

    # Find zoom regions
    mask = None
    if mask_path and os.path.exists(mask_path):
        mask_img = Image.open(mask_path).convert('L')
        if mask_img.size != (w, h):
            mask_img = mask_img.resize((w, h), Image.NEAREST)
        mask = np.array(mask_img) > 128

    zoom_regions = []
    if with_zooms:
        zoom_regions = find_zoom_regions(ours, baseline, gt, mask, num_crops=2, crop_size=min(h, w) // 4)

    # Save clean copies for crop extraction BEFORE drawing boxes
    columns_clean = [col.copy() for col in columns]

    # Draw zoom boxes on display copies
    if zoom_regions:
        colors = [(255, 50, 50), (50, 180, 50)]
        for i in range(len(columns)):
            if labels[i] in ('GT', 'Baseline (No Adapter)', 'Ours (GeoTex-Adapter)'):
                for region, color in zip(zoom_regions, colors):
                    columns[i] = draw_zoom_box(columns[i], region, color=color, thickness=2)

    # Assemble main row
    gap = 4
    n_cols = len(columns)
    main_w = n_cols * w + (n_cols - 1) * gap
    main_row = np.ones((h, main_w, 3), dtype=np.uint8) * 255
    for i, col in enumerate(columns):
        x = i * (w + gap)
        main_row[:, x:x+w] = col

    # Add labels
    label_height = 24
    labeled = np.ones((label_height + h, main_w, 3), dtype=np.uint8) * 255
    labeled[label_height:, :] = main_row
    for i, label in enumerate(labels):
        x = i * (w + gap)
        cell = labeled[:label_height, x:x+w]
        labeled[:label_height, x:x+w] = add_label(cell, label, position='top', font_size=11)

    # Add zoom row
    if zoom_regions:
        zoom_size = min(h // 2, 192)
        # Border adds 2*width pixels on each side
        border_width = 2
        crop_with_border_size = zoom_size + 2 * border_width
        zoom_row_h = crop_with_border_size + 4  # extra padding
        zoom_row = np.ones((zoom_row_h, main_w, 3), dtype=np.uint8) * 255

        colors = [(255, 50, 50), (50, 180, 50)]
        zoom_col_indices = [i for i, l in enumerate(labels)
                           if l in ('GT', 'Baseline (No Adapter)', 'Ours (GeoTex-Adapter)')]

        for crop_idx, (region, color) in enumerate(zip(zoom_regions, colors)):
            for col_offset, col_i in enumerate(zoom_col_indices):
                x_base = col_i * (w + gap)
                # Use clean copies (no boxes drawn) for crop extraction
                crop = extract_crop(columns_clean[col_i], region, (zoom_size, zoom_size))
                crop = add_border(crop, width=border_width, color=color)
                crop_h, crop_w = crop.shape[:2]

                x_pos = x_base + crop_idx * (crop_with_border_size + 8)
                # Ensure we don't overflow
                y_end = min(2 + crop_h, zoom_row_h)
                x_end = min(x_pos + crop_w, main_w)
                actual_h = y_end - 2
                actual_w = x_end - x_pos
                if actual_h > 0 and actual_w > 0 and x_pos < main_w:
                    zoom_row[2:y_end, x_pos:x_end] = crop[:actual_h, :actual_w]

        # Combine
        final = np.ones((labeled.shape[0] + gap + zoom_row_h, main_w, 3), dtype=np.uint8) * 255
        final[:labeled.shape[0], :] = labeled
        final[labeled.shape[0]+gap:, :] = zoom_row
    else:
        final = labeled

    if output_path:
        Image.fromarray(final).save(output_path)

    return final


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate paper comparison figures")
    parser.add_argument('--input_dir', required=True,
                        help='Directory with quality_showcase or visualizations')
    parser.add_argument('--output_dir', required=True,
                        help='Output directory for paper figures')
    parser.add_argument('--objects', type=str, required=True,
                        help='Comma-separated object indices')
    parser.add_argument('--layout', default='standard_with_zooms',
                        choices=['standard', 'standard_with_zooms', 'extended', 'ablation'])
    parser.add_argument('--cell_width', type=int, default=256)
    parser.add_argument('--cell_height', type=int, default=384)
    parser.add_argument('--with_error', action='store_true',
                        help='Include error maps')
    parser.add_argument('--source', choices=['quality_showcase', 'eval_vis'],
                        default='quality_showcase',
                        help='Source format of input images')
    args = parser.parse_args()

    obj_indices = [int(x.strip()) for x in args.objects.split(',')]
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating paper figures for objects: {obj_indices}")
    print(f"Layout: {args.layout}")

    # Collect objects data
    objects_data = []

    for obj_idx in obj_indices:
        if args.source == 'quality_showcase':
            obj_dir = os.path.join(args.input_dir, f'obj_{obj_idx:03d}')
            if not os.path.exists(obj_dir):
                print(f"  WARNING: {obj_dir} not found, skipping")
                continue
            obj = {
                'gt': os.path.join(obj_dir, 'gt.png'),
                'baseline': os.path.join(obj_dir, 'baseline_no_adapter.png'),
                'ours': os.path.join(obj_dir, 'BEST_adapter.png'),
                'reference': os.path.join(obj_dir, 'reference.png'),
                'normal': os.path.join(obj_dir, 'normal.png'),
                'mask': os.path.join(obj_dir, 'mask.png'),
            }
            # Fallback: if BEST doesn't exist, try first adapter file
            if not os.path.exists(obj['ours']):
                adapter_files = sorted(Path(obj_dir).glob('adapter_*.png'))
                if adapter_files:
                    obj['ours'] = str(adapter_files[0])

        elif args.source == 'eval_vis':
            vis_dir = args.input_dir
            prefix = f'obj_{obj_idx:03d}'
            obj = {
                'gt': os.path.join(vis_dir, f'{prefix}_gt.png'),
                'baseline': os.path.join(vis_dir, f'{prefix}_original.png'),
                'ours': os.path.join(vis_dir, f'{prefix}_adapter_enhanced.png'),
                'mask': os.path.join(vis_dir, f'{prefix}_mask.png'),
            }
            # Fallback to non-enhanced
            if not os.path.exists(obj['ours']):
                obj['ours'] = os.path.join(vis_dir, f'{prefix}_adapter.png')

        objects_data.append(obj)

    if not objects_data:
        print("ERROR: No valid objects found!")
        return

    # Generate individual comparisons
    print("\n--- Individual comparisons ---")
    for obj_idx, obj in zip(obj_indices, objects_data):
        if not os.path.exists(str(obj.get('gt', ''))):
            continue
        out_path = os.path.join(args.output_dir, f'comparison_obj_{obj_idx:03d}.png')
        make_single_comparison(
            obj['gt'], obj['baseline'], obj['ours'],
            mask_path=obj.get('mask'),
            reference_path=obj.get('reference'),
            output_path=out_path,
            with_zooms=True,
            with_error=args.with_error,
        )
        print(f"  Saved: {out_path}")

    # Generate multi-row grid
    print("\n--- Multi-row grid ---")
    grid = make_comparison_grid(
        objects_data, layout=args.layout,
        cell_size=(args.cell_width, args.cell_height),
    )
    grid_path = os.path.join(args.output_dir, 'comparison_grid.png')
    Image.fromarray(grid).save(grid_path)
    print(f"  Saved: {grid_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"DONE. {len(objects_data)} objects processed.")
    print(f"Output directory: {args.output_dir}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
