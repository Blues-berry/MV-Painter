# Reviewer action matrix — next-round revision (2026-09-30)

Basis: `coordination/reviewer_materials/CAG-D-26-00962-reviews.txt` (original
opinions, unmodified order). Current paper = `final/round2/final_round2.tex`
(layer-wise author-review version). Evidence paths verified 2026-09-30;
hashes recomputed in `METHOD_IMPLEMENTATION_AUDIT.md`.

Status legend: PASS = directly answered with current-method evidence;
PARTIAL = answered but with a disclosed boundary/gap; MISSING = not yet
answered; BLOCKED = cannot be completed with available resources (reason
given). "LW-direct?" states whether the cited evidence was produced with the
new layer-wise method (LW) or only with the older global C3/LHL.

## Reviewer 1

### R1.1 Full-object visual quality: color shifts, repeated textures, 3D baking, unseen views, seams

- Original demand: full-object comparisons across a broader object set,
  unmodified pipeline + competitive fixed-scale baseline, baked meshes from
  unseen viewpoints, seam/cross-view assessment, supplementary video.
- Current response: section "Visible complete-object evidence"
  (complete-object panels incl. failure boundaries obj_0048/0078); section
  "Baking and unseen-view case study" (12-object Exact-GLB, 48 GLBs, 528
  unseen-view rows); Supplementary S4a contact sheet (all 12 objects).
- Evidence: `final/round2/main_adapter_clean_v2/comparisons/*` (GT, no
  adapter, fixed-low, fixed-high, C3) — **not LW-direct**; bake audit
  `main_adapter_clean_v2` + `cpu_bake_12` — **not LW-direct** (four global
  conditions only). No supplementary video exists; the review noted it
  "could not be assessed" — answer honestly (no video in package).
- Gaps: (a) no layer-wise condition in the bake; (b) seam metric has no
  seam-pair denominator; (c) cross-view/source-fusion color inconsistency
  observed — retained as limitation.
- Action: keep the bake labeled as a global-control operational case study;
  add an explicit statement that the new layer-wise method has no direct 3D
  bake validation; answer the video point explicitly; report seam definition
  + missing denominator as limitation. Rewrite limitations around LW.
- Location: baking section, limitations, response letter R1.1.
- Status: **PARTIAL**.

### R1.2 Evaluation-set crossing: 300/24-probe overlap, main-adapter strict-276, historical +0.96 dB

- Original demand: evaluate the main adapter and relevant baselines under the
  same held-out protocol; verify the 0.96 dB claim outside the selection set.
- Current response: "Strict holdout and stage-placement evidence" — clean-v2
  strict-276 four-condition panel (same checkpoint as main adapter,
  controlled retraining); stage-placement follow-up; layer-LHL strict-276
  record. The +0.96 dB is removed from active text (only inside an
  `\iffalse` provenance block) and the claim ledger marks it
  HISTORICAL_ONLY.
- Evidence: `mvpoutput/.../eval300_clean_v2_unique6` (global four-condition);
  `stage_placement_276_20260929` (global); layer-LHL via
  `run_layer_official.py` (LW-direct); shared-input ablation (LW-direct).
- Gap: the strict-276 layer-wise evidence covers layer-LHL only; the
  development-probe winner (layer-LLH) and layer-fixed-mean have no holdout
  record. The historical v1 checkpoint is missing (cannot re-verify the old
  +0.96 dB directly) — stated in the ledger.
- Action: run frozen-candidate strict-276 confirmations for layer-LLH and
  layer-fixed-mean under the same runner as layer-LHL (pre-registered in
  EXPERIMENT_PROTOCOL_LOCK.md); keep +0.96 dB out of active claims; explain
  the re-audit handling in the response letter.
- Location: layer-ablation section, large-scale section, response letter.
- Status: **PARTIAL, becomes PASS after confirmation runs complete.**

### R1.3 Texture Variation vs Texture Fidelity

- Original demand: distinguish the two; gradients/Laplacian can reflect
  artifacts.
- Current response: metrics + setup sections state variation diagnostics
  "are not direct measures of texture fidelity; their symmetric log-ratio
  errors relative to ground truth are reported separately"; the CAI
  paragraph repeats it.
