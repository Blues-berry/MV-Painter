# Remaining Agent Orders — C&G 01549 Round 2

Issued by coordination on 2026-09-29 UTC.

These orders are based on the preserved review material, the current
`final/round2/final_round2.tex`, and the locally verified artifact registry.
They do not authorize changes to the dataset, checkpoint, C3, metric code,
main tables, manuscript, or response letter unless an order explicitly says so.

## Global freeze rules

1. Do not chase the historical `+0.96 dB`.
2. Do not select a new cohort, retrain, change C3, apply the float32 proposal
   patch, or replace a metric because it improves the narrative.
3. Do not call a CI crossing zero equivalence or non-inferiority.
4. Keep `historical`, `clean-v2`, `MV-Adapter Exact`, `smoke`, and
   `follow-up` protocol labels separate.
5. All output directories below are append-only/new directories. No agent may
   overwrite a prior CSV or share a live output directory with another agent.

## Order A-1 — same-generation Full-SSIM trace — COMPLETE WITH LIMITATIONS

Owner: A, with D as independent reviewer.  
Priority: P0, completed 2026-09-29.

The frozen trace was run on GPU0 in the new output directory
`main_adapter_clean_v2/float_png_trace_12_controlled_20260929/`.
Do not change the object list, seed, views, resolution, denoising steps,
checkpoint, C3, or evaluation implementation during the trace.

Required per method/object output:

- A: tensor used for float-eval;
- B: tensor passed to the PNG encoder;
- C: PNG-reloaded tensor;
- dtype, shape, range, mean/std, SHA-256 or exact array hash;
- A/B, B/C and A/C pixel MAE, max absolute error and PSNR;
- the same 3x3 Full-SSIM implementation evaluated at A, B and C;
- a manifest proving shared generation and object ordering.

Acceptance: all 12 objects × 4 conditions are present, finite and mapped to
the frozen CSV/PNG records. A missing original tensor is not a failure of the
experiment if the controlled rerun creates A/B/C simultaneously; it is a
limitation that must remain disclosed. Do not apply
`METRIC_FLOAT32_RECOMMENDED.patch` in this task.

Deliverables: trace directory and
`coordination/CONTROLLED_FULL_SSIM_TRACE_20260929.md`. A/B/C tensor and paired
SSIM acceptance passed. The historical 300-object A tensors remain missing;
the PNG-reloaded float32/raw-GT branch is the recommended saved-artifact path.
The paper and main table were not edited.

## Order A-2 — main-adapter temporal-placement ablation — COMPLETE WITH LIMITATIONS

Owner: A, with E as evidence reviewer.  
Priority: P0, completed 2026-09-29.

The frozen `STAGE_PLACEMENT_PROTOCOL.json` was run on GPU1 through the
independent resumable launcher
`scripts/run_stage_placement_276_20260929.py`; do not start a duplicate. Its
state is persisted in `final/round2/stage_placement_276_20260929/status.json`
and the run resumed the valid records already present in the clean-v2 strict
holdout
276 using the controlled step-2000 checkpoint. Conditions are exactly:

- fixed mean `(5/3, 5/3, 5/3)`;
- HLL `(2.50, 1.25, 1.25)`;
- existing C3/LHL `(1.25, 2.50, 1.25)`;
- LLH `(1.25, 1.25, 2.50)`.

Shared seed/latent, GT/camera/mask, 50 steps, unique6 mapping, 256x256 views,
object list and checkpoint must remain unchanged. Keep actual adapter residual
L2/RMS logs separate from nominal mean scale.

Acceptance:

- 276/276 objects have four complete atomic records;
- all numeric outputs are finite and there are no duplicate or missing IDs;
- paired bootstrap CIs and direction-aware win rates are computed at object
  level with the frozen seed;
- results include global, foreground, edge and GT-relative texture metrics;
- any conclusion distinguishes nominal equal mean from effective residual
  budget and calls this a targeted follow-up, not a blind confirmatory test.

If the placement effect is weak or metric-dependent, report that honestly. A
failed “unique winner” is a valid result and must not trigger more schedule
search.

Acceptance passed for the formal run: 276/276 objects × four schedules, zero
errors, finite fields, 50 actual residual steps per object/schedule, and
10,000-resample paired statistics. Because the formal runner computes metrics
before PNG serialization, E additionally required the CPU-only serialized
Full-SSIM audit in
`stage_placement_276_20260929/SERIALIZED_FULL_SSIM_STAGE_PLACEMENT.md`.
That saved-artifact branch reports C3/LHL versus fixed-mean `+0.00749`
([0.00674, 0.00826]), versus HLL `+0.02151` ([0.01984, 0.02319]), and versus
LLH `-0.00170` ([-0.00205, -0.00134]). The result supports stage utility but
not a unique LHL winner or a universal schedule rule. No further A GPU work
is authorized in this decision cycle.

