#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
BUILD_DIR="${SCRIPT_DIR}/build/manuscript_1008"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf -- "${STAGE_DIR}"' EXIT
mkdir -p "${BUILD_DIR}" "${STAGE_DIR}/figures"
cp "${SCRIPT_DIR}/manuscript_1008.tex" "${STAGE_DIR}/manuscript_1008.tex"
cp "${SOURCE_DIR}/cag.sty" "${SOURCE_DIR}/elsarticle.cls" "${SOURCE_DIR}/cag-logo.pdf" "${SOURCE_DIR}/elsevier-logo.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/fig2.pdf" "${SCRIPT_DIR}/fig3.pdf" "${STAGE_DIR}/"
cp "${SCRIPT_DIR}/figures/"* "${STAGE_DIR}/figures/"
cd "${STAGE_DIR}"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="${BUILD_DIR}" manuscript_1008.tex
