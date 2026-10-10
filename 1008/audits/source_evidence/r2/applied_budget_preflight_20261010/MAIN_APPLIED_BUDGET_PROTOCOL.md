# GeoTex equal-applied-budget timing study

**Evidence grade: RETROSPECTIVE.** The Fresh C cohort and the native GFL, native GFH, and C3 outcomes have already been observed. This addendum freezes the remaining conditions and analysis before producing any new condition outputs. It cannot be presented as an independent prospective confirmation.

## Question and estimand

On the frozen Fresh C objects and the existing GeoTex checkpoint, does placing the same nominal applied-scale sum in the early, middle, or late denoising steps change object-level foreground PSNR? The primary estimand is the paired object-level contrast:

`Middle-high FG-PSNR − (Early-high FG-PSNR + Late-high FG-PSNR) / 2`.

The primary endpoint is `fg_psnr`. It will not be replaced after examining results. The six-condition descriptive matrix is Fixed Low (`native_gfl`), Fixed High (`native_gfh`), Fixed Applied Mean (`budget_fixed_mean`), Middle-high (`native_gc3`), Early-high (`budget_early16`), and Late-high (`budget_late16`). The three existing condition outputs are reused only after identity and shared-input checks pass; new inference is limited to Fixed Applied Mean, Early-high, and Late-high.

## Frozen controls

- Runner: historical `run_validation_v3_experiment.py`, SHA-256 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
- Checkpoint: `geotex_step_0002000.pt`, SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Config bytes: SHA-256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Frozen cohort: 300 Fresh C UIDs from `1006/data/fresh_c/fresh_c_objects.txt`, SHA-256 `d93881865b6478dd31222a51c7d3ebafe44839fd5e1b76c5eb9605d3f1fdfa58`.
- Cohort manifest: SHA-256 `0f2c50f0bcce6678d578bd7ec4e8931e39606045b1b105ccbdae7546556a3859`.
- Existing six-input per-object hashes are checked across old conditions; the frozen runner checks shared-input equality across conditions for each new object.
- Same EulerDiscreteScheduler, 50 steps, object seed `42 + object_idx`, latent seed 42, unique6 target views, checkpoint, model path, and per-object input batch are retained.

The config uses `../checkpoints/hf_repo`. The historical launcher ran with the original project directory as its working directory, where that path resolves through `/4T/CXY/checkpoints` to the project’s `checkpoints/hf_repo`. The new launcher preserves this working directory and archives the exact config bytes. All 38 Python files in the historical GeoTex/MVPainter source snapshot match the archived release package byte-for-byte; the five omitted files are one unrelated inference helper and four stale rasterizer build copies. The historical run manifest does not contain a cryptographic digest of the 9 GB base-model directory. The launcher records current file sizes and modification times, but equality between historical and new base-model contents is not cryptographically proven; this limit must remain explicit.

## Applied-scale profiles

There are 50 loop steps, indexed 0–49. The unmodified runner uses `progress = step_idx / 49`; the stage function places C3’s middle stage at steps 17–32. Caps are deep 3.0, middle 3.5, and shallow 0.8.

| Profile | High steps | Other steps | Deep/middle applied sum | Shallow applied sum |
|---|---:|---:|---:|---:|
| Fixed Low | none | 1.25 | 62.50 | 40.00 |
| Fixed High | none | 2.50 | 125.00 | 40.00 |
| Fixed Applied Mean | none | 1.65 | 82.50 | 40.00 |
| Early-high | 0–15 | 16–49 low | 82.50 | 40.00 |
| Middle-high / original C3 | 17–32 | all other steps low | 82.50 | 40.00 |
| Late-high | 34–49 | 0–33 low | 82.50 | 40.00 |

All placement profiles request 1.25 on the two boundary steps 16 and 33. Fixed Applied Mean requests 1.65 in all groups; its shallow request is capped to 0.8 at every step. Thus, its applied scale mean is 1.65 for deep/middle and 0.8 for shallow. The 50-step arithmetic is checked by `verify_applied_budget_profiles.py` before launch.

Equal applied-scale sums are only an input-control match. They do not imply equal realized residual norms, accumulated latent effects, or equal effective intervention strength. Per-step residual logs are required and will be summarized separately.

## Analysis plan

Each object is one paired unit; views are not treated as independent observations. For the primary contrast, report the mean, median, 95% percentile paired-bootstrap CI (10,000 resamples; seed 20261010), and proportion of objects with a positive contrast. Also report all three pairwise placement differences for FG-PSNR, FG-LPIPS, FG-SSIM, and Edge-SSIM, with object-level means, medians, 95% paired-bootstrap CIs, and win rates. Apply Holm correction to the 12 secondary pairwise metric comparisons; retain the primary contrast as a single predeclared test. CIEDE2000 is unavailable in the frozen runner output and will be marked unavailable unless a separately frozen, mask-matched image calculation is validated before analyzing new results.

Residual norm curves are descriptive and must include the actual per-step depth-group logs. Any low/medium/high texture-complexity subgroup result is exploratory: define tertiles from ground-truth-only image texture before reading the new condition outputs, show all strata and failures, and do not turn them into an automatic schedule-selection rule.

Keep all valid positive, null, and negative outcomes. Report failed objects and missing outputs; do not replace the cohort. Do not describe this retrospective cohort as an independent confirmation or claim a realized-dose-independent mechanism.

## Run state

No new GPU inference has been started because both GPUs are currently heavily occupied. The guarded launcher refuses to start unless both devices are below 1 GiB allocated and 10% utilization. It writes only below this worktree’s `1010/experiments/` directory.
