# CODEX D Phase 2 CPU Baking Report

Date: 2026-09-29  
Scope: frozen 12-object Exact-GLB cohort; no clean-v2 input files or shared metric code were modified.

## Executive result

- **Task 1 — Full-SSIM root-cause crosscheck: PARTIALLY_CONFIRMED.** The original float prediction tensors are not present. Float32/float64, PyTorch/NumPy, and the tested SSIM parameter choices do not explain the 0.026–0.037 gap. The reproducible boundary is between the recorded float-eval scalar and the saved-PNG evaluation branch; exact pre-save quantization/provenance remains unresolved.
- **Task 2 — CPU bake smoke: PASS for geometry, camera, UV, visibility, export, and unseen rendering.** A low-complexity object (`obj_0015`, 27,520 triangles) and a high-complexity object (`obj_0013`, 150,000 triangles) were selected by geometry only, not by C3 performance. Both were run through five conditions: `gt`, `no_adapter`, `fixed_low`, `fixed_high`, and `c3`.
- **Task 3 — 12-object Exact Baking: COMPLETE as a diagnostic batch.** Four generated conditions were baked for all 12 frozen objects: 48 textured GLBs, 48 1024² textures, 48 metadata records, and 528 unseen-view renders. Results are object-level and must not be presented as a 276-object population estimate.

## Implementation and invariants

`geotex/cpu_texture_bake.py` runs inside Blender 4.2.4 background CPU mode. Blender performs authoritative GLB import/export and material-image binding. The bake/raster path uses the original geometry, normalization, UVs, handed-off world-to-camera poses, NumPy CPU triangle rasterization, depth-buffer visibility, and UV bilinear splatting. No proxy mesh, re-unwrap, contact sheet, or texture collage is used.

All methods share the same exact GLB, UV, camera poses, target resolution (1024), source-view set (`[0, 15, 12, 16, 13, 14]`), unseen set (raw views 1–11), visibility raster, blend rule, and CPU unseen-view rasterizer. Source foreground masks are applied before splatting. Uncovered texels are retained in a raw coverage map; the optional eight-iteration explicit 4-neighbor UV propagation is separately recorded in `inpainted_coverage` and `texture_coverage_after_inpaint`.

The unseen diagnostic renderer is an unlit texture lookup with the same fixed rendering rule for every method. It is intended to isolate texture/geometry/camera behavior; it is not a final Cycles photometric-relighting result.

## Smoke acceptance

| object | GT-to-GT masked PSNR | CIEDE2000 | silhouette IoU | raw coverage | after-inpaint coverage | exported texture verified |
|---|---:|---:|---:|---:|---:|---|
| obj_0015 | 42.3589 dB | 0.3894 | 0.9999167 | 0.6325 | 0.6847 | yes |
| obj_0013 | 30.8646 dB | 0.8331 | 0.9996277 | 0.1441 | 0.3752 | yes |

The GT-to-GT sanity check shows no obvious camera inversion, UV flip, silhouette displacement, or visibility failure. The exported GLBs were re-imported and their image textures were verified before unseen rendering. A current generated C3 render and a GT render were visually inspected. Generated views show strong cross-view appearance/contour inconsistency, while GT is smooth and geometrically aligned; this is classified as a **COLOR / SOURCE-FUSION limitation**, not a CAMERA, UV, VISIBILITY, or RASTERIZATION failure.

## 12-object output and metrics

Primary outputs:

- `cpu_bake_12/BAKE_RUN_SUMMARY.json` — 12 objects × 4 methods = 48 records.
- `cpu_bake_12/UNSEEN_OBJECT_METRICS.csv` — 48 object-level rows.
- `cpu_bake_12/UNSEEN_PER_VIEW_METRICS.csv` — 528 view-level rows.
- `cpu_bake_12/UNSEEN_METRICS_SUMMARY.json` — protocol and dependency status.

The batch reports masked PSNR, CIEDE2000, silhouette IoU, GT/render coverage, raw texture coverage, cross-view texel variance, UV seam discontinuity, FG-LPIPS, and DISTS columns. LPIPS ran with cached AlexNet CPU weights. DISTS is explicitly unavailable because `DISTS_pytorch` is not installed; its cells are left empty rather than substituted.

For orientation only, the 12-object unweighted means are:

| method | masked PSNR | CIEDE2000 | FG-LPIPS | raw texture coverage | cross-view texel variance |
|---|---:|---:|---:|---:|---:|
| no_adapter | 11.8245 | 18.2004 | 0.1563 | 0.1574 | 0.0345 |
| fixed_low | 6.0008 | 48.6233 | 0.1988 | 0.1574 | 0.0195 |
| fixed_high | 3.8907 | 60.4200 | 0.2164 | 0.1574 | 0.0127 |
| c3 | 5.6382 | 51.1835 | 0.2009 | 0.1574 | 0.0186 |

These numbers are diagnostic only. The severe generated-source disagreement and the small, mechanism-oriented cohort prevent a paper-facing superiority claim.

## Full-SSIM crosscheck link

See `../independent_validation/SSIM_ROOT_CAUSE_CROSSCHECK.md`. The candidate `METRIC_FLOAT32_RECOMMENDED.patch` remains unapplied.

