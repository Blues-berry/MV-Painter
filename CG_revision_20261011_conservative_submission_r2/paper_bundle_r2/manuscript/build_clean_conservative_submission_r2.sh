#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
BUILD_DIR="${SCRIPT_DIR}/build/Manuscript_conservative_submission_r2"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT
mkdir -p "${BUILD_DIR}" "${STAGE_DIR}/figures"
cp "${SCRIPT_DIR}/Manuscript_conservative_submission_r2.tex" "${STAGE_DIR}/Manuscript_conservative_submission_r2.tex"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/fig2.pdf" "${SCRIPT_DIR}/fig3.pdf" "${STAGE_DIR}/"
cp -a "${SCRIPT_DIR}/figures/." "${STAGE_DIR}/figures/"
cd "${STAGE_DIR}"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${STAGE_DIR}/Manuscript_conservative_submission_r2.tex"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${STAGE_DIR}/Manuscript_conservative_submission_r2.tex"
