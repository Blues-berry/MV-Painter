#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../../source_01549"
BUILD_DIR="${SCRIPT_DIR}/build"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT
mkdir -p "${BUILD_DIR}"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/manuscript_round_013.tex" "${SCRIPT_DIR}/Supplementary_round_013.tex" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/fig2.pdf" "${SCRIPT_DIR}/fig3.pdf" "${STAGE_DIR}/"
cp -r "${SCRIPT_DIR}/figures" "${SCRIPT_DIR}/tables" "${SCRIPT_DIR}/sections" "${STAGE_DIR}/"
cd "${STAGE_DIR}"
for doc in manuscript_round_013 Supplementary_round_013; do
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${doc}.tex" >"${BUILD_DIR}/${doc}.pass1.txt"
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${doc}.tex" >"${BUILD_DIR}/${doc}.pass2.txt"
done
