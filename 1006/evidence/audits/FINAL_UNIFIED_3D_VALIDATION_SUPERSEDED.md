# Final unified 3D validation — same-draw bake audit

## Scope and authority

This report preserves the **historical 2026-10-05** reconciliation of frozen image-space outputs with the unified bake. It covers 20 of 24 frozen objects; four were excluded because one or more source meshes lacked a UV layer. The original CPU unseen renderer clamped UVs and omitted the GLBs' mipmap filtering, so the metrics below are retained as provenance only. The current native-render result is in `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`: it evaluates the exact stored N=20/8 GLBs with their embedded sampler and replaces the old renderer status, not the old files. The run-summary discrepancy (16/128 versus output 20/160) is retained as a provenance note.

All 20 objects have paired condition outputs. The source LLH and GFL outputs join to the same 20 UIDs in campaigns B1B2 and B3 and match on checkpoint, object-list hash, latent seed, reference policy, protocol, and realization. The handoff's source panel and six target-view SHA256s were reverified (980 files). The bake handoff freezes shared references, camera/view selection, texture resolution, bake implementation, and unseen camera set. `cross_view_texel_variance` is a fused-texel disagreement proxy, not a calibrated color-error measure. The legacy seam/control ratio is excluded because zero or near-zero control values produce extreme unstable ratios.

Bootstrap summaries below resample objects (10,000 draws; seed 20261005). These are descriptive closure intervals on the fixed subset; the extra diagnostic correlations are exploratory and have no p-values.

## Per-condition evidence (N=20)

| Condition | Unseen PSNR | Unseen FG-LPIPS | CIEDE2000 | Seam ΔE00 mean | 2px control | Seam excess* | Seam P90 | Seam tail >10 | Raw UV coverage | Coverage after inpaint | Inpainted fraction | Fused-texel variance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| No adapter | 8.038 | 0.1592 | 38.849 | 10.34 | 4.14 | 6.20 | 26.49 | 0.343 | 0.088 | 0.363 | 0.274 | 0.03192 |
| GFL | 11.570 | 0.1623 | 25.618 | 16.93 | 5.61 | 11.32 | 40.28 | 0.460 | 0.088 | 0.363 | 0.274 | 0.01859 |
| GFH | 11.894 | 0.1403 | 25.485 | 11.10 | 3.61 | 7.50 | 25.36 | 0.378 | 0.088 | 0.363 | 0.274 | 0.00690 |
| GC3 | 11.817 | 0.1528 | 24.898 | 14.66 | 4.87 | 9.79 | 34.76 | 0.428 | 0.088 | 0.363 | 0.274 | 0.01503 |
| LFM-EXACT | 11.630 | 0.1432 | 26.697 | 11.45 | 3.87 | 7.59 | 26.70 | 0.386 | 0.088 | 0.363 | 0.274 | 0.01009 |
| LHL | 11.655 | 0.1449 | 26.593 | 11.92 | 4.22 | 7.69 | 27.77 | 0.396 | 0.088 | 0.363 | 0.274 | 0.01232 |
| LLH | 11.713 | 0.1384 | 26.920 | 10.03 | 3.42 | 6.62 | 22.85 | 0.361 | 0.088 | 0.363 | 0.274 | 0.00764 |

## Paired LLH differences

Positive PSNR favors LLH; negative LPIPS/CIEDE/seam values favor LLH. Coverage and fusion differences are diagnostic quantities, not quality scores.

