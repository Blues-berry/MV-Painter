# C&G V4 submission package

This package continues the single V4 line on PR #1, branch `codex/cg-final-v4-20261014`. The text revision started from verified PR HEAD `11006e003842b25976e20cafd51a7970770f269f`; it does not rebuild from V1–V3. `FINAL_V4_MANUSCRIPT.tex` is the only official manuscript source. The editorial draft files are review-only archives.

## Current deliverables

- Main manuscript: `FINAL_V4_MANUSCRIPT.pdf` (13 pages) and `.tex`
- Supplement: `FINAL_V4_SUPPLEMENTARY.pdf` (71 pages) and `.tex`
- Response: `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` (5 pages) and the source in `review/`
- Original-to-final marked manuscript: `FINAL_V4_MARKED_MANUSCRIPT.pdf` (20 pages), generated against the authenticated original submission
- Figure 2: three rows, five matched columns, one camera per object
- Figure 3: candidate B, an input-property-selected Tire plus a clearly post-outcome Baptisimal Font tradeoff; the full Bake10 distribution remains in Supplement S5

The abstract and main text now present three connected evidence strands: executed control semantics, competitive and applied-budget comparisons, and final native-UV asset appearance. The paper is framed as a bounded empirical graphics study, not a new general schedule optimizer. Frozen numeric tables and the Supplement are unchanged in this text pass.

For version clarity, the current main source includes only `figures/fig3_bake10_two_object_v4.pdf`, selected as candidate B. Candidate A's actual page is review-only. The earlier candidate-C effect-strip PDF and its selection record remain archived for lineage; they are not referenced by the official main source. `EDITORIAL_REWRITE_REVIEW_ONLY.tex` and `FINAL_V4_MANUSCRIPT_EDITORIAL_DRAFT.tex` are also non-submission candidates.

## Evidence and handoff

`quality_review/FIGURE3_DECISION_V4.md` includes the seven-object assessment and actual rendered page comparison for candidates A and B. `quality_review/FIGURE2_DECISION_V4.md` records the actual four-row versus three-row page comparison. `quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md` states scientific strengths, limits, and readiness separately from build status. `JOURNAL_SUBMISSION_HANDOFF_V4.md` gives the actual local delivery directory, file hashes, and separate MP4 submission paths.

The local journal package is prepared but has not been uploaded to the portal. Large videos and the frozen research archive stay in the delivery directory; the current source, figure assets and checksum manifest are in this repository.

## Rebuild order

Run `python3 build_v4_manuscript.py`, `bash review/build_response.sh`, `python3 marked/regenerate_marked_v4.py`, `python3 marked/build_marked_pdf.py`, then `python3 alignment/build_submission_manifest.py`. To regenerate the Figure 3 page comparison, run `python3 quality_review/build_figure3_page_comparison_v4.py`. No GPU inference or new inferential computation is part of this revision.
