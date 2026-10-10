#!/usr/bin/env python3
"""Build the Figure 1 SVG/PDF with generated artwork and vector annotations."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

import cairosvg
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "fig1_assets"
FIGURES = ROOT / "figures"
BASE = ASSETS / "fig1_generated_editorial_base.png"
SOURCE_VIEWS = ASSETS / "target_views.png"
SVG_OUTPUT = FIGURES / "fig1_tcas_control.svg"
PDF_OUTPUT = FIGURES / "fig1_tcas_control.pdf"

WIDTH, HEIGHT = 1860, 845
INK = "#20384D"
NAVY = "#174A7C"
BLUE = "#2F76C6"
TEAL = "#0B8585"
AMBER = "#C87431"
MUTED = "#6D7F89"
PANEL = "#FFFEFB"
BORDER = "#D7E0E4"
BACKGROUND = "#FDFCF8"


def png_data_uri(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{data}"


def file_data_uri(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def text(
    x: float,
    y: float,
    value: str,
    size: float,
    *,
    fill: str = INK,
    weight: int = 500,
    anchor: str = "start",
    spacing: float | None = None,
) -> str:
    letter_spacing = "" if spacing is None else f' letter-spacing="{spacing}"'
    return (
        f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}"{letter_spacing}>{escape(value)}</text>'
    )


def rounded_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str,
    stroke: str = BORDER,
    radius: float = 10,
    stroke_width: float = 1.4,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}"/>'
    )


def image_element(x: float, y: float, width: float, height: float, uri: str) -> str:
    return (
        f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
        f'preserveAspectRatio="xMidYMid meet" xlink:href="{uri}"/>'
    )


def input_cards() -> str:
    rows = [
        ("Reference image", "reference.png", 88, 166, NAVY),
        ("Normal map", "normal.png", 264, 152, BLUE),
        ("Depth map", "depth.png", 428, 154, BLUE),
        ("Foreground mask", "mask.png", 592, 151, AMBER),
    ]
    output: list[str] = []
    for label, filename, y, height, accent in rows:
        output.append(rounded_rect(29, y, 221, height, fill=PANEL))
        output.append(f'<circle cx="44" cy="{y + 18}" r="4.2" fill="{accent}"/>')
        label_size = 18 if label == "Foreground mask" else 20
        output.append(text(56, y + 25, label, label_size, weight=650))
        output.append(
            rounded_rect(
                38, y + 32, 203, height - 39, fill="#F4F6F5",
                stroke="#EDF0F0", radius=6, stroke_width=0.6
            )
        )
        output.append(
            image_element(
                40, y + 34, 199, height - 43,
                file_data_uri(ASSETS / filename),
            )
        )
    return "\n".join(output)


def target_cards() -> str:
    source = Image.open(SOURCE_VIEWS).convert("RGB")
    crops = [
        (32, 30, 184, 182),
        (210, 28, 376, 183),
        (397, 30, 560, 184),
        (28, 222, 185, 378),
        (210, 222, 376, 382),
        (397, 222, 562, 379),
    ]
    output: list[str] = []
    xs = [1495, 1613, 1731]
    ys = [200, 312]
    for index, crop in enumerate(crops):
        x, y = xs[index % 3], ys[index // 3]
        output.append(rounded_rect(x, y, 110, 104, fill=PANEL, radius=9))
        output.append(
            image_element(
                x + 5, y + 4, 100, 96,
                png_data_uri(source.crop(crop)),
            )
        )
    return "\n".join(output)


def build() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for asset in (BASE, SOURCE_VIEWS):
        if not asset.exists():
            raise FileNotFoundError(f"Missing Figure 1 asset: {asset}")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
      <title>TCAS residual control in multi-view texture generation</title>
      <desc>Generated editorial illustration with vector labels and source thumbnails.</desc>
      <image x="0" y="0" width="{WIDTH}" height="{HEIGHT}"
        preserveAspectRatio="none" xlink:href="{file_data_uri(BASE)}"/>
      <g id="restored-source-inputs">
        <rect x="24" y="80" width="230" height="672" fill="{BACKGROUND}"/>
        {input_cards()}
      </g>
      <g id="restored-source-target-views">
        <rect x="1490" y="120" width="370" height="570" fill="{BACKGROUND}"/>
        {target_cards()}
      </g>
      <g id="vector-labels">
        {text(29, 69, "CONDITION INPUTS", 23, fill=NAVY, weight=700, spacing=0.7)}
        {text(366, 69, "FROZEN MULTI-VIEW DIFFUSION U-NET", 28, fill=NAVY, weight=700, spacing=0.35)}
        {text(1495, 181, "SIX TARGET VIEWS", 22, fill=NAVY, weight=700, spacing=0.5)}
        {text(1495, 436, "Illustrative examples retained from 01549", 16, fill=MUTED, weight=500)}
        {text(369, 584, "GeoTex-Adapter", 22, fill=AMBER, weight=700)}
        {text(863, 412, "TCAS SCALE GATE", 22, fill=TEAL, weight=700, anchor="middle", spacing=0.4)}
        {text(1180, 580, "Applied scale: s_app = min(s_req, c_l)", 16, fill=INK, weight=600, anchor="start")}
        {text(1180, 604, "r_scaled = s_app · r_geo", 16, fill=INK, weight=600, anchor="start")}
        {text(330, 628, "Requested C3 scale", 22, fill=TEAL, weight=700)}
        {rounded_rect(1495, 470, 345, 70, fill="#FFFEFB", stroke="#E1C7AB", radius=10, stroke_width=1.3)}
        {text(1513, 500, "Fresh C shallow cap", 18, fill=AMBER, weight=700)}
        {text(1513, 526, "1.25 requested  →  0.8 applied", 17, fill=INK, weight=600)}
        {text(596, 783, "Steps 0–16", 18, fill=MUTED, weight=600, anchor="middle")}
        {text(863, 783, "Steps 17–32", 18, fill=MUTED, weight=600, anchor="middle")}
        {text(1093, 783, "Steps 33–49", 18, fill=MUTED, weight=600, anchor="middle")}
        {text(596, 808, "1.25", 22, fill=TEAL, weight=700, anchor="middle")}
        {text(863, 808, "2.50", 22, fill=TEAL, weight=700, anchor="middle")}
        {text(1093, 808, "1.25", 22, fill=TEAL, weight=700, anchor="middle")}
      </g>
    </svg>
    """
    svg = svg.strip() + "\n"
    SVG_OUTPUT.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(
        bytestring=svg.encode("utf-8"),
        write_to=str(PDF_OUTPUT),
        output_width=WIDTH,
        output_height=HEIGHT,
    )
    print(f"Created {SVG_OUTPUT}")
    print(f"Created {PDF_OUTPUT}")


if __name__ == "__main__":
    build()
