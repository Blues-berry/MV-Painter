# Codex A — main-adapter controlled rerun

Updated: 2026-09-28

## Scope

This status file covers only the main-adapter recovery, controlled retraining,
checkpoint audit, and unique6 evaluation. It does not modify the round-two
manuscript, supplementary source, MV-Adapter work, CAI calibration, or the
shared round-two statistics helpers.

## Controlled retraining

- Status: completed.
- Historical training commit: `f2f0019a008277213af0127fa7cb628cb5fa1eef`.
- Historical model source: `/tmp/mv_main_rerun/MVPainter/mvpainter/model_unet_geotex.py`.
- Historical training entry point: `/tmp/mv_main_rerun/geotex/train.py`.
- Historical config: `/tmp/mv_main_rerun/MVPainter/configs/mvpainter-geotex-full-train.yaml`.
- Training list: `/tmp/mv_main_rerun/archive/deprecated_lora_rais/paper_assets/train_objects_full.txt` (1,118 objects).
- Training list SHA-256: `7b3e998fc494ecffde247793e24efab715b4536b96382eb5fe559434fa57cae7`.
- Fixed training step: 2,000; learning rate: `1e-4`; seed: historical script default (not exposed by the historical entry point); device: `cuda:1`.
- Output: `mvpoutput/reviewer1_main_rerun_20260928/`.
- Training summary: `mvpoutput/reviewer1_main_rerun_20260928/train_summary.json`.

The checkpoint is a controlled retraining artifact, not the missing original
`geotex_refattn_v1/geotex_step_0002000.pt`.

## Final checkpoint audit

- Checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`.
- MD5: `acfb47eb48b6c567fc4e35ecb883cbcd`.
- SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Structure: `adapters` plus `encoder`; 28 finite tensor entries in the serialized state; no NaN/Inf detected.
- Filename and fixed training protocol identify step 2,000; final training summary records `max_steps=2000` and final loss `0.019594017416238785`.

## Sanity check

- Output: `mvpoutput/reviewer1_main_rerun_20260928/sanity_c3_unique6/`.
- 24 objects completed with the historical no-cap model and corrected unique-six target view order `[0, 15, 12, 16, 13, 14]`.
- Frozen schedule: C3 = `(1.25, 2.50, 1.25)`; 50 Euler steps; seed 42.
- `per_object_metrics.csv`, `summary_metrics.json`, and `manifest.json` are present.
- Model loading and forward inference completed successfully.

## Full evaluation

- Runner: `geotex/round2_main_eval.py`.
- Runner smoke test: completed for one object under `eval_runner_smoke/`.
- Full 300-object evaluation: completed normally under `eval300_unique6/` with one shared no-adapter generation per object and four conditions: no-adapter, fixed-low, fixed-high, C3.
- Protocol: 256x256, unique-six target views `[0, 15, 12, 16, 13, 14]`, seed 42, 50 Euler steps, frozen C3 `(1.25, 2.50, 1.25)`.
- Image audit: 300 PNGs in each of `predictions/no_adapter/`, `predictions/fixed_low/`, `predictions/fixed_high/`, `predictions/c3/`, and `predictions/ground_truth/`.
- CSV audit: each per-condition CSV has 300 data rows; `per_object_metrics.csv` has 1,200 rows covering all four conditions. IDs are complete and unique within each condition; all numeric fields are finite.
- Required output is present: per-condition CSVs, long CSV, evaluation manifest, ground-truth images, and four prediction image directories.

The exact launcher uses the historical source tree in `/tmp/mv_main_rerun`,
injects `target_view_mode=unique6`, and writes to the absolute output path
`/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6`.

## Deliverables

- Controlled checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`.
- Training config snapshot, 1,118-object list snapshot, and training manifest are in `mvpoutput/reviewer1_main_rerun_20260928/`.
- Command records are `training_command.txt` and `evaluation_command.txt` in `mvpoutput/reviewer1_main_rerun_20260928/`.
- Evaluation manifest and complete per-object outputs are in `mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6/`.
- Completion audit is recorded in `eval300_unique6/evaluation_audit.log`; training metrics/log artifacts are `train_metrics.csv` and `train_summary.json`.
- Main-adapter analysis tables are in `eval300_unique6/tables_main_adapter/`: `TABLES.md`, `TABLES_TEXTURE.md`, split-wise absolute CSVs, paired-bootstrap JSONs, and `table_analysis_manifest.json`.
- An earlier table audit incorrectly reported zero overlap because it compared synthetic `obj_XXXX` labels against UID lists. That statement is superseded by the UID-level correction below. These tables describe the controlled rerun and must not be relabeled as recovery of the missing historical checkpoint.
- The 24-object probe remains separately recorded in `sanity_c3_unique6/`; it was not used for checkpoint selection.
- **Audit correction:** UID-level comparison found 101 train/evaluation overlaps overall and 79 overlaps inside the nominal 276-object split. The earlier zero-overlap note was incorrect and is superseded by `MAIN_ADAPTER_RESULT_AUDIT.md`.
- The nominal 276-object tables remain reproducible controlled-rerun tables, but must not be called an independent strict holdout.
- Formal independent Exact-GLB baking is currently blocked: all 43 nominal-holdout objects with raw GLB, complete views, and usable UVs overlap the training list.

