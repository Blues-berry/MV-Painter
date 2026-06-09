# GeoTex-Adapter Cleanup Plan

## Principles
1. Only GeoTex-Adapter mainline survives
2. attn2-only LoRA / RAIS / RSD / old ablation → ARCHIVE or DELETE
3. Never delete: original data/, checkpoints/hf_repo, final checkpoints, final reports
4. All paths configurable, no hardcoded /4T/CXY/MV-Painter

## Phase 0: Safety
- [x] Branch: new0529 (current)
- [x] Backup: backup/geotex-before-cleanup

## File Classification

### KEEP (GeoTex mainline)
| File | Reason |
|------|--------|
| MVPainter/mvpainter/model_unet_geotex.py | Core model |
| MVPainter/configs/mvpainter-geotex-full-train.yaml | Current training config |
| geotex_scripts/train_geotex_simple.py | → MERGE into geotex/train.py |
| geotex_scripts/eval_geotex_simple.py | → MERGE into geotex/eval.py |
| geotex_scripts/sanity_check_step0.py | → MERGE into geotex/audit.py |
| geotex_scripts/audit_data_pipeline.py | → MERGE into geotex/audit.py |
| geotex_scripts/eval_geotex.py | → DELETE (superseded by eval_geotex_simple.py) |
| mvpoutput/geotex_checkpoints/*.pt | Final checkpoints |
| mvpoutput/geotex_stage1_fix_report.md | Final report |
| mvpoutput/geotex_sanity/ | Sanity check output |
| mvpoutput/geotex_eval/ | Evaluation output |
| mvpoutput/geotex_audit/ | Audit output |

### ARCHIVE (old LoRA/RAIS direction → archive/deprecated_lora_rais/)
| File | Reason |
|------|--------|
| mvp-lora-script/*.py (all 60+ files) | Old LoRA/RAIS direction, no longer pursued |
| MVPainter/configs/mvpainter-lora-*.yaml | Old LoRA configs |
| MVPainter/configs/mvpainter-pbr-*.yaml | PBR configs (separate direction) |
| MVPainter/configs/mvpainter-train-unet-lora*.yaml | Old LoRA training |
| MVPainter/configs/style_warm_*.yaml | Old style transfer |
| MVPainter/configs/mvpainter-geotex-midup.yaml | Superseded by full-train |
| MVPainter/configs/mvpainter-geotex-uponly.yaml | Superseded by full-train |
| MVPainter/configs/mvpainter-geotex-small-experiment.yaml | Superseded by full-train |
| logs/mvpainter-lora-* | Old LoRA training logs |
| MVPainter/logs/* (except geotex) | Old training logs |
| MVPainter/output/pbr-*/ | PBR output (separate) |
| PBR/ | PBR experiments (separate) |
| mvpoutput/benchmark/ | Old benchmarks |
| mvpoutput/paper_assets/ | Old paper assets |

### DELETE (temp, cache, duplicates)
| File | Reason |
|------|--------|
| geotex_scripts/eval_geotex.py | Superseded by eval_geotex_simple.py |
| mvp-lora-script/__pycache__/ | Cache |
| **/__pycache__/ (all) | Python cache |
| mvpoutput/geotex_sanity/geotex_step_0000000.pt | Intermediate step0 checkpoint |
| MVPainter/__pycache__/ | Cache |

### data_process/ → KEEP (data pipeline utilities, not experiment-specific)
| File | Reason |
|------|--------|
| batch_render.py | Data pipeline |
| batch_depth_convert.py | Data pipeline |
| blender_script.py | Data pipeline |
| cleanup_invalid_objects.py | Data pipeline |

### MVPainter/ core → KEEP (not experiment-specific)
| File | Reason |
|------|--------|
| MVPainter/mvpainter/*.py | Core model code |
| MVPainter/evaluation/ | Evaluation framework |
| MVPainter/src/ | Data loading |
| checkpoints/ | Base model weights |
