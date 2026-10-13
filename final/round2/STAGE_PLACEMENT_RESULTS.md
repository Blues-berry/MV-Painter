# Stage-placement results

Status: the protocol and CPU dry-run passed; formal fixed-mean/HLL/LLH inference is pending a CUDA resource handoff. This is a prespecified follow-up after clean-v2 inspection, not a blind experiment.

## Existing comparisons on frozen strict holdout

C3 versus fixed-low and fixed-high are complete with 10,000 object-level paired bootstrap resamples. The machine-readable CIs and win rates are in `paired_stage_comparisons.json`.

- C3 vs fixed-low: C3 is lower on Full PSNR and FG PSNR/FG SSIM in the current clean-v2 table, while it has a small Full-SSIM advantage and similar/better FG-LPIPS.
- C3 vs fixed-high: C3 is higher on Full PSNR, FG PSNR and FG SSIM, with essentially tied full/foreground perceptual scores.

## Mechanistic conclusion status

No stage-position conclusion is made until fixed-mean, HLL and LLH are run with the same frozen checkpoint, unique6 cameras, 256×256 targets, seed 42 and 50 steps. The final analysis will compare global, foreground, edge and reference-based texture metrics and will report both paired CIs and win rates.
