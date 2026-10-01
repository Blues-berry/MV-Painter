# MV-Adapter Mapping-Sensitivity Protocol (pre-registered)

Date: 2026-10-01. Status: **frozen before any mapping-variant inference** (commit time of
this file precedes all result files in `results/mapping_sensitivity/` and
`results/holdout_exact_layer_llh_mapB211_76/`). Parent protocol:
`MVADAPTER_LAYERWISE_PROTOCOL.md` (unmodified).

## 1. Objective and reviewer concern

Reviewer 2 question: *does the layer-wise transfer result depend on the arbitrary choice
of the 4→3 layer partition?* This protocol tests partition sensitivity once, mechanically,
with no search.

## 2. Frozen protocol surface (identical to the L-LLH 76 run)

Everything except the layer profile is bit-frozen to
`results/holdout_exact_layer_llh_76/run_config.json`: manifest `data_manifest.json`,
base model `models/sd21_base`, adapter `models/mv-adapter`, split `holdout`,
`geometry_source=exact`, seed 20260928, steps 50, low 0.75, high 1.0, schedule `LLH`
(canonical `L-LLH`), 76-object Exact holdout, runner
`run_layerwise_experiment.py` (sha256 `441aef4f…`), metric suite
`run_experiment.object_metrics` (PSNR, FG-SSIM, Edge-SSIM, FG-LPIPS, CIEDE2000,
GT-relative texture error), per-point pre-multiplication wrapper, caps deep 3.0 /
middle 3.5 / shallow 0.8, no recalibration.

## 3. Partition space (complete, no search)

The frozen source profile assigns group values shallow=0.58, middle=1.65, deep=1.65
(deep = middle). For 4 ordered injection points split into 3 contiguous groups there are
exactly three partitions; with these source values they reduce to **two distinct
per-point multiplier vectors**:

| Partition (shallow/middle/deep sizes) | Per-point source values | Normalized list (mean=1) | Status |
|---|---|---|---|
| C = (1,1,2) | 0.58, 1.65, 1.65, 1.65 | [0.4195298372513563, 1.193490054249548, 1.193490054249548, 1.193490054249548] | already run (`holdout_exact_layer_llh_76`) |
| D = (1,2,1) | 0.58, 1.65, 1.65, 1.65 | **identical to C by arithmetic** | degenerate; 3-object identity check only |
| B′ = (2,1,1) | 0.58, 0.58, 1.65, 1.65 | [0.5201793721973094, 0.5201793721973094, 1.4798206278026904, 1.4798206278026904] | new; full 76-object run |

Degeneracy proof for D: the source middle and deep values coincide (1.65), so partitions
(1,1,2) and (1,2,1) induce the same multiset of per-point source values and the same
weighted mean 1.3825; the wrapper scales per point, so D ≡ C bitwise. D is verified, not
assumed, by a 3-object identity check.

## 4. Execution plan

1. **Preflight (3 objects: obj_0024, obj_0025, obj_0026, L-LLH)**:
   (a) control re-run with the reference profile C;
   (b) degenerate profile D.
   Pass criterion: (a) must reproduce the archived L-LLH rows for these objects
   bit-for-bit in `per_object_metrics.csv` (confirms runner/GPU-sharing determinism);
   (b) must equal (a) bit-for-bit (confirms degeneracy empirically).
2. **Main run**: profile B′ (`layer_profile_mapping_B_prime_211.json`), L-LLH, all 76
   objects → `results/holdout_exact_layer_llh_mapB211_76/`.

## 5. Analysis (frozen)

Paired object-level differences and 10,000-resample percentile bootstrap CIs, seed
20260928 (the panel's seed), comparing L-LLH(B′) against the existing rows: G-FL,
G-LLH, L-LLH(C). Benefit-oriented sign convention as in
`MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json` (positive = left condition better; LPIPS /
ΔE00 / GT-texture lower-better).

## 6. Pre-registered interpretations

- **Outcome 1** — L-LLH(B′) reproduces the layer-wise advantage (PSNR, ΔE00, GT-texture
  CIs exclude zero in favor of the layer condition, matching the C pattern):
  > "Layer redistribution transfers independent of the exact layer partition."
- **Outcome 2** — L-LLH(B′) fails to reproduce the advantage:
  > "Transfer is architecture-aware and mapping-sensitive; the reported layer-wise
  > effect holds under the pre-registered partition and not under every reasonable
  > partition."
- **Outcome 3** — mixed metrics: report as found; claim only the metrics that replicate,
  listing the others explicitly.

Negative or mixed components are preserved in all outcomes. No seventh method, no
re-search of scales/schedules, no post-hoc partition selection.
