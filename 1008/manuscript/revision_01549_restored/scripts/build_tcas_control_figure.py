#!/usr/bin/env python3
"""Build the vector overview of the TCAS residual-control path."""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "fig1_tcas_control.pdf"
WIDTH, HEIGHT = 1400, 540

NAVY = HexColor("#274B67")
INK = HexColor("#263746")
MUTED = HexColor("#667C8B")
TEAL = HexColor("#147D7E")
TEAL_LIGHT = HexColor("#E8F3F2")
BLUE_LIGHT = HexColor("#EDF3F7")
ORANGE = HexColor("#BD713B")
ORANGE_LIGHT = HexColor("#FBF1E9")
LINE = HexColor("#CFD9E0")
PANEL = HexColor("#FAFCFD")
GRAY_LIGHT = HexColor("#F3F5F6")


def label(c: canvas.Canvas, x: float, y: float, value: str, size: int = 20,
          *, color=INK, bold: bool = False, align: str = "left") -> None:
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    draw = {"left": c.drawString, "center": c.drawCentredString,
            "right": c.drawRightString}[align]
    draw(x, y, value)


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float,
        *, fill=white, stroke=LINE, radius: float = 14, width: float = 1.5,
        dash: bool = False) -> None:
    c.setLineWidth(width)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.setDash(6, 4) if dash else c.setDash()
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    c.setDash()


def arrow(c: canvas.Canvas, start: tuple[float, float], end: tuple[float, float],
          *, color=NAVY, width: float = 2.8, dashed: bool = False,
          head: float = 11) -> None:
    x1, y1 = start
    x2, y2 = end
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.setDash(6, 4) if dashed else c.setDash()
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


def landscape_icon(c: canvas.Canvas, x: float, y: float) -> None:
    c.setFillColor(BLUE_LIGHT)
    c.roundRect(x, y, 48, 36, 5, stroke=0, fill=1)
    c.setFillColor(HexColor("#9BB9B5"))
    path = c.beginPath()
    path.moveTo(x + 4, y + 4)
    path.lineTo(x + 16, y + 20)
    path.lineTo(x + 25, y + 11)
    path.lineTo(x + 34, y + 22)
    path.lineTo(x + 44, y + 8)
    path.lineTo(x + 44, y + 4)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.circle(x + 35, y + 27, 2.8, stroke=0, fill=1)


