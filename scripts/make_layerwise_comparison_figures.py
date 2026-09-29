"""Build compact, paper-ready layer-wise visual comparison panels.

The panels use the already completed seed-42 development renders. They are
visual evidence only; all numerical claims remain based on the paired CSV and
bootstrap summary. No inference is run by this script.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data/train_data/rendered_full"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
PRED_ROOT = Path("/4T/tmp/mvpainter-layer-lhl-ablation/seed42/predictions")
OUT_ROOT = ROOT / "final/round2/coordination/layer_lhl_v1"
VIEWS = [0, 15, 12, 16, 13, 14]
METHOD_DIRS = {
    "fixed-low": "fixed_low",
    "C3/LHL": "c3_lhl",
    "layer-fixed-low": "layer_fixed_low",
    "layer-fixed-mean": "layer_fixed_mean",
    "layer-LHL": "layer_lhl",
    "layer-LLH": "layer_llh",
}


def font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tile(images, size=160):
    canvas = Image.new("RGB", (size * 3, size * 2), "white")
    for i, image in enumerate(images):
        image = image.convert("RGBA").resize((size, size))
        if image.getbands()[-1] == "A":
            bg = Image.new("RGBA", image.size, "white")
            bg.alpha_composite(image)
            image = bg.convert("RGB")
        else:
            image = image.convert("RGB")
        row, col = divmod(i, 3)
        canvas.paste(image, (col * size, row * size))
    return canvas


def gt_grid(uid, size=160):
    return tile([Image.open(DATA_ROOT / uid / "image" / f"{view:03d}.png") for view in VIEWS], size)


def prediction_grid(method, idx, size=160):
    path = PRED_ROOT / METHOD_DIRS[method] / f"obj_{idx:04d}.png"
    if not path.exists():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGB").resize((size * 3, size * 2))


def make_panel(name, indices, methods, title):
    objects = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    cell_w, cell_h, label_h, row_gap = 480, 320, 44, 26
    left = 12
    width = left * 2 + len(methods) * cell_w + (len(methods) - 1) * 8
    height = 54 + len(indices) * (label_h + cell_h + row_gap)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((left, 10), title, fill="black", font=font(26))
    header_font = font(20)
    small_font = font(18)

    for col, method in enumerate(methods):
        x = left + col * (cell_w + 8)
        draw.text((x + 8, 38), method, fill="black", font=header_font)

    for row, idx in enumerate(indices):
        y = 78 + row * (label_h + cell_h + row_gap)
        uid = objects[idx]
        for col, method in enumerate(methods):
            x = left + col * (cell_w + 8)
            grid = gt_grid(uid) if method == "GT" else prediction_grid(method, idx)
            canvas.paste(grid, (x, y + label_h))
            draw.rectangle((x, y + label_h, x + cell_w - 1, y + label_h + cell_h - 1), outline="#bbbbbb")
        draw.text((left, y + 2), f"development object {idx:02d}  ({uid[:8]}…)", fill="#333333", font=small_font)

    output = OUT_ROOT / name
    canvas.save(output, optimize=True)
    print(f"saved {output} {canvas.size}")


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    make_panel(
        "layerwise_visual_success_panel.png",
        [0],
        ["GT", "fixed-low", "C3/LHL", "layer-LHL"],
        "Representative foreground/detail comparison",
    )
    make_panel(
        "layerwise_visual_tradeoff_panel.png",
        [1],
        ["GT", "layer-fixed-low", "layer-fixed-mean", "layer-LHL", "layer-LLH"],
        "Counterexample: temporal schedule remains metric-dependent",
    )


if __name__ == "__main__":
    main()
