"""
Figure 4: C3 vs Uniform Adapter Scaling Qualitative Comparison

Layout:
  Columns: GT | s=1.25 (Conservative) | s=2.50 (Aggressive) | C3 (Ours)
  Rows: 2-3 objects (different from main comparison figure)
  
  Each cell shows a single representative view from the 6-view output.
  Red boxes highlight regions where s=2.50 shows texture loss that C3 avoids.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================================
# Configuration
# ============================================================
BASE_DIR = '/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1'
OUTPUT_DIR = '/4T/CXY/MV-Painter/mvpoutput/paper_figures_final'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Objects to use (different from main comparison figure which uses 32,41,43,56,72,79,106,209)
OBJECTS = [2, 1, 4]  # copper pan, building, furniture

# Directories for each condition
DIRS = {
    'gt': lambda obj_idx: os.path.join(BASE_DIR, 'C3_300obj/visualizations', f'obj_{obj_idx:03d}_gt.png'),
    's125': lambda obj_idx: os.path.join(BASE_DIR, 'scale_1p25_300obj/visualizations', f'obj_{obj_idx:03d}_adapter.png'),
    's250': lambda obj_idx: os.path.join(BASE_DIR, 'eval_300obj_scale_2p50/visualizations', f'obj_{obj_idx:03d}_adapter.png'),
    'C3': lambda obj_idx: os.path.join(BASE_DIR, 'C3_300obj/visualizations', f'obj_{obj_idx:03d}_adapter.png'),
}

# Column headers
COL_HEADERS = ['GT', 's = 1.25', 's = 2.50', 'C3 (Ours)']
CONDITIONS = ['gt', 's125', 's250', 'C3']

# Each source image is 512x768 (6 views in a 2x3 grid, each 256x256)
# We'll extract specific views to show the most informative angle
# View layout in 512x768 image: 2 columns x 3 rows, each cell 256x256
VIEW_POSITIONS = {
    # (col, row) -> (x, y) top-left
    (0, 0): (0, 0),      # view 0: front
    (1, 0): (256, 0),    # view 1: right-front
    (0, 1): (0, 256),    # view 2: right
    (1, 1): (256, 256),  # view 3: back
    (0, 2): (0, 512),    # view 4: left
    (1, 2): (256, 512),  # view 5: top
}

# Which view to show for each object (pick most informative)
# After seeing the images: 512x768 = 2col x 3row of 256x256 views
BEST_VIEWS = {
    2: [(0, 0), (0, 1)],  # copper pan: front + side (show interior + exterior)
    1: [(0, 0), (1, 0)],  # building: front angles
    4: [(0, 0), (1, 1)],  # furniture: front + different angle
}

# Zoom regions for red boxes (relative to 256x256 view, x1,y1,x2,y2)
# These highlight texture flattening in s=2.50
ZOOM_REGIONS = {
    2: (60, 60, 200, 180),    # copper pan: interior/surface area
    1: (40, 80, 220, 200),    # building: facade detail
    4: (50, 50, 210, 180),    # furniture: panel/drawer area
}


def extract_view(img_path, view_pos):
    """Extract a single 256x256 view from the 6-view grid."""
    img = Image.open(img_path)
    col, row = view_pos
    x, y = col * 256, row * 256
    return img.crop((x, y, x + 256, y + 256))


def extract_two_views(img_path, view_positions):
    """Extract two views and stack them horizontally."""
    views = []
    for vp in view_positions:
        views.append(extract_view(img_path, vp))
    # Stack horizontally
    combined = Image.new('RGB', (512, 256), 'white')
    combined.paste(views[0], (0, 0))
    combined.paste(views[1], (256, 0))
    return combined


def add_zoom_inset(img, region, inset_size=100, border_width=2, border_color='red'):
    """Add a zoom inset to the image showing the highlighted region."""
    x1, y1, x2, y2 = region
    draw = ImageDraw.Draw(img)
    
    # Draw red box on original
    draw.rectangle([x1, y1, x2, y2], outline=border_color, width=border_width)
    
    # Extract and zoom the region
    cropped = img.crop((x1, y1, x2, y2))
    zoomed = cropped.resize((inset_size, inset_size), Image.LANCZOS)
    
    # Place zoomed inset at bottom-right
    inset_x = img.width - inset_size - 5
    inset_y = img.height - inset_size - 5
    
    # Add border to inset
    bordered = Image.new('RGB', (inset_size + 2*border_width, inset_size + 2*border_width), border_color)
    bordered.paste(zoomed, (border_width, border_width))
    
    img.paste(bordered, (inset_x - border_width, inset_y - border_width))
    return img


def make_figure():
    """Create the full comparison figure."""
    # Cell size: 512x256 (two views side by side)
    cell_w, cell_h = 512, 256
    
    # Layout
    n_rows = len(OBJECTS)
    n_cols = len(CONDITIONS)
    
    # Margins and header
    header_h = 50
    row_label_w = 0  # No row labels needed
    gap = 4
    
    # Total size
    total_w = row_label_w + n_cols * cell_w + (n_cols - 1) * gap + 40
    total_h = header_h + n_rows * cell_h + (n_rows - 1) * gap + 40
    
    fig = Image.new('RGB', (total_w, total_h), 'white')
    draw = ImageDraw.Draw(fig)
    
    # Try to get a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # Draw column headers
    for c, header in enumerate(COL_HEADERS):
        x = row_label_w + 20 + c * (cell_w + gap) + cell_w // 2
        bbox = draw.textbbox((0, 0), header, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((x - text_w // 2, 15), header, fill='black', font=font)
    
    # Draw cells
    for r, obj_idx in enumerate(OBJECTS):
        views = BEST_VIEWS[obj_idx]
        zoom = ZOOM_REGIONS[obj_idx]
        
        for c, cond in enumerate(CONDITIONS):
            img_path = DIRS[cond](obj_idx)
            
            # Extract two views
            cell_img = extract_two_views(img_path, views)
            
            # Add zoom inset for non-GT conditions
            if cond != 'gt':
                # Scale zoom region for the combined view (left half)
                cell_img = add_zoom_inset(cell_img, zoom, inset_size=90, border_width=2)
            
            # Paste into grid
            x = row_label_w + 20 + c * (cell_w + gap)
            y = header_h + r * (cell_h + gap)
            fig.paste(cell_img, (x, y))
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'fig4_c3_vs_scaling.png')
    fig.save(output_path, quality=95)
    print(f'Saved: {output_path} ({fig.size[0]}x{fig.size[1]})')
    
    # Also save a higher-res version
    fig_hr = fig.resize((total_w * 2, total_h * 2), Image.LANCZOS)
    output_path_hr = os.path.join(OUTPUT_DIR, 'fig4_c3_vs_scaling_2x.png')
    fig_hr.save(output_path_hr, quality=95)
    print(f'Saved 2x: {output_path_hr} ({fig_hr.size[0]}x{fig_hr.size[1]})')


if __name__ == '__main__':
    make_figure()
