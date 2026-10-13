#!/usr/bin/env bash
set -euo pipefail
candidate_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$candidate_dir"
mkdir -p build_response
pandoc Response_to_Reviewers.md --standalone --pdf-engine=pdflatex \
  -V fontsize=10pt -V geometry:margin=0.85in --include-in-header=response_header.tex \
  -o Response_to_Reviewers.tex
for pass_num in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error \
    -output-directory=build_response Response_to_Reviewers.tex \
    > "build_response/pass${pass_num}.log"
done
cp build_response/Response_to_Reviewers.pdf Response_to_Reviewers.pdf
