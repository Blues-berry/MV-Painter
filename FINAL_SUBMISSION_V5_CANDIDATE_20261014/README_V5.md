# V5 candidate submission package

This V5 continuation is on PR #1 branch `codex/cg-final-v4-20261014`. The first-round submitted version is CAG-S-26-01549; its authenticated source remains the Marked Manuscript baseline. V4 source baseline commit `91b6c42b16b82eca0fa7a477be1266c1d1a7e485` is retained. V5 contains no new experiments or recomputed statistics. The current editorial addition cites CAD/Graphics 2026 Paper 75, states the journal extension and its new evidence in the Abstract, Introduction, and Conclusion, and updates the Cover Letter to include the conference-paper reference, status, differences, and scope fit. The original conference submission is supplied separately for editorial comparison.

The marked manuscript compares against the exact source of first-round submitted version **CAG-S-26-01549**: `final_0903.tex` extracted from the 0907 LaTeX ZIP, SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`. The final response is for second-round manuscript `CAG-D-26-00962`.

## Submission files

- `FINAL_V5_MANUSCRIPT.pdf` and `FINAL_V5_MANUSCRIPT.tex`
- `FINAL_V5_SUPPLEMENTARY.pdf` and `FINAL_V5_SUPPLEMENTARY.tex`
- `FINAL_V5_RESPONSE_TO_REVIEWERS.docx` and `FINAL_V5_RESPONSE_TO_REVIEWERS.pdf`; upload the editable DOCX, keeping the PDF as a local proof unless the portal prefers PDF.
- `FINAL_V5_MARKED_MANUSCRIPT.pdf` and its source/diff under `marked/`
- `Graphical_Abstract_V5.pdf` (required by the supplied C&G Guide; candidate still needs author visual approval and replaces the stale first-round graphic)
- `Title_Page_V5.docx` and `Declaration_of_Interest_V5.docx` are separate; the Title Page no longer repeats the competing-interest declaration.
- `Acknowledgements_V5.docx` carries the 0907 acknowledgment text byte-for-byte as a local comparison copy. Upload the Title Page, which already contains the acknowledgement, rather than a duplicate standalone file unless the live portal explicitly requests one.
- `Cover_Letter_V5.docx` includes the Paper 75 status and reference, the added journal evidence, revised interpretation, and fit to C&G scope. Upload the DOCX only; the old PDF proof predates this update and is not for upload.
- `Manuscript_LaTeX_Sources_V5.zip` (48 files, flat archive; rebuilds main and Supplement)
- The four main figures are also supplied individually as vector PDFs for figure upload.
- `Original_Conference_Submission_CAD_Graphics_2026_Paper_75.pdf` (for editorial comparison; not public Supplementary Material)
- `Research_Evidence_V5.zip` (internal reproducibility archive; not a repository deposit)
- `SHA256SUMS_V5.txt`

The main manuscript is 13 pages; the 69-page Supplement shares the 210 × 280 mm page box. The response is 6 pages and the marked manuscript is 20 pages. The Supplement received a focused editorial cleanup of internal archive notes, duplicate implementation/provenance notes and repeated figure caveats; cohorts, statistical results, tables and source-render pixels are unchanged. Figure 2/3 now use neutral object and condition labels, and the rebuilt Supplement Figure S26 changes only its title bands. The GeoTex and GSO supplementary comparison videos, their matching stills, and the caption file are separate multimedia items outside the LaTeX source archive.

The rights-filtered research data are archived as [Zenodo version 1.0.1](https://doi.org/10.5281/zenodo.23383807) and available from the matching [GitHub release](https://github.com/Blues-berry/MV-Painter-research-data/releases/tag/v1.0.1) at tag commit `c33c568398c5b0b5f9b5a838d36722140fe0e8d1`. The archived ZIP checksum was verified against Zenodo metadata. It contains derived metrics and figure-source metadata only; source meshes, textures, generated-image archives, model weights, and participant-level responses are excluded.

## Presentation and demo

`presentation_demo_v5/` contains the V5-aligned editable 10-slide deck, a PDF review copy, 90-second silent and 255-second narrated 1080p demos, a preview still, English subtitles, and narration text synchronized across the PowerPoint speaker notes and script. The narration was generated locally with Piper (`en_US-lessac-medium`); its opening sentence discloses AI-generated narration. The 0907 presentation/demo files remain in their original archive paths and the old narration was not reused because it does not match V5. These companion materials are outside the 20 journal `UPLOAD_FILES` items.

## Readiness

Technical formatting, bibliography integrity, source-archive rebuilding, and media decoding passed. The supplied Guide requirements were checked. `AUTHOR_REVIEW_READY` is YES. `SUBMISSION_READY` remains NO pending funder-role confirmation, Graphical Abstract visual approval, and live portal metadata/item-type checks. Supplement S7 records the author-provided basis for the minimal-risk, non-interventional preference study; ethics/consent is not an outstanding gate. The manuscript cites the versioned Zenodo DOI and matching GitHub release. See `V5_SUBMISSION_INSTRUCTIONS.txt` and the readiness/manifest files.

## Rebuild

Run `python3 build_v5_manuscript.py`, then `python3 marked/regenerate_marked_v5.py`, `python3 marked/build_v5_marked_pdf.py`, and `bash review/build_v5_response.sh`. Rebuild the flat source archive with `python3 build_v5_source_archive.py`. `Graphical_Abstract_V5.tex` builds the one-page vector graphical abstract separately.

The evidence boundaries and independent C&G-style assessment are in `quality_review/V5_EDITORIAL_DECISION.md` and `quality_review/INDEPENDENT_CG_ASSESSMENT_V5.md`. Actual-page alternatives for Figures 3 and 2 are in `quality_review/FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.png` and `quality_review/FIGURE2_FOUR_VS_V5_THREE_ACTUAL_PAGES.png`.
