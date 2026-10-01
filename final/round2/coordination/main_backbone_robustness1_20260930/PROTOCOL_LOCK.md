# PROTOCOL LOCK — Main-backbone Core-5 Robustness-1 (2026-09-30)

Written BEFORE any Realization-1 metric was observed. Branch
`codex/main-backbone-robustness1-20260930` (from `codex/next-review-response-20260930`
at `edfb8d0`). Task boundary: experiment + audit + experiment report ONLY.
No paper text, supplementary, response-letter, or method-definition changes.
The other agent's cross-backbone work (processes, outputs, GPU sessions) is
out of scope and untouched.

## Question this run answers

Does the frozen main-backbone conclusion — layer-LLH advantage over
Global fixed-low, Global C3, Layer fixed-mean, and Layer-LHL — hold on a
fully independent, pre-frozen reference-preprocessing realization
(Realization-1), under strict per-object shared inputs across all five
methods?

## Frozen candidate set (Core-5) — NO additions, NO re-selection

| ID | Runner name | Definition (identical to frozen runners) |
|---|---|---|
| GFL | `global_fixed_low` | scale 1.25 constant |
| GC3 | `global_c3` | `stage(p, 1.25, 2.50, 1.25)` |
| LFM | `layer_fixed_mean` | deep/middle 1.65, shallow 0.58 |
| L-LHL | `layer_lhl` | deep/middle `stage(p, 1.25, 2.50, 1.25)`, shallow `stage(p, 0.50, 0.75, 0.50)` |
| L-LLH | `layer_llh` | deep/middle `stage(p, 1.25, 1.25, 2.50)`, shallow `stage(p, 0.50, 0.50, 0.75)` |

`stage(p,e,m,l)`: progress = step/49; early < 1/3, middle < 2/3 (17/16/17).
Scale semantics: wrapper applies `min(requested, cap)` with caps deep 3.0 /
middle 3.5 / shallow 0.8 — identical to all frozen runners.

Forbidden: HLL, LLL, LHH, HLH, HHH, TRB, TRB2, FAC, any new
controller/schedule/scale, and ANY post-hoc re-selection of a layer pattern
after seeing Robustness-1 results. These five were frozen before this file
was written (factorial + protocol lock + confirmation runs).

## Realization definitions

- **Realization-0 (R0)** = the existing official strict-276 records:
  `object_seed = 42 + object_idx` for python `random` / numpy / torch before
  `collate_batch`; `torch.manual_seed(42)` before initial latent AND again
  immediately before `generate_with_schedule` (VAE `latent_dist.sample()`
  consumes torch RNG). Rows: `/4T/tmp/mvpainter-layer-confirmation-20260930/`
  (`global_fixed_low`, `layer_llh`, `layer_fixed_mean`, `layer_lhl`).
- **Realization-1 (R1)** = NEW pre-frozen namespace:
  **`object_seed = 10042 + object_idx`**, everything else byte-identical
  (same seed sequence structure, same latent seed 42, same runner code path).
  R1 seed != R0 seed for every object. R1 was fixed before running; it must
  not be changed regardless of results. No third realization may be created
  to "rescue" results.

## R0 matrix completion (pre-registered necessity)

The R0 same-runner strict-276 set contains 4 of the Core-5 methods; `global_c3`
was never run under the R0 runner, so the LLH−GC3 paired comparison has no R0
anchor. To make the R0-vs-R1 stability table complete for all four core
comparisons, `global_c3` is run ONCE under the byte-identical R0 protocol
(`MVP_SEED_BASE=42`, same runner script, same config/checkpoint/list/steps/
seed-sequence) into a separate `r0_completion_global_c3/` directory, clearly
labeled as matrix completion (not a new method, not a re-run of frozen rows).
All other R0 rows stay exactly as frozen.

## Frozen run matrix

| Block | Seed namespace | Methods | Rows |
|---|---|---|---|
| R1 Core-5 | 10042 + idx | all 5 | 276 x 5 = 1380 |
| R0 completion | 42 + idx | global_c3 only | 276 |

Per-object-per-method block replicates the frozen runner exactly:
seed(object_seed) -> `collate_batch` -> `prepare_batch` -> geo_clean ->
`geo_encoder` -> edge mask -> `torch.manual_seed(42)` -> init latent ->
`torch.manual_seed(42)` -> `generate_with_schedule` -> `ee.compute_metrics`.
The five methods re-collate independently per object; shared-input equality
is guaranteed by determinism (object-seeded) and verified by the preflight.

## Frozen protocol values (unchanged from EXPERIMENT_PROTOCOL_LOCK)

