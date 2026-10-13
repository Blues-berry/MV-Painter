# Core-7 final provenance audit — 2026-10-01

## Row-level source matrix

The independent script `scripts/final_core7_forensic_stats_20261001.py` reads
the seven per-condition serialized CSVs listed in `CORE7_ROW_AUDIT.json`.
It verified **276 unique indices per condition (1,932 rows total)**, exact
`0..275` index coverage, no duplicate/missing rows, no non-finite numeric
fields, correct schedule labels, identical object labels by index, and
bit-identical serialized GT texture statistics across methods.

| Condition | Per-object rows | Source |
|---|---:|---|
| No Adapter | 276 | `core7_same_runner_completion_20261001/formal_no_adapter/per_object_metrics.csv` |
| GFL | 276 | `final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930/global_fixed_low_per_object_metrics.csv` |
| GFH | 276 | `core7_same_runner_completion_20261001/formal_global_fixed_high/per_object_metrics.csv` |
| GC3 | 276 | `main_backbone_robustness1_20260930/r0_completion_global_c3/per_object_metrics.csv` |
| LFM | 276 | `layer_confirmation_20260930/layer_fixed_mean_per_object_metrics.csv` |
| LHL | 276 | `layer_confirmation_20260930/layer_lhl_per_object_metrics.csv` |
| LLH | 276 | `layer_confirmation_20260930/layer_llh_per_object_metrics.csv` |

The protocol manifests agree on checkpoint SHA-256
`0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`, strict
object-list SHA-256
`a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044`,
50-step Euler sampling, `unique6` views `[0,15,12,16,13,14]`, and
`geotex.eval_exploration.compute_metrics`. R0 uses per-object seed `42+idx`;
the latent is reset to seed 42 before creation and again before generation.
The two newly run formal arms serialize six input hashes per object; the
existing shared-input report finds 0/276 mismatches between them.

**Serialization limit:** the five original Core-5 CSVs do not contain
per-object tensor hashes. Their pinned protocol and runner reset the same
Python/NumPy/Torch seeds and prior shared-input preflight supports the
deterministic input contract, but a full 276-row tensor-hash comparison for
those five conditions is not recoverable from the serialized rows. This is
disclosed in `CORE7_ROW_AUDIT.json`; it is not replaced by an inference from
equal metric values.

## Independent statistics

The independent script recalculates condition means/medians, ranks, raw paired
deltas, benefit-oriented deltas, object-level wins/losses/ties, and 95%
percentile bootstrap intervals (10,000 object resamples, seed 20260930). It
reconciles exactly on **42 shared comparison/metric rows** with the prior
`PAIRED_BOOTSTRAP_CORE7.csv`; no mismatches were found. The additional
LFM−GFL comparison is computed directly from source rows.

| Check | Recomputed result |
|---|---|
| GFH−GFL Full-PSNR | raw mean `+0.01365 dB`; 95% CI `[-0.13747,+0.15690]`; 156 wins / 120 losses / 0 ties; **NO_DETECTED_DIFFERENCE** |
| LLH−GFL FG-PSNR | `+3.2443 dB`; 95% benefit CI `[+2.9463,+3.5305]`; 242/34/0 |
| LLH−GFL Full-PSNR | `+2.5988 dB`; 95% benefit CI `[+2.3599,+2.8362]`; 249/27/0 |
| LLH−LHL Full-PSNR | `+1.1926 dB`; 95% benefit CI `[+1.1252,+1.2606]`; 276/0/0 |
| LLH mean ranks | rank 1 on 4/7 metrics; rank 2 on Full-LPIPS and Edge-SSIM; rank 3 on FG-SSIM |

The machine-readable results are `CORE7_FINAL_AGGREGATES.csv` and
`CORE7_FINAL_PAIRED_STATISTICS.csv`. For LPIPS, benefit sign is reversed so a
positive value means the left condition is better; raw `left−right` values
remain present in parallel.

The LLH−GFL contrast is a **combined allocation effect**. Do not add
overlapping pairwise contrasts into a causal decomposition (including
`3.24 ≈ 2.4 + 0.9 + 0.8`). The seven-condition matrix is independently
usable without importing any uncapped panel.

## Disposition

`PASS_WITH_LIMITATION`: the strict-276 capped Core-7 is a standalone
quantitative evidence candidate. The limitation above should remain visible
in the reproducibility record. LLH is not a universal winner; it ranks first
on four of seven headline metric means, with explicit reversals on the other
three. In particular, do not claim that GFH wins Full-PSNR over GFL.
