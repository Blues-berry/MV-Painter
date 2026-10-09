#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
BUILD_DIR="${SCRIPT_DIR}/build/supplement_1008"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT
mkdir -p "${BUILD_DIR}" "${STAGE_DIR}/figures"
cp "${SCRIPT_DIR}/Supplementary_1008.tex" "${STAGE_DIR}/Supplementary_1008.tex"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/figures/figS1_adverse_c3_gfl.png" "${SCRIPT_DIR}/figures/figS1_color_detail_failure.png" "${STAGE_DIR}/figures/"
cd "${STAGE_DIR}"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="${BUILD_DIR}" Supplementary_1008.tex
