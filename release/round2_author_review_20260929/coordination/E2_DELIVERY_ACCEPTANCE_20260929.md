# E2 Delivery Acceptance — 2026-09-29

## Final status

**READY FOR AUTHOR REVIEW.** This package is not an automatic submission and
does not contain a new GPU experiment.

## Evidence closure

- E0-A: PASS_WITH_LIMITATIONS; exact 276-object × 4-schedule pairing,
  1,104 stage rows, 1,104 serialized Full-SSIM rows, PNG/GT pairing, hashes,
  and 17/16/17 budget audit are frozen.
- Fixed-GT Full-SSIM decomposition: saved-tensor CPU-only diagnostic separates
  fp16 arithmetic (+0.03198), prediction PNG quantization (-0.00036), and GT
  PNG serialization (-0.00007).
- E0-B: WITH_LIMITATIONS; 76-object MV-Adapter audit keeps high 1.50 and
  high 1.00 separate, retains CAI undefined/set-valued, and does not claim
  official pretraining UID disjointness.
- E0-D: WITH_LIMITATIONS; 48 GLB object--condition exports and 528
  unseen-view rows pass traceability checks, but the bake is a 12-object
  descriptive case study with explicit coverage, inpainting, source-fusion,
  missing-GT, DISTS, seam-denominator, source-hash, and Blender reindexing
  limitations.

## Revision acceptance

- The active manuscript reports strict-276 main results and the stage
  follow-up as separate protocol surfaces; repeated C3 outputs are not pooled.
- LLH is explicitly reported as better than LHL on all six non-SSIM metrics
  and saved-artifact Full-SSIM; LHL is not presented as a universal winner.
- The 17/16/17 intervention is explicitly not strict equal-effective-budget
  causal isolation.
- Old pooled +0.96 dB, CLIP-IQA, and blinded-preference claims are excluded
  from the compiled manuscript.
- The supplementary package includes object-level cases obj_0048, obj_0078,
  and obj_0082, the two-object GT smoke scope, and missing
  holdout_exact_76/PROTOCOL.json provenance.
- FAC is a separate negative extension and is not used to claim universal
  TCAS superiority.

## Expert assessment

Independent expert review is recorded in
EXPERT_NOVELTY_REVIEW_20260929.md.

- Algorithmic novelty: weak to weak--moderate.
- CAI as a unique selector: weak.
- Empirical/measurement contribution: moderate, bounded and adapter-dependent.
- R1/R2 revision coverage: accepted after targeted fixes.
- Final recommendation: ready for author review.

## Build and QA

- Native Codex LaTeX compiler: unavailable because the platform returned
  "Unable to find standard directories for platform"; source was preserved.
- Local pdflatex two-pass check: passed for both documents; no hard errors or
  unresolved references/citations.
- Output pages: manuscript 9 pages; supplementary material 3 pages.
- Round-two tests: 15 passed.
- Evidence scripts: py_compile passed.
- Active claim scan: no old pooled, CLIP-IQA, blind-study, universal-winner,
  or equal-budget wording.
- Remaining LaTeX warning: approximately 0.8--1.0 pt in the journal
  frontmatter template only; supplementary overfull warnings are cleared.

## Deliverables

- final/round2/final_round2.tex
- final/round2/final_round2.pdf
- final/round2/supplementary_round2.tex
- final/round2/supplementary_round2.pdf
- final/round2/response_letter_round2.md
- final/round2/coordination/E1_CLAIM_EVIDENCE_FREEZE_20260929.md
- final/round2/coordination/EXPERT_NOVELTY_REVIEW_20260929.md
- This file

