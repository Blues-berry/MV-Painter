# MV-Adapter Layer-wise 76-Object Report (Second Backbone)

Experiment facts only. Branch `codex/next-review-response-20260930`,
date 2026-09-30. Protocol: `MVADAPTER_LAYERWISE_PROTOCOL.md`
(pre-registered); profile: `layer_profile_transfer.json` (frozen).

## Gates

- IDENTITY_AUDIT = **PASS** (wrapper with multipliers = 1.0 is
  bitwise identical to the global runner on 3 objects x G-FL/G-LHL/G-LLH;
  PNG SHA-256, pixels, max abs diff 0, metrics equal; cond_encoder shapes
  `[12,320,64,64],[12,640,32,32],[12,1280,16,16],[12,1280,8,8]`).
- SMOKE = **PASS** (technical checks only).

## New runs

3 conditions x 76 objects = 228 new rows, all `exact_mesh`, all metrics
finite: `holdout_exact_layer_fixed_76` (L-FIX), `holdout_exact_layer_llh_76`
(L-LLH), `holdout_exact_layer_lhl_76` (L-LHL). Seed 20260928, 50 steps,
low 0.75, high 1.00 (frozen; no recalibration).

## Standard panel means (7 conditions)

| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| R0 | 13.114180 | 0.498481 | 0.233429 | 0.183496 | 20.719805 | 1.700798 |
| G-FL | 13.357177 | 0.527539 | 0.239997 | 0.187693 | 20.149543 | 2.224047 |
| G-LHL | 13.344064 | 0.528325 | 0.240235 | 0.188051 | 20.182146 | 2.269096 |
| G-LLH | 13.353306 | 0.527814 | 0.239974 | 0.188346 | 20.157122 | 2.198930 |
| L-FIX | 13.431922 | 0.523473 | 0.239052 | 0.187647 | 19.877910 | 1.903374 |
| L-LLH | 13.453797 | 0.523564 | 0.238899 | 0.187731 | 19.805120 | 1.913272 |
| L-LHL | 13.446348 | 0.525148 | 0.239619 | 0.187920 | 19.868912 | 1.980378 |

## Paired comparisons (10,000 object bootstrap, seed 20260928)

Deltas direction-adjusted so positive favors the left condition
(LPIPS/dE00/GT-texture are lower-better). * = 95% CI excludes 0.

| comparison | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| P1_L-LLH_vs_G-FL | +0.0966* [+0.0149,+0.1863] | -0.0040* [-0.0072,-0.0011] | -0.0011* [-0.0022,-0.0001] | -0.0000 [-0.0022,+0.0018] | +0.3444* [+0.1624,+0.5484] | +0.3108* [+0.1283,+0.5235] |
| P2_L-LLH_vs_G-LLH | +0.1005* [+0.0164,+0.1940] | -0.0042* [-0.0075,-0.0014] | -0.0011* [-0.0022,-0.0001] | +0.0006 [-0.0014,+0.0024] | +0.3520* [+0.1618,+0.5651] | +0.2857* [+0.0928,+0.5084] |
| P3_L-LLH_vs_L-FIX | +0.0219 [-0.0212,+0.0641] | +0.0001 [-0.0013,+0.0014] | -0.0002 [-0.0011,+0.0006] | -0.0001 [-0.0008,+0.0005] | +0.0728* [+0.0044,+0.1567] | -0.0099 [-0.0886,+0.0778] |
| P4_L-LHL_vs_G-LHL | +0.1023* [+0.0226,+0.1958] | -0.0032* [-0.0059,-0.0007] | -0.0006 [-0.0015,+0.0002] | +0.0001 [-0.0022,+0.0021] | +0.3132* [+0.1531,+0.4869] | +0.2887* [+0.1043,+0.5045] |
| P5_G-LLH_vs_G-LHL | +0.0092 [-0.0227,+0.0554] | -0.0005 [-0.0012,+0.0001] | -0.0003* [-0.0005,-0.0000] | -0.0003 [-0.0012,+0.0007] | +0.0250 [-0.0321,+0.1083] | +0.0702 [-0.0502,+0.2164] |

Full mean/median/CI/win-rate records: `MVADAPTER_LAYERWISE_PAIRED_BOOTSTRAP.json`.

## Reading (experiment-level conclusion, no paper edits)

- Layer-wise vs global (P1, P2, P4): PSNR, dE00 and GT-relative texture
  error consistently favor the layer-wise conditions (CI excludes 0 for
  all three pairs); FG-SSIM and Edge-SSIM consistently favor global by a
  small margin; FG-LPIPS is not separated. The layer-wise effect exists
  (SUPPORTED) but its direction is metric-dependent.
- Temporal-position effect within the frozen scales (P3 L-LLH vs L-FIX,
  P5 G-LLH vs G-LHL): not separated except a marginal dE00 term in P3.
  (NOT_SUPPORTED at this protocol.)
- Per task §42 these are reported as found; no re-search was performed.
