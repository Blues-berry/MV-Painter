# Cross-backbone / cross-domain validation addendum

Date: 2026-09-29  
Status: **WITH LIMITATIONS; no universal transfer claim**

This addendum records the reviewer-facing interpretation of the existing
MV-Adapter evidence and the newly completed strict TRB development check. It
does not pool scores produced by different interfaces or backbones.

## What is actually validated

The completed second-backbone evidence is an Exact Mesh MV-Adapter evaluation
covering 76 objects, 50 denoising steps and 11 evaluated schedule/condition
rows. The equal-budget follow-up contains four conditions with the same nominal
mean scale. It is sufficient to test whether temporal placement changes the
observed metrics inside the MV-Adapter pipeline; it is not sufficient to claim
that the same schedule transfers to every geometry-conditioned backbone.

The new strict TRB run is a separate 24-object clean-v2 development pilot on
the main GeoTex/MVPainter checkpoint. It was used only to test whether a
runtime residual-budget controller deserved one locked holdout. Its integrity
checks passed, but its primary FG-LPIPS gate failed against C3_TCAS, so no
holdout was started and no new cross-backbone claim is added.

## MV-Adapter equal-budget result

| condition | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS ↓ | GT-relative texture error ↓ |
|---|---:|---:|---:|---:|---:|
| fixed-mean | 13.337215 | 0.527776 | 0.240051 | 0.188163 | 2.202812 |
| HLL | 13.320944 | 0.526805 | 0.239621 | 0.188194 | 2.232062 |
| LHL | 13.344064 | 0.528325 | 0.240235 | 0.188051 | 2.269096 |
| LLH | 13.353306 | 0.527814 | 0.239974 | 0.188346 | 2.198930 |

The paired comparisons give a narrow, metric-specific stage-placement signal:
LHL−HLL Edge-SSIM is `+0.000613` with 95% CI `[+0.000135,+0.001217]`, and
LHL−LLH Edge-SSIM is `+0.000261` with CI `[+0.000032,+0.000522]`. This does
not make LHL a practical winner: LLH has the highest PSNR and lower texture
error, while LHL's advantage is confined to selected structure metrics.

Against fixed-low, LHL has raw paired deltas of PSNR `−0.013114`
(CI `[−0.062438,+0.020680]`), FG-SSIM `+0.000785`
(CI `[+0.000110,+0.001568]`), Edge-SSIM `+0.000238`
(CI `[−0.000026,+0.000532]`), and FG-LPIPS `+0.000358`
(CI `[−0.000476,+0.001396]`). The mixed directions and zero-crossing
intervals support “stage sensitivity / non-uniform trade-off”, not “uniform
improvement”. The frozen CAI rule remains undefined/set-valued, and
pretraining-UID disjointness is not established.

## Strict TRB development gate

The corrected pilot used the predeclared clean-v2 24-object list, unique6
views `[0,15,12,16,13,14]`, shared object latents, 50 steps, AlexNet LPIPS,
Edge-SSIM, 168 saved paired maps and 24 calibration budgets.

| comparison | TRB−comparator FG-LPIPS | 95% paired bootstrap CI | result |
|---|---:|---:|---|
| fixed-low | `−0.005508` | `[−0.007830,−0.003391]` | passes this comparison |
| C3_TCAS | `+0.001302` | `[+0.000092,+0.002538]` | fails; C3 is better |

TRB's mean calibration time was `6.082 s/object`; including calibration, its
mean cost was `12.342 s/object`, about `2.01×` fixed-low inference. The
development result is therefore **not promoted** and the strict 276-object
holdout was correctly not launched. The full machine-readable audit is in
`STRICT_TRB_DEVELOPMENT_AUDIT_20260929.json` and the reusable checker is
`scripts/audit_strict_trb_development.py`.

## MVDiffusion boundary

The deployed MVDiffusion depth branch remains an interface diagnostic, not a
paper-quality absolute cross-backbone baseline. Its 75-object/50-step summary
is interop PSNR `10.1036`, interop foreground SSIM `0.3154` and interop
Edge-SSIM `0.2189`, but it uses an orthographic-to-pinhole conversion, known
target geometry in the input, and a locally compatible base with a
zero-initialized extra depth channel. Those values must not be pooled with the
native MVPainter or MV-Adapter tables.

## Permitted revision language

The evidence supports: “temporal placement produces measurable, but
metric-dependent, differences within the second backbone; the observed
trade-off does not establish a universally dominant schedule or a unique CAI
winner.” It does not support absolute score transfer across backbones,
pretraining-disjointness claims, causal mechanism claims, or describing LHL
or TRB as a confirmed practical winner.

Primary sources:

- `final/round2/mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.csv`
- `final/round2/mv_adapter/MV_ADAPTER_PAIRED_COMPARISONS.json`
- `final/round2/mv_adapter/MV_ADAPTER_FINAL_INTERPRETATION.md`
- `final/round2/mvdiffusion/MVDIFFUSION_INTEROP.md`
- `final/round2/coordination/STRICT_TRB_DEVELOPMENT_AUDIT_20260929.md`
