# Main adapter clean-v2 audit

Status: clean-v2 provenance and inference are frozen. The checkpoint is the controlled-retraining checkpoint at step 2000, not a recovered historical checkpoint. No dataset, checkpoint, C3 value, or paper source was changed in this audit.

## Frozen evaluation

- 300 objects, ordered by `eval_objects_300_clean_v2.txt`.
- `obj_0000`–`obj_0023`: probe (24); `obj_0024`–`obj_0299`: strict holdout (276).
- 199 objects were retained from the previous evaluation list and 101 were replaced because their old UID occurred in the historical 1,118-object training list.
- The clean-v2 UID intersection with the historical 1,118-object train list is 0. The replacement UID intersection is also 0.
- `train_objects_1200.txt` is a 1,200-entry local candidate pool used when constructing the replacement set. It is not the historical 1,118-object training list, and it was not used to select the checkpoint. The clean-v2 list intersects that pool in 101 UIDs; those are the replacements, not training-list overlap.
- Target view mode is `unique6`, with ordered source views `[0, 15, 12, 16, 13, 14]`, 256×256 per view, stored as a 512×768 3×2 panel.
- Conditions are no adapter, fixed low `s=1.25`, fixed high `s=2.50`, and frozen C3 `(1.25, 2.50, 1.25)`.
- The inference manifest records shared initial latents, reference/GT camera, seed, scheduler, steps, config, object list and checkpoint hash.

The machine-readable freeze record is `clean_v2_freeze_manifest.json`; the per-object provenance and replacement-source record is `clean_v2_provenance_300.csv`.

## Checkpoint

`geotex_step_0002000.pt` is labeled as a controlled retraining checkpoint. SHA-256 is `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`; MD5 is `acfb47eb48b6c567fc4e35ecb883cbcd`. Source commit is `f2f0019a008277213af0127fa7cb628cb5fa1eef`. The historical train-list SHA-256 is `7b3e998fc494ecffde247793e24efab715b4536b96382eb5fe559434fa57cae7`.

## Main-adapter tables

The paired 276-object, pooled 300-object and probe tables are in `mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/tables_main_adapter_clean_v2/`. Existing strict-holdout means are:

| condition | Full PSNR | FG PSNR | Full SSIM | FG SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---:|---:|---:|---:|---:|
| No adapter | 10.514 | 8.776 | 0.726 | 0.478 | 0.207 | 0.479 |
| Fixed low | 15.086 | 7.030 | 0.850 | 0.355 | 0.202 | 0.500 |
| Fixed high | 13.365 | 5.410 | 0.823 | 0.229 | 0.210 | 0.494 |
| C3 | 14.875 | 6.763 | 0.855 | 0.348 | 0.201 | 0.500 |

The negative foreground result is retained: C3 is below no-adapter on FG-PSNR and FG-SSIM while improving full-image PSNR/SSIM and edge agreement. It is not used to redefine the metrics or select a checkpoint.

## Source stratification and set audit

The retained-199 and replacement-101 results are reported separately in `CLEAN_V2_SOURCE_STRATIFIED_RESULTS.md` and `source_stratified_results.json`. The replacement set is a subset of `train_objects_1200` (101 objects), disjoint from historical `train_objects_1118`; the historical list and candidate pool intersect in 1,011 objects. The complete clean-v2 evaluation list is disjoint from historical `train_objects_1118`. Per-object records use source UID and, where available, source-asset SHA-256; no object was removed after inspecting its outcome.

## Foreground metric audit

`geotex/audit_clean_v2_raw_metrics.py` reconstructs target RGB, alpha masks and depth from the original PNGs, applies the historical compositing and unique6 panel layout, and recomputes full/foreground PSNR, full/foreground SSIM and Edge-SSIM. The foreground PSNR denominator is the mean squared RGB error over the selected foreground RGB values; masked SSIM uses the historical 3×3 max-pooled mask. The raw-audit CSV and summary are under `raw_metric_audit/`.

The saved GT panel was checked against the raw RGBA reconstruction. Across all 300 objects, mean GT reconstruction MAE is `2.19e-4`, maximum object mean MAE is `4.50e-4`, and the mean per-object maximum absolute difference is `0.0308` after PNG quantization/resampling. The batch result is recorded in `raw_metric_audit/mask_alignment_audit.csv`. The lowest threshold-derived mask IoU is `0.431` on a tiny object with only `0.33%` panel foreground coverage; this is a threshold/quantization sensitivity check, not the mask used by inference. The inference mask itself is reconstructed from the same RGBA alpha channel and camera/view ordering. Thus the high discrepancy seen in the first ad-hoc check was a temporary panel rearrangement error, not a GT-camera mismatch.