| Comparator | Metric | LLH − comparator [95% object-bootstrap CI] | Favorable objects for LLH |
|---|---|---:|---:|
| GFL | Unseen masked PSNR (dB) | +0.1436 [-1.3156, +1.6529] | 40.0% |
| GFL | Unseen FG-LPIPS (lower is better) | -0.0239 [-0.0319, -0.0166] | 95.0% |
| GFL | Unseen CIEDE2000 (lower is better) | +1.3022 [-3.5401, +5.7686] | 40.0% |
| GFL | UV seam ΔE00 mean | -6.9009 [-8.2881, -5.5218] | 100.0% |
| GFL | Seam ΔE00 excess over 2px control | -4.7022 [-6.1426, -3.3920] | 100.0% |
| GFL | UV seam ΔE00 P90 | -17.4369 [-21.1361, -13.6622] | 100.0% |
| GFL | UV seam fraction >10 ΔE00 | -0.0994 [-0.1415, -0.0592] | 95.0% |
| GFL | Local 2px control ΔE00 | -2.19869 [-2.95662, -1.46608] | descriptive |
| GFL | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFL | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFL | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFL | Cross-view fused-texel variance | -0.01095 [-0.01352, -0.00859] | descriptive |
| GFH | Unseen masked PSNR (dB) | -0.1802 [-0.8143, +0.4876] | 30.0% |
| GFH | Unseen FG-LPIPS (lower is better) | -0.0019 [-0.0052, +0.0013] | 45.0% |
| GFH | Unseen CIEDE2000 (lower is better) | +1.4353 [-0.2354, +3.0968] | 35.0% |
| GFH | UV seam ΔE00 mean | -1.0711 [-1.6478, -0.5149] | 75.0% |
| GFH | Seam ΔE00 excess over 2px control | -0.8813 [-1.3301, -0.4361] | 80.0% |
| GFH | UV seam ΔE00 P90 | -2.5114 [-3.9731, -1.0491] | 85.0% |
| GFH | UV seam fraction >10 ΔE00 | -0.0174 [-0.0377, -0.0001] | 75.0% |
| GFH | Local 2px control ΔE00 | -0.18984 [-0.52843, +0.07133] | descriptive |
| GFH | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFH | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFH | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| GFH | Cross-view fused-texel variance | +0.00073 [+0.00015, +0.00128] | descriptive |
| GC3 | Unseen masked PSNR (dB) | -0.1036 [-1.0326, +0.9209] | 30.0% |
| GC3 | Unseen FG-LPIPS (lower is better) | -0.0144 [-0.0198, -0.0096] | 90.0% |
| GC3 | Unseen CIEDE2000 (lower is better) | +2.0221 [-1.1072, +4.9289] | 30.0% |
| GC3 | UV seam ΔE00 mean | -4.6279 [-5.6314, -3.6443] | 100.0% |
| GC3 | Seam ΔE00 excess over 2px control | -3.1699 [-4.1032, -2.3117] | 100.0% |
| GC3 | UV seam ΔE00 P90 | -11.9167 [-14.8918, -9.0632] | 100.0% |
| GC3 | UV seam fraction >10 ΔE00 | -0.0677 [-0.0974, -0.0379] | 95.0% |
| GC3 | Local 2px control ΔE00 | -1.45801 [-2.16561, -0.75834] | descriptive |
| GC3 | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| GC3 | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| GC3 | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| GC3 | Cross-view fused-texel variance | -0.00739 [-0.00955, -0.00545] | descriptive |
| LFM-EXACT | Unseen masked PSNR (dB) | +0.0837 [-0.2385, +0.4260] | 35.0% |
| LFM-EXACT | Unseen FG-LPIPS (lower is better) | -0.0049 [-0.0068, -0.0031] | 95.0% |
| LFM-EXACT | Unseen CIEDE2000 (lower is better) | +0.2231 [-0.6583, +1.1150] | 40.0% |
| LFM-EXACT | UV seam ΔE00 mean | -1.4198 [-1.8268, -1.0468] | 100.0% |
| LFM-EXACT | Seam ΔE00 excess over 2px control | -0.9683 [-1.3293, -0.6377] | 90.0% |
| LFM-EXACT | UV seam ΔE00 P90 | -3.8506 [-4.8207, -2.9139] | 100.0% |
| LFM-EXACT | UV seam fraction >10 ΔE00 | -0.0256 [-0.0427, -0.0115] | 95.0% |
| LFM-EXACT | Local 2px control ΔE00 | -0.45152 [-0.70057, -0.23280] | descriptive |
| LFM-EXACT | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| LFM-EXACT | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| LFM-EXACT | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| LFM-EXACT | Cross-view fused-texel variance | -0.00245 [-0.00326, -0.00177] | descriptive |
| LHL | Unseen masked PSNR (dB) | +0.0581 [-0.2480, +0.4027] | 45.0% |
| LHL | Unseen FG-LPIPS (lower is better) | -0.0065 [-0.0092, -0.0042] | 90.0% |
| LHL | Unseen CIEDE2000 (lower is better) | +0.3276 [-0.5326, +1.2077] | 35.0% |
| LHL | UV seam ΔE00 mean | -1.8828 [-2.4595, -1.3637] | 100.0% |
| LHL | Seam ΔE00 excess over 2px control | -1.0765 [-1.6410, -0.4965] | 85.0% |
| LHL | UV seam ΔE00 P90 | -4.9205 [-6.5679, -3.3821] | 100.0% |
| LHL | UV seam fraction >10 ΔE00 | -0.0351 [-0.0547, -0.0173] | 95.0% |
| LHL | Local 2px control ΔE00 | -0.80632 [-1.43899, -0.32698] | descriptive |
| LHL | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| LHL | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| LHL | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| LHL | Cross-view fused-texel variance | -0.00469 [-0.00626, -0.00338] | descriptive |
| No adapter | Unseen masked PSNR (dB) | +3.6754 [+2.4751, +4.6062] | 95.0% |
| No adapter | Unseen FG-LPIPS (lower is better) | -0.0208 [-0.0334, -0.0090] | 75.0% |
| No adapter | Unseen CIEDE2000 (lower is better) | -11.9289 [-16.1974, -7.6633] | 90.0% |
| No adapter | UV seam ΔE00 mean | -0.3048 [-2.5020, +1.9423] | 55.0% |
| No adapter | Seam ΔE00 excess over 2px control | +0.4229 [-1.0662, +1.8582] | 45.0% |
| No adapter | UV seam ΔE00 P90 | -3.6395 [-11.1234, +3.7059] | 50.0% |
| No adapter | UV seam fraction >10 ΔE00 | +0.0178 [-0.0673, +0.1091] | 65.0% |
| No adapter | Local 2px control ΔE00 | -0.72767 [-1.78307, +0.37201] | descriptive |
| No adapter | Inpainted UV fraction | +0.00000 [+0.00000, +0.00000] | descriptive |
| No adapter | Raw UV coverage | +0.00000 [+0.00000, +0.00000] | descriptive |
| No adapter | UV coverage after inpainting | +0.00000 [+0.00000, +0.00000] | descriptive |
| No adapter | Cross-view fused-texel variance | -0.02428 [-0.03207, -0.01699] | descriptive |

