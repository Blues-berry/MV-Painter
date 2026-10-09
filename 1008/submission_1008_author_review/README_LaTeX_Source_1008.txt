LaTeX source package — 1008 second-round revision

Package root contains two sibling directories: revision_01549_restored/ and source_01549/. Keep this layout.

Build requirements: bash, Python 3, latexmk, pdfTeX/TeX Live, latexdiff (for the marked-up comparison), and Pandoc + XeLaTeX (for the reviewer-response PDF).

From revision_01549_restored/ run:
  bash build_revision_1008.sh
  bash build_supplement_1008.sh
  bash build_marked_up_1008.sh
  bash build_original_01549.sh  # optional authenticated baseline comparison

Build outputs go under revision_01549_restored/build/. The source lock is a plain SHA-256 text file. No experiment JSON, raw participant data, checkpoints, caches, or generated object collections are included. The Fresh C figure assets in the paper are selected final outputs; the full run manifests and provenance are in the repository author-review package, while large raw RGB outputs remain in their controlled local evidence store.

Historical status: 01549 is the 2026-09-07 post-first-round submission. The enclosed 1008 source is a second-round revision. It is not a submission approval.
