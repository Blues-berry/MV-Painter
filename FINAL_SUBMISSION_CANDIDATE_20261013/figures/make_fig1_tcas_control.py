#!/usr/bin/env python3
"""Build the Figure 1 method schematic as a self-contained SVG and PDF."""

from base64 import b64encode
import math
from pathlib import Path

import cairosvg


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "fig1_assets"
OUT = ROOT / "fig1_tcas_control"
WIDTH, HEIGHT = 1720, 610


def image_data(filename):
    path = ASSETS / filename
    return "data:image/png;base64," + b64encode(path.read_bytes()).decode("ascii")


def svg_text(x, y, value, *, size=18, weight=400, color="#40546A",
             anchor="start", spacing=0, opacity=1):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{size}px" '
        f'font-weight="{weight}" letter-spacing="{spacing}px" '
        f'fill="{color}" opacity="{opacity}" dominant-baseline="middle">'
        f'{value}</text>'
    )


def card(x, y, width, height, *, fill="#FFFFFF", stroke="#DDE6EE",
         radius=17, dash=None, stroke_width=1.5):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}"{dash_attr}/>'
    )


def line(x1, y1, x2, y2, *, color="#536F89", width=2.4,
         dash=None, arrow=False, marker="arrow"):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    arrow_attr = f' marker-end="url(#{marker})"' if arrow else ""
    return (
        f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round"{dash_attr}{arrow_attr}/>'
    )


def image(filename, x, y, width, height, *, clip=None, preserve="xMidYMid meet"):
    clip_attr = f' clip-path="url(#{clip})"' if clip else ""
    return (
        f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
        f'href="{image_data(filename)}" preserveAspectRatio="{preserve}"{clip_attr}/>'
    )


def section_header(number, title, x, y, *, color="#466786"):
    return "".join([
        f'<circle cx="{x}" cy="{y}" r="16" fill="{color}"/>',
        svg_text(x, y + 0.5, number, size=14, weight=700, color="#FFFFFF", anchor="middle"),
        svg_text(x + 27, y, title, size=19, weight=700, color="#20384E", spacing=0.35),
    ])


def tiny_camera(cx, cy, color="#4E897C"):
    return "".join([
        f'<circle cx="{cx}" cy="{cy}" r="8" fill="#FFFFFF" stroke="{color}" stroke-width="1.5"/>',
        f'<rect x="{cx-4.4}" y="{cy-2.8}" width="6.4" height="5.6" rx="1" fill="none" stroke="{color}" stroke-width="1.1"/>',
        f'<path d="M{cx+2},{cy-1.6} L{cx+4.6},{cy-3} V{cy+3} L{cx+2},{cy+1.6} Z" fill="{color}"/>',
    ])