## Order B-1 — freeze and package cross-backbone evidence

Owner: B.  
Priority: P1; no new GPU inference.

B's numerical work is complete. B should only perform read-only packaging:

- verify that the unified CSV, paired JSON, Exact cohort, scale-family labels,
  bootstrap seed and GPU handoff are mutually consistent;
- add a short reviewer-facing boundary note stating that the result is
  within-backbone schedule evidence, that CAI is set-valued, and that official
  MV-Adapter pretraining UID disjointness is unknown;
- do not compare absolute PSNR across MVPainter and MV-Adapter;
- do not call LHL a CAI winner or start another calibration/holdout run.

Acceptance: all values in the boundary note trace to existing files and no GPU
process is launched.

## Order D-1 — record and preserve validated real 3D baking

Owner: D.  
Priority: P1, bookkeeping and scope control.

The existing `final/round2/main_adapter_baking/cpu_bake_12` process has
finished. Do not launch a duplicate or extend the cohort. Preserve the
read-only validation and unseen-view metrics recorded in
`coordination/BAKE_12_VALIDATION_AUDIT.md` and the dated addendum in
`independent_validation/CODEX_D_STATUS.md`.

Required scope:

- 12 frozen Exact GLBs, original UVs and mesh geometry unchanged;
- four generated conditions: no-adapter, fixed-low, fixed-high, C3;
- six source views used for baking and 11 views not used for baking;
- actual textured GLB export with embedded image texture;
- GT-relative masked PSNR, CIEDE2000 and CPU LPIPS; DISTS is unavailable in
  this environment;
- raw texture coverage and post-inpainting coverage separately;
- UV seam discontinuity and cross-view texel variance;
- displayed/inspected GT-to-GT sanity output and representative actual
  unseen-view renders.

Acceptance already met with limitations: 48 method records, 528 unseen
renders (12 × 4 × 11), all finite where a metric is enabled, and semantic
mesh/polygon/UV checks. This is not a byte-identical mesh/UV hash guarantee:
Blender exporter vertex reindexing was observed for `obj_0048`; the 12-object
run also has no GT bake. The 12 objects are stratified case-study evidence,
not an unbiased estimate for all 276 objects.

D's dated coordinator addendum and the original pre-run/next-step wording must
remain traceable rather than silently overwritten.

## Order E/C-1 — scoped paper release after G1–G4 review

Owner: E coordinates; C is downstream.  
Priority: scoped release authorized 2026-09-29 after G1–G4 review.

C may now edit the manuscript and response letter, but only from the frozen
evidence ledger and the scoped authorization in
`coordination/C_PAPER_EDIT_AUTHORIZATION.md`. C must:

- use the serialized PNG/raw-GT Full-SSIM branch for the stage-placement claim;
- describe C3/LHL as adapter- and protocol-scoped, with LLH as a counterexample;
- retain the old `+0.96 dB` as historical provenance only, if mentioned;
- retain G1's missing historical tensor limitation, B's undefined CAI and
  pretraining-UID limitation, and D's 12-object case-study limitations;
- avoid universal, unique-winner, non-inferiority, absolute cross-backbone,
  population-level 3D, DISTS, or generated-texture superiority language.

C may not change datasets, checkpoints, C3, metric implementation, frozen
raw outputs, or experiment registry entries. E will audit the resulting diff
and numerical citations before final submission.

E's decision after A-1/A-2/D-1 is narrative 2:

2. **Mechanism study with bounded method support:** retain TCAS as a
   training-free temporal stage-utility analysis. The clean-v2 rerun supports
   gains against selected fixed schedules, but the LLH counterexample and
   fixed-low competition rule out a universal optimizer or blanket fidelity
   claim. The real 3D result remains feasibility/case-study evidence.

The other narratives are closed for this cycle:

1. **Method with bounded benefit:** retain TCAS as a training-free schedule
   that improves over fixed-high and shows a reproducible but non-dominant
   shape-texture trade-off, with real 3D evidence.
3. **Insufficient method support:** if placement effects and baking provide no
   reliable benefit, report the evidence to the user/mentor before any final
   claim rewrite.

