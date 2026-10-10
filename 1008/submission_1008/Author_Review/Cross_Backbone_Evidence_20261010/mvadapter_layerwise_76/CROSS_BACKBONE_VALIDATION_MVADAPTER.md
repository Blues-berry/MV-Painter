# Cross-Backbone Validation — MV-Adapter (Second Backbone)

Date: 2026-10-01. Branch: `codex/next-review-response-20260930`.
Task: Round-2 cross-backbone final experiment (Phase A + Phase B).
Scope: layer-wise residual-scheduling validation on MV-Adapter; experiment
facts and conclusions only — no paper text was modified.

## 1. Frozen protocol (pre-registered before any layer-wise run)

Full document: `final/round2/mv_adapter/MVADAPTER_LAYERWISE_PROTOCOL.md`;
profile: `final/round2/mv_adapter/layer_profile_transfer.json`.

- Injection points (verified): `cond_encoder` (diffusers `T2IAdapter`) emits
  one feature per SD2.1 down block; consumed in order as
  `down_intrablock_additional_residuals`:
  `[320ch @64, 640ch @32, 1280ch @16, 1280ch @8]` (batch 12 = 6 views x CFG).
- Mechanical mapping (topology/resolution/relative depth only, no metrics):
  shallow = 320@64, middle = 640@32, deep = {1280@16, 1280@8} — the source
  (MVPainter) profile's 1/1/2 point counts transfer 1:1 (both networks have
  exactly 4 injection points).
- Frozen profile transfer: source `layer_fixed_mean` deep=1.65/middle=1.65/
  shallow=0.58 (`geotex/layer_lhl_ablation_shared.py`, provenance SHA-256
  recorded); normalized to weighted mean 1.0 over the 4 points with point-
  count weights 2/1/1: deep = middle = 1.193490054249548, shallow =
  0.4195298372513563.
- Semantics: effective_scale(point, t) = layer_multiplier(point) x
  temporal_scale(t); temporal schedules frozen at low=0.75, high=1.00,
  fixed mean=5/6, boundaries 1/3 and 2/3. No recalibration.
- Runner: `final/round2/mv_adapter/run_layerwise_experiment.py` — thin wrapper
  reusing the global runner end-to-end; only addition is per-point
  pre-multiplication of the cond_encoder outputs (inference-only, weights
  frozen; multipliers 1.0 are bitwise the original state).

## 2. Gates

| gate | result |
|---|---|
| IDENTITY_AUDIT (wrapper, multipliers=1.0 vs global runner; 3 objects x G-FL/G-LHL/G-LLH) | **PASS** — PNG SHA-256 / pixels / max-abs-diff 0 / metrics all equal; also 9/9 PNG SHA equal to the archived 76-object grids (reproducibility) |
| SMOKE (3 objects x L-FIX/L-LHL/L-LLH) | **PASS** — 9/9 rows finite, methods pairwise distinct, norm ratios equal frozen multipliers, 6 views per grid |

cond_encoder shapes logged at first wrapped call:
`[12,320,64,64], [12,640,32,32], [12,1280,16,16], [12,1280,8,8]`.

## 3. Runs

New conditions x 76-object Exact holdout, seed 20260928, 50 steps:
L-FIX (`holdout_exact_layer_fixed_76`), L-LHL (`holdout_exact_layer_lhl_76`),
L-LLH (`holdout_exact_layer_llh_76`) = 228 new rows, all `exact_mesh`, all
metrics finite. Existing global rows reused without rerun: R0 (`no_geometry`),
G-FL (`fixed_low`), G-LHL (`LHL`), G-LLH (`LLH`).

## 4. Panel means (7 conditions)

| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| R0 | 13.114180 | 0.498481 | 0.233429 | 0.183496 | 20.719805 | 1.700798 |
| G-FL | 13.357177 | 0.527539 | 0.239997 | 0.187693 | 20.149543 | 2.224047 |
| G-LHL | 13.344064 | 0.528325 | 0.240235 | 0.188051 | 20.182146 | 2.269096 |
| G-LLH | 13.353306 | 0.527814 | 0.239974 | 0.188346 | 20.157122 | 2.198930 |
| L-FIX | 13.431922 | 0.523473 | 0.239052 | 0.187647 | 19.877910 | 1.903374 |
| L-LLH | 13.453797 | 0.523564 | 0.238899 | 0.187731 | 19.805120 | 1.913272 |
| L-LHL | 13.446348 | 0.525148 | 0.239619 | 0.187920 | 19.868912 | 1.980378 |

## 5. Paired comparisons (10,000 object bootstrap, seed 20260928)

Positive favors the left condition (LPIPS/dE00/GT-texture lower-better);
`*` = 95% CI excludes 0.

| comparison | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| P1 L-LLH vs G-FL | +0.0966* | -0.0040* | -0.0011* | -0.0000 | +0.3444* | +0.3108* |
| P2 L-LLH vs G-LLH | +0.1005* | -0.0042* | -0.0011* | +0.0006 | +0.3520* | +0.2857* |
| P3 L-LLH vs L-FIX | +0.0219 | +0.0001 | -0.0002 | -0.0001 | +0.0728* | -0.0099 |
| P4 L-LHL vs G-LHL | +0.1023* | -0.0032* | -0.0006 | +0.0001 | +0.3132* | +0.2887* |
| P5 G-LLH vs G-LHL | +0.0092 | -0.0005 | -0.0003* | -0.0003 | +0.0250 | +0.0702 |

Full mean/median/CI/win-rate records:
`final/round2/mv_adapter/MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json`.

## 6. Conclusions (experiment-level)

- **Layer-wise effect: SUPPORTED.** PSNR, dE00 and GT-relative texture error
  consistently and significantly favor the layer-wise conditions over their
  global counterparts (P1, P2, P4); FG-/Edge-SSIM consistently favor global by
  a small margin; FG-LPIPS is not separated. The effect exists; its direction
  is metric-dependent.
- **Temporal-position effect: NOT_SUPPORTED.** Within the frozen scales, LLH
  vs fixed-mean under layer-wise scaling (P3) and global LLH vs G-LHL (P5)
  are not separated; only marginal single-metric terms appear (P3 dE00 +0.073*
  favoring L-LLH, P5 Edge-SSIM -0.0003* favoring G-LHL), inconsistent in
  direction across the two comparisons.
- Negative/mixed components are reported as found; no re-search of low/high,
  profile, mapping or schedules was performed, and no seventh method was
  added.
- This closes the previously BLOCKED MV-Adapter layer-wise gate (commit
  08e3ea3) via the pre-registered mechanical mapping above.

## 7. Artifact index

- `final/round2/mv_adapter/MVADAPTER_LAYERWISE_PROTOCOL.md`
- `final/round2/mv_adapter/layer_profile_transfer.json`
- `final/round2/mv_adapter/run_layerwise_experiment.py`
- `final/round2/mv_adapter/analyze_layerwise_identity_audit.py` /
  `analyze_layerwise_smoke.py` / `analyze_layerwise_panel_20260930.py` /
  `build_layerwise_report_20260930.py`
- `final/round2/mv_adapter/results/identity_audit_*`, `results/layerwise_smoke_3/`,
  `results/holdout_exact_layer_{fixed,lhl,llh}_76/`
- `final/round2/mv_adapter/MVADAPTER_STANDARD_PANEL_76.csv`,
  `MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json`,
  `MVADAPTER_LAYERWISE_76_REPORT.md`, `MVADAPTER_LAYERWISE_HASH_MANIFEST.json`
