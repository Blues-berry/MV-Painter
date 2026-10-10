#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../source_01549"
python3 "${SCRIPT_DIR}/verify_baseline_source.py"
mkdir -p "${SCRIPT_DIR}/build"
cd "${SOURCE_DIR}"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="${SCRIPT_DIR}/build" "${SCRIPT_DIR}/final_0903.tex"
