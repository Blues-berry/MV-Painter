# Round 2 Blockers

## B1 — Full-SSIM final path and historical attribution

- Severity: `P0 / paper-gating`.
- Root evidence: saved predictions are PNGs; static code shows the historical
  metric sees a pre-save float16 tensor while the audit sees a float32 PNG
  reload. The original float and pre-encoder tensors were not saved.
- Concrete files: `main_adapter_clean_v2/FLOAT_PNG_SERIALIZATION_TRACE.md`,
  `main_adapter_clean_v2/float_png_trace_12/float_png_serialization_manifest.json`,
  `geotex/trace_float_png_serialization.py`.
- Completed: one 12-object same-generation CUDA trace saved A/B/C tensors and
  exact scalar/array comparisons. A/B are identical; B→C is the measurable
  PNG quantization/reload boundary.
- Remaining: freeze the PNG-reloaded float32/raw-GT branch for any future
  saved-artifact table and keep historical 300-object attribution limited by
  missing original tensors. Do not apply the metric patch retroactively.

## B2 — main-adapter temporal placement inference

- Severity: `P0 / mechanism-gating`.
- Root evidence: frozen protocol and CPU dry-run exist; the formal result is
  now running in `stage_placement_276_20260929` and is not yet complete.
- Concrete files: `STAGE_PLACEMENT_PROTOCOL.json`,
  `STAGE_PLACEMENT_RUN_READY.md`, `geotex/stage_placement_eval.py`.
- Needed/acceptance: fixed mean, HLL, existing C3/LHL and LLH under identical
  seed, latent, camera, checkpoint, steps and unique6 mapping, plus actual
  residual norm logs for all 276 objects.
- Stop condition: partial run, nonfinite records, protocol mismatch, or any
  object/schedule selection invalidates formal inference; resume only from
  valid atomic records.

## B3 — 12-object real 3D bake validation

- Severity: `P1 / practical-value-gating`.
- Root evidence: 12-object CPU bake and unseen-view metrics are complete, but
  the evidence is stratified and has explicit exporter/DISTS/GT-sanity limits.
- Concrete files: `main_adapter_baking/BAKE_INPUT_HANDOFF.json`,
  `main_adapter_baking/cpu_bake_smoke_final/`,
  `main_adapter_baking/cpu_bake_12/`.
- Completed: 48 textured GLBs, 528 unseen renders, finite masked PSNR,
  CIEDE2000, LPIPS, coverage, seam and cross-view metrics; semantic polygon/UV
  checks pass. See `BAKE_12_VALIDATION_AUDIT.md`.
- Remaining limitation: `obj_0048` has exporter vertex reindexing, DISTS is
  unavailable, and the 12-object run did not include a GT bake. Do not call
  this byte-identical or DISTS-complete evidence.

## B4 — cross-backbone evidence boundary

- Severity: `P1 / interpretation-gating`.
- Root evidence: B's Exact 76-object unified values are complete, but the
  official MV-Adapter pretraining UID list is not available and scale families
  differ.
- Needed: no more inference for the current paper decision; disclose the
  pretraining limitation and avoid absolute cross-backbone PSNR comparisons.

## B5 — stale coordination artifacts

- Severity: `P1 / bookkeeping`.
- Root evidence: `CODEX_D_STATUS.md` records the batch as complete but its
  original next-step section predates the detailed validation; generated
  `cpu_bake_smoke_final` and completed `cpu_bake_12` outputs exist.
- Resolution: the dated coordinator addendum plus
  `BAKE_12_VALIDATION_AUDIT.md` are the current acceptance record. No bake
  duplication or cohort expansion is authorized.

## B6 — paper release dependency

- Severity: `P0 / publication`.
- Root evidence: Full-SSIM ordering, main stage effects and real 3D value are
  unresolved; claim ledger contains `PENDING` and `PROTOCOL_MISMATCH` rows.
- Resolution: C is blocked from filling final claims until E accepts G1–G4.
  Formatting, compilation and response scaffolding may proceed without numbers.

