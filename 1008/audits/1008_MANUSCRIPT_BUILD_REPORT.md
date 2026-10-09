# 1008 author-review package build report

## Built artifacts

| Artifact | Result | Notes |
|---|---:|---|
| `Manuscript_1008.pdf` | 13 pages | Built from the authenticated 01549-derived active source. Figures 4–5 use matched Fresh C context-plus-ROI layouts; Figure 6 remains the 24-object development plot. |
| `Supplementary_1008.pdf` | 11 pages | Includes Fresh C protocol/identity detail, bounded interface evidence, historical analyses, FAC results, full Fresh C Figure S1, and the retrospective Core-7 tables in S5 (pp. 6–7). |
| `Marked-up_Manuscript_1008.pdf` | 19 pages | Generated against authenticated 01549. Text edits are marked; deleted legacy passages may retain unresolved citation/reference markers. |
| `Response_to_Reviewers_1008.pdf` | 5 pages | Compiled from the current R1/R2/R3 response Markdown using Pandoc and XeLaTeX. |
| `LaTeX_Source_1008.zip` | 6.8 MB | Self-contained sources and referenced graphics; excludes raw experiment archives and generated PDFs. |
| `FIGURE_LAYOUT_COMPARISON_FIG4_FIG6.pdf` | 2 pages | Side-by-side review of authenticated 01549 Fig. 4/Fig. 6 and the Fresh C replacements. |

## Build and verification

- Active main and Supplement compiled with TeX Live 2019 / pdfTeX and the project class/style files. Final main/Supplement logs contain no unresolved citations or references; ordinary layout warnings remain.
- The refreshed source ZIP was extracted into a clean temporary directory. Both documents compiled using only the archive contents: main 13 pages, Supplement 11 pages.
- The marked comparison compiled successfully. Remaining unresolved markers are confined to old material deleted from the revision.
- The response PDF was regenerated from the matching Markdown with Pandoc and XeLaTeX.
- Main pages 11–12 were rendered at 110 dpi and visually checked: both Fresh C figures show the full-object context, a shared ROI across methods, readable crop detail, and the Generic Linear counterexample. Supplement pages 6–7 were rendered at 1600-pixel page width and checked for table clipping and legibility. No method-specific image adjustment was applied.
- The 01549 baseline source and original figure hashes remain unchanged. Fresh C input, identity, ROI, crop, and output hashes are in `FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv`; asset rights are in `FIGURE_ASSET_CREDITS.csv`.
- The built-in editor compiler had remained unresponsive for over two minutes on the isolated worktree path. The project scripts and clean-ZIP builds passed; no editor source was changed.

## Round and evidence framing

01549 is the post-first-round manuscript submitted on 2026-09-07; current R1/R2/R3 are the second-round reviews. Fresh C remains the author-specified same-checkpoint paired N=300 evidence. Historical v1/v2 differences remain explicit. The R2.3 production additive-residual bootstrap is labeled invalid due to its zero-power null; the post hoc robust-Wald results are exploratory and none survives Holm correction. No new GPU experiment was run. No valid Fresh C bake, seam, PBR, human-preference, or unmodified-default output is claimed.
