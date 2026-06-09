"""
Create paper main figure v2 with width >= 3000px.
Shows three-way comparison: Original / Crashed LoRA / Working LoRA
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


def create_paper_figure(output_path, width=3200):
    """Create a wide paper figure with three-way comparison."""

    # Select 3 representative objects
    objects = [
        ('d6a5427888b8413fbfcbcaad14353af8', 'Object 1'),
        ('aa82baf218104070a932dee9a1db61ce', 'Object 2'),
        ('e3f35d4cfbb14410bf96a4ffa28235a1', 'Object 3'),
    ]

    base_dir = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison'

    # Load images
    rows = []
    for obj_id, label in objects:
        cond_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
        orig_path = f'{base_dir}/{obj_id}_original.png'
        broken_path = f'{base_dir}/{obj_id}_broken.png'
        working_path = f'{base_dir}/{obj_id}_attn2only.png'

        if all(os.path.exists(p) for p in [cond_path, orig_path, broken_path, working_path]):
            rows.append({
                'cond': Image.open(cond_path).convert('RGBA'),
                'orig': Image.open(orig_path),
                'broken': Image.open(broken_path),
                'working': Image.open(working_path),
                'label': label,
                'id': obj_id,
            })

    if not rows:
        print("No valid images found!")
        return

    # Layout: 3 rows (objects) x 4 columns (cond, orig, broken, working)
    n_rows = len(rows)
    n_cols = 4

    # Calculate dimensions
    cell_width = width // n_cols
    cell_height = cell_width  # Square cells
    header_height = 80
    footer_height = 40
    total_height = header_height + n_rows * cell_height + footer_height

    # Create figure
    fig = Image.new('RGB', (width, total_height), (255, 255, 255))
    draw = ImageDraw.Draw(fig)

    # Try to load a font
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Draw header
    headers = ['Condition', 'Original', 'Crashed LoRA\n(attn1+attn2)', 'Working LoRA\n(attn2-only)']
    config_labels = ['Input', 'A', 'B', 'C']
    for i, header in enumerate(headers):
        x = i * cell_width + cell_width // 2
        # Split multiline text
        lines = header.split('\n')
        for j, line in enumerate(lines):
            draw.text((x, 10 + j * 20), line, fill='black', font=font_large, anchor='mt')
        draw.text((x, 35 + len(lines) * 20), f'Config {config_labels[i]}', fill='gray', font=font_small, anchor='mt')

    # Draw images
    for row_idx, row in enumerate(rows):
        y = header_height + row_idx * cell_height

        # Row label
        draw.text((10, y + cell_height // 2), row['label'], fill='black', font=font_medium, anchor='lm')

        # Resize and paste images
        images = [row['cond'], row['orig'], row['broken'], row['working']]
        for col_idx, img in enumerate(images):
            x = col_idx * cell_width
            img_resized = img.resize((cell_width - 4, cell_height - 4), Image.LANCZOS)
            fig.paste(img_resized, (x + 2, y + 2))

    # Draw footer
    draw.text((width // 2, total_height - 25),
              'MV-Painter LoRA Fine-Tuning: attn2-only preserves reference attention',
              fill='gray', font=font_medium, anchor='mm')

    # Save
    fig.save(output_path, quality=95)
    print(f"Paper figure saved to {output_path}")
    print(f"Dimensions: {fig.size[0]} x {fig.size[1]} px")


if __name__ == '__main__':
    output_path = '/4T/CXY/MV-Painter/mvpoutput/paper_assets/paper_main_figure_v2.png'
    create_paper_figure(output_path, width=3200)
