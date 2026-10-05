# LAYER_TIME_CAUSAL_MAP_REPORT — Experiment A

> **AMENDED 2026-10-05 (P0-1 closure):** the production SS-interaction
> cluster bootstrap has zero power against object-shared interactions
> (`PRE_ACCEPTANCE_AUDIT_20261005.md` P0-1); its p-values below are
> retracted. The authoritative interaction result is the validated
> cluster-robust Wald test (`audit_scripts/AUDIT_INTERACTION_VALID_TEST.json`):
> A2 FG-LPIPS W=481.1 (p=8.0e-99, interaction SS share 43.5%), A2 FG-PSNR
> W=1880 (p≈0, 56.8%), A3 FG-LPIPS W=657.2 (p=1.1e-136, 11.9%), A3 FG-PSNR
> W=1389.1 (p=1.3e-294, 0.8%). The interaction is REAL at native dose and
> remains significant at matched dose with a collapsed variance share. The
> A3 "equal dose" reading is exact only for the deep row (middle
> approximate, shallow stress-only — `A3_DOSE_VALIDITY_AUDIT.md`).

Cohort: FRESH_CONFIRM_300. Runner: run_validation_v3_experiment.py (verbatim
Core-7 per-object code path). 16 conditions (baseline + 3 layers x 5 windows).
Windows: W1 steps 0-9 ... W5 steps 40-49. Base: layer-fixed-low
(deep/middle 1.25, shallow 0.50); frozen high: deep/middle 2.50, shallow 0.75.

## A2 raw map (descriptive)

Artifacts: formal/campaign_A2/layermap_raw.json (FG-LPIPS primary),
layermap_raw_fgpsnr.json, layermap_raw_ciede2000.json,
texture_extension_per_object.csv.

- 15/15 cell effects Holm-significant on FG-LPIPS but small (|mean delta| <= 0.006).
- Layer x Window interaction: **[AMENDED P0-1]** SUPPORTED on the valid Wald
  test (W=481.1, p=8.0e-99; SS share 43.5% FG-LPIPS / 56.8% FG-PSNR); the
  production bootstrap p = 0.50/0.51 was a zero-power artifact and is
  retracted.
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
1. Layer x Time interaction? **[AMENDED P0-1] YES** — Wald W=657.2,
   p=1.1e-136 (FG-LPIPS; SS share 11.9%), W=1389.1, p=1.3e-294 (FG-PSNR;
   share 0.8%) on the dose-normalized map; W=481.1/1880 (shares 43.5%/56.8%)
   raw. The earlier "p = 1.0 / p = 0.50, NO" answer was a zero-power-test
   artifact and is retracted.
2. Survives dose normalization? Yes statistically, but the time-structure
   variance share collapses at matched dose (FG-PSNR 56.8% -> 0.8%; FG-LPIPS
   43.5% -> 11.9%): the layer main effect dominates and the window profile is
   nearly flat within each layer at equal dose (exact reading for the deep
   row only; middle approximate; shallow stress-only).
3. Non-monotonic temporal curves? The raw-map deep curve shows a clean
   early->late progression (deltas x1e-4 = [-29.3, +5.9, +41.3, +35.2, +23.8],
   sign flip between W1 and W3); at equal dose no meaningful
   non-monotonicity beyond noise within the valid (deep) row.
4. 1/3 stage boundaries supported? **No** — nothing special at steps 16/17 or
   32/33; responses are window-flat within layers (dose-normalized).
5. Is a full S=[s_l,k] empirically justified? **[AMENDED P0-1] Partially** —
   the 2D interaction is real (significant at matched dose), so S is a
   meaningful control space; but the layer x constant representation plus a
   monotone late-increasing profile captures the practical benefit (B1/B2/C),
   and the matched-dose time-structure variance share is small (0.8%
   FG-PSNR / 11.9% FG-LPIPS). S is scientifically meaningful but not
   empirically necessary for deployment-level gains.