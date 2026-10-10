#!/usr/bin/env python3
"""Replace unsupported interpretive labels on the historical C3 probe plot."""
from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas


FIGURE = Path(__file__).resolve().parents[1] / "figures/fig7_c3_development.pdf"


def run(args: list[str]) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def page_size(pdf: Path) -> tuple[float, float]:
    info = run(["pdfinfo", str(pdf)])
    match = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts$", info, re.MULTILINE)
    if not match or not re.search(r"^Pages:\s+1$", info, re.MULTILINE):
        raise ValueError(f"Expected a single-page PDF with a readable size: {pdf}")
    return float(match.group(1)), float(match.group(2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=FIGURE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.input.resolve()
    target = args.output.resolve() if args.output else source
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="c3_probe_figure_") as temporary:
        work = Path(temporary)
        prefix = work / "plot"
        run(["pdfimages", "-png", str(source), str(prefix)])
        images = list(work.glob("plot-*.png"))
        if len(images) != 1:
            raise ValueError(f"Expected one full-page plot image, found {len(images)}")

        image_path = images[0]
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        page_width, page_height = page_size(source)
        if (width, height) != (2651, 1899):
            raise ValueError(f"Label masks are defined for the source raster size, got {(width, height)}")
        scale_x = page_width / width
        scale_y = page_height / height

        # The raster contains the original chart, including its historical labels.
        # These masks avoid all plotted marks, axes, gridlines, and tick labels.
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, 99), fill="white")
        draw.rectangle((0, 100, 104, 1680), fill="white")
        draw.rectangle((0, 1790, width, height), fill="white")
        image.save(image_path, format="PNG")

        temporary_pdf = work / "relabelled.pdf"
        pdf = canvas.Canvas(str(temporary_pdf), pagesize=(page_width, page_height))
        pdf.drawImage(str(image_path), 0, 0, width=page_width, height=page_height)

        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Times-Bold", 11.5)
        pdf.drawCentredString(
            page_width / 2,
            page_height - 65 * scale_y,
            "C3 Development Probe: 17 Schedule Variants",
        )

        pdf.setFont("Times-Roman", 10.2)
        pdf.drawCentredString(page_width / 2, 17 * scale_y, "FG-SSIM difference")

        pdf.saveState()
        pdf.translate(48 * scale_x + 1.5, (height - 890) * scale_y)
        pdf.rotate(90)
        pdf.setFont("Times-Roman", 10.2)
        pdf.drawCentredString(0, -3.0, "Laplacian variance difference")
        pdf.restoreState()
        pdf.showPage()
        pdf.save()

        target_temp = target.with_suffix(target.suffix + ".tmp")
        target_temp.write_bytes(temporary_pdf.read_bytes())
        target_temp.replace(target)


if __name__ == "__main__":
    main()