- Evidence: GT-relative texture errors recorded in the layer-LHL handoff
  (RGB-std/Lap/HF/gradient errors vs fixed-low); `compute_all_extended`
  produces GT-relative values in probe rows (LW-direct).
- Gap: the main text still lacks a compact evaluation taxonomy separating
  Structure / Reference-fidelity / Texture-variation / 3D-output; the
  purple-shift, repeated-texture, and noise-amplification counterexamples
  are present only as qualitative panels, not tied to the metric discussion.
- Action: add the four-dimension evaluation taxonomy; cite the
  failure-boundary figures as metric counterexamples; ban "higher HF energy
  = better texture" phrasing anywhere it remains.
- Location: metrics section, baking discussion, response letter R1.3.
- Status: **PARTIAL, becomes PASS after edit.**

### R1.4 Paired CIs, Edge-SSIM trade-off, CI-crossing-zero is not equivalence

- Original demand: paired intervals; acknowledge Edge-SSIM 0.529 vs 0.559
  trade-off; justify a non-inferiority margin or moderate the claim.
- Current response: the statistical-reporting paragraph explicitly forbids
  the equivalence reading; the stage follow-up reports paired bootstrap CIs
  and the C3-minus-LLH detected loss; the historical 0.529/0.559 numbers are
  no longer active (old table inside `\iffalse`).
- Evidence: all active tables have paired CIs (layer_lhl_v1 ablation
  summary; stage follow-up comparisons; handoff comparisons).
- Gap: ensure the response letter quotes the historical Edge-SSIM trade-off
  as re-audited-and-retired, and confirms no non-inferiority margin is
  claimed anywhere.
- Status: **PASS** (after response-letter wording check).

### R1.5 FAC implementation and code reproducibility

- Original demand: release code for FAC; Section 4.1.3 detail insufficient.
- Current response: FAC section gives training objective, optimizer, LR
  schedule, step count, parameter count (~6e3), disjoint pool; supplementary
  S7; Data availability says "available upon request".
- Evidence: `geotex/train_fac_v2.py`, `eval_fac_v2.py` exist; the EM
  share-kit contains a code copy
  (`final/EM_questionnaire_notes/share_kit/`).
- Gap: no public repo URL; "available upon request" is weak; must not
  promise a supplementary video that does not exist.
- Action: align Data availability with reality; list what the share-kit
  contains (scripts + records, no checkpoints on public hosting).
- Location: FAC section, Data availability, response letter R1.5.
- Status: **PARTIAL**.

## Reviewer 2

### R2.1 Beyond a hand-tuned three-stage schedule?

- Original demand: methodological contribution beyond schedule selection for
  an existing adapter.
- Current response: contributions reframed to training-free LAYER-WISE
  residual scaling with s_l(p) per depth group; shared-input ablation
  separates layer redistribution from temporal placement; explicit
  counterexamples (fixed-mean, LLH) reject "unique optimum".
- Evidence: `layer_lhl_v1` ablation (LW-direct); NEW: complete 8-pattern
  binary factorial (LW-direct, 24x3, 576 rows) — LLH best on 5/7 metrics,
  LHL beaten by LLL/LLH/LHH on FG-LPIPS; equal-budget global pilot
  (strict-276, running) tests placement under equal nominal budget.
- Gap: selection must not silently switch to LLH without holdout
  confirmation; strict-276 LLH/fixed-mean runs are pre-registered (protocol
  lock) and will run on the local GPU.
- Action: reorganize the ablation narrative into (i) global vs layer-wise,
  (ii) constant vs scheduled, (iii) layer-allocation effect, (iv) temporal
  placement effect; report all 8 patterns; no "LHL uniquely optimal".
- Location: method equation, layer-ablation section, large-scale section,
  contributions.
- Status: **PARTIAL, becomes PASS after confirmation + rewrite.**

### R2.2 Is CAI only post-hoc interpretation?

- Original demand: CAI appears to formalize an empirically selected schedule.
- Current response: the method paragraph "How the stage schedule is selected:
  the CAI interpretation" + the Remark already demote CAI to an empirical
  diagnostic with a set-valued/undefined rule on MV-Adapter.
