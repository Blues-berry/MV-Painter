"""
Figure 4 v2: C3 vs Uniform Adapter Scaling - Qualitative Comparison
Redesigned for paper quality:
- One clear view per cell at large size
- Proper magnified zoom insets with connector lines
- Zoom strip below each row for direct comparison
- High resolution output
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# Configuration
# ============================================================
BASE_DIR = '/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1'
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/paper_figures_final'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Objects (0-4 have all 3 conditions)
# Obj 2 = copper pan (best contrast), Obj 4 = furniture/chest, Obj 0 = humanoid figure
OBJECTS = [2, 4]  # Use 2 objects for cleaner figure

# Condition paths
DIRS = {
    'gt': lambda idx: os.path.join(BASE_DIR, 'C3_300obj/visualizations', f'obj_{idx:03d}_gt.png'),
    's125': lambda idx: os.path.join(BASE_DIR, 'scale_1p25_300obj/visualizations', f'obj_{idx:03d}_adapter.png'),
    's250': lambda idx: os.path.join(BASE_DIR, 'eval_300obj_scale_2p50/visualizations', f'obj_{idx:03d}_adapter.png'),
    'C3': lambda idx: os.path.join(BASE_DIR, 'C3_300obj/visualizations', f'obj_{idx:03d}_adapter.png'),
}

CONDITIONS = ['gt', 's125', 's250', 'C3']
COL_HEADERS = ['GT', r's = 1.25', r's = 2.50', 'C3 (Ours)']

# View selection: (col, row) in the 2x3 grid of 256x256 views
# Pick the most informative single view for each object
BEST_VIEW = {
    2: (0, 0),   # copper pan front view
    4: (0, 0),   # furniture front view
    0: (0, 0),   # humanoid front view  
    1: (0, 0),   # building front view
    3: (0, 0),   # organic shape front view
}

# Zoom crop regions (in 256x256 view coordinates): (x1, y1, x2, y2)
# Choose regions that show texture detail differences
ZOOM_CROP = {
    2: (50, 80, 190, 180),    # copper pan: surface area with texture detail
    4: (40, 60, 200, 160),    # furniture: panel/drawer area
    0: (70, 70, 190, 170),    # humanoid: torso area
    1: (50, 60, 200, 170),    # building: facade
    3: (60, 60, 196, 170),    # organic: center
}

# Output cell size (each view displayed at this size)
CELL_SIZE = 300  # pixels per cell
ZOOM_H = 120    # height of zoom strip
GAP = 4
HEADER_H = 40
ZOOM_BORDER = 3


def extract_view(img_path, view_pos):
    """Extract a single 256x256 view from the 2x3 grid (512x768 image)."""
    img = Image.open(img_path)
    col, row = view_pos
    x, y = col * 256, row * 256
    return img.crop((x, y, x + 256, y + 256))


def get_font(size, bold=False):
    """Try to load a system font."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_figure():
    n_objs = len(OBJECTS)
    n_cols = len(CONDITIONS)
    
    # Each row = main view row + zoom strip row
    row_h = CELL_SIZE + GAP + ZOOM_H  # main + gap + zoom
    
    # Figure dimensions
    fig_w = n_cols * CELL_SIZE + (n_cols - 1) * GAP + 60  # 30px margins each side
    fig_h = HEADER_H + n_objs * row_h + (n_objs - 1) * (GAP * 3) + 30  # extra spacing between objects
    
    fig = Image.new('RGB', (fig_w, fig_h), 'white')
    draw = ImageDraw.Draw(fig)
    
    font_header = get_font(20, bold=True)
    font_small = get_font(14, bold=False)
    
    # Column headers
    x_start = 30
    for c, header in enumerate(COL_HEADERS):
        x_center = x_start + c * (CELL_SIZE + GAP) + CELL_SIZE // 2
        bbox = draw.textbbox((0, 0), header, font=font_header)
        tw = bbox[2] - bbox[0]
        draw.text((x_center - tw // 2, 10), header, fill='black', font=font_header)
    
    # Draw each object row
    for r, obj_idx in enumerate(OBJECTS):
        y_base = HEADER_H + r * (row_h + GAP * 3)
        view_pos = BEST_VIEW[obj_idx]
        crop_region = ZOOM_CROP[obj_idx]
        
        zoom_crops = []  # collect zoom crops for this row
        
        for c, cond in enumerate(CONDITIONS):
            x = x_start + c * (CELL_SIZE + GAP)
            
            # Extract and resize view
            img_path = DIRS[cond](obj_idx)
            view = extract_view(img_path, view_pos)
            view_resized = view.resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)
            
            # Draw red rectangle on main view (zoom indicator)
            view_draw = ImageDraw.Draw(view_resized)
            # Scale crop region from 256x256 to CELL_SIZE x CELL_SIZE
            scale = CELL_SIZE / 256.0
            sx1 = int(crop_region[0] * scale)
            sy1 = int(crop_region[1] * scale)
            sx2 = int(crop_region[2] * scale)
            sy2 = int(crop_region[3] * scale)
            view_draw.rectangle([sx1, sy1, sx2, sy2], outline='red', width=2)
            
            fig.paste(view_resized, (x, y_base))
            
            # Extract zoom crop from original 256x256 view
            zoom = view.crop(crop_region)
            # Resize zoom to fill ZOOM_H
            crop_w = crop_region[2] - crop_region[0]
            crop_h = crop_region[3] - crop_region[1]
            zoom_aspect = crop_w / crop_h
            zoom_display_w = int(ZOOM_H * zoom_aspect)
            # Make all zoom crops the same width as CELL_SIZE for alignment
            zoom_resized = zoom.resize((CELL_SIZE, ZOOM_H), Image.LANCZOS)
            zoom_crops.append((zoom_resized, x))
        
        # Draw zoom strip
        y_zoom = y_base + CELL_SIZE + GAP
        for zoom_img, x in zoom_crops:
            # Add red border to zoom
            bordered = Image.new('RGB', (CELL_SIZE + 2*ZOOM_BORDER, ZOOM_H + 2*ZOOM_BORDER), 'red')
            bordered.paste(zoom_img, (ZOOM_BORDER, ZOOM_BORDER))
            fig.paste(bordered, (x - ZOOM_BORDER, y_zoom - ZOOM_BORDER))
    
    # Save
    out_path = os.path.join(OUTPUT_DIR, 'fig4_c3_comparison_v2.png')
    fig.save(out_path, quality=95, dpi=(300, 300))
    print(f'Saved: {out_path} ({fig.size[0]}x{fig.size[1]})')
    
    # 2x version for high-DPI
    fig_2x = fig.resize((fig_w * 2, fig_h * 2), Image.LANCZOS)
    out_2x = os.path.join(OUTPUT_DIR, 'fig4_c3_comparison_v2_2x.png')
    fig_2x.save(out_2x, quality=95, dpi=(600, 600))
    print(f'Saved 2x: {out_2x} ({fig_2x.size[0]}x{fig_2x.size[1]})')


if __name__ == '__main__':
    make_figure()
