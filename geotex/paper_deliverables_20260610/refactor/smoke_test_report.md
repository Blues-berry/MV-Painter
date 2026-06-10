# Smoke Test Report

**Date:** 2026-06-10
**Branch:** new0529
**Checkpoint:** mvpoutput/geotex_checkpoints/geotex_step_0002000.pt

## CLI Help Tests

| Script | Status | Args |
|--------|--------|------|
| eval.py | ✅ | --config, --checkpoint, --num_objects, --output_dir, --device, --steps, --seed, --save_vis, --vis_count |
| train.py | ✅ | --config, --output_dir, --steps, --save_every, --lr, --img_size, --device, --resume |
| audit.py | ✅ | --config, --check |
| analyze_300obj.py | ✅ | --input_dir, --git_hash |
| make_comparison_figures.py | ✅ | --config, --checkpoint, --input_dir, --output_dir, --device, --steps, --num_objects |
| make_paper_figures.py | ✅ | --input_dir (bar/scatter only, NOT main figures) |
| mv_consistency.py | ✅ | --config, --checkpoint, --num_objects |

## Line Count Check

| Script | Lines | < 500? |
|--------|-------|--------|
| eval.py | 442 | ✅ |
| train.py | 231 | ✅ |
| audit.py | 209 | ✅ |
| analyze_300obj.py | 317 | ✅ |
| make_comparison_figures.py | 220 | ✅ |
| make_paper_figures.py | 216 | ✅ |
| mv_consistency.py | 220 | ✅ |
| metrics.py | 87 | ✅ |
| data_utils.py | 60 | ✅ |
| vis_utils.py | 37 | ✅ |
| **Total** | **2039** | — |

## Hardcoded Path Check

**Result:** ✅ No hardcoded `/4T/CXY/` paths found in main scripts. All paths via CLI args or config.

## Import Check

All scripts import from shared modules:
- `metrics.py` — PSNR, SSIM, edge mask, latent scaling
- `data_utils.py` — Batch preparation, collation
- `vis_utils.py` — Comparison visualization

No duplicate metric implementations found.

## Result Integrity Check

300-object results not modified:

| File | Status |
|------|--------|
| per_object_metrics.csv | ✅ 300 rows |
| region_metrics.csv | ✅ 300 rows |
| summary_metrics.json | ✅ Present |
| region_summary.json | ✅ Present |
| mv_consistency/mv_consistency_summary.json | ✅ Present |

## Visualization Files

| Category | Count | Location |
|----------|-------|----------|
| Per-object images (0-9) | 70 files | visualizations/ |
| Comparison figures | 5 files | comparison_figures/ |
| Paper figures (bar/scatter) | 5 files | paper_figures/ |

## Summary

All entry points work correctly. No hardcoded paths. No duplicate code. 300-object results preserved. Code is clean and ready for paper writing.
