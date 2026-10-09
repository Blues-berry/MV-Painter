# Failure cases and negative results

## C1 visual gate failures

- **Original Fig. 4 row 1 — `eac4b392b7b448a2b6ec77e8936abe1b`.** Applied offset: Δa* +1.974, Δb* −0.572. The unseen-view mean ΔCIEDE2000 is only −0.146 in the manual review summary; at native PNG resolution the candidate is nearly indistinguishable from GFL. No clear visible cast reduction was observed. GFL SHA-256 `e09d983d72d70dc8582118b080b1ffa96de71f0cd6fd5fedd89eb1e7e2a6c78e`; candidate SHA-256 `6df7dab535c5a98f9c7a0287d1070fea5cd7c939c5d3dff23bdcb2067faa7db8`.
- **Original Fig. 4 row 2 — `ea7601dbeb2c46188571cb86e8fdb5bf`.** The applied offset clipped at Δa*=−6, Δb*=−6. The output became somewhat cooler but retained substantial brown-versus-GT mismatch and developed faint cyan/blue silhouette rims. GFL SHA-256 `9418637e06726a79d3d373869050f72917118ffa3e9a6ff3436012defdcdd923`; candidate SHA-256 `7c7a64e3981a8bcb99f0997bd03bf1b816fbe9b4c9b2de067c6b37dd6a2a789a`.

The normal-color and high-texture development objects did not show obvious detail/structure damage or a new cast. Their favorable numeric values do not override the two failure-enriched visual failures. The gate was frozen in `protocol/C1_DEV_METHOD_LOCK.json`; outcome and the no-holdout decision are in `C_REPAIR_METHOD_LOCK.json`.

## B2 raw selected-source embedding gate failure

Replacing the cached feature with the two-encoder embedding of the official raw selected source RGB changed only the global appearance feature. All eight calls completed with paired condition, geometry, initial latent, VAE posterior and RNG hashes matching. The five-view object-level FG-CIEDE2000 deltas were +0.0773 (Fig. 4 row 1), +0.0068 (Fig. 4 row 2), +0.9058 (normal) and −0.2982 (high texture): 1/4 wins and +0.1729 mean, with 95% object-bootstrap CI [−0.2044, +0.6810]. This fails the frozen requirement of at least 3/4 wins and mean ≤−1.0. The Fig. 4 casebook shows no clear visual reduction in either mismatch. Fresh B remained sealed.

The remaining metrics did not show a large aggregate detail regression: mean ΔFG-PSNR −0.0708 dB (95% CI [−0.1894, +0.0478]), mean ΔFG-LPIPS +0.000965 (95% CI [−0.000031, +0.001949]), and mean foreground L* SSIM-to-GT change +0.00349 (95% CI [−0.00477, +0.00952]). These do not compensate for the absent color improvement. Full paired rows, object values and PNG hashes are in `B2_RAW_SOURCE_EMBEDDING_PAIRED_RESULTS.csv` and `runs/phase_b2_raw_source_embedding_attempt_04/B2_RAW_SOURCE_EMBEDDING_RESULTS.csv`; the reconstructed GT/mask identity chain is in `B2_METRIC_INPUT_RECONSTRUCTION.json`.

## Causal interpretation limits

- The global embedding path controls output chroma, but response is not repair: color movement can increase or decrease GT error.
- The transformed-condition refresh changed the two failure cases in opposite GT-relative directions. The B2 raw selected-source embedding replacement produced only 1/4 unseen-view color wins and no clear Fig. 4 visual correction. Cache mismatch remains a provenance defect and possible contributor, not a sufficient color fix.
- No Adapter is much worse than GFL by unseen CIEDE2000 on the four objects (+20.067 mean), but it also changes geometry and lightness substantially. The contrast does not isolate an adapter-specific hue cause.
- LLH is mixed against GFL on color (mean +2.564 CIEDE2000, two wins/two losses) with strong lightness/structure change (mean L* SSIM 0.576). This is not evidence that LLH improves fine texture.
- The frozen magenta-direction statistic is a narrow residual descriptor and is low in some objects with large total color errors.
- No independent validation, C2 generation constraint, or broad Q4 assessment was run after C1 failed its visual gate.

## Next evidence-based route

Do not search thresholds, masks, adapter scales, or time-step schedules. The 150-object input-only audit and the four-object selected-raw-source intervention are now complete; the latter failed its correction gate. The next justified step is a read-only audit of the historical `global_embeds.npy` builder and its view-selection/processor provenance, with zero GPU calls. There is no supported next repair candidate until that audit identifies one concrete implementation error.

Only if a read-only audit finds a specific correction should a new method be pre-registered. The B2 measured rate is 77.3 s / 8 = 9.67 s per call: an eight-call development comparison would be about 77 seconds of sampler time; a strict 300-call independent paired validation would be about 48.3 minutes, plus model startup, preprocessing and artifact review. Those calls are not authorized by the failed B2 gate and have not been run.

Until such a mechanism produces an obvious correction without edge artifacts, retain C1 as a negative result and report the current limitation.
