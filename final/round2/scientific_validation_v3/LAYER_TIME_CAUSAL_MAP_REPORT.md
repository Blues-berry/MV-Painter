# LAYER_TIME_CAUSAL_MAP_REPORT — Experiment A

Cohort: FRESH_CONFIRM_300. Runner: run_validation_v3_experiment.py (verbatim
Core-7 per-object code path). 16 conditions (baseline + 3 layers x 5 windows).
Windows: W1 steps 0-9 ... W5 steps 40-49. Base: layer-fixed-low
(deep/middle 1.25, shallow 0.50); frozen high: deep/middle 2.50, shallow 0.75.

## A2 raw map (descriptive)

Artifacts: formal/campaign_A2/layermap_raw.json (FG-LPIPS primary),
layermap_raw_fgpsnr.json, layermap_raw_ciede2000.json,
texture_extension_per_object.csv.

- 15/15 cell effects Holm-significant on FG-LPIPS but small (|mean delta| <= 0.006).
- Layer x Window interaction: NOT supported (SS-interaction cluster bootstrap
  p = 0.50; FG-PSNR p = 0.51).
- Patterns: deep/middle late-window injections mildly improve FG-PSNR
  (middle_W5 +0.52 dB); shallow injections mildly harmful on all metrics.

## A3 dose-normalized map (CONFIRMATORY, H1)

Artifacts: a3_normalization.json (frozen rule + values),
formal/campaign_A3/layermap_dosenorm.json, layermap_dosenorm_fgpsnr.json,
layermap_dosenorm_ciede2000.json.

Normalization (pre-registered): R_l,t from probe-24 baseline residuals;
C = 1.25 * mean_w M_deep,w; delta_l = C / mean_w M_l,w; high_l = LOW_l + delta_l.
Result: deep high 2.50 (delta 1.25), middle 6.84 (delta 5.59), shallow 30.38
(delta 29.88); middle/shallow exceed native caps -> whole A3 map run under the
uncapped injection path (cap-inactive for the baseline cells either way).

Answers (pre-registered questions):
1. Layer x Time interaction? **NO** — p = 1.0 (dose-normalized), p = 0.50 (raw).
   The observed additive residual is SMALLER than the bootstrap null: the cell
   structure is more additive than resampling noise itself.
2. Survives dose normalization? The interaction was already absent raw; at
   equal dose the layer main effect becomes dominant and the window profile is
   flat within each layer (shallow uniformly harmful, deep uniformly helpful).
3. Non-monotonic temporal curves? No meaningful non-monotonicity beyond noise
   at equal dose; raw-map deep curve decreases monotonically-ish over windows.
4. 1/3 stage boundaries supported? **No** — nothing special at steps 16/17 or
   32/33; responses are window-flat within layers (dose-normalized).
5. Is a full S=[s_l,k] empirically justified? **No** — a layer x constant
   representation (per-layer scale, no timestep structure) captures the
   supported structure; timestep-dependence is not supported at equal dose.