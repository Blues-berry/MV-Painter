# Experiment protocol lock — next-round confirmations (2026-09-30)

## Purpose

Pre-registration for the strict-276 holdout confirmation runs required before
the paper may describe a layer-wise schedule as a confirmed transfer result.
Written BEFORE any new holdout number was observed. The 24-object probe and
the two existing development ablations are selection surfaces; the strict-276
cohort is a confirmation surface and must not be used to choose parameters.

## Frozen protocol (unchanged from the layer-official runner)

| Item | Value |
|---|---|
| Config | `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml` (equivalent to `MVPainter/configs/mvpainter-geotex-full-train.yaml`; diffed: object list + view mode only) |
| Checkpoint | `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`, SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` |
| Object list | `final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt`, SHA-256 `a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044` |
| Views | unique6 `[0, 15, 12, 16, 13, 14]`, 256x256 |
| Steps / sampler | 50, Euler discrete |
| Seed | 42 (torch.manual_seed(42) before initial latent and again immediately before generation) |
| Metric path | `geotex.eval_exploration.compute_metrics` (identical to the stage-placement follow-up and the layer-LHL official record) |
| Schedules under test | `layer_llh` = deep/middle [1.25, 1.25, 2.50], shallow [0.50, 0.50, 0.75]; `layer_fixed_mean` = deep/middle 1.65, shallow 0.58 (17/16/17 means of layer-LHL) |
| Stage partition | progress = step/49; early < 1/3, middle < 2/3 (17/16/17 steps) |
| Scale semantics | wrapper applies min(requested scale, per-group cap deep 3.0 / middle 3.5 / shallow 0.8) |
| Output | per-object CSV + JSON rows + protocol manifest + SHA-256 index under `/4T/tmp/mvpainter-layer-confirmation-20260930/` |

## Known protocol boundary (recorded before running)

`MVPainterData.__getitem__` applies a random stretch/compress (0.5-1.5x) and
random resize to the reference conditioning image at every dataset load;
targets, masks, depths, and view order are deterministic. Consequences:

1. All methods compared WITHIN one run share the same per-object reference
   draw -> paired comparisons are valid.
2. Absolute values are NOT comparable across separate runner invocations;
   cross-runner tables must stay labeled as independent protocol surfaces.
3. The new confirmation runs are paired against the existing layer-LHL
   official record ONLY through same-object ranking/win-rate summaries with
   explicit cross-runner caveats, never by pooling absolute values.

## Pre-registration (decided 2026-09-30, before holdout observation)

- Selection surface: the complete 8-pattern binary factorial
  (`full_factorial_layer_ablation`, 24 objects x 3 seeds, 576 rows,
  development_only) with pre-specified primary metric FG-LPIPS (lower
  better), plus the earlier 6-method shared-input ablation as secondary
  evidence.
- Development ranking (FG-LPIPS): LLH 0.1046 < LHH 0.1093 < LLL 0.1124 <
  LHL 0.1193 < HLH 0.1206 < HHH 0.1248 < HLL 0.1295 < HHL 0.1355.
- Candidates promoted to holdout confirmation: **layer-LLH** (development
  winner on 5/7 metrics and in both independent probe runs) and
  **layer-fixed-mean** (constant-scale control, best non-LLH constant in the
  6-method run). NOT promoted: layer-LHH (secondary in only one probe run),
  all early-high patterns.
- Selection rule: fixed before observation; no hyperparameter of the
  schedules is re-tuned on the holdout; no additional pattern may be added to
  the holdout after seeing its result.
- Analysis plan (fixed): report the seven pre-save metrics as means over 276
  objects; paired object-level 95% percentile bootstrap (10,000 resamples,
  seed 20260930) for layer-LLH minus layer-LHL and layer-fixed-mean minus
  layer-LHL WITHIN the new runs (same runner); object win rates; no
  equivalence claims from CI crossing zero; descriptive comparison to the
  global clean-v2 panel stays qualitatively labeled (different runner).

## Determinism smoke (required before the full run)

Two same-GPU executions of object obj_0024 with identical seeds must produce
identical PNG MD5 and metrics; a third run on the other GPU is allowed to
differ (different physical device is out of scope for identity) and must be
reported separately.

## Companion runs (already protocol-frozen elsewhere)

- Equal-budget global placement pilot
  (`/4T/tmp/mvpainter-adaptive-control/geotex/residual_budget_pilot.py`,
  protocol `strict-trb-development-v2`): nominal scale sum 82.5 for
  HLL_eq/LLH_eq/LLH_ramp_eq/LLH_cosine_eq vs C3; interrupted at 211/276 with
  paired partial rows; will be resumed and completed on the free GPU. Its
  rows are a same-runner paired set; partial rows are only reported as
  partial until 276/276.
- No FAC or TRB controller search is started (task boundary).

## Status

- [x] Protocol written before new holdout runs
- [x] Candidates fixed by development metric
- [ ] Determinism smoke
- [ ] layer-LLH strict-276 (276/276)
- [ ] layer-fixed-mean strict-276 (276/276)
- [ ] Equal-budget pilot completed (276/276)
