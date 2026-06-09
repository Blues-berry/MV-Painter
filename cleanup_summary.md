# Cleanup Summary

## Date: 2026-06-09

## Branch: new0529
## Backup: backup/geotex-before-cleanup

## Files Archived (→ archive/deprecated_lora_rais/)

### mvp-lora-script/ (60+ files)
Old LoRA/RAIS/RSD direction scripts. Not pursued.
- ablation_study.py, eval_ablation_*.py, module_ablation_eval*.py
- hook_analysis*.py, mechanism_hook_analysis.py
- benchmark_*.py, compute_statistics.py
- eval_clip_*.py, eval_dino.py, eval_lpips*.py
- create_paper_figures.py, create_mechanism_fig*.py
- lora_layer_analysis.py, lora_loading_sanity_check.py
- pipeline_consistency_check.py, pipeline_utils.py
- test_*.py, verify_*.py, zeroshot_audit.py
- All __pycache__/

### configs/ (archived)
- mvpainter-lora-*.yaml (8 files)
- mvpainter-pbr-*.yaml (12 files)
- mvpainter-train-unet-lora*.yaml (2 files)
- style_warm_*.yaml (1 file)
- mvpainter-geotex-midup.yaml
- mvpainter-geotex-uponly.yaml
- mvpainter-geotex-small-experiment.yaml
- ablation/ directory (4 files)

### logs/ (archived)
- logs/mvpainter-lora-* (old LoRA logs)
- MVPainter/logs/train_* (old training logs)
- MVPainter/logs/mvpainter-lora-*

### Other archived
- PBR/ (PBR experiments)
- MVPainter/output/pbr-*/ (PBR outputs)
- mvpoutput/paper_assets/ (old paper assets)
- mvpoutput/benchmark/ (old benchmarks)
- MVPainter/create_*.py, make_*.py (old figure scripts)
- geotex_stage1_report.md (superseded by fix report)

## Files Deleted
- geotex_scripts/eval_geotex.py (superseded by eval_geotex_simple.py)
- mvpoutput/geotex_sanity/geotex_step_0000000.pt (intermediate)
- All __pycache__/ directories

## Files Kept (GeoTex mainline)

### Core
- MVPainter/mvpainter/model_unet_geotex.py — model architecture
- MVPainter/configs/mvpainter-geotex-full-train.yaml — training config

### New geotex/ package
- geotex/__init__.py
- geotex/metrics.py — PSNR, SSIM, edge mask, latent scaling
- geotex/data_utils.py — batch preparation
- geotex/vis_utils.py — visualization
- geotex/train.py — training entry point
- geotex/eval.py — evaluation entry point
- geotex/audit.py — sanity, leakage, range checks

### Outputs
- mvpoutput/geotex_checkpoints/ (500, 1000, 1500, 2000)
- mvpoutput/geotex_stage1_fix_report.md
- mvpoutput/geotex_sanity/
- mvpoutput/geotex_eval/
- mvpoutput/geotex_audit/

### Data & Models (never deleted)
- data/ — original dataset
- checkpoints/hf_repo/ — base model weights
