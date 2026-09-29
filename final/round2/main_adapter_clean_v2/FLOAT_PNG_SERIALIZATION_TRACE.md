# Float-to-PNG serialization trace

Status: `STATIC_ROOT_CAUSE_CLASS_CONFIRMED; EXACT_A_B_PIXEL_TRACE_PENDING_CUDA`.
No dataset, checkpoint, C3, or paper table was changed.

## Static data-chain audit

The frozen evaluation path is:

1. `geotex/round2_main_eval.py` sets `dtype = torch.float16` and loads the
   historical `eval_exploration.generate` implementation.
2. `prepare_batch` loads and resizes the target RGBA composite as float32. The
   historical dataset loader returns `target_imgs` and alpha masks as float32.
3. `generate` runs the UNet/VAE in float16, unscales the decoded image, applies
   `(image * 0.5 + 0.5).clamp(0, 1)`, and returns that tensor without a float32
   cast.
4. `compute_metrics(prediction, target_imgs, ...)` is called immediately on
   that returned prediction, before any file save.
5. The same `prediction` object is passed to `torchvision.utils.save_image`.
   There is no second prediction cache, duplicate normalization, resize, RGB/BGR
   conversion, or alternate filename at this boundary.
6. `save_image` performs `clamp(prediction * 255 + 0.5, 0, 255).to(uint8)` and
   writes an RGB PNG. Reloading therefore produces float32 values on the
   `q/255` grid, not the original float16 values.

Relevant source locations:

- `/4T/CXY/MV-Painter/geotex/round2_main_eval.py:70-71,121-158`
- `/tmp/mv_main_rerun/geotex/eval_exploration.py:71-88,143-194,265-305`
- `/tmp/mv_main_rerun/geotex/metrics.py:22-39`
- `torchvision.utils.save_image` in the active Python environment

The historical Full-SSIM implementation computes local variance by subtracting
`avg_pool(pred ** 2) - avg_pool(pred) ** 2`. Therefore the pre-save prediction
is evaluated through a float16-sensitive path, while the PNG audit evaluates a
float32 reloaded image. This is sufficient to explain a systematic branch
difference; the exact A/B pixel contribution cannot be measured without the
missing original tensor.

## File and manifest consistency

The frozen manifest points to the clean-v2 UID list, checkpoint, unique6 order,
seed, steps, and four condition names. The 12-object audit verified all 48
CSV-to-PNG mappings by object index and filename. No tensor-like A/B artifact
was found in the frozen evaluation directory.

The audit-only result is:

`final/round2/main_adapter_clean_v2/float_png_trace_12/FLOAT_PNG_PIXEL_COMPARISON.csv`

It records the historical A scalar, PNG-reloaded C statistics, PNG hashes, and
the explicit unavailable status for A/B pixel tensors. It does not fabricate
pixel MAE or PSNR for unavailable tensors.

## Fixed 12-object diagnostic evidence

The fixed objects are indices `13,15,38,48,54,66,68,78,82,83,110,111`.
The following values are means over the 12 objects; `PNG-fp16` is a diagnostic
proxy made by converting the reloaded PNG prediction to float16 before applying
the historical SSIM implementation. It is not claimed to be the original A
tensor.

| condition | recorded A | PNG-fp16 proxy | PNG-fp32 | PNG-fp16 − A | PNG-fp32 − A |
|---|---:|---:|---:|---:|---:|
| no adapter | 0.751344 | 0.772850 | 0.790606 | 0.021506 | 0.039261 |
| fixed low | 0.867758 | 0.888320 | 0.895336 | 0.020562 | 0.027578 |
| fixed high | 0.821831 | 0.843933 | 0.857722 | 0.022102 | 0.035891 |
| C3 | 0.868465 | 0.885567 | 0.891905 | 0.017102 | 0.023440 |

The corresponding C3-minus-fixed-low means are `+0.000708` for recorded A,
`-0.002753` for the PNG-fp16 proxy, and `-0.003430` for PNG-fp32. This supports
the conclusion that dtype-sensitive pre-save evaluation is a major contributor,
while not pretending that a PNG proxy reconstructs the missing original tensor.

## Controlled rerun prepared for CUDA

`geotex/trace_float_png_serialization.py --mode run` uses the frozen checkpoint,
clean-v2 list, unique6, seed 42, 50 steps, and the four existing conditions.
For each object-condition from one generation it will save:

- A: the tensor used for float-eval;
- B: the tensor passed to the PNG encoder;
- C: the reloaded PNG tensor;
- per-stage dtype/shape/min/max/mean/std;
- A/B, B/C, and A/C pixel MAE, maximum absolute error, PSNR, and Full-SSIM;
- PNG SHA-256 and a manifest proving the shared generation.

The current host has no usable CUDA device (`torch.cuda.is_available() ==
False`; `nvidia-smi` cannot communicate with the driver), so this controlled
rerun was not started and no GPU was occupied.

