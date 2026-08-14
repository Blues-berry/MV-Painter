"""
Figure 4 v3: Texture Degradation Under Different Adapter Scales
Design: Large crops as primary content + small thumbnail showing crop location.
Layout: 3 columns (GT, s=1.25, s=2.50) × 3 objects, figure* (double-column width)

Key principle: texture flattening should be immediately visible without squinting.
"""
from pathlib import Path
from fig_utils import make_crop_comparison_figure

# ============================================================
# Configuration
# ============================================================
BASE_DIR = Path('/4T/CXY/MV-Painter/mvpoutput/revision_clipiqa/images')
OUTPUT_DIR = Path('/4T/CXY/MV-Painter/final/output/figures')

# --- Object selection (based on CLIP-IQA flattening + foreground coverage) ---
OBJECTS = [
    {
        'id': 4,
        'view': (0, 0),       # front view: antique potion chest, leather + brass studs
        'crop': (48, 100, 198, 240),  # brass studs, diamond ornament, leather grain (fg=63%)
    },
    {
        'id': 3,
        'view': (0, 0),       # front view: classical stone bust sculpture
        'crop': (70, 50, 200, 185),   # face detail, veil edges, necklace (fg=71%)
    },
    {
        'id': 12,
        'view': (1, 0),       # row=0, col=1: highest flattening with good fg=92%
        'crop': (70, 60, 200, 190),   # main surface area
    },
]

# --- Layout ---
COL_HEADERS = ['GT', 's = 1.25', 's = 2.50']
METHODS = ['GT', 's_1.25', 's_2.50']

# Colors
COLOR_GT = (80, 80, 80)
COLOR_CONSERVATIVE = (60, 160, 60)
COLOR_AGGRESSIVE = (200, 50, 50)
BORDER_COLORS = [COLOR_GT, COLOR_CONSERVATIVE, COLOR_AGGRESSIVE]


if __name__ == '__main__':
    fig = make_crop_comparison_figure(
        objects=OBJECTS,
        methods=METHODS,
        col_headers=COL_HEADERS,
        border_colors=BORDER_COLORS,
        base_dir=BASE_DIR,
        output_png=OUTPUT_DIR / 'fig4.png',
        output_pdf=OUTPUT_DIR / 'fig4.pdf',
        header_font_size=24,
    )
    print(f'\nFigure 4 generated: {fig.size[0]}×{fig.size[1]} px')
    print(f'Objects used: {[o["id"] for o in OBJECTS]}')
