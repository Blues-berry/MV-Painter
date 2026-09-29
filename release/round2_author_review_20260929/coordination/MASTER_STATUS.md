# C&G 01549 Round 2 — Master Status

Audit date: 2026-09-29 UTC  
Role: coordination / scientific evidence gate

## Audit basis

This status is based on the local repository and its generated artifacts, not
only on the handoff report. Existing user changes in the worktree were left
untouched. No dataset, checkpoint, metric implementation, manuscript, or
response letter was changed while creating this coordination record.

Evidence labels used here:

- `INDEPENDENTLY_VERIFIED`: the artifact, path, protocol field, or hash was
  checked from this workspace.
- `VERIFIED_BY_AGENT_REPORT`: supported by an agent status report but not fully
  reconstructed here.
- `PENDING`: a protocol or output is prepared, but the required experiment or
  audit is not complete.
- `PROTOCOL_MISMATCH`: the result cannot be pooled with the target claim.
- `HISTORICAL_ONLY`: retained for provenance, not current independent evidence.

## Executive decision

E's final G1–G4 review is complete. All four gates pass with explicit
limitations, and Codex C is released for scoped manuscript and response-letter
edits. The remaining gate is editorial: E must audit C's diff, numerical
provenance and compiled tables before submission. No further GPU experiment is
required in this decision cycle.

The decisive scientific conclusion is bounded stage utility, not a universal
LHL optimizer. On the serialized PNG/raw-GT Full-SSIM branch, C3/LHL beats
fixed-mean and HLL but loses to LLH. B's handoff does not establish a unique
CAI winner or uniform LHL advantage; D's real 3D result remains a stratified
case study. The old `+0.96 dB` claim remains historical provenance only.

## Gate table

| Gate | State | Evidence assessment | Owner | Required next acceptance |
|---|---|---|---|---|
| G0 dataset/provenance | `PASS_WITH_LIMITATIONS` | Clean-v2 has 300 UIDs and zero recorded overlap with the historical 1,118-object list; controlled step-2000 checkpoint is hashed. Semantic alias detection for local-only assets remains limited. | A/D | Keep clean-v2 and checkpoint frozen; no cohort substitution. |
| G1 Full-SSIM | `PASS_WITH_LIMITATIONS` | Controlled same-generation trace is complete for 12 objects × 4 conditions: A/B pre-save tensors are identical, B→C shows uint8 PNG quantization/reload error, and C3−fixed-low changes from inconclusive A/B to negative C. Historical 300-object A tensors remain unavailable. | E, A, D | Freeze the PNG-reloaded float32/raw-GT branch for saved-artifact Full-SSIM, retain the historical-attribution limitation, and do not patch metrics retroactively. |
| G2 main stage mechanism | `PASS_WITH_LIMITATIONS` | Frozen 276-object CUDA run completed with 276×4 atomic records, zero errors, finite metrics and actual residual logs. A CPU-only PNG-reloaded float32/raw-RGBA Full-SSIM audit is complete; it supports stage-position effects but not a unique LHL winner. | E/A | Freeze the serialized Full-SSIM branch, retain pre-save versus saved-artifact provenance, and report LLH as a counterexample. |
| G3 cross-backbone | `PASS_WITH_LIMITATIONS` | B's 76-object Exact unified table and paired bootstrap are present. Frozen CAI is `undefined_set_valued`; MV-Adapter pretraining UID disjointness is unknown. | B | No more GPU inference unless a separately approved question arises; preserve labels and limitations. |
| G4 actual 3D | `PASS_WITH_LIMITATIONS` | Twelve Exact objects × four generated conditions produced 48 textured GLBs and 528 unseen renders; CPU LPIPS is available. Semantic mesh/polygon/UV checks pass, with Blender exporter reindexing on obj_0048; DISTS unavailable, 12-run has no GT bake, and visual inspection shows COLOR/SOURCE-FUSION inconsistency. | D | Preserve as stratified descriptive evidence; do not claim byte-identical export, DISTS, generated-texture superiority, or population-level TCAS advantage. |
| G5 paper release | `READY_FOR_SCOPED_C_EDIT` | E reviewed G1–G4. All gates pass only with the limitations in the claim ledger; the mechanism-study narrative is selected and C has a written authorization. | E → C | C may edit only under `C_PAPER_EDIT_AUTHORIZATION.md`; E must audit the diff and compiled numerical citations before submission. |

