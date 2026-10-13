# REPORT — Core-7 same-runner strict-276 confirmation (2026-10-01)

Protocol: PROTOCOL_LOCK_CORE7_COMPLETION.md (frozen before any observation).
The two added conditions completed 276/276 rows each (formal_no_adapter/,
formal_global_fixed_high/), on the byte-identical R0 protocol
(layer-confirmation-strict276-v1 code path, object_seed = 42+idx, latent
seed 42, same config/checkpoint/list/metrics as the frozen Core-5).

Gates: preflight PASS-a/b/c (GFL anchor bit-exact vs frozen R0 rows;
cross-method and cross-process input hashes identical); in-run integrity
0 aborts; post-hoc cross-process hash audit 0/276 mismatches
(SHARED_INPUT_AUDIT_CORE7.json).

## The Core-7 matrix (same cohort + runner + realization + shared input)

| ID | condition | FG-PSNR | FG-SSIM | FG-LPIPS | Full-PSNR | Full-SSIM | Full-LPIPS | Edge-SSIM |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | no_adapter | 8.826 | **0.480** | 0.2059 | 10.563 | 0.728 | 0.6260 | 0.479 |
| 2 | global_fixed_low (GFL) | 10.731 | 0.399 | 0.1917 | 18.229 | 0.844 | 0.2107 | 0.520 |
| 3 | global_fixed_high (GFH) | 13.153 | 0.478 | 0.1677 | 18.242 | 0.850 | **0.1967** | **0.554** |
| 4 | global_c3 | 11.939 | 0.430 | 0.1817 | 18.968 | 0.851 | 0.2029 | 0.528 |
| 5 | layer_fixed_mean | 13.100 | 0.455 | 0.1698 | 19.516 | 0.850 | 0.2082 | 0.536 |
| 6 | layer_lhl | 12.974 | 0.445 | 0.1719 | 19.635 | 0.849 | 0.2278 | 0.527 |
| 7 | **layer_llh** | **13.975** | 0.462 | **0.1610** | **20.828** | **0.851** | 0.1988 | 0.548 |

(exact values in aggregate_metrics_core7.csv; the table above is rounded
for reading. Rankings incl. all metrics: core7_rankings.json.)

## Primary comparisons (paired bootstrap, 10k resamples, seed 20260930;
raw delta = first minus second, no sign reversal; * = 95% CI excludes 0)

### Reviewer-1 gate 1: unmodified pipeline
`layer_llh − no_adapter` (higher is better unless noted):
FG-PSNR **+5.149*** [+4.896, +5.396], Full-PSNR **+10.265***, Full-SSIM
**+0.123***, Edge-SSIM **+0.068***, FG-LPIPS **−0.0449*** (LLH better).
One honest reversal: FG-SSIM **−0.018*** favors no_adapter — the
adapter-free pipeline is blurrier (lowest FG gradient energy of all seven
conditions) and blur raises SSIM while destroying PSNR/LPIPS. Reported,
not hidden. Win rate 0.97/1.00/0.00 (FG-PSNR/Full-PSNR/Full-LPIPS).

### Reviewer-1 gate 2: competitive fixed-scale baseline
`layer_llh − global_fixed_high`:
FG-PSNR **+0.822*** [+0.617, +1.033], Full-PSNR **+2.585*** [+2.400,
+2.769], FG-LPIPS **−0.0068*** (LLH better), Full-SSIM **+0.0016*** (LLH);
fixed_high better on FG-SSIM **−0.016***, Edge-SSIM **−0.006*** and
Full-LPIPS **+0.0021*** (all small; win rates 0.21-0.62). LLH dominates
the competitive fixed baseline on the primary fidelity metrics and is
marginally behind on three secondary ones.

### Does the adapter help at all (same runner)?
`no_adapter − global_fixed_low`: Full-PSNR **−7.666***, Full-SSIM
**−0.116***, FG-PSNR **−1.905***, Edge-SSIM **−0.041***, FG-LPIPS
+0.0142*** (worse). The residual adapter at the frozen fixed-low scale is
strongly beneficial under the shared-input protocol; FG-SSIM again favors
the blurrier adapter-free output (+0.081*).

### Fixed-scale direction
`global_fixed_high − global_fixed_low`: FG-PSNR **+2.422***, FG-SSIM
+0.080*, Edge-SSIM +0.034*, Full-PSNR +0.014 (ns). fixed-high is the
competitive fixed baseline claimed.

### Texture-fidelity extension (GT-relative errors; lower is better;
TEXTURE_FIDELITY_EXTENSION_*.csv/json)
`layer_llh − global_fixed_low`: grad_err **−0.510***, lap_err **−1.883***,
rgbstd_err **−0.429***, hf_err **−0.055*** — LLH matches the GT texture
statistics significantly better than fixed-low on ALL four diagnostics.
vs layer_lhl: 3/4 favor LLH (grad/lap/rgbstd), hf_err +0.006* marginal.
vs no_adapter: lap_err −1.98* (LLH), grad/rgbstd ns, hf_err +0.010* —
mixed, consistent with the blur/energy story above.

## Honest-claims summary

1. Under the cleanest same-runner protocol, LLH is the best of seven
   conditions on FG-PSNR, FG-LPIPS, Full-PSNR, Full-SSIM and all four
   GT-relative texture errors, and beats both Reviewer-1 baselines on the
   primary fidelity metrics.
2. FG-SSIM ranks no_adapter first (blur artifact of the adapter-free
   pipeline); fixed_high leads Full-LPIPS by 0.002 and Edge-SSIM by 0.006
   over LLH. These reversals are small but significant and are reported
   verbatim.
3. The seven-condition table retires the need to quote any cross-runner
   or archived numbers for the baseline family.

## Mechanism note (texture-energy calibration)

Mean foreground gradient magnitude vs GT (276 objects):
no_adapter 0.89x GT (undershoot; blur), global_fixed_low **1.54x GT
(overshoot)**, layer_llh **1.13x GT (closest)**. The adapter residuals at
the frozen fixed-low scale inject excess high-frequency energy (which
also produces its higher seam discontinuity in the bake audit); LLH's
late-stage high / shallow-low profile calibrates the injected energy
closest to GT. This single mechanism explains simultaneously: LLH's
texture-error advantage, fixed-low's gradient overshoot, and why
adapter-free output wins FG-SSIM (blur rewards SSIM while destroying
PSNR/LPIPS).
