#!/usr/bin/env python3
"""Build the vector overview of the TCAS residual-control path."""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "fig1_tcas_control.pdf"
WIDTH, HEIGHT = 1600, 620

NAVY = HexColor("#254867")
INK = HexColor("#263746")
MUTED = HexColor("#64748B")
TEAL = HexColor("#147D7E")
TEAL_LIGHT = HexColor("#E7F3F2")
BLUE_LIGHT = HexColor("#EFF4F8")
ORANGE = HexColor("#C77B32")
ORANGE_LIGHT = HexColor("#FAF0E5")
LINE = HexColor("#9AAAB7")
PANEL = HexColor("#FCFDFE")
GRAY_LIGHT = HexColor("#F3F5F7")


def label(c: canvas.Canvas, x: float, y: float, value: str, size: int = 22,
          *, color=INK, bold: bool = False, align: str = "left") -> None:
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    draw = {"left": c.drawString, "center": c.drawCentredString,
            "right": c.drawRightString}[align]
    draw(x, y, value)


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float,
        *, fill=white, stroke=LINE, radius: float = 16, width: float = 2,
        dash: bool = False) -> None:
    c.setLineWidth(width)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.setDash(7, 5) if dash else c.setDash()
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.setDash()


def arrow(c: canvas.Canvas, start: tuple[float, float], end: tuple[float, float],
          *, color=NAVY, width: float = 4, dashed: bool = False,
          head: float = 13) -> None:
    x1, y1 = start
    x2, y2 = end
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.setDash(8, 6) if dashed else c.setDash()
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


def panel(c: canvas.Canvas, x: float, y: float, w: float, h: float,
          title: str) -> None:
    box(c, x, y, w, h, fill=PANEL, stroke=HexColor("#C8D3DC"), radius=22,
        width=2)
    label(c, x + 24, y + h - 43, title, 24, color=NAVY, bold=True)


