# Original Baseline Authenticity Report

**Date:** 2026-06-10
**Verdict:** **PASS — Original IS authentic MV-Painter RGB baseline**

---

## 1. File Path Audit

All images load from correct paths:

| Object | GT Path | Original Path | Adapter Path |
|--------|---------|---------------|--------------|
| obj_008 | `.../visualizations/obj_008_gt.png` | `.../visualizations/obj_008_original.png` | `.../visualizations/obj_008_adapter.png` |
| obj_006 | `.../visualizations/obj_006_gt.png` | `.../visualizations/obj_006_original.png` | `.../visualizations/obj_006_adapter.png` |
| obj_000 | `.../visualizations/obj_000_gt.png` | `.../visualizations/obj_000_original.png` | `.../visualizations/obj_000_adapter.png` |
| obj_009 | `.../visualizations/obj_009_gt.png` | `.../visualizations/obj_009_original.png` | `.../visualizations/obj_009_adapter.png` |
| obj_001 | `.../visualizations/obj_001_gt.png` | `.../visualizations/obj_001_original.png` | `.../visualizations/obj_001_adapter.png` |
| obj_004 | `.../visualizations/obj_004_gt.png` | `.../visualizations/obj_004_original.png` | `.../visualizations/obj_004_adapter.png` |

No wrong files loaded. No error maps, normal maps, or debug outputs mixed in.

## 2. Code Trace: How Original Is Generated

In `eval.py:63-108`, `generate_images()`:
```python
def generate_images(model, batch, device, weight_dtype, geo_feats=None, ...):
    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)
    # ... denoising loop ...
    return (image * 0.5 + 0.5).clamp(0, 1)
```

When called for Original:
```python
image_orig = generate_images(model, batch, device, weight_dtype, None, num_steps, shared_latents)
#                                                                       ^^^^
#                                                          geo_feats=None → adapter bypassed
```

**When `geo_feats=None`, `_set_geo_feats_on_wrappers()` is never called. The adapters are completely bypassed. The model runs as vanilla MV-Painter.**

## 3. File Timestamp Consistency

| Object | GT mtime | Original mtime | Adapter mtime | Consistent? |
|--------|----------|----------------|---------------|-------------|
| obj_008 | 1781007891 | 1781007891 | 1781007891 | ✅ Same second |
| obj_006 | 1781007832 | 1781007832 | 1781007832 | ✅ Same second |
| obj_000 | 1781007655 | 1781007655 | 1781007655 | ✅ Same second |
| obj_009 | 1781007921 | 1781007921 | 1781007921 | ✅ Same second |
| obj_001 | 1781007685 | 1781007685 | 1781007685 | ✅ Same second |
| obj_004 | 1781007773 | 1781007773 | 1781007773 | ✅ Same second |

All three images (GT, Original, Adapter) generated in the same eval run. No stale cache.

## 4. Pixel-Level Analysis

### Channel Statistics

| Object | Image | R_mean | G_mean | B_mean | R-G diff | R-B diff |
|--------|-------|--------|--------|--------|----------|----------|
| obj_008 | GT | 245.1 | 242.8 | 240.1 | 2.3 | 5.0 |
| obj_008 | **Original** | **233.6** | **219.3** | **211.1** | **14.3** | **22.5** |
| obj_008 | Adapter | 244.1 | 241.3 | 238.5 | 2.8 | 5.6 |
| obj_006 | GT | 249.2 | 249.3 | 251.4 | 0.1 | 2.2 |
| obj_006 | **Original** | **239.8** | **217.2** | **219.6** | **22.6** | **20.2** |
| obj_006 | Adapter | 251.3 | 251.3 | 252.0 | 0.0 | 0.7 |

**Key observation:** Original has R_mean >> G_mean > B_mean (warm/reddish tone). GT and Adapter are nearly neutral. This is consistent with MV-Painter baseline producing color-cast output that the adapter corrects.

### File Size Comparison

| Object | GT size | Original size | Adapter size | Original/GT ratio |
|--------|---------|---------------|--------------|-------------------|
| obj_008 | 64 KB | 295 KB | 96 KB | 4.6× |
| obj_006 | 40 KB | 329 KB | 50 KB | 8.2× |
| obj_000 | 115 KB | 325 KB | 114 KB | 2.8× |

Original files are 3-8× larger because they contain more unique colors (color artifacts in foreground).

### Unique Color Count

| Object | GT | Original | Adapter |
|--------|-----|----------|---------|
| obj_008 | 12,401 | 55,110 | 16,601 |
| obj_006 | 9,129 | 56,058 | 9,853 |

Original has 4-6× more unique colors — consistent with noisy/colorful foreground content.

## 5. Why Original Looks "Rainbow"

The Original MV-Painter baseline (without adapter) produces images with:
1. **Color cast in foreground**: R channel consistently 15-25 units higher than G/B
2. **More color variation**: 4-6× more unique colors than GT or Adapter
3. **Larger file size**: More complex color content requires more bytes

This is **expected behavior** — the adapter's purpose is to correct these color artifacts. The "rainbow" appearance in the figure is the genuine MV-Painter baseline quality, not a visualization bug.

## 6. Cross-Check: Is Adapter Really Better?

| Object | |Orig-GT| | |Adapt-GT| | Improvement |
|--------|-----------|------------|-------------|
| obj_008 | 39.9 | 3.8 | 10.5× |
| obj_006 | 33.0 | 3.4 | 9.7× |
| obj_000 | 37.1 | 6.8 | 5.5× |
| obj_009 | 42.2 | 6.0 | 7.0× |
| obj_001 | 61.0 | 20.3 | 3.0× |
| obj_004 | 60.8 | 18.6 | 3.3× |

Adapter is consistently 3-10× closer to GT. The improvement is real.

## 7. Conclusion

**PASS: Original IS authentic MV-Painter RGB baseline.**

The "rainbow" appearance is the genuine quality of MV-Painter without the adapter. This is NOT a visualization bug, NOT a cached debug output, and NOT an error map.

The adapter's purpose is to correct these color artifacts, which it does successfully (3-10× closer to GT).

### Implication for Paper Figures

The Original column SHOULD show this poor quality — it demonstrates the adapter's value. However, for cleaner presentation:
- Consider showing GT | Original | GeoTex without zooming into the noisy foreground
- Or show the zoom with a note explaining the Original's color cast is expected
- The failure cases (obj_001, obj_004) show less improvement, which is also genuine

### Raw Images Saved

For manual inspection, raw images saved to:
`mvpoutput/geotex/eval_300obj_region/original_auth_audit/obj_XXX/original_raw.png`

No processing, no crop, no normalization — just the raw PNG as saved by eval.py.
