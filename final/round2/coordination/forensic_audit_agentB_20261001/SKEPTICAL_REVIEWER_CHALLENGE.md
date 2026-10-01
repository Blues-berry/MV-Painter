# SKEPTICAL_REVIEWER_CHALLENGE.md (Phase 19 — agent B)

Format: hardest 10 questions per persona; each answered with artifact + code +
explanation or marked OPEN. A = Reviewer 1 (fidelity/texture), B = Reviewer 2
(novelty/mechanism), C = Reviewer 3 (evaluation rigor), D = Skeptical
Reproducibility Reviewer.

## Reviewer 1 — fidelity & texture
1. "Why is LLH +3.24 dB over fixed-low?" → Decomposed: ≈+2.4 dB deep/middle
   effective budget, ≈+0.9 temporal placement, ≈+0.8 temporal variation
   (RESIDUAL_BUDGET_CONFOUND_AUDIT; LLH−LHL 276/0 Full-PSNR). Not a pure
   scheduling effect; claim width adjusted.
2. "Is texture variation texture fidelity?" → Distance-to-GT framing
   everywhere (parallel session texture audit + Core-7 extension); exceptions
   listed verbatim; LapVar never claimed as fidelity.
3. "What about the 34 losses?" → Realization-persistent (32/34), concentrated
   on 2-3× richer GT textures; LLH lap-var 0.47× GT there; FG-SSIM still wins
   (FAILURE_MODE_AUDIT).
4. "Do images look 3 dB better?" → Capped layer-LLH images: only obj_0024/25
   archived — structurally faithful, warm tint vs gray GT (VISUAL_FORENSIC);
   holdout-scale visual set = ARTIFACT_INSUFFICIENT (no PNGs archived). OPEN
   until a future image-archiving run or reliance on dev/bake visuals with
   labels.
5. "Seams?" → Corrected texture-space seam ΔE00 (LLH 4.89 lowest of 8 in
   matched generation); original zero metric documented invalid
   (BAKE_METRIC_IMPLEMENTATION_AUDIT).
6. "Cross-view consistency of generation?" → Bake cross-view descriptors +
   source-view texel variance semantics documented; render-time descriptor
   labeled non-fidelity (parallel session report).
7. "Why does No-Adapter win FG-SSIM?" → Blur pseudo-advantage, gradient
   0.89× GT; retained as honest residue.
8. "Warm tint vs gray GT?" → Visible on the archived capped images; metric
   gap consistent; no silent claim that generations match untextured GT
   better than they do.
9. "Is obj_0066 representative?" → No: rank 2/276 (FIGURE_SELECTION);
   re-pick via median-band rule or re-caption.
10. "Bake population claim?" → 12-object stratified case study only; never
    pooled.

## Reviewer 2 — novelty & mechanism
1. "Isn't this just schedule tuning?" → Mechanism framing: where × when
   separable at matched budgets (LLH−LHL, LLH−LFM); architecture-dependent
   boundary (MV-Adapter/MVDiffusion).
2. "Why layer groups 3 with 4 blocks?" → Pre-registered mechanical mapping +
   bitwise-degenerate + budget-neutral + frozen-value axes all tested
   (mapping sensitivity; PSNR nuance disclosed).
3. "Is CAI automatic discovery?" → No: undefined_set_valued; diagnostic
   motivation only.
4. "Why temporal positions 1/3-2/3?" → Convention frozen before confirmation;
   stage boundaries documented (17/16/17); the LLH-vs-LHL comparison is
   within-convention.
5. "MVDiffusion negative — why claim transfer at all?" → Claim width: one
   additional adapter architecture, scale dimension only; MVDiffusion is a
   structurally different interface (MVDIFFUSION_INTERVENTION_EQUIVALENCE).
6. "Is LLH universal?" → No — refuted internally; never claimed.
7. "What does the budget decomposition add?" → It reattributes the headline:
   combined allocation effect; prevents overclaiming (binding rule).