def draw() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    c.setTitle("TCAS control path for multi-view diffusion texture generation")
    c.setAuthor("MVPainter authors")
    c.setSubject("Author-generated vector method schematic")
    c.setFillColor(white)
    c.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)

    # Three pipeline regions.
    panel(c, 28, 72, 268, 476, "INPUTS")
    panel(c, 328, 72, 934, 476, "FROZEN MULTI-VIEW DENOISER")
    panel(c, 1292, 72, 280, 476, "OUTPUTS")

    # Reference and geometry inputs.
    box(c, 52, 397, 220, 94, fill=white, stroke=HexColor("#B8C8D4"), radius=14)
    label(c, 68, 462, "Reference image", 20, color=INK, bold=True)
    c.setFillColor(BLUE_LIGHT)
    c.roundRect(68, 412, 72, 36, 5, stroke=0, fill=1)
    c.setFillColor(HexColor("#9ABBB5"))
    path = c.beginPath()
    path.moveTo(68, 412)
    path.lineTo(91, 437)
    path.lineTo(106, 423)
    path.lineTo(119, 438)
    path.lineTo(140, 418)
    path.lineTo(140, 412)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.circle(126, 440, 4, stroke=0, fill=1)
    label(c, 151, 432, "appearance", 17, color=MUTED)

    box(c, 52, 157, 220, 218, fill=white, stroke=HexColor("#B8C8D4"), radius=14)
    label(c, 68, 344, "Geometry maps", 20, color=INK, bold=True)
    map_rows = [
        ("Normal", HexColor("#DAE7F1"), HexColor("#577A9B")),
        ("Depth", HexColor("#E8EDF0"), HexColor("#778894")),
        ("Foreground mask", HexColor("#F4E7D9"), ORANGE),
    ]
    for i, (name, fill, accent) in enumerate(map_rows):
        y = 286 - 62 * i
        box(c, 68, y, 188, 48, fill=fill, stroke=fill, radius=9, width=1)
        c.setFillColor(accent)
        c.roundRect(79, y + 9, 32, 30, 5, stroke=0, fill=1)
        label(c, 123, y + 16, name, 18, color=INK)
    # Inputs go to their corresponding paths.
    arrow(c, (296, 444), (371, 365), color=NAVY)
    label(c, 301, 463, "view conditioning", 15, color=MUTED)
    arrow(c, (296, 263), (374, 302), color=ORANGE)
    label(c, 302, 318, "geometry", 15, color=MUTED)

    # Inference-time schedule: it changes the residual multiplier only.
    box(c, 417, 421, 652, 77, fill=TEAL_LIGHT, stroke=TEAL, radius=14, width=2)
    label(c, 437, 473, "C3 requested profile s_req(p), before group caps", 19,
          color=TEAL, bold=True)
    stages = [
        ("Early  1.25", HexColor("#D4E8E6"), TEAL),
        ("Middle  2.50", TEAL, white),
        ("Late  1.25", HexColor("#D4E8E6"), TEAL),
    ]
    for i, (name, fill, color) in enumerate(stages):
        x = 438 + i * 198
        c.setFillColor(fill)
        c.roundRect(x, 433, 182, 30, 8, stroke=0, fill=1)
        label(c, x + 91, 442, name, 17, color=color, bold=True, align="center")
    label(c, 1228, 454, "50 denoising steps", 16, color=MUTED,
          align="right")

    # Frozen denoiser feature path and the GeoTex correction path.
    label(c, 379, 390, "current UNet features h_(j,l)", 18, color=NAVY)
    arrow(c, (371, 365), (1046, 365), color=NAVY, width=4)
    c.setStrokeColor(TEAL)
    c.setFillColor(white)
    c.setLineWidth(4)
    c.circle(1074, 365, 27, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(TEAL)
    c.drawCentredString(1074, 354, "+")
    arrow(c, (1102, 365), (1314, 365), color=NAVY, width=4)
    label(c, 1220, 393, "updated features", 16, color=MUTED, align="center")

    box(c, 374, 239, 260, 102, fill=ORANGE_LIGHT, stroke=ORANGE, radius=14,
        width=2)
    label(c, 504, 307, "GeoTex-Adapter", 21, color=ORANGE, bold=True,
          align="center")
    label(c, 504, 278, "geometry-conditioned", 17, color=INK, align="center")
    label(c, 504, 255, "residual r_geo", 17, color=INK, bold=True,
          align="center")

    box(c, 700, 239, 295, 102, fill=TEAL_LIGHT, stroke=TEAL, radius=14,
        width=2)
    label(c, 847, 307, "TCAS scale gate", 21, color=TEAL, bold=True,
          align="center")
    label(c, 847, 278, "s_app(p,l) = min(s_req, c_l)", 17, color=INK,
          align="center")
    label(c, 847, 255, "r_app = s_app * r_geo", 17, color=INK, bold=True,
          align="center")

    arrow(c, (634, 290), (700, 290), color=ORANGE, width=4)
    arrow(c, (851, 421), (851, 345), color=TEAL, width=3, dashed=True, head=11)
    label(c, 867, 372, "requested scale", 14, color=TEAL)
    arrow(c, (995, 290), (1062, 335), color=TEAL, width=4)
    label(c, 1003, 320, "scaled residual", 14, color=TEAL)

    # Output images and explicitly bounded downstream pipeline context.
    box(c, 1314, 356, 236, 138, fill=white, stroke=HexColor("#B8C8D4"), radius=14)
    label(c, 1432, 467, "Six target views", 19, color=NAVY, bold=True,
          align="center")
    for row in range(2):
        for col in range(3):
            x = 1343 + col * 65
            y = 385 + row * 37
            c.setFillColor(BLUE_LIGHT if (row + col) % 2 == 0 else GRAY_LIGHT)
            c.roundRect(x, y, 52, 29, 4, stroke=0, fill=1)
            c.setStrokeColor(HexColor("#8A9AA6"))
            c.setLineWidth(1.5)
            c.line(x + 6, y + 6, x + 25, y + 23)
            c.line(x + 25, y + 23, x + 44, y + 7)
            c.line(x + 6, y + 6, x + 44, y + 6)

    arrow(c, (1432, 350), (1432, 317), color=LINE, width=3, dashed=True,
          head=10)
    box(c, 1314, 166, 236, 142, fill=GRAY_LIGHT, stroke=LINE, radius=14,
        width=2, dash=True)
    label(c, 1432, 275, "Projection / baking", 19, color=INK, bold=True,
          align="center")
    # Simple wireframe mesh icon; it is illustrative and contains no model asset.
    c.setStrokeColor(HexColor("#7F8D97"))
    c.setLineWidth(2)
    c.line(1381, 222, 1410, 239)
    c.line(1410, 239, 1440, 221)
    c.line(1440, 221, 1411, 204)
    c.line(1411, 204, 1381, 222)
    c.line(1381, 222, 1381, 190)
    c.line(1381, 190, 1411, 174)
    c.line(1411, 174, 1411, 204)
    c.line(1440, 221, 1440, 190)
    c.line(1440, 190, 1411, 174)
    c.line(1411, 174, 1381, 190)
    label(c, 1452, 205, "downstream", 15, color=MUTED, align="left")
    label(c, 1432, 115, "Pipeline context only; Fresh C does not validate", 13,
          color=MUTED, align="center")
    label(c, 1432, 97, "baked or PBR quality", 13, color=MUTED, align="center")

    c.showPage()
    c.save()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    draw()