- Evidence: MV-Adapter calibration `undefined_set_valued`; the stage
  follow-up counterexample (LLH beats LHL on six metrics); the new factorial
  confirms CAI could not have predicted LHL.
- Gap: none substantive; keep CAI out of the contribution list; do not claim
  CAI independently derives anything.
- Status: **PASS** (wording audit at Phase 7).

### R2.3 Cross-backbone validation on a genuinely different backbone

- Original demand (R2's stated most-important missing experiment).
- Current response: MV-Adapter 76-object audit (11 conditions, paired
  comparisons) + explicit boundary: within-backbone diagnostic, no layer-wise
  mapping on the second backbone, pretraining-UID disjointness unknown.
  MVDiffusion interop labeled interface diagnostic only.
- Evidence: `final/round2/mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.csv` etc.
- Gap: **the second backbone has no layer-wise condition** — MV-Adapter's
  geometry-residual interface was not verified to support depth-group
  mapping; the 76-object rows validate global temporal scheduling only. A
  true LW cross-backbone run requires an MV-Adapter injection-point audit
  (blocked on engineering verification, not GPU).
- Action: either implement the depth-group mapping (if the residual interface
  exposes per-level hooks) or state the technical obstacle and label the
  76-object experiment a "global stage-position replication", never "the new
  method's cross-backbone validation". The response letter must state this
  directly.
- Location: second-backbone section, limitations, response letter R2.3.
- Status: **PARTIAL / LW part BLOCKED pending interface audit.**

## Reviewer 3

- Original: "revision now looks good for publication" — thank; note that
  method/experiments were further strengthened in response to R1/R2
  (layer-wise repositioning, complete factorial, protocol separation).
- Status: **PASS** (acknowledgment in response letter).

## Cross-cutting obligations

| Obligation | State |
|---|---|
| Old +0.96 dB / CLIP-IQA / preference results removed from active claims | Removed from active text; still inside `\iffalse` provenance blocks — Phase 7 must strip them from the deliverable source (keep archived copy outside the submission tex). |
| No dataset relabeling (24-probe is not holdout) | Development ablation explicitly labeled; full factorial labeled development_only with holdout-selection forbidden. |
| No cross-runner pooling | Documented (0.00395 SSIM runner gap); new runs reuse the layer-official runner for same-runner pairing. |
| Conditional CI language | Enforced in the stats paragraph; audit all new text at Phase 9. |
| Supplementary video | Does not exist; must not be claimed. |
| Data availability | Must match reality (request-based; list artifact set). |

## New findings from this audit (feed Phase 2/7)

1. **Reference-image nondeterminism**: `MVPainterData.__getitem__` applies
   `random_stretch_or_compress` (0.5-1.5x) + `random_resize` to the
   conditioning image at every load; targets/masks/views are deterministic.
   All same-run method comparisons are paired and valid; absolute values are
   NOT comparable across separate runner invocations. This explains the
   runner differences already documented (0.00395 SSIM) and the large gap
   between the 6-method development ablation (LHL FG-PSNR 11.21) and the
   8-pattern factorial (LHL 15.66).
2. **Complete 8-pattern factorial (24x3, 576 rows, hash-verified protocol)**:
   FG-LPIPS order LLH < LHH < LLL < LHL < HLH < HHH < HLL < HHL. LLH best on
   5/7 metrics (LHH best on Full-SSIM/Full-LPIPS). LHL-LLH +0.0147
   [0.0116,0.0187]; LHL-LLL +0.0069 [0.0042,0.0108]; LHL-HLL -0.0101
   [-0.0130,-0.0074].
3. **Direction stability across the two independent probe runs**: LLH beats
   LHL in both (consistent); LHL vs LLL flips sign between runs, so mid-rank
   orderings among {LLL, LHL, fixed-mean} are reference-draw-sensitive and
   must not be claimed as stable rankings.
4. Global baselines are shallow-capped at 0.8 (min-cap); layer candidates
   are not clipped — disclosed; layer_fixed_low isolates exactly this
   difference.
