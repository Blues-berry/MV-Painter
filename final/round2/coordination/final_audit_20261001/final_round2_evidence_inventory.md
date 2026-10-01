# Final Round-2 Evidence Inventory (final_audit_20261001, RE-SIGNED)

Audit date: 2026-10-01 (re-signed at the evidence-convergence commit). Branch:
`codex/round2-evidence-integrated-20261001`, **evidence freeze HEAD `0d308b5`**
(convergence commit: M3 + stage-2 formalized into the governance layer, wording gates
closed, `MANUSCRIPT_RELEASE_GATE.md` issued). Purpose: freeze the complete evidence
baseline for Round-2. No manuscript text was modified. Companion files:
`FINAL_REPRODUCIBILITY_MANIFEST.json` (phase-0 record, `git_head_at_audit` =
`d30ed4f…` is that phase's historical record, deliberately not rewritten),
`claim_evidence_matrix.md`, `MANUSCRIPT_RELEASE_GATE.md`,
`rescued_tmp_20261001/SHA256_MANIFEST.txt`.

Status vocabulary: `PASS` = complete, frozen, hash-verified; `RESCUED` = recovered from
volatile storage into this directory this audit; `AUDIT NEEDED` = evidence exists but a
named gap is closed by this audit; `EXCLUDED` = not admissible for quantitative claims.

| # | Evidence | Dataset | Backbone | Status | Reviewer concern |
|---|---|---|---|---|---|
| 1 | Strict-276 stage-placement panel A-2 (fixed_mean / c3_lhl / hll / llh) with full prediction + GT images retained on disk | 276-object clean-v2 strict holdout (`strict_holdout_objects_276_clean_v2.txt`) | MVPainter (main) | PASS — `final/round2/stage_placement_276_20260929/` (5×276 PNGs, per-object CSVs, manifests) | R1 holdout integrity; temporal placement |
| 2 | Strict-276 same-runner layer-confirmation (global_fixed_low / layer_fixed_mean / layer_lhl / layer_llh), protocol `layer-confirmation-strict276-v1` | same 276 | MVPainter (main) | RESCUED — CSVs, rows, run manifests, analysis JSON, logs recovered from `/4T/tmp/mvpainter-layer-confirmation-20260930/` into `rescued_tmp_20261001/layer_confirmation_20260930/` (generation images already purged upstream; only obj_0024/0025 PNGs per schedule survive) | R1 holdout; headline paired statistics |
| 3 | Global C3 development pilot (fixed_low, C3_TCAS, HLL_eq, LLH_eq, LLH_ramp_eq, LLH_cosine_eq), protocol `strict-trb-development-v2` | same 276 | MVPainter (main) | AUDIT NEEDED — `coordination/c3_schedule_followup_strict276_20260930_persistent/pilot_results.json`; equal-budget development comparison, not a paper headline table | R1 schedule comparison context |
| 4 | Core-7 same-runner completion (no_adapter, global_fixed_high; GFL preflight anchor) | same 276 | MVPainter (main) | RESOLVED — executed by the parallel task (protocol locked); 276/276 rows each; independently verified this audit (means + primary paired CI recomputed digit-for-digit) → `STRICT276_CORE7_MATRIX.md` | R2 "different pipeline" confound — CLOSED |
| 5 | Robustness R0/R1 stochastic-stability replication (seeds 42+idx / 10042+idx) | same 276 | MVPainter (main) | PASS — `coordination/main_backbone_robustness1_20260930/` (report, paired bootstrap, per-object CSV, SHAs, sign-convention erratum) | R1 stochastic stability |
| 6 | Reference-realization difference R0 vs R1 (cond stretch realizations quantified: cond MAE median 0.031, cond-lat cosine median 0.940) | same 276 | MVPainter (main) | PASS — `REFERENCE_REALIZATION_DIFFERENCE{.csv,_summary.json}` in the same directory | Phase-1 LHL anomaly forensics |
| 7 | MV-Adapter cross-backbone layer-wise panel (R0, G-FL, G-LHL, G-LLH, L-FIX, L-LHL, L-LLH), 76-object Exact holdout, seed 20260928 | 76 Exact holdout | MV-Adapter (secondary) | PASS — `final/round2/mv_adapter/` (protocol, identity audit 9/9 bitwise, paired bootstrap JSON, hash manifest) | R2 cross-backbone transfer |
| 8 | MV-Adapter mapping sensitivity — **both axes complete** | same 76 | MV-Adapter (secondary) | RESOLVED — Axis 1 budget-neutral (this audit): B'−C indistinguishable on 6/6 metrics, D ≡ C bitwise, layer advantage replicates → `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`. Axis 2 frozen-value M3 (row 13): direction-preserving, primary effects slightly stronger | R2 mapping-choice robustness — CLOSED (both tested axes) |
| 9 | MVDiffusion cross-backbone panel (α-interface, 6 conditions × 75 objects; identity 36/36 bitwise; native mirror equivalent) | 75-object holdout | MVDiffusion (boundary) | PASS (negative/mixed result preserved) — `final/round2/mvdiffusion/` | Applicability boundary (R2) |
| 10 | CPU bake, 12-object stratified cohort, 8 method variants (`cpu_bake_12`, `cpu_bake_12_layerwise`), textured GLBs + unseen-view renders | 12 stratified objects | MVPainter (main) | RESOLVED — seam / cross-view consistency audited this audit (`baking_consistency_report.md`); cross-view values are render-time color-stability descriptors (vertex-colored rendering), seam ΔE00 is the direct texture-space evidence | R1 practical quality |
| 11 | Historical official layer-LHL strict-276 record (FG-PSNR ≈14.78) | legacy 276 pool | MVPainter (main) | EXCLUDED — provenance audited in Phase 1 (`ARCHIVED_LHL_PROVENANCE_AUDIT.md`, `historical_result_exclusion_reason.md`); record rescued to `rescued_tmp_20261001/official_lhl_v2_merged/`; stage-2 discriminating run (row 14) refutes the last benign hypothesis and strengthens the exclusion | Legacy anomaly |
| 12 | Eval-augmentation / shared-input determinism audits (cond `random_stretch_or_compress` provenance; object_seed=42+idx freezing) | — | MVPainter (main) | PASS — `coordination/final_acceptance_20260930/{EVAL_AUGMENTATION_AUDIT,SHARED_INPUT_DETERMINISM_AUDIT}.md` | LHL anomaly root cause |
| 13 | MV-Adapter M3 frozen-value mapping run (3 × 76 = 228 rows; committed at `75a4068`, formalized at convergence) | same 76 | MV-Adapter (secondary) | PASS — `final/round2/mv_adapter/results/holdout_exact_mapM3_{llh,lhl,fix}_76/` (77-row per-object CSVs each), profile `layer_profile_transfer_mappingM3.json`, pre-registered protocol + report `coordination/core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_{PROTOCOL,REPORT}.md`: 16/18 MAPPING_STABLE, 1 ATTENUATED (edge_ssim, |Δ|≤0.001), 1 magnitude-trivial LPIPS flip; per-point mean 0.8065 ≠ 1 → budget-changing axis, kept separate from B′ | R2 mapping-choice robustness (axis 2) |
| 14 | LHL-forensics stage-2 discriminating run (12 stratified objects; committed at `75a4068`, formalized at convergence) | 12-object forensic cohort | MVPainter (main) | PASS — `coordination/core7_same_runner_completion_20261001/lhl_forensics/` (`stage2_regen.json`, `stage2.log`, 24 pred PNGs): aug-ON regen bit-exact vs frozen seeded rows; aug-OFF still −6.96 dB on hexuid → cond-augmentation hypothesis REFUTED; Case B strengthened (`ARCHIVED_LHL_PROVENANCE_AUDIT.md` §8) | Legacy anomaly mechanism |

## Volatile-storage rescue log

At audit start the following paper-facing artifacts existed only under `/4T/tmp/`
(non-durable). All were copied into `rescued_tmp_20261001/` and SHA-256 recorded:

- `mvpainter-layer-confirmation-20260930/` → `rescued_tmp_20261001/layer_confirmation_20260930/` (41 files incl. 4 schedules' per-object CSVs, rows, run manifests, `confirmation_analysis.json`, logs, smoke scripts, 8 surviving PNGs)
- `mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/` → `rescued_tmp_20261001/official_lhl_v2_merged/` (per-object CSV, report, handoff/comparison JSONs)
- `mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml` → `rescued_tmp_20261001/clean_holdout.yaml` (runner config referenced by the frozen confirmation protocol; SHA `295311ba…`)

Note: the Core-7 runner also references `/4T/tmp/.../clean_holdout.yaml` — the rescued
copy now backs this dependency.

## Convergence re-verification (this re-signature)

Deliverable index of `final_audit_20261001/` re-checked against the tree at freeze
HEAD `0d308b5`: 13 reports + 3 data directories (`bake_consistency/`, `texture_audit/`,
`rescued_tmp_20261001/`) + `FINAL_REPRODUCIBILITY_MANIFEST.json` all present. M3 and
stage-2 artifacts re-verified on disk: three 77-row `mapM3` per-object CSVs, M3 profile
JSON, `MAPPING_SENSITIVITY_{PROTOCOL,REPORT}.md`, `lhl_forensics/stage2_regen.json` +
`stage2.log`. Governance documents aligned at this HEAD: readiness report (re-issue
note), claim matrix ("no pending rows remain"), mapping report (M3 update +
tested-partition width), metric-direction audit (two-convention wording + manuscript
rule), bake report (descriptor rule), narrative recommendation (experiment freeze),
release gate (`MANUSCRIPT_RELEASE_GATE.md`).

## Known gaps recorded honestly

1. Same-runner confirmation generation images were purged before this audit (2 objects
   per schedule survive). Offline texture metrics (Phase 3) therefore use the retained
   stage-placement A-2 image set (evidence #1), which is a different runner from #2;
   this is stated in the texture report.
2. Masks are never written to disk by the strict-276 evaluation kernel; Phase 3
   recomputes them under the documented deterministic rule or states the deviation.
3. The equal-budget pilot (#3) has no checkpoint provenance for part of its rows
   (per 0930 decision) and stays out of paper-facing tables.
4. The bake cross-view metric uses vertex-colored rendering (environment limitation);
   values are render-time stability descriptors, never texture-fidelity metrics.
5. The historical archived record's exact runner-time state is unreconstructible
   (Case B); the record is excluded rather than explained.
