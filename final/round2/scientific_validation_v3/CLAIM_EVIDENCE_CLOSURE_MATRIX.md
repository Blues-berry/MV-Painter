# CLAIM_EVIDENCE_CLOSURE_MATRIX — Scientific Validation V3

Created: 2026-10-05. Refreshed by independent evidence-closure passes on
2026-10-05 and 2026-10-06. Protocol: `# Scientific Validation V3` §1 (the claim graph
precedes all newly designed experiments; manuscript editing remains forbidden
until the evidence closure gate).

Inputs read in full: `PRE_ACCEPTANCE_AUDIT_20261005.md` (+ its five section
audits, `A3_DOSE_VALIDITY_AUDIT.md`, `STATISTICAL_REPRO_AUDIT.md`),
`MASTER_PROTOCOL_LOCK.md`, `COHORT_FREEZE.md`, `CLAIM_TEST_MATRIX.md`,
`PRIMARY_HYPOTHESES.md`, `RUN_BUDGET.md`, all A/B/C/D/E/F/G campaign reports,
`SCIENTIFIC_VALIDATION_DECISION_REPORT.md`, `NARRATIVE_RESTRUCTURE_REQUIRED.md`,
the historical forensic set (`coordination/forensic_audit_agentB_20261001/*`,
`final_audit_20261001/FINAL_REVIEWER_READINESS_REPORT.md`),
`final_round2.tex`, `supplementary_round2.tex`, `response_letter_round2.md`,
round-1 reviewer comments.

Status vocabulary (per protocol): STRONG / PARTIAL / WEAK / UNSUPPORTED /
CONTRADICTED. A claim may not disappear from this matrix because the final
paper uses weaker wording.

P0-1 note: the production Layer×Window interaction test was zero-power
(`STATISTICAL_REPRO_AUDIT.md` §2). All interaction statuses below use the
validated cluster-robust Wald test
(`audit_scripts/AUDIT_INTERACTION_VALID_TEST.json`,
`audit_scripts/AUDIT_INTERACTION_VALID_TEST_G.json`). Where this changes a
verdict, the claim is marked [RE-DERIVED].

Master summary (detail per claim below):

| ID | Claim (short) | Status | Blocking closure action |
|----|---------------|--------|-------------------------|
| C1 | Adapter scale affects shape–texture / reference-fidelity trade-off | STRONG (with shallow stress caveat) | wording only |
| C2 | Depth-wise redistribution is beneficial | PARTIAL (primary-backbone response; cap/dose contrasts limit pure depth attribution) | scope to measured intervention and backbone |
| C3 | Temporal variation helps beyond requested mean budget | PARTIAL (B effect statistically detectable but inside frozen practical margins; actual dose differs) | describe as small and nominal-dose matched |
| C4 | Early-vs-late placement matters | PARTIAL (registered LLH−HLL mean effect; PSNR object heterogeneity) | no universal placement rule |
| C5 | "Early-high hurts / late-high helps" | PARTIAL; full directional signature fails because HLL−LLL is exploratory and PSNR CI crosses zero | retire broad directional wording |
| C6 | Genuine Layer×Time interaction exists | PARTIAL [A2 native-dose discovery; A3b heterogeneity with no dose common support] | no dose-independent interaction claim |
| C7 | S=[s_l,k] empirically justified as a necessary 2D control law | WEAK / not established as necessary for practical gains | present dimensions separately; no interaction mechanism claim |
| C8 | 1/3 stage partition is meaningful | WEAK (the completed B contrasts do not identify a phase boundary) | describe thirds as a convenient discretization; do not tune boundaries on the observed cohort |
| C9 | LLH gain not merely residual-budget/cap artifact | PARTIAL (requested means controlled in selected contrasts; actual residual norms differ) | do not call equal post-scale dose |
| C10 | L-TCAS outperforms generic schedules under one protocol | PARTIAL / no unique winner (`gen_linear` has no detected primary-endpoint difference; B extension is post-lock) | retain generic controls; characterize allocation rather than claim a winning schedule |
| C11 | Metric improvement = faithful texture reproduction | OPEN (no human responses; four locked pairs, including endpoint-matched `gen_linear`; 40 fixed slots, minimum 36 valid) | run the frozen study and report all eight endpoints, or explicitly de-scope human-validated fidelity |
| C12 | Final 3D baking / unseen-view output improves | PARTIAL (stored N=20 GLBs now evaluated with native base-color sampler; endpoint results are mixed; no-UV coverage and perceptual fidelity remain open) | scope to N=20/eight stored conditions; report endpoint-specific results; no unique 3D winner |
| C13 | Failure behavior systematic and explainable | STRONG (quantitative boundary plus bounded visual classes) | retain scope and applicability limits |
| C14 | Principle transfers beyond primary backbone | Broad transfer unsupported; G gives a bounded result for 98/99 planned inputs | retain scale/cohort scope; no universal no-interaction statement |
| C15 | CAI has predictive value beyond post-hoc | UNSUPPORTED as predictive; DESCRIPTIVE_ONLY | remove from novelty claims during rewrite |
| C16 | Computational / reproducibility claims traceable | PARTIAL (core statistics, one full clean-clone A2 condition, and full artifact archives verified; paper-wide post-rewrite regeneration remains open) | rebuild final paper tables and figures after narrative approval |

**Current hard-rule overlay (2026-10-06):** The table above is the current
claim status. It supersedes stronger wording in the historical per-claim
notes below wherever they conflict, especially for C3–C7 and C10–C12. The
current provisional class is `NARRATIVE_D`: characterize adapter scaling and
residual allocation, with depth allocation primary and tested timing
contrasts secondary. The registered generic linear schedule has no detected
FG-PSNR difference from LLH, but no formal equivalence margin was registered.
This narrative re-evaluation is retrospective because B was exposed before
the safeguard locks. See `NARRATIVE_SWITCH_REASSESSMENT_20261005.md`,
`FINAL_NARRATIVE_DECISION.md`, and
`FINAL_SCIENTIFIC_READINESS_20261006.md`.

---

## C1 — Adapter scale affects the shape–texture / reference-fidelity trade-off

- Manuscript wording: "adapter scaling as a layer-by-stage residual allocation
  problem rather than a single global magnitude" (Abstract, final_round2.tex
  L34); contribution (1) "identify and quantify the shape–texture and
  reference-fidelity trade-off" (L65).
- Reviewer concern addressed: R1.3 (texture variation vs texture fidelity).
- Supporting experiments: Core-7 confirmation (strict-276, L319–323); A2/A3
  maps (metric-direction heterogeneity across cells); B3 decomposition;
  GT-relative texture probes (§4.5).
