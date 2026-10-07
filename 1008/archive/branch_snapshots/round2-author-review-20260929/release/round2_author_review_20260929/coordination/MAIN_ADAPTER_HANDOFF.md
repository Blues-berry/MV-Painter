# Main Adapter v1 — Round 2 Handoff

This handoff is for downstream manuscript integration. It does not modify the manuscript or response letter.

## Status

**PARTIALLY VERIFIED / HOLDOUT INDEPENDENCE BLOCKED**

The controlled v1 checkpoint loads and evaluates correctly under the unique-six protocol. The original checkpoint was not recovered. The current 1,118-object historical training list overlaps the current evaluation UIDs: 101 objects overall and 79 of the nominal 276-object holdout. Thus the nominal holdout tables must not be described as independent unseen-object generalization.

## Safe evidence to use

- 1,200 complete object-condition rows in `mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6/per_object_metrics.csv`.
- Fixed protocol manifest: 256×256, Euler 50 steps, seed 42, target views `[0,15,12,16,13,14]`.
- Paired object-level statistics with 10,000 bootstrap resamples and seed 20260928:
  `main_adapter_baking/paired_statistics_c3_vs_baselines.json`.
- Direct LaTeX tables, explicitly labeled nominal rather than independent:
  `main_adapter_baking/main_adapter_nominal_276.tex` and `main_adapter_baking/main_adapter_pooled_300.tex`.
- Full audit: `MAIN_ADAPTER_RESULT_AUDIT.md` and `main_adapter_baking/protocol_audit.json`.

## Recommended scientific reading

C3 is a mixed trade-off configuration. Relative to fixed-high it improves foreground PSNR/SSIM but slightly lowers Edge-SSIM. Relative to fixed-low it improves Full SSIM and Full LPIPS while slightly reducing FG-PSNR and leaving FG-SSIM essentially unresolved. GT-relative texture errors show improvement in RGB-Std, gradient, and Laplacian errors but a worsening HF-energy error. This supports a conditional shape–texture trade-off, not a uniformly superior method.

## Do not claim

- recovery of the original v1 checkpoint;
- an independent strict-holdout result;
- the old `+0.96 dB` value;
- comparable FG-SSIM without qualification;
- no structural sacrifice;
- complete texture preservation;
- C3 superiority on every metric;
- 11 unseen cameras;
- independent 3D baking evidence from the current nominal holdout.

## 3D baking

No formal baking result is handed off as independent evidence. The available raw-GLB/UV candidates in the nominal holdout all overlap training. The existing legacy bake helper is not protocol-safe because it uses canonical cameras and re-unwraps UVs. A future bake must preserve original UVs, use the stored camera poses, and label any current-object result as training-overlap/descriptive unless a disjoint artifact is supplied.

