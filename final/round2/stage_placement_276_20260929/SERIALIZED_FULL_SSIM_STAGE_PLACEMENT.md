# Serialized Full-SSIM stage-placement audit

This CPU-only post-processing pass recomputes Full-SSIM from the frozen PNG predictions, reloaded as float32, against the original RGBA/white-background float32 GT. The formal pre-save metric CSV remains unchanged; this file is the saved-artifact Full-SSIM branch.

- Objects: 276
- Schedules: fixed_mean, hll, llh, c3_lhl
- Bootstrap: 10,000 object-level paired resamples, seed 20260928
- No checkpoint, dataset, prediction PNG, or paper source was modified.
