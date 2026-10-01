# FINAL_FORENSIC_AUDIT_REPORT.md (Round-2 Final Forensic Audit — agent B, 2026-10-01)

Session isolation: parallel audit session active in `final_audit_20261001/`;
this session delivered Phases 0-3, 5-7, 9, 11, 13-19, 21 in this directory
without touching the manuscript, the shared tree, or the other session's
files. Manuscript blob SHAs verified unchanged (FINAL_EVIDENCE_BRANCH_PROVENANCE.md §3).

## 1. Executive verdict

**YES — the paper can enter the final revision window**, conditional on the
revision-window items in §14 being executed (they are text/table substitutions
from already-frozen artifacts; none requires a new inference). No
experiment-blocking P0 remains open.

## 2. Scientific conclusions that survived audit

1. Layer-wise × temporal reallocation improves strict-holdout fidelity on the
   main backbone — same-runner, capped, hash-pinned; independently
   recomputed digit-for-digit (LLH−GFL +3.244, 242/276; LLH−LHL +1.001,
   Full-PSNR 276/0; LLH−LFM +0.875; Core-7 +5.149/+0.822 vs no_adapter/GFH).
2. Temporal placement and variation effects exist at matched budgets
   (~0.8-1.0 dB each).
3. R0/R1 robustness: outputs ~45 dB self-similar under a 35 % conditioning
   change; per-object drift median ≤0.09 dB; ranking unaffected.
4. MV-Adapter: layer redistribution SUPPORTED (metric-dependent, scale
   dimension); identity 9/9; mapping robustness closed on both tested axes.
5. MVDiffusion: valid as a boundary experiment; negatives preserved
   (identity 36/36; native mirror 1552/1552).
6. Statistics: directions verified by two independent implementations;
   bootstrap seeds documented; win rates reproduced.

## 3. Conclusions weakened by audit

1. **LLH−GFL +3.24 dB is a combined allocation effect**, not a pure temporal
   effect: ≈+2.4 dB deep/middle effective budget, ≈+0.9 placement,
   ≈+0.8 variation (RESIDUAL_BUDGET_CONFOUND_AUDIT). Claim width reduced
   accordingly.
2. **The clean-v2 "non-dominance" panel (tab:strict276) is an uncapped-regime
   artifact**: under the paper's own capped semantics the fixed_low/fixed_high
   ordering flips (7.03 vs 13.15 FG-PSNR) and no_adapter's FG paradox
   disappears (§7/§6; CROSS_RUNNER_SCALE_SEMANTICS_AUDIT).
3. **"LLH closest to GT gradient energy" is wrong** — GFH 1.11× vs LLH 1.13×;
   timing matters beyond energy (erratum flagged for the Core-7 report).
4. Per-object effect magnitude is strongly modulated by GT texture complexity
   (|ρ|≈0.64-0.68) — population-level claims only.

## 4. Invalidated / quarantined evidence

1. Archived LHL record (14.776 FG-PSNR): Case-B exclusion upheld; **the tex
   still quotes its means and the refuted unseeded-RNG causality (L470-481) —
   mandatory revision item**.
2. Original bake `uv_seam_discontinuity` (48/48 zeros): INVALID — index-keyed
   pairing cannot see UV-chart seams and the 1e-5 threshold admits degenerate
   same-texel pairs; superseded by corrected seam ΔE00 (LLH 4.89 lowest).
3. Uncapped-panel absolute numbers: QUARANTINED for cross-panel use
   (within-panel paired conclusions remain valid).

## 5. Dataset findings

Cohorts positional, disjoint, result-blind (FINAL_DATASET_FORENSIC):
probe∩strict=∅; 76-object cross-backbone cohort = first 76 of the frozen list;
obj_0070 exclusion predefined technical; view constants consistent (unique6;
documented output-order permutations). Caveats: MVDiffusion interop targets
not geometry-held-out; MV-Adapter cal-24 ≠ clean-v2 probe-24 (do not conflate).

## 6. Runner/code findings

Checkpoint/runner SHA-pinned; RNG inventory complete; latent fixed (42) by
design; train-mode uniform and provably inert (BatchNorm/dropout absent);
GFL anchor bit-exact; 0/276 input mismatches. Gaps (archival only): config
rescued; no formal-run PNGs; no residual-norm logs. **Major structural
finding: two wrapper regimes (capped repo vs uncapped /tmp legacy) executed
different paper panels** (§7).

## 7. Metric/statistical findings

Full-SSIM provenance: no table mixes branches (FULL_SSIM_GLOBAL_PROVENANCE_TABLE.csv);
CI/wording discipline clean ("no detected difference" convention). The
cross-runner gap for identical conditions is +3.7 to +7.7 dB FG-PSNR
(uncapped vs capped), with no_adapter invariant (+0.05) — isolating the
wrapper as the cause. A capped four-condition strict-276 table already exists
in frozen artifacts (no_adapter 8.826 / GFL 10.731 / GFH 13.153 / C3 11.939).

