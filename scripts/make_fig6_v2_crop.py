"""
Figure 6 v2: C3 (TCAS) vs Uniform Adapter Scaling - Qualitative Comparison
Design: Large crops as primary content + small thumbnail showing crop location.
Layout: 4 columns (GT, s=1.25, s=2.50, C3) × 2-3 objects, figure (single-column width)

Shows that C3 preserves texture like s=1.25 while maintaining geometric correction like s=2.50.
"""
from pathlib import Path
from fig_utils import make_crop_comparison_figure

# ============================================================
# Configuration
# ============================================================
BASE_DIR = Path('/4T/CXY/MV-Painter/mvpoutput/revision_clipiqa/images')
OUTPUT_DIR = Path('/4T/CXY/MV-Painter/final/output/figures')

# --- Object selection (best C3 advantage over s2.50 with good foreground) ---
# Different objects from Fig4 (which uses 3, 4, 12) to avoid redundancy
OBJECTS = [
    {
        'id': 1,
        'view': (0, 2),       # row=2, col=0 (bottom-left): fg=99% crop
        'crop': (60, 70, 190, 200),
    },
    {
        'id': 15,
        'view': (1, 0),       # row=0, col=1 (top-right): fg=94%
        'crop': (50, 60, 180, 190),
    },
    {
        'id': 7,
        'view': (0, 2),       # row=2, col=0 (bottom-left): fg=73%
        'crop': (60, 70, 190, 200),
    },
]

# --- Layout ---
COL_HEADERS = ['GT', 's = 1.25', 's = 2.50', 'C3 (Ours)']
METHODS = ['GT', 's_1.25', 's_2.50', 'C3_TCAS']

# Colors
COLOR_GT = (80, 80, 80)
COLOR_CONSERVATIVE = (60, 160, 60)
COLOR_AGGRESSIVE = (200, 50, 50)
COLOR_C3 = (220, 140, 20)
BORDER_COLORS = [COLOR_GT, COLOR_CONSERVATIVE, COLOR_AGGRESSIVE, COLOR_C3]


if __name__ == '__main__':
    fig = make_crop_comparison_figure(
        objects=OBJECTS,
        methods=METHODS,
        col_headers=COL_HEADERS,
        border_colors=BORDER_COLORS,
        base_dir=BASE_DIR,
        output_png=OUTPUT_DIR / 'fig6.png',
        output_pdf=OUTPUT_DIR / 'fig6.pdf',
        # Smaller layout for single-column figure
        crop_display_size=220,
        thumb_size=55,
        gap_inner=6,
        gap_col=8,
        gap_row=16,
        header_h=40,
        margin=20,
        header_font_size=18,
        target_width_inches=3.4,
    )
    print(f'\nFigure 6 generated: {fig.size[0]}×{fig.size[1]} px')
    print(f'Objects used: {[o["id"] for o in OBJECTS]}')
