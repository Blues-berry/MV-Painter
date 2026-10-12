"""Portable three-pass build; resolve page-dependent outer-margin line numbers."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"


def main():
    BUILD.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cg-round014-") as name:
        stage = Path(name)
        for filename in ["cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"]:
            shutil.copy2(ROOT / "vendor/source_01549" / filename, stage / filename)
        for filename in ["manuscript_round_014.tex", "Supplementary_round_014.tex", "fig2.pdf", "fig3.pdf"]:
            shutil.copy2(ROOT / filename, stage / filename)
        for dirname in ["figures", "tables", "sections"]:
            shutil.copytree(ROOT / dirname, stage / dirname)
        for doc in ["manuscript_round_014", "Supplementary_round_014"]:
            for pass_number in [1, 2, 3]:
                with (BUILD / f"{doc}.pass{pass_number}.txt").open("w") as log:
                    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                                    f"-output-directory={BUILD}", f"{doc}.tex"],
                                   cwd=stage, stdout=log, stderr=subprocess.STDOUT, check=True)
            print(f"Built {doc}.pdf", flush=True)


if __name__ == "__main__":
    main()
