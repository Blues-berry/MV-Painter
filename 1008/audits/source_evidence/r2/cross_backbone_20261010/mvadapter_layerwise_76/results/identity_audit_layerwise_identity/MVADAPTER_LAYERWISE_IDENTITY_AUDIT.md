# MV-Adapter Layer-wise Identity Audit

Comparison A = global runner (`run_experiment.py`) vs B = layer-wise wrapper
(`run_layerwise_experiment.py --identity`, all multipliers = 1.0).
Objects: obj_0024, obj_0025, obj_0026. Schedules: fixed_low, LHL, LLH.
Seed 20260928, 50 steps, low 0.75, high 1.00, exact meshes, same GPU.

**IDENTITY_AUDIT = PASS**

| check | result |
|---|---|
| all_png_sha_equal | True |
| all_pixel_equal | True |
| all_max_abs_pixel_diff_zero | True |
| all_metrics_equal | True |
| all_cases_present | True |
| cond_encoder_features_count_ok | True |
| norm_ratios_are_one | True |

## cond_encoder diagnostics (first wrapped call)

- adapter_state shapes: `[[12, 320, 64, 64], [12, 640, 32, 32], [12, 1280, 16, 16], [12, 1280, 8, 8]]`
- input norms: `[2285.84716796875, 1763.89599609375, 2535.650390625, 2316.997802734375]`
- scaled norms: `[2285.84716796875, 1763.89599609375, 2535.650390625, 2316.997802734375]`
- norm ratios (must be 1.0): `[1.0, 1.0, 1.0, 1.0]`

## Per-case detail

| schedule | object | PNG SHA equal | pixel equal | max abs diff | metrics equal | archived SHA equal |
|---|---|---|---|---|---|---|
| fixed_low | obj_0024 | True | True | 0 | True | True |
| fixed_low | obj_0025 | True | True | 0 | True | True |
| fixed_low | obj_0026 | True | True | 0 | True | True |
| LHL | obj_0024 | True | True | 0 | True | True |
| LHL | obj_0025 | True | True | 0 | True | True |
| LHL | obj_0026 | True | True | 0 | True | True |
| LLH | obj_0024 | True | True | 0 | True | True |
| LLH | obj_0025 | True | True | 0 | True | True |
| LLH | obj_0026 | True | True | 0 | True | True |
