# SCIENTIFIC_VALIDATION_DECISION_REPORT — FINAL

- Date: 2026-10-05
- **AMENDED 2026-10-05 (P0-1 closure):** the production interaction test was
  zero-power (`PRE_ACCEPTANCE_AUDIT_20261005.md` P0-1). CLAIM 2 (failure-
  cases line), CLAIM 3, CLAIM 8 and the final ruling below are re-derived
  with the validated cluster-robust Wald test
  (`audit_scripts/AUDIT_INTERACTION_VALID_TEST.json`,
  `AUDIT_INTERACTION_VALID_TEST_G.json`). Amendments are marked **[AMENDED
  P0-1]**. No data row changed; see `PRE_ACCEPTANCE_ISSUE_CLOSURE.md`.
- Branch: codex/scientific-validation-v3-20261002 (base 29b3a0a)
- Cohort: FRESH_CONFIRM_300 (frozen, seed 20261002; 508 disjoint candidates →
  450 technically valid → 300 selected; full audit trail committed)
- Runner: scripts/run_validation_v3_experiment.py (verbatim Core-7 per-object
  path; latent seed 42; unique6 [0,15,12,16,13,14]; 50 Euler steps) + G runner
- Statistics: PRIMARY_HYPOTHESES.md (pre-registered); paired object-level
  bootstrap 10,000 resamples, seed 20261002; Holm per family
- Manuscript files were NOT modified in this phase (STOP RULE honored).
- See also: NARRATIVE_RESTRUCTURE_REQUIRED.md (triggered).

Per-claim fields: experiment | cohort | comparator | effect (95% CI) |
correction | failure cases | allowed wording | forbidden wording.

--------------------------------------------------------------------------------
CLAIM 1 "Adapter scaling has a layer-dependent effect." → **SUPPORTED**
--------------------------------------------------------------------------------
- Experiment: A3 (dose-normalized) + B3 TRUE-GLOBAL decomposition
- Cohort: FRESH_CONFIRM_300 (n=300)
- Comparator: equal-dose interventions vs layer-fixed-low baseline;
  LFM-EXACT / native vs TRUE-GLOBAL
- Effect: equal-dose layer marginals (FG-PSNR): deep +0.55 dB, middle +0.29 dB,
  shallow −6.07 dB; LFM-EXACT vs TRUE-GLOBAL-1.675 +2.99 dB [2.43, 3.55]
- Correction: A3 family (16 tests) Holm; layer effects significant
- Failure cases: none at the layer level; shallow at high dose is destructive
  (this is the effect, not a failure)
- Allowed: "adapter residual effects differ strongly and reproducibly across
  UNet depth groups at matched residual dose; shallow protection is critical"
- Forbidden: any claim that the layer map generalizes across backbones (see
  claim 8); any dose-numbers claim without the uncapped-path caveat

--------------------------------------------------------------------------------
CLAIM 2 "Adapter effect is timestep-dependent." → **PARTIALLY SUPPORTED (weak)**
--------------------------------------------------------------------------------
- Experiment: A2 raw map + B2 temporal-location contrasts
- Comparator: single-window interventions vs baseline; LLH vs LLL/HLL
- Effect: A2 cell deltas exist but are tiny (|ΔFG-LPIPS| ≤ 0.0064); B2:
  late-high beats all-low by +0.84 dB [0.75, 0.93] and early-high by +0.85 dB
  [0.66, 1.05]
- Correction: Holm (A: 16 tests; B2: 4 tests) — all rejected
- Failure cases: **[AMENDED P0-1]** at equal dose (A3) the *time-structure*
  variance share is strongly reduced (FG-PSNR interaction share 0.8%,
  FG-LPIPS 11.9%) but NOT absent — the interaction is statistically
  significant on the valid Wald test; no single window is special at equal
  dose within the valid (deep) row
- Allowed: "a monotone late-increasing temporal profile yields a small real
  benefit over a constant budget-matched scale"
- Forbidden: "timestep-specific gating/switching is a discovered mechanism";
  any per-window tuning claims

