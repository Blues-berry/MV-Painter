# E6 cap calibration: development stop record

This small evidence bundle preserves the 1006 branch's decision to stop the E6 calibration candidate. The original archive remains the full source of branch history; this selection carries only the machine diagnostic and its post-development method review.

## Source and interpretation

- Original branch tip: `34d15cab5f2d4312d75e6921efb60eaad62c53c2` (WIP snapshot); pre-WIP source: `a9ac1459b3d6d4312dab8dbd17534403133fb922`.
- Archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/paper-1006-20261006`.
- The source review describes 24 development objects, three seeds, and four conditions (288 fixed quality rows). It retained the original selected multiplier 1.25 and explicitly says there was no independent confirmation.
- The selected development candidate's foreground mean changes were FG-PSNR +5.452684 dB and FG-LPIPS −0.069220. The reported whole-image LPIPS mean change was +0.196705 (unfavorable), with all 24/24 objects moving in the unfavorable direction. Full-PSNR (+3.139129 dB) and full-SSIM (+0.004145) are preserved as separate endpoints; they do not cancel the LPIPS tradeoff.
- Shallow reads saturated 5,618/10,800 times (52.02%). The source also limits timing interpretation and says peak GPU memory was not recorded.

This is a development-stage descriptive stop decision, not independent confirmation, a confirmatory test, or a result to add to the active paper. It does not authorize a Fresh D run. No raw experiment data, per-object result table, images, checkpoints, embeddings, cache, PDF, or generated figure is included here; the original data and historical worktree were left in place.

## Byte identity of selected source files

- `E6_COMPLETE_DEVELOPMENT_DIAGNOSTIC_20261006.json`: SHA-256 `4061c74ff61051e1d91a376b630a679fa6cba398758bd66f7f9735fc05b4659c`.
- `E6_POST_DEVELOPMENT_METHOD_REVIEW_20261006_ZH.md`: SHA-256 `f9091d5884a1adec2ce745d0add65a51e5d7d21d1a8535423e8b368791475656`.

No active manuscript, supplement, response, figure, or submission-package file was changed. `SUBMISSION_APPROVED=NO`.
