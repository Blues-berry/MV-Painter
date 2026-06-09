"""Create a single combined comparison figure for all test samples."""
import os
from PIL import Image, ImageDraw, ImageFont

FIGURES_DIR = 'comparison_figures'
OUTPUT = 'comparison_figures/all_samples_comparison.png'

def get_font(size=20):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

# Load all comparison figures
figures = []
for f in sorted(os.listdir(FIGURES_DIR)):
    if f.startswith('comparison_') and f.endswith('.png') and f != 'all_samples_comparison.png':
        img = Image.open(os.path.join(FIGURES_DIR, f))
        figures.append(img)

if not figures:
    print('No figures found!')
    exit(1)

# Stack vertically with titles
font = get_font(20)
margin = 10
title_h = 40
sample_w = figures[0].width
sample_h = figures[0].height

# Add title at top
title_text = 'MVPainter LoRA Comparison: Input | Zero-shot | LoRA-r4 | LoRA-r8'
canvas_w = sample_w
canvas_h = title_h + len(figures) * (sample_h + margin) + margin

canvas = Image.new('RGB', (canvas_w, canvas_h), (240, 240, 240))
draw = ImageDraw.Draw(canvas)
draw.text((margin, 8), title_text, fill=(0, 0, 0), font=font)

for i, fig in enumerate(figures):
    y = title_h + margin + i * (sample_h + margin)
    canvas.paste(fig, (margin, y))

canvas.save(OUTPUT, quality=95)
print(f'Combined figure: {OUTPUT} ({canvas.size})')