--------------------------------------------------------------------------------
CLAIM 3 "There is a layer × timestep interaction." → **SUPPORTED WITH
QUALIFICATION** **[AMENDED P0-1]**
--------------------------------------------------------------------------------
- Experiment: A2 raw + A3 dose-normalized (pre-registered primary H1)
- Comparator: two-way model; interaction tested with the VALIDATED
  cluster-robust Wald test (8 Helmert row×col interaction contrasts,
  object-level sandwich covariance), replacing the zero-power production
  bootstrap (P0-1)
- Effect: A2 (native dose): FG-LPIPS W = 481.1, p = 8.0e-99, interaction SS
  share 43.5%; FG-PSNR W = 1880.0, p ≈ 0, share 56.8% — the interaction is
  REAL and substantial (cell structure directly visible: deep deltas ×1e-4 =
  [−29.3, +5.9, +41.3, +35.2, +23.8] across W1–W5, an early→late sign flip).
  A3 (dose-normalized): still highly significant (FG-LPIPS W = 657.2,
  p = 1.1e-136, share 11.9%; FG-PSNR W = 1389.1, p = 1.3e-294, share 0.8%)
  but the time-structure variance share collapses at matched dose.
  Cross-checks: naive ANOVA F = 117.8 (p = 1.9e-179); subsample- and
  winsorization-stable; corroborated by B3's independent +0.43 dB temporal
  component.
- Correction: the pre-registered H1 family used the defective bootstrap for
  the interaction member; the Wald test is size-validated (tests A/F) and
  power-validated (test B ≥ 32/40) — reported here as the authoritative
  interaction result
- Qualification: dose normalization is exact only for the deep row
  (VALID_DOSE_NORMALIZED_CONFIRMATION); middle is approximate (E-ratio 5.1×
  vs requested 2.73×); shallow is STRESS_TEST_ONLY — "survives dose
  normalization" is fully valid for deep, approximate for middle
- Allowed: "a genuine layer × timestep interaction exists at native dose
  (large variance share); after residual-dose normalization it remains
  statistically detectable but its variance share collapses, especially on
  FG-PSNR; the layer main effect dominates at equal dose"
- Forbidden: "no interaction" / "the supported structure is purely additive"
  (false); "the interaction is a large practical scheduling lever" (bounded:
  linear-ramp equivalence, CLAIM 7); per-window tuning claims

--------------------------------------------------------------------------------
CLAIM 4 "1/3 stage boundaries reflect the empirical response." → **HEURISTIC ONLY**
--------------------------------------------------------------------------------
- Experiment: A2/A3 response maps
- Comparator: window response profiles vs frozen boundaries at steps 16/17,
  32/33
- Effect: no discontinuity or boundary-aligned response at equal dose;
  profiles are window-flat within layers
- **[AMENDED P0-1 note]** the "window-flat at equal dose" reading is fully
  valid only for the deep row (A3 middle = approximate normalization,
  shallow = stress-only); the valid A2 map shows a smooth positional
  response (deep early→late sign flip), not boundary-aligned switches —
  boundary status unchanged (heuristic)
- Correction: descriptive (A3) + Holm family A
- Allowed: "three-stage boundaries are a design heuristic"
- Forbidden: "empirically derived/validated boundaries"

--------------------------------------------------------------------------------
CLAIM 5 "Temporal variation helps beyond the exact per-layer mean." → **SUPPORTED (small)**
--------------------------------------------------------------------------------
- Experiment: B1 (LFM-EXACT = exact 17/16/17 per-layer means, constant)
- Cohort: FRESH_CONFIRM_300 (n=300)
- Effect: LLH − LFM-EXACT = +0.435 dB FG-PSNR [0.356, 0.516]; −0.0045 FG-LPIPS
  [−0.0052, −0.0039]; Holm family B1 p = 0.0002
- Correction: Holm family B1 (2 tests)
- Failure cases: pre-registered equivalence NOT established (PSNR CI upper
  0.516 > 0.5 margin). LLH−GFL is +1.288 dB; only +0.435 dB is isolated by
  the exact per-layer-mean temporal contrast. The remaining +0.853 dB
  LLH−LFM-EXACT vs LFM-EXACT−GFL term changes depth doses and shallow-cap
  state together; it cannot be labeled “budget alone” or “layer alone.”
