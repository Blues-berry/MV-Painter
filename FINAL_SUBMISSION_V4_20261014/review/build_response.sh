#!/usr/bin/env bash
set -euo pipefail
candidate_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$candidate_dir"
mkdir -p build_response
pandoc FINAL_V4_RESPONSE_TO_REVIEWERS.md --standalone --pdf-engine=pdflatex \
  -V fontsize=10pt -V geometry:margin=0.85in --include-in-header=response_header.tex \
  -o FINAL_V4_RESPONSE_TO_REVIEWERS.tex
for pass_num in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error \
    -output-directory=build_response FINAL_V4_RESPONSE_TO_REVIEWERS.tex \
    > "build_response/pass${pass_num}.log"
done
cp build_response/FINAL_V4_RESPONSE_TO_REVIEWERS.pdf ../FINAL_V4_RESPONSE_TO_REVIEWERS.pdf
