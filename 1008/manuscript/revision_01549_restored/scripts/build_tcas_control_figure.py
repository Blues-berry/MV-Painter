#!/usr/bin/env python3
"""Build the author-generated Figure 1 overview for the 1008 revision."""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "fig1_assets"
OUTPUT = ROOT / "figures" / "fig1_tcas_control.pdf"
WIDTH, HEIGHT = 1500, 620

NAVY = HexColor("#173F5F")
BLUE = HexColor("#397CA5")
BLUE_LIGHT = HexColor("#EDF4F8")
BLUE_CELL = HexColor("#D6E6EF")
TEAL = HexColor("#147D7E")
TEAL_LIGHT = HexColor("#E8F3F2")
ORANGE = HexColor("#C36D32")
ORANGE_LIGHT = HexColor("#FBF0E7")
INK = HexColor("#263746")
MUTED = HexColor("#687D8B")
LINE = HexColor("#D7E1E7")
PANEL = HexColor("#F8FAFC")
GRAY_LIGHT = HexColor("#F2F5F7")


def label(c: canvas.Canvas, x: float, y: float, value: str, size: int = 16,
          *, color=INK, bold: bool = False, align: str = "left") -> None:
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    draw = {"left": c.drawString, "center": c.drawCentredString,
            "right": c.drawRightString}[align]
    draw(x, y, value)


def rounded_box(c: canvas.Canvas, x: float, y: float, w: float, h: float,
                *, fill=white, stroke=LINE, radius: float = 12,
                width: float = 1.2, dash: bool = False) -> None:
    c.setLineWidth(width)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.setDash(5, 4) if dash else c.setDash()
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.setDash()


def arrow(c: canvas.Canvas, start: tuple[float, float],
          end: tuple[float, float], *, color=NAVY, width: float = 2.4,
          dashed: bool = False, head: float = 9) -> None:
    x1, y1 = start
    x2, y2 = end
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.setDash(5, 4) if dashed else c.setDash()
    c.line(x1, y1, x2, y2)
    c.setDash()
    angle = math.atan2(y2 - y1, x2 - x1)
    side = head * 0.58
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2 - head * math.cos(angle) + side * math.sin(angle),
                y2 - head * math.sin(angle) - side * math.cos(angle))
    path.lineTo(x2 - head * math.cos(angle) - side * math.sin(angle),
                y2 - head * math.sin(angle) + side * math.cos(angle))
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def section_heading(c: canvas.Canvas, x: float, title: str, number: str) -> None:
    c.setFillColor(NAVY)
    c.circle(x + 10, 574, 10, stroke=0, fill=1)
    label(c, x + 10, 570, number, 11, color=white, bold=True, align="center")
    label(c, x + 28, 569, title, 15, color=NAVY, bold=True)


def draw_image(c: canvas.Canvas, filename: str, x: float, y: float,
               w: float, h: float) -> None:
    path = ASSETS / filename
    c.drawImage(ImageReader(str(path)), x, y, width=w, height=h,
                preserveAspectRatio=True, anchor="c", mask="auto")


def feature_map(c: canvas.Canvas, x: float, y: float, size: float = 48) -> None:
    """A small feature tensor glyph, used only as a schematic symbol."""
    rounded_box(c, x, y, size, size, fill=white, stroke=HexColor("#B5CBD8"),
                radius=6, width=1)
    cell = 10
    gap = 2
    shades = [BLUE_CELL, HexColor("#C4DAE6"), HexColor("#E4EEF3"),
              HexColor("#B9D2E0"), BLUE_CELL, HexColor("#DCE9EF"),
              HexColor("#E4EEF3"), HexColor("#C4DAE6"), BLUE_CELL]
    left = x + (size - 3 * cell - 2 * gap) / 2
    bottom = y + (size - 3 * cell - 2 * gap) / 2
    for row in range(3):
        for col in range(3):
            c.setFillColor(shades[row * 3 + col])
            c.roundRect(left + col * (cell + gap),
                        bottom + row * (cell + gap), cell, cell, 2,
                        stroke=0, fill=1)


