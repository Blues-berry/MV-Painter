# Phase B color-response intervention

Generation calls: 64; measured sampler wall time: 485.1 s.
The four locked development objects and all 64 conditions use the same checkpoint, geometry, object order, initial latent, scheduler, and posterior RNG seed.

## Shared-factor integrity

All per-object initial-latent, geometry-feature, and pre-posterior RNG hashes agree across conditions: **True**.

## Directional response by appearance channel

| Arm | Axis | Sign | Source pass (objects) | Unseen pass (objects) | Mean unseen aligned response (Lab) |
|---|---|---:|---:|---:|---:|
| vae_only | a* | +1 | 0/4 | 0/4 | 0.100 |
| vae_only | a* | -1 | 0/4 | 0/4 | -0.143 |
| vae_only | b* | +1 | 0/4 | 0/4 | 0.240 |
| vae_only | b* | -1 | 0/4 | 0/4 | 0.017 |
| embedding_only | a* | +1 | 4/4 | 4/4 | 2.733 |
| embedding_only | a* | -1 | 4/4 | 4/4 | 2.234 |
| embedding_only | b* | +1 | 4/4 | 4/4 | 1.611 |
| embedding_only | b* | -1 | 2/4 | 2/4 | 1.570 |
| vae_and_embedding | a* | +1 | 4/4 | 4/4 | 2.939 |
| vae_and_embedding | a* | -1 | 4/4 | 4/4 | 2.160 |
| vae_and_embedding | b* | +1 | 4/4 | 4/4 | 1.879 |
| vae_and_embedding | b* | -1 | 3/4 | 3/4 | 1.594 |

The locked response criterion is shown with the result CSV. A response is evidence of causal color control only; it is not evidence that the shift reduces GT-relative color error.

## Cache-refresh control

Compare `global_embedding_recomputed` against `gfl_baseline` in the paired CSV. It isolates current-condition cache refresh from the color-direction arms and must not be merged with them.
