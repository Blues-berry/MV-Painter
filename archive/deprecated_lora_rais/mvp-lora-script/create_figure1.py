"""
Generate Figure 1 for 6-2-sb paper:
Side-by-side comparison of bare pipeline vs correct pipeline (ControlNet+depth).
Shows the same LoRA checkpoints evaluated under both conditions.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BARE_DIR = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison'
FIXED_DIR = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison_fixed'
OUTPUT_DIR = '/4T/CXY/MV-Painter/output/paper_draft'

# Use d6a54278 as representative object (clear visual difference)
OBJ = 'd6a5427888b8413fbfcbcaad14353af8'
OBJ_SHORT = 'd6a54278'

CELL_W, CELL_H = 256, 256
HEADER_H = 40
LABEL_W = 160


def load_and_resize(path, size=(CELL_W, CELL_H)):
    if os.path.exists(path):
        img = Image.open(path).convert('RGB')
        return img.resize(size, Image.LANCZOS)
    return Image.new('RGB', size, (200, 200, 200))


def add_label(draw, x, y, text, font, fill=(0, 0, 0)):
    draw.text((x, y), text, fill=fill, font=font)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        font_small = font
        font_header = font

    # Layout: 3 rows (bare, fixed s=1.0, fixed s=0.25) × 3 cols (Original, Full, attn2)
    n_rows = 3
    n_cols = 3
    fig_w = LABEL_W + CELL_W * n_cols + 20
    fig_h = HEADER_H + (CELL_H + 50) * n_rows + 20

    fig = Image.new('RGB', (fig_w, fig_h), (255, 255, 255))
    draw = ImageDraw.Draw(fig)

    # Column headers
    col_labels = ['Original', 'Full LoRA', 'attn2-only']
    for j, label in enumerate(col_labels):
        x = LABEL_W + CELL_W * j + 10
        add_label(draw, x, 10, label, font_header)

    # Row data
    rows = [
        {
            'label': 'Bare pipeline\n(no depth)',
            'original': os.path.join(BARE_DIR, f'{OBJ}_original.png'),
            'full': os.path.join(BARE_DIR, f'{OBJ}_broken.png'),
            'attn2': os.path.join(BARE_DIR, f'{OBJ}_attn2only.png'),
            'psnr_full': '14.99 dB*',
            'psnr_attn2': '42.67 dB*',
        },
        {
            'label': 'Correct pipeline\n(ControlNet+depth)\nscale=1.0',
            'original': os.path.join(FIXED_DIR, 'scale_1.0', f'{OBJ}_original.png'),
            'full': os.path.join(FIXED_DIR, 'scale_1.0', f'{OBJ}_full_lora.png'),
            'attn2': os.path.join(FIXED_DIR, 'scale_1.0', f'{OBJ}_attn2only.png'),
            'psnr_full': '10.53 dB',
            'psnr_attn2': '7.10 dB',
        },
        {
            'label': 'Correct pipeline\n(ControlNet+depth)\nscale=0.25',
            'original': os.path.join(FIXED_DIR, 'scale_0.25', f'{OBJ}_original.png'),
            'full': os.path.join(FIXED_DIR, 'scale_0.25', f'{OBJ}_full_lora.png'),
            'attn2': os.path.join(FIXED_DIR, 'scale_0.25', f'{OBJ}_attn2only.png'),
            'psnr_full': '18.37 dB',
            'psnr_attn2': '16.72 dB',
        },
    ]

    for i, row in enumerate(rows):
        y_base = HEADER_H + i * (CELL_H + 50)

        # Row label (multi-line)
        for line_idx, line in enumerate(row['label'].split('\n')):
            add_label(draw, 5, y_base + 5 + line_idx * 18, line, font_small, fill=(80, 80, 80))

        # Images
        imgs = [
            load_and_resize(row['original']),
            load_and_resize(row['full']),
            load_and_resize(row['attn2']),
        ]
        for j, img in enumerate(imgs):
            x = LABEL_W + CELL_W * j
            fig.paste(img, (x, y_base))

        # PSNR labels under images (Original = reference, no PSNR)
        add_label(draw, LABEL_W + 5, y_base + CELL_H + 5, "(reference)", font_small, fill=(100, 100, 100))
        add_label(draw, LABEL_W + CELL_W + 5, y_base + CELL_H + 5, f"PSNR: {row['psnr_full']}", font_small, fill=(0, 100, 0))
        add_label(draw, LABEL_W + CELL_W * 2 + 5, y_base + CELL_H + 5, f"PSNR: {row['psnr_attn2']}", font_small, fill=(0, 100, 0))

    # Add figure caption
    caption_y = fig_h - 25
    add_label(draw, 10, caption_y,
              f"Figure 1: Object {OBJ_SHORT}. Top: bare pipeline (no ControlNet/depth); "
              f"Middle/Bottom: correct pipeline (ControlNet+depth, scale=1.0/0.25). "
              f"Note: 'Original' baseline differs between pipelines (*bare also had inconsistent scale).",
              font_small, fill=(100, 100, 100))

    save_path = os.path.join(OUTPUT_DIR, 'fig1_bare_vs_correct.png')
    fig.save(save_path, dpi=(300, 300))
    print(f"Saved to {save_path}")
    print(f"  Size: {fig.width}×{fig.height}")


if __name__ == '__main__':
    main()