Config `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml`;
checkpoint `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`
(SHA-256 `0618d6b2...14c0`); object list
`final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt`
(SHA-256 `a6aa8ab6...d044`, 276 objects, order preserved, no resampling);
unique6 views [0,15,12,16,13,14] @ 256x256; 50 steps, Euler discrete;
latent seed 42; metric path `geotex.eval_exploration.compute_metrics`
(7 metrics: fg/full psnr/ssim/lpips + edge_ssim).

## Preflight gate (mandatory before the formal 276)

10 fixed strict-276 objects — `random.Random(20260930).sample(range(276),10)`
= indices [3,23,45,60,88,137,166,199,232,262] (same frozen sample as the
R0 shared-input audit) — x 5 methods, SHA-256 over: raw reference PNGs,
`cond_imgs` raw, cond resized, VAE cond-latent, target raw + grid, normals
raw + grid, depth raw + grid, mask grid, geo_clean, geo_feats dict, global
embeds, initial latent (GPU fp16 + CPU fp32), scheduler timesteps/sigmas.

PASS requires, under the R1 seed namespace:
1. cross-method mismatch = 0 within each process;
2. pass1 vs pass2 (two independent Python processes) mismatch = 0.

If the gate fails: STOP. No formal 276 rows may be produced until the input
sharing fault is fixed. Formal rows are also aborted if any in-run integrity
check fails (see runner).

## Statistics plan (fixed before R1 metrics were seen)

Per (realization, comparison, metric): paired object-level deltas over the
276 common objects; 95% percentile bootstrap, 10,000 resamples, seed
20260930, object as the sampling unit (views are never independent samples);
mean/median delta, CI, win rate, ties. Comparisons (R1 minus R0-analog,
"minus" = first minus second):

- `layer_llh − global_fixed_low` (primary)
- `layer_llh − global_c3`
- `layer_llh − layer_fixed_mean`
- `layer_llh − layer_lhl`

R0 deltas come from the frozen same-runner R0 rows (+ the pre-registered
R0-C3 completion). The two realizations are NEVER pooled into a 552-row
sample; only per-realization paired deltas are compared.

Stability labels (experiment-report labels, not paper wording), per
comparison x metric:

- `STABLE_STRONG`: same sign in R0 and R1, both CIs exclude 0
- `STABLE_DIRECTIONAL`: same sign, at least one CI crosses 0
- `UNSTABLE`: sign flip between realizations

Ranking sensitivity: Core-5 order per metric in R0 vs R1; explicit check
whether LLH > LHL and LLH > GFL hold in both, and whether mid-rank orders
({GFL, GC3, LFM} and {LHL, LFM}) change. Mid-rank flips are reported, not
hidden.

## Primary robustness gate (fixed before R1 results)

Gate = `layer_llh − global_fixed_low`. Classify:

- `ROBUSTNESS_SUPPORTED` — R1 direction matches R0 on the key
  fidelity/structure metrics, most paired CIs exclude 0, no systematic
  reversal;
- `ROBUSTNESS_SUPPORTED_WITH_ATTENUATION` — directions mostly consistent,
  effects shrink, some CIs cross 0;
- `ROBUSTNESS_NOT_SUPPORTED` — clear direction reversal on several core
  metrics.

The gate is NOT "LLH must rank #1 on every metric".

## Output contract

All artifacts under
`final/round2/coordination/main_backbone_robustness1_20260930/`:
PROTOCOL_LOCK.md, RUN_MANIFEST.json, ROBUSTNESS1_SHARED_INPUT_AUDIT.{md,json},
per_object_metrics.csv, aggregate_metrics.csv, paired_bootstrap.json,
R0_R1_DIRECTION_STABILITY.csv, R0_R1_STABILITY_SUMMARY.json,
REFERENCE_REALIZATION_DIFFERENCE.csv, MAIN_BACKBONE_ROBUSTNESS1_REPORT.md,
ARTIFACT_SHA256SUMS.txt. Runner state supports resume via a progress
manifest; existing frozen outputs (layer_confirmation_20260930,
bake_layerwise_20260930, stage_placement_276_20260929,
main_adapter_clean_v2) are read-only for this task.

## Status

- [x] Protocol frozen before any R1 observation
- [x] Preflight shared-input audit (R1 namespace): PASS — see ROBUSTNESS1_SHARED_INPUT_AUDIT.md
- [x] R1 formal 276 x 5 = 1380/1380 (realization1_core5/), in-run integrity 0 aborts
- [x] R0 anchor re-check: bit-exact vs frozen rows (r0_anchor_llh_10/)
- [x] R0-C3 completion 276/276 (r0_completion_global_c3/)
- [x] Analysis + stability tables + report: 27 STABLE_STRONG / 1 STABLE_DIRECTIONAL /
      0 UNSTABLE; primary gate = ROBUSTNESS_SUPPORTED (MAIN_BACKBONE_ROBUSTNESS1_REPORT.md)
