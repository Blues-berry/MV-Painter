# BAKE_PIPELINE_INDEPENDENT_AUDIT (final acceptance, 2026-09-30)

## BAKE_PIPELINE_AUDIT = PASS

243 forensic checks passed, 0 problems. Machine-readable trace:
`BAKE_PIPELINE_INDEPENDENT_AUDIT.json` (script:
`scripts/bake_pipeline_independent_audit_20260930.py`).

## Scope

End-to-end hand trace of 3 objects — `obj_0013` (ordinary), `obj_0048`
(exporter-reindexing case), `obj_0078` (requested alternative) — x 4 methods
(`global_fixed_low`, `global_c3`, `layer_lhl`, `layer_llh`), covering
prediction panel -> UV texture -> GLB -> unseen renders -> metrics. Summary
CSVs were NOT trusted; every checked quantity was recomputed from raw files.

## Verified chain per (object, method)

1. **Prediction panel** (`/4T/tmp/mvpainter-layer-bake-input-20260930/<method>/<obj>.png`):
   exists, SHA-256 recorded, 4 distinct hashes across methods, 4 distinct
   real paths (no softlink aliasing). Generation manifests for the layer
   runner and the global-controls runner record the same checkpoint
   (0618d6b2...), eval list (49627906...), cohort objects and cohort indices
   (13/15/38/48/54/66/68/78/82/83/110/111) -> same-draw seeding basis.
2. **Input Exact GLB**: `bake_metadata.input_exact_glb` resolves to the
   handoff `exact_glb_path` and its SHA-256 equals the handoff record — the
   same frozen input mesh for all four methods.
3. **UV texture**: 4 distinct SHA-256 across methods, correct dimensions,
   located inside its own method directory.
4. **GLB**: 4 distinct SHA-256; glTF JSON chunk declares the texture as an
   embedded bufferView image; the binary chunk contains the method's texture
   PNG byte-identically (no cross-method texture URI reuse).
5. **Unseen renders**: 11 per method (views 1..11 = handoff
   `unseen_raw_view_indices`, source set {0,12,13,14,15,16} excluded);
   all 44 render hashes distinct within each object across the 4 methods —
   no previous-method render reuse, LHL and LLH reference different files.
6. **GT**: per-object GT RGBA paths come from the method-independent handoff
   record (`gt_rgba_17`); GT hashes recorded per unseen view — identical GT
   for all methods by construction (evaluator code path confirmed:
   `geotex/evaluate_cpu_bakes.py` loads GT from the handoff, mask = GT alpha,
   no caching anywhere in the evaluator).

## Independent metric recomputation (from PNGs, not CSVs)

For each traced (object, method) and views {1, 6, 11}: masked PSNR and
CIEDE2000 recomputed from render vs GT with the evaluator's formulas:

- 18/18 PSNR and 18/18 CIEDE2000 recomputations match the per-view CSV
  within 1e-4.
- Object-level CSV values equal the mean of their 11 per-view rows.
- Per-object means for the traced objects (frozen CSV, masked PSNR):
  strictly ordered fixed_low < C3 < LHL < LLH on all three objects, e.g.
  obj_0013: 10.340 / 12.491 / 15.002 / 16.367; obj_0048: 9.418 / 11.194 /
  13.669 / 14.966; obj_0078: 6.767 / 7.153 / 9.182 / 12.019.
- `obj_0048` inpainted fraction = 0.8440961 for all four methods, matching
  the manuscript's "0.8441" (geometry-driven, method-independent as stated).

## Ruled-out failure modes

Wrong prediction dir, object-ID mismatch, camera-order mismatch, GT
mismatch, source-view-as-unseen, mask inconsistency, softlink aliasing,
texture reuse across methods, GLB texture URI mismatch, evaluator cache
pollution, previous-method render reuse, LHL/LLH same-file aliasing, metric
CSV copy/concatenation errors — all explicitly checked, none found.

## Permitted claim

On the frozen 12-object stratified case-study cohort, layer-wise controls
consistently improve the reported unseen-view metrics over the same-draw
global controls. This is a case-study result, not population-level 3D
superiority; no generated GT bake or DISTS evaluation is available.