- Cohort: strict-276 ( manuscript) / FRESH_CONFIRM_300 (V3). Fresh at
  experiment-design time: FRESH_CONFIRM_300 yes (frozen 2026-10-02 before
  outcomes); strict-276 is STRICT276_REEVALUATION only (correctly labeled).
- Comparator: no_adapter / global / layer-fixed / LLH family; budget/cap/runner/
  seed matched within each V3 panel; manuscript panels pre-Core-7 had
  cross-runner scale-semantics confound (QUARANTINED for cross-panel absolute
  use — CROSS_RUNNER_SCALE_SEMANTICS_AUDIT).
- Statistical support: paired bootstrap CIs, Holm families; effect magnitudes
  reproduced exactly by audit.
- Qualitative support: GT-relative probes; visual panels (24-object archive).
- 3D-output support: stored F outputs were rerendered through their embedded
  GLB sampler for the supported N=20/eight-condition cohort. Adapter-vs-none
  and schedule contrasts remain endpoint-specific and do not establish a
  unique winner; see `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`.
- Cross-backbone support: MV-Adapter metric-dependent directions; MVDiffusion
  negative boundary.
- Alternative explanations: residual budget / cap (decomposed by B3 — held
  fixed in interpretation).
- **Status: STRONG** (trade-off exists and is quantified; the shallow
  high-dose leg is STRESS_TEST_ONLY per `A3_DOSE_VALIDITY_AUDIT.md` — any
  "shallow uniformly harmful" generalization is a stress-regime statement).
- Required closure action: none beyond wording discipline.

## C2 — Depth-wise redistribution is beneficial

- Manuscript wording: "the layer-wise redistribution itself—not only the
  temporal pattern—carries the gain" (+3.083 dB FG-PSNR, §4.4 L377–379).
- Reviewer concern: R2.1 (contribution beyond schedule search).
- Supporting experiments: B3 LFM-EXACT vs TRUE-GLOBAL-1.675 +2.99 dB
  [2.43, 3.55] (deep/middle requested scales match; shallow exposure differs);
  GFL vs TGU-1.25 +1.60 dB [1.37, 1.82] (same requested scales, cap differs);
  GFH vs TGU-2.50 +4.66 dB [4.07, 5.23]; A3 layer marginals deep +0.55 /
  middle +0.29 / shallow −6.07 dB (deep valid-local-dose, middle approximate,
  shallow stress-only).
- Cohort: FRESH_CONFIRM_300, fresh at original preregistration. The named
  B3 contrasts are paired within cohort; global scale values are not matched
  in total residual dose, and uncapped diagnostics are not deployment rows.
- Statistical support: paired CIs for named contrasts; no additive
  decomposition is supported. TGU-0.80 is absent from B3 and remains required.
- Cross-backbone: MV-Adapter layer redistribution near-zero (see C14) —
  claim must stay backbone-scoped.
- Alternative explanation: cap and realized dose are part of the named B3
  contrasts; only LLH−LFM-EXACT isolates temporal variation at matched
  per-layer requested means.
- **Status: STRONG on the primary backbone; UNSUPPORTED as a general
  cross-backbone principle.**
- Required closure action: none (wording must retain backbone scope).

## C3 — Temporal variation is beneficial beyond average residual budget

- Manuscript wording: §3.3 fixed-mean control design; §4.3 LLH > layer-fixed-
  mean on all seven metrics (L323).
- Supporting experiment: B1 (H2) LLH − LFM-EXACT = +0.435 dB FG-PSNR
  [0.356, 0.516], −0.0045 FG-LPIPS [−0.0052, −0.0039], Holm p = 0.0002.
- Cohort: FRESH_CONFIRM_300, fresh; exactly mean-matched per layer
  (17/16/17); same runner/cap/seed.
- Equivalence margin: pre-registered margins NOT met → advantage stands as a
  temporal effect (honest).
- Alternative explanation: budget — excluded by exact matching; ~1.5%
  17/16/17 asymmetry leak ≈ +0.11 dB quantified in
  LLH_EFFECTIVE_CONTROL_AUDIT (smaller than the effect).
- **Status: STRONG (small but real; ~+0.4 dB of the +1.29 dB LLH−GFL total).**
- Required closure action: none.

## C4 — Early-vs-late placement matters

- Supporting experiment: B2 (H3) LLH > HLL +0.854 dB [0.658, 1.052]; LLH >
  LLL +0.840 dB [0.747, 0.934]; Holm family B2 all p = 0.0004; descriptive
  LLH > LHL +0.647.
- Cohort: FRESH_CONFIRM_300, fresh; equal nominal high duration (17 steps);
  same runner.
- **Status: STRONG.**
- Required closure action: none.

## C5 — "Early-high hurts / late-high helps"

- Manuscript wording: Abstract L34; contribution (3) robust directions with
  layer-LLH/LHH/LLL as counterexamples to layer-LHL optimum (L69); §4.4.1
  sign structure (L450–472).
- Supporting experiments: B2 confirms the LLH-vs-HLL (late vs early) contrast
  confirmatorily; the full 8-pattern enumeration behind the manuscript's
  direction claims was development/probe evidence (FINAL_FORENSIC_AUDIT §16:
  "8-pattern factorial only development-only probe evidence").
- Alternative explanation: budget — equal-duration design controls it.
- **Status: PARTIAL** (direction replicated confirmatorily for the clean
  LLH/HLL/LLL contrasts; the broader enumeration-derived wording retains
  development-only provenance and must stay labeled as such).
- Required closure action: manuscript wording (revision window).

## C6 — A genuine Layer × Time interaction exists [RE-DERIVED]

- Manuscript wording (current): interaction framed as supported structure
  (§3.2 two-axis control; §4.4 pattern structure).
- V3 pre-registered H1 (A3): interaction on FG-LPIPS after dose
  normalization.
- Production test defect: zero power (P0-1) — old "p = 0.50/1.0, NOT
  SUPPORTED" wording is uninformative.
- Valid cluster-robust Wald test (8 interaction contrasts, object sandwich):
  A2 FG-LPIPS W = 481.1, p = 8.0e-99, interaction SS share 43.5%; A2 FG-PSNR
  W = 1880.0, p ≈ 0, share 56.8%; A3 FG-LPIPS W = 657.2, p = 1.1e-136, share
  11.9%; A3 FG-PSNR W = 1389.1, p = 1.3e-294, share 0.8%. Cross-checks: naive
  ANOVA F = 117.8 (p = 1.9e-179); subsample-stable; winsorization-stable.
  Cell structure directly visible: deep deltas (×1e-4) = [−29.3, +5.9,
  +41.3, +35.2, +23.8] across W1–W5 (early→late sign flip).
