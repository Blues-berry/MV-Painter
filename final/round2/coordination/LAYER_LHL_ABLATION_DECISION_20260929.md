# Shared-input layer-wise ablation decision

## Protocol

The development ablation used 24 clean-v2 probe objects, three seeds (42, 43,
44), six unique views `[0, 15, 12, 16, 13, 14]`, 50 Euler steps, and the same
checkpoint as the strict holdout. Each object was collated once per seed. All
six methods reused the same batch, GeoTex features, and initial latent; the
generation seed was reset before each method so the condition-VAE sampling
path was paired. Shared target, geo-input, geo-feature, and initial-latent
hashes are in `shared_input_hashes.json`.

Methods were:

- `fixed_low`: global 1.25;
- `c3_lhl`: global `[1.25, 2.50, 1.25]`;
- `layer_fixed_low`: deep/middle 1.25, shallow 0.50;
- `layer_fixed_mean`: deep/middle 1.65, shallow 0.58, the exact 17/16/17
  means of layer-LHL;
- `layer_lhl`: deep/middle `[1.25, 2.50, 1.25]`, shallow `[0.50, 0.75, 0.50]`;
- `layer_llh`: deep/middle `[1.25, 1.25, 2.50]`, shallow
  `[0.50, 0.50, 0.75]`.

The shallow implementation cap is 0.8; no layer-LHL value exceeds it.

## Frozen 72-pair summary

Means over 24 objects and three seeds are shown below. The primary metric was
FG-LPIPS; lower is better.

| method | Full PSNR | Full LPIPS | FG PSNR | FG-SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---:|---:|---:|---:|---:|
| fixed-low | 15.085 | 0.2922 | 8.125 | 0.3454 | 0.2195 | 0.4896 |
| C3/LHL | 16.058 | 0.2748 | 9.556 | 0.3929 | 0.2072 | 0.5063 |
| layer-fixed-low | 16.861 | 0.3501 | 10.753 | 0.4249 | 0.1964 | 0.5238 |
| layer-fixed-mean | 16.892 | 0.2796 | 11.179 | 0.4352 | **0.1889** | 0.5287 |
| layer-LHL | 17.036 | 0.3143 | 11.209 | 0.4352 | 0.1928 | 0.5239 |
| layer-LLH | **18.165** | **0.2562** | **12.364** | **0.4467** | **0.1785** | **0.5438** |

Layer-LHL versus fixed-low has paired 95% bootstrap improvements of +1.951 dB
Full-PSNR, +3.083 dB FG-PSNR, +0.0899 FG-SSIM, and −0.0267 FG-LPIPS. These
gains support layer-wise control. They do not identify layer-LHL as the best
layer-wise schedule: layer-fixed-mean is better on FG-LPIPS, and layer-LLH is
better than layer-LHL on all seven reported metrics in this development
protocol. The layer-LHL minus layer-fixed-mean FG-LPIPS difference is +0.00388
with 95% CI `[+0.00273,+0.00518]`; layer-LLH minus layer-LHL is −0.01436 with
95% CI `[-0.01642,-0.01224]`.

## Decision

The paper contribution is narrowed to **layer-wise adapter scaling with
schedule-dependent trade-offs**. Layer-LHL is retained as the originally
motivated representative schedule and as the existing strict-276 result, but
is not called globally optimal. The new 24×3 evidence must be reported as a
development ablation, not as an independent holdout confirmation. Layer-LLH
is a direct counterexample and may be mentioned as a stronger development
control; no schedule selector or universal temporal optimum is claimed.

No second-backbone layer-wise experiment or new baking run is promoted until
the paper revision makes clear that the current evidence supports inference
control at the adapter-layer level, with temporal placement still empirical.

Raw CSVs, manifests, hashes, and the machine-readable summary are stored in
this directory. Temporary prediction PNGs remain under
`/4T/tmp/mvpainter-layer-lhl-ablation/` and are indexed by the seed manifests.
