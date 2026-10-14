# V5 candidate submission package

This is an additive V5 candidate based on the V4 files at PR #1 branch `codex/cg-final-v4-20261014`, HEAD `91b6c42b16b82eca0fa7a477be1266c1d1a7e485`. V4 remains unchanged. V5 makes bounded editorial changes to the main-text interpretation and placement of existing results; it does not add experiments or recompute statistics.

## Submission files

- `FINAL_V5_MANUSCRIPT.pdf` and `FINAL_V5_MANUSCRIPT.tex`
- `FINAL_V5_SUPPLEMENTARY.pdf` and `FINAL_V5_SUPPLEMENTARY.tex`
- `FINAL_V5_RESPONSE_TO_REVIEWERS.pdf` and the editable Markdown/TeX source in `review/`
- `FINAL_V5_MARKED_MANUSCRIPT.pdf` and its source/diff under `marked/`
- `Manuscript_LaTeX_Sources_V5.zip`
- `Research_Evidence_V5.zip`, unchanged from the V4 evidence archive, in the local journal package
- `SHA256SUMS_V5.txt`

The main manuscript is 13 pages, the Supplement is 71 pages, the response is 6 pages, and the marked manuscript is 20 pages. See `quality_review/FINAL_READINESS_V5.json`, `JOURNAL_SUBMISSION_MANIFEST_V5.json`, and `quality_review/JOURNAL_DELIVERY_MANIFEST_V5.json` for the checks, file hashes, local MP4 paths, and journal-upload instructions. The complete local upload package is `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v5_candidate`; its MP4s must be uploaded separately in the journal portal. They are not in the GitHub source archive.

## Rebuild

Run `python3 build_v5_manuscript.py`, then `python3 marked/regenerate_marked_v5.py`, `python3 marked/build_v5_marked_pdf.py`, and `bash review/build_v5_response.sh`. The V5 source archive contains the full TeX dependencies and these scripts.

## Editorial decision

The V5 changes and their evidence boundaries are recorded in `quality_review/V5_EDITORIAL_DECISION.md`; the independent C&G-style assessment is in `quality_review/INDEPENDENT_CG_ASSESSMENT_V5.md`. The actual-page alternatives for Figure 3 and Figure 2 are in `quality_review/FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.png` and `quality_review/FIGURE2_FOUR_VS_V5_THREE_ACTUAL_PAGES.png`.
