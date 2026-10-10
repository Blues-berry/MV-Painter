#!/usr/bin/env python3
"""Build an internal side-by-side review of the 01549 and Fresh C figure layouts."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


SCRIPT_PATH = Path(__file__).resolve()
ROOT = next(
    (parent for parent in SCRIPT_PATH.parents if (parent / "1008" / "manuscript" / "source_01549").is_dir()),
    None,
)
if ROOT is None:
    raise RuntimeError("Could not locate the repository's authenticated 01549 source directory")
REVISION = ROOT / "1008" / "manuscript" / "revision_01549_restored"
ORIGINAL = ROOT / "1008" / "manuscript" / "source_01549"
FIGURES = REVISION / "figures"
AUDITS = ROOT / "1008" / "audits"


def rasterize(pdf: Path, destination: Path) -> Path:
    prefix = destination.with_suffix("")
    subprocess.run(
        ["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-png", "-r", "180", str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return prefix.with_suffix(".png")


def draw_fit(pdf: canvas.Canvas, image_path: Path, x: float, y: float, w: float, h: float) -> None:
    image = ImageReader(str(image_path))
    iw, ih = image.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    pdf.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, width=dw, height=dh, preserveAspectRatio=True, mask="auto")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=AUDITS / "01549_fig4_fig6_vs_fresh_c_layout_review_20261009.pdf",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    pairs = [
        ("Original 01549 Fig. 4", ORIGINAL / "fig4.pdf", "Fresh C replacement for Fig. 4", FIGURES / "fig4_freshc_context_roi.pdf"),
        ("Original 01549 Fig. 6", ORIGINAL / "fig6.pdf", "Fresh C replacement for Fig. 6 (current Fig. 5)", FIGURES / "fig5_freshc_context_roi.pdf"),
    ]

    page_size = (18 * inch, 11.7 * inch)
    with tempfile.TemporaryDirectory(prefix="figure-layout-review-") as temp_dir:
        temp = Path(temp_dir)
        rasters = []
        for index, (old_label, old_pdf, new_label, new_pdf) in enumerate(pairs):
            rasters.append((old_label, rasterize(old_pdf, temp / f"old-{index}.png"), new_label, rasterize(new_pdf, temp / f"new-{index}.png")))

        output = canvas.Canvas(str(args.output), pagesize=page_size, pageCompression=1)
        page_width, page_height = page_size
        margin = 0.38 * inch
        gap = 0.30 * inch
        panel_width = (page_width - 2 * margin - gap) / 2
        image_y = 1.05 * inch
        image_height = page_height - 2.0 * inch
        for old_label, old_img, new_label, new_img in rasters:
            output.setFont("Helvetica-Bold", 16)
            output.drawCentredString(page_width / 2, page_height - 0.52 * inch, "Figure layout review — internal author comparison")
            output.setFont("Helvetica-Bold", 12)
            output.drawCentredString(margin + panel_width / 2, page_height - 0.90 * inch, old_label)
            output.drawCentredString(margin + panel_width + gap + panel_width / 2, page_height - 0.90 * inch, new_label)
            draw_fit(output, old_img, margin, image_y, panel_width, image_height)
            draw_fit(output, new_img, margin + panel_width + gap, image_y, panel_width, image_height)
            output.setFont("Helvetica", 9)
            note = "Original pixels shown at preserved aspect ratio; Fresh C panels are rebuilt from saved RGB outputs with one shared ROI per object."
            output.drawCentredString(page_width / 2, 0.46 * inch, note)
            output.showPage()
        output.save()


if __name__ == "__main__":
    main()
