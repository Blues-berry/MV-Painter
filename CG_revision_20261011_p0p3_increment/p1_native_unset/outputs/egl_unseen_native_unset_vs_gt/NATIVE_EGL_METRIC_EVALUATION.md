# Fresh C native GLB EGL: exploratory unseen-view metrics

10 objects × 11 unseen views × 3 methods; metrics were averaged over views within each object.

The EGL shader samples the exported GLB baseColor texture using the embedded glTF sampler. The render is unlit and texture-only; results do not claim full PBR fidelity.

| Method | FG-PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-LPIPS ↓ | CIEDE2000 ↓ | Silhouette IoU ↑ |
|---|---:|---:|---:|---:|---:|---:|
| gt | 22.3761 | 0.7683 | 0.7533 | 0.0590 | 4.4407 | 0.9990 |
| native_unset | 11.1350 | 0.3376 | 0.5356 | 0.1372 | 26.4715 | 0.9990 |
| no_adapter | 5.9192 | 0.3829 | 0.3178 | 0.1600 | 40.9184 | 0.9990 |

LPIPS status: `available` on `cpu`. Detailed per-object paired contrasts and render/depth hashes are in `NATIVE_EGL_METRIC_EVALUATION.json`.
