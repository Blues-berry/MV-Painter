# Controlled Full-SSIM Serialization Trace — 2026-09-29

## Decision

Status: `PASS_WITH_LIMITATIONS` for the controlled same-generation
serialization experiment. The historical 300-object A tensors are still not
recoverable, so the stronger historical attribution remains
`PARTIALLY_CONFIRMED`. The trace does establish the current tensor boundary
under the frozen clean-v2 checkpoint and protocol.

## Frozen protocol

- Checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`
- Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`
- Cohort: fixed 12 diagnostic objects, indices
  `[13,15,38,48,54,66,68,78,82,83,110,111]`
- Conditions: `no_adapter`, `fixed_low`, `fixed_high`, `c3`
- Target views: unique6 `[0,15,12,16,13,14]`; 50 steps; seed 42
- Output: `main_adapter_clean_v2/float_png_trace_12_controlled_20260929/`

## Completeness

- 48/48 object-condition rows are present and finite.
- 168 tensor files are present: GT float/reload pairs and A/B/C tensors for
  all 48 conditions.
- The manifest records `same_generation_for_A_B_C=true` and status
  `completed`.
- A and B are the same pre-save prediction tensor in this controlled run;
  every A/B pixel MAE and maximum error is exactly zero.
- A/B tensors are `torch.float16`; PNG-reloaded C tensors are `torch.float32`.
- B→C pixel MAE is nonzero for all four methods; the observed maximum error
  is approximately one 8-bit quantization step (`0.0022059`).

## Paired Full-SSIM result on the 12-object trace

| branch | C3 − fixed-low mean | 95% paired bootstrap CI | C3 − fixed-high mean | 95% paired bootstrap CI |
|---|---:|---:|---:|---:|
| A/B pre-save | `+0.000398` | `[-0.002713,+0.003391]` | `+0.045744` | `[+0.028200,+0.063520]` |
| C PNG reload | `−0.003546` | `[-0.005824,−0.001458]` | `+0.033948` | `[+0.021797,+0.046541]` |

The trace therefore reproduces the important direction change against
fixed-low: the pre-save branch is inconclusive on this small diagnostic
cohort, while the PNG-reloaded branch favors fixed-low. This does not prove
equivalence or non-inferiority, and it is not a replacement for the 300-object
main table until one final metric path is chosen and applied consistently.

## Scientific conclusion

`float32` versus `float64` is not the explanation for the original gap. In the
same-generation controlled run, the model output passed to float-eval and the
PNG encoder is identical; the observable tensor change occurs at uint8 PNG
serialization and reload. The exact historical 300-object gap may still
include missing pre-save provenance, so the paper must describe this as a
controlled serialization finding and retain the limitation.

No metric patch was applied. No dataset, checkpoint, C3 schedule, frozen main
table, or manuscript was modified.
