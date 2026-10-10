#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
OUT_DIR="${SCRIPT_DIR}/build/marked_up_1008_review4"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT

mkdir -p "${OUT_DIR}" "${STAGE_DIR}/figures"
cp "${SCRIPT_DIR}/../round_008/manuscript_round_008.tex" "${STAGE_DIR}/previous_round.tex"
cp "${SCRIPT_DIR}/manuscript_round_009.tex" "${STAGE_DIR}/Manuscript_round_009.tex"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SOURCE_DIR}"/fig*.pdf "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/fig2.pdf" "${SCRIPT_DIR}/fig3.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/figures/"* "${STAGE_DIR}/figures/"

cd "${STAGE_DIR}"
latexdiff --type=CFONT --flatten --math-markup=0 --graphics-markup=none --floattype=IDENTICAL --exclude-textcmd=section,subsection,subsubsection,paragraph,caption previous_round.tex Manuscript_round_009.tex > Marked-up_Manuscript_round_009.tex
python3 - <<'PY'
from pathlib import Path
path = Path("Marked-up_Manuscript_round_009.tex")
source = path.read_text(encoding="utf-8")
marker = r"\begin{document}"
float_marking = r"""\renewcommand{\DIFaddbeginFL}{}
\renewcommand{\DIFaddendFL}{}
\renewcommand{\DIFdelbeginFL}{}
\renewcommand{\DIFdelendFL}{}
\renewcommand{\DIFaddFL}[1]{#1}
\renewcommand{\DIFdelFL}[1]{}
\setcounter{dbltopnumber}{3}
\renewcommand{\dbltopfraction}{0.90}
\renewcommand{\textfraction}{0.10}
"""
if source.count(marker) != 1:
    raise SystemExit("Expected one document start in latexdiff output")
path.write_text(source.replace(marker, float_marking + marker, 1), encoding="utf-8")
PY
python3 "${SCRIPT_DIR}/strip_latexdiff_deletions.py" Marked-up_Manuscript_round_009.tex Marked-up_Manuscript_round_009.tex
python3 - <<'PY'
from pathlib import Path
path = Path("Marked-up_Manuscript_round_009.tex")
source = path.read_text(encoding="utf-8")
marker = r"\begin{thebibliography}{45}"
if source.count(marker) != 1:
    raise SystemExit("Expected one bibliography in marked-up manuscript")
source = source.replace(marker, marker + "\n\\linespread{0.90}\\selectfont\\setlength{\\itemsep}{-0.6pt}", 1)
path.write_text(source, encoding="utf-8")
PY
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${OUT_DIR}" Marked-up_Manuscript_round_009.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${OUT_DIR}" Marked-up_Manuscript_round_009.tex
