# GeoTex-Adapter Trust Audit and Cleanup Report

## A. Cleanup Summary

### Archived (→ archive/deprecated_lora_rais/)
- mvp-lora-script/ (60+ old LoRA/RAIS scripts)
- Old configs: mvpainter-lora-*.yaml, mvpainter-pbr-*.yaml, etc.
- Old logs, PBR experiments, old paper assets, old benchmarks
- Old figure scripts in MVPainter root

### Deleted
- geotex_scripts/eval_geotex.py (superseded)
- mvpoutput/geotex_sanity/geotex_step_0000000.pt (intermediate)
- All __pycache__/ directories

### Kept (GeoTex mainline)
- MVPainter/mvpainter/model_unet_geotex.py
- MVPainter/configs/mvpainter-geotex-full-train.yaml
- geotex/ package (train.py, eval.py, audit.py, metrics.py, data_utils.py, vis_utils.py)
- mvpoutput/geotex_checkpoints/ (500, 1000, 1500, 2000)
- mvpoutput/geotex_stage1_fix_report.md
- mvpoutput/geotex_sanity/, geotex_eval/, geotex_audit/

## B. Restructured Code

```
geotex/
├── metrics.py      # PSNR, SSIM, edge mask, latent scaling
├── data_utils.py   # Batch preparation
├── vis_utils.py    # Visualization
├── train.py        # Training entry point
├── eval.py         # Evaluation entry point (with region metrics + LPIPS)
└── audit.py        # Sanity, leakage, range checks
```

All hardcoded paths removed. All scripts config-driven via CLI args.

## C. Low PSNR Explanation

Absolute PSNR is low because pixel-level comparison against rendered GT is strict and generative outputs are not perfectly pixel-aligned with renderer GT. White background dominance would normally increase PSNR if backgrounds are aligned, so the low value requires careful foreground/edge reporting.

The foreground-only PSNR (4.87 → 11.76, +6.90 dB) is lower than full-image PSNR (9.36 → 19.86, +10.51 dB) because the background is easier to reconstruct (near-white, low variance). This confirms that foreground and full metrics are genuinely different, and foreground is the harder task.

## D. PSNR/SSIM Range and Mask Verification

| Check | Result |
|-------|--------|
| Identical images → PSNR=100.0 | ✓ |
| Noisy images → PSNR matches formula | ✓ |
| Image range [0,1] | ✓ |
| Mask fg_ratio=0.151 (50-object avg) | ✓ |
| Mask from alpha channel | ✓ |
| Foreground ≠ Full metric | ✓ (fg_PSNR=4.87, full_PSNR=9.36) |

## E. Data Leakage Audit

| Check | Result |
|-------|--------|
| train_objects_1200 ∩ test_objects_300 | 0 overlap ✓ |
| train_meta vs test_meta | Separate files ✓ |

## F. Fairness Check

| Check | Result |
|-------|--------|
| Same seed (42) | ✓ |
| Same scheduler (EulerDiscreteScheduler) | ✓ |
| Same init latents | ✓ |
| Same condition image | ✓ |
| Same normal/depth/mask | ✓ |
| Same view order | ✓ |
| Geo_feats cleared after forward | ✓ |
| Step0 = pixel-identical to original | ✓ (max_diff=0) |
| Config: mvpainter-geotex-full-train.yaml | ✓ |

## G. 50-Object Region Metrics (step 2000)

### Region Ratios (mean across 50 objects)
| Region | Pixel Ratio |
|--------|-------------|
| Foreground | 15.1% |
| Background | 84.9% |
| Edge | 3.5% |
| Non-edge FG | 14.3% |

### Full Image
| Metric | Original | Adapter | Diff | Improved |
|--------|----------|---------|------|----------|
| PSNR | 9.36 | 19.86 | **+10.51** | 50/50 |
| SSIM | 0.772 | 0.900 | **+0.128** | 50/50 |
| LPIPS | 0.627 | 0.200 | **-0.427 ↓** | 50/50 |

### Foreground Only
| Metric | Original | Adapter | Diff | Improved |
|--------|----------|---------|------|----------|
| PSNR | 4.87 | 11.76 | **+6.90** | 49/50 |
| SSIM | 0.289 | 0.403 | **+0.114** | 50/50 |
| LPIPS | 0.234 | 0.169 | **-0.064 ↓** | 49/50 |

### Background Only
| Metric | Original | Adapter | Diff | Improved |
|--------|----------|---------|------|----------|
| PSNR | 11.21 | 26.59 | **+15.38** | 50/50 |
| SSIM | 0.869 | 0.972 | **+0.103** | 50/50 |
| LPIPS | 0.472 | 0.083 | **-0.390 ↓** | 50/50 |

### Edge Region
| Metric | Original | Adapter | Diff | Improved |
|--------|----------|---------|------|----------|
| PSNR | 8.24 | 11.60 | **+3.36** | 49/50 |
| SSIM | 0.415 | 0.490 | **+0.075** | 48/50 |
| LPIPS | 0.114 | 0.092 | **-0.022 ↓** | 45/50 |

### Non-Edge Foreground
| Metric | Original | Adapter | Diff | Improved |
|--------|----------|---------|------|----------|
| PSNR | 4.76 | 12.14 | **+7.38** | 49/50 |
| SSIM | 0.316 | 0.421 | **+0.104** | 47/50 |
| LPIPS | 0.214 | 0.155 | **-0.059 ↓** | 48/50 |

### Per-Object Failures
- Object 29: fg_PSNR -0.50, fg_ratio=0.000 (no foreground pixels — metric invalid)
- Object 31: fg_PSNR +0.19, edge_PSNR -0.55, fg_ratio=0.019 (minimal foreground)
- Edge SSIM: 2/50 objects decreased (Objects 29, 31 — both have near-zero foreground)

## H. Judgment

### Criteria Check
| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Full PSNR/SSIM ↑ | Yes | +10.51 / +0.128 (50/50) | ✓ |
| Foreground PSNR/SSIM ↑ | Yes | +6.90 / +0.114 (49/50, 50/50) | ✓ |
| Edge SSIM not ↓ | Yes | +0.075 (48/50) | ✓ |
| LPIPS not worse | Yes | Full -0.427, FG -0.064, Edge -0.022 (all ↓) | ✓ |
| FG ≠ Full metric | Yes | fg_PSNR=4.87 ≠ full_PSNR=9.36 | ✓ |
| No train/test leakage | Yes | 0 overlap | ✓ |
| Visualization OK | Yes | No blur/color shift/structure deformation | ✓ |

### Conclusion

**CONDITIONAL PASS** — 50-object results are strong positive signals. All region metrics (full, foreground, background, edge, non-edge-fg) show improvement. LPIPS improves significantly across all regions. Foreground metrics are genuinely different from full metrics.

However, the following items are pending before paper-ready final results:
1. Multi-view consistency not yet evaluated
2. 300-object formal evaluation not yet run
3. Only 5 objects have visualizations saved
4. Edge-region LPIPS improvement is modest (-0.022) with 5/50 non-improvers

**Can proceed to 300-object formal evaluation.** Current results are sufficient to justify the effort.

## I. Next Steps

1. Run 300-object formal evaluation with region metrics
2. Add multi-view consistency metric
3. Generate publication-quality visualizations for 10+ objects
4. Compare against LoRA baselines (if checkpoints available)
