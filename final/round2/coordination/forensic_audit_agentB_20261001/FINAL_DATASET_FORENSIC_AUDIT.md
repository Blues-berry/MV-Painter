# FINAL_DATASET_FORENSIC_AUDIT.md (Phase 5 — agent B)

Scope: cohort definitions, disjointness, selection rules, view constants, and
the MVDiffusion exclusion. Raw: `phase5_dataset_audit.json`. Heavy per-file
SHA inventory is NOT duplicated here — cross-reference
`final_audit_20261001/FINAL_REPRODUCIBILITY_MANIFEST.json` (parallel session)
and `SHARED_INPUT_DETERMINISM_AUDIT*.json` (0930 acceptance), both of which
verified input identity bitwise.

## 1. Cohort definitions (verified from files)

| cohort | definition | n | selection rule |
|---|---|---|---|
| eval-300 | `clean_dataset_v2/eval_objects_300_clean_v2.txt` = `data/train_data/rendered_full/test_objects_300.txt` (SHA e1bb89bb…) | 300 | frozen upstream test list |
| strict-276 holdout | `eval300[24:300]` (verified line-identical) ↔ obj_0024…obj_0299 | 276 | positional (last 276 of frozen order) |
| clean-v2 probe-24 | `probe_objects_24_clean_v2.txt` | 24 | frozen file; **∩ strict-276 = ∅ (verified)** |
| MV-Adapter calibration-24 | obj_0000…obj_0023 of the same frozen test list | 24 | positional (`range(0,24)`, prepare_manifest.py L62); **different set from probe-24** (verified ≠); precedes the holdout, no overlap |
| MV-Adapter holdout-76 | obj_0024…obj_0099 | 76 | positional (`range(24,100)`, L63) — **mechanical, result-blind** |
| MVDiffusion 76 | byte-equal object list to MV-Adapter holdout-76 (verified) | 76 | same rule |
| MVDiffusion 75 | 76 minus obj_0070 | 75 | predefined technical exclusion (below) |
| bake-12 | stratified 3-per-delta-quartile from a development comparison | 12 | documented; case-study only, never pooled |

Contamination checks: probe ∩ strict = ∅; MV-Adapter cal ∩ hold = ∅; no
duplicate IDs within any list (verified); all cohorts are test-side objects —
the 1,118/1,706 training pools are disjoint by the train/test file split (the
paper states this and the v1-checkpoint provenance audit covered the pool;
no contradicting evidence found in this pass).

## 2. Selection-rule integrity (no result-based selection found)

The 76-object cross-backbone cohort is chosen by **list position only**
(`prepare_manifest.py` slices the frozen UID file) — no metric, delta, or
visual criterion appears in the selection code path. The strict-276 is
likewise positional. No evidence of post-hoc object replacement: manifests
record `mesh_missing_objects` (10 objects, incl. obj_0013/obj_0015) with a
`GLB_RECOVERY_MANIFEST.json` documenting recovery; no silent swaps found in
the manifests compared here.

## 3. MVDiffusion obj_0070 exclusion — VALIDATED as predefined/technical

`MVDIFFUSION_INTEROP.md`: "obj_0070 is excluded from the runnable 75-object
holdout because its repaired RGB render has no valid depth pixels. No
replacement depth is synthesized." The 75-object manifest carries
`excluded_objects: ["obj_0070"]` and the runner flag `--exclude-object
obj_0070`. Rule is input-integrity-based, recorded before evaluation, and not
outcome-dependent. **PASS** (task-doc requirement satisfied).

## 4. View consistency

- Main backbone: `target_view_mode="unique6"` set and asserted by every
  formal runner (`run_layer_confirmation_276_20260930.py` L111/L114-115,
  core7, robustness); protocol manifests record
  `target_views = [0, 15, 12, 16, 13, 14]`.
- MV-Adapter: `round2_camera_ids: [0, 15, 12, 16, 13, 14]` (same set/order);
  output order `[14, 0, 12, 13, 15, 16]` is the official azimuth order and is
  documented as a permutation, not a different view set.
- MVDiffusion interop: target set `[0, 12, 13, 14, 15, 16]` — same set,
  different export order (documented); 12-view condition includes view 0.
- No reversed-orientation anomaly was found in the manifests checked;
  `reverse_dataset_orientation` is an explicit per-object handoff field.
- Known caveat (documented in the MVDiffusion manifest itself): interop
  target depth maps remain part of the 12-view condition, so those targets
  are not geometry-held-out novel views; and orthographic→perspective
  intrinsics are an approximation — no cross-backbone pooling.

## 5. File integrity

Per-object reference/GT/normal/depth/mask/GLB SHA verification is covered by:
`FINAL_REPRODUCIBILITY_MANIFEST.json` (evidence freeze), the bake handoff
(`BAKE_INPUT_HANDOFF*.json` exact_glb_sha256), `GLB_RECOVERY_MANIFEST.json`,
and the 0930 shared-input determinism audits (GFL anchor bit-exact;
0/276 input mismatches). This audit re-verified the cohort-list layer only.

## Verdict

`VALIDATED` — cohort structure is positional, documented, and disjoint; the
only exclusion (obj_0070) is predefined and technical; view constants are
consistent modulo documented output-order permutations. Residual limitations
to carry: (a) MVDiffusion interop targets are not geometry-held-out; (b) the
MV-Adapter calibration-24 and clean-v2 probe-24 are different 24-object sets —
paper text should not conflate them.
