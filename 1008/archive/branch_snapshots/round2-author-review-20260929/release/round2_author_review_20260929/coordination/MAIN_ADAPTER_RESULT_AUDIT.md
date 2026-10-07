# Main Adapter v1 — Round 2 Result Audit

Date: 2026-09-28  
Checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`  
Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`

## Executive result

The inference artifact is internally reproducible and the metric implementation is auditable. However, the nominal 276-object split is **not an independent strict holdout** for this controlled rerun: 79 of its UIDs occur in the historical 1,118-object training list. The earlier zero-overlap statement was caused by comparing synthetic `obj_XXXX` labels against UID lists and is superseded.

Therefore:

- the tables are valid as a fixed-protocol controlled-rerun analysis;
- they are not valid evidence for an independent unseen-object generalization claim;
- the missing original v1 checkpoint remains unrecovered;
- no 3D baking result from the current nominal holdout may be presented as independent holdout evidence.

## Verified protocol audit

| Item | Status | Evidence |
|---|---|---|
| 300 objects × 4 conditions | VERIFIED | `eval300_unique6/per_object_metrics.csv`: 1,200 rows, 1,200 unique object-condition pairs |
| Required views and files | VERIFIED | Required `000`–`016` image/normal/depth/camera files exist for all 300 objects; extra depth files exist for 41 objects but are not protocol views |
| Unique-six target mapping | VERIFIED | `[0,15,12,16,13,14]`, manifest and historical dataset code |
| Shared checkpoint/seed/latents | VERIFIED | One checkpoint, seed 42, shared per-object initial latent, 50 Euler steps, 256×256 |
| Train/eval disjointness | BLOCKED | 101 UID overlaps overall; 79 overlap the nominal 276 split |
| Metric values finite | VERIFIED | All CSV numeric fields finite; no missing object-condition rows |
| Exact GLB independent holdout | BLOCKED | 43 nominal-holdout objects have existing raw GLB + complete views + UV, but all 43 overlap training |

The machine-readable audit is `main_adapter_baking/protocol_audit.json`.

## Metric implementation audit

The historical evaluator computes:

- `Full PSNR`: `compute_psnr(pred, target)` over all RGB pixels, including the white background.
- `FG-PSNR`: `compute_psnr(pred, target, mask)` after expanding the alpha foreground mask to RGB and thresholding at `>0.5`.
- `Full SSIM`: 3×3 local SSIM map averaged over the full image.
- `FG-SSIM`: the same local map averaged over a 3×3 max-pooled/dilated foreground mask.
- `Full LPIPS`: Alex LPIPS on the full image after mapping `[0,1]` to `[-1,1]`.
- `FG-LPIPS`: Alex LPIPS after zeroing the background with the foreground mask.

Thus Full metrics are background-dominated and cannot be interpreted as foreground texture fidelity. The foreground mask is sourced from target-image alpha, resized by `prepare_batch`; edge metrics use a Sobel mask from depth when available, otherwise normals. Metrics are computed on the six-view concatenated object tensor and then resampled at the object level.

The source hashes and exact implementation notes are in `main_adapter_baking/protocol_audit.json`.

## C3 findings

On the **nominal** 276-object split:

- C3 vs fixed-high: FG-PSNR `+1.123 dB`, FG-SSIM `+0.0924`, Edge-SSIM `-0.0034`.
- C3 vs fixed-low: FG-PSNR `-0.211 dB`, FG-SSIM `-0.0003` with a CI crossing zero, Full SSIM `+0.0047`, Full LPIPS improvement `+0.0037` after direction normalization.
- C3 vs no-adapter: Full PSNR `+6.089 dB`, Full SSIM `+0.1325`, FG-PSNR `+1.039 dB`, but FG-SSIM `-0.0511`.

These results support a trade-off interpretation, not a claim that C3 is uniformly optimal. In particular, C3 improves global/full-image fidelity and is substantially better than fixed-high on foreground metrics, while its advantage over fixed-low is mixed and its foreground SSIM is not improved.

## Texture fidelity audit

GT-relative errors use `abs(log((generated_stat+1e-6)/(GT_stat+1e-6)))`; lower is better. On the nominal 276 split:

| condition | RGB-Std error | Gradient error | Laplacian error | HF-energy error |
|---|---:|---:|---:|---:|
| no-adapter | 0.9267 | 0.5965 | 0.9062 | 0.1247 |
| fixed-low | 0.7859 | 0.3267 | 0.7943 | 0.2064 |
| fixed-high | 0.8324 | 0.3128 | 0.6741 | 0.2997 |
| C3 | 0.7360 | 0.3097 | 0.7801 | 0.2248 |

C3 improves three GT-relative variation errors versus no-adapter but worsens HF-energy error. Variation diagnostics and reference-based texture fidelity are therefore not interchangeable. DISTS and CIEDE2000 are not present in the original per-object CSV and are not installed/available in the current main-evaluation environment.

## Camera and unseen-view audit

The dataset contains 17 camera roles. The six target views are `[0,15,12,16,13,14]`. The historical loader selects reference view `000` or `014` using the alpha-count orientation rule; the selected reference view is included in the six target views. Consequently only **five of the six target views** are unseen relative to the reference input. The other 11 of the 17 cameras are not evaluated. Any statement claiming 11 unseen views is unsupported by this protocol.

## 3D baking status

The current nominal holdout contains 43 objects with an existing raw Objaverse GLB, complete 17-view render assets, and usable UVs. All 43 are in the training-list overlap. The existing legacy baking helper also uses canonical azimuth/elevation cameras and re-unwraps UVs, so it cannot be used unchanged for the requested same-UV, actual-pose bake.

Formal independent-holdout baking is therefore **BLOCKED** pending a disjoint training/evaluation artifact or an explicit decision to treat the selected objects as descriptive training-overlap cases.

## Claim audit

| Prior claim | Audit status |
|---|---|
| Old `+0.96 dB` | NOT SUPPORTED by this controlled rerun |
| Comparable FG-SSIM | NOT SUPPORTED; C3 vs fixed-high improves it, but C3 vs fixed-low is approximately flat/slightly negative |
| Does not sacrifice structure | NOT SUPPORTED as a blanket claim; Edge-SSIM is lower than fixed-high |
| Completely preserves texture | NOT SUPPORTED; HF-energy error worsens |
| C3 is better than fixed-low/high on all metrics | NOT SUPPORTED |

