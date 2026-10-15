#!/usr/bin/env python3
"""Build the V5 presentation deck and a silent video from the frozen V5 figures."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import uno
from com.sun.star.awt import Point, Size


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
BUILD = OUT / "build"
FIGURES = ROOT / "figures"
W, H = 33867, 19050  # 16:9, 1/100 mm
NAVY = 0x18324B
TEAL = 0x087E8B
BLUE = 0x2F6BCE
INK = 0x243444
GRAY = 0x596B7B
LIGHT = 0xF5F8FC
PALE = 0xE8F1F5
WHITE = 0xFFFFFF
GOLD = 0xE5A83B
RED = 0xB64B49
GREEN = 0x3C8C72


NARRATION = [
    ("01 | Title", "This presentation summarizes the V5 journal study of timestep-conditioned adapter scaling for multi-view diffusion texture generation. The focus is what survives comparison with strong controls and evaluation on baked assets."),
    ("02 | The graphics task", "For graphics, generated RGB views are intermediate. The deliverable is a textured mesh whose appearance should be checked from cameras not used to generate or bake its texture. Projection, UV coverage, and resampling can change the result. This study connects image-space scores to that asset-level outcome."),
    ("03 | The executed intervention", "TCAS changes the requested multiplier on an existing GeoTex adapter residual; it does not add a learned module. The historical C3 profile requests 1.25, 2.50, and 1.25 across early, middle, and late windows. In Fresh C, the shallow group is capped at 0.80 throughout. The realized correction also depends on the evolving hidden state, so a scale label is not a residual-dose measurement."),
    ("04 | Strong controls on 300 objects", "On 300 held-out objects, C3 improves foreground PSNR over Fixed Low by 0.522 decibels. That comparison also raises the deep and middle applied-scale sums from 62.5 to 82.5. Fixed High and Generic Linear have better means than C3 across all four evaluated image endpoints. This revises the interpretation of the original low-versus-high-versus-low result. The figure shows examples, not an estimate of typical appearance."),
    ("05 | Matched-budget timing test", "The specified timing primary compares Middle-high with the object-wise average of Early-high and Late-high at matched per-group applied-scale sums. The mean difference is minus 0.0339 decibels, with a 95 percent interval from minus 0.1172 to plus 0.0514 and a p-value of 0.432. It detects no middle-window advantage and does not establish equivalence. Retrospective pairwise contrasts differ in opposite directions, indicating within-cohort placement sensitivity without selecting a preferred schedule."),
    ("06 | Native-UV baking", "In the compatibility-selected GeoTex bake pilot, Late-high—not C3—reduces unseen-view LPIPS relative to Fixed Mean by 0.00265 on ten objects. The change closes about 3.7 percent of the mean reference self-bake gap, while substantial appearance error remains. A separate twenty-object GSO bake study does not detect the same benefit under its distinct protocol."),
    ("07 | Appearance boundary", "The visual comparison makes the remaining reference-appearance gap concrete. Image-space improvements do not establish faithful color or material reproduction. The bake evaluation uses unlit base color; it does not test a physically based material or lighting pipeline."),
    ("08 | Native-interface boundaries", "The two MV-Adapter timing primaries also do not detect their specified middle-window contrasts: plus 0.029 decibels on fifty objects and minus 0.014 on the GSO one-hundred-object cohort, with both intervals spanning zero. These are separate cohorts and primary comparisons. GSO one hundred uses the same MV-Adapter interface, so it is not an independent backbone replication."),
    ("09 | Graphics contribution", "The contribution is an evidence chain for an implemented graphics control. We report requested values, cap-adjusted applied values, and state-dependent corrections; compare C3 with competitive fixed and linear controls and a matched scalar budget; then evaluate native UV bakes from unseen cameras and test boundaries across interfaces. The findings support reporting the executed interface and asset response, not a universal schedule recommendation."),
    ("10 | Data and conclusion", "The limited public data release is archived as Zenodo version 1.0.1 at DOI 10.5281 slash zenodo dot 23383807. It contains selected derived metrics and attribution records. It excludes source meshes and textures, generated-image archives, model weights, checkpoints, and participant-level responses. Overall, the evidence does not identify a universally preferred schedule or establish faithful material reproduction. Thank you."),
]


def pv(name, value):
    item = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    item.Name = name
    item.Value = value
    return item


def connect():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local
    )
    url = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
    for _ in range(40):
        try:
            context = resolver.resolve(url)
            desktop = context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", context
            )
            return desktop
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("LibreOffice UNO service on port 2002 is unavailable")


def make_rect(doc, page, x, y, width, height, color, line_color=None):
    shape = doc.createInstance("com.sun.star.drawing.RectangleShape")
    shape.Position = Point(int(x), int(y))
    shape.Size = Size(int(width), int(height))
    shape.FillStyle = 1
    shape.FillColor = int(color)
    shape.LineStyle = 0 if line_color is None else 1
    if line_color is not None:
        shape.LineColor = int(line_color)
    page.add(shape)
    return shape


def add_text(doc, page, x, y, width, height, text, size=16, color=INK,
             bold=False, align=0, vertical=0, font="Liberation Sans"):
    shape = doc.createInstance("com.sun.star.drawing.RectangleShape")
    shape.Position = Point(int(x), int(y))
    shape.Size = Size(int(width), int(height))
    shape.FillStyle = 0
    shape.LineStyle = 0
    shape.TextLeftDistance = 0
    shape.TextRightDistance = 0
    shape.TextUpperDistance = 0
    shape.TextLowerDistance = 0
    shape.TextWordWrap = True
    shape.TextVerticalAdjust = vertical
    page.add(shape)
    shape.setString(text)
    shape.CharFontName = font
    shape.CharHeight = float(size)
    shape.CharColor = int(color)
    if bold:
        shape.CharWeight = 150.0
    shape.ParaAdjust = align
    return shape


def add_image(doc, page, path, x, y, width, height):
    shape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
    shape.Position = Point(int(x), int(y))
    shape.Size = Size(int(width), int(height))
    shape.GraphicURL = uno.systemPathToFileUrl(str(path))
    page.add(shape)
    return shape


def add_notes(page, text):
    notes_page = page.getNotesPage()
    for i in range(notes_page.getCount()):
        shape = notes_page.getByIndex(i)
        if str(getattr(shape, "ShapeType", "")).endswith("NotesShape"):
            shape.setString(text)
            break


def add_footer(doc, page, number, dark=False):
    c = 0xB9C7D2 if dark else 0x758697
    line = 0x375066 if dark else 0xD9E2EA
    make_rect(doc, page, 1300, 18150, 31250, 22, line)
    add_text(doc, page, 1300, 18240, 25000, 390,
             "V5 journal study  |  Timestep-conditioned geometry control",
             size=9, color=c)
    add_text(doc, page, 31000, 18240, 1500, 390, f"{number:02d} / 10",
             size=9, color=c, align=2)


def add_header(doc, page, number, title, eyebrow=None):
    add_text(doc, page, 1300, 400, 29000, 500,
             eyebrow or "COMPUTERS & GRAPHICS  |  V5 JOURNAL STUDY",
             size=10, color=TEAL, bold=True)
    add_text(doc, page, 1300, 1050, 31000, 1250, title,
             size=27, color=NAVY, bold=True)
    add_footer(doc, page, number)


def clear_page(page):
    for shape in list(page):
        page.remove(shape)


def add_bullet(doc, page, x, y, width, text, size=16, color=INK, height=1400):
    add_text(doc, page, x, y, 500, height, "•", size=size + 2, color=TEAL, bold=True)
    add_text(doc, page, x + 700, y, width - 700, height, text,
             size=size, color=color)


def prepare_figures():
    BUILD.mkdir(parents=True, exist_ok=True)
    fig_dir = BUILD / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    names = {
        "method": "fig1_tcas_control",
        "controls": "fig2_freshc_controls_v5",
        "bake": "fig3_bake10_two_object_v5",
        "appearance": "fig4_color_diagnostic_freshc_context_roi_v5",
    }
    output = {}
    for key, basename in names.items():
        pdf = FIGURES / f"{basename}.pdf"
        png = fig_dir / f"{basename}.png"
        subprocess.run([
            "pdftoppm", "-f", "1", "-l", "1", "-png", "-singlefile",
            "-scale-to-x", "2000", "-scale-to-y", "-1", str(pdf), str(png.with_suffix(""))
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output[key] = png
    return output


def add_cell(doc, page, x, y, width, height, text, *, fill=None,
             color=INK, size=12, bold=False, align=0):
    if fill is not None:
        make_rect(doc, page, x, y, width, height, fill)
    add_text(doc, page, x + 120, y + 80, width - 240, height - 150,
             text, size=size, color=color, bold=bold, align=align, vertical=0)


def build_slide_deck(figs):
    desktop = connect()
    doc = desktop.loadComponentFromURL("private:factory/simpress", "_blank", 0, ())
    pages = doc.getDrawPages()
    first = pages.getByIndex(0)
    first.Width = W
    first.Height = H
    clear_page(first)
    slide_pages = [first]
    for i in range(1, 10):
        page = pages.insertNewByIndex(i)
        page.Width = W
        page.Height = H
        clear_page(page)
        slide_pages.append(page)

    # 1. Title
    p = slide_pages[0]
    make_rect(doc, p, 0, 0, W, H, NAVY)
    make_rect(doc, p, 0, 0, 360, H, TEAL)
    make_rect(doc, p, 2000, 2480, 1800, 120, GOLD)
    add_text(doc, p, 2000, 1800, 30000, 500,
             "COMPUTERS & GRAPHICS  |  JOURNAL STUDY", size=12, color=0xC7D6E2, bold=True)
    add_text(doc, p, 2000, 3500, 29600, 2600,
             "Timestep-Conditioned Adapter Scaling\nfor Multi-view Diffusion Texture Generation",
             size=31, color=WHITE, bold=True)
    add_text(doc, p, 2050, 6800, 28500, 1100,
             "Control allocation and baked appearance", size=22, color=0xB9E3E5)
    add_text(doc, p, 2050, 10000, 27800, 1450,
             "A controlled evaluation of an existing geometry-residual interface,\nfrom applied scale to UV-textured assets viewed from unseen cameras.",
             size=16, color=WHITE)
    add_text(doc, p, 2050, 15300, 27500, 650,
             "CAD/Graphics 2026 Paper 75  |  Revised journal evaluation",
             size=12, color=0xC7D6E2)
    add_notes(p, NARRATION[0][1])

    # 2. Graphics task and asset-level endpoint
    p = slide_pages[1]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 2, "The graphics result is the textured asset, not only the generated view")
    add_bullet(doc, p, 1500, 4200, 13200,
               "Generated RGB views are intermediate outputs in a 3D texturing pipeline.", size=17, height=2100)
    add_bullet(doc, p, 1500, 7100, 13200,
               "Projection, UV coverage, hole filling, and resampling affect the final appearance.", size=17, height=2300)
    add_bullet(doc, p, 1500, 10300, 13200,
               "We evaluate baked meshes from cameras withheld from texture generation and baking.", size=17, height=2300)
    add_text(doc, p, 1500, 14400, 13000, 1200,
             "Study path: executed control → generated views → native-UV bake → unseen-view appearance",
             size=13, color=TEAL, bold=True)
    add_image(doc, p, figs["method"], 15400, 3900, 17000, 9500)
    add_notes(p, NARRATION[1][1])

    # 3. Implemented control
    p = slide_pages[2]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 3, "Follow the executed control, not the schedule label")
    add_text(doc, p, 1700, 3300, 30000, 650,
             "Historical C3 request across 50 denoising steps", size=16, color=GRAY, bold=True)
    xs = [2200, 11900, 21600]
    labels = [("EARLY  ·  0–16", "1.25"), ("MIDDLE  ·  17–32", "2.50"), ("LATE  ·  33–49", "1.25")]
    fills = [0xDCECF2, TEAL, 0xDCECF2]
    for i, (lab, val) in enumerate(labels):
        make_rect(doc, p, xs[i], 4500, 7800, 2600, fills[i])
        col = WHITE if i == 1 else NAVY
        add_text(doc, p, xs[i] + 250, 4850, 7300, 550, lab, size=13, color=col, bold=True, align=1)
        add_text(doc, p, xs[i] + 250, 5450, 7300, 1000, val, size=30, color=col, bold=True, align=1)
    add_text(doc, p, 2200, 7700, 28800, 680,
             "Fresh C: deep and middle groups retain the requested profile; shallow requests are capped at 0.80 in every window.",
             size=16, color=INK)
    make_rect(doc, p, 1800, 9300, 30000, 3200, PALE)
    add_text(doc, p, 2200, 9700, 28600, 600,
             "THREE DISTINCT QUANTITIES", size=12, color=TEAL, bold=True)
    add_text(doc, p, 2200, 10400, 28600, 1600,
             "Requested scale  →  cap-adjusted applied scale  →  state-dependent residual correction\n\nEqual scalar sums do not imply equal accumulated residual dose.",
             size=16, color=NAVY, bold=True)
    add_notes(p, NARRATION[2][1])

    # 4. Competitive controls and qualitative examples
    p = slide_pages[3]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 4, "Strong controls revise the interpretation of C3")
    add_text(doc, p, 1500, 3100, 14200, 600,
             "Fresh C · 300 held-out objects", size=15, color=TEAL, bold=True)
    headers = ["Condition", "FG-PSNR ↑", "FG-LPIPS ↓"]
    rows = [
        ["Fixed Low", "11.31", "0.2051"],
        ["C3 / Middle", "11.83", "0.1998"],
        ["Fixed High", "12.58", "0.1891"],
        ["Generic Linear", "12.42", "0.1862"],
    ]
    x0, y0 = 1500, 4000
    widths = [6000, 4200, 4200]
    h = 1150
    xx = x0
    for j, t in enumerate(headers):
        add_cell(doc, p, xx, y0, widths[j], h, t, fill=NAVY, color=WHITE, size=11, bold=True)
        xx += widths[j]
    for ri, row in enumerate(rows):
        xx = x0
        fill = WHITE if ri % 2 == 0 else 0xEEF3F8
        for j, t in enumerate(row):
            add_cell(doc, p, xx, y0 + h * (ri + 1), widths[j], h, t,
                     fill=fill, color=INK, size=12, bold=(row[0].startswith("C3")))
            xx += widths[j]
    add_text(doc, p, 1500, 9900, 14400, 2100,
             "C3 − Fixed Low: +0.522 dB FG-PSNR, while deep/middle applied sums rise from 62.5 to 82.5.\n\nFixed High and Generic Linear have better means than C3 on all four image endpoints.",
             size=14, color=INK)
    add_text(doc, p, 17000, 3000, 15000, 450,
             "Same target, five conditions, three display objects", size=11, color=GRAY)
    add_image(doc, p, figs["controls"], 16800, 3650, 15800, 10700)
    add_text(doc, p, 16800, 14700, 15800, 700,
             "Examples illustrate condition differences; they do not estimate population performance.",
             size=10, color=GRAY)
    add_notes(p, NARRATION[3][1])

    # 5. Matched budget primary
    p = slide_pages[4]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 5, "Matched applied-scale budgets detect no middle-window advantage")
    add_text(doc, p, 1500, 3150, 30000, 650,
             "Fresh C · N = 300 · per-group applied-scale sums = 82.5 / 82.5 / 40",
             size=15, color=TEAL, bold=True)
    chart_x, chart_y, chart_w = 5000, 6100, 24000
    minv, maxv = -0.15, 0.15
    zero = chart_x + chart_w * (0 - minv) / (maxv - minv)
    low, mean, high = -0.1172, -0.0339, 0.0514
    xlow = chart_x + chart_w * (low - minv) / (maxv - minv)
    xmean = chart_x + chart_w * (mean - minv) / (maxv - minv)
    xhigh = chart_x + chart_w * (high - minv) / (maxv - minv)
    make_rect(doc, p, zero - 18, chart_y - 1300, 36, 3700, 0xB7C3CE)
    make_rect(doc, p, xlow, chart_y, xhigh - xlow, 250, BLUE)
    make_rect(doc, p, xlow - 35, chart_y - 120, 70, 500, BLUE)
    make_rect(doc, p, xhigh - 35, chart_y - 120, 70, 500, BLUE)
    make_rect(doc, p, xmean - 160, chart_y - 160, 320, 570, TEAL)
    add_text(doc, p, chart_x - 450, chart_y - 1000, 1300, 600, "−0.15", size=11, color=GRAY, align=1)
    add_text(doc, p, zero - 500, chart_y - 1000, 1000, 600, "0", size=11, color=GRAY, align=1)
    add_text(doc, p, chart_x + chart_w - 850, chart_y - 1000, 1300, 600, "+0.15", size=11, color=GRAY, align=1)
    add_text(doc, p, chart_x + 200, chart_y + 750, chart_w - 400, 600,
             "Middle-high − mean(Early-high, Late-high) FG-PSNR (dB)", size=13, color=GRAY, align=1)
    add_text(doc, p, 2200, 10400, 28500, 900,
             "−0.0339 dB     95% interval [−0.1172, +0.0514]     p = 0.4324",
             size=21, color=NAVY, bold=True, align=1)
    add_text(doc, p, 2400, 11800, 28000, 1500,
             "The specified primary does not support a middle-window advantage; it also does not establish equivalence.\nRetrospective early/late pairwise contrasts differ in opposite directions, showing placement sensitivity without a preferred schedule.",
             size=14, color=INK, align=1)
    add_notes(p, NARRATION[4][1])

    # 6. Asset-level bake
    p = slide_pages[5]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 6, "A small baked-view effect does not make C3 the winner")
    add_image(doc, p, figs["bake"], 1350, 3800, 17800, 10150)
    add_text(doc, p, 19800, 3350, 12500, 600,
             "GEOTEX BAKE PILOT  ·  N = 10", size=13, color=TEAL, bold=True)
    add_text(doc, p, 19800, 4400, 12500, 2100,
             "Late-high − Fixed Mean\nunseen-view FG-LPIPS\n−0.00265 [−0.00414, −0.00137]",
             size=17, color=NAVY, bold=True)
    add_text(doc, p, 19800, 7000, 12500, 1700,
             "All ten objects favored Late-high. The change closes 3.7% of the mean reference self-bake gap.",
             size=14, color=INK)
    make_rect(doc, p, 19700, 9400, 12600, 3600, PALE)
    add_text(doc, p, 20100, 9750, 11800, 2600,
             "Late-high is distinct from C3. The separate GSO bake (N = 20) did not detect the same benefit: +0.000084 LPIPS, interval [−0.000103, +0.000286].\n\nCompatibility-selected pilot; substantial reference-appearance error remains.",
             size=13, color=INK)
    add_notes(p, NARRATION[5][1])

    # 7. Appearance/fidelity boundary
    p = slide_pages[6]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 7, "Image-space gains do not imply faithful reference appearance")
    add_image(doc, p, figs["appearance"], 2300, 3400, 29300, 12100)
    make_rect(doc, p, 2000, 15800, 29700, 900, PALE)
    add_text(doc, p, 2300, 15950, 29000, 650,
             "Reference-color and texture discrepancies remain visible. Unlit base-color renders do not establish PBR or material fidelity.",
             size=13, color=NAVY, bold=True, align=1)
    add_notes(p, NARRATION[6][1])

    # 8. Transfer boundaries
    p = slide_pages[7]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 8, "Native-interface tests bound transfer across implementations")
    add_text(doc, p, 1500, 3050, 30000, 650,
             "Study-specific middle-window FG-PSNR primary contrasts · pointwise 95% intervals",
             size=14, color=TEAL, bold=True)
    plot_x, plot_y, plot_w = 9000, 5100, 19000
    minv, maxv = -0.14, 0.10
    zero = plot_x + plot_w * (0 - minv) / (maxv - minv)
    make_rect(doc, p, zero - 18, plot_y - 950, 36, 8500, 0xAFC0CC)
    contrasts = [
        ("GeoTex Fresh C · N=300", -0.0339, -0.1172, 0.0514),
        ("MV-Adapter50 · N=50", 0.0290, -0.0194, 0.0807),
        ("GSO100 · N=100", -0.0137, -0.0306, 0.0035),
    ]
    rowy = [5700, 8300, 10900]
    for (label, value, lo, hi), yy in zip(contrasts, rowy):
        add_text(doc, p, 1500, yy - 220, 7300, 720, label, size=13, color=INK, bold=True)
        xlo = plot_x + plot_w * (lo - minv) / (maxv - minv)
        xval = plot_x + plot_w * (value - minv) / (maxv - minv)
        xhi = plot_x + plot_w * (hi - minv) / (maxv - minv)
        make_rect(doc, p, xlo, yy, xhi - xlo, 170, BLUE)
        make_rect(doc, p, xlo - 30, yy - 100, 60, 370, BLUE)
        make_rect(doc, p, xhi - 30, yy - 100, 60, 370, BLUE)
        make_rect(doc, p, xval - 120, yy - 120, 240, 410, TEAL)
        add_text(doc, p, 28100, yy - 250, 4500, 700,
                 f"{value:+.3f} dB", size=12, color=NAVY, bold=True)
    add_text(doc, p, plot_x - 200, 13200, 1800, 450, "−0.14", size=10, color=GRAY)
    add_text(doc, p, zero - 150, 13200, 900, 450, "0", size=10, color=GRAY, align=1)
    add_text(doc, p, plot_x + plot_w - 500, 13200, 900, 450, "+0.10", size=10, color=GRAY, align=2)
    add_text(doc, p, 1600, 14250, 29800, 1300,
             "All three intervals include zero. The studies use separate cohorts and study-specific contrasts; GSO100 shares the MV-Adapter interface and is not an independent backbone replication.",
             size=13, color=INK, align=1)
    add_notes(p, NARRATION[7][1])

    # 9. Contributions and limits
    p = slide_pages[8]
    make_rect(doc, p, 0, 0, W, H, LIGHT)
    add_header(doc, p, 9, "The contribution is an evidence chain for deployed geometry control")
    cards = [
        (1400, "01  IMPLEMENTATION", "Separate requested scales, cap-adjusted applied scales, and state-dependent residual corrections."),
        (11800, "02  CONTROLLED COMPARISONS", "Compare C3 with strong fixed and linear controls and a matched applied-scale timing test."),
        (22200, "03  ASSET-LEVEL EVALUATION", "Connect image-space results to native-UV bakes from unseen cameras and report transfer boundaries."),
    ]
    for x, heading, body in cards:
        make_rect(doc, p, x, 4700, 9400, 5600, WHITE)
        make_rect(doc, p, x, 4700, 9400, 160, TEAL)
        add_text(doc, p, x + 400, 5200, 8600, 850, heading, size=13, color=TEAL, bold=True)
        add_text(doc, p, x + 400, 6350, 8600, 3400, body, size=16, color=NAVY, bold=True)
    make_rect(doc, p, 1500, 11200, 29800, 2800, PALE)
    add_text(doc, p, 1900, 11550, 29000, 2100,
             "The evidence supports reporting the executed interface, applied control, cohort, and asset-level response.\nIt does not identify a universally preferred schedule or establish faithful material reproduction.",
             size=16, color=NAVY, bold=True, align=1)
    add_notes(p, NARRATION[8][1])

    # 10. Conclusion and data access
    p = slide_pages[9]
    make_rect(doc, p, 0, 0, W, H, NAVY)
    make_rect(doc, p, 0, 0, 360, H, TEAL)
    add_text(doc, p, 1900, 1000, 29000, 500,
             "CONCLUSION  |  LIMITED PUBLIC DATA", size=12, color=0xB9E3E5, bold=True)
    add_text(doc, p, 1900, 2050, 29400, 1900,
             "No universal timing winner.\nThe baked asset remains the graphics endpoint.",
             size=27, color=WHITE, bold=True)
    add_text(doc, p, 1900, 5200, 29300, 1700,
             "C3 improves over Fixed Low, but stronger controls lead on mean image endpoints. The matched-budget primary detects no middle-window advantage. A small GeoTex bake benefit does not recur in the separate GSO protocol.",
             size=16, color=WHITE)
    make_rect(doc, p, 1800, 8100, 29600, 4300, 0x24465F)
    add_text(doc, p, 2250, 8500, 28600, 600,
             "ZENODO · VERSION 1.0.1 · LIMITED DERIVED DATA", size=12, color=0xB9E3E5, bold=True)
    add_text(doc, p, 2250, 9350, 28600, 850,
             "DOI: 10.5281/zenodo.23383807", size=24, color=WHITE, bold=True)
    add_text(doc, p, 2250, 10500, 28600, 1200,
             "Selected object-level metrics and attribution records. Source meshes, textures, model weights, checkpoints, generated-image archives, and participant-level responses are excluded.",
             size=13, color=0xE4EDF4)
    add_text(doc, p, 1900, 14900, 28600, 750,
             "Thank you", size=19, color=WHITE, bold=True)
    add_text(doc, p, 1900, 15800, 28600, 600,
             "https://doi.org/10.5281/zenodo.23383807", size=12, color=0xB9E3E5)
    add_notes(p, NARRATION[9][1])

    pptx_path = OUT / "TCAS_Demo_V5.pptx"
    doc.storeAsURL(uno.systemPathToFileUrl(str(pptx_path)),
                   (pv("FilterName", "Impress MS PowerPoint 2007 XML"), pv("Overwrite", True)))
    doc.close(True)
    return pptx_path


def export_pdf_and_video(pptx_path):
    pdf = OUT / "TCAS_Demo_V5.pdf"
    if pdf.exists():
        pdf.unlink()
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(pptx_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    slide_dir = BUILD / "slides"
    slide_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "pdftoppm", "-png", "-r", "144", str(pdf), str(slide_dir / "slide")
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Normalize the PDF render to exact 16:9 HD frame files used by ffmpeg.
    normalized = []
    for i, raw in enumerate(sorted(slide_dir.glob("slide-*.png")), 1):
        target = slide_dir / f"frame-{i:02d}.png"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(raw), "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white",
            "-frames:v", "1", str(target), "-loglevel", "error"
        ], check=True)
        normalized.append(target)
    concat = BUILD / "slides.ffconcat"
    with concat.open("w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for frame in normalized:
            f.write(f"file '{frame.as_posix()}'\n")
            f.write("duration 9\n")
        f.write(f"file '{normalized[-1].as_posix()}'\n")
    silent = OUT / "TCAS_Demo_V5_Silent.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium",
        "-crf", "21", "-movflags", "+faststart", "-an", str(silent), "-loglevel", "error"
    ], check=True)
    return pdf, silent, normalized


def write_script_and_manifest(pptx, pdf, silent, normalized_slides):
    script = OUT / "TCAS_Demo_V5_Narration_EN.md"
    with script.open("w", encoding="utf-8") as f:
        f.write("# TCAS Demo V5 — English narration script\n\n")
        f.write("Delivery: clear, neutral, steady pace. Speaker notes in the PowerPoint use the same text.\n\n")
        for heading, paragraph in NARRATION:
            f.write(f"## {heading}\n\n{paragraph}\n\n")
        f.write("Voiceover status: audio synthesis pending local OPENAI_API_KEY configuration.\n")
    still = OUT / "TCAS_Demo_V5_Still.png"
    subprocess.run(["cp", str(normalized_slides[5]), str(still)], check=True)
    readme = OUT / "README_PRESENTATION_DEMO_V5.md"
    readme.write_text(
        "# V5 presentation and demo\n\n"
        "These companion files follow the current V5 manuscript and are separate from the journal `UPLOAD_FILES` directory.\n\n"
        "- `TCAS_Demo_V5.pptx`: editable 10-slide deck; speaker notes match the narration script.\n"
        "- `TCAS_Demo_V5.pdf`: review copy of the deck.\n"
        "- `TCAS_Demo_V5_Silent.mp4`: 90-second, 1080p silent slideshow demo.\n"
        "- `TCAS_Demo_V5_Still.png`: baked-asset slide preview.\n"
        "- `TCAS_Demo_V5_Narration_EN.md`: slide-by-slide English voiceover script.\n"
        "- `build_v5_demo.py`: rebuilds the deck and silent video from the V5 figure PDFs.\n\n"
        "A narrated MP4 is not included yet. The local OpenAI speech API credential was not available during this build; the old 0907 audio was not reused because it does not match V5.\n\n"
        "The display examples are illustrative. All quantitative claims are taken from V5; no experimental results or cohort statistics were changed.\n",
        encoding="utf-8",
    )
    manifest = {
        "version": "V5",
        "source_manuscript": "FINAL_V5_MANUSCRIPT.pdf",
        "slides": 10,
        "silent_video_seconds_nominal": 90,
        "silent_video_resolution": "1920x1080",
        "narrated_video": "pending local OPENAI_API_KEY",
        "doi": "10.5281/zenodo.23383807",
        "files": [p.name for p in (pptx, pdf, silent, still, script, readme, Path(__file__))],
        "note": "The PowerPoint speaker notes and narration script carry matching V5 wording.",
    }
    (OUT / "PRESENTATION_DEMO_MANIFEST_V5.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    checksum_files = [pptx, pdf, silent, still, script, readme, Path(__file__)]
    with (OUT / "SHA256SUMS_PRESENTATION_DEMO_V5.txt").open("w", encoding="utf-8") as f:
        for path in checksum_files:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            f.write(f"{digest}  {path.name}\n")


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    figs = prepare_figures()
    pptx = build_slide_deck(figs)
    pdf, silent, normalized_slides = export_pdf_and_video(pptx)
    write_script_and_manifest(pptx, pdf, silent, normalized_slides)
    print(json.dumps({
        "pptx": str(pptx),
        "pdf": str(pdf),
        "silent_mp4": str(silent),
        "narration_script": str(OUT / "TCAS_Demo_V5_Narration_EN.md"),
        "slides": 10,
        "voiceover": "pending local OPENAI_API_KEY",
    }, indent=2))


if __name__ == "__main__":
    main()
