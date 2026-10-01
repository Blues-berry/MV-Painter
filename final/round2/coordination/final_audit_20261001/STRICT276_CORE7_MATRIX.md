# Strict-276 Core-7 Same-Runner Matrix — Audit Record (final_audit_20261001, Phase 5)

Date: 2026-10-01. The Core-7 completion runs were executed by the parallel task
(`scripts/run_core7_completion_276_20261001.py`, protocol
`core7_same_runner_completion_20261001/PROTOCOL_LOCK_CORE7_COMPLETION.md`, frozen before
any observation). Per the no-duplication decision, this audit does **not** rerun the
experiment; it independently verifies the delivered numbers against the per-object CSVs
and certifies the pipeline-identity gates.

## 1. Pipeline-identity verification (the reviewer concern being closed)

Concern: "the layer schedules come from a different pipeline than the baselines."

Evidence chain, verified this audit:

1. The Core-7 runner's per-object-per-method code path is a **verbatim copy** of the
   frozen `run_layer_confirmation_20260930.py` (protocol `layer-confirmation-strict276-v1`,
   R0 namespace `object_seed = 42 + idx`, latent seed 42, same config/checkpoint/object
   list/metrics). Runner SHA recorded in `FINAL_REPRODUCIBILITY_MANIFEST.json`.
2. Preflight GFL anchor: **bit-exact** vs the frozen R0 rows (their PASS-a gate).
3. Post-hoc cross-process shared-input hash audit: 0/276 mismatches
   (`SHARED_INPUT_AUDIT_CORE7.json`).
4. Independent recompute of condition means from the per-object CSVs (frozen
   confirmation rows for GFL/LLH; formal CSVs for no_adapter/GFH):

| condition | recomputed FG-PSNR | report value |
|---|---:|---:|
| global_fixed_low (R0) | 10.731 | 10.731 |
| layer_llh (R0) | 13.975 | 13.975 |
| no_adapter | 8.826 | 8.826 |
| global_fixed_high | 13.153 | 13.153 |

5. Independent recompute of the primary paired comparison (LLH − no_adapter, FG-PSNR,
   10k object-level percentile bootstrap, seed 20260930): **+5.1490 [4.8974, 5.3958]** —
   matches the delivered +5.149 [+4.896, +5.396].

Verdict: the delivered Core-7 matrix is **verified**; the "different pipeline" confound
is closed.

## 2. The Core-7 matrix (delivered; FG-PSNR / FG-LPIPS / Full-PSNR shown)

| condition | FG-PSNR | FG-LPIPS | Full-PSNR |
|---|---:|---:|---:|
| no_adapter | 8.826 | 0.2059 | 10.563 |
| global_fixed_low | 10.731 | 0.1917 | 18.229 |
| global_fixed_high | 13.153 | 0.1677 | 18.242 |
| global_c3 | 11.939 | 0.1817 | 18.968 |
| layer_fixed_mean | 13.100 | 0.1698 | 19.516 |
| layer_lhl | 12.974 | 0.1719 | 19.635 |
| **layer_llh** | **13.975** | **0.1610** | **20.828** |

Full 7-metric table, rankings and all paired bootstraps:
`core7_same_runner_completion_20261001/{aggregate_metrics_core7.csv, core7_rankings.json,
paired_bootstrap_core7.json, CORE7_SAME_RUNNER_REPORT.md}`.

## 3. What this closes, and the honest residue

- Closes: LLH dominates both Reviewer-facing baselines (unmodified pipeline
  no_adapter; competitive global_fixed_high) on the primary fidelity metrics **under
  the identical runner/seed/realization/shared-input protocol** — no cross-runner
  comparison is needed anywhere in the baseline family.
- Honest residue (delivered verbatim by the run): FG-SSIM ranks no_adapter first
  (blur artifact — lowest FG gradient energy of all seven); global_fixed_high leads
  Full-LPIPS by +0.002 and Edge-SSIM by +0.006 over LLH.
- Mechanism note (from the delivered report): mean FG gradient magnitude vs GT —
  no_adapter 0.89× (undershoot), global_fixed_low 1.54× (overshoot), layer_llh 1.13×
  (closest). One calibration mechanism explains the texture-error advantage, the
  fixed-low overshoot, and the SSIM reversal simultaneously.
- Realization cross-check: R0 vs R1 GFL means differ by 0.027 dB (10.731 vs 10.704),
  consistent with the mean-neutrality quantified in `ARCHIVED_LHL_PROVENANCE_AUDIT.md`.
