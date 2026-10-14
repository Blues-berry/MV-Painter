#!/usr/bin/env python3
"""Compile the committed V4 marked manuscript from its portable TeX source."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKED = ROOT / "marked" / "FINAL_V4_MARKED_MANUSCRIPT.tex"

def main():
    build = ROOT / "marked" / "build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="marked-v4-") as name:
        stage = Path(name)
        for filename in ("cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"):
            shutil.copy2(ROOT / "vendor" / filename, stage / filename)
        for folder in ("figures", "tables", "sections"):
            shutil.copytree(ROOT / folder, stage / folder)
        shutil.copy2(MARKED, stage / MARKED.name)
        for number in range(1, 4):
            with (build / f"marked_pass{number}.log").open("w") as log:
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MARKED.name],
                               cwd=stage, stdout=log, stderr=subprocess.STDOUT, check=True)
        final_log = (stage / "FINAL_V4_MARKED_MANUSCRIPT.log").read_text(errors="replace").lower()
        if "undefined references" in final_log or "undefined citations" in final_log:
            raise RuntimeError("Undefined citation/reference in marked manuscript")
        shutil.copy2(stage / "FINAL_V4_MARKED_MANUSCRIPT.pdf", ROOT / "FINAL_V4_MARKED_MANUSCRIPT.pdf")
    print("Built FINAL_V4_MARKED_MANUSCRIPT.pdf")

if __name__ == "__main__":
    main()
