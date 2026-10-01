# Final Round-2 Evidence Inventory (final_audit_20261001)

Audit date: 2026-10-01. Branch: `codex/round2-evidence-integrated-20261001`, HEAD `d30ed4f`.
Purpose: freeze the complete evidence baseline for the Round-2 final audit. No manuscript
text was modified. Companion files: `FINAL_REPRODUCIBILITY_MANIFEST.json`,
`claim_evidence_matrix.md`, `rescued_tmp_20261001/SHA256_MANIFEST.txt`.

Status vocabulary: `PASS` = complete, frozen, hash-verified; `RESCUED` = recovered from
volatile storage into this directory this audit; `AUDIT NEEDED` = evidence exists but a
named gap is closed by this audit; `IN PROGRESS (EXTERNAL)` = owned by another agent with
a locked protocol; `EXCLUDED` = not admissible for quantitative claims.

| # | Evidence | Dataset | Backbone | Status | Reviewer concern |
|---|---|---|---|---|---|
| 1 | Strict-276 stage-placement panel A-2 (fixed_mean / c3_lhl / hll / llh) with full prediction + GT images retained on disk | 276-object clean-v2 strict holdout (`strict_holdout_objects_276_clean_v2.txt`) | MVPainter (main) | PASS — `final/round2/stage_placement_276_20260929/` (5×276 PNGs, per-object CSVs, manifests) | R1 holdout integrity; temporal placement |
| 2 | Strict-276 same-runner layer-confirmation (global_fixed_low / layer_fixed_mean / layer_lhl / layer_llh), protocol `layer-confirmation-strict276-v1` | same 276 | MVPainter (main) | RESCUED — CSVs, rows, run manifests, analysis JSON, logs recovered from `/4T/tmp/mvpainter-layer-confirmation-20260930/` into `rescued_tmp_20261001/layer_confirmation_20260930/` (generation images already purged upstream; only obj_0024/0025 PNGs per schedule survive) | R1 holdout; headline paired statistics |
| 3 | Global C3 development pilot (fixed_low, C3_TCAS, HLL_eq, LLH_eq, LLH_ramp_eq, LLH_cosine_eq), protocol `strict-trb-development-v2` | same 276 | MVPainter (main) | AUDIT NEEDED — `coordination/c3_schedule_followup_strict276_20260930_persistent/pilot_results.json`; equal-budget development comparison, not a paper headline table | R1 schedule comparison context |
| 4 | Core-7 same-runner completion (no_adapter, global_fixed_high; GFL preflight anchor) | same 276 | MVPainter (main) | IN PROGRESS (EXTERNAL) — `scripts/run_core7_completion_276_20261001.py` running on both GPUs since 2026-10-01; protocol frozen in `coordination/core7_same_runner_completion_20261001/PROTOCOL_LOCK_CORE7_COMPLETION.md`; code path is a verbatim copy of the frozen confirmation runner, R0 namespace (object_seed = 42+idx) | R2 "different pipeline" confound |
| 5 | Robustness R0/R1 stochastic-stability replication (seeds 42+idx / 10042+idx) | same 276 | MVPainter (main) | PASS — `coordination/main_backbone_robustness1_20260930/` (report, paired bootstrap, per-object CSV, SHAs, sign-convention erratum) | R1 stochastic stability |
| 6 | Reference-realization difference R0 vs R1 (cond stretch realizations quantified: cond MAE median 0.031, cond-lat cosine median 0.940) | same 276 | MVPainter (main) | PASS — `REFERENCE_REALIZATION_DIFFERENCE{.csv,_summary.json}` in the same directory | Phase-1 LHL anomaly forensics |
| 7 | MV-Adapter cross-backbone layer-wise panel (R0, G-FL, G-LHL, G-LLH, L-FIX, L-LHL, L-LLH), 76-object Exact holdout, seed 20260928 | 76 Exact holdout | MV-Adapter (secondary) | PASS — `final/round2/mv_adapter/` (protocol, identity audit 9/9 bitwise, paired bootstrap JSON, hash manifest) | R2 cross-backbone transfer |
| 8 | MV-Adapter mapping sensitivity (alternative partition (2,1,1) + degenerate-partition identity check) | same 76 | MV-Adapter (secondary) | AUDIT NEEDED → executed in this audit (`MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL.md` + report) | R2 mapping-choice robustness |
| 9 | MVDiffusion cross-backbone panel (α-interface, 6 conditions × 75 objects; identity 36/36 bitwise; native mirror equivalent) | 75-object holdout | MVDiffusion (boundary) | PASS (negative/mixed result preserved) — `final/round2/mvdiffusion/` | Applicability boundary (R2) |
| 10 | CPU bake, 12-object stratified cohort, 8 method variants (`cpu_bake_12`, `cpu_bake_12_layerwise`), textured GLBs + unseen-view renders | 12 stratified objects | MVPainter (main) | AUDIT NEEDED — seam / cross-view consistency closed by this audit (`baking_consistency_report.md`) | R1 practical quality |
| 11 | Historical official layer-LHL strict-276 record (FG-PSNR ≈14.78) | legacy 276 pool | MVPainter (main) | EXCLUDED — provenance audited in Phase 1 (`ARCHIVED_LHL_PROVENANCE_AUDIT.md`, `historical_result_exclusion_reason.md`); record rescued to `rescued_tmp_20261001/official_lhl_v2_merged/` | Legacy anomaly |
| 12 | Eval-augmentation / shared-input determinism audits (cond `random_stretch_or_compress` provenance; object_seed=42+idx freezing) | — | MVPainter (main) | PASS — `coordination/final_acceptance_20260930/{EVAL_AUGMENTATION_AUDIT,SHARED_INPUT_DETERMINISM_AUDIT}.md` | LHL anomaly root cause |

## Volatile-storage rescue log

At audit start the following paper-facing artifacts existed only under `/4T/tmp/`
(non-durable). All were copied into `rescued_tmp_20261001/` and SHA-256 recorded:

- `mvpainter-layer-confirmation-20260930/` → `rescued_tmp_20261001/layer_confirmation_20260930/` (41 files incl. 4 schedules' per-object CSVs, rows, run manifests, `confirmation_analysis.json`, logs, smoke scripts, 8 surviving PNGs)
- `mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/` → `rescued_tmp_20261001/official_lhl_v2_merged/` (per-object CSV, report, handoff/comparison JSONs)
- `mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml` → `rescued_tmp_20261001/clean_holdout.yaml` (runner config referenced by the frozen confirmation protocol; SHA `295311ba…`)

Note: the Core-7 runner also references `/4T/tmp/.../clean_holdout.yaml` — the rescued
copy now backs this dependency.

## Known gaps recorded honestly

1. Same-runner confirmation generation images were purged before this audit (2 objects
   per schedule survive). Offline texture metrics (Phase 3) therefore use the retained
   stage-placement A-2 image set (evidence #1), which is a different runner from #2;
   this is stated in the texture report.
2. Masks are never written to disk by the strict-276 evaluation kernel; Phase 3
   recomputes them under the documented deterministic rule or states the deviation.
3. The equal-budget pilot (#3) has no checkpoint provenance for part of its rows
   (per 0930 decision) and stays out of paper-facing tables.