8. "Novelty vs TCAS/C3 literature?" → Layer×temporal reallocation as an
   inference-time control dimension; bounded by the two external backbones.
9. "Is the mechanism gradient-energy calibration?" → Partially: LLH 1.13× GT
   closest among layer schedules BUT GFH 1.11× is closer and loses — timing
   matters beyond energy (corrected wording flagged).
10. "Why no learned controller?" → FAC negative results retained; no
    configuration selected on evaluation objects.

## Reviewer 3 — evaluation rigor
1. "Are panels comparable?" → No across panels; disclosed; cap-regime cause
   now documented (CROSS_RUNNER_SCALE_SEMANTICS) — revision item to upgrade
   the disclosure from 0.00395 SSIM to dB magnitudes.
2. "Full-SSIM two orderings?" → pre-save vs PNG-reload split into separate
   labeled tables; 0.00395 runner gap quantified; no mixed table.
3. "Holdout integrity?" → Positional cohorts, UID-disjoint, no replacement
   after outcomes (FINAL_DATASET_FORENSIC); obj_0070 exclusion predefined
   technical.
4. "76-object fatigue — still holdout?" → Selection positional/result-blind;
   BUT the cohort has now been observed across many panels; no result-based
   exclusion found. Honest wording: "evaluation cohort" rather than fresh
   holdout for cross-backbone claims. PARTIALLY OPEN (framing).
5. "Metric directions verified?" → Double-implementation recheck (parallel
   session + agent B digit-match); benefit-oriented convention documented.
6. "Statistics reproducible?" → Seed 20260930/20260928 bootstrap, bitwise
   re-run (parallel session), agent B independent recomputation agrees.
7. "Equal-budget pilot?" → Excluded (no checkpoint provenance); matched pairs
   (LHL/LFM) used instead.
8. "Why no CIs in some tables?" → Descriptive case studies labeled as such.
9. "Multiple comparisons?" → Not formally corrected; primary hypotheses were
   pre-registered (protocol lock); secondary comparisons framed as
   exploratory. PARTIALLY OPEN (could add one sentence).
10. "Randomness source?" → Realization lottery quantified mean-neutral; latent
    fixed by design (uniform across methods); dev-24 3-seed covers noise
    robustness.

## Reviewer D — reproducibility
1. "Checkpoint/config provenance?" → SHA-pinned; config rescued into repo.
2. "Runner hash?" → Frozen runner SHA in manifests; verbatim-path policy.
3. "Why did historical LHL differ 1.8 dB?" → Case B: head/tail merge,
   realization-neutrality proof, root cause unreconstructible; excluded; RNG
   causality retired (archived_vs_current_runner_diff).
4. "Cross-process determinism?" → GFL anchor bit-exact; 0/276 input-hash
   mismatches; identity gates 9/9 and 36/36 bitwise; native mirror
   1552/1552.
5. "Two wrapper regimes?" → Documented (this audit); caps bind only for
   global schedules; layer-schedule results cap-insensitive.
6. "Seed semantics?" → object_seed 42+idx / 10042+idx; latent 42; cond-VAE
   reseed; RNG inventory in FINAL_RUNNER_FORENSIC.
7. "Why no prediction PNGs for formal runs?" → Archival gap; disclosed; fix
   recommended. OPEN (remediation only).
8. "Eval mode?" → Train-mode uniform across all conditions; BatchNorm/dropout
   inert (verified); hygiene note only.
9. "Legacy /tmp code trees?" → clean-v2 + stage-placement ran under
   /tmp/mv_main_rerun (uncapped); tree still on disk; recommend archiving the
   two wrapper variants' diff into the repo (this audit documents it).
10. "Can a stranger re-derive every table?" → Traceability JSON lists the
    chain per table; two cells flagged (archived quote; uncapped panels).

**OPEN count: 0 blocking / 2 partial-framing items (76-object fatigue
wording; multiple-comparisons sentence) + 1 archival remediation (PNGs).**