## Image-space to baked-output reconciliation

For the exact same 20 UIDs, 2D condition rows and baked unseen-view rows were joined by object. The 2D comparison comes from the frozen B1B2/B3 source ledgers; it is not a separate resampling or a different cohort.

| Endpoint | 2D LLH−GFL [95% CI] | Baked unseen LLH−GFL [95% CI] |
|---|---:|---:|
| fg_psnr | +0.2789 [-1.0735, +1.7034] | +0.1436 [-1.3156, +1.6529] |
| fg_lpips | -0.0100 [-0.0196, -0.0009] | -0.0239 [-0.0319, -0.0166] |

The object-level 2D versus baked-delta rank correlations are ρ=+0.988 for PSNR and ρ=+0.617 for LPIPS (descriptive, N=20). Correlations of baked PSNR delta with changes in inpaint fraction, raw coverage, fused-texel variance, seam mean and seam P90 are undefined (constant paired values), undefined (constant paired values), +0.391, +0.134, and +0.026. These exploratory associations do not identify a failure mechanism.

### What the matched comparison supports

The stored 2D-to-bake numerical comparison cannot determine whether a real 2D-to-GLB quality mismatch exists: the unseen render does not reproduce exported-GLB addressing or filtering. Its intervals and rank correlations remain provenance/sensitivity outputs, not a faithful 3D comparison. Do not interpret the historical FG-LPIPS or seam directions as final-mesh evidence. The 2D source results are separately valid for their registered image-space endpoints; the 150-object B estimate comes from a disjoint cohort and is not the same-sample 2D comparator for this bake.

The stored seam audit provides raw seam ΔE00 and a local 2-pixel control ΔE00. This report also computes an exploratory excess value as raw seam mean minus the local-control mean; that subtraction was not a frozen endpoint and is not used for a confirmatory claim. The tracked generator was found and its two outputs were reproduced byte-for-byte, but its integer conversion emits 28 overflow warnings for the extreme-UV object and its sampling also clamps out-of-range UVs. The stored seam/control ratio is unstable when the control is near zero. These results are reproducible as files but not valid as seam evidence for the exported GLB mapping. No new UVs or re-bake were made.

## Historical closure verdict (superseded 2026-10-06)

`UNIFIED_BAKE_STATUS = FAITHFUL_GLTF_EVALUATION_OPEN; STORED_N20_RESULTS = HISTORICAL_DIAGNOSTIC_ONLY`. The original source rows and same-draw condition pairing remain traceable, but UV address and filtering mismatches mean the unseen-render, seam, and practical 3D endpoints are not eligible as faithful exported-mesh evidence. The run-summary coverage discrepancy is also retained as a provenance note. Four no-UV exclusions leave the strict 24-object request incomplete. Do not infer a schedule advantage or final 3D-quality claim from these stored metrics. The 2D source results remain separate. This report supersedes `UNIFIED_COREDRAW_BAKE_REPORT.md` only as a historical reconciliation; it does not close 3D validation.

## Provenance

- Frozen input handoff: `bake_handoff/BAKE_INPUT_HANDOFF_V3.json`.
- Exclusion record: `bake_handoff/excluded_uv_missing.json`.
- Image-space ledgers: `formal/campaign_B1B2/per_object_metrics.csv`, `formal/campaign_B3/per_object_metrics.csv`.
- Unseen-view ledger: `bake_handoff/cpu_bake_v3/UNSEEN_OBJECT_METRICS.csv`.
- Per-object bake metadata: `bake_handoff/cpu_bake_v3/<condition>/<uid>/bake_metadata.json`.
- Seam audit generator: `scripts/audit_bake_seams_v3.py` (byte-reproduced outputs; UV validity open).
- UV addressing audit: `UV_VALIDITY_AUDIT_20261005.md`.
- Machine-readable audit and hashes: `bake_handoff/UNIFIED_BAKE_CLOSURE_AUDIT.json`.
