"""Build the 1014finalv1 manuscript and supplement in an isolated directory."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
VENDOR = ROOT / "vendor"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
SECTIONS = ROOT / "sections"
DOCUMENTS = ["1014finalv1", "Supplementary_1014finalv1"]


def main():
    BUILD.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mv-painter-1014finalv1-") as name:
        stage = Path(name)
        for filename in ["cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"]:
            shutil.copy2(VENDOR / filename, stage / filename)
        for document in DOCUMENTS:
            shutil.copy2(ROOT / f"{document}.tex", stage / f"{document}.tex")
        for filename in ["fig2.pdf", "fig3.pdf"]:
            shutil.copy2(ROOT / filename, stage / filename)
        for directory in ["figures", "tables", "sections"]:
            shutil.copytree(ROOT / directory, stage / directory)

        for document in DOCUMENTS:
            for pass_number in range(1, 4):
                log_path = BUILD / f"{document}.pass{pass_number}.txt"
                with log_path.open("w") as log:
                    subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                         "-output-directory", str(BUILD), f"{document}.tex"],
                        cwd=stage, stdout=log, stderr=subprocess.STDOUT, check=True)
            log_text = (BUILD / f"{document}.log").read_text(errors="replace")
            if re.search(r"^!", log_text, re.M):
                raise RuntimeError(f"LaTeX error in {document}")
            if "undefined references" in log_text.lower():
                raise RuntimeError(f"Undefined references in {document}")
            if "undefined citations" in log_text.lower():
                raise RuntimeError(f"Undefined citations in {document}")
            shutil.copy2(BUILD / f"{document}.pdf", ROOT / f"{document}.pdf")
            print(f"Built {document}.pdf")

    report = {
        "status": "PASS",
        "engine": "pdflatex",
        "passes_per_document": 3,
        "checks": ["no LaTeX errors", "no undefined references", "no undefined citations"],
        "artifacts": {},
    }
    for filename in [f"{document}.pdf" for document in DOCUMENTS]:
        path = ROOT / filename
        report["artifacts"][filename] = {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (ROOT / "BUILD_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
