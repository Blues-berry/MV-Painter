# Method implementation audit — layer-wise stage-aware adapter scaling

Audit date: 2026-09-30 UTC.
Scope: verify that the implemented "layer-wise stage-aware adapter scaling"
matches the paper equation `h'_{l,t} = h_{l,t} + s_l(p_t) · A_l(h_{l,t}, G)`
and that every runner that produced a paper number shares the same scale
semantics. All paths read from source; all hashes recomputed on 2026-09-30.

## 1. Frozen assets (recomputed)

| Asset | SHA-256 (prefix) | Status |
|---|---|---|
| Checkpoint `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt` | `0618d6b284ab…` | matches freeze manifest |
| Probe list `final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt` | `187185c6e94d…` | matches clean-v2 freeze |
| Strict holdout `final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt` | `a6aa8ab6e475…` | matches clean-v2 freeze |
| Eval pool `final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt` | `49627906573f…` | matches clean-v2 freeze |
| `coordination/layer_lhl_v1/ARTIFACT_SHA256SUMS.txt` (5 files) | `sha256sum -c` | 5/5 OK |

## 2. Injection points and depth mapping

- Model config used by ALL paper runners: `adapter_mode: up_only`
  (`MVPainter/configs/mvpainter-geotex-full-train.yaml` vs
  `clean_holdout.yaml` diffed: object list / view mode only).
- UNet structure (`checkpoints/hf_repo/unet/config.json`):
  `up_block_types = [CrossAttnUpBlock2D, CrossAttnUpBlock2D, UpBlock2D]`,
  `block_out_channels = [320, 640, 1280]` → exactly three up blocks.
- Injection (`MVPainter/mvpainter/model_unet_geotex.py`, `inject_adapters`,
  L371–438): each up block's resnets are wrapped by `GeoTexResnetWrapper`.
  Depth mapping (L402–408, mirrored in `geotex/eval_exploration.py` L42–47):

  | Block | Depth group | Spatial role (256² input) | Cap |
  |---|---|---|---|
  | `up_0` (+`mid` if present) | deep | 32×32, global structure | 3.0 |
  | `up_1` | middle | 64×64, shape lever | 3.5 |
  | `up_2` | shallow | 128×128, fine texture | 0.8 |

  With `up_only` there are 9 wrappers (3 resnets × 3 up blocks); no `mid`
  wrappers exist. "Shallow" is the highest-resolution group (fine texture);
  "deep" is the lowest-resolution group.

## 3. Scale application and caps

`GeoTexResnetWrapper.forward` (L326–368):

```python
correction = self.adapter.compute_correction(hidden_states, geo_feat)
if hasattr(self, '_adapter_scale'):
    effective_scale = min(self._adapter_scale, self._max_scale)
    correction = correction * effective_scale
hidden_states = hidden_states + correction
```

- The scale is a per-step Python attribute, NOT a network parameter.
- Caps: `LAYER_MAX_SCALES = {deep: 3.0, middle: 3.5, shallow: 0.8}` (L298–302).
- Consequence (verified): **global** schedules are clipped at shallow layers —
  global fixed-low 1.25 → effective 0.8; global fixed-high 2.50 → effective
  0.8. **Layer-wise** candidate values never touch a cap: layer-LHL shallow
  max 0.75 < 0.8; layer high 2.50 < caps 3.0/3.5. This asymmetry is real,
  disclosed in the paper ("shallow cap 0.8 does not change any layer-LHL
  value"), and is exactly what `layer_fixed_low` (deep/middle 1.25 + shallow
  0.50) isolates against global fixed-low (deep/middle 1.25 + shallow 0.8).
- Per-layer schedule setting: `geotex/explore_contradiction.py`
  `generate_with_schedule` L158–167 — per step,
  `module._adapter_scale = scale.get(module.depth_group, 1.0)` for dict
  schedules (layer-wise) or the scalar for global schedules. Scales are
  deleted after generation (L196–201).

## 4. Schedule parameter verification

Source `geotex/layer_lhl_ablation_shared.py` L54–75 (development ablation) and
`/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/run_layer_official.py`
(strict-276 transfer record):

| Method | deep | middle | shallow | Semantics |
|---|---|---|---|---|
| fixed-low (global) | 1.25 | 1.25 | 1.25→**0.8 capped** | scalar |
| C3/LHL (global) | 1.25/2.50/1.25 | same | same→**0.8 capped late** | scalar per stage |
| layer-fixed-low | 1.25 | 1.25 | 0.50 | dict |
| layer-fixed-mean | 1.65 | 1.65 | 0.58 | dict, constant |
| layer-LHL | [1.25, 2.50, 1.25] | same | [0.50, 0.75, 0.50] | dict per stage |
| layer-LLH | [1.25, 1.25, 2.50] | same | [0.50, 0.50, 0.75] | dict per stage |

- Layer-fixed-mean = exact 17/16/17 step means of layer-LHL:
  deep/middle (1.25·17 + 2.50·16 + 1.25·17)/50 = **1.65**;
  shallow (0.50·17 + 0.75·16 + 0.50·17)/50 = **0.58**. ✔ matches paper.
