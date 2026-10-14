from pathlib import Path
import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "quality_review"
SOURCE = ROOT / "FINAL_V4_MANUSCRIPT.tex"
B_FIGURE = ROOT / "figures/fig3_bake10_two_object_v4.pdf"
A_FIGURE = OUT / "FIGURE3_A_v4.pdf"

A_BODY = (
    "Figure~\\ref{fig:baked-context} shows the Stone object with the lowest absolute "
    "eleven-view FG-LPIPS among seven display-cleared assets. Its Late-high minus "
    "Fixed Mean difference is only $-0.000464$ FG-LPIPS and $+0.001$ dB FG-PSNR, "
    "so low absolute error does not imply a large schedule effect. The full "
    "ten-object effect distribution remains in Supplementary Section~S5."
)
A_CAPTION = (
    r"\caption{GeoTex Bake10 lowest-absolute-error example at held-out camera 004. "
    r"The Stone object has the lowest existing eleven-view FG-LPIPS among seven "
    r"display-cleared assets, but Late-high minus Fixed Mean is only $-0.000464$ "
    r"FG-LPIPS ($+0.001$ dB FG-PSNR). GT-256 reference self-bake, Fixed Mean, and "
    r"Late-high use one common crop and the same mesh/UVs. This outcome-selected "
    r"example separates absolute error from schedule benefit; it does not show a "
    r"general effect or faithful material reproduction. The complete ten-object "
    r"effect distribution is in Supplementary Section~S5.}"
)


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def compile_variant(tex, variant, page_pdf, page_png):
    with tempfile.TemporaryDirectory(prefix="v4-fig3-pages-") as temp_name:
        stage = Path(temp_name)
        for filename in ("cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"):
            os.symlink(ROOT / "vendor" / filename, stage / filename)
        for folder in ("figures", "tables", "sections", "vendor", "quality_review"):
            os.symlink(ROOT / folder, stage / folder, target_is_directory=True)
        (stage / "FINAL_V4_MANUSCRIPT.tex").write_text(tex)
        for _ in range(3):
            run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "FINAL_V4_MANUSCRIPT.tex"], cwd=stage)
        pdf = stage / "FINAL_V4_MANUSCRIPT.pdf"
        raw = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        pages = raw.split("\f")
        matches = [i + 1 for i, page in enumerate(pages) if "Fig. 3. GeoTex Bake10" in page]
        if len(matches) != 1:
            raise RuntimeError(f"Figure 3 page is ambiguous: {matches}")
        page = matches[0]
        prefix = stage / f"FIGURE3_{variant}_PAGE"
        run(["pdftoppm", "-png", "-singlefile", "-f", str(page), "-l", str(page), "-r", "130", str(pdf), str(prefix)])
        extracted = stage / "page-%d.pdf"
        run(["pdfseparate", "-f", str(page), "-l", str(page), str(pdf), str(extracted)])
        shutil.copy2(stage / f"page-{page}.pdf", page_pdf)
        shutil.copy2(Path(f"{prefix}.png"), page_png)
        return page


def main():
    source = SOURCE.read_text()
    marker = r"\includegraphics[width=\textwidth]{figures/fig3_bake10_two_object_v4.pdf}"
    image_start = source.index(marker)
    block_start = source.rfind(r"\begin{figure*}", 0, image_start)
    block_end = source.index(r"\end{figure*}", image_start) + len(r"\end{figure*}")
    figure = source[block_start:block_end]
    a_figure = figure.replace(marker, r"\includegraphics[width=\textwidth]{quality_review/FIGURE3_A_v4.pdf}")
    cap_start = a_figure.index(r"\caption{")
    cap_end = a_figure.index("\n\\label{fig:baked-context}", cap_start)
    a_figure = a_figure[:cap_start] + A_CAPTION + a_figure[cap_end:]
    a_source = source[:block_start] + a_figure + source[block_end:]
    b_sentence = (
        r"Figure~\ref{fig:baked-context} pairs Tire, selected by median source-foreground "
        r"Laplacian variance among seven display-cleared assets, with the carved font, "
        r"selected post hoc for its largest existing eleven-view LPIPS decrease. The latter "
        r"also has lower PSNR, so the example displays an endpoint tradeoff rather than a "
        r"general benefit. The full ten-object effect distribution and values remain in "
        r"Supplementary Section~S5. These two displays illustrate persistent appearance "
        r"mismatch and small, object-dependent method differences; they do not estimate "
        r"prevalence or establish faithful material reproduction."
    )
    if b_sentence not in a_source:
        raise RuntimeError("Could not locate the Figure 3 discussion for A variant")
    a_source = a_source.replace(b_sentence, A_BODY, 1)

    a_png = OUT / "FIGURE3_A_FINAL_MAIN_PAGE.png"
    b_png = OUT / "FIGURE3_B_FINAL_MAIN_PAGE.png"
    a_page_pdf = OUT / "FIGURE3_A_FINAL_PAGE_9.pdf"
    b_page_pdf = OUT / "FIGURE3_B_FINAL_PAGE_9.pdf"
    a_page = compile_variant(a_source, "A", a_page_pdf, a_png)
    b_page = compile_variant(source, "B", b_page_pdf, b_png)
    if a_page != 9 or b_page != 9:
        a_page_pdf.rename(OUT / f"FIGURE3_A_FINAL_PAGE_{a_page}.pdf")
        b_page_pdf.rename(OUT / f"FIGURE3_B_FINAL_PAGE_{b_page}.pdf")
        a_page_pdf = OUT / f"FIGURE3_A_FINAL_PAGE_{a_page}.pdf"
        b_page_pdf = OUT / f"FIGURE3_B_FINAL_PAGE_{b_page}.pdf"

    a = Image.open(a_png).convert("RGB")
    b = Image.open(b_png).convert("RGB")
    header_h, gap = 54, 20
    canvas = Image.new("RGB", (a.width + gap + b.width, max(a.height, b.height) + header_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
    draw.text((12, 10), "A — lowest absolute LPIPS; near-zero schedule effect", fill=(24, 35, 48), font=font)
    draw.text((a.width + gap + 12, 10), "B — input-property example + explicit post-outcome tradeoff", fill=(24, 35, 48), font=font)
    canvas.paste(a, (0, header_h))
    canvas.paste(b, (a.width + gap, header_h))
    canvas.save(OUT / "FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.png")

    run(["pdfunite", str(a_page_pdf), str(b_page_pdf), str(OUT / "FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.pdf")])
    (OUT / "FIGURE3_PAGE_COMPARISON_V4.json").write_text(
        "{\n"
        f'  "candidate_a_page": {a_page},\n'
        f'  "candidate_b_page": {b_page},\n'
        f'  "candidate_a_page_pdf": "quality_review/{a_page_pdf.name}",\n'
        f'  "candidate_b_page_pdf": "quality_review/{b_page_pdf.name}",\n'
        '  "comparison_pdf": "quality_review/FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.pdf",\n'
        '  "comparison_png": "quality_review/FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.png",\n'
        '  "selection_basis": "Same final prose, with only Figure 3 assets and selection-aligned sentence/caption varied for candidate A; full intermediate manuscripts are compiled in temporary directories and not retained."\n'
        "}\n"
    )
    print(f"Candidate A and B page {a_page} rendered; final manuscript candidate B uses page {b_page}.")


if __name__ == "__main__":
    main()