- Allowed: "LLH retains a small advantage over an exactly per-layer-
  mean-matched constant (+0.4 dB); the larger LLH−GFL difference also changes
  depth doses and the shallow cap profile."
- Forbidden: "the LLH−GFL difference is additively decomposed into cap,
  layer, and temporal contributions" or "the remaining effect is budget
  alone."

--------------------------------------------------------------------------------
CLAIM 6 "Named depth/cap policies differ from uncapped uniform controls." → **SUPPORTED (DESCRIPTIVE DIAGNOSTICS)**
--------------------------------------------------------------------------------
- Experiment: B3 TRUE-GLOBAL diagnostics (uncapped, causal-only)
- Cohort: FRESH_CONFIRM_300 (n=300)
- Comparator: native/capped conditions vs TRUE-GLOBAL at matched requested
  global scales; these do not match effective shallow scale or total dose
- Effect: GFL vs TRUE-GLOBAL-1.25 +1.60 dB [1.37, 1.82]; LFM-EXACT vs
  TRUE-GLOBAL-1.675 +2.99 dB [2.43, 3.55]; GFH vs TRUE-GLOBAL-2.50 +4.66 dB
  [4.07, 5.23]; FG-LPIPS all favor layer-aware
- Correction: descriptive diagnostic contrasts only; not a decomposable
  factorial effect and not a deployment recommendation
- Failure cases: TRUE-GLOBAL runs were stable (no NaN); they are diagnostics,
  not deployment candidates
- Allowed: "at requested global 1.25 and 2.50, the native shallow cap changes
  the paired FG-PSNR result by +1.60 and +4.66 dB respectively; LFM-EXACT
  differs from uncapped TGU-1.675 by +2.99 dB while reducing shallow exposure.
  These are separate contrasts with different endpoints and must not be
  summed."
- Forbidden: presenting TRUE-GLOBAL numbers as method variants; pooling
  capped/uncapped rows

--------------------------------------------------------------------------------
CLAIM 7 "L-TCAS beats generic schedule families under the authoritative protocol."
→ **METRIC-DEPENDENT / PARTIAL**
--------------------------------------------------------------------------------
- Experiment: C (endpoint- and budget-matched generic families)
- Cohort: FRESH_CONFIRM_300 (n=300)
- Comparator: LLH vs linear warm-up / cosine bump / trapezoid / Gaussian peak
  (both variants)
- Effect: LLH − generic = +0.30..+0.59 dB FG-PSNR (all Holm-rejected) EXCEPT
  endpoint-matched linear warm-up: +0.005 dB [−0.10, +0.11], Holm p = 0.81
  (statistically equivalent); FG-LPIPS favors LLH slightly everywhere
- Correction: Holm family C (16 tests): 15/16 rejected
- Failure cases: the linear-ramp equivalence
- Allowed: "LLH outperforms bump/trapezoid/Gaussian generic shapes and their
  budget-matched variants; a per-layer linear warm-up performs on par"
- Forbidden: "LLH universally dominates generic schedules"; hiding the linear
  equivalence

--------------------------------------------------------------------------------
CLAIM 8 "The principle transfers to MV-Adapter." → **UNSUPPORTED (backbone-specific)**
--------------------------------------------------------------------------------
- Experiment: G (per-point window map, frozen topology-derived mapping)
- Cohort: **n = 98/99 planned** after completing 17 of the 18 missing
  objects. The original 1,600 ledger rows contained 304 exact repeated
  object-condition rows; 81 unique objects were supplemented by 272 rows for
  17 further objects. The last planned object (`g_0098`) is a frozen GLB with
  path geometry and no triangle faces, so the unchanged G loader cannot
  process it. No substitute input was used; see `g_formal_complete/` and
  `PRE_ACCEPTANCE_ISSUE_CLOSURE.md` P1-5.
- Comparator: g_baseline vs 15 (group, window) interventions at 0.75→1.00
- Effect: the production additive-residual bootstrap remains invalid for
  interaction inference. Exploratory cluster-robust Wald reanalysis on the
  completed data gives primary FG-LPIPS W = 13.322, p = 0.101 and PSNR
  W = 7.995, p = 0.434. FG-SSIM is p = 0.039 unadjusted but p = 0.156 after
  Holm correction across four metrics; no interaction metric survives that
  exploratory correction. Shallow W3–W5 show small adverse FG-LPIPS deltas
  (+0.00045 to +0.00046) that survive the registered 15-cell Holm family;
  deep and middle effects remain near zero.