- Stage partition: `progress = step_idx / 49`; early `< 1/3`, middle `< 2/3`.
  For 50 steps this yields steps {0–16, 17–32, 33–49} = 17/16/17, enforced by
  `geotex/stage_placement_eval.py` protocol check (L114–117). The alternate
  thresholds 0.33/0.66 in `eval_exploration.get_timestep_scale` produce the
  identical partition for 50 steps. ✔
- No UNet/VAE/adapter weight is modified; `_adapter_scale` is deleted after
  each generation.

## 5. Runner inventory and semantic consistency

All runners share: checkpoint `geotex_step_0002000.pt` (hash above), Euler
discrete 50 steps, seed 42 (development ablation adds seeds 43/44 with
`object_seed = seed + obj_idx`), unique6 views `[0,15,12,16,13,14]`, 256×256,
and the metric function `eval_exploration.compute_metrics`.

| Runner | Output | Schedule type | Metric path | Notes |
|---|---|---|---|---|
| clean-v2 four-condition (`mvpoutput/…/eval300_clean_v2_unique6`) | Table strict276 | global scalars (no_adapter 0.0, fixed_low 1.25, fixed_high 2.50, C3) | `compute_metrics` | manifest frozen |
| stage-placement follow-up (`geotex/stage_placement_eval.py` → `final/round2/stage_placement_276_20260929`) | Table stage276 + serialized SSIM | **global** scalar per stage (fixed_mean 5/3, HLL, LHL, LLH) | `compute_metrics` + forward-hook residual norms | protocol-locked 17/16/17 |
| strict-276 layer-LHL (`run_layer_official.py`, temp dir) | layer-LHL transfer record | **dict** (layer-wise) | `compute_metrics` | same seed/step/views |
| shared-input development ablation (`geotex/layer_lhl_ablation_shared.py`) | Table layerablation | scalar (fixed-low, C3) + dict (4 layer methods) | `compute_metrics` | shared target/geo/latent hashes |
| full-factorial binary probe (`full_factorial_layer_ablation/run_full_factorial_probe.py`, temp dir) | 8-pattern development ablation | dict, LOW/HIGH per group | `compute_metrics` | shared inputs; holdout selection forbidden |

Differences that are documented and do not invalidate comparisons:

1. Two generation functions exist (`eval_exploration.generate` vs
   `explore_contradiction.generate_with_schedule`); both run the same Euler
   loop through the same wrapper path with the same min-cap semantics. The
   latter additionally accepts precomputed geo features and logs residuals.
2. The stage-placement follow-up and clean-v2 four-condition run are separate
   runs; their repeated C3 outputs differ (mean |ΔFull-SSIM| 0.00395) and are
   never pooled — the paper states this.
3. The strict-276 layer-LHL record was produced by a third runner; the paper
   labels it an independent holdout record, not a paired replacement.

## 6. Fairness findings (actionable)

- **[RESOLVED-BY-DISCLOSURE] Shallow cap asymmetry.** Global baselines are
  effectively shallow-capped at 0.8; layer-wise candidates are not clipped.
  This is inherent to the historical global runs and is disclosed. The paper
  must keep describing global fixed-low as "global 1.25 under the same
  per-layer caps", not as a truly uniform 1.25.
- **[RESOLVED] No hidden scaling coefficients or conditioning-path
  differences.** The only difference between global and layer-wise runners is
  the schedule type; configs, caps, generation loop, VAE conditioning path,
  and metric code are shared.
- **[RESOLVED] Stage partition consistency.** 17/16/17 verified in code and
  protocol manifests; nominal budgets (1.650/1.6667/1.675 means) and actual
  residual L2/RMS summaries are recorded in the follow-up records.
- **[OPEN at audit time] The 8-pattern binary layer-wise ablation (D18) was
  still running** (`/4T/tmp/mvpainter-recovery-HLzm9O/full_factorial_layer_ablation/`,
  seeds 42+43 complete, seed 44 in progress, 521/576 rows). Its result must
  be integrated before any layer-wise schedule is named "selected" in the
  paper.

## 7. Computational overhead

- No additional network forward: the adapter correction `A_l(h,G)` is computed
  whenever geometry conditioning is active, with or without scaling.
- Layer-wise scheduling adds only per-step Python attribute writes (≤9
  wrappers × 50 steps) — negligible.
- Residual logging (L2/RMS per wrapper per step) exists only in experiment
  runners, not in the method itself.
- Memory: no additional tensors retained beyond the existing correction.

## 8. Verdict

The implementation matches the paper equation and the frozen parameter tables.
Global and layer-wise controls differ only in schedule semantics; caps are
applied identically in both paths. The layer-LHL strict-276 record, the
development ablation, and the running full-factorial probe all use the same
checkpoint, metric path, and generation semantics, so a same-runner
shared-input comparison is valid. No fairness blocker was found.
