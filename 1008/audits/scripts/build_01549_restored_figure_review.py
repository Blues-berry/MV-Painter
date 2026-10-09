#!/usr/bin/env python3
"""Render the seven authenticated 01549 figures beside the active restored figures."""
from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "manuscript/source_01549"
ACTIVE = ROOT / "manuscript/revision_01549_restored"
OUT = ROOT / "audits/forensics_R2_1_20261008"
RENDERS = OUT / "renders/restored"
FIGDIR = ACTIVE / "figures"
MAIN_TEX = ACTIVE / "manuscript_1008.tex"

ITEMS = [
    {
        "id": 1, "final_no": "1", "original_tex": "103–111", "active_tex": "101–105", "page": "4",
        "assets": [(FIGDIR / "fig1_01549_original.pdf", "yes")],
        "purpose": "Complete pipeline context: reference and geometry conditions, frozen multi-view diffusion, GeoTex residual, TCAS, optional FAC branch, and projection/baking output.",
        "concern": "FAC remains a previously reported auxiliary result with archival limits. Fresh C tests target images only, so the baked mesh cannot be presented as validated.",
        "recommendation": "Keep the original layout and full pipeline, including the optional FAC branch. Limit only the caption claims and link FAC to the reported negative re-examination.",
        "changes": "The original figure asset is byte-identical in the active manuscript. Its caption preserves the optional FAC context, points to the reported negative result, and states that Fresh C does not validate baking.",
        "status": "KEEP_ORIGINAL_LOCAL_CAPTION_EDIT",
    },
    {
        "id": 2, "final_no": "2", "original_tex": "250–257", "active_tex": "223–225", "page": "6",
        "assets": [(ACTIVE / "fig2.pdf", "yes")],
        "purpose": "Fixed-scale curve: the submitted structural and crop-structure trends motivate examining more than one endpoint.",
        "concern": "The source rows, run manifest, and metric implementation cannot be independently reconstructed from the current evidence archive.",
        "recommendation": "Restore the authenticated original curve as historical development evidence, not as a newly verified result.",
        "changes": "Original PDF asset is byte-identical and is cited in the active TeX. Its caption discloses the historical status and missing row-level provenance.",
        "status": "KEEP",
    },
    {
        "id": 3, "final_no": "3", "original_tex": "259–266", "active_tex": "232–234", "page": "6",
        "assets": [(ACTIVE / "fig3.pdf", "yes")],
        "purpose": "50-object × 13-scale heatmap exposes the originally reported object-level response variation.",
        "concern": "The object ordering and per-row outputs are not traceable enough for a current population inference.",
        "recommendation": "Keep the original visual only as a submitted-paper historical diagnostic; do not infer a new response distribution.",
        "changes": "Original PDF asset is byte-identical and is cited in the active TeX. The caption states the provenance limitation.",
        "status": "KEEP",
    },
    {
        "id": 4, "final_no": "4", "original_tex": "267–280", "active_tex": "247–253", "page": "7",
        "assets": [
            (FIGDIR / "fig4_typical_c3_gfl.png", "yes"),
            (FIGDIR / "fig4_adverse_c3_gfl.png", "yes"),
            (FIGDIR / "fig4_generic_linear_counter.png", "yes"),
        ],
        "purpose": "Original selected crops illustrated how fixed scale changed appearance; the research question is whether geometry strength affects texture appearance.",
        "concern": "Crops and selected examples do not establish flattening prevalence or texture fidelity; Reviewer 1 requested whole-object comparisons and baselines.",
        "recommendation": "Replace the crop-only examples with matched, whole-object Fresh C target-view panels and disclose outcome-based selection.",
        "changes": "Three current full-object sheets show near-median, adverse C3–GFL, and Generic Linear counterexample cases across reference and seven conditions. They are illustrative, not prevalence estimates or baked-mesh evidence.",
        "status": "REPLACE_EVIDENCE",
    },
    {
        "id": 5, "final_no": "none", "original_tex": "281–289", "active_tex": "237–242, 315", "page": "5–6",
        "assets": [],
        "purpose": "26-object RGB-standard-deviation and gradient-ratio audit was used to claim high-scale texture flattening.",
        "concern": "Object IDs, subset-selection trace, raw ratios, and executable metric definitions are not recoverable. The proxies measure variation, not fidelity.",
        "recommendation": "Retire the prevalence and texture-loss conclusion until the underlying audit can be reproduced.",
        "changes": "No active figure corresponds to original Fig. 5. The closest current visual context is final Fig. 4, but it is a different Fresh C selected-image study and is not a replacement measurement. The retirement and reason are stated in the main text.",
        "status": "REMOVE",
    },
    {
        "id": 6, "final_no": "5", "original_tex": "323–330", "active_tex": "301–305", "page": "8",
        "assets": [
            (FIGDIR / "fig6_favorable_c3_gfl.png", "yes"),
            (FIGDIR / "fig6_c3_gfh_tradeoff.png", "yes"),
        ],
        "purpose": "GT / fixed-low / fixed-high / C3 comparison gives the original schedule-selection question a qualitative counterpart.",
        "concern": "The original 24-object visuals lack current row-level provenance; selected images alone cannot support a schedule ranking.",
        "recommendation": "Preserve the comparison question with traceable matched Fresh C views, keeping the paired cohort results as the quantitative evidence.",
        "changes": "Final Fig. 5 shows one selected C3-favourable case and one C3–GFH endpoint trade-off on matched target views. These are not the original 24-object probe and do not establish a winner.",
        "status": "REPLACE_EVIDENCE",
    },
    {
        "id": 7, "final_no": "6", "original_tex": "332–339", "active_tex": "310–312", "page": "9",
        "assets": [(FIGDIR / "fig7_c3_development.pdf", "yes")],
        "purpose": "17 schedule variants and C3 on the 24-object development shape–texture plane show the submitted schedule-selection context.",
        "concern": "The former “Promising zone” and “C3 (ours)” wording could imply a verified optimum or method novelty; the point-level data are not available for reanalysis.",
        "recommendation": "Keep the plot and all points, make only local label edits, and state that it is development evidence rather than holdout validation.",
        "changes": "The authenticated original is preserved. The active copy changes only “Promising zone” to “Development region” and “C3 (ours)” to “C3 (probe)”; the caption restricts interpretation to the 24-object development set.",
        "status": "LOCAL_REWRITE",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def render_pdf(path: Path, stem: Path) -> Path:
    stem.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-singlefile", "-r", "125", str(path), str(stem)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return stem.with_suffix(".png")


def current_panel(item: dict) -> Path:
    out = RENDERS / f"current_fig{item['id']}.png"
    if item["id"] == 5:
        image = Image.new("RGB", (1400, 900), (248, 249, 251))
        d = ImageDraw.Draw(image)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        title = ImageFont.truetype(font_path, 52)
        body = ImageFont.truetype(font_path, 34)
        d.rounded_rectangle((40, 40, 1360, 860), radius=28, fill="white", outline=(170, 180, 190), width=4)
        d.text((100, 150), "No active counterpart", font=title, fill=(40, 52, 66))
        d.text((100, 270), "Original Fig. 5 was retired", font=body, fill=(75, 87, 101))
        d.text((100, 340), "26-object proxy audit lacks traceable rows", font=body, fill=(75, 87, 101))
        d.text((100, 410), "and reproducible metric definitions.", font=body, fill=(75, 87, 101))
        d.text((100, 560), "Final Fig. 4 shows different Fresh C visual evidence;", font=body, fill=(75, 87, 101))
        d.text((100, 630), "it is not a replacement for the retired ratios.", font=body, fill=(75, 87, 101))
        image.save(out)
        return out
    paths = [path for path, _ in item["assets"]]
    panels: list[Image.Image] = []
    for index, path in enumerate(paths):
        if path.suffix.lower() == ".pdf":
            panel_path = render_pdf(path, RENDERS / f"render_{path.stem}")
            panel = Image.open(panel_path).convert("RGB")
        else:
            panel = Image.open(path).convert("RGB")
            # Match the active TeX trim of 36 points from the image bottom.
            trim = min(panel.height, round(36 * panel.width / 1392))
            if trim:
                panel = panel.crop((0, 0, panel.width, panel.height - trim))
        panels.append(panel)
    if len(panels) == 1:
        panels[0].save(out)
        return out
    width = max(panel.width for panel in panels)
    gap = 24
    height = sum(panel.height for panel in panels) + gap * (len(panels) - 1)
    composite = Image.new("RGB", (width, height), "white")
    y = 0
    for panel in panels:
        composite.paste(panel, ((width - panel.width) // 2, y))
        y += panel.height + gap
    composite.save(out)
    return out


def fit_box(path: Path, width: float, height: float) -> tuple[float, float]:
    with Image.open(path) as im:
        return min(width / im.width, height / im.height), im.size


def draw_fit(c: canvas.Canvas, path: Path, box: tuple[float, float, float, float]) -> None:
    x, y, width, height = box
    scale, (iw, ih) = fit_box(path, width, height)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x + (width - dw) / 2, y + (height - dh) / 2,
                width=dw, height=dh, preserveAspectRatio=True, mask="auto")


def build_manifest() -> None:
    out = OUT / "RESTORED_FIGURE_ASSET_MANIFEST.csv"
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow([
            "original_figure", "final_figure", "disposition", "original_tex_lines", "active_tex_lines",
            "active_pdf_page", "original_asset", "original_sha256", "active_assets_path=sha256",
            "referenced_by_active_main_tex",
        ])
        for item in ITEMS:
            original = SOURCE / f"fig{item['id']}.pdf"
            writer.writerow([
                f"Fig. {item['id']}", f"Fig. {item['final_no']}", item["status"],
                item["original_tex"], item["active_tex"], item["page"],
                str(original.relative_to(ROOT)), sha256(original),
                "; ".join(f"{p.relative_to(ROOT)}={sha256(p)}" for p, _ in item["assets"]) or "NONE",
                "yes" if item["assets"] else "no",
            ])


def build_pdf() -> None:
    page_w, page_h = landscape(A4)
    path = OUT / "01549_original_vs_current_figures_internal.pdf"
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h), pageCompression=1)
    style = ParagraphStyle("notes", fontName="Helvetica", fontSize=8.4, leading=10.6,
                           textColor=colors.HexColor("#202833"))
    for item in ITEMS:
        idx = item["id"]
        original = render_pdf(SOURCE / f"fig{idx}.pdf", RENDERS / f"original_fig{idx}")
        current = current_panel(item)
        c.setFont("Helvetica-Bold", 14.5)
        c.setFillColor(colors.HexColor("#182536"))
        c.drawString(34, page_h - 29, f"Authenticated 01549 Figure {idx}  |  Active final Figure {item['final_no']}")
        c.setFont("Helvetica", 8)
        c.drawString(38, page_h - 46,
                     f"Original TeX {item['original_tex']}  |  SHA-256 {sha256(SOURCE / f'fig{idx}.pdf')[:12]}…")
        final_label = item["final_no"] if item["final_no"] != "none" else "—"
        c.drawString(430, page_h - 46, f"Active final Fig. {final_label}  |  TeX {item['active_tex']}  |  p. {item['page']}")
        c.setStrokeColor(colors.HexColor("#A8B1BC"))
        c.rect(34, 250, 374, 260, stroke=1, fill=0)
        c.rect(422, 250, 386, 260, stroke=1, fill=0)
        draw_fit(c, original, (40, 256, 362, 248))
        draw_fit(c, current, (428, 256, 374, 248))
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#39495A"))
        c.drawString(40, 519, "ORIGINAL SUBMISSION")
        c.drawString(428, 519, "ACTIVE RESTORED REVISION")
        if not item["assets"]:
            c.setFillColor(colors.HexColor("#8A3B12"))
            c.drawString(430, 239, "No active figure; retirement is explicit in the manuscript.")
        y = 226
        for label, key in [
            ("Argument function", "purpose"),
            ("Reviewer concern", "concern"),
            ("Recommended preservation", "recommendation"),
            ("Changes / remaining limit", "changes"),
        ]:
            p = Paragraph(f"<b>{label}.</b> {item[key]}", style)
            _, h = p.wrap(page_w - 72, y)
            y -= h
            p.drawOn(c, 36, y)
            y -= 5
        c.setFont("Helvetica", 6.7)
        c.setFillColor(colors.HexColor("#606D7B"))
        active_hashes = ", ".join(sha256(p)[:12] for p, _ in item["assets"]) or "no active asset"
        c.drawString(36, 18, f"Disposition: {item['status']}  |  Active asset SHA-256 prefix: {active_hashes}")
        c.showPage()
    c.save()


def build_preview() -> None:
    tile_w, tile_h = 720, 460
    sheet = Image.new("RGB", (2 * tile_w, 7 * tile_h), (246, 247, 249))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 21)
    for item in ITEMS:
        idx = item["id"]
        current = current_panel(item)
        original = RENDERS / f"original_fig{idx}.png"
        for col, (label, path) in enumerate([("Original 01549", original), ("Active restored", current)]):
            x, y = col * tile_w, (idx - 1) * tile_h
            draw.text((x + 14, y + 10), f"Fig. {idx} — {label}", font=font, fill=(26, 38, 52))
            image = Image.open(path).convert("RGB")
            image = ImageOps.contain(image, (tile_w - 28, tile_h - 54))
            sheet.paste(image, (x + (tile_w - image.width) // 2,
                                y + 38 + (tile_h - 54 - image.height) // 2))
            draw.rectangle((x + 4, y + 4, x + tile_w - 4, y + tile_h - 4), outline=(180, 188, 198), width=1)
    target = RENDERS / "all_figures_restored_preview.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


if __name__ == "__main__":
    RENDERS.mkdir(parents=True, exist_ok=True)
    for item in ITEMS:
        render_pdf(SOURCE / f"fig{item['id']}.pdf", RENDERS / f"original_fig{item['id']}")
    build_manifest()
    build_pdf()
    build_preview()
    print(OUT / "01549_original_vs_current_figures_internal.pdf")
    print(OUT / "RESTORED_FIGURE_ASSET_MANIFEST.csv")
