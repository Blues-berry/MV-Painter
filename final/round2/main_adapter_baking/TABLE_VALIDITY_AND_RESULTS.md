# Main-adapter tables: validity and usable interpretation

Date: 2026-09-28  
Checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`  
Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`

## Validity decision

The 300-object inference artifact is internally usable: all four conditions are
present for all 300 objects, the unique-six target views are fixed, numeric
fields are finite, and the object-level paired bootstrap is reproducible.

The nominal `obj_0024`--`obj_0299` partition is **not an independent strict
holdout** for this controlled rerun. UID-level auditing finds 79 overlaps with
the historical 1,118-object training list; the full 300-object pool has 101
overlaps, including 22 in the probe. Therefore the tables support a
fixed-protocol controlled-rerun comparison, not an unseen-object
generalization claim.

## Rechecked nominal-276 results

Object-weighted means:

| condition | Full PSNR | Full SSIM | Full LPIPS | FG PSNR | FG SSIM | FG LPIPS | Edge SSIM |
|---|---:|---:|---:|---:|---:|---:|---:|
| no-adapter | 9.8886 | 0.7189 | 0.6194 | 7.0660 | 0.3941 | 0.2171 | 0.4353 |
| fixed-low | 16.1108 | 0.8468 | 0.1808 | 8.3154 | 0.3433 | 0.1889 | 0.4920 |
| fixed-high | 14.6879 | 0.8272 | 0.1757 | 6.9819 | 0.2507 | 0.1939 | 0.4963 |
| C3 | 15.9779 | 0.8514 | 0.1770 | 8.1049 | 0.3430 | 0.1879 | 0.4930 |

C3 minus baseline, with LPIPS direction-normalized so positive means better:

| comparison | Full PSNR | FG PSNR | FG SSIM | Edge SSIM | Full LPIPS improvement |
|---|---:|---:|---:|---:|---:|
| C3 vs no-adapter | +6.089 dB | +1.039 dB | -0.0511 | +0.0577 | +0.4424 |
| C3 vs fixed-low | -0.133 dB | -0.211 dB | -0.0003 | +0.0010 | +0.0037 |
| C3 vs fixed-high | +1.290 dB | +1.123 dB | +0.0924 | -0.0034 | -0.0013 |

The C3 comparison is therefore a trade-off result. It is clearly better than
fixed-high on foreground PSNR/SSIM, but not on Edge-SSIM; relative to
fixed-low, foreground PSNR is lower and foreground SSIM is statistically
unresolved. The old `+0.96 dB` claim is not reproduced by this artifact.

## Texture table

GT-relative error is `abs(log((generated_stat+1e-6)/(GT_stat+1e-6)))`; lower is
better. On the nominal 276 split, C3 lowers RGB-std, gradient, and Laplacian
errors versus no-adapter, but its HF-energy error remains worse than
no-adapter. This does not support a blanket “completely preserves texture”
claim.

| condition | RGB-std error | gradient error | Laplacian error | HF-energy error |
|---|---:|---:|---:|---:|
| no-adapter | 0.9267 | 0.5965 | 0.9062 | 0.1247 |
| fixed-low | 0.7859 | 0.3267 | 0.7943 | 0.2064 |
| fixed-high | 0.8324 | 0.3128 | 0.6741 | 0.2997 |
| C3 | 0.7360 | 0.3097 | 0.7801 | 0.2248 |

## Deliverables and restrictions

- Full raw inference and per-object CSVs: `mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6/`.
- Main tables: `eval300_unique6/tables_main_adapter/TABLES.md` and `TABLES_TEXTURE.md`.
- LaTeX tables: `main_adapter_nominal_276.tex` and `main_adapter_pooled_300.tex`.
- Machine audit: `protocol_audit.json`; corrected table manifest: `eval300_unique6/tables_main_adapter/table_analysis_manifest.json`.
- Independent Exact-GLB baking is blocked: all 43 nominal-holdout objects with raw GLB, complete views, and usable UVs overlap training.
- `selected_12_objects.csv` is retained as an audit trail only and is invalidated for independent-holdout use. A bake of those objects, if later requested, must be labeled training-overlap descriptive evidence.
