# C&G FINAL V4 submission package

This directory is the authoritative V4 submission and continuation point. Start every subsequent manuscript edit from the V4 sources here. V1–V3 are historical records and are intentionally excluded from this GitHub package.

## Deliverables

- `FINAL_V4_MANUSCRIPT.pdf` and `.tex` — 13-page main manuscript; references through [41] end on p. 13.
- `FINAL_V4_SUPPLEMENTARY.pdf` and `.tex` — complete 71-page Supplement; S35 is on p. 58 and S36 is on p. 59.
- `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` plus synchronized Markdown and TeX sources.
- `FINAL_V4_MARKED_MANUSCRIPT.pdf` and its generated TeX source.
- TeX figure, table, section and class dependencies; figure credits and frozen Figure 6 validation.
- A sanitized visual selection manifest, seven-candidate Bake10 ranking, selected source pixels and display crops.
- 01549 reuse audit, layout/science check, change log and author handoff.
- Build comparison showing that a clean rebuild matches the frozen PDFs in page count and extracted text.

## Figure 3 selection and scientific limits

Figure 3 shows one rights-cleared Bake10 best-case example, UID `238ff3e41c964655b83aa9c8770cc766`, selected as the lowest existing 11-view FG-LPIPS case among seven cleared assets for both Fixed Mean (0.05895328) and Late-high (0.05848895). This is explicitly a post-outcome illustration, not a prevalence estimate or general material-fidelity result. The selected 512×512 source images, display crops, attribution and sanitized camera/protocol record are included. The full candidate atlas, unselected pixels, GLBs, checkpoints and internal absolute-path index remain outside the submission package.

The upstream render record has a metadata inconsistency: its per-render field says 1024×1024, while the renderer setting and actual hashed PNGs are 512×512. V4 discloses the discrepancy and reports the renderer setting/actual pixels; no source image or experiment result was altered.

No experiment or inferential statistic changed, and no GPU experiment was run. The frozen primary remains −0.0338775 dB, 95% CI [−0.117170, +0.051422], p = 0.432378. R1's material/texture fidelity limitation remains. R2.1 remains partly addressed: the paper argues for a task-specific empirical contribution and makes no claim of a new general scheduling method.

## Rebuild

From this directory, with a LaTeX toolchain and Pandoc installed:

1. `python3 build_v4_manuscript.py` — rebuilds the main manuscript and Supplement.
2. `bash review/build_response.sh` — rebuilds the reviewer response.
3. `python3 marked/build_marked_pdf.py` — rebuilds the supplied marked manuscript from its committed V4 TeX.

`alignment/SUBMISSION_MANIFEST_V4.json` records page counts, key scientific checks and hashes for the submitted files. Regenerate it with `python3 alignment/build_submission_manifest.py`; it intentionally excludes its own hash to avoid recursion. `BUILD_VERIFICATION_V4.md` explains the clean-build comparison. The internal candidate-ranking script and full source index are not included because they depend on the private, unselected candidate archive; the final selection rule, ranking and sanitized provenance are included.
