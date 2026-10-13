#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build/Response_to_Reviewers_conservative_submission_r2"
mkdir -p "${BUILD_DIR}"
pandoc "${SCRIPT_DIR}/Response_to_Reviewers_conservative_submission_r2.md" -s -o "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.tex"
xelatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.tex"
xelatex -interaction=nonstopmode -halt-on-error -output-directory="${BUILD_DIR}" "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.tex"
pandoc "${SCRIPT_DIR}/Response_to_Reviewers_conservative_submission_r2.md" -o "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.docx"
cp "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.tex" "${SCRIPT_DIR}/Response_to_Reviewers_conservative_submission_r2.tex"
cp "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.pdf" "${SCRIPT_DIR}/Response_to_Reviewers_conservative_submission_r2.pdf"
cp "${BUILD_DIR}/Response_to_Reviewers_conservative_submission_r2.docx" "${SCRIPT_DIR}/Response_to_Reviewers_conservative_submission_r2.docx"
