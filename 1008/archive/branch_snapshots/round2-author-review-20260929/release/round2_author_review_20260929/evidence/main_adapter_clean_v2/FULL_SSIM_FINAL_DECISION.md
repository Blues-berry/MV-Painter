# Full-SSIM final decision

## Decision status

The root-cause class is established by static code and artifact audit:
Full-SSIM was computed on the pre-save float16 prediction tensor, whereas the
PNG audit computed on an 8-bit PNG reload represented as float32. The frozen
run uses the same logical prediction for metric evaluation and PNG saving; the
problem is not a filename or object-order mismatch and is not an SSIM-library
disagreement. Exact A/B pixel-level attribution remains pending the prepared
12-object CUDA trace because the original tensors were not saved.

No compensation is applied to the recorded A values.

## Unified evaluation path for the frozen artifacts

For a single comparable four-condition Full-SSIM table, use the serialized
prediction artifact as the common input:

- prediction: reload each saved RGB PNG as float32;
- GT: reconstruct the corresponding unique6 3x2 panel from the original RGBA
  source over white, using the frozen camera/view mapping and resize;
- metric: the historical 3x3 SSIM implementation, float32, same 3x2 panel,
  same constants and padding for all four conditions;
- aggregation: identical object-level means and paired bootstrap across all
  conditions.

This is the current raw-PNG audit branch C. It includes the real information
loss of the saved prediction PNG and is reproducible from the delivered files.
It is not an additive correction to A and does not select the representation
because it restores the old C3 advantage.

## Frozen 300-object pooled values under the selected serialized-image path

| condition | recorded A | unified PNG/raw-GT C |
|---|---:|---:|
| no adapter | 0.727334 | 0.764067 |
| fixed low | 0.850439 | 0.881914 |
| fixed high | 0.822611 | 0.857469 |
| C3 | 0.855002 | 0.881327 |

Under C, C3 minus fixed-low is `-0.000587` with 95% CI
`[-0.000984,-0.000188]` and win rate `0.463`; C3 minus fixed-high is
`+0.023858` with 95% CI `[0.021792,0.026008]` and win rate `0.990`.
The complete per-object A/B/C evidence is in
`full_ssim_reconciliation/full_ssim_comparison.csv`.

## Handoff gate

The serialized-image C path is the only currently defensible unified Full-SSIM
path for the already saved 300-object artifacts. However, the formal A/B/C
serialization trace is still pending because the host has no CUDA/NVIDIA
driver. Therefore this decision is recorded for audit and reproducibility, but
the result is not silently substituted into the paper or handed to Codex C as a
new main-table number in this turn. Once the 12-object trace is run on an
assigned GPU, the same unified path remains valid; only the attribution report
will be completed.

