#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
BUILD_DIR="${SCRIPT_DIR}/build/supplement_round_010"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT
mkdir -p "${BUILD_DIR}" "${STAGE_DIR}/figures" "${STAGE_DIR}/tables"
cp "${SCRIPT_DIR}/Supplementary_round_010.tex" "${STAGE_DIR}/Supplementary_round_010.tex"
cp "${SCRIPT_DIR}/tables/mvadapter_layerwise_supplement.tex" "${STAGE_DIR}/tables/"
cp "${SCRIPT_DIR}/tables/mvdiffusion_raw_contrasts.tex" "${STAGE_DIR}/tables/"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/figures/"* "${STAGE_DIR}/figures/"
cp "${SCRIPT_DIR}/tables/native_round009_complete.tex" "${STAGE_DIR}/tables/"
cp "${SCRIPT_DIR}/tables/native_round010_complete.tex" "${STAGE_DIR}/tables/"
cd "${STAGE_DIR}"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" Supplementary_round_010.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" Supplementary_round_010.tex
