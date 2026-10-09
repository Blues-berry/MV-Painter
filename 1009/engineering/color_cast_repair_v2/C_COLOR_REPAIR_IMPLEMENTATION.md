# C1 source-conditioned chroma anchor: implementation and outcome

## Implementation

The frozen post-process estimates a robust componentwise Lab a*/b* offset from the transformed source condition and generated GFL tile 0. It uses pixels with alpha at least 0.75 after three-pixel erosion, requires at least 64 trusted pixels in each region, clips each channel independently to ±6 Lab units, and applies the same offset to each of the six views through the geometry silhouette mask. Zero-mask RGB values are preserved. Candidate PNGs are written to a separate directory; source GFL and LLH PNGs are not overwritten.

The estimator has no target RGB input. GT RGB and target masks are used only after candidate pixels are fixed, for evaluation and the casebook. No source-to-target pixel correspondence, UV reprojection, per-object tuning, or copying of source pixels is used. Implementation SHA-256: `8d2f460509280e9cbe4e22081a47e3ce938f53262bd321d8971be18095572be8`.

## Experiment and evaluation

The only candidate run used four predeclared development objects (the two Fig. 4 failures, one normal-color object, and one high-texture object). It was CPU-only post-processing and made no diffusion calls. `C_REPAIR_PAIRED_RESULTS.csv` contains 24 object/view paired rows with view identity, checkpoint, baseline runner and generation manifest, all relevant input/target/mask/PNG hashes, candidate code/runner/lock hashes, and per-view metrics. `COLOR_REPAIR_VALIDATION.csv` contains the four object-level aggregates across source and five unseen views; its `cohort` column is explicitly `dev`. The bootstrap object-level summary is in `runs/phase_c/dev/COLOR_REPAIR_PAIRED_STATISTICS.md` and `.json`.

Object-paired bootstrap summary (10,000 draws; seed 20261009): five unseen views averaged equally per object. Mean ΔFG-CIEDE2000 was −1.5602 (95% percentile CI [−2.2621, −0.6299], 4/4 objects improved, dz −1.572). Mean ΔFG-PSNR was +0.1805 dB; mean ΔFG-LPIPS −0.00186; mean foreground L* SSIM-to-GT Δ −0.00015. These favorable numeric development results did not pass the separately locked visual failure-case gate.

Visual review found no clear improvement on Fig. 4 row 1 (unseen mean ΔCIEDE2000 −0.146) and a faint cyan/blue silhouette rim with substantial remaining brown-versus-GT mismatch on Fig. 4 row 2. The normal and high-texture cases showed no obvious detail or structure damage. The full four-object reviewed casebook is `C_REPAIR_BEFORE_AFTER.pdf`.

## Decision

`C_REPAIR_METHOD_LOCK.json` records `development_gate_pass=false`, `validation_authorized=false`, and a closed Fresh B holdout guard. No independent Fresh B output or repair metric was opened, and no Fresh B candidate was run. The result is an unvalidated development-only numeric color shift, not a validated repair. No C2 generation-time constraint was attempted because the C1 visual gate failed.

The focused module tests cover byte-exact identity/no-op behavior, zero-alpha preservation, fractional mask-boundary weighting without color bleed, bounded offsets, foreground-only Lab perturbation, and embedding-refresh identity/corruption handling. Final result: 8 passed under Python 3.13.5; `runs/phase_c/test_color_repair_pytest.log` records the run and the corrected assertion from the initial test attempt. No claim of generalization or product integration is supported by four development objects.
