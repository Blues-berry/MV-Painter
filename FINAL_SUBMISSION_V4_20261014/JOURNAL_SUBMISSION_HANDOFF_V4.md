# V4 journal submission handoff

Actual local upload directory: `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4`. `alignment/refresh_journal_delivery_v4.py` copied the current four PDFs and refreshed the current LaTeX source archive; video bytes and ancillary author documents were preserved. Verify the upload system's file roles and preview before the author submits.

| Upload role | Local file |
|---|---|
| Clean/Revised Manuscript | `FINAL_V4_MANUSCRIPT.pdf` (14 pages) |
| Marked/Tracked Changes Manuscript | `FINAL_V4_MARKED_MANUSCRIPT.pdf` (21 pages) |
| Supplementary Material | `FINAL_V4_SUPPLEMENTARY.pdf` (71 pages) |
| Response to Reviewers | `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` or `.docx` (PDF 5 pages) |
| Source files | `Manuscript_LaTeX_Sources_V4.zip`, selecting `FINAL_V4_MANUSCRIPT.tex` as main source |
| Research evidence | `Research_Evidence_V4.zip` (previous frozen archive retained); new evidence decisions and current source in LaTeX ZIP |
| Ancillary forms | Existing Title Page, Highlights and Declaration files in the same directory |
| Videos and stills | Each MP4 and its Still.png uploaded as separate supplemental/video files |

Actual video files to submit separately:

- `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4/Supplementary_GeoTex_Baked_Comparison.mp4` — SHA-256 `6191b81e6336c6be62fcd8962a33f1e84245667b68ae6346be2815da1d9502a3`; LG Remote and Tire, eleven discrete GeoTex unseen raw001–011 cameras. Tire shares Figure 3's asset protocol, but the video includes all seven controls and more cameras.
- `/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4/Supplementary_GSO_Baked_Comparison.mp4` — SHA-256 `2e76a5d742fc8432aa8f0f6e58df13d442074bfddcb8552bc539fe665f1261b5`; first source-ordered Razer mouse, seed 42, twelve conditions and eleven separate GSO camera indices 0–10. Its source-mesh column is **not** a GT self-bake.

Both videos were fully decoded and checked against archived frame/object/camera records in `quality_review/VIDEO_VALIDATION_V4.json`. Their camera indices are protocol-specific, and neither single-object video estimates cohort prevalence. The complete absolute path, byte size and SHA of every local upload file are in `journal_upload_v4/JOURNAL_SUBMISSION_MANIFEST_V4.json`, mirrored in `quality_review/JOURNAL_DELIVERY_MANIFEST_V4.json`. The videos are not in GitHub; this does not remove them from the periodical submission checklist.

`AUTHOR_REVIEW_READY=YES`; `SUBMISSION_READY=YES` for author submission of the bounded empirical manuscript. The author still needs to review and perform the journal portal submission. Scientific limits and rejection risks are in `quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md`.
