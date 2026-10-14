# Journal handoff — current V4 delivery

The versioned local delivery is:

`/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v4`

It was created as a new sibling directory. The previous `1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4` directory remains unchanged. The full local file list, byte sizes, SHA-256 values, video metadata and decode results are in `quality_review/JOURNAL_DELIVERY_MANIFEST_V4.json` and the copied manifest in the delivery directory.

| Journal role | File in the delivery directory |
|---|---|
| Clean/revised manuscript | `FINAL_V4_MANUSCRIPT.pdf` — 13 pages |
| Marked/tracked manuscript | `FINAL_V4_MARKED_MANUSCRIPT.pdf` — 20 pages |
| Supplementary document | `FINAL_V4_SUPPLEMENTARY.pdf` — 71 pages |
| Response to reviewers | `FINAL_V4_RESPONSE_TO_REVIEWERS.pdf` — 5 pages; `.docx` also supplied |
| LaTeX source | `Manuscript_LaTeX_Sources_V4.zip`; use `FINAL_V4_MANUSCRIPT.tex` as main source |
| Title page, highlights and declaration | Existing `Title_Page_V4.*`, `Highlights_V4.*`, and `Declaration_of_Interest_V4.docx` |
| Research archive | Existing `Research_Evidence_V4.zip`; retain for the journal's requested evidence workflow |

## Supplemental videos

The two MP4s physically exist in the delivery directory, decode fully, and have corresponding representative stills at identical pixel dimensions. Submit each MP4 as a separate supplemental-media/video item in the journal portal and associate its matching still as the representative image. Check the portal's file role and preview before completing submission. They are not hosted in GitHub. The journal's media guidance also calls for supplemental media to be identified in the manuscript and supplied with representative stills ([Elsevier Media Overview](https://www.elsevier.com/researcher/author/policies-and-guidelines/artwork-and-media-instructions/media-overview)); the manuscript cites Videos 1 and 2. Portal upload has not been performed.

1. **GeoTex baked comparison** — [local MP4](/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v4/Supplementary_GeoTex_Baked_Comparison.mp4), SHA-256 `6191b81e6336c6be62fcd8962a33f1e84245667b68ae6346be2815da1d9502a3`; H.264, 2304×346, 24 fps, 22 s, 528 decoded frames. It shows two rights-cleared GeoTex objects (LG Remote and Tire), all seven bake settings plus reference, over raw cameras 001–011. Tire is the same object used in Figure 3, but the video includes additional conditions and views. The matching still is `Supplementary_GeoTex_Baked_Comparison_Still.png` (2304×346).
2. **GSO baked comparison** — [local MP4](/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v4/Supplementary_GSO_Baked_Comparison.mp4), SHA-256 `2e76a5d742fc8432aa8f0f6e58df13d442074bfddcb8552bc539fe665f1261b5`; H.264, 1024×1128, 2 fps, 5.5 s, 11 decoded frames. It shows the first source-ordered GSO object (Razer mouse), seed 42, twelve conditions and protocol-specific camera indices 0–10. The source-mesh panel is not a GT self-bake. The matching still is `Supplementary_GSO_Baked_Comparison_Still.png` (1024×1128).

Object, camera, condition and frame identity checks are recorded in `quality_review/VIDEO_VALIDATION_V4.json`. Camera indices belong to each protocol. Neither video is a cohort-prevalence estimate.

## Readiness

`AUTHOR_REVIEW_READY=YES`; `SUBMISSION_READY=YES` for the bounded empirical paper, with material method-novelty risk disclosed in `quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md`. These decisions reflect the scientific scope and provenance as well as the completed files; compilation alone is not the basis. Portal submission remains `NOT_PERFORMED`.
