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

The historical C3 development plot's title and axis labels can be regenerated with revision_01549_restored/scripts/relabel_development_probe_figure.py (Python 3, Pillow, ReportLab, and Poppler's pdfinfo/pdfimages). The script retains the original plotted pixels and replaces only the interpretive labels. The author-generated vector Figure 1 can be rebuilt with revision_01549_restored/scripts/build_tcas_control_figure.py (Python 3 and ReportLab); its PDF is included in the archive. Its illustrative input/target thumbnails can be re-extracted from the archived 01549 Figure 1 with revision_01549_restored/scripts/extract_fig1_visual_assets.py (Python 3, Pillow, and Poppler's pdfimages). They are historical examples, not Fresh C results; the source of the archived images still needs author confirmation.

Historical status: 01549 is the 2026-09-07 post-first-round submission. The enclosed 1008 source is a second-round revision. It is not a submission approval.