The corrected table manifest and protocol audit now record 101 overall UID overlaps, including 79 in the nominal 276 split and 22 in the probe. The regenerated 276-object paired table recheck passed for all 1,200 rows/condition records and the Round-2 statistics/texture/bake test suite passed (15 tests). The tables are usable for a fixed-protocol controlled-rerun analysis, but not for an independent strict-holdout claim.

No formal independent 3D bake was produced. The retained `selected_12_objects.csv` is explicitly invalidated for independent use because every exact-GLB candidate in the nominal holdout overlaps the historical training list. Any future bake of those 12 objects must be labeled training-overlap descriptive evidence.

## Clean evaluation dataset v2

- Status: dataset constructed; inference, table generation, and output audits completed.
- New dataset directory: `final/round2/clean_dataset_v2/`.
- The old `test_objects_300.txt`, old rendered objects, and old inference output are preserved.
- Exactly 101 overlapping positions were replaced in place; 199 disjoint old UIDs were retained.
- The replacement pool contains 189 complete existing rendered objects; all 101 selected replacements have required views `000`--`016` for image, normal, depth_png, and camera.
- New 300-object UID intersection with the historical 1,118-object training list: 0.
- New probe/holdout sizes: 24 / 276; target views: unique6 `[0, 15, 12, 16, 13, 14]`.
- New evaluation output: `mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/`.
- New table output: `mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/tables_main_adapter_clean_v2/`.
- Completeness audit: 300 objects x 4 conditions plus 300 ground-truth images;
  each per-condition CSV has 300 rows and the long CSV has 1,200 finite rows.
- Generated split tables cover probe-24, clean strict holdout-276, and pooled-300;
  paired comparisons use 10,000 bootstrap resamples with seed `20260928`.
- The runner now accepts an explicit UID list, forces `target_view_mode=unique6`, and records the list hash and UID mapping in `evaluation_manifest.json`.
- Important quarantine rule: the 101 replacement objects came from the existing `train_objects_1200.txt` pool but were not in the historical 1,118-object training list. They must not be used to train a future model evaluated on clean-v2; future retraining must use the preserved 1,118 list or a separately audited disjoint training list.
- Result interpretation: clean-v2 is technically usable as a UID-disjoint
  fixed-protocol evaluation, but its source composition differs because of the
  101 replacements. On clean holdout-276, C3 improves full-image metrics over
  no-adapter and beats fixed-high, but is below no-adapter and fixed-low on
  foreground PSNR/SSIM. The old paper trend must not be silently reused.
- Result audit: `final/round2/clean_dataset_v2/TABLE_VALIDITY_AND_RESULTS.md`
  and `eval300_clean_v2_unique6/tables_main_adapter_clean_v2/TABLES.md`.
- No paper source, supplementary, response letter, MV-Adapter, or calibration
  file was changed. No formal independent 3D bake is claimed for clean-v2.

## Reproduction command shape

The historical source tree is staged at `/tmp/mv_main_rerun`; the evaluation
launcher injects `target_view_mode=unique6` into the validation config and uses
the existing GPU execution environment. The full command is recorded in the
evaluation manifest after launch.

