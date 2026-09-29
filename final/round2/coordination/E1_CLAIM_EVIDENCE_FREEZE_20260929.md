# E1 Claim--Evidence Freeze (2026-09-29)

## Scope

This ledger freezes the claims that may appear in the round-two manuscript,
supplementary material, and response letter. It supersedes older pooled,
preference-study, and exploratory-checkpoint wording. One bounded GPU
development pilot was subsequently completed; it is frozen as a negative
method-iteration record and does not alter the main TCAS evidence.

## Positive claims retained

| Claim | Direct evidence | Boundary |
|---|---|---|
| Adapter scale changes the shape--fidelity trade-off in the studied main adapter. | E0A_EVIDENCE_FREEZE_20260929.md; strict-276 clean-v2 table in final_round2.tex. | This is an adapter/protocol result, not a universal law. |
| Stage placement changes outputs under a frozen follow-up protocol. | 276 paired records, four schedules, six non-SSIM metrics, and serialized Full-SSIM in stage_placement_276_20260929. | The intervention is not strict equal-effective-budget: 17/16/17 steps and different scale sums/squared sums/residual norms. |
| TCAS is a simple training-free low--high--low residual-scaling implementation. | Method definition and frozen schedule (1.25, 2.50, 1.25). | It is an implementation and controlled mechanism study, not a learned selector. |
| The follow-up contains a useful LHL result but no universal LHL winner. | LLH exceeds LHL on all six non-SSIM means; saved-artifact Full-SSIM is 0.88313 vs 0.88144, with C3-minus-LLH CI [-0.00205,-0.00134]. | The result is a counterexample to unique CAI/LHL selection. |
| Full-SSIM serialization effects can be separated without model rerun. | fixed_gt_ssim_decomposition.py and FIXED_GT_SSIM_DECOMPOSITION.md. | The decomposition uses the saved 12-object tensors and is diagnostic, not a retrofit of old tables. |
| The end-to-end GLB/unseen-view path is operational for a small case study. | 48 object--condition exports and 528 unseen-view rows in cpu_bake_12. | 12 objects are descriptive only; no population-level 3D superiority, no DISTS, no GT bake, and cross-view colour inconsistency remain. |
| The independent MV-Adapter audit is a transfer audit with bounded interpretation. | 76-object/11 evaluated conditions/schedules frozen tables and paired comparisons. | High 1.50 and high 1.00 are separate; CAI is undefined/set-valued; official pretraining UID disjointness is unknown. |
| FAC is a separate negative extension under controlled paired conditions. | FAC audit and supplementary S6. | The initial positive comparison is superseded and is not a current claim. |
| TRB-TCAS does not replace the existing C3 schedule. | Pre-specified 24-object clean-v2 development pilot; TRB FG-LPIPS 0.1349 vs C3 0.1336, with approximately 2x calibration-inclusive cost. | Negative development evidence only; no strict-276 TRB holdout and no controller claim. |

## Explicit counterclaims and prohibited wording

- Do not state that LHL is best on all metrics, always best, or selected by a uniquely predictive CAI rule.
- Do not call the 17/16/17 comparison an equal-budget, causal, or perfectly isolated intervention.
- Do not pool the clean-v2 C3 outputs with the stage-follow-up LHL outputs: the common-object mean absolute Full-SSIM difference is 0.00395.
- Do not report the former +0.96 dB pooled value as a current result.
- Do not use the old CLIP-IQA or blinded preference study as evidence.
- Do not claim a population-level 3D quality gain from the 12-object bake.
- Do not call a confidence interval crossing zero evidence of equivalence.
- Do not claim cross-backbone causality, universal schedule transfer, or official pretraining-disjointness when the UID list is unavailable.

## Reviewer mapping

| Reviewer concern | Frozen answer |
|---|---|
| R1: practical quality versus fixed-low | The main strict-276 panel is non-dominating; fixed-low remains competitive. The 12-object baking case study does not show a C3 advantage. |
| R1: real 3D output | The GLB and unseen-view path is traceable, but the evidence is a limited case study with explicit missing GT bake/DISTS and colour-consistency limitations. |
| R1: metric provenance | Pre-save metrics and saved-artifact Full-SSIM are separated; fixed-GT decomposition reports dtype, prediction PNG, and GT PNG effects. |
| R2: method novelty | TCAS contributes a concrete training-free stage intervention and a reproducible stage-utility audit, while the manuscript now limits the claim to a bounded adapter-dependent study. |
| R2: empirical support | LHL has some wins in the follow-up, but LLH wins all six non-SSIM metrics and saved-artifact Full-SSIM; this is reported as a counterexample. |
| R2: generality/CAI | The second-backbone audit leaves CAI undefined/set-valued; the manuscript does not claim a unique or transferable selector. |
| FAC/learned extension | The controlled FAC re-examination is negative and is clearly separated from TCAS. |

## Added baking and provenance boundaries

- Supplementary S4 now lists obj_0048, obj_0078, and obj_0082 with raw
  coverage, inpainting fraction, and fixed-low/C3 unseen-view metrics.
- GT-to-GT baking sanity was only a two-object smoke (obj_0013, obj_0015);
  the 12-object generated batch has no GT condition.
- The original results/holdout_exact_76/PROTOCOL.json is absent. The
  available run_config.json and paired_bootstrap_exact.json are partial
  replacement provenance, not a reconstructed original protocol file.
- Baking source canonical hashes are blank in the handoff, and the seam scalar
  lacks a saved seam-pair count; these remain explicit audit limitations.

## Delivery state

The active manuscript, supplementary material, and response letter must be
compiled/checked against this ledger. The package is for author review only and
is not an automatic submission package.