def build_svg():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}px" height="{HEIGHT}px" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs>',
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse">',
        '<path d="M0,0 L9,5 L0,10 Z" fill="#536F89"/>',
        '</marker>',
        '<marker id="arrow-orange" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse">',
        '<path d="M0,0 L9,5 L0,10 Z" fill="#C47A3C"/>',
        '</marker>',
        '<marker id="arrow-green" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse">',
        '<path d="M0,0 L9,5 L0,10 Z" fill="#4E897C"/>',
        '</marker>',
        '<clipPath id="ref-clip"><rect x="69" y="175" width="178" height="178" rx="8"/></clipPath>',
        '<clipPath id="output-clip"><rect x="1132" y="185" width="216" height="154" rx="7"/></clipPath>',
        '</defs>',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        # Title and small protocol badge.
        svg_text(31, 34, "GEOMETRY-CONDITIONED TEXTURE GENERATION", size=14, weight=700,
                 color="#698198", spacing=1.55),
        svg_text(31, 67, "Inference-time scale control, from inputs to baked-asset evaluation", size=26,
                 weight=700, color="#1F354A"),
        '<rect x="1461" y="17" width="229" height="38" rx="19" fill="#F2F6FA" stroke="#DEE7EF"/>',
        svg_text(1575.5, 36.5, "50 INFERENCE STEPS", size=14, weight=700,
                 color="#5D758B", anchor="middle", spacing=0.6),
        # Main cards.
        card(28, 94, 260, 454),
        card(312, 94, 778, 454),
        card(1110, 94, 260, 454, fill="#FFFEFC", stroke="#E7E1D9"),
        card(1390, 94, 340, 454, fill="#FBFDFC", stroke="#78A99F", dash="7 6", stroke_width=1.8),
        # Input section.
        section_header("01", "CONDITIONING INPUTS", 53, 128),
        svg_text(47, 153, "Reference + normal / depth / mask", size=14.5, color="#708398"),
        '<rect x="48" y="169" width="220" height="190" rx="12" fill="#F5F8FA" stroke="#E1E8EE"/>',
        '<rect x="69" y="175" width="178" height="178" rx="8" fill="#FFFFFF"/>',
        image("reference.png", 69, 175, 178, 178, clip="ref-clip"),
        svg_text(158, 376, "REFERENCE IMAGE", size=14, weight=700, color="#526B81", anchor="middle", spacing=0.65),
        svg_text(158, 398, "Building 03 · actual input", size=14, color="#73879A", anchor="middle"),
        svg_text(48, 422, "GEOMETRY MAPS", size=14, weight=700, color="#6B8297", spacing=0.8),
        '<rect x="48" y="433" width="61" height="61" rx="7" fill="#F0F3F7" stroke="#D8E1E8"/>',
        '<rect x="126" y="433" width="61" height="61" rx="7" fill="#F0F3F7" stroke="#D8E1E8"/>',
        '<rect x="204" y="433" width="61" height="61" rx="7" fill="#F0F3F7" stroke="#D8E1E8"/>',
        image("normal.png", 51, 436, 55, 55),
        image("depth.png", 129, 436, 55, 55),
        image("mask.png", 207, 436, 55, 55),
        svg_text(78.5, 512, "Normal", size=14, weight=600, color="#5D7489", anchor="middle"),
        svg_text(156.5, 512, "Depth", size=14, weight=600, color="#5D7489", anchor="middle"),
        svg_text(234.5, 512, "Mask", size=14, weight=600, color="#5D7489", anchor="middle"),
        # Main denoising section.
        section_header("02", "INFERENCE-TIME CONTROL", 338, 128),
        svg_text(338, 157, "TCAS acts on an existing GeoTex residual path", size=16, color="#708398"),
        '<rect x="909" y="111" width="153" height="32" rx="16" fill="#F2F6FA" stroke="#E2EAF0"/>',
        '<rect x="923" y="124" width="14" height="11" rx="2" fill="none" stroke="#71899D" stroke-width="1.4"/>',
        '<path d="M926 124 V121.5 C926 116.5 934 116.5 934 121.5 V124" fill="none" stroke="#71899D" stroke-width="1.4"/>',
        svg_text(1005, 127, "WEIGHTS FROZEN", size=13, weight=700, color="#6A8196", anchor="middle", spacing=0.35),
        # Frozen U-Net panel.
        card(334, 178, 744, 171, fill="#F7F9FC", stroke="#E4EBF2", radius=13, stroke_width=1.2),
        svg_text(353, 198, "FROZEN U-NET · LATENT PATH", size=14, weight=700,
                 color="#698198", spacing=0.55),
        # Skip links behind feature blocks.
        '<path d="M463 298 V317 H834 V298" fill="none" stroke="#9DB2C5" stroke-width="1.8" stroke-dasharray="4 5" marker-end="url(#arrow)"/>',
        '<path d="M545 316 V332 H738 V316" fill="none" stroke="#B3C3D0" stroke-width="1.6" stroke-dasharray="4 5" marker-end="url(#arrow)"/>',
        # Latent path and feature blocks.
        card(351, 240, 57, 42, fill="#FFFFFF", stroke="#D2DEE8", radius=9, stroke_width=1.2),
        svg_text(379.5, 261, "zₜ", size=18, weight=700, color="#506B82", anchor="middle"),
        card(434, 226, 58, 70, fill="#DCEAF5", stroke="#A9C3D6", radius=9, stroke_width=1.2),
        svg_text(463, 261, "D1", size=19, weight=700, color="#3E6480", anchor="middle"),
        card(516, 211, 58, 100, fill="#D5E5F1", stroke="#A0BBD0", radius=9, stroke_width=1.2),
        svg_text(545, 261, "D2", size=19, weight=700, color="#3E6480", anchor="middle"),
        card(600, 197, 82, 128, fill="#C8DCEA", stroke="#91ADC4", radius=10, stroke_width=1.3),
        svg_text(641, 261, "MID", size=18, weight=700, color="#355B78", anchor="middle"),
        card(708, 211, 58, 100, fill="#D5E5F1", stroke="#A0BBD0", radius=9, stroke_width=1.2),
        svg_text(737, 261, "U2", size=19, weight=700, color="#3E6480", anchor="middle"),
        card(806, 226, 58, 70, fill="#DCEAF5", stroke="#A9C3D6", radius=9, stroke_width=1.2),
        svg_text(835, 261, "U1", size=19, weight=700, color="#3E6480", anchor="middle"),
        card(902, 240, 64, 42, fill="#FFFFFF", stroke="#D2DEE8", radius=9, stroke_width=1.2),
        svg_text(934, 261, "zₜ₋₁", size=17, weight=700, color="#506B82", anchor="middle"),
        line(408, 261, 431, 261, width=2, arrow=True),
        line(492, 261, 513, 261, width=2, arrow=True),
        line(574, 261, 597, 261, width=2, arrow=True),
        line(682, 261, 705, 261, width=2, arrow=True),
        line(766, 261, 803, 261, width=2, arrow=True),
        line(864, 261, 899, 261, width=2, arrow=True),
        # Residual path and cap.
        card(340, 365, 171, 62, fill="#FFF2E5", stroke="#E7C6A5", radius=11, stroke_width=1.3),
        svg_text(425.5, 384, "GeoTex-Adapter", size=17, weight=700, color="#835324", anchor="middle"),
        svg_text(425.5, 407, "geometry residual", size=14, color="#9A7046", anchor="middle"),
        line(511, 396, 553, 396, color="#C47A3C", width=2.4, arrow=True, marker="arrow-orange"),
        card(560, 365, 225, 62, fill="#E8F4F1", stroke="#A8CFC4", radius=11, stroke_width=1.3),
        svg_text(672.5, 383, "TCAS · scale control", size=17, weight=700, color="#2B655B", anchor="middle"),
        svg_text(672.5, 406, "s_app = min(s_req, c_l)", size=14, weight=600, color="#477B70", anchor="middle"),
        line(785, 396, 805, 396, color="#4E897C", width=2.4, arrow=True, marker="arrow-green"),
        '<circle cx="823" cy="396" r="17" fill="#FFFFFF" stroke="#4E897C" stroke-width="2.2"/>',
        '<path d="M815 396 H831 M823 388 V404" stroke="#4E897C" stroke-width="2.5" stroke-linecap="round"/>',
        '<path d="M823 379 V300" fill="none" stroke="#4E897C" stroke-width="2.3" marker-end="url(#arrow-green)"/>',
        svg_text(855, 369, "scaled residual", size=13, weight=600, color="#4E897C"),
        # C3 requested profile.
        card(334, 442, 744, 91, fill="#F7FBFA", stroke="#D5E9E3", radius=12, stroke_width=1.2),
        '<rect x="351" y="458" width="40" height="23" rx="11.5" fill="#2E8174"/>',
        svg_text(371, 470, "C3", size=14, weight=700, color="#FFFFFF", anchor="middle"),
        svg_text(402, 469, "REQUESTED SCALE", size=13, weight=700, color="#59877F", spacing=0.5),
        svg_text(351, 506, "s_req · 50 execution steps", size=16, weight=600, color="#355F58"),
        '<path d="M565 504 H720 V478 H875 V504 H1048" fill="none" stroke="#2E8174" stroke-width="3.5" stroke-linejoin="round"/>',
        svg_text(642.5, 490, "1.25", size=16, weight=700, color="#2B756B", anchor="middle"),
        svg_text(797.5, 468, "2.50", size=16, weight=700, color="#2B756B", anchor="middle"),
        svg_text(961.5, 490, "1.25", size=16, weight=700, color="#2B756B", anchor="middle"),
        svg_text(642.5, 522, "0–16", size=13.5, weight=600, color="#68857F", anchor="middle"),
        svg_text(797.5, 522, "17–32", size=13.5, weight=600, color="#68857F", anchor="middle"),
        svg_text(961.5, 522, "33–49", size=13.5, weight=600, color="#68857F", anchor="middle"),
        # Generated-view card: recorded six-view output from the same object UID.
        section_header("03", "GENERATED VIEWS", 1136, 128, color="#6E8194"),
        svg_text(1128, 155, "Recorded C3 output · same object UID", size=14.5, color="#778A9D"),
        '<rect x="1126" y="177" width="228" height="230" rx="11" fill="#F7F9FB" stroke="#DDE6EE"/>',
        image("target_views.png", 1132, 185, 216, 154, clip="output-clip", preserve="xMidYMid meet"),
        svg_text(1240, 362, "Six generated RGB views", size=14.5, weight=700, color="#526B81", anchor="middle"),
        svg_text(1240, 385, "C3 confirmation · UID c76ac44d…", size=12.5, color="#73879A", anchor="middle"),
        svg_text(1240, 400, "Example output, not a quality summary", size=11.5, color="#8A7965", anchor="middle"),
        # Downstream bake/evaluation path, explicitly separated from the model.
        section_header("04", "ASSET-LEVEL EVALUATION", 1418, 128, color="#4E897C"),
        svg_text(1410, 155, "Selected, separate cohorts", size=15.5, color="#66897F"),
        card(1408, 178, 304, 165, fill="#F4FAF8", stroke="#D3E7E1", radius=12, stroke_width=1.2),
        svg_text(1427, 199, "01  PROJECT TO NATIVE UV", size=14, weight=700, color="#4A786F", spacing=0.3),
        # Six input tiles and a native UV texture swatch.
        *[f'<rect x="{1428 + (i % 3) * 25}" y="{220 + (i // 3) * 24}" width="19" height="17" rx="3" fill="{["#D6B59A", "#E2C5A9", "#B9876A", "#D4BDA6", "#A9785D", "#CFAD8E"][i]}" stroke="#B9A28C" stroke-width="0.7"/>' for i in range(6)],
        svg_text(1453, 288, "generated views", size=12.5, color="#778E87", anchor="middle"),
        '<path d="M1505 247 H1545" fill="none" stroke="#4E897C" stroke-width="2.2" marker-end="url(#arrow-green)"/>',
        '<rect x="1558" y="216" width="75" height="66" rx="5" fill="#E7D3BE" stroke="#9DBAB0" stroke-width="1.2"/>',
        '<path d="M1583 216 V282 M1608 216 V282 M1558 238 H1633 M1558 260 H1633" stroke="#F8F3EB" stroke-width="2"/>',
        '<path d="M1558 238 L1583 216 M1608 282 L1633 260 M1583 260 L1608 238" fill="none" stroke="#B28868" stroke-width="1.1"/>',
        svg_text(1595.5, 298, "native UV map", size=12.5, color="#66857C", anchor="middle"),
        svg_text(1560, 326, "Views projected onto the input mesh", size=14, weight=600, color="#446F67", anchor="middle"),
        card(1408, 355, 304, 170, fill="#F4FAF8", stroke="#D3E7E1", radius=12, stroke_width=1.2),
        svg_text(1427, 377, "02  UNSEEN-VIEW ASSESSMENT", size=14, weight=700, color="#4A786F", spacing=0.25),
        # Eleven camera markers around a schematic textured mesh.
        '<ellipse cx="1560" cy="444" rx="109" ry="45" fill="none" stroke="#B7D0C9" stroke-width="1.4" stroke-dasharray="3 5"/>',
        *[tiny_camera(1560 + 109 * math.cos(2 * math.pi * i / 11),
                      444 + 45 * math.sin(2 * math.pi * i / 11)) for i in range(11)],
        '<path d="M1534 425 L1560 411 L1586 425 L1560 440 Z M1534 425 V457 L1560 473 V440 M1586 425 V457 L1560 473" '
        'fill="#E6EFEA" stroke="#648A81" stroke-width="1.8" stroke-linejoin="round"/>',
        '<path d="M1560 411 V440 M1547 433 V464 M1573 433 V464 M1534 441 L1560 456 L1586 441" '
        'fill="none" stroke="#A2BEB6" stroke-width="1.1"/>',
        svg_text(1560, 500, "Unlit renders · 11 unseen cameras", size=14.5, weight=700, color="#416F66", anchor="middle"),
        svg_text(1560, 518, "Baking is an evaluation path", size=12.5, color="#739087", anchor="middle"),
        # Connections clarify the real model path and the separate evaluation branch.
        '<path d="M288 267 H303 C319 267 309 182 339 182 H978 V197" fill="none" stroke="#536F89" stroke-width="2.2" marker-end="url(#arrow)"/>',
        '<rect x="888" y="201" width="180" height="26" rx="13" fill="#FFFFFF" stroke="#D5E1EA"/>',
        svg_text(978, 214, "reference conditioning", size=12.5, weight=600, color="#668097", anchor="middle"),
        '<path d="M288 462 C306 462 312 446 323 429 L342 403" fill="none" stroke="#C47A3C" stroke-width="2.6" marker-end="url(#arrow-orange)"/>',
        '<path d="M966 261 H985" fill="none" stroke="#536F89" stroke-width="2.2" marker-end="url(#arrow)"/>',
        card(988, 240, 62, 42, fill="#FFFFFF", stroke="#D2DEE8", radius=9, stroke_width=1.2),
        svg_text(1019, 254, "VAE", size=15, weight=700, color="#506B82", anchor="middle"),
        svg_text(1019, 270, "decode", size=10.5, weight=600, color="#73879A", anchor="middle"),
        '<path d="M1050 261 H1090" fill="none" stroke="#536F89" stroke-width="2.2" marker-end="url(#arrow)"/>',
        '<path d="M1090 267 H1110" fill="none" stroke="#536F89" stroke-width="2.6" marker-end="url(#arrow)"/>',
        '<path d="M1370 290 H1390" fill="none" stroke="#4E897C" stroke-width="2.4" stroke-dasharray="4 4" marker-end="url(#arrow-green)"/>',
        '</svg>',
    ]
    return "\n".join(str(part) for part in parts)


def main():
    svg = build_svg().encode("utf-8")
    OUT.with_suffix(".svg").write_bytes(svg)
    cairosvg.svg2pdf(bytestring=svg, write_to=str(OUT.with_suffix(".pdf")))
    cairosvg.svg2png(bytestring=svg, write_to=str(OUT.with_suffix(".png")),
                     output_width=3440, output_height=1220)


if __name__ == "__main__":
    main()
