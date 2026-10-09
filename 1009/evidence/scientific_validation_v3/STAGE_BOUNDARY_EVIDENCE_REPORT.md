# Stage-boundary evidence report — FRESH_CONFIRM_B

**Classification: `HEURISTIC_ONLY` (earlier label: `BOUNDARY-HEURISTIC`).** The four frozen profiles share a 10-step high pulse, the same per-layer nominal scale integrals, and the same native cap path; only pulse onset changes. This is a bounded sensitivity check, not an optimization search or evidence for a physical diffusion phase boundary.

The integrity gate passed before outcome analysis. Effects use paired objects (n=150), 10,000 percentile-bootstrap resamples, seed 20261002. For the primary FG-LPIPS endpoint, Holm correction is across four profile-versus-baseline contrasts; a separate three-test Holm family compares the 34/32/34 profile with each alternative. Bootstrap p-values at the 1/10,000 resolution floor are reported as upper bounds.

## Frozen schedule checks

| Profile | Pulse onset | High steps | Per-layer requested integral (D/M/S) | Cap activation (D/M/S) |
|---|---:|---|---:|---:|
| 20/60/20 | 40 | 40–49 | 75.0/75.0/27.5 | 0%/0%/0% |
| 30/40/30 | 35 | 35–44 | 75.0/75.0/27.5 | 0%/0%/0% |
| 34/32/34 | 33 | 33–42 | 75.0/75.0/27.5 | 0%/0%/0% |
| 40/20/40 | 30 | 30–39 | 75.0/75.0/27.5 | 0%/0%/0% |

## Frozen profiles versus shared low baseline

Negative FG-LPIPS and positive FG-PSNR favor the pulse. Holm is applied only to the four primary FG-LPIPS tests; other endpoints are descriptive.

| Profile | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ [95% CI] | Favorable objects |
|---|---:|---:|---:|---:|---:|
| 20/60/20 | -0.006617 [-0.007858, -0.005378] | 84.7% | ≤0.0004 | +0.5828 [+0.4995, +0.6695] | 92.7% |
| 30/40/30 | -0.004299 [-0.005435, -0.003139] | 80.0% | ≤0.0004 | +0.4208 [+0.3374, +0.5067] | 74.0% |
| 34/32/34 | -0.003575 [-0.004648, -0.002463] | 79.3% | ≤0.0004 | +0.3602 [+0.2803, +0.4427] | 66.7% |
| 40/20/40 | -0.002780 [-0.003763, -0.001756] | 77.3% | ≤0.0004 | +0.2774 [+0.2002, +0.3561] | 60.0% |

## 34/32/34 versus the other frozen onsets

The three-test Holm family is on FG-LPIPS. FG-PSNR and other endpoints are co-reported without a second confirmatory family.

| Contrast (34/32/34 minus comparator) | FG-LPIPS Δ [95% CI] | Favorable objects | Holm p | FG-PSNR Δ dB [95% CI] | Favorable objects |
|---|---:|---:|---:|---:|---:|
| 34/32/34 − 20/60/20 | +0.003042 [+0.002430, +0.003671] | 17.3% | ≤0.0003 | -0.2226 [-0.2631, -0.1818] | 12.7% |
| 34/32/34 − 30/40/30 | +0.000724 [+0.000545, +0.000905] | 26.0% | ≤0.0003 | -0.0606 [-0.0723, -0.0496] | 14.7% |
| 34/32/34 − 40/20/40 | -0.000795 [-0.001041, -0.000543] | 70.7% | ≤0.0003 | +0.0828 [+0.0663, +0.1000] | 80.7% |

## Co-reported baseline contrasts

Descriptive paired means; CIs and direction-aware win rates are in the analysis JSON.

| Profile | Full-PSNR | Full-LPIPS | FG-SSIM | Edge-SSIM | CIEDE2000 | Laplacian log error | RGB-std log error | Gradient log error | HF-energy log error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20/60/20 | +0.6231 [+0.5633, +0.6846] | -0.038036 [-0.041208, -0.034843] | +0.0150 [+0.0124, +0.0177] | +0.0107 [+0.0093, +0.0122] | -1.057118 [-1.253726, -0.858342] | +0.0429 [+0.0066, +0.0776] | -0.0385 [-0.0483, -0.0282] | -0.0258 [-0.0449, -0.0064] | -0.0068 [-0.0104, -0.0032] |
| 30/40/30 | +0.4235 [+0.3620, +0.4875] | -0.035360 [-0.038049, -0.032595] | +0.0182 [+0.0151, +0.0215] | +0.0076 [+0.0062, +0.0089] | -0.663108 [-0.849686, -0.477301] | +0.0587 [+0.0163, +0.1005] | -0.0375 [-0.0463, -0.0282] | -0.0323 [-0.0536, -0.0109] | -0.0035 [-0.0059, -0.0011] |
| 34/32/34 | +0.3574 [+0.2976, +0.4203] | -0.033703 [-0.036396, -0.030957] | +0.0169 [+0.0138, +0.0202] | +0.0054 [+0.0042, +0.0066] | -0.585484 [-0.761595, -0.408022] | +0.0412 [+0.0008, +0.0807] | -0.0394 [-0.0484, -0.0302] | -0.0342 [-0.0540, -0.0146] | -0.0035 [-0.0061, -0.0009] |
| 40/20/40 | +0.2605 [+0.2037, +0.3199] | -0.031212 [-0.033873, -0.028520] | +0.0156 [+0.0126, +0.0188] | +0.0027 [+0.0015, +0.0039] | -0.494636 [-0.667004, -0.323146] | +0.0114 [-0.0238, +0.0462] | -0.0436 [-0.0526, -0.0343] | -0.0338 [-0.0517, -0.0163] | -0.0034 [-0.0064, -0.0003] |

## Decision

Within this frozen family, later pulse onsets show a consistent primary-endpoint ordering: onset 40 (20/60/20) performs best, followed by 35 (30/40/30), then 33 (34/32/34), then 30 (40/20/40). The direct FG-LPIPS contrasts after the predeclared three-test Holm correction favor onset 40 and 35 over 33, while 33 outperforms onset 30. This is evidence that pulse position matters in this family; it does not support the exact one-third boundary as a discovered phase transition or establish onset 40 as a universal optimum.

The four equal-duration comparisons are bounded evidence about this pulse family only. A non-significant difference would not be an equivalence claim because no equivalence margin was frozen.

Use thirds as a convenient discretization (`BOUNDARY-HEURISTIC`); the observed onset gradient should be reported as a fixed-family sensitivity result, not used to select or tune a replacement boundary.

## Provenance

- Frozen design: `STAGE_BOUNDARY_PROTOCOL_LOCK.md`.
- Integrity gate: `B_FORMAL_INTEGRITY_GATE.md` (PASS).
- Complete paired estimates: `formal/campaign_FRESH_CONFIRM_B_20261005/BOUNDARY_SENSITIVITY_ANALYSIS.json`.
- Texture extension: `formal/campaign_FRESH_CONFIRM_B_20261005/boundary_texture_extension_per_object.csv`.
