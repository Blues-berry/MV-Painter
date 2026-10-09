# Main source and scientific authority

**Captured:** 2026-10-09T04:42:50Z UTC  
**State:** `AUTHOR_REVIEW_READY`; not submission-approved.

## Version authority

- `1008/manuscript/source_01549/final_0903.tex` is the authenticated 01549 source, SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`. The 0907 archive has SHA-256 `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a` and contains the same `final_0903.tex` bytes. The source directory and original figures/template were not modified.
- 01549 is the post-first-round submission dated 2026-09-07. The active R1/R2/R3 packet is second-round review, and the current 1008 source is the second-round revision.
- Active source: `1008/manuscript/revision_01549_restored/manuscript_1008.tex`, SHA-256 `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`. Author-review copy hash is identical. Supplement SHA-256 `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f`. Timestamped records are appended to `1008/MANUSCRIPT_REVISION_INTEGRITY.csv`.
- PDFs and LaTeX source ZIP hashes are in `1008/submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md`. The source ZIP has a text SHA lock and contains no JSON.

## Fresh C primary evidence

- Paired cohort: 300 unique objects, disjoint from the original probe/evaluation and the stated training cohorts. Primary contrast: C3−GFL FG-PSNR +0.5223522385 dB; object-bootstrap 95% CI [+0.404160, +0.640669] dB; 10,000 draws, seed 20261006.
- Primary delta CSV SHA-256: `33f1153632963e33a887d6b852b2d60e8be2086bb2c948ebd27029933eba1bd2`. `verify_fresh_c_primary_from_deltas.py` reproduces the estimate and confidence interval.
- One checkpoint SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`; one runner SHA-256 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`; shared inputs, reference, camera views, metrics, and per-object seed `42 + object_idx`. Native shallow cap applied to requested C3 scale is 0.8. Historical Table 4 checkpoint identity is not an added validity gate. The 01549 v1/v2 distinction remains separately disclosed.
- The figure source/ROI CSV records 16 figure-method rows and per-input/output hashes. It records the same checkpoint and runner across all rows; final Fig. 4 and Fig. 5 PDF hashes match the corresponding manifest fields. The visible examples are illustrative and do not estimate cohort rates.
- Main-text counter-results remain: GFH and Generic Linear have more favorable means than C3 on all four reported Fresh C endpoints. The Fig. 5 Generic Linear counterexample shows C3−Generic Linear FG-PSNR −3.491 dB and FG-LPIPS difference +0.08172 favoring Generic Linear. LLH endpoint trade-offs remain reported.

## Retained claims and limits

- TCAS remains the training-free method. CAI optimality is withdrawn; the original fixed-scale and 24-object schedule-selection records remain historical development evidence with provenance limits.
- FAC's first-round controlled negative re-examination and the first-round preference study remain bounded historical results, not Fresh C texture-fidelity or 3D-quality evidence.
- Fresh B, A2/A3b, Core-7, strict-276, and cross-backbone probes retain their actual cohort/protocol limitations. Core-7 endpoint directions oppose each other; it is retrospective and not an independent Fresh C replication.
- The N=20 unseen-view test remains small and mixed, using unlit base color. No Fresh C bake, seam, PBR, human-preference, or unmodified-default pipeline outcome is claimed. Cross-backbone results are interface probes, not general transfer.
- The R2.3 production additive-residual bootstrap has an invalid zero-power null. Exploratory robust-Wald results do not survive Holm correction; no interaction conclusion is claimed.

## Implementation authority

The curated main source uses per-wrapper state for the reference-only correction bypass. The former class-level toggle was replaced with an instance flag restored in `finally`, avoiding cross-instance leakage if reference evaluation raises. Core scripts, selected evidence tooling, and tests are enumerated in the integration manifest. No GPU experiment was run during this consolidation.

## Repository handover state

Private `mvpainter/main` is verified at `b02a64102a40c83370902486d47b1ffad217a49e`. The active daily working tree is `/4T/MV-Painter-main`. The editor UI folder switch has not been verified, so this remains an operational handoff item. Nonessential JSON and ignored research outputs remain local; no paper content changed in this status update.

## V3 frozen reproducibility snapshot

`1009/evidence/scientific_validation_v3/reproducibility_release/` now contains the exact frozen V3 code/data subset separately from active `MVPainter/` code. The runner and source files are SHA-verified against the original text provenance; 20 A2/B condition CSVs and the ordered object lists are included. A clean-copy analysis rebuild reproduced `outputs/core_evidence_table.md` byte for byte and the paired LLH−LFM-EXACT analysis used 150 matched objects. The snapshot is limited to the A2 map and selected B contrasts, not the full B campaign. No new GPU generation was run.