## 2026-09-29 clean-v2 freeze and exact-cohort audit

- Clean-v2 is frozen: 300 objects, 199 retained, 101 replacements, zero intersection with the historical 1,118-object training list.
- The controlled-retraining checkpoint and full inference manifest are unchanged. Machine-readable provenance is in `final/round2/main_adapter_clean_v2/clean_v2_freeze_manifest.json` and `clean_v2_provenance_300.csv`.
- Twelve locally recovered Exact GLBs are UID-disjoint and UV-valid; the fixed cohort and hashes are in `exact_baking_cohort_manifest.csv/.json`. No proxy meshes are used.
- Raw PNG/alpha/depth metric recheck completed for all 300 objects. It confirms the real negative foreground result: no-adapter remains higher than C3 on FG-PSNR/FG-SSIM while C3 is stronger on full-image and edge metrics.

## 2026-09-29 A1--A5 audit continuation

- A1 is complete for the available artifacts. The raw audit reconstructs RGB from RGBA over white, checks the unique6 order `[0, 15, 12, 16, 13, 14]`, verifies GT/prediction panel alignment, and recomputes Full/FG PSNR, Full/FG SSIM and Edge-SSIM. Mean GT reconstruction MAE is `2.19e-4`; the saved GT panel is therefore consistent with the source camera/view arrangement within PNG/resampling error.
- LPIPS is provenance-labeled `REUSED_ORIGINAL_EVAL`. It is attached from the original same-run float-eval records and is not claimed as an independent raw-PNG LPIPS recomputation.
- The raw-vs-historical comparison is in `main_adapter_clean_v2/raw_metric_audit/raw_vs_historical_comparison.csv` and `raw_vs_historical_error_summary.json`. PSNR and FG-SSIM are close; Full-SSIM has a systematic discrepancy (mean absolute delta `0.0264`--`0.0367`, 206--300/300 threshold anomalies) and Edge-SSIM has 121--254 anomalies. This is retained as a raw-PNG versus pre-save float-eval provenance/precision discrepancy. Historical float-eval values remain the primary frozen tables; raw values remain a separate audit table.
- A2 is complete in `main_adapter_clean_v2/CLEAN_V2_SOURCE_STRATIFIED_RESULTS.md` and `source_stratified_results.json`. Results are separated for retained-199 and replacement-101, with source UID, asset hash fields where available, and the set relations among `train_objects_1200`, historical `train_objects_1118`, and replacement-101. No outcome-based deletion or re-selection was performed.
- A5 handoff is complete at `main_adapter_baking/BAKE_INPUT_HANDOFF.json`. It provides the 12 UID-disjoint Exact GLB paths and SHA-256 values, Blender-validated original UV/material metadata, 17-view cameras, GT RGBA, masks, four generated conditions, unseen-view mapping, normalization, and bake parameters. Original GLB bytes were not modified.
- A3 is protocol-complete and CPU-dry-run complete. `STAGE_PLACEMENT_PROTOCOL.json` freezes fixed-mean, HLL, LLH and C3/LHL on strict holdout 276 with seed 42, 50 steps, unique6 and 256x256. The formal three-new-condition inference is pending CUDA; current host has no usable CUDA/NVIDIA driver. `STAGE_PLACEMENT_RESULTS.md` and `paired_stage_comparisons.json` explicitly mark those comparisons pending and do not make a mechanistic conclusion.
- Full-object comparison panels and paper-ready strict-276 LaTeX table were generated under `final/round2/main_adapter_clean_v2/`.
- Real visibility-aware texture baking and unseen-view metrics remain blocked on this host because `nvidia-smi` cannot communicate with a driver and the existing bake backend is CUDA-dependent and re-unwraps UVs. The audit records this as a blocker rather than substituting a proxy or changing metrics.

## 2026-09-29 Full-SSIM reconciliation and stage run preparation

- Full-SSIM reconciliation is complete for the fixed 12-object diagnostic subset
  and all 300 frozen clean-v2 objects. The machine-readable output is
  `main_adapter_clean_v2/full_ssim_reconciliation/full_ssim_comparison.csv`;
  the protocol and interpretation are in
  `main_adapter_clean_v2/full_ssim_reconciliation/FULL_SSIM_RECONCILIATION.md`.