- Dose-normalization caveat (A3_DOSE_VALIDITY_AUDIT): deep = valid
  confirmation; middle = approximate (E-ratio 5.1× vs requested 2.73×);
  shallow = STRESS_TEST_ONLY. The A3-based "survives dose normalization"
  statement is fully valid only for the deep row.
- Independent corroboration: B3 temporal component +0.43 dB vs uniform.
- **Status: PARTIAL — the interaction is REAL (strong evidence at native
  dose); at matched dose it remains statistically detectable but its
  variance share collapses (FG-PSNR 56.8%→0.8%; FG-LPIPS 43.5%→11.9%), and
  dose normalization is only approximate for middle/shallow.** Practical
  scheduling value of the 2D structure remains bounded (endpoint-matched
  linear ramp is a credible competitor; H4 did not freeze an equivalence
  margin, C10).
- Required closure action: P0-1 fix (done — interpretation documents revised
  2026-10-05; see `PRE_ACCEPTANCE_ISSUE_CLOSURE.md`).

## C7 — S=[s_l,k] is empirically justified as a 2D control space [RE-DERIVED]

- Manuscript wording: contribution (2) training-free layer × timestep control
  S=[s_l,k] (L67); §3.2.
- Evidence after valid test: 2D structure carries real variance at native
  dose (C6); at equal dose the layer main effect dominates and the
  time-structure share is small (FG-PSNR) to modest (FG-LPIPS 11.9%);
  layer×constant (LFM-EXACT) + linear ramp captures the practical benefit.
- **Status: PARTIAL — S is scientifically meaningful (interaction real), but
  not empirically NECESSARY for deployment-level gains; the justified
  representation for claims is layer allocation + monotone late-increasing
  profile, with the 2D interaction reported as present with dose-dependent
  magnitude.**
- Required closure action: P0-1 fix (done).

## C8 — The 1/3,1/3,1/3 stage partition is meaningful

- Manuscript wording: Eq.(3) p=1/3, 2/3 boundaries (L129–134) with stage
  hypotheses.
- Reviewer concern: R2 explicitly questioned fixed one-third boundaries.
- Evidence: A2 valid map shows smooth positional response (deep sign flip
  between W1 and W3) — no discontinuity at steps 16/17 or 32/33; A3
  dose-normalized window-flatness is valid for deep only (middle
  approximate, shallow invalid).
- **Status: WEAK — heuristic discretization.**
- Required closure action: V3 §8 boundary-sensitivity test on an untouched
  cohort (PENDING — needs FRESH_CONFIRM_B or another untouched cohort);
  manuscript must describe thirds as a convenient discretization.

## C9 — LLH improvement is not merely a residual-budget/cap artifact

- Evidence: LLH−GFL = +1.288 dB. The clean LLH−LFM-EXACT temporal contrast is
  +0.435 dB; the same-endpoint residual LFM-EXACT−GFL is +0.853 dB and
  changes depth scales, realized dose, and shallow-cap state together.
  Separate GFL−TGU-1.25 (+1.60) and LFM-EXACT−TGU-1.675 (+2.99) contrasts use
  different endpoints and cannot be added to explain LLH−GFL.
- Historical closure: RESIDUAL_BUDGET_CONFOUND_AUDIT binding rule (never
  present historical or V3 headline deltas as pure temporal scheduling
  effects) — incorporated.
- **Status: PARTIAL** (claim survives in its narrow form; the broad
  implication "schedule > budget" is refuted).
- Required closure action: none beyond wording.

## C10 — L-TCAS outperforms generic schedules under one authoritative protocol

- Evidence: Experiment C — LLH beats cosine/trapezoid/Gaussian and all
  budget-matched variants (FG-PSNR +0.30..+0.59 dB, Holm-rejected);
  endpoint-matched linear warm-up is not detectably different on FG-PSNR
  (+0.005 dB, Holm p = 0.81). H4 froze no equivalence margin, so equivalence
  is not established.
- Reviewer concern: R3 (generic schedules on independent set) — closed by
  design (same cohort/runner/seed/cap).
- **Status: PARTIAL (metric-dependent; the endpoint-matched linear ramp is a
  credible competitor, but its effect is not formally equivalent under a
  registered margin).**
- Required closure action: incorporate the FRESH_CONFIRM_B post-lock
  sensitivity and retain its non-independent scope.

## C11 — Metric improvement corresponds to faithful texture reproduction

- Evidence: D 24-object formal visual archive (GT-only frozen selection,
  reproduction byte-identical) exists; E ties metric deltas to GT texture
  complexity (advantage concentrated on texture-poor objects, reversal on
  texture-rich). These support a bounded image-space characterization, not
  a human-fidelity claim. F's stored FG-LPIPS and seam values are historical
  diagnostics because the bake/render address and filtering semantics do not
  match the exported GLBs.
- Visual evidence: all 24 frozen formal panels were classified for visible
  color/material mismatch, fine-detail loss, thin/small-part readability, and
  cross-view concern. These 2D panels do not establish unseen-view geometry,
  UV coverage, or 3D seam causes; see `FORMAL_VISUAL_EVIDENCE_REPORT.md`.
- Human evidence: the balanced 40-slot / 24-items-per-participant, four-pair
  package is frozen before responses, including the registered endpoint-
  matched `gen_linear` competitor. It has separate Q1/Q2 and eight planned
  endpoints. Collection has not started, so the metric/perceptual gap remains
  open. The final pair lock is post-B and supersedes the earlier three-pair
  amendment.
- **Status: OPEN for human-validated fidelity; image-space evidence remains
  PARTIAL.**
- Required closure action: execute `HUMAN_STUDY_FINAL_PAIR_LOCK.md` at its
  fixed 40-slot stop, requiring at least 36 valid completions, or formally
  de-scope human-validated fidelity. Report all eight endpoints separately.
  No old preference values are reused.

## C12 — Final 3D baking / unseen-view output improves

- Evidence: F's stored N=20 rows, metadata, and GLBs remain traceable. The old
  CPU unseen metrics and seam rows remain historical because their sampler
  behavior differed from the exported files. On 2026-10-06 all 160 GLBs were
  rendered at 11 frozen unseen views with the embedded repeat/mipmap sampler;
  image and source hashes passed, and mask IoU against the old geometric
  renderer was at least 0.999768. `layer_llh − native_gfl` has FG-PSNR
  −0.422 dB [−1.361, +0.652], FG-LPIPS −0.01175 [−0.01988, −0.00564], and
  CIEDE2000 +2.563 [−1.007, +5.893]. The corrected base-color evaluation
  therefore supports an endpoint tradeoff, not an overall winner.