## Agent state

### A — main adapter

- Controlled retraining and clean-v2 four-condition baseline evaluation are
  complete and frozen (`INDEPENDENTLY_VERIFIED` from the manifests and audits).
- Full-SSIM controlled trace is complete with a limitation: controlled A/B/C
  tensors are saved and the PNG boundary is verified, but the original
  historical 300-object float tensors remain unavailable.
- Stage-placement runner, protocol, resume logic and CPU dry-run are ready;
  formal CUDA inference completed on GPU1 with a successful terminal manifest.
  The CPU serialized Full-SSIM postpass is now the paper-facing Full-SSIM
  branch; the pre-save formal CSV remains an audit artifact and is not to be
  substituted silently.
- A must not retrain, change C3, select a new cohort, or overwrite the frozen
  tables.

### B — MV-Adapter cross-backbone

- Exact calibration, selected-pair calibration, holdout, LHL transfer,
  matched-range and equal-budget results are already aggregated.
- `MV_ADAPTER_UNIFIED_RESULTS.csv`, `MV_ADAPTER_PAIRED_COMPARISONS.json`, and
  `MV_ADAPTER_FINAL_INTERPRETATION.md` are present and numerically usable.
- B is released from GPU work. No further inference is authorized for the
  current decision cycle.

### D — independent validation and baking

- `CODEX_D_STATUS.md` records the 12-object batch as complete, but its
  original next-step section predates the detailed Blender/UV/GT-sanity audit.
  The dated coordinator addendum and
  `coordination/BAKE_12_VALIDATION_AUDIT.md` are the current scope/acceptance
  record; the earlier text remains provenance.
- The two-object smoke is implementation evidence only, not a population
  result.
- D must not modify the frozen GLBs, UVs, source images, or cohort. D's dated
  correction is recorded; no further bake is authorized for this decision
  cycle.

## Current scientific interpretation

What can be said now:

- Clean-v2 is a UID-disjoint fixed-protocol controlled-rerun evaluation, not
  recovery of the missing original checkpoint.
- C3 is better than fixed-high on the clean-v2 controlled rerun in several
  global and foreground metrics, but it is below fixed-low on foreground PSNR
  and FG-SSIM; this is a non-dominance result.
- A-2 now provides a strict 276-object, four-schedule main-adapter mechanism
  test. On the frozen serialized Full-SSIM path, C3/LHL is above fixed-mean
  by `+0.00749` (95% CI `[+0.00674,+0.00826]`) and HLL by `+0.02151`
  (`[+0.01984,+0.02319]`), but below LLH by `-0.00170`
  (`[-0.00205,-0.00134]`). This supports adapter-scoped stage utility, not a
  unique or universal LHL rule.
- MV-Adapter shows some schedule-position differences, but no unique CAI
  choice and no uniform LHL gain over fixed-low or equal-budget fixed-mean.
- The completed 12-object CPU bake proves a real Exact-GLB textured export and
  unseen-render path for a stratified case-study cohort. It does not prove a
  276-object 3D advantage; the obj_0048 exporter reindexing, unavailable DISTS,
  and absence of a 12-object GT bake remain disclosed limitations.

What cannot be said now:

- the historical `+0.96 dB` as a strict independent result;
- that C3 has a stable Full-SSIM advantage over fixed-low;
- that CAI selected LHL, or that all schedules are equivalent;
- that a contact sheet or two-object smoke is a population-level 3D result;
- that the two backbone experiments establish absolute cross-backbone gains.
- that the A-2 pre-save Full-SSIM CSV is interchangeable with the serialized
  PNG/raw-GT branch.

## Next execution order

1. D's completed bake remains frozen as stratified descriptive evidence; no
   second bake is authorized. The current audit is
   `coordination/BAKE_12_VALIDATION_AUDIT.md`.
2. E freezes the serialized stage-placement Full-SSIM audit in
   `stage_placement_276_20260929/serialized_full_ssim_paired_comparisons.json`
   and the claim ledger in `coordination/CLAIM_EVIDENCE_LEDGER.md`.
3. C edits the manuscript and response letter under
   `coordination/C_PAPER_EDIT_AUTHORIZATION.md`; no new GPU work is queued.
4. E audits C's diff, table provenance and compiled output before any final
   submission decision.

