# Full-SSIM Root-Cause Crosscheck

Status: **PARTIALLY_CONFIRMED**.

This is a fixed-input cross-check over the already frozen 11-object / 44-row diagnostic sample. No model inference and no 300-object recomputation were performed.

## Tensor provenance

No original float prediction tensor was found under `/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6`. The A branch is therefore the recorded `original_float_ssim` scalar from the original per-object CSV, not a recovered tensor. This report does not claim to reconstruct that tensor. Tensor-like files found: `0`.

## A/B/C definitions

- **A — float-eval scalar:** recorded original float-eval Full-SSIM value.
- **B — PNG/original implementation:** saved prediction PNG and saved GT PNG, evaluated by the historical 3×3 PyTorch implementation.
- **C — PNG/independent implementation:** the same fixed PNG inputs evaluated by an independent NumPy zero-padded 3×3 implementation. The existing raw-GT audit branch is also retained in the CSV for comparison.

## Aggregate fixed-input result

| branch | mean SSIM | mean absolute difference vs A |
|---|---:|---:|
| A recorded float-eval | 0.833496 | — |
| B original impl, float32 | 0.864573 | 0.031117 |
| B original impl, float64 | 0.864584 | 0.031127 |
| C independent NumPy, float32 | 0.864565 | 0.031109 |
| C independent NumPy, float64 | 0.864584 | 0.031127 |

## Dtype and paired-difference isolation

- Original implementation float64 versus float32 mean absolute difference: `0.00002117`.
- Independent NumPy versus original implementation at float32 mean absolute difference: `0.00002461`.
- Recorded A C3−fixed-low paired mean: `0.006881`; PNG/original implementation float32: `0.001205`.
- Recorded A C3−fixed-high paired mean: `0.031496`; PNG/original implementation float32: `0.027270`.

## Confirmed boundary

B and C agree on the fixed PNG inputs to numerical tolerance, while float32 versus float64 does not materially change B. Therefore the 0.026–0.037 gap is not explained by data range, window size, Gaussian weighting, padding, montage versus per-view aggregation, or ordinary float32/float64 arithmetic in the PNG branch. The paired C3-versus-fixed-low conclusion also changes between A and PNG, so the PNG quantization/provenance boundary can affect method comparisons.

The remaining unresolved distinction is whether the A values came from float predictions before 8-bit serialization, a different target/prediction tensor branch, or another pre-save evaluation path. Without the original float tensors or an exact inference rerun that emits them, no stronger root-cause claim is justified.

## Files

- `SSIM_ROOT_CAUSE_CROSSCHECK.csv`: object/method A/B/C and dtype rows.
- `SSIM_ROOT_CAUSE_CROSSCHECK.json`: machine-readable summary.
- `final/round2/main_adapter_clean_v2/full_ssim_reconciliation/FULL_SSIM_RECONCILIATION.md`: Codex A's 300-object reconciliation retained as prior evidence.
