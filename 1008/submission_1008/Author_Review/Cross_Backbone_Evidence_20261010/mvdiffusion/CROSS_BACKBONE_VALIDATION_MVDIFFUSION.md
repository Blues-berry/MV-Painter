# Cross-Backbone Validation — MVDiffusion (Third Backbone)

Date: 2026-10-01. Branch: `codex/next-review-response-20260930`.
Task: Round-2 cross-backbone final experiment (Phase C + Phase D).
Scope: SD2-depth native mirror resolution + controllable-residual validation;
experiment facts and conclusions only — no paper text was modified.

## 1. SD2-depth native mirror (Phase C)

Full record: `final/round2/mvdiffusion/MVDIFFUSION_SD2_DEPTH_DOWNLOAD.md`.

- Connectivity: `sd2-community/stable-diffusion-2-depth` public, commit
  `6cb92dd9430a7f6da8d9e99d7b60acdebcc348b7`. Download initially blocked by
  egress-proxy 502s, completed after recovery via resumable
  `snapshot_download` (priority: vae -> unet/text fp bins -> ema ckpt).
- Section 26 check **PASS**: `StableDiffusionDepth2ImgPipeline` loads locally;
  `UNet in_channels = 5` (native depth-concat base, as required by the
  deployed DepthGenerator).
- Section 27 **POSTLOAD_STATE_EQUIVALENT = YES**: constructing DepthGenerator
  on both bases (`sd21_depth_compat` vs native mirror) and strict-loading the
  identical `depth_gen_new.pth` gives 1552/1552 bitwise-identical tensors
  (SHA-256 + max/mean abs diff per tensor; zero name/shape/dtype/value diffs).
- Section 28 **OUTPUT_EQUIVALENT = YES**: obj_0024, official runner, seed 42,
  50 steps — 12/12 views PNG SHA-256 bitwise equal; max abs pixel diff 0.
- Section 29 verdict: `NATIVE_MIRROR_EQUIVALENT = YES`; no 75-object rerun
  required; the archived deployment (and the panel below) remain valid, with
  the mirror as a bitwise-equivalent provenance upgrade.

## 2. Controllable-residual audit (Phase D)

Full document: `final/round2/mvdiffusion/MVDIFFUSION_RESIDUAL_CONTROL_AUDIT.md`.

- Deployed generation path: depth enters via latent concat
  (`cat([latents, depth_inv_norm])`, 5-channel `conv_in`) — a **prohibited
  surface** (scaling it would scale the depth input). The literal additive
  condition branches are inactive in this path.
- Active controllable modules: 9 CPBlocks (correspondence-aware attention),
  replacement semantics `y = CPBlock(x)`, applied after each down/mid/up
  segment.
- **Classification: PARTIAL** — no independent additive branch on the deployed
  path, but an exact, inference-only, weight-frozen residual-scale interface
  exists: `y_alpha = (1 - alpha) x + alpha y` with `Delta = y - x` scaled by
  alpha; alpha = 1 is bitwise the original model.
- Pre-registered mechanical mapping (topology only): scheduled surface = the
  5 decoder-side CPBlocks; deep = {mid, up_0}, middle = {up_1},
  shallow = {up_2, up_3} (two independent reasonings converge: relative-depth
  fraction thresholds and resolution-level alignment; encoder CPBlocks stay at
  alpha = 1). Normalized profile (weighted mean 1.0, point-count weights
  2/1/2): deep = middle = 1.3502458265122749, shallow = 0.4746317504091673.
- Frozen scales: low = 0.75, high = 1.00, fixed mean = 5/6, boundaries 1/3
  and 2/3 — identical to the MV-Adapter freeze; no recalibration.

## 3. Identity gate

`IDENTITY` condition (alpha identically 1 at every scheduled point, strict
interpolation path, no shortcut), 3 objects x 12 views, seed 42: **PASS,
36/36 PNG SHA-256 bitwise equal** to the official model. (A first attempt
with a mis-specified condition applying layer multipliers at alpha = 1.35/0.47
produced different outputs as expected; it was discarded and rerun correctly.)
Deployment reproducibility: official rerun vs archived grids 36/36 bitwise.

## 4. Runs

75-object holdout, official deployment base `sd21_depth_compat` (unchanged),
seed 42, 50 DDIM steps, 12 views: R0 = archived official unmodified run;
new scheduled conditions G-FL, G-LHL, G-LLH (global alpha) and L-FIX, L-LHL,
L-LLH (layer-wise alpha) = **450 new 12-view generations**. Metrics: unified
6-metric set via `scripts/evaluate_mvdiffusion_depth_ext.py` (legacy interop
PSNR/SSIM values reproduced exactly, diff 0.0 vs archived CSV; FG-LPIPS /
CIEDE2000 / GT-texture added with the same geotex functions as the MV-Adapter
runner; obj_0029 views with near-empty GT foreground are NaN at view level —
reported, not faked).

