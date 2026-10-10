# 1008 final build and clean-source check

**Captured:** 2026-10-10 · **State:** `AUTHOR_REVIEW_READY / DRAFT` · **Submission approval:** `NO`

## Source identity and archive

- Active and author-review manuscript TeX are byte-identical (SHA-256 `b10909885558de1da6fb6c449bd2933142ad06e9749e1eda3617048f95d3cf50`). Active and author-review Supplement TeX are byte-identical (SHA-256 `811517c535a9398fafe4580be4982c1705d8dcd81a1c52467b2e9edcb5f858c2`).
- Response Markdown, PDF, and DOCX are synchronized between `review/` and `submission_1008_author_review/`. Their hashes are `0ae658b1969e140ea56f7f09ccc57b4be80d451d9526f285c38c3c46462b6a47`, `b211405ba8eefcd9df4f99604744d444b2ce8bf5c4d9f07d4c5a97ba0f7ab831`, and `3626d504fd7b2ae8562eb6431698488226520f57c71bbc6436a459e26f37c611`, respectively.
- `LaTeX_Source_1008.zip` has 62 members, 35,931,678 bytes, and SHA-256 `105bee245c213717813cf35a31a93639f7806f0bda3660ed6b73a8fbcb964bce`. ZIP CRC passes. It contains the active manuscript, Supplement, referenced figures, figure provenance, and authenticated 01549 baseline; it excludes experiment JSON, arrays, checkpoints, GLBs, generated PDFs, and caches.
- The upload-style `submission_1008/` directory was regenerated with the refreshed manuscript, response, source archive, and separate author-review evidence snapshots. Its file manifest and checksum list are generated from the assembled contents.
- The active Figure 1 is an author-generated vector diagram of the TCAS cap-aware residual path. The original 01549 Figure 1 remains preserved in `source_01549`.

## Author-review artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 16 | 2,000,464 | `3315ce2acb1bb689f50ec5420e3cd2de10bd99561e7a82520670f30a02dcf148` |
| `Marked-up_Manuscript_1008.pdf` | 16 | 2,023,794 | `004fac2bc9204091af80f5a7122503cdc4e6ed14d8c07c84e3e2527b0e33ef08` |
| `Supplementary_1008.pdf` | 15 | 1,670,609 | `e31deed73b1c1620ea14130afdab4ae35d27cb9c13f3e13b810c89af3f177839` |
| `Response_to_Reviewers_1008.pdf` | 4 | 36,200 | `b211405ba8eefcd9df4f99604744d444b2ce8bf5c4d9f07d4c5a97ba0f7ab831` |
| `Response_to_Reviewers_1008.docx` | — | 14,872 | `3626d504fd7b2ae8562eb6431698488226520f57c71bbc6436a459e26f37c611` |
| `LaTeX_Source_1008.zip` | — | 35,931,678 | `105bee245c213717813cf35a31a93639f7806f0bda3660ed6b73a8fbcb964bce` |

## Build and page review

- The working-tree and fresh-extraction builds completed for the manuscript, Supplement, and marked-up manuscript at 16, 15, and 16 pages. Whitespace-normalized extracted text matches each author-review PDF. The final logs contain no unresolved citations or cross-references.
- Main layout anchors: Figure 1 p. 4; historical fixed-scale Table 1 p. 6; Fresh C Tables 3–4 p. 8; Figure 5 p. 9; temporal/layer-window/color Tables 5–7 p. 11; licensed color-diagnostic Figure 6 p. 12; full-object Figure 7 p. 13; Cross-Interface Table 8 p. 14; Limitations p. 15. The A3b dimension limitation is legible on p. 10.
- Supplement anchors: layer/window Tables S3–S5 pp. 3–5; requested/applied accounting Table S6 p. 6; placement Table S7 p. 7; MV-Adapter Tables S10–S11 pp. 9–10; FAC Table S15 p. 13; color Table S17 p. 15. The per-entry correction values and their descriptive-only caption are legible on p. 6.
- Response anchors after the final 4-page build: R1.1 pp. 1–2; R1.2 p. 2; R1.3 p. 2; R1.4–R1.5 p. 3; R2.1 pp. 3–4; R2.2–R2.3 and Reviewer 3 p. 4. The final page and the A3b withdrawal paragraph were visually checked.
- The reviewer-risk decision sheet is regenerated from its Markdown source during package assembly as a one-page landscape PDF; its dimension-aware A3b wording is retained.
- The retained review PDF is labeled “Initial submission”; the exact second-round decision export remains unavailable. Response headings are paraphrased and require author verification rather than being presented as verbatim quotations.
- Nonfatal TeX geometry, underfull/overfull box, and `latexdiff` Unicode warnings remain. The largest observed overfull line is about 1.1 pt; no clipping was observed in the checked pages.

## Evidence update and limits

- The A3b `0/2,250` overlap statistic and probe-24 calibration both used integrated raw $L_2$ across feature groups at 24×16, 48×32, and 96×64 spatial resolutions; channel counts were not logged. The cross-layer common-support and equal-dose/imbalance interpretations are withdrawn. The recorded scale values remain tested settings. The CPU-only audit and per-entry sensitivity are packaged under `Author_Review/Residual_Norm_Dimension_Audit_20261010/`; they do not establish dose matching, common support, or causality.
- Fresh C remains a matched 300-object image-space comparison. C3−GFL FG-PSNR is `+0.522352 dB` (95% object-bootstrap CI `[+0.404160,+0.640669]`); GFH and Generic Linear have more favorable means on all four displayed endpoints. C3/GFL applied deep/middle sums remain `82.5/62.5`; this is not a timing-only contrast.
- The retrospective strict-276 L–L–H comparison favors that profile over C3 on six endpoints, but does not match layer-wise post-scale corrections. Fresh B/A3b and Core-7 remain retrospective sensitivity evidence.
- The 76-object MV-Adapter panel is retrospective and interface-specific; its 30 temporal intervals are unadjusted. The 75-object MVDiffusion panel used a compatibility base; a later native-mirror check covered one object, not the full panel. Neither establishes matched cross-backbone transfer.
- The failure-enriched 26-object color diagnosis and locked three-object P0 trace validate no repair and do not establish the full color cause. Figure 6 uses a licensed, hash-traced Fresh C case and is not a prevalence estimate or independent confirmation.
- No validated color repair, native-default comparison, valid Fresh C bake, seam/PBR result, or matched cross-backbone trial is claimed. The CPU applied-budget preflight checked schedule arithmetic only. Its GPU-idle gate failed before inference; no GPU experiment was launched, and the historical base-model directory has no content hash.
- `SUBMISSION_APPROVED=NO`; no journal submission was made.

## Open author checks

- Compare the response headings with the exact second-round decision and update any inaccurate paraphrase.
- Verify Figure 6 attribution and caption against the review PDF.
- Decide whether the task-specific empirical contribution meets the journal's novelty threshold; review the open R1.1 color/3D and R2.3 cross-backbone boundaries.
- Verify carried-forward author metadata, funding, conflicts, current manuscript ID, and portal-specific requirements before any upload.
