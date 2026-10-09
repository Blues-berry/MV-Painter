# C — Color-failure mechanism evidence and boundary

## Finding

`COLOR_CONDITION_CAUSE_IDENTIFIED = PARTIAL`. The new input-chain audit finds no wrong-object condition, stale embedding, changed encoder asset or condition-tensor mismatch. The available model receives one selected appearance view and an object-level global embedding while producing six distinct target views. That leaves a plausible information limit for per-view color, but the evidence does not prove it is the unique source of any observed shift. No specific color-generation bug or complete causal mechanism is identified.

## Same-input No Adapter / GFL / LLH evidence

The Fresh C No Adapter/GFL probe uses the exact frozen `no_adapter` and `native_gfl` predictions from `c3_confirmation`. Every object has the same UID, object index, seed, target, condition, normal, depth, global embedding and initial-latent hashes; both RGB files match the original output SHA manifest. The LLH addendum also matches those six inputs per object. All three conditions therefore form a valid same-input control on 300 objects.

| Fresh C contrast | Mean paired delta [95% CI] | Favorable objects |
|---|---:|---:|
| GFL − No Adapter, FG-CIEDE2000 | `−11.228` [−12.929, −9.540] | 227/300 lower |
| GFL − No Adapter, FG-PSNR | `+4.330 dB` [+3.958, +4.689] | 259/300 higher |
| GFL − No Adapter, FG-LPIPS | `−0.02370` [−0.02860, −0.01882] | 210/300 lower |
| GFL − No Adapter, GT-relative Laplacian error | `+0.01876` [+0.01636, +0.02122] | 61/300 lower |
| GFL − No Adapter, absolute mean Δa* magnitude | `+2.389` [+1.747, +3.002] | 79/300 lower |
| GFL − No Adapter, absolute mean Δb* magnitude | `+1.199` [+0.500, +1.884] | 109/300 lower |

The main color distance and signed channel summaries do not tell the same story: adapter-on GFL has lower mean CIEDE2000, but larger mean absolute a*/b* residuals. CIEDE2000 includes lightness and chroma/hue interactions; neither mean channel shift nor CIEDE alone proves a pixel-wise cause. The correct conclusion is that adding GFL does not systematically increase CIEDE2000 on Fresh C, but color mismatch persists and the adapter changes the error vector.

The older diagnostic-26 RGBs also show lower average CIEDE2000 for GFL than No Adapter (24/26 lower); the two original Fig. 4 examples remained visually pink/purple under No Adapter and adapter conditions. That older contrast is forensically useful but is not an estimate of how often color artifacts occur in the population.

## LLH: average improvement, not a color repair guarantee

On Fresh C 300, LLH−GFL CIEDE2000 is `−2.232` [−3.137, −1.338]; it is lower on 187/300. FG-PSNR is `+1.143 dB` [+0.814, +1.480], FG-LPIPS `−0.01748` [−0.02003, −0.01496], and GT-relative Laplacian error `−0.01786` [−0.01866, −0.01709], lower on 300/300. Fresh B 150 independently shows CIEDE2000 `−1.905` [−3.262, −0.529], FG-PSNR `+1.030 dB` [+0.577, +1.493], FG-LPIPS `−0.01556` [−0.01920, −0.01192], and high-frequency error `−0.01871` [−0.02016, −0.01743].

These are cohort averages. Fresh B's GT-defined Q4 instead has LLH−GFL CIEDE2000 `+3.624` [1.907, 5.303] and FG-PSNR `−0.770 dB` [−1.165, −0.315]. Fresh C's same-fixed-cutpoint Q4 trend is also positive for CIEDE2000 and negative for PSNR, although the diagnostic-overlap-excluded intervals include zero. Thus LLH can improve average RGB agreement while making color/detail fidelity worse on texture-rich objects. The complete endpoint set and per-object deltas are in `A_COHORT_HETEROGENEITY.csv`, `B_OBJECT_LEVEL_RESULTS.csv`, `A_QUARTILE_EFFECTS.csv` and `C_CAUSAL_PROBE_STATISTICS.csv`.

## Where and before what the visible shift occurs

The preceding frozen stage trace found a pink surface in a GFL decode snapshot by scheduler update 40; earlier high-noise snapshots do not support a precise first latent step. The color is already present in generated RGB before texture baking and GLB export. A normal GT VAE encode/decode round trip had foreground CIEDE2000 about `4.09`, compared with `22.03` for the paired reviewed GFL example, and did not reproduce its pink-shift direction. This weakens the claim that ordinary VAE round-trip drift alone explains the generated mismatch; it does not rule out a VAE interaction with generated latents.

The prior trace and VAE controls are documented in `../color_failure/final_closure/COLOR_CAUSAL_DIAGNOSIS.md`, `../color_failure/final_closure/REPRODUCIBILITY_ROOT_CAUSE.md`, and their frozen image/metric tables. No residual/metric correlation is used here as causal evidence.

## What remains unresolved

- The condition pipeline's identity and normalization pass. No code bug is established.
- One source RGB view plus one global feature vector is not six per-view color ground truths. The evidence supports a conditioning-density limitation as plausible, not as a proven unique cause.
- The exact generated color error is relative to a rendered GT, not a calibrated physical-color standard.
- The shared UIDs between old diagnostic-26 and Fresh C have different saved predictions. The newer same-UID group does not reproduce the old positive LLH CIEDE delta, while its `n=20` interval is wide. The prior three-object trace confirms cross-stack output drift can occur but does not resolve every diagnostic object.
- LLH and GFL use different effective layer/time schedules, so neither saved residual magnitude nor the LLH-vs-GFL difference isolates a single adapter layer or denoising stage as a color cause.

The causal evidence therefore does not justify a Gate change, scale retuning, time-step search, GT-conditioned recoloring or a new repair claim. No validated color repair exists in this package.
