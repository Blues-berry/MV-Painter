"""
Figure 6 v2: C3 (TCAS) vs Uniform Adapter Scaling - Qualitative Comparison
Design: Large crops as primary content + small thumbnail showing crop location.
Layout: 4 columns (GT, s=1.25, s=2.50, C3) × 2-3 objects, figure (single-column width)

Shows that C3 preserves texture like s=1.25 while maintaining geometric correction like s=2.50.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# ============================================================
# Configuration
# ============================================================
BASE_DIR = Path('/4T/CXY/MV-Painter/mvpoutput/revision_clipiqa/images')
OUTPUT_DIR = Path('/4T/CXY/MV-Painter/final/output/figures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Object selection (best C3 advantage over s2.50 with good foreground) ---
# Different objects from Fig4 (which uses 3, 4, 12) to avoid redundancy
# Selected for: fg>60%, C3 advantage, distinct from fig4 objects
OBJECTS = [
    {
        'id': 1,
        'view': (0, 2),       # row=2, col=0 (bottom-left): fg=99% crop
        'crop': (60, 70, 190, 200),   # 130x130
    },
    {
        'id': 15,
        'view': (1, 0),       # row=0, col=1 (top-right): fg=94%
        'crop': (50, 60, 180, 190),   # 130x130
    },
    {
        'id': 7,
        'view': (0, 2),       # row=2, col=0 (bottom-left): fg=73%
        'crop': (60, 70, 190, 200),   # 130x130 - body + harness area
    },
]

# --- Layout constants ---
# Target figure width: ~3.4 inches at 300 DPI ≈ 1020 px
# With 4 columns this is tight, use smaller crops
CROP_DISPLAY_SIZE = 220      # Crop display size (px)
THUMB_SIZE = 55              # Small thumbnail size
GAP_INNER = 6               # Gap between crop and thumbnail
GAP_COL = 8                 # Gap between columns
GAP_ROW = 16                # Gap between object rows
HEADER_H = 40               # Column header height
MARGIN = 20                 # Page margin
BORDER_WIDTH = 3            # Colored border width

# Column configuration
COL_HEADERS = ['GT', 's = 1.25', 's = 2.50', 'C3 (Ours)']
METHODS = ['GT', 's_1.25', 's_2.50', 'C3_TCAS']

# Colors
COLOR_GT = (80, 80, 80)               # Dark gray
COLOR_CONSERVATIVE = (60, 160, 60)    # Green for s=1.25
COLOR_AGGRESSIVE = (200, 50, 50)      # Red for s=2.50
COLOR_C3 = (220, 140, 20)            # Orange for C3
BORDER_COLORS = [COLOR_GT, COLOR_CONSERVATIVE, COLOR_AGGRESSIVE, COLOR_C3]


def get_font(size, bold=False):
    """Load system font."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def extract_view(img_path, col, row):
    """Extract a single 256×256 view from the 2×3 grid (512×768 image)."""
    img = Image.open(img_path)
    x, y = col * 256, row * 256
    return img.crop((x, y, x + 256, y + 256))


def make_figure():
    n_objs = len(OBJECTS)
    n_cols = len(METHODS)

    # Calculate total figure dimensions
    cell_w = CROP_DISPLAY_SIZE  # Main content = large crop
    cell_h = CROP_DISPLAY_SIZE + GAP_INNER + THUMB_SIZE  # crop + gap + thumb

    fig_w = MARGIN * 2 + n_cols * cell_w + (n_cols - 1) * GAP_COL
    fig_h = MARGIN + HEADER_H + n_objs * cell_h + (n_objs - 1) * GAP_ROW + MARGIN

    fig = Image.new('RGB', (fig_w, fig_h), 'white')
    draw = ImageDraw.Draw(fig)

    font_header = get_font(18, bold=True)
    font_label = get_font(12, bold=False)

    # --- Draw column headers ---
    for c, header in enumerate(COL_HEADERS):
        x_center = MARGIN + c * (cell_w + GAP_COL) + cell_w // 2
        bbox = draw.textbbox((0, 0), header, font=font_header)
        tw = bbox[2] - bbox[0]
        color = BORDER_COLORS[c]
        draw.text((x_center - tw // 2, MARGIN + 5), header, fill=color, font=font_header)

    # --- Draw each object row ---
    for r, obj_info in enumerate(OBJECTS):
        obj_id = obj_info['id']
        view_col, view_row = obj_info['view']
        cx1, cy1, cx2, cy2 = obj_info['crop']

        y_base = MARGIN + HEADER_H + r * (cell_h + GAP_ROW)

        for c, method in enumerate(METHODS):
            x_base = MARGIN + c * (cell_w + GAP_COL)
            border_color = BORDER_COLORS[c]

            # Load image and extract view
            img_path = BASE_DIR / method / f'obj_{obj_id:04d}.png'
            view = extract_view(str(img_path), view_col, view_row)

            # --- Large crop (primary content) ---
            crop = view.crop((cx1, cy1, cx2, cy2))
            crop_resized = crop.resize((CROP_DISPLAY_SIZE, CROP_DISPLAY_SIZE), Image.LANCZOS)

            # Add colored border
            bordered_size = CROP_DISPLAY_SIZE + 2 * BORDER_WIDTH
            bordered = Image.new('RGB', (bordered_size, bordered_size), border_color)
            bordered.paste(crop_resized, (BORDER_WIDTH, BORDER_WIDTH))

            # Paste large crop
            crop_x = x_base + (cell_w - bordered_size) // 2
            fig.paste(bordered, (crop_x, y_base))

            # --- Small thumbnail with crop indicator ---
            thumb = view.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            thumb_draw = ImageDraw.Draw(thumb)

            # Draw red rectangle showing crop region
            scale = THUMB_SIZE / 256.0
            tx1 = int(cx1 * scale)
            ty1 = int(cy1 * scale)
            tx2 = int(cx2 * scale)
            ty2 = int(cy2 * scale)
            thumb_draw.rectangle([tx1, ty1, tx2, ty2], outline='red', width=1)

            # Paste thumbnail centered below crop
            thumb_x = x_base + (cell_w - THUMB_SIZE) // 2
            thumb_y = y_base + bordered_size + GAP_INNER
            fig.paste(thumb, (thumb_x, thumb_y))

    # --- Save outputs ---
    # PNG for preview
    png_path = OUTPUT_DIR / 'fig6.png'
    fig.save(str(png_path), quality=95, dpi=(300, 300))
    print(f'Saved PNG: {png_path} ({fig.size[0]}×{fig.size[1]})')

    # PDF (single column = ~3.4 inches)
    target_dpi = fig_w / 3.4
    pdf_path = OUTPUT_DIR / 'fig6.pdf'
    fig_rgb = fig.convert('RGB')
    fig_rgb.save(str(pdf_path), 'PDF', resolution=target_dpi)
    print(f'Saved PDF: {pdf_path} (effective DPI: {target_dpi:.0f})')

    return fig


if __name__ == '__main__':
    fig = make_figure()
    print(f'\nFigure 6 generated: {fig.size[0]}×{fig.size[1]} px')
    print(f'Objects used: {[o["id"] for o in OBJECTS]}')
