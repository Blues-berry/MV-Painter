#!/usr/bin/env python3
"""Compile the committed V4 marked manuscript from its portable TeX source."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKED = ROOT / "marked" / "FINAL_V4_MARKED_MANUSCRIPT.tex"

def main():
    with tempfile.TemporaryDirectory(prefix="marked-v4-") as name:
        stage = Path(name)
        for filename in ("cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"):
            shutil.copy2(ROOT / "vendor" / filename, stage / filename)
        for folder in ("figures", "tables", "sections"):
            shutil.copytree(ROOT / folder, stage / folder)
        shutil.copy2(MARKED, stage / MARKED.name)
        for _ in range(3):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MARKED.name],
                           cwd=stage, stdout=subprocess.DEVNULL, check=True)
        shutil.copy2(stage / "FINAL_V4_MARKED_MANUSCRIPT.pdf", ROOT / "FINAL_V4_MARKED_MANUSCRIPT.pdf")
    print("Built FINAL_V4_MARKED_MANUSCRIPT.pdf")

if __name__ == "__main__":
    main()
