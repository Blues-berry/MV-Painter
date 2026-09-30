# FINAL_TECHNICAL_ACCEPTANCE_20260930

Branch `codex/next-review-response-20260930`; final evidence commit `2b788e6`
(acceptance-doc commits follow). All audits re-verified from raw artifacts in
this session; no prior handoff state was trusted without re-checking.

## SUBMISSION_READY = YES

## A. Evaluation augmentation

**LEGAL_INFERENCE_PREPROCESSING.** Full audit: `EVAL_AUGMENTATION_AUDIT.md`.
Reason (short): all five official MVPainter configs instantiate the SAME
`MVPainterData` loader (with the reference stretch/compress) for
`validation:` — it is part of the official evaluation data path, has no
disable flag, and keeps evaluation conditioning in-distribution for the
frozen checkpoint; the demo pipeline's unstretched path is not an evaluation
protocol. Nothing was "fixed away": the historical failure was the UNSEEDED
realization, now frozen per object (seed 42+idx) in every runner. All
paper-facing experiments use this one protocol (list in the audit file). No
rerun required on protocol grounds; conditional obligation: shared-input
verification (item B), which PASSED.

## B. Shared-input determinism

**PASS.** `SHARED_INPUT_DETERMINISM_AUDIT.md/.json` (+ pass1/pass2 raw
tables): 10 strict-276 objects x 5 methods (global fixed-low, global C3,
layer-fixed-mean, layer-LHL, layer-LLH); SHA-256 over raw reference PNGs,
processed reference tensors, VAE cond-latents, targets, normals, depth,
masks, geometry features, global embeds, initial latents (GPU+CPU), and
scheduler timesteps/sigmas. 0 mismatches across two independent processes
and 0 mismatches across methods within a process. Extends to the bake
same-draw pair of runners (line-identical input construction).

## C. Baking (12-object stratified case study)

**PASS.** `BAKE_PIPELINE_INDEPENDENT_AUDIT.md/.json`: hand-traced obj_0013
(ordinary), obj_0048 (exporter-reindexing), obj_0078 x 4 methods through
panel -> texture -> GLB -> 11 unseen renders -> metrics; 243 checks, 0
problems. Highlights: 4 distinct panel/texture/GLB hashes per object; all 44
renders per object distinct across methods (no LHL/LLH aliasing, no render
reuse); GLB embeds its own texture byte-identically; same input Exact GLB
(hash-matched) for all methods; independent PSNR/CIEDE2000 recomputation
matches the CSVs (18/18 each); per-object means strictly ordered
fixed-low < C3 < LHL < LLH on all three traced objects. Permitted claim:
case-study consistency, not population-level 3D superiority; no GT bake, no
DISTS.

## D. strict-276 global fixed-low (same runner)

**COMPLETED.** `STRICT276_GLOBAL_FIXED_LOW_CONFIRMATION.md` +
`STRICT276_GLOBAL_FIXED_LOW_RAW.csv` + `..._MANIFEST.json`. 276 objects,
identical runner/config/checkpoint/list/steps/seed/preprocessing/metric code
as the layer confirmations. Key paired results (10k percentile bootstrap,
seed 20260930):

- **layer-LLH − global fixed-low: better on 7/7 metrics, all CIs excluding
  zero** — FG-PSNR +3.244 dB [+2.936,+3.542] (242/276), FG-LPIPS −0.0308
  [−0.0331,−0.0283] (261/276), Full-PSNR +2.599 dB [+2.353,+2.838] (249/276),
  Edge-SSIM +0.0276 (237/276), Full-LPIPS −0.0119, Full-SSIM +0.0076,
  FG-SSIM +0.0633.
- layer-fixed-mean − global fixed-low: better on 7/7 (FG-PSNR +2.369 dB).
- layer-LHL replica − global fixed-low: better on 6/7; global control
  retains Full-LPIPS (+0.0170 replica-minus-global) — reported honestly.

## E. Cross-backbone (MV-Adapter)

**BLOCKED** (layer-wise). `MVADAPTER_LAYER_MAPPING.md`: injection points
enumerated (4 down-block groups, 320/640/1280/1280 ch @ 96/48/24/12);
per-block scaling is implementable inference-time-only, BUT (1) the 4->3
depth-group assignment is not unique from topology, and (2) no
calibration-free layer scale values exist — the frozen MV-Adapter calibration
ended `NO_CLEAR_TRADEOFF` / stage labels not uniquely defined, and
transferring GeoTex values or picking new ones is forbidden selection. The
paper therefore keeps **global stage-position replication only** (76-object
exact-mesh holdout), matching Reviewer-2 boundary language.

## F. Reviewer coverage

