"""Rebuild V5 Figures 2 and 3 from hash-verified display assets.

Only figure text and spacing are edited. Source display pixels are embedded
unchanged after their recorded SHA-256 hashes are checked.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("V5Sans", FONT_PATH))


def draw_text(c: canvas.Canvas, x: float, y: float, value: str, size: float = 8) -> None:
    c.setFont("V5Sans", size)
    c.setFillColorRGB(0.10, 0.15, 0.22)
    c.drawString(x, y, value)


def checked_image(relative: str, expected_sha256: str) -> ImageReader:
    path = ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"SHA-256 mismatch for {relative}: {actual}")
    return ImageReader(str(path))


def draw_panel(c: canvas.Canvas, record: dict, box: tuple[float, float, float, float], digest_field: str) -> None:
    image = checked_image(record["display_asset"], record[digest_field])
    x, y, width, height = box
    c.setStrokeColorRGB(0.78, 0.81, 0.85)
    c.setLineWidth(0.4)
    c.rect(x, y, width, height)
    c.drawImage(image, x + 3, y + 3, width - 6, height - 6,
                preserveAspectRatio=True, anchor="c", mask="auto")


def build_figure2() -> None:
    manifest = list(csv.DictReader(
        (ROOT / "visual_candidates/VISUAL_SELECTION_MANIFEST_V5_PUBLIC.csv").open(newline="")
    ))
    rows_by_uid: dict[str, dict] = {}
    for record in manifest:
        if record["figure"] != "Figure 2":
            continue
        row = rows_by_uid.setdefault(record["uid"], {
            "title": record["source_title"],
            "panels": {},
        })
        label = record["display_label"]
        if label in row["panels"]:
            raise ValueError(f"Duplicate Figure 2 panel: {record['uid']} {label}")
        row["panels"][label] = record

    expected_order = ["Target", "Fixed Low", "C3", "Fixed High", "Generic Linear"]
    expected_titles = ["Green Iguan, re-created (not mine)", "Building 03", "Specimen 103"]
    rows = list(rows_by_uid.values())
    if [r["title"] for r in rows] != expected_titles:
        raise ValueError("Figure 2 row identity/order changed from the checked V5 selection")
    for row in rows:
        if list(row["panels"]) != expected_order:
            raise ValueError(f"Incomplete or reordered Figure 2 panels for {row['title']}")

    page_height = 390
    c = canvas.Canvas(str(ROOT / "figures/fig2_freshc_controls_v5.pdf"), pagesize=(576, page_height))
    c.setTitle("Figure 2 — shared-view controls")
    margin, gap = 8, 5
    column_width = (576 - 2 * margin - 4 * gap) / 5
    for j, label in enumerate(expected_order):
        draw_text(c, margin + j * (column_width + gap) + 2, page_height - 15, label, 8.5)

    short_names = {
        "Green Iguan, re-created (not mine)": "Green Iguan",
        "Building 03": "Building 03",
        "Specimen 103": "Specimen 103",
    }
    for i, row in enumerate(rows):
        y = page_height - 33 - i * 117
        draw_text(c, 8, y, short_names[row["title"]], 8.4)
        for j, label in enumerate(expected_order):
            box = (margin + j * (column_width + gap), y - 104, column_width, 100)
            draw_panel(c, row["panels"][label], box, "display_tile_sha256")
    c.save()


def build_figure3() -> None:
    config = json.loads((ROOT / "quality_review/FIGURE3_B_SELECTION_V5.json").read_text())
    rows = config["rows"]
    expected_titles = ["Tire", "Baptisimal Font - Aughrim"]
    if [r["title"] for r in rows] != expected_titles:
        raise ValueError("Figure 3 row identity/order changed from the checked V5 selection")
    height = 328
    c = canvas.Canvas(str(ROOT / "figures/fig3_bake10_two_object_v5.pdf"), pagesize=(576, height))
    c.setTitle("Figure 3 — reference and baked appearance")
    labels = ["GT-256 self-bake", "Fixed Mean", "Late-high"]
    margin, gap = 12, 10
    column_width = (576 - 2 * margin - 2 * gap) / 3
    for j, label in enumerate(labels):
        draw_text(c, margin + j * (column_width + gap) + 3, height - 14, label, 8.6)
    for i, row in enumerate(rows):
        top = height - 37 - i * 150
        display_title = "Baptismal font" if row["title"] == "Baptisimal Font - Aughrim" else row["title"]
        draw_text(c, 12, top, display_title, 8.2)
        for j, panel in enumerate(row["panels"]):
            if panel["label"] != labels[j]:
                raise ValueError(f"Figure 3 panel order changed for {row['title']}")
            box = (margin + j * (column_width + gap), top - 126, column_width, 118)
            draw_panel(c, panel, box, "display_sha256")
    c.save()


def clean_supplementary_pair() -> None:
    output_png = ROOT / "figures/source_assets/quality_v5/fig_supp_pair_v5.png"
    output_pdf = ROOT / "figures/fig4_freshc_context_roi_v5.pdf"
    expected_hash = "4cd7922afd2327e9c41cffd5efab0eb9958e19caf9839f10c9224efb9a4c26ba"
    if hashlib.sha256(output_png.read_bytes()).hexdigest() != expected_hash:
        raise ValueError("Supplementary comparison image does not match its audited V5 source hash")
    image = Image.open(output_png)
    if image.size != (2560, 2688):
        raise ValueError(f"Unexpected Supplementary image size: {image.size}")
    width, height = 614.4, 645.12
    c = canvas.Canvas(str(output_pdf), pagesize=(width, height))
    c.setTitle("Supplementary paired Fresh C views")
    c.drawImage(ImageReader(str(output_png)), 0, 0, width=width, height=height)
    c.save()


def main() -> None:
    build_figure2()
    build_figure3()
    clean_supplementary_pair()
    print("Rebuilt Figures 2 and 3 from hash-verified pixels; cleaned the two Supplement figure title bands only.")


if __name__ == "__main__":
    main()