- Cohort: 20 of the frozen 24 objects. Four source objects lacked UV layers
  before bake generation. `01e3…` remains in the primary set; the fixed N=19
  sensitivity excluding this preidentified extreme-UV UID is also reported.
- **Status: PARTIAL (stored N=20 GLB base-color results are renderer-valid;
  strict N=24, full PBR, and human-perceived fidelity are not established).**
- Required closure action: preserve N=20 scope and endpoint limits in any
  manuscript claim. A claim of all-24 3D coverage would need a separately
  justified treatment of the four no-UV sources; human fidelity remains under
  C11.

## C13 — Failure behavior is systematic and explainable

- Evidence: E prospective replication on FRESH_CONFIRM_300 (Spearman
  ΔFG-PSNR ~ GT HF energy −0.691 [−0.745, −0.626]; quartile flip Q1 +4.14 dB
  92% win → Q3/Q4 negative); historical strict-276 34-loss taxonomy
  (realization-persistent, schedule-family-wide) — replicated.
- Visual taxonomy on the frozen 24-object archive is descriptive and limited
  to visible properties; it does not replace the quantitative boundary or
  identify 3D failure causes.
- **Status: STRONG (quantitative applicability boundary plus bounded visual
  description).**
- Required closure action: preserve scope and correct lower-is-better win
  semantics.

## C14 — The principle transfers beyond the primary backbone

- Evidence: the frozen completion adds 17 runnable objects to the 81-object
  deduplicated base, for n=98/99 and 1,568 object-condition rows. The final
  planned input is a hash-verified line-only GLB (`Path3D`, no triangles) and
  is recorded as a technical exclusion; it was not substituted. Deep and
  middle mean FG-LPIPS changes are +5.4e-5 and −4.5e-6; shallow is +3.99e-4.
  Shallow W3–W5 are small adverse cells that survive the frozen 15-cell Holm
  correction. The exploratory Wald re-test gives FG-LPIPS p=0.101, PSNR
  p=0.434, FG-SSIM p=0.039 (four-metric Holm p=0.156), and CIEDE2000
  p=0.862. MVDiffusion remains an interface-boundary negative
  (α≡1 tensor identity 36/36).
- Cohort closure: **P1-5 closed with scope limit**, with the sole technical
  exclusion identified, hashed, and outcome-independent; see
  `g_formal_complete/MERGE_AUDIT.json` and
  `g_formal_complete/TECHNICAL_EXCLUSION_G_0098.json`.
- **Status: broad transfer UNSUPPORTED; bounded G result PARTIAL.** Do not
  claim universal MV-Adapter insensitivity or a confirmatory interaction
  absence. The Wald reanalysis is exploratory because the test was selected
  after discovery of the production bootstrap defect.
- Required closure action: wording only; preserve the 98/99 cohort scope and
  the observed small late-shallow effect.

## C15 — CAI has predictive value beyond post-hoc interpretation

