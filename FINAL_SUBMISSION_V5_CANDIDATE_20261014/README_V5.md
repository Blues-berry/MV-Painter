# V5 candidate submission package

This V5 continuation is on PR #1 branch `codex/cg-final-v4-20261014`, extending the candidate from commit `894fdb56a31ee0949bae23f1ffb6328907e0b8a1`. It uses V4 source baseline commit `91b6c42b16b82eca0fa7a477be1266c1d1a7e485`; V4 is retained. V5 contains bounded editorial changes to existing evidence and no new experiments or recomputed statistics. This continuation updates the Figure 2 positive example and the Figure 4 color/detail illustration with hash-verified frozen outputs. The V5 graphical abstract is a separate vector summary of results already reported in the paper.

The marked manuscript compares against the exact source of first-round submitted version **CAG-S-26-01549**: `final_0903.tex` extracted from the 0907 LaTeX ZIP, SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`. The final response is for second-round manuscript `CAG-D-26-00962`.

## Submission files

- `FINAL_V5_MANUSCRIPT.pdf` and `FINAL_V5_MANUSCRIPT.tex`
- `FINAL_V5_SUPPLEMENTARY.pdf` and `FINAL_V5_SUPPLEMENTARY.tex`
- `FINAL_V5_RESPONSE_TO_REVIEWERS.pdf` and editable Markdown/TeX source in `review/`
- `FINAL_V5_MARKED_MANUSCRIPT.pdf` and its source/diff under `marked/`
- `Graphical_Abstract_V5.pdf` (author-review candidate; replaces the stale first-round 0907 graphic if the revision portal requires a Graphical Abstract)
- `Manuscript_LaTeX_Sources_V5.zip` (49 files, flat archive; rebuilds main and Supplement)
- `Research_Evidence_V5.zip` (internal reproducibility archive; upload only if requested)
- `SHA256SUMS_V5.txt`

The main manuscript is 13 pages; the 69-page Supplement shares the 210 × 280 mm page box. The response is 6 pages and the marked manuscript is 20 pages. The Supplement received a focused editorial cleanup of internal archive notes, duplicate implementation/provenance notes and repeated figure caveats; cohorts, statistical results, tables and image pixels are unchanged. The full local upload package is `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v5_candidate`. The two MP4s are stored there and must be uploaded separately, with their matching stills; they are not in the GitHub source archive.

## Readiness

Technical formatting, bibliography integrity, source-archive rebuilding, and media decoding passed. `AUTHOR_REVIEW_READY` is YES. `SUBMISSION_READY` remains NO until the authors provide accurate ethics/exemption and informed-consent facts for the historical 24-participant study retained in the Supplement, and the live C&G revision portal requirements are checked. The C&G Guide URL returned HTTP 403 during this audit, so the portal and decision letter remain authoritative for journal-specific item types and whether to submit the V5 graphical abstract. See `V5_SUBMISSION_INSTRUCTIONS.txt` and the readiness/manifest files.

## Rebuild

Run `python3 build_v5_manuscript.py`, then `python3 marked/regenerate_marked_v5.py`, `python3 marked/build_v5_marked_pdf.py`, and `bash review/build_v5_response.sh`. Rebuild the flat source archive with `python3 build_v5_source_archive.py`. `Graphical_Abstract_V5.tex` builds the one-page vector graphical abstract separately.

The evidence boundaries and independent C&G-style assessment are in `quality_review/V5_EDITORIAL_DECISION.md` and `quality_review/INDEPENDENT_CG_ASSESSMENT_V5.md`. Actual-page alternatives for Figures 3 and 2 are in `quality_review/FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.png` and `quality_review/FIGURE2_FOUR_VS_V5_THREE_ACTUAL_PAGES.png`.