- Correction: Holm family G (16 tests)
- Failure cases: the intervention range [0.75, 1.0] may simply be too weak on
  this backbone — the report must state this scope limit (no dose escalation
  was run by design; dose ratio <2x pre-registered rule)
- Allowed: "the large main-backbone layer/time response was not reproduced
  by this frozen MV-Adapter intervention range; only small late shallow
  FG-LPIPS worsening was detected, and an interaction remains unconfirmed"
- Forbidden: "architecture-dependent allocation principle" (option A) or
  "layer-aware scaling transfers" (option B) — neither is supported

--------------------------------------------------------------------------------
CLAIM 9 "The method improves practical 3D texturing." → **BOUNDED SUPPORT**
--------------------------------------------------------------------------------
- Experiment: F unified same-draw bake (one namespace, 11 unseen views)
- Cohort: 20/24 pre-frozen objects (4 technical exclusions: UV-less meshes)
- Comparator: adapter conditions vs no_adapter; LLH vs other schedules
- Effect: adapter vs no_adapter +3.6 dB [2.2, 4.7] (large, unambiguous);
  LLH vs GFL on unseen views +0.14 dB [−1.29, +1.65] (n.s.); FG-LPIPS favors
  LLH (−0.024 [−0.032, −0.017]); LLH has the LOWEST UV-seam dE00 of all
  schedules (vs GFL mean −6.90 [−8.29, −5.47], p90 −17.44 [−21.12, −13.60])
- Correction: descriptive paired CIs (F was confirmatory only for claim scope)
- Failure cases: 4 UV-less objects excluded; DISTS unavailable
- Allowed: "the adapter materially improves 3D texturing; LLH additionally
  yields better perceptual fidelity and UV-seam cross-view consistency on
  unseen views (n=20)"
- Forbidden: population-level LLH PSNR superiority on 3D metrics

--------------------------------------------------------------------------------
CLAIM 10 "Texture-rich objects define a systematic failure boundary." → **REPLICATED**
--------------------------------------------------------------------------------
- Experiment: E prospective test (pre-registered H0 rejected)
- Cohort: FRESH_CONFIRM_300 (n=300, no exclusions)
- Comparator: Δ(LLH−GFL) vs GT-only texture statistics
- Effect: Spearman ΔFG-PSNR ~ GT HF energy −0.691 [−0.745, −0.626]; quartiles:
  Q1 +4.14 dB (92% win) → Q3 −0.09 / Q4 −0.03 (LLH loses); Holm family E: all
  10 tests rejected
- Correction: Holm family E (10 tests)
- Failure cases: none; the boundary IS the finding
- Allowed: "LLH's advantage concentrates on texture-poor objects and reverses
  on texture-rich ones, predictable from GT statistics alone"
- Forbidden: reporting the +1.29 dB average without the boundary; any claim
  that the average advantage applies to texture-rich content

--------------------------------------------------------------------------------
## FINAL RULING ON THE FRAMING **[AMENDED P0-1]**

Keep "L-TCAS" as a name ONLY if immediately qualified; the supported story is
"depth-aware adapter scaling with a monotone late-increasing temporal
profile, and a real but dose-dependent layer × time interaction":
layer allocation = first-order effect; temporal profile = small real benefit
captured by a linear ramp; the Layer × Time interaction EXISTS (large
variance share at native dose; collapses after dose normalization —
authoritative Wald re-test), so "no interaction / purely additive" wording is
FORBIDDEN, but the 2D structure is also not a large practical scheduling
lever (linear-ramp equivalence stands); NO empirical stage boundaries
(heuristic only); G supports only a bounded statement for its frozen
0.75-to-1.00 range (98/99 planned objects), with broad interaction transfer
unconfirmed; texture-rich failure boundary mandatory in any deployment
statement. Manuscript rewriting remains gated on completion of the evidence
closure protocol and evidence freeze (see NARRATIVE_RESTRUCTURE_REQUIRED.md).
