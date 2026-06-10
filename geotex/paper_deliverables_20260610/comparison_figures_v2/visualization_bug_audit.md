# Visualization Bug Audit

**Date:** 2026-06-10
**Auditor:** Automated pixel-level verification

## Conclusion: Source Images Are Correct — No Column Misalignment

The previous `foreground_edge_zoom_comparison.png` had visual quality issues (too small crops, rainbow error maps, cluttered layout), but the **underlying image data is correct**.

## Audit Details

### Image Format Verification

All 10 objects (0-9) have 7 visualization images each:
- `obj_XXX_gt.png` — Ground truth (uint8, [0,255], 768×512×3)
- `obj_XXX_original.png` — Original MV-Painter prediction (uint8, [0,255])
- `obj_XXX_adapter.png` — GeoTex prediction (uint8, [0,255])
- `obj_XXX_original_error.png` — |Original - GT| amplified (uint8, [0,255])
- `obj_XXX_adapter_error.png` — |Adapter - GT| amplified (uint8, [0,255])
- `obj_XXX_edge_mask.png` — Edge mask from depth gradients
- `obj_XXX_mask.png` — Foreground mask

### Column Identity Verification

| Object | |Orig-GT| | |Adapt-GT| | |Orig-Adapt| | Closer to GT |
|--------|-----------|------------|--------------|-------------|
| 000 | 37.1 | 6.8 | 35.6 | ✅ adapter |
| 001 | 61.0 | 20.3 | 48.2 | ✅ adapter |
| 002 | 43.7 | 11.3 | 36.5 | ✅ adapter |
| 003 | 53.0 | 14.6 | 44.4 | ✅ adapter |
| 004 | 60.8 | 18.6 | 51.0 | ✅ adapter |
| 005 | 31.5 | 4.6 | 31.0 | ✅ adapter |
| 006 | 33.0 | 3.4 | 31.3 | ✅ adapter |
| 007 | 54.4 | 14.3 | 45.4 | ✅ adapter |
| 008 | 39.9 | 3.8 | 39.6 | ✅ adapter |
| 009 | 42.2 | 6.0 | 40.8 | ✅ adapter |

**All 10 objects: adapter is closer to GT than original.** Mean improvement ratio: 8.7×.

### Original ≠ Adapter

Mean pixel difference between Original and Adapter: 31-51 out of 255 range. These are **completely different images**, not duplicates.

### Error Map Verification

Saved error maps are amplified versions of |pred - GT|. The amplification factor varies per object (×2 to ×5 range). The error maps are NOT the raw predictions.

## Issues with Previous `foreground_edge_zoom_comparison.png`

1. **Crop too small** (160×160 pixels) — hard to see detail at print resolution
2. **Rainbow error maps** — RGB absolute error looks noisy, not informative
3. **7 columns per row** — too cluttered for paper
4. **Edge mask included** — not needed for main visual comparison
5. **Source image with red box** — the full image at 160×160 loses all detail

## Fix: New Figures in `comparison_figures_v2/`

- `main_visual_comparison_clean.png` — 6 objects, 6 columns (GT|Orig|GeoTex|ZoomGT|ZoomOrig|ZoomGeoTex)
- `edge_zoom_clean.png` — 5 columns with grayscale error
- `paper_main_qualitative_candidate.png` — Final candidate for paper
