LaTeX source package — 1008 second-round revision

Package root contains two sibling directories: revision_01549_restored/ and source_01549/. Keep this layout.

Build requirements: bash, Python 3, latexmk, pdfTeX/TeX Live, latexdiff (for the marked-up comparison), and Pandoc + XeLaTeX (for the reviewer-response PDF).

The current-manuscript, Supplement, and marked-up build scripts run pdfLaTeX twice so the clean build resolves citations and cross-references in the same staging directory. latexmk remains listed because the optional authenticated-baseline build uses it.

From revision_01549_restored/ run:
  bash build_revision_1008.sh
  bash build_supplement_1008.sh
  bash build_marked_up_1008.sh
  bash build_original_01549.sh  # optional authenticated baseline comparison

Build outputs go under revision_01549_restored/build/. The source lock is a plain SHA-256 text file. No experiment JSON, raw participant data, checkpoints, caches, or generated object collections are included. The Fresh C figure assets in the paper are selected final outputs. Figure 6 uses a rights-cleared CC BY 4.0 asset and a frozen, previously viewed sample that was not selected for color; its one-row selection record and image/source hashes are included in the archive and author-review package. Large raw RGB outputs remain in their controlled local evidence store. The retired historical color panel remains only in the authenticated 01549 source archive and is not referenced by the active manuscript.

The historical C3 development plot can be relabeled with scripts/relabel_development_probe_figure.py (Pillow, ReportLab and Poppler); only interpretive labels change. Figure 1 combines disclosed OpenAI Images conceptual artwork, an exact piecewise C3 vector request and actual rights-cleared Building03 maps/output thumbnails. Rebuild with scripts/build_tcas_control_figure.py (Pillow and CairoSVG), using included fig1_assets/. Their replacement sources/hashes are in FIG1_THUMBNAIL_PROVENANCE.csv. The legacy extraction script is an archive utility and must not overwrite active verified thumbnails. The original 01549 overview remains unchanged in source_01549/.

New Figure8 and Supplement FigureS2 show actual full-object unlit unseen renders; complete credits and source hashes are included. A 22-second MP4 uses actual discrete unseen views. Reproduction_1008.zip is a separate numerical/script archive; its raw metric JSON is intentionally excluded from the LaTeX source archive.

Historical status: 01549 is the 2026-09-07 post-first-round submission. The enclosed 1008 source is a second-round revision. It is not a submission approval.
