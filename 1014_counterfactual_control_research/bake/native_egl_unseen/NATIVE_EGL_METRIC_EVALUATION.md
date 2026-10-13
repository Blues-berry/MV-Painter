# Fresh C native GLB EGL: exploratory unseen-view metrics

6 objects × 11 unseen views × 4 methods; metrics were averaged over views within each object.

The EGL shader samples the exported GLB baseColor texture using the embedded glTF sampler. The render is unlit and texture-only; results do not claim full PBR fidelity.

| Method | FG-PSNR ↑ | FG-SSIM ↑ | Edge-SSIM ↑ | FG-LPIPS ↓ | CIEDE2000 ↓ | Silhouette IoU ↑ |
|---|---:|---:|---:|---:|---:|---:|
| gt | 21.9537 | 0.7278 | 0.7372 | 0.0701 | 4.8541 | 0.9986 |
| counterfactual_b0 | 12.7028 | 0.4221 | 0.5644 | 0.1413 | 22.0080 | 0.9986 |
| counterfactual_bplus | 12.7160 | 0.4223 | 0.5647 | 0.1412 | 21.9751 | 0.9986 |
| counterfactual_bminus | 12.6967 | 0.4223 | 0.5639 | 0.1413 | 22.0189 | 0.9986 |

LPIPS status: `available` on `cuda:0`. Detailed per-object paired contrasts and render/depth hashes are in `NATIVE_EGL_METRIC_EVALUATION.json`.