def draw() -> None:
    for filename in ("reference.png", "normal.png", "depth.png", "mask.png",
                     "target_views.png"):
        if not (ASSETS / filename).is_file():
            raise FileNotFoundError(ASSETS / filename)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    c.setTitle("TCAS residual control in multi-view texture generation")
    c.setAuthor("MVPainter authors")
    c.setSubject("Figure 1; inputs, TCAS residual path, and target-view images")
    c.setFillColor(white)
    c.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)

    # A three-part reading order follows the original overview while reserving
    # visual emphasis for the cap-aware residual path evaluated in 1008.
    section_heading(c, 40, "CONDITION INPUTS", "1")
    section_heading(c, 330, "RESIDUAL CONTROL", "2")
    section_heading(c, 1240, "TARGET-VIEW IMAGES", "3")
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(310, 88, 310, 548)
    c.line(1220, 88, 1220, 548)

    # Reference image and geometry inputs reuse the corresponding thumbnails
    # from the authenticated 01549 overview; they are illustrative inputs.
    rounded_box(c, 40, 397, 245, 151, fill=white, stroke=LINE)
    label(c, 54, 523, "Reference image", 15, color=INK, bold=True)
    draw_image(c, "reference.png", 53, 407, 219, 103)

    label(c, 54, 369, "Geometry maps", 15, color=INK, bold=True)
    map_rows = [("Normal", "normal.png"), ("Depth", "depth.png"),
                ("Foreground mask", "mask.png")]
    for i, (name, filename) in enumerate(map_rows):
        y = 276 - 91 * i
        rounded_box(c, 40, y, 245, 75, fill=white, stroke=LINE,
                    radius=10, width=1)
        draw_image(c, filename, 50, y + 8, 108, 59)
        is_mask = name == "Foreground mask"
        c.setFillColor(ORANGE if is_mask else BLUE)
        c.roundRect(162 if is_mask else 169, y + 24, 4, 27, 2,
                    stroke=0, fill=1)
        label(c, 173 if is_mask else 182, y + 34, name,
              12 if is_mask else 14, color=INK, bold=True)

    # Frozen denoiser feature path: reference conditioning flows across the
    # top lane, while the scaled GeoTex residual is added at the feature path.
    rounded_box(c, 335, 362, 875, 186, fill=PANEL,
                stroke=HexColor("#C8D7E0"), radius=16, width=1.35)
    label(c, 359, 514, "Frozen multi-view diffusion U-Net", 19,
          color=NAVY, bold=True)
    rounded_box(c, 1046, 496, 140, 27, fill=BLUE_LIGHT,
                stroke=BLUE_LIGHT, radius=13, width=0.5)
    label(c, 1116, 505, "50 denoising steps", 12,
          color=NAVY, bold=True, align="center")
    label(c, 359, 387, "hidden-feature path", 12, color=MUTED)

    # Draw connecting arrows before the feature glyphs so they remain crisp.
    arrow(c, (285, 467), (335, 445), color=NAVY, width=2.5)
    feature_xs = [430, 523, 616, 784, 877]
    arrow(c, (335, 445), (430, 445), color=NAVY)
    for left, right in zip(feature_xs, feature_xs[1:]):
        if right - left > 100:
            c.setStrokeColor(MUTED)
            c.setLineWidth(1.6)
            c.setDash(3, 4)
            c.line(left + 48, 445, right - 2, 445)
            c.setDash()
            label(c, (left + right) / 2, 440, "...", 16,
                  color=MUTED, bold=True, align="center")
        else:
            arrow(c, (left + 48, 445), (right, 445), color=NAVY, width=1.8,
                  head=7)
    arrow(c, (925, 445), (1031, 445), color=NAVY, width=2.2)
    arrow(c, (1079, 445), (1236, 445), color=NAVY, width=2.5)
    label(c, 1141, 468, "updated features", 12, color=MUTED, align="center")

    for x in feature_xs:
        feature_map(c, x, 421)
    c.setStrokeColor(TEAL)
    c.setFillColor(white)
    c.setLineWidth(2.5)
    c.circle(1055, 445, 24, stroke=1, fill=1)
    label(c, 1055, 437, "+", 26, color=TEAL, bold=True, align="center")

    # Geometry-conditioned residual, followed by the inference-time scale gate.
    rounded_box(c, 365, 239, 220, 96, fill=ORANGE_LIGHT, stroke=ORANGE,
                radius=12, width=1.5)
    label(c, 475, 303, "GeoTex-Adapter", 18, color=ORANGE,
          bold=True, align="center")
    label(c, 475, 278, "geometry-conditioned residual", 12,
          color=INK, align="center")
    label(c, 475, 255, "r_geo", 16, color=INK, bold=True, align="center")
    c.setStrokeColor(ORANGE)
    c.setLineWidth(1.8)
    c.line(298, 104, 298, 347)
    c.line(285, 104, 298, 104)
    c.line(285, 347, 298, 347)
    arrow(c, (298, 225), (365, 285), color=ORANGE, width=2.5)
    arrow(c, (585, 287), (640, 287), color=ORANGE, width=2.5)

    rounded_box(c, 640, 226, 335, 122, fill=TEAL_LIGHT, stroke=TEAL,
                radius=12, width=1.6)
    label(c, 807.5, 318, "TCAS scale gate", 19, color=TEAL,
          bold=True, align="center")
    label(c, 807.5, 287, "s_app(p_j,l) = min(s_req(p_j,l), c_l)", 14,
          color=INK, align="center")
    label(c, 807.5, 257, "r = s_app * r_geo", 15,
          color=INK, bold=True, align="center")
    arrow(c, (975, 287), (1047, 419), color=TEAL, width=2.8)
    label(c, 1001, 353, "scaled residual", 12, color=TEAL, bold=True)

    # Requested schedule and Fresh C cap are separated to avoid conflating the
    # requested scale with the applied scale or realized correction.
    rounded_box(c, 350, 94, 605, 111, fill=white, stroke=LINE,
                radius=12, width=1.1)
    label(c, 366, 181, "Requested C3 profile", 14,
          color=TEAL, bold=True)
    label(c, 938, 181, "50 steps", 12, color=MUTED, align="right")
    stages = [("Steps 0-16", "1.25", False),
              ("Steps 17-32", "2.50", True),
              ("Steps 33-49", "1.25", False)]
    for i, (window, value, active) in enumerate(stages):
        x = 365 + i * 190
        fill = TEAL if active else HexColor("#E2F0EE")
        fg = white if active else TEAL
        c.setFillColor(fill)
        c.roundRect(x, 112, 178, 55, 8, stroke=0, fill=1)
        label(c, x + 89, 146, window, 12, color=fg,
              bold=True, align="center")
        label(c, x + 89, 123, value, 16, color=fg,
              bold=True, align="center")

    rounded_box(c, 976, 112, 228, 75, fill=white, stroke=LINE,
                radius=10, width=1.1)
    label(c, 1090, 160, "Fresh C shallow cap", 13,
          color=MUTED, bold=True, align="center")
    label(c, 1090, 136, "1.25 requested -> 0.8 applied", 12,
          color=INK, bold=True, align="center")
    arrow(c, (807, 205), (807, 224), color=TEAL, width=1.8,
          dashed=True, head=7)

    # The original target-view thumbnails identify the six-view pipeline.
    # Projection/baking stays visually secondary and explicitly unevaluated.
    rounded_box(c, 1240, 331, 222, 217, fill=white, stroke=LINE,
                radius=13, width=1.1)
    label(c, 1351, 516, "Six target views", 15,
          color=NAVY, bold=True, align="center")
    draw_image(c, "target_views.png", 1250, 363, 202, 140)
    label(c, 1351, 344, "illustrative 01549 examples", 10,
          color=MUTED, align="center")

    arrow(c, (1351, 327), (1351, 280), color=LINE, width=1.8,
          dashed=True, head=7)
    rounded_box(c, 1240, 145, 222, 128, fill=GRAY_LIGHT, stroke=LINE,
                radius=12, width=1.1, dash=True)
    label(c, 1351, 235, "Projection / baking", 14,
          color=INK, bold=True, align="center")
    label(c, 1351, 207, "Downstream pipeline context", 11,
          color=MUTED, align="center")
    label(c, 1351, 184, "not evaluated here", 12,
          color=MUTED, bold=True, align="center")

    c.showPage()
    c.save()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    draw()
