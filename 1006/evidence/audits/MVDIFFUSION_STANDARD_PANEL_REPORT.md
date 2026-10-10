# MVDiffusion Standard Panel Report (Third Backbone, PARTIAL interface)

Experiment facts only. Branch `codex/next-review-response-20260930`, 2026-09-30.
Audit: `MVDIFFUSION_RESIDUAL_CONTROL_AUDIT.md` (classification PARTIAL;
interface = exact convex interpolation on the 5 decoder-side CPBlocks,
alpha = layer_multiplier x temporal_scale, frozen low/high/mean).

## Gates

- IDENTITY (alpha identically 1 at every scheduled point, strict path):
  **PASS**, 36/36 PNG SHA-256 bitwise equal to the official model
  (obj_0024-obj_0026 x 12 views, seed 42, 50 steps).
- Deployment reproducibility: official rerun vs archived 75-object grids:
  36/36 PNG SHA-256 equal.
- SD2-depth native mirror: download BLOCKED (egress proxy 502; see
  `MVDIFFUSION_SD2_DEPTH_DOWNLOAD.md`). All conditions therefore ran on the
  unchanged deployment base `sd21_depth_compat` with the archived seeds, so
  every paired comparison is internal to one base.

## Runs

R0 = archived official unmodified deployment (75 objects). New scheduled
conditions: G-FL, G-LHL, G-LLH (global alpha schedules) and L-FIX, L-LHL,
L-LLH (layer-wise alpha, decoder mapping deep={mid,up0}, middle={up1},
shallow={up2,up3}, normalized multipliers deep=middle=1.3502458265122749,
shallow=0.4746317504091673) x 75 objects x 50 steps, seed 42. 450 new
12-view generations.

## Panel means (7 conditions)

| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| R0 | 10.103600 | 0.315352 | 0.218925 | 0.206795 | 32.309273 | 1.118610 |
| G-FL | 9.978809 | 0.314607 | 0.198513 | 0.203837 | 31.801392 | 1.066277 |
| G-LHL | 10.070471 | 0.314459 | 0.200250 | 0.204955 | 31.781372 | 1.081426 |
| G-LLH | 9.991708 | 0.314459 | 0.198779 | 0.203583 | 31.797233 | 1.048759 |
| L-FIX | 9.617544 | 0.294686 | 0.195399 | 0.207671 | 33.091787 | 1.021080 |
| L-LLH | 9.524981 | 0.295215 | 0.192572 | 0.206582 | 33.174413 | 0.983991 |
| L-LHL | 9.549824 | 0.293029 | 0.192968 | 0.207446 | 33.326652 | 0.982505 |

## Paired comparisons (10,000 object bootstrap, seed 20260928)

Positive favors the left condition (LPIPS/dE00/GT-texture lower-better).
* = 95% CI excludes 0. n=75 for all metrics (obj_0029 texture/CIEDE2000
views with near-empty GT foreground are NaN at view level and excluded by
nanmean; no object dropped).

| comparison | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| P1_L-LLH_vs_G-FL | -0.4538* [-0.7521,-0.1605] | -0.0194* [-0.0294,-0.0099] | -0.0059* [-0.0103,-0.0014] | -0.0027 [-0.0076,+0.0018] | -1.3730* [-2.3747,-0.4182] | +0.0823* [+0.0201,+0.1453] |
| P2_L-LLH_vs_G-LLH | -0.4667* [-0.7676,-0.1748] | -0.0192* [-0.0292,-0.0097] | -0.0062* [-0.0106,-0.0016] | -0.0030 [-0.0078,+0.0015] | -1.3772* [-2.3936,-0.4009] | +0.0648* [+0.0051,+0.1244] |
| P3_L-LLH_vs_L-FIX | -0.0926* [-0.1823,-0.0032] | +0.0005 [-0.0037,+0.0049] | -0.0028* [-0.0052,-0.0004] | +0.0011 [-0.0005,+0.0027] | -0.0826 [-0.4102,+0.2353] | +0.0371 [-0.0003,+0.0811] |
| P4_L-LHL_vs_G-LHL | -0.5206* [-0.8109,-0.2321] | -0.0214* [-0.0323,-0.0111] | -0.0073* [-0.0114,-0.0032] | -0.0025 [-0.0072,+0.0019] | -1.5453* [-2.5268,-0.5927] | +0.0989* [+0.0443,+0.1546] |
| P5_G-LLH_vs_G-LHL | -0.0788 [-0.1639,+0.0045] | -0.0000 [-0.0023,+0.0024] | -0.0015 [-0.0035,+0.0006] | +0.0014* [+0.0001,+0.0026] | -0.0159 [-0.2990,+0.2648] | +0.0327 [-0.0026,+0.0682] |

## Reading (experiment-level conclusion, no paper edits)

- Layer-wise vs global (P1, P2, P4): PSNR, FG-/Edge-SSIM and dE00
  consistently and significantly favor the GLOBAL conditions; GT-relative
  texture error consistently and significantly favors the LAYER-WISE
  conditions; FG-LPIPS is not separated. On this backbone the layer-wise
  intervention trades structure/color fidelity for a small texture-error
  gain: the layer-wise scheduling advantage is NOT replicated (negative/
  mixed result, preserved as found per the no-tuning rule).
- Temporal position within layer-wise (P3): small significant PSNR and
  Edge-SSIM differences against L-LLH vs L-FIX; other metrics ns.
  Global LLH vs LHL (P5): ns except a small LPIPS term favoring G-LHL.
- Interface caveat (PARTIAL): the scheduled surface is correspondence-
  aware attention (serial, feature-derived), not an independent geometry-
  residual branch; cross-backbone comparison of the layer-wise direction
  must carry this classification, and no absolute cross-backbone score
  pooling is performed.
