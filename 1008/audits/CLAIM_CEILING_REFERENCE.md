# Claim ceiling and evidence scope for 1008

**Updated:** 2026-10-08, following the author's round-history and R1.2 correction.

## Controlling history

The 01549 manuscript (`CAG-S-26-01549`) is the post-first-round revision submitted on 2026-09-07. The current R1/R2/R3 comments are the second-round reviews of that version; 1008 is its second-round revision. The official `final/submission_new_0907/` package—Manuscript, Marked-up Manuscript, Response Letter, Supplement, and `latex.zip`—is the first-round historical record. The authenticated TeX hash is `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.

Fresh C is interpreted under the author's specified paired protocol: one frozen checkpoint across the primary and same-cohort addendum conditions, common runner and seed policy, inputs, views, metrics, and recorded scale-cap semantics. Fresh C need not match the checkpoint hash named historically in 01549 Table 4. The v1/v2 historical experiment distinction remains explicit.

## Numerical anchors

The Fresh C primary contrast is C3 minus GFL on foreground PSNR:

- N=300 objects; mean difference **+0.522352 dB**.
- 95% object-bootstrap CI **[+0.404160, +0.640669] dB**.
- Median difference **+0.554514 dB**; C3 is higher on 206/300 objects (68.7%).
- Fresh C is a revision-era held-out paired result, not a numerical reproduction of historical Table 4's +0.96 dB.

The 01549 first-round 3AFC study (30 objects, 24 participants) remains a separately reported, scoped subjective preference result. The manuscript retains aggregate first-choice counts and its reported two-level participant/object bootstrap summary; individual participant rows are not redistributed.

The 01549 FAC controlled negative re-examination also remains as a previously reported auxiliary result, not a new 1008 run. The current archive has a recovered 1,200-object list against the 1,706-object pool reported in 01549, and lacks a run-bound seed/output manifest; that discrepancy is disclosed.

## Boundaries for paper-facing claims

| Topic | Supported wording | Do not claim |
|---|---|---|
| C3 / TCAS | A task-specific, training-free residual-scaling intervention with an empirical low–high–low profile; tested under the stated adapter and protocol | Universal optimum, unique winner, model-independent stage law, or schedule uniquely derived by CAI |
| Fresh C | Positive C3−GFL FG-PSNR result under one frozen checkpoint and shared paired protocol; report GFH, Generic Linear, and LLH endpoint counter-results | Overall superiority across endpoints; a Fresh C versus 01549 checkpoint-identity gate; numerical reproduction of +0.96 dB |
| Requested/applied scales | Report recorded native caps and distinguish requested scale, applied scale, and residual magnitude | Treating requested scale as applied scale or implying shared cap behavior where logs differ |
| Historical fixed-scale and C3 probe | Retain the original diagnostic and 24-object development questions, clearly marked historical/development-only | New confirmation, independent holdout, or verified schedule optimum from unrecoverable row-level records |
| Texture measures | Describe variation/high-frequency metrics as diagnostics where provenance is available | Texture fidelity, naturalness, or preservation inferred from RGB standard deviation, gradient magnitude, or Laplacian variance alone |
| Historical `+0.96 dB` | Identify it as the 01549 reported result and retain the v1/v2 and endpoint history | Present it as the Fresh C estimate or as numerically reproduced by Fresh C |
| CAI | State that the unsupported post-hoc derivation, selector, proof, and optimality claim are withdrawn | Predictive selector, proof of optimality, or unique derivation of C3 |
| FAC | Retain the 01549-reported negative controlled re-examination as auxiliary historical evidence with the archive limitation | New 1008 reproduction, positive FAC finding, code-release claim, or FAC as the TCAS contribution |
| First-round 3AFC | Report the submitted three-condition choice result and bootstrap summary within its original objects, questions, and design | Texture-fidelity, Fresh C, unseen-view, 3D-quality, or general perceptual-superiority claims |
| 3D / seams | Historical N=20 unlit base-color unseen-view observations with mixed endpoints, if explicitly scoped | PBR/material fidelity, seam quality, or population-level unseen-view superiority |
| Cross-backbone/interface | Report actual MV-Adapter and MVDiffusion interface probes and their limitations | Architecture-invariant transfer, causal backbone comparison, or direct absolute-score comparison |
| Prior art | Discuss Scheduled Style Injection and acknowledge layer/timestep schedule precedents; state the task-specific distinction | “First layer × timestep schedule” or broad control-space novelty |

Fresh C's C3–GFH Edge-SSIM contrast is post hoc (mean −0.018814; nominal 95% CI [−0.020803, −0.016790]; 47/300 objects favor C3). It must not be called equivalence or non-inferiority. LLH minus Generic Linear FG-LPIPS is +0.001372 (95% CI [+0.000762, +0.002081]); because lower LPIPS is better, this endpoint favors Generic Linear. Keep those counter-results visible alongside the primary comparison.

## Round-specific interpretation

- **R1:** resolve only the remaining second-round methodological and evidence concerns against 01549 and the first-round response; preserve first-round work acknowledged by R2.
- **R2.1:** strengthen the task-specific TCAS account without claiming general scheduling novelty.
- **R2.2:** withdraw only CAI's unsupported derivation and optimality claims; retain TCAS and C3.
- **R2.3:** report actual cross-backbone/interface tests and boundaries.
- **R3:** positive assessment; no new technical task.

This document supersedes its 2026-10-07 d59-based human/FAC dispositions and any interpretation that treats 01549 as the initial submission or requires Fresh C to match the historical Table 4 checkpoint.
