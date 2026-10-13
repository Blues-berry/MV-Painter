# R0_R1_OUTPUT_SENSITIVITY_AUDIT.md (Phase 7 — agent B)

Question (task doc): conditioning changes substantially between realizations
(cond SSIM ≈ 0.93, cond-latent cosine ≈ 0.94, L2 diff ≈ 35 % of norm) yet
aggregate metrics drift only ≈ 0.03 dB. Is that *true robustness*, or is the
conditioning path not actually reaching the forward pass?

Method: offline only, no regeneration.
(a) Image-level comparison of the four available R0-vs-R1 PNG pairs
(`r0_anchor_llh_10/`, `r0_completion_global_c3/` = re-executed R0 protocol
images vs `realization1_core5/` R1 images). (b) Per-object metric drift over
all 276 objects, R0 (seed 42, confirmation artifacts) vs R1 (seed 10042,
robustness artifacts). Script: `phase7_r0r1_sensitivity.py`; raw:
`phase7_r0r1_sensitivity.json`.

## 1. Image-level R0 vs R1

| pair | MAE ([0,1]) | PSNR | identical bytes? |
|---|---|---|---|
| layer_llh obj_0024 | 0.00168 | 46.6 dB | no |
| layer_llh obj_0025 | 0.00117 | 48.5 dB | no |
| global_c3 obj_0024 | 0.00152 | 47.1 dB | no |
| global_c3 obj_0025 | 0.00143 | 43.7 dB | no |

**Outputs are not identical** — all four SHA-256 hashes differ, so the changed
conditioning demonstrably flows through the network. But the outputs are
extremely self-similar: 43.7–48.5 dB, i.e. the realization perturbation moves
outputs ~30–38 dB less (in MSE terms) than the LLH-vs-GFL schedule effect
(+3.24 dB at FG-PSNR against GT).

## 2. Per-object metric drift, R0 → R1 (n = 276 each)

| schedule | median \|ΔFG-PSNR\| | p90 | max | mean signed | median \|ΔFG-LPIPS\| |
|---|---|---|---|---|---|
| layer_llh | 0.076 dB | 0.359 | 1.304 | −0.038 | 0.0007 |
| layer_lhl | 0.063 | 0.318 | 1.396 | −0.029 | 0.0008 |
| layer_fixed_mean | 0.068 | 0.345 | 1.738 | −0.030 | 0.0008 |
| global_fixed_low | 0.088 | 0.392 | 1.484 | −0.026 | 0.0008 |

All four schedules drift by the same small magnitude (median 0.06–0.09 dB,
mean signed ≈ −0.03 dB, reproducing the reported ≈0.03 dB), so the *ranking*
is untouched; individual objects can move up to ~1.3–1.7 dB, i.e. the drift is
broad and directionless rather than concentrated. Because all paper-facing
schedule comparisons are paired within one runner on one frozen realization,
this drift cannot inflate between-schedule deltas.

## 3. Diagnosis

`VALIDATED` — **genuine population-level robustness, not a dropped
conditioning path.** The conditioning change is large (median cosine 0.940,
median L2 diff 456 on a norm of ~1,319 — from
`REFERENCE_REALIZATION_DIFFERENCE_summary.json`), the outputs do change
 measurably, yet remain ~45 dB self-similar with ≤0.09 dB median metric drift.

Scope caveat (do not over-read): this audit bounds sensitivity to
**realization-scale perturbations of a valid reference**; it does not measure
the importance of the reference pathway itself. The premise that conditioning
dominates generation rests on the paper's reference-based evidence (structured
textures following the reference), not on this test.

## 4. Notes for the manuscript

- Safe sentence: "outputs remain self-similar at ≈45 dB PSNR under a
  realization change that alters the conditioning latent by ~35 % in L2;
  per-object metric drift has a median ≤0.09 dB and no schedule-dependent
  direction."
- The four image pairs are archived with hashes in `phase7_r0r1_sensitivity.json`
  so reviewers can re-verify without regeneration.