## 5. Panel means (7 conditions)

| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| R0 | 10.103600 | 0.315352 | 0.218925 | 0.206795 | 32.309273 | 1.118610 |
| G-FL | 9.978809 | 0.314607 | 0.198513 | 0.203837 | 31.801392 | 1.066277 |
| G-LHL | 10.070471 | 0.314459 | 0.200250 | 0.204955 | 31.781372 | 1.081426 |
| G-LLH | 9.991708 | 0.314459 | 0.198779 | 0.203583 | 31.797233 | 1.048759 |
| L-FIX | 9.617544 | 0.294686 | 0.195399 | 0.207671 | 33.091787 | 1.021080 |
| L-LLH | 9.524981 | 0.295215 | 0.192572 | 0.206582 | 33.174413 | 0.983991 |
| L-LHL | 9.549824 | 0.293029 | 0.192968 | 0.207446 | 33.326652 | 0.982505 |

## 6. Paired comparisons (10,000 object bootstrap, seed 20260928)

Positive favors the left condition (LPIPS/dE00/GT-texture lower-better);
`*` = 95% CI excludes 0. n = 75 for every metric.

| comparison | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | dE00 | GT-texture |
|---|---:|---:|---:|---:|---:|---:|
| P1 L-LLH vs G-FL | -0.4538* | -0.0194* | -0.0059* | -0.0027 | -1.3730* | +0.0823* |
| P2 L-LLH vs G-LLH | -0.4667* | -0.0192* | -0.0062* | -0.0030 | -1.3772* | +0.0648* |
| P3 L-LLH vs L-FIX | -0.0926* | +0.0005 | -0.0028* | +0.0011 | -0.0826 | +0.0371 |
| P4 L-LHL vs G-LHL | -0.5206* | -0.0214* | -0.0073* | -0.0025 | -1.5453* | +0.0989* |
| P5 G-LLH vs G-LHL | -0.0788 | -0.0000 | -0.0015 | +0.0014* | -0.0159 | +0.0327 |

Full records: `final/round2/mvdiffusion/MVDIFFUSION_PAIRED_BOOTSTRAP.json`.

## 7. Conclusions (experiment-level)

- **Layer-wise effect: NOT_REPLICATED (negative/mixed, preserved as found).**
  On this backbone the layer-wise intervention trades structure/color fidelity
  for a small texture-error gain: PSNR, FG-/Edge-SSIM and dE00 consistently
  and significantly favor the GLOBAL conditions (P1, P2, P4), while
  GT-relative texture error consistently and significantly favors the
  LAYER-WISE conditions; FG-LPIPS is not separated.
- **Temporal position:** P3 shows small significant PSNR and Edge-SSIM
  differences against L-LLH vs L-FIX (other metrics ns); P5 is ns except a
  small LPIPS term favoring G-LHL.
- **Interface caveat (carried into any paper wording):** the scheduled surface
  is correspondence-aware attention — a serial, feature-derived module — not
  an independent geometry-residual branch like the T2I-Adapter-style injection
  scaled on MV-Adapter. No absolute cross-backbone score pooling is performed;
  only within-backbone paired contrasts are valid.
- Per the no-tuning rule: no re-search of scales, mapping, or schedules was
  performed and the negative direction was not "fixed".

## 8. Artifact index

- `final/round2/mvdiffusion/MVDIFFUSION_RESIDUAL_CONTROL_AUDIT.md`
- `final/round2/mvdiffusion/MVDIFFUSION_SD2_DEPTH_DOWNLOAD.md`
- `final/round2/mvdiffusion/results/phase_c_logs/` (connectivity, download
  logs, load check, `MVDIFFUSION_POSTLOAD_OUTPUT_EQUIVALENCE.md`,
  `postload_equivalence.json`)
- `scripts/run_mvdiffusion_schedule.py`,
  `scripts/evaluate_mvdiffusion_depth_ext.py`,
  `scripts/mvdiffusion_postload_equivalence.py`,
  `scripts/analyze_mvdiffusion_panel_20260930.py`
- `final/round2/mvdiffusion/results/panel_{G-FL,G-LHL,G-LLH,L-FIX,L-LHL,L-LLH}_75/`,
  `phase_d_identity_{official,alpha1}/`, `phase_c_output_eq_{compat,mirror}/`
- `final/round2/mvdiffusion/MVDIFFUSION_STANDARD_PANEL_RESULTS.csv`,
  `MVDIFFUSION_STANDARD_PANEL_REPORT.md`, `MVDIFFUSION_PAIRED_BOOTSTRAP.json`
