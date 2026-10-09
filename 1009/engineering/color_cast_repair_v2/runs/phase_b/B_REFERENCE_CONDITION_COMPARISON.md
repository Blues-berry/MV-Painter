# Phase B reference-condition comparison

Object-paired analysis of the four locked development objects; each unseen-view value equally averages five views.
The RGB difference is a descriptive full-grid uint8 comparison against the same object's GFL PNG, not a GT quality metric.
No Fresh B prediction or repair metric is read.

| Condition vs GFL | Mean unseen ΔCIEDE2000 | Object wins / losses | Mean unseen L* SSIM vs GFL | Mean RGB MAE |
|---|---:|---:|---:|---:|
| gfl_baseline | +0.000 | 0 / 0 | 1.000 | 0.000 |
| global_embedding_recomputed | -0.021 | 1 / 1 | 0.957 | 0.938 |
| no_adapter | +20.067 | 0 / 4 | 0.193 | 51.328 |
| layer_llh | +2.564 | 2 / 2 | 0.576 | 11.980 |

## Interpretation limits

No Adapter has a large CIEDE2000 penalty relative to GFL on these four objects, but its geometry is substantially different; this does not isolate a pure adapter-induced color cast.
LLH changes lightness/structure strongly and has mixed object-level color effects. These locked readouts do not establish a fine-detail benefit.
Recomputing the global embedding changes the two Fig. 4 failure outputs in opposite GT-relative directions, while the two Fresh C development outputs are pixel-identical to GFL. This shows the cached-vs-current embedding can causally affect failure outputs, but the effect is not a consistent correction.

Source CSV SHA-256: `2544445cf181f425f1bd4d049404b185790182d8289915a4a430cddb68fc26c5`.