def view_tile(c: canvas.Canvas, x: float, y: float, w: float = 43,
              h: float = 24) -> None:
    c.setFillColor(BLUE_LIGHT)
    c.setStrokeColor(HexColor("#D8E1E7"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
    c.setStrokeColor(HexColor("#7E94A2"))
    c.setLineWidth(1.1)
    c.line(x + 7, y + 5, x + w / 2, y + h - 5)
    c.line(x + w / 2, y + h - 5, x + w - 7, y + 5)
    c.line(x + 7, y + 5, x + w - 7, y + 5)


def draw() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    c.setTitle("TCAS control path for multi-view diffusion texture generation")
    c.setAuthor("MVPainter authors")
    c.setSubject("Author-generated vector method schematic")
    c.setFillColor(white)
    c.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)

    # A compact left-to-right pipeline follows the original overview structure.
    box(c, 20, 52, 210, 435, fill=white, stroke=LINE, radius=18, width=1.2)
    box(c, 245, 52, 910, 435, fill=PANEL, stroke=HexColor("#BDCCD6"),
        radius=18, width=1.5)
    box(c, 1170, 52, 210, 435, fill=white, stroke=LINE, radius=18,
        width=1.2)
    label(c, 40, 457, "Inputs", 22, color=NAVY, bold=True)
    label(c, 270, 457, "Frozen multi-view denoiser", 22, color=NAVY,
          bold=True)
    label(c, 1190, 457, "Outputs", 22, color=NAVY, bold=True)

    # Inputs retain the reference/geometry split from the original figure.
    box(c, 40, 344, 170, 94, fill=white, stroke=LINE, radius=11, width=1.1)
    label(c, 54, 411, "Reference image", 17, color=INK, bold=True)
    landscape_icon(c, 54, 358)
    label(c, 112, 374, "appearance", 15, color=MUTED)

    box(c, 40, 132, 170, 188, fill=white, stroke=LINE, radius=11, width=1.1)
    label(c, 54, 292, "Geometry maps", 17, color=INK, bold=True)
    map_rows = [
        ("Normal", HexColor("#DCE8F0"), HexColor("#567994")),
        ("Depth", HexColor("#E8EDF0"), HexColor("#7A8B96")),
        ("Foreground mask", HexColor("#F5E8DE"), ORANGE),
    ]
    for i, (name, fill, accent) in enumerate(map_rows):
        y = 245 - 45 * i
        c.setFillColor(fill)
        c.roundRect(53, y, 144, 34, 7, stroke=0, fill=1)
        c.setFillColor(accent)
        c.roundRect(61, y + 8, 19, 18, 4, stroke=0, fill=1)
        label(c, 89, y + 10, name, 15, color=INK)

    # Reference appearance conditions enter the frozen denoising path.
    arrow(c, (210, 392), (284, 365), color=NAVY, width=2.5)
    label(c, 285, 393, "current UNet features", 17, color=NAVY, bold=True)
    arrow(c, (284, 365), (936, 365), color=NAVY, width=3)

    # Geometry-conditioned residual and the inference-time TCAS scale gate.
    box(c, 292, 213, 216, 102, fill=ORANGE_LIGHT, stroke=ORANGE,
        radius=12, width=1.5)
    label(c, 400, 283, "GeoTex-Adapter", 19, color=ORANGE, bold=True,
          align="center")
    label(c, 400, 257, "geometry residual", 15, color=INK, align="center")
    label(c, 400, 235, "r_geo", 17, color=INK, bold=True, align="center")
    arrow(c, (210, 224), (292, 258), color=ORANGE, width=2.5)
    arrow(c, (508, 264), (555, 264), color=ORANGE, width=2.8)

    box(c, 555, 190, 370, 145, fill=TEAL_LIGHT, stroke=TEAL,
        radius=12, width=1.7)
    label(c, 740, 306, "TCAS scale gate", 20, color=TEAL, bold=True,
          align="center")
    label(c, 740, 277, "s_app = min(s_req, c_l)", 17, color=INK,
          align="center")
    label(c, 740, 250, "r = s_app * r_geo", 17, color=INK, bold=True,
          align="center")
    label(c, 740, 220, "correction magnitude depends on r_geo", 15,
          color=MUTED, align="center")

    # The requested C3 schedule feeds the gate; a cap changes the applied
    # shallow scale, while the resulting correction still depends on r_geo.
    label(c, 565, 166, "C3 requested profile", 15, color=TEAL, bold=True)
    label(c, 875, 166, "50 steps", 15, color=TEAL, bold=True, align="right")
    stages = [("0-16", "1.25", False), ("17-32", "2.50", True),
              ("33-49", "1.25", False)]
    for i, (window, value, active) in enumerate(stages):
        x = 565 + i * 105
        fill = TEAL if active else HexColor("#D9EBE9")
        fg = white if active else TEAL
        c.setFillColor(fill)
        c.roundRect(x, 82, 97, 70, 8, stroke=0, fill=1)
        label(c, x + 48.5, 125, window, 14, color=fg,
              bold=True, align="center")
        label(c, x + 48.5, 99, value, 17, color=fg,
              bold=True, align="center")

    box(c, 890, 82, 245, 70, fill=white, stroke=LINE, radius=8, width=1)
    label(c, 1012.5, 124, "Fresh C shallow cap", 15, color=MUTED,
          bold=True, align="center")
    label(c, 1012.5, 99, "1.25 requested -> 0.8 applied", 15,
          color=INK, bold=True, align="center")
    arrow(c, (740, 152), (740, 188), color=TEAL, width=2,
          dashed=True, head=9)

    # Add the scaled adapter residual to the frozen UNet features.
    c.setStrokeColor(TEAL)
    c.setFillColor(white)
    c.setLineWidth(2.8)
    c.circle(963, 365, 23, stroke=1, fill=1)
    label(c, 963, 355, "+", 29, color=TEAL, bold=True, align="center")
    arrow(c, (925, 264), (946, 344), color=TEAL, width=3)
    label(c, 971, 291, "scaled residual", 14, color=TEAL, bold=True)
    arrow(c, (986, 365), (1186, 365), color=NAVY, width=3)
    label(c, 1083, 393, "updated features", 15, color=MUTED,
          align="center")

    # Outputs show evaluated target views; downstream baking is subdued and
    # explicitly marked as outside the image-space evaluation.
    box(c, 1188, 328, 174, 101, fill=white, stroke=LINE, radius=11,
        width=1.1)
    label(c, 1275, 402, "Six target views", 16, color=NAVY,
          bold=True, align="center")
    for row in range(2):
        for col in range(3):
            view_tile(c, 1201 + col * 52, 342 + row * 29)

    arrow(c, (1275, 323), (1275, 283), color=LINE, width=2,
          dashed=True, head=9)
    box(c, 1190, 164, 170, 110, fill=GRAY_LIGHT, stroke=LINE,
        radius=11, width=1.1, dash=True)
    label(c, 1275, 229, "Projection / baking", 16, color=INK,
          bold=True, align="center")
    label(c, 1275, 202, "Downstream", 14, color=MUTED, align="center")
    label(c, 1275, 183, "not evaluated", 14, color=MUTED, align="center")

    c.showPage()
    c.save()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    draw()
