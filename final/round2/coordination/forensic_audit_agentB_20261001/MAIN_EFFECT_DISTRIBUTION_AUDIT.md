# MAIN_EFFECT_DISTRIBUTION_AUDIT.md (Phase 1A — agent B)

Trigger: `LARGE_EFFECT_AUDIT` — LLH − GFL FG-PSNR ≈ +3.24 dB is a very large gap;
task doc requires verification that it is not an artifact of a few extreme
objects, a baseline pathology, or metric misuse.

Data: `final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv`
(same-runner strict-276: layer_llh / layer_lhl / layer_fixed_mean / global_fixed_low,
one runner, object_seed=42+idx, latent seed 42). Covariates joined from
`layer_confirmation_20260930/layer_llh_per_object_metrics.csv` (crop_area, GT
texture statistics). Independent recomputation script:
`phase1a_effect_distribution.py`; per-object deltas:
`phase1a_llh_gfl_per_object_deltas.csv`; raw stats: `phase1a_stats.json`.

## Headline distribution (LLH − GFL, benefit-oriented, n=276)

| stat | FG-PSNR Δ (dB) |
|---|---|
| mean | **+3.244** (reproduces the paper-facing +3.244) |
| median | **+3.366** (median ≥ mean → no tail-driven inflation) |
| p10 / p25 / p75 / p90 | −0.465 / +1.417 / +5.422 / +6.443 |
| min / max | −2.634 (obj_0106) / +7.423 (obj_0081) |
| wins / losses / ties | 242 / 34 / 0 (reproduces 242/276) |
| SD | 2.523 |

## Concentration checks (anti "few extreme objects")

| check | value | verdict |
|---|---|---|
| top-5 / top-10 / top-20 / top-28 share of positive Δ mass | 3.8% / 7.6% / 14.8% / 20.4% | no concentration |
| mean Δ excluding top-10 | +3.099 | still large |
| trimmed mean (excl. top & bottom 5%) | +3.324 | ≥ untrimmed mean |

## Win distribution across baseline quality (baseline pathology check)

Objects banded by GFL baseline FG-PSNR quartile:

| band | n | wins | mean Δ | median Δ |
|---|---|---|---|---|
| Q1 (worst baseline) | 69 | 65 (94%) | +4.58 | +5.15 |
| Q2 | 69 | 65 (94%) | +3.48 | +3.33 |
| Q3 | 69 | 59 (86%) | +2.87 | +2.34 |
| Q4 (best baseline) | 69 | 53 (77%) | +2.05 | +1.53 |

- Pearson/Spearman corr(Δ, GFL baseline FG-PSNR) = −0.372 / −0.359.
- corr(Δ, GFL baseline FG-LPIPS) = +0.050 / +0.041 (≈ none).
- Interpretation: gains are **larger where the baseline is worse**, but remain
  clearly positive on the easiest quartile (+2.05 mean, 77% wins). This is the
  normal regression profile of a real improvement, not a "baseline collapsed on a
  few objects" signature.

## Object-dependency of effect size (honest caveat for the paper)

Spearman correlation of Δ with GT-side foreground statistics:

| covariate | Pearson | Spearman |
|---|---|---|
| crop_area (FG coverage) | +0.078 | −0.027 |
| GT FG Laplacian variance | −0.439 | **−0.640** |
| GT FG RGB std | −0.523 | **−0.667** |
| GT FG gradient magnitude | −0.562 | **−0.682** |

Effect size is **object-dependent**: objects with low-variance GT textures gain
more (up to ~7 dB); texture-rich objects gain less. FG coverage itself has no
relationship. The paper may claim a broad mean effect; it must **not** imply a
uniform per-object magnitude, and any "3 dB" statement should stay
population-level.

## Not-driven-by-outliers across other metrics

| metric (benefit-oriented Δ) | mean | median | wins/losses |
|---|---|---|---|
| Full-PSNR (dB) | +2.599 | +2.447 | 249/27 |
| FG-LPIPS | +0.0308 | +0.0277 | 261/15 |
| Full-LPIPS | +0.0119 | +0.0104 | 196/80 (mixed, known) |
| FG-SSIM | +0.0633 | +0.0647 | 252/24 |
| Full-SSIM | +0.0076 | +0.0071 | 245/31 |
| Edge-SSIM | +0.0276 | +0.0210 | 237/39 |

Medians track means everywhere; no metric's mean is carried by a tail.

## Visual-magnitude question (hand-off to Phase 2)

A 3 dB FG-PSNR gap in a regime where absolute FG-PSNR is 8–21 dB is plausibly
visible; whether generation quality visually matches the metric gap is checked
in `VISUAL_FORENSIC_AUDIT.md` using the fixed object sets below (no
aesthetics-based re-picking permitted):

- **top-12 wins**: obj_0081, obj_0066, obj_0051, obj_0100, obj_0063, obj_0101, obj_0091, obj_0099, obj_0076, obj_0067, obj_0110, obj_0064
- **median band** (6 closest to median): obj_0130, obj_0261, obj_0205, obj_0150, obj_0277, obj_0140
- **bottom-12 losses** (Phase 16 failure set): obj_0106, obj_0062, obj_0124, obj_0086, obj_0027, obj_0178, obj_0080, obj_0208, obj_0096, obj_0266, obj_0204, obj_0227

## Verdict

`VALIDATED_WITH_LIMITATIONS` — the +3.24 dB LLH-vs-GFL effect is broad (median
+3.37, top-10 objects carry only 7.6% of the positive mass, trimmed mean
unchanged), monotone across baseline quartiles, and reproduced across metrics.
Limitation to carry into the manuscript: per-object magnitude is strongly
modulated by GT texture complexity (|ρ|≈0.64–0.68); do not present the effect as
uniform.
