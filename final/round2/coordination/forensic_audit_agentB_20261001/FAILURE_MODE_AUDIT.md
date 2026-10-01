# FAILURE_MODE_AUDIT.md (Phase 16 — agent B)

Loss set: the 34/276 objects where layer_llh loses to global_fixed_low on
FG-PSNR in the same-runner strict-276 confirmation (paper-facing "242/276
wins" hides this set; Reviewer 1 will ask). Script:
`phase16_failure_analysis.py`; raw: `phase16_failure_stats.json`; sorted loss
list: `loss_objects_sorted` (worst obj_0106 −2.63 dB … mildest obj_0069
−0.03 dB; obj_0069 is the thin-foreground object already excluded from the
texture-audit panel).

## 1. Are the losses real or realization luck?

| check | result |
|---|---|
| same object also loses at R1 (seed 10042 realization) | **32/34 (94%)** |
| wins that also win at R1 | 239/242 (99%) |
| also loses under layer_lhl vs GFL | **32/34** |
| also loses under layer_fixed_mean vs GFL | **30/34** |

The loss set is **object-intrinsic and schedule-family-intrinsic**, not a
stochastic artifact of one runner/realization and not LLH-specific: essentially
the same objects lose to fixed-low under every layer-wise schedule.

## 2. What kind of objects fail?

| covariate | losses (n=34) | wins (n=242) |
|---|---|---|
| GT FG Laplacian variance | **0.0284** | 0.0099 (2.9× lower) |
| GT FG RGB std | **0.0599** | 0.0293 (2.0× lower) |
| GFL baseline FG-PSNR | 11.96 (easier) | 10.56 |
| crop_area (FG coverage) | 0.925 | 0.949 (no meaningful gap) |

Losses concentrate on **texture-rich objects** (2–3× the GT texture variance
of the average win object) where the fixed-low baseline is already decent —
the same modulation direction found in the Phase-1A correlation analysis
(Spearman ≈ −0.64 to −0.68 vs GT texture statistics).

## 3. Metric signature of a loss

On the 34 loss objects (LLH − GFL):

| metric | mean Δ | also loses |
|---|---|---|
| Full-LPIPS | −0.0118 | **30/34** |
| Full-PSNR | −0.632 | 26/34 |
| Edge-SSIM | −0.0049 | 22/34 |
| FG-SSIM | **+0.0066** | 17/34 (still favors LLH on average) |
| FG-LPIPS | +0.0055 | 12/34 |

## 4. Mechanism proxy (texture-energy accounting)

pred/GT ratios on loss vs win objects (from R1 realization, both methods):

| ratio | losses | wins |
|---|---|---|
| fg_lap_var / GT (LLH) | **0.470** (undershoot) | 1.605 |
| fg_lap_var / GT (GFL) | **1.047** (≈GT) | 4.021 (large overshoot) |
| fg_rgb_std / GT (LLH) | 3.18 | 14.52 |
| fg_rgb_std / GT (GFL) | 3.42 | 14.95 |

Reading: on the failing objects LLH **under-delivers high-frequency texture
energy (0.47× GT)** while fixed-low's constant allocation happens to match GT
energy (1.05×); on typical wins both overshoot, GFL massively. The failure is
therefore a **texture-energy deficit on texture-rich objects under the
late-concentrated schedule**, visible mostly in whole-image perceptual metrics
(Full-LPIPS) and FG-PSNR, while structural FG-SSIM still favors LLH.

## 5. Failure taxonomy status

- Quantitative taxonomy: delivered above (texture-energy deficit class
  dominates; realization-persistent; schedule-family-wide).
- **Visual taxonomy: `ARTIFACT_INSUFFICIENT`** — the formal confirmation and
  Core-7 runs did not archive per-object prediction PNGs (metrics only; only
  isolated preflight images exist), so per-object visual failure classes
  (repeated pattern / color shift / thin-structure failure …) cannot be
  verified from the formal artifacts. Available proxies: dev-24 comparison
  panels (`layer_lhl_v1/obj_*_ablation_comparison.png`), stage-placement
  global-schedule images (different schedules — not the main method), and the
  12-object bake GLBs. If reviewers require visual failure cases, the paper
  must either use dev-set images with an explicit "development-set example"
  label, or a small pre-registered image-export pass would be needed (decision
  gate item, not automatic).

## 6. Recommended paper sentence (width-tested)

"LLH wins on 242/276 objects; the 34 losses are realization-persistent
(32/34) and concentrate on objects with 2–3× higher ground-truth texture
variance, where the late-concentrated schedule under-delivers high-frequency
texture energy relative to fixed-low (Laplacian-variance ratio 0.47× GT vs
1.05×); on these objects FG-SSIM still favors LLH while Full-LPIPS and
FG-PSNR favor fixed-low."

This is honest, reviewer-1-aligned, and fully backed by archived per-object
artifacts.
