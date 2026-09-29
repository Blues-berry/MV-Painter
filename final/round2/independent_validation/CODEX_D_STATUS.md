# CODEX D Status

Date: 2026-09-29  
Scope: D1 independent clean-v2 provenance validation, D2 metric recheck, and D3 CPU baking.

## Current status

- **D1: PASS WITH LIMITATIONS.** The UID-set, split, mapping, checkpoint linkage, direct Smithsonian metadata, source-SHA, local-GLB, and complete rendered-bundle checks pass on the available evidence.
- **D2: PARTIALLY CONFIRMED.** The 11-object/44-row fixed diagnostic crosscheck confirms that float32/float64 precision and the tested SSIM implementation parameters do not explain the 0.026–0.037 Full-SSIM gap. No original float prediction tensors were found; the remaining boundary is recorded in `SSIM_ROOT_CAUSE_CROSSCHECK.md`.
- **D3: CPU BAKE SMOKE PASS; 12-OBJECT DIAGNOSTIC BATCH COMPLETE.** Two geometry-selected smoke objects passed GT-to-GT projection/export/re-import/unseen-render sanity checks. The four generated conditions were then baked for all 12 frozen objects, producing 48 textured GLBs and object-level metrics. The output is diagnostic rather than a 276-object population claim; DISTS is unavailable and generated-source color disagreement is documented.

## D1 deliverables

- `CLEAN_V2_PROVENANCE_MATRIX.csv`
- `CLEAN_V2_PROVENANCE_AUDIT.json`
- `CLEAN_V2_INDEPENDENT_AUDIT.md`

The clean-v2 UID set has zero overlap with the historical 1,118-object training list. The replacement rows are a subset of the 1,200-object candidate pool, and no replacement UID overlaps the historical training set. The remaining limitation is semantic alias detection for 187 local-only rendered assets without canonical source identifiers or local GLBs.

## D2 deliverables

- `METRIC_RECOMPUTE_SAMPLE.csv`
- `METRIC_RECOMPUTE_ALL.csv` (sample-scoped in this run)
- `METRIC_RECOMPUTE_SUMMARY.json`
- `METRIC_IMPLEMENTATION_AUDIT.md`
- `METRIC_FLOAT32_RECOMMENDED.patch` (proposal only; not applied)

The Full SSIM discrepancy is recorded as a provenance/implementation mismatch candidate rather than silently corrected. The proposed float32 hardening patch must be tested against original float predictions before any shared-code change.

## D3 readiness and result notes

- Handoff: `../main_adapter_baking/BAKE_INPUT_HANDOFF.json`; it freezes 12 exact GLBs, original UV preservation, 17 camera poses, 512×512 GT/masks, six unique6 generated views per condition, and a 1024 texture target.
- Static check: all referenced paths exist; all exact-GLB SHA-256 values, generated panel/view SHA-256 values, and expected dimensions pass. The cohort has 12/12 unique objects and 12/12 unique GLBs.
- Blender 4.2.4 was used for actual background CPU GLB import/export/material binding, not only startup checking.
- Implementation: `geotex/cpu_texture_bake.py`; evaluation: `geotex/evaluate_cpu_bakes.py`.
- Detailed result: `../main_adapter_baking/CPU_BAKE_PHASE2_REPORT.md`.
- Formal output: `../main_adapter_baking/cpu_bake_12/`.
- GT-to-GT smoke output: `../main_adapter_baking/cpu_bake_smoke_masked/`.
- The historical `BAKE_STATIC_AUDIT.md` remains the read-only pre-run audit; the Phase 2 report records the subsequent execution.

## Stop-gate

The available UID, metadata-SHA, local-GLB-SHA, and complete rendered-bundle evidence did not trigger the replacement stop-gate. No files in the frozen clean-v2 dataset or shared metric implementation were modified by this audit.

## Next required evidence

1. Recover original float prediction tensors or rerun the exact metric-producing evaluation.
2. Implement and test a CPU z-buffer/UV-preserving bake with explicit uncovered-texel reporting and shared blending across all conditions.
3. Recompute the full 300-object metric table before using Full SSIM in a paper-facing claim.

## Coordinator addendum — 2026-09-29

The 12-object CPU bake and unseen-view evaluation are now independently
audited in `../coordination/BAKE_12_VALIDATION_AUDIT.md`. The completed scope
is 48 generated GLBs and 528 unseen-view rows (12 objects × 4 methods × 11
views). Blender import/export checks preserve mesh-object counts, polygon
counts and UV-loop semantics; `obj_0048` has exporter vertex reindexing, so
the result is not byte-identical mesh evidence. CPU LPIPS is available, DISTS
is unavailable, and the 12-object run has no `gt` bake; the earlier
two-object smoke is the only GT-to-GT sanity scope. These results are
stratified implementation/case-study evidence, not a 276-object population
claim. No additional bake or cohort expansion is authorized in this decision
cycle.