- A is the recorded original float-eval Full-SSIM, B is the original consolidated
  SSIM implementation applied after reloading the saved PNGs, and C is the raw
  PNG audit implementation applied to the reloaded PNGs and independently
  reconstructed RGBA/white-background GT. No additive or fitted compensation was
  applied.
- For all 300 objects, the mean A/B/C Full-SSIM values are respectively:
  no-adapter `0.727334/0.764174/0.764067`, fixed-low
  `0.850439/0.882058/0.881914`, fixed-high
  `0.822611/0.857681/0.857469`, and C3
  `0.855002/0.881467/0.881327`. B-minus-A is `0.026465`--`0.036840`
  by condition, while C-minus-B is only `-0.000212`--`-0.000107`.
- The method-level paired conclusion is representation-sensitive: original A
  gives C3-minus-fixed-low `+0.004563` (95% CI `[0.003909,0.005210]`), while
  PNG-based B/C give `-0.000592/-0.000587` with CIs excluding zero on the
  negative side. C3 remains above fixed-high in all three representations.
  Therefore Full-SSIM is not released to Codex C as a single unified main-table
  number; any use must state the selected provenance explicitly.
- LPIPS remains `REUSED_ORIGINAL_EVAL`; no independent full 300-object PNG
  LPIPS recomputation is claimed, and it is not marked `FULLY_RECOMPUTED`.
- The source-stratified final candidate table is
  `main_adapter_clean_v2/CLEAN_V2_SOURCE_STRATIFIED_FINAL.md`. It retains all
  199 retained and 101 replacement objects, reports UID-level isolation and
  paired bootstrap results, and performs no outcome-based filtering.
- Stage-placement preparation is complete without formal inference: protocol
  checks, shared seed/latent checks, timestep-position mapping, atomic per-object
  records, `--resume`, error logging, and actual scaled-residual L2/RMS logging
  are implemented in `geotex/stage_placement_eval.py`. The CPU dry-run passed;
  formal CUDA execution remains pending a non-conflicting GPU assignment. The
  frozen `STAGE_PLACEMENT_PROTOCOL.json` was not changed.

## 2026-09-29 Full-SSIM serialization trace

- Static audit traced the frozen path from model output to metrics and PNG. The
  prediction returned by `eval_exploration.generate` remains float16; the
  float-eval metrics are computed before saving; the same prediction is then
  passed to `torchvision.utils.save_image`, which rounds/clamps to uint8 PNG.
  Targets are float32. No result-file, object-order, duplicate-normalization,
  or alternate prediction-cache mismatch was found.
- The likely and code-supported root-cause class is therefore the pre-save
  float16 SSIM arithmetic plus 8-bit serialization/reload, not two competing
  SSIM libraries. Exact A/B pixel MAE remains unavailable because the original
  tensors were not preserved.
- The fixed-12 audit verified all 48 CSV-to-PNG object mappings and produced
  `main_adapter_clean_v2/float_png_trace_12/FLOAT_PNG_PIXEL_COMPARISON.csv`.
  Its status explicitly marks A/B tensors unavailable and does not fabricate
  pixel comparisons. The full trace report is
  `main_adapter_clean_v2/FLOAT_PNG_SERIALIZATION_TRACE.md`.
- A controlled CUDA rerun script is ready at
  `geotex/trace_float_png_serialization.py`; it saves A/B/C tensors and exact
  pixel/SSIM comparisons from the same generation for the fixed 12 objects.
  It was not launched because this host reports no CUDA device and `nvidia-smi`
  cannot communicate with the NVIDIA driver.
- For the frozen saved artifacts, the selected uniform path is PNG-reloaded
  float32 prediction versus raw RGBA/white-background float32 GT (branch C),
  applied identically to all four methods. The decision and handoff gate are in
  `main_adapter_clean_v2/FULL_SSIM_FINAL_DECISION.md`. No compensation was
  applied, and no new Full-SSIM number was sent to Codex C or inserted into the
  paper tables.