| Comment | Status | Evidence |
|---|---|---|
| R1.1 full-object quality / baking / seams / video | CLOSED | main baking section + S4a/S4b; `BAKE_PIPELINE_INDEPENDENT_AUDIT.md`; seam disclaimer; no video referenced |
| R1.2 strict holdout, set crossing, +0.96 dB retired | CLOSED | clean-v2 strict-276 panel; confirmation incl. global fixed-low (`STRICT276_GLOBAL_FIXED_LOW_*`); legacy numbers absent from deliverable source |
| R1.3 variation vs fidelity | CLOSED | four-dimension metric separation; variation always paired with GT-relative errors |
| R1.4 paired CIs, CI≠equivalence | CLOSED | statistical-reporting paragraph; all active tables carry paired CIs/win rates |
| R1.5 FAC implementation & reproducibility | CLOSED | FAC re-implementation paragraph; Data availability statement; request-based code statement |
| R2.1 contribution beyond schedule search | CLOSED | layer-wise repositioning; shared-input ablations; 8-pattern factorial; no unique-optimum claim |
| R2.2 CAI post-hoc | CLOSED | CAI = empirical diagnostic only; set-valued on second backbone; in no contribution claim |
| R2.3 cross-backbone validation | PARTIALLY_CLOSED | global stage-position replication on 76-object holdout delivered; layer-wise gate BLOCKED with documented mechanical reasons (`MVADAPTER_LAYER_MAPPING.md`); no overclaim |

## G. Delivery reproducibility

- PDF/TeX same commit: YES — tex files byte-identical to commit `2b788e6`
  (verified via git status); PDFs built from that tree in `final/round2`.
- Hashes: recorded in `BUILD_REPRODUCIBILITY.md` (Phase 12 section): main
  PDF `30150d0e...`, supp PDF `28a623a8...`, letter `de5ec77a...`.
- Figures self-contained: YES (`fig1_layerwise_20260930.pdf` + logos inside
  `final/round2`; cls/sty via frozen `../output` symlinks).
- Compile: reproducible, 0 errors / 0 undefined refs; main 13pp, supp 7pp.
- Response letter synchronized: YES (new global fixed-low numbers appear in
  both; grep-verified).
- PDF metadata: no author identity.
- Bibliography: 43 entries, 1:1 with the frozen reference list.

## Evidence table (claim -> source)

| Claim | Manuscript | Letter | Raw source | Runner | Cohort | Seeds |
|---|---|---|---|---|---|---|
| LLH > LHL (7/7, CI excl. 0) | tab:confirmation + text | R1.2(3) | confirmation_analysis.json; layer_lhl/llh rows | run_layer_confirmation_276_20260930.py | strict-276 | 42+idx; latent 42 |
| LLH > global fixed-low (7/7) | tab:confirmation + text (new) | R1.2(3) (new) | STRICT276_GLOBAL_FIXED_LOW_RAW.csv/MANIFEST.json | same | strict-276 | same |
| Layer-wise > global on probe (+3.083 dB, dev) | dev-ablation section; conclusion (labeled dev probe) | R2.1(2) | E0A frozen CSV / shared-input probe | probe runner | 24 probe | 42-44 |
| Factorial robust directions (late-high helps, early-high hurts) | factorial section + S10 | R2.1(2) | full_factorial 576 rows | factorial runner | 24 probe x 3 seeds | 42-44 |
| Bake same-draw ordering (10.763/12.565/15.005/16.679) | baking section | R1.1(2) | bake_layerwise_20260930 CSVs | bake panels + global controls runners | 12 stratified | 42+idx |
| FAC negative result | FAC section | R1.5 | STRICT_TRB_DEVELOPMENT_AUDIT | FAC runner | 300 pool | 42 |
| MV-Adapter global replication (not layer-wise) | cross-backbone section | R2.3 | mv_adapter holdout_exact_76 | official pipeline + scale patch | 76 holdout | 20260928 |

Legacy numbers (+0.96 dB, CLIP-IQA, preference study) and the unseeded LHL
276 record appear NOWHERE as active evidence (the LHL archived mean 14.78
occurs only inside its labeled non-reproducibility caveat).

## Final Submission Gate (10/10 PASS)

1. Augmentation legality resolved (A: LEGAL) — PASS
2. Shared-input determinism (B) — PASS
3. Bake pipeline independence (C) — PASS
4. PDF/TeX/figures same final commit (G) — PASS
5. No cross-runner mixing in Reviewer-facing GFL comparison (D) — PASS
6. No historical invalid numbers re-entered (grep audit) — PASS
7. Cross-backbone wording within evidence (E) — PASS
8. Letter/manuscript number consistency — PASS
9. Anonymous release identity scan — PASS (after scrub; see
   ANONYMOUS_RELEASE_AUDIT.md; completeness gaps non-blocking for PDF-only)
10. Artifact hashes verifiable — PASS

## Remaining (non-blocking) notes

- Anonymous release package completeness (method-code copy into
  `release/round2_repro/`) is a pre-publication TODO, not required for the
  PDF-only submission.
- Equal-budget residual-budget pilot artifacts
  (`coordination/c3_schedule_followup_strict276_20260930_persistent/`,
  leftover tmux run finished during this session) remain OUT of the paper
  evidence set (no checkpoint provenance), consistent with prior decisions.
