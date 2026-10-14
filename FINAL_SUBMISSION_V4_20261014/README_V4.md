# C&G FINAL V4 — authoritative submission package

Continue from [PR #1](https://github.com/Blues-berry/MV-Painter/pull/1), branch `codex/cg-final-v4-20261014`. This is a continuation of V4, using the previously confirmed `0aa1c9b3` as this task's starting HEAD. V1–V3 are historical references only.

Final PDF set: `FINAL_V4_MANUSCRIPT.pdf/.tex` (14 pages), `FINAL_V4_SUPPLEMENTARY.pdf/.tex` (71), `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` (5), `FINAL_V4_MARKED_MANUSCRIPT.pdf` (21). Figure 3 C has one camera-matched Tire asset plus the complete ten-object Bake10 effect strip; Table 3/5/7 layouts are updated without changing their values. The manuscript restores the bounded S8 full-native quality comparison and S7 texture-complexity association. See `MAIN_TEXT_EVIDENCE_REINTEGRATION.md`, `SCIENTIFIC_CONTENT_ADDITION_LOG.md` and `VISUAL_AND_TABLE_BEFORE_AFTER.pdf`.

The actual local journal-upload directory, including both independently submitted MP4s, is listed in `JOURNAL_SUBMISSION_HANDOFF_V4.md`. Large videos and research archives remain local; current manuscript/figure source pixels and SHA list are in this GitHub package.

Rebuild order: `python3 visual_candidates/build_fig3_distribution_v4.py`, `python3 build_v4_manuscript.py`, `bash review/build_response.sh`, `python3 marked/regenerate_marked_v4.py`, `python3 marked/build_marked_pdf.py`, `python3 alignment/build_submission_manifest.py`. The authenticated original submission under `marked/original_submission` is solely a difference reference. No GPU experiment or inferential statistic was recomputed.
