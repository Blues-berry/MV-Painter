# SCIENTIFIC_VALIDATION_DECISION_REPORT — FINAL

- Date: 2026-10-05
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
- Effect: A2 cell deltas exist but are tiny (|ΔFG-LPIPS| ≤ 0.006); B2:
  late-high beats all-low by +0.84 dB [0.75, 0.93] and early-high by +0.85 dB
  [0.66, 1.05]
- Correction: Holm (A: 16 tests; B2: 4 tests) — all rejected
- Failure cases: at equal dose (A3) the window profile within a layer is flat;
  no window is special
- Allowed: "a monotone late-increasing temporal profile yields a small real
  benefit over a constant budget-matched scale"
- Forbidden: "timestep-specific gating/switching is a discovered mechanism";
  any per-window tuning claims

--------------------------------------------------------------------------------
CLAIM 3 "There is a layer × timestep interaction." → **NOT SUPPORTED**
--------------------------------------------------------------------------------
- Experiment: A2 raw + A3 dose-normalized (pre-registered primary H1)
- Comparator: two-way additive model SS-interaction, object-cluster bootstrap
- Effect: raw p = 0.50; dose-normalized p = 1.0 (observed additive residual
  SMALLER than the bootstrap null)
- Correction: Holm family A (16 tests): interaction p_holm = 1.0
- Failure cases: none — the null is affirmed by two independent maps
- Allowed: "we tested for a layer × timestep interaction and found none; the
  supported structure is additive (layer main effect + temporal profile)"
- Forbidden: ANY residual interaction narrative, any S=[s_l,k]
  full-matrix justification, "jointly conditioned" mechanism language

--------------------------------------------------------------------------------
CLAIM 4 "1/3 stage boundaries reflect the empirical response." → **HEURISTIC ONLY**
--------------------------------------------------------------------------------
- Experiment: A2/A3 response maps
- Comparator: window response profiles vs frozen boundaries at steps 16/17,
  32/33
- Effect: no discontinuity or boundary-aligned response at equal dose;
  profiles are window-flat within layers
- Correction: descriptive (A3) + Holm family A
- Allowed: "three-stage boundaries are a design heuristic"
- Forbidden: "empirically derived/validated boundaries"

--------------------------------------------------------------------------------
CLAIM 5 "LLH's gain is not explained by residual budget." → **SUPPORTED (small)**
--------------------------------------------------------------------------------
- Experiment: B1 (LFM-EXACT = exact 17/16/17 per-layer means, constant)
- Cohort: FRESH_CONFIRM_300 (n=300)
- Effect: LLH − LFM-EXACT = +0.435 dB FG-PSNR [0.356, 0.516]; −0.0045 FG-LPIPS
  [−0.0052, −0.0039]; Holm family B1 p = 0.0002
- Correction: Holm family B1 (2 tests)
- Failure cases: pre-registered equivalence NOT established (PSNR CI upper
  0.516 > 0.5 margin) — the temporal-variation component is real but small
  relative to the total LLH−GFL difference (+1.29 dB)
- Allowed: "LLH retains a small advantage over an exactly budget-matched
  constant (+0.4 dB); most of the layer allocation benefit is budget-side"
- Forbidden: "the LLH advantage cannot be explained by budget" (the dominant
  part CAN; only a +0.4 dB residual is attributable to temporal variation)

--------------------------------------------------------------------------------
CLAIM 6 "Layer-wise allocation improves over truly uniform scaling." → **SUPPORTED**
--------------------------------------------------------------------------------
- Experiment: B3 TRUE-GLOBAL diagnostics (uncapped, causal-only)
- Cohort: FRESH_CONFIRM_300 (n=300)
- Comparator: native/layer conditions vs TRUE-GLOBAL at matched nominal scales
- Effect: GFL vs TRUE-GLOBAL-1.25 +1.60 dB [1.37, 1.82]; LFM-EXACT vs
  TRUE-GLOBAL-1.675 +2.99 dB [2.43, 3.55]; GFH vs TRUE-GLOBAL-2.50 +4.66 dB
  [4.07, 5.23]; FG-LPIPS all favor layer-aware
- Correction: descriptive decomposition (pre-registered as non-confirmatory);
  CIs as given
- Failure cases: TRUE-GLOBAL runs were stable (no NaN); they are diagnostics,
  not deployment candidates
- Allowed: "protecting shallow (cap) and redistributing scale across depth
  groups jointly account for the schedule gains, additively"
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
- Cohort: 99 fresh disjoint objects (1 technical exclusion, documented)
- Comparator: g_baseline vs 15 (group, window) interventions at 0.75→1.00
- Effect: interaction p = 0.58; cell deltas ~1e-4 (deep/middle ≈ 0; only 3
  shallow cells Holm-rejected at ~5e-4)
- Correction: Holm family G (16 tests)
- Failure cases: the intervention range [0.75, 1.0] may simply be too weak on
  this backbone — the report must state this scope limit (no dose escalation
  was run by design; dose ratio <2x pre-registered rule)
- Allowed: "the main-backbone layer/time structure does not transfer to
  MV-Adapter under the frozen protocol; the principle is backbone-specific"
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
## FINAL RULING ON THE FRAMING

Keep "L-TCAS" as a name ONLY if immediately qualified; the supported story is
"depth-aware adapter scaling with a monotone late-increasing profile":
layer allocation = first-order effect; temporal profile = small real benefit
captured by a linear ramp; NO interaction; NO empirical stage boundaries;
backbone-specific; texture-rich failure boundary mandatory in any deployment
statement. Manuscript rewriting may now begin ONLY within these constraints
(see NARRATIVE_RESTRUCTURE_REQUIRED.md).
