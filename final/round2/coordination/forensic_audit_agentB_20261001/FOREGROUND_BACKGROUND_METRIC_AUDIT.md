# FOREGROUND_BACKGROUND_METRIC_AUDIT.md (Phase 2 trigger 4 — agent B)

Trigger: "No Adapter FG-PSNR higher than some adapter conditions but
Full-PSNR lower" — real trade-off or mask/background/metric artifact?

## 1. The paradox exists only in the uncapped panel

In tab:strict276 (uncapped legacy regime — see
`CROSS_RUNNER_SCALE_SEMANTICS_AUDIT.md`): no_adapter FG-PSNR 8.776 exceeds
fixed_low 7.030 and fixed_high 5.410 while its Full-PSNR (10.514) is lowest.

Under the capped frozen protocol (same runner family, Core-7 + confirmation +
r0_completion) the paradox disappears:

| condition | FG-PSNR | Full-PSNR | BG-PSNR | FG-SSIM | Full-SSIM |
|---|---:|---:|---:|---:|---:|
| no_adapter | 8.826 | 10.563 | 11.009 | **0.480** | 0.728 |
| global_fixed_low | 10.731 | 18.229 | 25.008 | 0.399 | 0.844 |
| global_c3 | 11.939 | 18.968 | 24.172 | 0.430 | 0.851 |
| global_fixed_high | 13.153 | 18.242 | 20.578 | 0.478 | 0.850 |
| layer_llh | 13.975 | 20.799 | 25.787 | 0.461 | 0.851 |

(R1-realization values for GFL/C3/LLH from the robustness CSV; no_adapter/GFH
from Core-7 — realization drift ≈0.03 dB, cross-verified.)

## 2. Decomposition of the (real) no-adapter signature

1. **Background collapse is real, not a mask artifact**: no_adapter BG-PSNR
   11.0 dB vs 20–26 dB for all adapter conditions. Without geometry control
   the non-foreground region drifts from the (near-white) GT background. This
   alone accounts for the Full-PSNR collapse (Full−FG gap ≈ 1.7 dB for
   no_adapter vs ≈ 7.3–7.5 dB for adapter conditions). The mask itself was
   audited (clean-v2 raw audit: GT reconstruction MAE 2.19e-4; mask from RGBA
   alpha; no camera/view mismatch) — `MAIN_ADAPTER_CLEAN_V2_FINAL_AUDIT.md`.
2. **The FG-SSIM first place is a blur pseudo-advantage**: no_adapter has the
   lowest gradient energy (0.89× GT — undershoot/blur). Blur inflates SSIM
   against locally smooth GT regions while destroying PSNR; the same effect
   makes no_adapter FG-SSIM (0.480) competitive with GFH (0.478) despite
   4.3 dB FG-PSNR deficit. Documented in the Core-7 report; retained here as
   the honest residue.
3. Under caps, fixed_high's FG advantage over fixed_low (+2.42 dB) with a
   modest BG cost (20.6 vs 25.0) is a coherent reallocation signature, not a
   normalization artifact.

## 3. Verdict

`VALIDATED` — the metric suite (FG/Full/BG decomposition, alpha-derived
masks, audited GT compositing) behaves correctly; the published FG/Full
inversion for No-Adapter is an uncapped-regime artifact that the revision
window should replace with the capped table above. No mask or alpha-
normalization bug was found.
