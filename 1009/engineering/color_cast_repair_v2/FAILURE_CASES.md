# Failure cases and negative results

## C1 visual gate failures

- **Original Fig. 4 row 1 — `eac4b392b7b448a2b6ec77e8936abe1b`.** Applied offset: Δa* +1.974, Δb* −0.572. The unseen-view mean ΔCIEDE2000 is only −0.146 in the manual review summary; at native PNG resolution the candidate is nearly indistinguishable from GFL. No clear visible cast reduction was observed. GFL SHA-256 `e09d983d72d70dc8582118b080b1ffa96de71f0cd6fd5fedd89eb1e7e2a6c78e`; candidate SHA-256 `6df7dab535c5a98f9c7a0287d1070fea5cd7c939c5d3dff23bdcb2067faa7db8`.
- **Original Fig. 4 row 2 — `ea7601dbeb2c46188571cb86e8fdb5bf`.** The applied offset clipped at Δa*=−6, Δb*=−6. The output became somewhat cooler but retained substantial brown-versus-GT mismatch and developed faint cyan/blue silhouette rims. GFL SHA-256 `9418637e06726a79d3d373869050f72917118ffa3e9a6ff3436012defdcdd923`; candidate SHA-256 `7c7a64e3981a8bcb99f0997bd03bf1b816fbe9b4c9b2de067c6b37dd6a2a789a`.

The normal-color and high-texture development objects did not show obvious detail/structure damage or a new cast. Their favorable numeric values do not override the two failure-enriched visual failures. The gate was frozen in `protocol/C1_DEV_METHOD_LOCK.json`; outcome and the no-holdout decision are in `C_REPAIR_METHOD_LOCK.json`.

## Causal interpretation limits

- The global embedding path controls output chroma, but response is not repair: color movement can increase or decrease GT error.
- The cached/current embedding discrepancy changes two failure cases in opposite directions and leaves two other development outputs pixel-identical. It is not a consistent fix.
- No Adapter is much worse than GFL by unseen CIEDE2000 on the four objects (+20.067 mean), but it also changes geometry and lightness substantially. The contrast does not isolate an adapter-specific hue cause.
- LLH is mixed against GFL on color (mean +2.564 CIEDE2000, two wins/two losses) with strong lightness/structure change (mean L* SSIM 0.576). This is not evidence that LLH improves fine texture.
- The frozen magenta-direction statistic is a narrow residual descriptor and is low in some objects with large total color errors.
- No independent validation, C2 generation constraint, or broad Q4 assessment was run after C1 failed its visual gate.

## Next evidence-based route

Do not search thresholds, masks, or adapter scales. The next useful experiment would require a newly justified mechanism that directly addresses the observed source/cache provenance issue, with a fresh pre-outcome method lock and a visual gate on failure-enriched development cases before any holdout access. Until such a mechanism produces an obvious correction without edge artifacts, retain this candidate as a negative result and report the current limitation.
