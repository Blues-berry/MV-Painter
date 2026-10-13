# Phase 2 evidence handoff

Date: 2026-09-29 UTC  
Status: evidence assembled and integrated into the author-review manuscript
package; final QA remains pending.

## R2 — cross-backbone evidence

The MV-Adapter package contains a traceable 76-object Exact Mesh cohort,
object-level metrics, paired bootstrap files, schedule provenance and an
equal-mean follow-up. It supports:

- the residual-scaling interface can be exercised on a distinct backbone;
- stage-position effects are observable within that backbone;
- no schedule dominates PSNR, FG-SSIM, Edge-SSIM, LPIPS, colour error and
  GT-relative texture error simultaneously;
- the frozen CAI rule is undefined/set-valued.

It does **not** support absolute cross-backbone score comparisons, transfer of
quality gains, causal claims, or pretraining-disjointness claims. The frozen
interpretation is in
`CROSS_BACKBONE_EVIDENCE_FREEZE_20260929.md`.

## R1 — complete-object and 3D-path evidence

The main-adapter package contains:

- 12 full-object comparison panels with GT, no-adapter, fixed-low,
  fixed-high and C3;
- an exact-cohort contact sheet and two stage-placement visual grids;
- a stratified 12-object exact-GLB cohort containing success, general and
  failure strata;
- 48 generated textured GLBs (four generated conditions × 12 objects) and
  528 unseen-view records (11 views × 48 condition/object rows);
- per-object coverage, seam, silhouette, LPIPS and colour-error records.

The CPU baking report confirms that geometry, UV, camera, visibility, export
and unseen rendering pass the smoke checks. It also records low coverage and a
source-fusion/colour inconsistency in generated results. Therefore the 3D
evidence demonstrates an operational path and failure boundaries, not a
population-level TCAS superiority claim.

## Required paper treatment

1. Put the full-object panels and fixed-low comparison in the R1 response and
   main results.
2. Put the full 12-object bake table, coverage and failure cases in the
   supplement; report missing metrics as unavailable.
3. State that the 12-object cohort is stratified and diagnostic.
4. Keep the MV-Adapter table as a bounded within-backbone audit.
5. Do not use the blocked aggregate `unseen_view_evaluation.csv` as a method
   result when its status is `blocked_no_baked_mesh`; use the completed CPU
   bake records with their explicit limitations instead.

## Phase 2 acceptance

The evidence is sufficient to revise the reviewer-facing narrative. It is not
evidence for a new universal controller or unconditional 3D improvement. The
manuscript, supplement and response letter have been updated using these
boundaries. Remaining work is final numerical cross-check, PDF visual
inspection and response-item QA.