- Manuscript state: CAI already demoted in-text to empirical diagnostic
  (§3.5 L205–210; response letter R2.2 admits post-hoc; "CAI appears in no
  contribution statement").
- Prospective prediction test: never performed; factorial evidence shows no
  unique selector value (LLH/LHH/LLL counterexamples; MV-Adapter rule
  undefined_set_valued).
- **Status: UNSUPPORTED as predictive → DESCRIPTIVE_ONLY.**
- Required closure action: at rewrite, remove CAI from novelty/contribution
  claims; it may remain as brief descriptive terminology.

## C16 — Computational / reproducibility claims fully traceable

- Evidence: bit-identical reproductions (A2 baseline ≡ A3 baseline; B3
  resume 1050/1050; 9/9 live end-to-end), per-row input hashes 16,950 rows,
  SHA256SUMS (304 entries), manuscript files untouched (SHA-verified).
- Open items: P1-2 branch not pushed (remote 502); P2-2 SHA index for
  prediction PNGs; P2-3 50 MB contact sheet in git; P2-4 G ledgers lack
  input_hashes (source_uid only).
- **Status: PARTIAL (operational gaps only; scientific reproducibility
  proven).**
- Required closure action: push when network allows; SHA index before
  archival.

---

## Cross-cutting legacy items carried into the closure ledger

1. Cross-runner scale semantics (capped vs uncapped wrappers, 7.7 dB
   cross-panel offsets): cross-panel absolute comparisons QUARANTINED;
   panel-internal paired conclusions VALIDATED; manuscript actions
   (tab:strict276 replacement, non-dominance rewrite, disclosure upgrade)
   are revision-window P0s from FINAL_FORENSIC_AUDIT §14 — BLOCKED until
   the evidence closure gate, tracked in the matrix.
2. Archived layer-LHL value (14.776) quoted in tex L470–481: QUARANTINED
   evidence — must be removed/replaced in the revision window.
3. Figure-selection provenance: obj_0066 (actual rank 2/276 vs "not best"
   caption) and obj_0048/0078 captions — revision-window P1.
4. "LLH closest to GT gradient energy" wording error (GFH is closer) —
   erratum item.
5. Duplicate source-asset pair in FRESH_CONFIRM_300 (0099ab6d44… /
   0130e5149b…; 299 unique contents / 300 UIDs) — P1-1, documented; optional
   leave-one-out sensitivity.
6. G cohort coverage — P1-5 closed with one documented path-only technical
   exclusion (see C14); cohort scope remains 98/99 planned.
7. V3 §3 FRESH_CONFIRM_B cohort freeze, §6 A3b lock, and §8 boundary family
   were frozen before their outcomes. The formal B campaign is complete and
   historically unblinded; its original integrity gate passed before
   aggregate analysis, while the added pre-unblind safeguards are
   retrospective. §12 formal visual classification and §15 CAI decision are
   complete. The four-pair human protocol/site are frozen; response
   collection remains pending.

---

## Independent refresh: protocol-required source and evidence fields

The fields below make the C1–C16 graph auditable against the *current*
manuscript and response letter. Exact excerpts are verbatim. “Fresh” refers to
whether the cohort was unseen when that experiment's design was frozen; a
later reanalysis on FRESH_CONFIRM_300 is explicitly exploratory and does not
inherit the original preregistration. For V3 campaigns A2/A3/B/C/E/F, the
cohort was frozen at 2026-10-02 15:50 before the first A2 formal row, and
within-campaign object inputs, latent seed, checkpoint, runner, and metrics
were shared as recorded by the manifests. That common fact does not make
post-hoc analysis choices preregistered.

### C1 — Scale changes the shape / texture / reference-fidelity balance

- Exact current wording/source: “We identify and quantify the shape--texture
  and reference-fidelity trade-off caused by adapter scaling” (contribution 1,
  `final_round2.tex` L65; Abstract L34; response R1.3).
- Reviewer concern: R1.3, variation is not fidelity; R1.4, metric trade-offs
  and intervals.
- Evidence/cohort/freshness: strict-276 Core-7 (frozen before its holdout
  outputs), FRESH_CONFIRM_300 A2/A3/B3/E, and the stored F N=20 historical
  outputs after frozen UV exclusions; the V3 cohort was fresh at its original
  design freeze.
- Comparators and controls: adapter/no-adapter, global/layer schedules, and
  GT-relative texture measures; pairing, seeds, and runner match within each
  panel. Exact total residual budget and cap state differ unless a named
  contrast controls them; old cross-runner panels remain quarantined.
- Support: paired CIs/Holm where confirmatory; GT-relative visual evidence is
  classified, but human-perceived fidelity remains unmeasured. The old F CPU
  metrics are not eligible as faithful-GLB evidence; the new N=20 base-color
  render is sampler-conformant but has mixed endpoints and no unique schedule
  winner. Cross-backbone directions are metric-dependent, not pooled.
- Alternative: cap, integrated residual dose, and increased texture variation
  can mimic a fidelity gain. B3 decomposes named contrasts; it does not license
  a single universal “quality” score.
- Confidence/action: STRONG for existence of a measured trade-off; finish
  formal visual classification and retain separate evidence dimensions.

### C2 — Depth-wise redistribution is beneficial

- Exact current wording/source: “Moving from a global scale to depth-group
  scales improves foreground fidelity over global fixed-low” (Conclusion
  L747–750); response R2.1 L190–201.
- Reviewer concern: R2.1, contribution beyond schedule selection.
- Evidence/cohort/freshness: V3 A3 and B3 on the originally frozen
  FRESH_CONFIRM_300; strict-276 Core-7 provides a distinct same-runner
  confirmation surface.
- Comparators/controls: LFM-EXACT versus TRUE-GLOBAL-1.675 controls the deep
  and middle requested scale but lowers shallow scale; it is not a fixed-total
  dose comparison. GFL versus TRUE-GLOBAL-1.25 isolates the native shallow cap
  at the same requested global scale. Same objects/seeds/runner within B3;
  cap differs in the named true-global contrasts.
- Support: B3 paired FG-PSNR +2.99 dB [2.43, 3.55] for LFM-EXACT versus
  TRUE-GLOBAL-1.675 and +1.60 dB [1.37, 1.82] for GFL versus TGU-1.25.
  Visual and 3D evidence supports only bounded aspects. MV-Adapter is
  metric-dependent and does not justify a general transfer claim.
- Alternative: residual budget and shallow-cap protection are part of these
  effects; no contrast here alone isolates an abstract “layer allocation”
  independent of realized dose.
- Confidence/action: STRONG within the tested primary backbone and schedule
  range; correct causal wording to name the actual matched contrast.

### C3 — Temporal variation helps beyond average residual budget

- Exact current wording/source: method/results distinguish “layer-fixed-mean”
  from scheduled controls (`final_round2.tex` L163–168, L337 onward); response
  R2.1 L198–204.
- Reviewer concern: R2.1, whether this is only schedule search or dose change.
- Evidence/cohort/freshness: preregistered B1 on FRESH_CONFIRM_300, frozen
  before that cohort's outputs; same object, runner, checkpoint, latent, and
  native caps for LLH and LFM-EXACT.
- Comparator/control: exact per-layer temporal means (deep/middle 1.675,
  shallow 0.585); cap profile does not bind either condition. This is the
  clean mean-matched temporal contrast.
- Support: LLH−LFM-EXACT FG-PSNR +0.435 dB [0.356, 0.516], FG-LPIPS
  −0.0045 [−0.0052, −0.0039], Holm-adjusted p=0.0002; V3 paired input/seed
  match. Visual/3D support is bounded; cross-backbone temporal effect is not
  consistently separated.
- Alternative: 17/16/17 step-count asymmetry is quantified in the historical
  effective-control audit but is smaller than the observed contrast.
- Confidence/action: STRONG for a small residual temporal effect on this
  backbone; report it separately from LLH−GFL.

### C4 — Early-versus-late placement matters

- Exact current wording/source: “late-stage high scale helps while early-stage
  high scale hurts” (Abstract L34; contribution 3 L69; Results L450–472).
- Reviewer concern: R2.1; R1.4 on paired effects and non-equivalence.
- Evidence/cohort/freshness: development factorial is probe-only; confirmatory
  B2 contrasts were frozen before and run on FRESH_CONFIRM_300.
- Comparator/control: LLH, HLL, and LLL have the same one-high-segment duration
  for LLH vs HLL; paired object, input, seed, runner, and cap. The full
  eight-pattern enumeration itself is development evidence, not holdout
  confirmation.
- Support: B2 LLH−HLL +0.854 dB [0.658, 1.052] and LLH−LLL +0.840 dB
  [0.747, 0.934], Holm-adjusted p=0.0004. Qualitative/3D support remains
  bounded; no cross-backbone temporal transfer established.
- Alternative: the contrast supports this placement comparison, not a unique
  optimum or universal schedule.
- Confidence/action: STRONG for the named B2 comparisons; narrow wording to
  those comparisons and label the full pattern enumeration development-only.

### C5 — “Early-high hurts / late-high helps”

- Exact current wording/source: verbatim phrase appears in Abstract L34 and
  contribution 3 L69; response R2.1 L202–204.
- Reviewer concern: R2.1, evidence beyond pattern search.
- Evidence/cohort/freshness: probe-24 factorial is development-only; B2 on
  FRESH_CONFIRM_300 confirms LLH/HLL/LLL contrasts but not all eight patterns.
- Comparator/control: named equal-duration B2 contrasts are object/input/seed/
  runner/cap matched; no equal-dose claim for arbitrary eight-pattern pairs.
- Support: paired B2 CIs/Holm as in C4. No formal visual classification yet;
  no independent cross-backbone confirmation of this rule.
- Alternative: full enumeration may overstate the evidence if its development
  status is omitted.
- Confidence/action: PARTIAL; explicitly separate development enumeration
  from confirmatory B2 contrasts.

### C6 — A genuine Layer × Time interaction exists

- Exact current wording/source: “We formulate a training-free layer ×
  timestep adapter residual allocation control S=[s_{l,k}]” (contribution 2
  L67; method L136–146); Abstract L34 describes depth and denoising-stage
  allocation.
- Reviewer concern: R2.1 (factorial contribution); R2.3 (architecture
  dependence).
- Evidence/cohort/freshness: A2 and A3 on FRESH_CONFIRM_300 under their frozen
  plans; the defective original bootstrap was discovered post hoc, and the
  Wald reanalysis is therefore labeled discovery reanalysis, not independent
  confirmation. The frozen A3b map on FRESH_CONFIRM_B is complete but
  `PARTIAL`: actual-dose common support is empty across all three layers.
- Comparator/control: object-level layer-by-window maps; same object/input/
  seed/runner within each map. A2 uses native doses; A3 dose normalization is
  valid for deep, approximate for middle, stress-only for shallow.
- Support: validated cluster-robust Wald reanalysis finds A2 interaction
  shares 43.5% FG-LPIPS / 56.8% FG-PSNR and A3 11.9% / 0.8%; the original
  bootstrap was zero-power. A3b confirms heterogeneity only for its frozen
  bounded intervention, without dose common support. No visual or valid 3D
  evidence isolates the interaction. G's completed n=98/99 exploratory Wald
  analysis does not survive metric-family correction and cannot establish
  interaction absence.
- Alternative: native-dose response, nonlinearity, and invalid extreme
  normalization could explain some apparent layer-time structure.
- Confidence/action: PARTIAL; keep the real native-dose result, complete
  A3b, and avoid implying the 2D interaction is necessary for deployment gain.

### C7 — S=[s_l,k] is empirically justified as a 2D control space

- Exact current wording/source: “the layer-wise generalization of this
  control” and “two control axes explicit” (method L136–146); contribution 2
  L67.
- Reviewer concern: R2.1 novelty and whether the matrix is experimentally
  necessary.
- Evidence/cohort/freshness: A2/A3 reanalysis on FRESH_CONFIRM_300 is
  exploratory for the repaired interaction test; B1/B2 were preplanned;
  fresh A3b is pending on B.
- Comparator/control: layer-fixed versus layer-varying and constant versus
  time-varying schedules; controls share object/runner/seed, but many change
  requested/effective dose unless specifically mean matched.
- Support: interaction evidence in C6 plus B1/B2 establish distinguishable
  axes; no independent 3D metric or cross-backbone confirmation of necessity.
- Alternative: layer allocation plus a simple late-increasing ramp may capture
  practical gains without a fully free matrix.
- Confidence/action: PARTIAL; make “unifying description/control space” the
  claim unless A3b shows fresh, bounded-dose interaction and added practical
  value.

### C8 — The one-third stage partition is meaningful

- Exact current wording/source: “TCAS divides denoising into early, middle,
  and late stages” with boundaries 1/3 and 2/3 (method L129–134).
- Reviewer concern: R2 explicitly questions fixed one-third boundaries.
- Evidence/cohort/freshness: A2/A3 maps on FRESH_CONFIRM_300; boundary
  sensitivity is not yet tested on unseen data.
- Comparator/control: current 10-step windows are descriptive within thirds;
  no matched-total-duration boundary family exists yet.
- Support: response profiles are smooth and no discontinuity is established;
  no qualitative or 3D result validates exact boundaries; no cross-backbone
  validation of these thirds.
- Alternative: thirds are a convenient discretization, not empirical phase
  transitions.
- Confidence/action: WEAK; preregister the small boundary family on
  FRESH_CONFIRM_B and report null preference if none is stable.

### C9 — LLH gain is not merely a residual-budget/cap artifact

- Exact current wording/source: current paper attributes gains to depth
  allocation and temporal placement (method L163–168; conclusion L747–771);
  response R2.1 L198–204.
- Reviewer concern: R2.1; historical residual-budget and cap audits.
- Evidence/cohort/freshness: B1/B3 on the originally frozen FRESH_CONFIRM_300;
  B1 LLH/LFM means and runner/caps are matched as stated.
- Comparator/control: LLH−LFM-EXACT is the clean temporal-variation
  comparison. GFL−TGU-1.25 isolates the cap at fixed requested global scale.
  LFM−TGU-1.675 changes shallow scale/dose while deep and middle requested
  scales match; it is not equal-total-dose redistribution. All are paired on
  the same 300 objects, but the cross-contrast components have different
  baselines and may not be summed into LLH−GFL.
- Support: LLH−LFM-EXACT +0.435 dB; LLH−GFL +1.288 dB. The existing B3
  report's “cap + layer + temporal” additive explanation is under audit
  because its cited pairwise contrasts do not share a common decomposition
  baseline. No visual/3D or cross-backbone result isolates the total effect.
- Alternative: the headline LLH−GFL includes changes in depth doses and
  shallow cap/effective scale; the temporal share is small.
- Confidence/action: PARTIAL; correct B3 causal language with a same-endpoint
  contrast table before evidence freeze.

### C10 — L-TCAS outperforms generic schedules under one protocol

- Exact current wording/source: Abstract L34 says the selected allocation
  “improves the primary reference-fidelity metrics”; Results C comparison and
  conclusion L753–758 state the holdout ranking; response R3 covers generic
  schedules/statistics.
- Reviewer concern: R3 (same-protocol generic comparisons); R2.1 novelty.
- Evidence/cohort/freshness: Core-7 strict-276 was frozen before holdout
  outputs; V3 C was frozen on FRESH_CONFIRM_300 before outcomes.
- Comparator/control: C uses same cohort, runner, checkpoint, seed, views,
  metric implementation, and cap; endpoint-matched and budget-matched
  families. Strict-276 Core-7 is a separate older protocol; absolute scores
  are not pooled across it and V3.
- Support: V3 C rejects 15/16 comparisons after Holm, except endpoint-matched
  linear warm-up (not detectably different on FG-PSNR; no equivalence margin
  was registered); metrics are mixed. Visual/3D ranking is bounded; no
  cross-backbone generic comparison.
- Alternative: effective dose, cap semantics, and the linear-ramp result
  limit a universal superiority claim.
- Confidence/action: PARTIAL; name winning families and state that H4 failed
  to detect a difference from endpoint-matched linear warm-up without
  claiming equivalence; keep metric-specific endpoints.

### C11 — Metric improvement corresponds to faithful texture reproduction

- Exact current wording/source: contribution 1 L65; metrics section L181–200
  explicitly separates texture variation from fidelity; Abstract L34 says
  “reference-fidelity metrics”.
- Reviewer concern: R1.1 and R1.3 (visible full-object fidelity, variation
  versus reference fidelity); R1.4 (metric trade-offs).
- Evidence/cohort/freshness: GT-only Visualization-24 frozen before A2
  outcomes; formal D archive exists; E on FRESH_CONFIRM_300; the 2026-10-06
  GLB-native base-color evaluation now validates stored F outputs for the
  supported 20-object cohort, but does not establish human-perceived fidelity.
- Comparator/control: panels include GT/no-adapter/GFL/GFH/GC3/LFM/LHL/LLH;
  same inputs/seed within render panels and same bake pipeline in F; formal
  failure/win/median rank rule still needs manual verification.
- Support: E links effects to GT texture statistics; FG-LPIPS and GT-relative
  error add evidence; F has unseen-view and seam outcomes. The completed
  visual audit found color/material mismatch in 18/24 panels and fine-detail
  loss in 21/24. Scalar metrics and this bounded visual audit do not prove
  human-perceived fidelity; no human preference data exist.
- Alternative: high-frequency variation can be noise, repetition, or color
  shift; the manual visual taxonomy is complete, but its limits leave the
  human evidence gate open.
- Confidence/action: OPEN for human-validated fidelity, PARTIAL for bounded
  image-space evidence; run the four-pair final lock or explicitly de-scope
  human validation. Report all eight endpoints separately.

### Historical C12 notes as of 2026-10-05 (superseded by the current C12 entry above)

The following notes predate the native EGL render completed on 2026-10-06.

- Exact current wording/source: contribution 4 L71 calls the 12-object bake
  “bounded practical evidence”; §4.7 L511–587; response R1.1 L30–73.
- Reviewer concern: R1.1 practical value, seams, unseen views, and old
  contradictory bake surfaces.
- Evidence/cohort/freshness: current V3 unified F was frozen on a GT-only
  24-object list before method outcomes; n=20 after pre-generation UV
  exclusions. Earlier 12-object case studies are separate and not pooled.
- Comparator/control: same source views/reference/latent/texture size/bake
  pipeline/unseen cameras within F. Object is unit; no performance-based
  exclusions. Same draw controls and no adapter included.
- Support at that time: source identities and paired outputs were traceable,
  but the clamp-versus-repeat addressing and bilinear-versus-mipmap filtering
  mismatch prevented the old metrics from validating exported GLBs. Cross-
  backbone baking is absent.
- Alternative: limited n, four no-UV exclusions, six substantially
  out-of-range UV objects, one extreme-scale UV object, and a run-summary
  coverage gap (16/20 objects) all limit the old evaluation.
- Confidence/action at that time: OPEN; rerun the supported cohort under a
  frozen GLB-conformant renderer and document the no-UV exclusions. The
  renderer rerun is complete for stored N=20/8 outputs; strict N=24 remains
  outside scope.

### C13 — Failure behavior is systematic and explainable

- Exact current wording/source: §4.5 texture/robustness audits L474–510 and
  the response R1.1/R1.3 failure-boundary discussion; limitations L694 onward.
- Reviewer concern: R1.1 visible color/repetition failures; R1.3 texture
  variation versus fidelity.
- Evidence/cohort/freshness: historical strict-276 losses are retrospective;
  E is prospective on FRESH_CONFIRM_300 with GT-only predictors and no
  outcome-selected thresholds.
- Comparator/control: LLH−GFL per object; same runner/input/seed; GT predictors
  fixed independently of method outputs. No matched cross-backbone boundary
  test.
- Support: E reports Spearman ΔFG-PSNR versus GT HF energy −0.691
  [−0.745, −0.626], quartile reversal, and Holm family results. Visual failure
  labels remain unverified until C11 review.
- Alternative: sample/cohort dependence and the duplicate-content pair can
  affect the exact boundary magnitude; no claim of universal predictor.
- Confidence/action: PARTIAL until visual taxonomy; retain the quantitative
  applicability boundary with predictor and cohort scope.

### C14 — Transfer beyond the primary backbone

- Exact current wording/source: Abstract L34 and contribution 4 L71 state
  layer redistribution “transfers to one additional adapter architecture”;
  §4.8 L642–691; response R2.3 L221–248.
- Reviewer concern: R2.3 architecture dependence, comparable intervention,
  mapping, and UID provenance.
- Evidence/cohort/freshness: legacy Exact-76 is evaluation evidence, not a
  fresh holdout; V3 G uses the originally frozen MV-Adapter subset and covers
  98/99 planned objects after 17 missing-object completions and one
  hash-verified path-only mesh exclusion. MVDiffusion is an interface
  boundary, not an additive-residual replication.
- Comparator/control: within-backbone paired schedules, fixed topology map;
  shared seeds within each panel. G tests low-to-high point intervention;
  no comparable common cap exists across backbones.
- Support: legacy transfer effects are small/metric-dependent. G shows near-
  zero deep/middle responses and small late-shallow LPIPS worsening. Its
  exploratory interaction tests do not survive four-metric correction;
  visual/3D transfer evidence is absent.
- Alternative: weak dose range, mapping choices, one technically unsupported
  frozen GLB, and lack of a comparable cross-backbone dose normalization.
- Confidence/action: UNSUPPORTED as broad transfer; allow only the bounded
  n=98/99 result for this intervention range. The observed difference from
  the primary-backbone map is consistent with intervention-specific response
  surfaces, but cannot isolate architecture because intervention geometries
  differ. No confirmatory interaction claim is supported.

### C15 — CAI predicts a useful schedule beyond post-hoc description

- Exact current wording/source: manuscript explicitly says CAI is “an
  empirical diagnostic, not as a theorem or a guaranteed selector” (L205–209);
  response R2.2 L212–219 says yes, it is post hoc.
- Reviewer concern: R2.2.
- Evidence/cohort/freshness: no prospective CAI prediction test; the factorial
  is development evidence and MV-Adapter CAI is undefined/set-valued.
- Comparator/control: no frozen CAI prediction or independent outcome cohort;
  budget/cap/runner controls do not apply to a prediction that was never
  specified.
- Support: evidence contradicts unique-selector language; no qualitative or
  3D predictive evidence, no cross-backbone rule.
- Alternative: CAI remains a descriptive vocabulary for measured stage
  utilities only.
- Confidence/action: UNSUPPORTED as predictive; write §15 decision record and
  retain only descriptive use or retire it from the core narrative.

### C16 — Computational and reproducibility claims are traceable

- Exact current wording/source: method L170–176 says no new forward or
  measurable memory cost; data/reproducibility text and response R1.5 make
  implementation/reproducibility claims.
- Reviewer concern: R1.5 code/reproducibility; R3 implementation and
  aggregation detail.
- Evidence/cohort/freshness: campaign ledgers/manifests, frozen protocols,
  identity/integrity audits, reproduction runs, and G manifest. All cohorts
  have explicit roles; absolute paths and ignored deliverables still need
  archive hygiene.
- Comparator/control: runner/checkpoint/input/seed equality is established
  within the campaign manifests; no cross-runner absolute pooling. The claim
  “no measurable memory cost” has no independent resource benchmark in the
  current evidence.
- Support: bitwise row/image reproductions and ledger checks support
  determinism; some bootstrap audit code used process-dependent Python hash
  seeds, so those bootstrap draws are not bitwise replayable without an
  explicit hash seed. No 3D/cross-backbone result bears on computational
  traceability.
- Alternative: branch is local, remote target branch absent; ignored audit
  files and machine-absolute paths reduce portability. This is operational,
  not a scientific result.
- Confidence/action: PARTIAL; replace unsupported “measurable memory cost”
  wording unless benchmarked, freeze hashes for cohort/runner/checkpoint, and
  archive portable artifacts before declaring full traceability.

### Additional substantive claims mapped so none disappear

- **Core-7 holdout ranking** (Abstract L34; Conclusion L753–758; R1.2):
  belongs to C2/C10/C11. Strict-276 is a pre-frozen evaluation cohort; it is
  not the V3 fresh cohort and cannot validate new A3b hypotheses. The claimed
  “four primary” metrics require audit against the historical preregistered
  endpoint list before reuse.
- **FAC learned-modulation negative result** (§4.8? current §4.6, L589–598;
  Abstract L34; R1.5): assign to C16 as a separately reported negative
  extension. The controlled result is within its documented small controls;
  it does not establish that learning cannot help in general.
- **MVDiffusion boundary** (contribution 4 L71; §4.8 L668–691; R2.3):
  assign to C14. It is not direct evidence for transfer of an additive
  residual mechanism.
- **No new network forward / no measurable memory cost** (method L170–176):
  assign to C16. “No added forward” is code-checkable; “no measurable memory
  cost” lacks a benchmark and is not yet fully supported.

### Newly detected B3 interpretation issue (analysis-only; no rows changed)

The report's claimed additive “cap + layer + temporal” explanation combines
pairwise contrasts with different endpoints. Raw paired FG-PSNR means are:
LLH−GFL = +1.288 dB; LLH−LFM-EXACT = +0.434 dB; LFM-EXACT−GFL =
+0.853 dB. The identity LLH−GFL = (LLH−LFM-EXACT) + (LFM-EXACT−GFL)
holds for the *same* object-paired endpoints, but the second term combines
layer doses and the active shallow cap and is not a pure allocation effect.
The separate contrasts GFL−TGU-1.25 (+1.60), LFM-EXACT−TGU-1.675 (+2.99),
and LLH−TGU-1.675 (+3.43) use different global controls and cannot be added
to decompose LLH−GFL. Update `BUDGET_AND_CAP_CAUSAL_AUDIT.md` and any derived
decision language before evidence freeze; no campaign rerun is indicated.

---

## Acceptance-addendum reassessment — current status (2026-10-05)

This section supersedes the older C3–C7, C10–C12 narrative conclusions above
where they conflict. Exact decision and permitted wording are in
`FINAL_NARRATIVE_DECISION.md`.

### B temporal decision

| Contrast | FG-PSNR Δ [95% CI] | FG-LPIPS Δ [95% CI] | Status |
|---|---:|---:|---|
| LLH − LFM-EXACT | +0.325 [0.209, 0.446] dB | −0.00460 [−0.00563, −0.00357] | Registered; statistically detectable, inside both frozen practical margins; requested means match but realized residual norms differ. |
| LLH − HLL | +0.687 [0.404, 0.981] dB | −0.01098 [−0.01349, −0.00851] | Registered equal-high-duration placement contrast; mean effect is object-heterogeneous (45.3% PSNR favorable; median −0.104 dB). |
| LLH − LLL | +0.734 [0.597, 0.875] dB | −0.00845 [−0.01029, −0.00659] | Registered comparison; supports LLH over the all-low profile but does not by itself isolate timing. |
| HLL − LLL | +0.047 [−0.120, 0.208] dB | +0.00253 [0.00155, 0.00354] | Post-unblinding exploratory; PSNR is inconclusive and LPIPS favors LLL. |

**Current C3–C5 reading:** temporal redistribution and placement affect the
registered mean comparisons, but LLH−LFM-EXACT is small within practical
margins, actual residual norms differ, and the complete “early-high hurts /
late-high helps” signature does not hold across endpoints. The four-way
conjunction is not confirmatory.

### Interaction and 2D-law decision

- A2: strong corrected native-dose discovery map; not an independent
  dose-control confirmation.
- A3b: two formulations detect bounded-map heterogeneity, but the frozen
  dose target is missed and three-layer common support is empty (0/2,250).
  Dose-adjusted interaction significance remains extrapolative.
- MV-Adapter: no interaction metric survives the exploratory four-metric
  correction on 98/99 planned objects.
- **Current C6–C7 reading:** retain the native-dose A2 response map as a
  scoped empirical result. Do not claim an equal-dose, dose-independent
  interaction law or that the full matrix is necessary for deployment gains.
  State depth and temporal placement as separately tested dimensions, not as
  statistically independent mechanisms.

### Practical and protocol gates

- Generic schedules remain in the comparison: endpoint-matched linear is a
  credible PSNR competitor, and B's generic extension is post-lock and
  same-cohort. No universal schedule winner is established.
- Human package is frozen at exactly 40 assigned slots; stop only after all
  slots complete or withdraw; no replacement slots or significance stopping;
  min 36 complete. Response count remains zero.
- Same-draw bake outputs cover 20/24 objects, but their clamp/filter
  semantics disagree with exported GLBs; metrics and seams are historical
  diagnostics. The run summary lists only 16/20 objects. Four UV-less meshes
  also leave strict 24-object closure open.
- Clean-clone statistic reruns, the full artifact archive, and one complete
  300-object A2 condition reproduction pass. Paper-wide output regeneration
  after narrative rewrite remains open.