## 8. Visual findings

View mapping, masks, GT compositing: no defect (4 objects verified; alpha
fractions match). Metric-vs-image agreement holds (uncapped dark-tone
failures match their low PSNR). Capped layer-LLH (only archived images):
faithful structure, warm tint vs gray GT. Holdout-scale visual audit:
ARTIFACT_INSUFFICIENT (no PNGs archived); fixed future visual sets defined
from delta ranks. Figure provenance: obj_0066 "representative" is rank-2/276
— re-pick (median-band set provided) or re-caption.

## 9. Baking findings

12-object case study stands (descriptive); corrected seam metric discriminative
(LLH best tail statistics in matched generation); cross_view_texel_variance
semantics = source-view disagreement (not final-texture variation); paper
already discloses the seam-denominator gap; revision should cite the corrected
audit.

## 10. Cross-backbone findings

Three-level boundary (CROSS_BACKBONE_CLAIM_BOUNDARY): main = full support;
MV-Adapter = scale-dimension support only; MVDiffusion = boundary/interface
experiment (convex α on a serial module ≠ additive residual scaling);
"generalizes across backbones" forbidden; pooling forbidden.

## 11. Remaining experiments

None mandatory. Optional (decision-gated): (P1) capped re-run of the global
four-condition + stage-placement panels for cross-panel consistency of
absolute levels (frozen protocol, 276×6); (P2) image-archiving pass for any
future holdout visual claim; (P3) MVDiffusion depth-concat exploration only
under reviewer pressure. No schedule search, no new seeds, no cohort changes.

## 12. Final paper narrative recommendation

B+C composition (FINAL_SCIENTIFIC_NARRATIVE_STUDY): mechanism core ("where ×
when residual allocation, separable at matched budgets, combined-allocation
wording") + architecture-dependent transfer boundary; schedule observation
demoted to empirical support.

## 13. Reviewer-specific readiness

- Reviewer 1: PASS with the loss-analysis sentence and texture distance-to-GT
  framing ready; figure fix required.
- Reviewer 2: PASS at mechanism-study width; CAI/transfer/universal-optimum
  downgrades already specified.
- Reviewer 3: PASS after the revision-window disclosure upgrades (cap regime,
  archived-quote removal, cross-panel dB magnitudes).
- Skeptical reproducibility reviewer: PASS; all 40 challenge questions
  answered from artifacts (2 partial-framing, 1 archival remediation;
  SKEPTICAL_REVIEWER_CHALLENGE.md).

## 14. Final unresolved risks → revision-window checklist

1. Remove archived LHL means + RNG-causality from tex L470-481 (Case-B
   sentence only). [P0]
2. Replace or re-caption tab:strict276 with capped-protocol values; rewrite
   the non-dominance paragraph. [P0]
3. Upgrade cross-panel disclosure (L436-444) to state the wrapper regimes and
   dB magnitudes. [P0]
4. Fix the obj_0066 figure provenance (median-band re-pick or rank-disclosing
   caption); clarify obj_0048/0078 "failure-boundary" wording. [P1]
5. Add "evaluation cohort" (not fresh holdout) wording for the 76-object
   panel; optional multiple-comparisons sentence. [P2]
6. Correct "layer_llh closest gradient calibration" wherever it migrates. [P2]
7. Archive prediction PNGs in any future formal run; cite rescued config
   copy. [P2 hygiene]
8. Land the audit deliverables (both sessions) and the branch-provenance
   notes at the next push. [P0 process]

## 15. Index of this session's deliverables

FINAL_EVIDENCE_BRANCH_PROVENANCE / MAIN_EFFECT_DISTRIBUTION_AUDIT /
LLH_EFFECTIVE_CONTROL_AUDIT / RESIDUAL_BUDGET_CONFOUND_AUDIT /
CROSS_RUNNER_SCALE_SEMANTICS_AUDIT / R0_R1_OUTPUT_SENSITIVITY_AUDIT /
TABLE_NUMERICAL_FORENSIC_AUDIT + FULL_SSIM_GLOBAL_PROVENANCE_TABLE.csv /
BAKE_METRIC_IMPLEMENTATION_AUDIT / MVDIFFUSION_INTERVENTION_EQUIVALENCE_AUDIT /
CROSS_BACKBONE_CLAIM_BOUNDARY / FAILURE_MODE_AUDIT / FINAL_DATASET_FORENSIC_AUDIT /
FINAL_RUNNER_FORENSIC_AUDIT / FIGURE_SELECTION_PROVENANCE / VISUAL_FORENSIC_AUDIT +
FOREGROUND_BACKGROUND_METRIC_AUDIT / PAPER_NUMBER_TRACEABILITY.json /
FINAL_EVIDENCE_AUTHORITY / SKEPTICAL_REVIEWER_CHALLENGE /
FINAL_SCIENTIFIC_NARRATIVE_STUDY (+ scripts phase1a/1b15/phase5/phase7/phase16
and their JSON/CSV outputs).
