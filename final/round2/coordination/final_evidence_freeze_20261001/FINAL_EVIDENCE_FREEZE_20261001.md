# Round-2 final evidence freeze — 2026-10-01

This is an audit closeout, not a manuscript rewrite. No manuscript,
Supplementary, or response-letter source was edited; no model inference or
real-object rebake was run.

## Gate table

| Gate | Status | Blocking? | Determination |
|---|---|---:|---|
| 0. Remote provenance | **FAIL / live check pending** | Yes | Public target `origin` and private `mvpainter` are distinct. `git ls-remote` failed due network/DNS; live branch SHA cannot be asserted. |
| 1. Cap chronology | **PASS with limitation** | No for Core-7; yes for old cross-panel manuscript claims | Core-7 uses one capped path. Cap history is outcome-informed at development level; no strict-276 cap retuning found. Earlier uncapped panels cannot be pooled with Core-7. |
| 2. Core-7 provenance/statistics | **PASS with serialized-input limitation** | No | 276×7 rows; independent statistics reconcile on 42 shared pair/metric rows; source CSV and protocol audit retained. Five original Core-5 arms lack full 276-row tensor hashes. |
| 3. Historical LHL quarantine | **FAIL / active-source cleanup required** | Yes | Active TeX, Supplementary, and response letter still quote quarantined means and the refuted unseeded-RNG cause. They were not edited by instruction. |
| 4. Bake seam metric | **PASS** | No | Positive/negative controls pass; all 96 existing object-method records are non-empty and finite. No rebake. |
| 5. Cross-backbone boundary | **PASS** | No | MV-Adapter mapping is prespecified/topology-derived; MVDiffusion is a non-isomorphic interface boundary. No mapping experiment remains. |

## Final active evidence set

| Evidence | Role | Permitted use |
|---|---|---|
| Strict-276 capped Core-7, R0 | **CONFIRMATORY** | Main same-runner seven-condition quantitative comparison; report metric-dependent outcomes, not a universal winner. |
| R0/R1 preprocessing realization comparison | **ROBUSTNESS** | Supports stability to the independently resampled reference-preprocessing realization under the tested protocol. |
| Complete temporal-pattern / factorial probes | **DEVELOPMENT** | Mechanistic and method-screening evidence only; not a confirmatory universal schedule selection. |
| MV-Adapter layer-wise and mapping audits | **TRANSFER** | Partial, metric-dependent transfer under a prespecified topology-derived mapping and tested contiguous alternatives. |
| MVDiffusion CPBlock panel | **BOUNDARY** | Negative/mixed evidence for a non-isomorphic interface; not a direct replication. |
| Existing 12-object bake and corrected ΔE00 seam rows | **CASE STUDY** | Bounded, stratified case-study evidence; no population-level 3-D claim. |

## Permanently quarantined / superseded

- Historical LHL record (`FG-PSNR 14.776`, `Full-PSNR 22.052`, rounded
  `14.78`) and any comparison to current seeded LHL.
- “Unseeded Python RNG / reference preprocessing randomness caused the
  discrepancy” explanation.
- Absolute/rank comparisons that mix capped Core-7 with uncapped clean-v2 or
  stage-placement panels; within-panel historical contrasts must remain
  explicitly regime-specific.
- Old seam metric `uv_seam_discontinuity=0.0` (48/48), invalid and superseded.
- Legacy C3/CAI “unique winner / only promising schedule” claims in old
  0903 manuscript artifacts.
- Additive causal decomposition of overlapping LLH−GFL pair contrasts. The
  supported description is **“combined allocation effect.”**

## Conclusions that survive

1. Adapter scaling is usefully analyzed as allocation of a bounded residual
   across depth and denoising stage, not as one universally optimal scalar or
   schedule.
2. On the capped strict-276 Core-7, LLH has the best mean on four of seven
   headline metrics, but is not uniformly best: No Adapter ranks first on
   FG-SSIM; GFH ranks first on Full-LPIPS and Edge-SSIM. LHL is not the
   universal or main-backbone optimum.
3. LLH−GFL is a combined allocation effect. Current evidence does not support
   adding overlapping pair contrasts into an additive causal decomposition.
4. The main result is stable across the tested independent preprocessing
   realization; this does not explain the historical archived-LHL gap.
5. Layer redistribution partially transfers to MV-Adapter under a
   prespecified topology-derived grouping; temporal placement and outcome
   effects remain architecture-dependent. MVDiffusion is a non-isomorphic
   interface boundary where the layer-wise result does not replicate.
6. High-frequency texture failures remain a bounded failure mode; the 12-object
   corrected seam result is a case study, not a population claim.

## Figure and manuscript blockers

- `obj_0066` is rank 2/276 under the current LLH−GFL FG-PSNR comparison and
  should not remain an unqualified “representative” example.
- Active paper sources still contain historical LHL values/causality and
  uncapped-era cross-panel claims. Gate 3 and the live public-remote check
  remain open. The requested manuscript rewrite is a separate task.

## Remaining experiments and stop rule

**Mandatory new experiments: NONE.** Mapping provenance is closed and the
corrected seam metric passed two synthetic controls plus the existing 12-object
row audit. This audit performed CPU-only statistics and synthetic GLB controls;
it ran no model inference and no real-object bake.

`EVIDENCE_FREEZE = NO` for now, due to Gate 0 live remote verification and
Gate 3 active manuscript-source cleanup—not due to a missing experiment.
Do not restart experiment agents or expand the matrix absent a new P0
data/code discrepancy. Complete the separate manuscript rewrite, then
re-run only the repository/paper-source closure checks and live remote check.
