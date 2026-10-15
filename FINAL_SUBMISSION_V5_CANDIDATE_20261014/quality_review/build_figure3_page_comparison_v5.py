from pathlib import Path
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "quality_review"
SOURCE = ROOT / "FINAL_V5_MANUSCRIPT.tex"
A_FIGURE = OUT / "FIGURE3_A_v5.pdf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("V5Sans", FONT_PATH))


def build_clean_a_figure():
    selection = json.loads((OUT / "FIGURE3_A_SELECTION_V5.json").read_text())
    row = selection["rows"][0]
    height = 178
    c = canvas.Canvas(str(A_FIGURE), pagesize=(576, height))
    c.setTitle("Figure 3 candidate A — Stone")
    labels = ["GT-256 self-bake", "Fixed Mean", "Late-high"]
    margin, gap = 12, 10
    column_width = (576 - 2 * margin - 2 * gap) / 3
    c.setFont("V5Sans", 8.6)
    c.setFillColorRGB(0.10, 0.15, 0.22)
    for j, label in enumerate(labels):
        c.drawString(margin + j * (column_width + gap) + 3, height - 14, label)
    c.drawString(12, height - 31, "Stone")
    for j, panel in enumerate(row["panels"]):
        if panel["label"] != labels[j]:
            raise RuntimeError("Candidate A panel order changed")
        path = ROOT / panel["display_asset"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != panel["display_sha256"]:
            raise RuntimeError(f"Candidate A source hash mismatch: {path}")
        x = margin + j * (column_width + gap)
        y, panel_h = 22, 118
        c.setStrokeColorRGB(0.78, 0.81, 0.85)
        c.setLineWidth(0.4)
        c.rect(x, y, column_width, panel_h)
        c.drawImage(ImageReader(str(path)), x + 3, y + 3, column_width - 6,
                    panel_h - 6, preserveAspectRatio=True, anchor="c", mask="auto")
    c.save()

A_BODY = (
    "Figure~\\ref{fig:baked-context} shows Stone, which has the lowest absolute "
    "eleven-view FG-LPIPS among seven display-cleared assets. Its Late-high minus "
    "Fixed Mean difference is $-0.000464$ FG-LPIPS and $+0.001$ dB FG-PSNR. "
    "The full ten-object effect distribution is in Supplementary Section~S5."
)
A_CAPTION = (
    r"\caption{GeoTex Bake10 appearance at held-out camera 004 for Stone. The "
    r"row shows a GT-256 reference self-bake, Fixed Mean, and Late-high under a "
    r"shared mesh/UV and within-object crop. The object has the lowest absolute "
    r"eleven-view FG-LPIPS among seven display-cleared assets, while the Late-high "
    r"minus Fixed Mean difference is $-0.000464$ FG-LPIPS and $+0.001$ dB FG-PSNR. "
    r"Source images are 512$\times$512 and shown without method-specific color edits. "
    r"The ten-object effect distribution and full credits are in Supplementary Section~S5.}"
)


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def compile_variant(tex, variant):
    with tempfile.TemporaryDirectory(prefix="v5-fig3-pages-") as temp_name:
        stage = Path(temp_name)
        for filename in ("cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"):
            (stage / filename).symlink_to(ROOT / "vendor" / filename)
        for folder in ("figures", "tables", "sections", "quality_review"):
            (stage / folder).symlink_to(ROOT / folder, target_is_directory=True)
        (stage / "FINAL_V5_MANUSCRIPT.tex").write_text(tex)
        for _ in range(3):
            run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "FINAL_V5_MANUSCRIPT.tex"], cwd=stage)
        pdf = stage / "FINAL_V5_MANUSCRIPT.pdf"
        raw = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        matches = [i + 1 for i, page in enumerate(raw.split("\f")) if "Fig. 3. GeoTex Bake10" in page]
        if len(matches) != 1:
            raise RuntimeError(f"Figure 3 page is ambiguous for {variant}: {matches}")
        page = matches[0]
        prefix = stage / f"FIGURE3_{variant}_PAGE"
        run(["pdftoppm", "-png", "-singlefile", "-f", str(page), "-l", str(page), "-r", "130", str(pdf), str(prefix)])
        run(["pdfseparate", "-f", str(page), "-l", str(page), str(pdf), str(stage / "page-%d.pdf")])
        extracted = stage / f"page-{page}.pdf"
        page_pdf = OUT / f"FIGURE3_{variant}_FINAL_PAGE_{page}_V5.pdf"
        page_png = OUT / f"FIGURE3_{variant}_FINAL_MAIN_PAGE_V5.png"
        shutil.copy2(extracted, page_pdf)
        shutil.copy2(Path(f"{prefix}.png"), page_png)
        return page, page_pdf, page_png


