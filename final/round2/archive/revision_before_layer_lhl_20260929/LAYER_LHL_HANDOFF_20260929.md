# Layer-LHL evidence handoff

Date: 2026-09-29 UTC  
Status: **VERIFIED FOR HANDOFF / PAPER NARRATIVE REVISION REQUIRED**

This handoff records a temporary, inference-only layer-wise schedule result. It
does not modify the manuscript, response letter, checkpoint, or existing
baseline tables.

## Frozen protocol

- Checkpoint: `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt`
- Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`
- Evaluation cohort: strict clean-v2 holdout, 276 objects `obj_0024`–`obj_0299`
- Object-list SHA-256: `a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044`
- Target views: unique6 `[0, 15, 12, 16, 13, 14]`
- Resolution/steps/seed: 256×256, 50 Euler steps, seed 42
- Metrics: the same formal full/foreground/LPIPS/edge path used by the clean-v2 evaluation

The candidate schedule is:

- deep: `[1.25, 2.50, 1.25]` for early/middle/late steps;
- middle: `[1.25, 2.50, 1.25]`;
- shallow: `[0.50, 0.75, 0.50]`.

The schedule is applied through the existing `GeoTexResnetWrapper` depth groups;
the shallow group also obeys the existing `0.8` implementation cap. This is a
sampling/inference schedule, not a newly trained checkpoint.

## Verified result

Means over the same 276-object cohort:

| method | Full PSNR | Full SSIM | Full LPIPS | FG PSNR | FG SSIM | FG LPIPS | Edge SSIM |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed-low | 15.086 | 0.8503 | 0.1936 | 7.030 | 0.3548 | 0.2024 | 0.5003 |
| C3/LHL | 14.875 | 0.8549 | 0.1895 | 6.763 | 0.3483 | 0.2013 | 0.5000 |
| LLH | 15.136 | 0.8518 | **0.1809** | 6.937 | 0.3569 | 0.1995 | 0.5355 |
| layer-LHL | **22.052** | **0.8841** | 0.1857 | **14.776** | **0.5510** | **0.1338** | **0.5533** |

Layer-LHL minus fixed-low is:

- Full PSNR `+6.965 dB`, paired 95% CI `[+6.492, +7.460]`;
- Full SSIM `+0.0339`, CI `[+0.0315, +0.0364]`;
- FG PSNR `+7.747 dB`, CI `[+7.151, +8.363]`;
- FG SSIM `+0.1962`, CI `[+0.1816, +0.2112]`;
- Full LPIPS `−0.00787`, CI `[−0.01339, −0.00243]`;
- FG LPIPS `−0.06868`, CI `[−0.07557, −0.06224]`.

Relative to GT texture probes, layer-LHL also reduces mean RGB-std error by
`0.01517`, Laplacian-variance error by `0.00855`, and HF-energy error by
`0.06080` versus fixed-low. The gradient-error reduction is `0.01977`, but its
paired interval reaches zero and must be described as a trend, not a decisive
claim.

## Reliability audit

The independent temporary verifier returned `PASS` with 8,910 checks:

- 138 head rows + 138 tail rows = 276 unique candidate rows;
- 138 + 138 prediction PNGs;
- exact object-index mapping and finite metrics;
- main and stage baseline CSVs have the same 276 object keys;
- strict holdout is exactly positions 24–299 of the frozen 300-object list;
- checkpoint and object-list hashes match the formal manifests;
- `obj_0024` GT PNG matches the existing formal-stage GT;
- same-GPU duplicate runs produce identical PNG MD5 and metrics;
- cross-GPU `obj_0024` PNG and metrics also match exactly.

The verifier artifact is:
`/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/handoff_verification.json`.

## Scientific interpretation

The old conclusion “C3/LHL is the optimum” is rejected. The safe conclusion is:

> Layer-wise stage-aware scaling substantially improves foreground and global
> fidelity on this fixed clean-v2 protocol, while schedule utility remains
> metric-dependent and no universal schedule dominates every metric.

LLH still has the lowest mean Full-LPIPS (`0.1809` versus layer-LHL `0.1857`),
so layer-LHL must not be described as the global winner on every metric. C3
must not be described as uniquely optimal or universally superior. The LML
probe was weaker and was not promoted to paper evidence.

## Evidence locations

The machine-readable v2 evidence remains in the temporary directory:

- `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/per_object_metrics.csv`
- `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/official_comparisons.json`
- `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/layer_official_v2_merged/texture_error_comparisons.json`
- `/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/FINAL_DECISION.md`

Before submission, these temporary artifacts should be archived into the
reproducibility package or regenerated from the pinned source hashes. No
manuscript edit is authorized by this handoff alone.