The raw PNG recheck means over all 300 objects are: no adapter `(10.580, 8.964, 0.764, 0.494, 0.205, 0.490)`, fixed low `(14.946, 6.909, 0.882, 0.356, 0.204, 0.514)`, fixed high `(13.228, 5.284, 0.857, 0.227, 0.212, 0.516)`, and C3 `(14.735, 6.647, 0.881, 0.349, 0.203, 0.513)` for `(Full-PSNR, FG-PSNR, Full-SSIM, FG-SSIM, FG-LPIPS, Edge-SSIM)`. These are an independent PNG/alpha/depth audit, not a replacement of the original float-eval table.

The raw-to-historical comparison is in `raw_metric_audit/raw_vs_historical_comparison.csv` with its distribution summary and anomaly object lists in `raw_metric_audit/raw_vs_historical_error_summary.json`. PSNR differences are small (method-wise mean absolute delta `0.0007`--`0.0037` dB), and FG-SSIM differences are small (`0.0012`--`0.0096`). Full-SSIM is a systematic audit discrepancy: mean absolute deltas are `0.0264`--`0.0367`, with 206--300 of 300 objects over the `0.01` audit threshold; Edge-SSIM has 121--254 anomalies. This is retained as a provenance/precision discrepancy between the original pre-save float-eval rows and recomputation from quantized PNG panels, not treated as evidence of a camera or mask mismatch. Consequently, the historical float-eval CSV remains the source for the frozen primary tables, while the raw-PNG table is the independent audit table; the two must not be numerically pooled.

LPIPS in the raw-audit table is explicitly labeled `REUSED_ORIGINAL_EVAL`: on this CPU-only host the default audit attaches the LPIPS values recorded during the same float inference. It is not an independent raw-PNG LPIPS recomputation. The optional `--compute-lpips` mode performs a separate CPU PNG recomputation and is not used for the reported LPIPS provenance.

## Exact GLB cohort

Twelve clean-v2 objects have locally recovered, UID-disjoint Exact GLBs with usable original UVs. The files are in `exact_glbs/`; the cohort and SHA-256 values are in `exact_baking_cohort_manifest.csv` and `.json`. The cohort has four deterministic failure, four general and four success cases, defined by the lower/middle/upper thirds of clean-v2 C3-minus-fixed-high FG-PSNR. This stratification is post-hoc case organization only; it did not select the checkpoint or C3.

Full-object GT/No-adapter/C3 panels for these 12 objects are in `comparisons/`. They are 2D inference visualizations, not claims of baked texture fidelity.

## Baking and unseen-view status

The exact GLBs, original UV presence and 17-view camera/depth records have been validated. A final texture bake requires the project's visibility-aware rasterizer or an equivalent calibrated renderer. The current execution host reports no NVIDIA driver (`nvidia-smi` cannot communicate with the driver), while the existing bake implementation depends on the CUDA rasterizer and also re-unwraps UVs, which would violate the frozen original-UV requirement. Therefore no proxy mesh, re-UV bake, or unverified unseen-view number is included here. Baked meshes, Texture Fidelity metrics and unseen-view evaluation remain explicitly blocked until a calibrated visibility-aware backend is available.

This is an audit limitation, not a favorable-result substitution. The exact cohort manifest is retained so the baking stage can resume without changing the dataset or checkpoint.

The frozen baking inputs for Codex D are in `/4T/CXY/MV-Painter/final/round2/main_adapter_baking/BAKE_INPUT_HANDOFF.json`. They include the 12 original GLB paths and hashes, Blender-native UV/material audits, 17-view camera records, target/unseen mapping, GT RGBA and masks, four generated conditions, and normalization/baking parameters. The GLB bytes were not copied into or modified by the handoff.

## Stage-placement follow-up

`STAGE_PLACEMENT_PROTOCOL.json` freezes fixed-mean `(5/3,5/3,5/3)`, HLL `(2.50,1.25,1.25)`, LLH `(1.25,1.25,2.50)`, and the existing C3/LHL schedule on strict holdout objects `obj_0024`--`obj_0299`, with 50 steps, seed 42, unique6, 256×256 views, and the same controlled checkpoint. The experiment is explicitly a pre-specified follow-up after observing clean-v2. The CPU dry-run passed, but formal stage inference is pending CUDA and no stage-placement result has been fabricated. Existing C3 versus fixed-low/high bootstrap comparisons remain in `paired_stage_comparisons.json`.

## Reproduction commands

```bash
python geotex/freeze_clean_v2.py
python geotex/build_exact_cohort_manifest.py
python geotex/make_clean_v2_comparisons.py
PYTHONPATH=/tmp/mv_main_rerun/geotex python geotex/audit_clean_v2_raw_metrics.py \
  --eval-dir mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6 \
  --object-list final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt \
  --data-root data/train_data/rendered_full \
  --output-dir final/round2/main_adapter_clean_v2/raw_metric_audit
```
