# Final acceptance checklist — layer-wise author-review package

Date: 2026-09-29

## Completed

- [x] Previous manuscript/PDF/response snapshots retained.
- [x] New layer-wise shared-input run completed: 24 objects × 3 seeds × 6
      conditions = 432 method/object-seed rows.
- [x] Hash audit completed for target, geometric input/features, and initial
      latent: 72 object-seed manifests.
- [x] Raw CSVs, manifests, summary, bootstrap seed, and SHA-256 index copied
      into `coordination/layer_lhl_v1/`.
- [x] Main manuscript and supplementary material compile successfully.
- [x] New visible complete-object and layer-wise comparison figure retained.
- [x] Added a direct visual baseline chain (GT, fixed-low, C3/LHL, layer-LHL)
      and a separate layer-wise schedule counterexample panel; both are
      included in the compiled main PDF.
- [x] Conclusion, limitations, response letter, and evidence index state that
      layer-LHL is representative rather than universally optimal.
- [x] Expert review completed for R1 practical evidence, R2 method novelty,
      cross-backbone scope, and remaining acceptance risks.

## Numerical acceptance

The new paired development evidence supports layer-wise foreground gains over
global fixed-low, but also records the counterexamples that constrain the
claim. Layer-LHL is not reported as the best method: layer-fixed-mean is
better on FG-LPIPS and layer-LLH is better on all seven reported metrics in
this development comparison. The strict-276 layer-LHL result is retained as a
separate transfer record, not relabeled as a paired holdout.

## Visual/PDF acceptance

- Main PDF: 11 pages, compiled twice after edits.
- Supplementary PDF: 5 pages, compiled twice after edits.
- Key pages inspected: complete-object evidence, shared-input table and both
  new comparison panels, strict-stage table, baking/cross-backbone boundary,
  limitations/conclusion, and full supplementary contact sheet.
- No new GPU experiment remains required for this revision decision. TRB is
  stopped and remains exploratory.

## Open items before submission

1. Author should decide whether to retain the old blinded preference study in
   the final submission package, since it evaluates C3 rather than the new
   layer-wise variant. If retained, label it historical/original-protocol
   evidence; if removed, preserve it in the archive.
2. If the journal requires a single main-method name, use “layer-wise
   stage-aware adapter scaling” and describe TCAS/C3 as the shared-layer
   baseline, not as the claimed optimum.
3. A future independent layer-wise second-backbone comparison would strengthen
   generality, but its absence is already disclosed and does not invalidate
   the current bounded claim.

Status: author-review delivery complete; no automatic submission performed.
