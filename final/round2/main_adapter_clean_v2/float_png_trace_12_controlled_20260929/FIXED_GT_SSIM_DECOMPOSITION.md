# Fixed-GT Full-SSIM decomposition

CPU-only decomposition of the saved 12-object controlled trace; no model inference was run.

- Objects: 12; methods: no_adapter, fixed_low, fixed_high, c3; rows: 480.
- A/B maximum absolute difference: `0`.
- `A_fp16`/`A_fp32` are the same saved pre-serialization prediction evaluated at two arithmetic dtypes.
- `C_fp32` is the saved PNG-reloaded prediction; `gt_float32` is the saved original GT tensor and `gt_png_float32` is the saved PNG-reloaded GT.

## Mean decomposition effects

| isolated effect | mean SSIM change |
|---|---:|
| A fp16 → fp32, fixed original GT | -0.03198064 |
| A fp32 → C fp32, fixed original GT (prediction PNG quantization) | -0.00036340 |
| original GT → PNG GT, fixed A fp32 (GT serialization) | -0.00006934 |
| A/original GT → C/PNG GT (observed combined path) | -0.00043251 |

The paired C3-minus-baseline values are provided in the JSON for each fixed-GT/prediction branch. The 12-object trace is diagnostic evidence for the serialization boundary; it is not a replacement for the 276-object stage-placement result.

Machine-readable outputs: `FIXED_GT_SSIM_DECOMPOSITION.csv` and `FIXED_GT_SSIM_DECOMPOSITION.json`.
