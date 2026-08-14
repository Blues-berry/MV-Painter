"""Shared utilities for figure generation scripts."""
import os
from PIL import Image, ImageDraw, ImageFont


def get_font(size, bold=False):
    """Load system font with fallback."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def extract_view(img_path, col, row, view_size=256):
    """Extract a single view from a multi-view grid image.

    Args:
        img_path: Path to the grid image.
        col, row: Grid coordinates (0-based).
        view_size: Size of each view tile (default 256).
    """
    img = Image.open(img_path)
    x, y = col * view_size, row * view_size
    return img.crop((x, y, x + view_size, y + view_size))


def make_crop_comparison_figure(
    objects, methods, col_headers, border_colors, base_dir,
    output_png, output_pdf=None,
    crop_display_size=360, thumb_size=80,
    gap_inner=8, gap_col=12, gap_row=20,
    header_h=50, margin=30, border_width=3,
    header_font_size=24, target_width_inches=7.0,
):
    """Generate a crop-comparison figure (e.g., Fig 4 or Fig 6).

    Args:
        objects: list of dicts with keys 'id', 'view' (col, row), 'crop' (x1, y1, x2, y2).
        methods: list of method directory names (e.g., ['GT', 's_1.25']).
        col_headers: display names for each column.
        border_colors: list of RGB tuples, one per column.
        base_dir: Path to base directory containing method subdirs.
        output_png: output PNG path.
        output_pdf: optional output PDF path.
        crop_display_size: rendered size of the enlarged crop.
        thumb_size: rendered size of the thumbnail.
        gap_inner, gap_col, gap_row: spacing.
        header_h: height for column headers.
        margin: page margin.
        border_width: colored border width.
        header_font_size: font size for column headers.
        target_width_inches: target figure width for PDF DPI calculation.

    Returns:
        PIL Image of the generated figure.
    """
    from pathlib import Path
    base_dir = Path(base_dir)

    n_objs = len(objects)
    n_cols = len(methods)

    cell_w = crop_display_size
    cell_h = crop_display_size + gap_inner + thumb_size

    fig_w = margin * 2 + n_cols * cell_w + (n_cols - 1) * gap_col
    fig_h = margin + header_h + n_objs * cell_h + (n_objs - 1) * gap_row + margin

    fig = Image.new('RGB', (fig_w, fig_h), 'white')
    draw = ImageDraw.Draw(fig)

    font_header = get_font(header_font_size, bold=True)

    # Draw column headers
    for c, header in enumerate(col_headers):
        x_center = margin + c * (cell_w + gap_col) + cell_w // 2
        bbox = draw.textbbox((0, 0), header, font=font_header)
        tw = bbox[2] - bbox[0]
        color = border_colors[c]
        draw.text((x_center - tw // 2, margin + 5), header, fill=color, font=font_header)

    # Draw each object row
    bordered_size = crop_display_size + 2 * border_width
    for r, obj_info in enumerate(objects):
        obj_id = obj_info['id']
        view_col, view_row = obj_info['view']
        cx1, cy1, cx2, cy2 = obj_info['crop']

        y_base = margin + header_h + r * (cell_h + gap_row)

        for c, method in enumerate(methods):
            x_base = margin + c * (cell_w + gap_col)
            border_color = border_colors[c]

            # Load image and extract view
            img_path = base_dir / method / f'obj_{obj_id:04d}.png'
            view = extract_view(str(img_path), view_col, view_row)

            # Large crop (primary content)
            crop = view.crop((cx1, cy1, cx2, cy2))
            crop_resized = crop.resize((crop_display_size, crop_display_size), Image.LANCZOS)

            # Add colored border
            bordered = Image.new('RGB', (bordered_size, bordered_size), border_color)
            bordered.paste(crop_resized, (border_width, border_width))

            # Paste large crop (centered in cell)
            crop_x = x_base + (cell_w - bordered_size) // 2
            fig.paste(bordered, (crop_x, y_base))

            # Small thumbnail with crop indicator
            thumb = view.resize((thumb_size, thumb_size), Image.LANCZOS)
            thumb_draw = ImageDraw.Draw(thumb)

            scale = thumb_size / 256.0
            tx1 = int(cx1 * scale)
            ty1 = int(cy1 * scale)
            tx2 = int(cx2 * scale)
            ty2 = int(cy2 * scale)
            thumb_draw.rectangle([tx1, ty1, tx2, ty2], outline='red', width=2)

            # Paste thumbnail centered below crop
            thumb_x = x_base + (cell_w - thumb_size) // 2
            thumb_y = y_base + bordered_size + gap_inner
            fig.paste(thumb, (thumb_x, thumb_y))

    # Save outputs
    Path(output_png).parent.mkdir(parents=True, exist_ok=True)
    fig.save(str(output_png), quality=95, dpi=(300, 300))
    print(f'Saved PNG: {output_png} ({fig.size[0]}×{fig.size[1]})')

    if output_pdf:
        target_dpi = fig_w / target_width_inches
        fig_rgb = fig.convert('RGB')
        fig_rgb.save(str(output_pdf), 'PDF', resolution=target_dpi)
        print(f'Saved PDF: {output_pdf} (effective DPI: {target_dpi:.0f})')

    return fig