def main():
    build_clean_a_figure()
    source = SOURCE.read_text()
    marker = r"\includegraphics[width=\textwidth]{figures/fig3_bake10_two_object_v5.pdf}"
    image_start = source.index(marker)
    block_start = source.rfind(r"\begin{figure*}", 0, image_start)
    block_end = source.index(r"\end{figure*}", image_start) + len(r"\end{figure*}")
    block = source[block_start:block_end]
    a_figure = block.replace(marker, r"\includegraphics[width=\textwidth]{quality_review/FIGURE3_A_v5.pdf}")
    cap_start = a_figure.index(r"\caption{")
    cap_end = a_figure.index("\n\\label{fig:baked-context}", cap_start)
    a_figure = a_figure[:cap_start] + A_CAPTION + a_figure[cap_end:]
    a_source = source[:block_start] + a_figure + source[block_end:]
    b_sentence = (
        r"Generated-view and baked-view ranking associations and per-object winner changes are descriptive "
        r"and remain in Supplementary Section~S5; they do not establish a general ranking reversal. "
        r"Figure~\ref{fig:baked-context} pairs the reference and generated bakes for Tire and the "
        r"baptismal font at held-out camera 004; the ten-object distribution remains the inferential result."
    )
    if b_sentence not in a_source:
        raise RuntimeError("Could not locate the V5 Figure 3 discussion for the A variant")
    a_source = a_source.replace(b_sentence, A_BODY, 1)

    a_page, a_pdf, a_png = compile_variant(a_source, "A")
    b_page, b_pdf, b_png = compile_variant(source, "B")
    a = Image.open(a_png).convert("RGB")
    b = Image.open(b_png).convert("RGB")
    header_h, gap = 54, 20
    canvas = Image.new("RGB", (a.width + gap + b.width, max(a.height, b.height) + header_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
    draw.text((12, 10), "A — Stone; near-zero schedule effect", fill=(24, 35, 48), font=font)
    draw.text((a.width + gap + 12, 10), "B — Tire and baptismal font; two-object comparison", fill=(24, 35, 48), font=font)
    canvas.paste(a, (0, header_h))
    canvas.paste(b, (a.width + gap, header_h))
    comparison_png = OUT / "FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.png"
    comparison_pdf = OUT / "FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.pdf"
    canvas.save(comparison_png)
    run(["pdfunite", str(a_pdf), str(b_pdf), str(comparison_pdf)])
    (OUT / "FIGURE3_PAGE_COMPARISON_V5.json").write_text(
        "{\n"
        f'  "candidate_a_page": {a_page},\n'
        f'  "candidate_b_page": {b_page},\n'
        f'  "candidate_a_page_pdf": "quality_review/{a_pdf.name}",\n'
        f'  "candidate_b_page_pdf": "quality_review/{b_pdf.name}",\n'
        f'  "comparison_pdf": "quality_review/{comparison_pdf.name}",\n'
        f'  "comparison_png": "quality_review/{comparison_png.name}",\n'
        '  "selection_basis": "Both variants compile the complete V5 manuscript; only Figure 3 image, aligned caption, and adjacent explanatory sentence differ. The final V5 manuscript uses candidate B."\n'
        "}\n"
    )
    print(f"Candidate A page {a_page}; candidate B page {b_page}. V5 manuscript retains candidate B.")


if __name__ == "__main__":
    main()
