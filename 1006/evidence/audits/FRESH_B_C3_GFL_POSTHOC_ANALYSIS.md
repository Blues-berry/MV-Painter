# FRESH_CONFIRM_B native-GC3 versus native-GFL post-hoc analysis

Date: 2026-10-06. Disposition: **retrospective supplemental evidence only**.

The pair `native_gc3 - native_gfl` was not included in the registered B1/B2
confirmatory families. The B campaign had already been unblinded before this
additional comparison was selected. The object cohort is disjoint from the
earlier evaluation cohorts, but this analysis is not a prospective or
registered confirmation.

## Provenance and integrity

- FRESH_CONFIRM_B: 150 objects; 4,500 unique object-condition rows.
- The pre-analysis integrity gate recorded 13,888 verified input-file hashes,
  4,500 prediction images, 4,500 residual logs, no duplicate keys, no missing
  pairs, no non-finite values, matching runner/config/checkpoint/data-root
  identities, and exact row-ledger/CSV reconstruction.
- The all-campaign input identity audit found no shared-input mismatches. The
  cohort lock records zero prior-method-output overlap, zero source-GLB byte
  duplicates, zero within-B decoded-view duplicate groups, and zero duplicates
  across the earlier selected 300 objects.
- Both B shard manifests record runner SHA-256
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` and
  checkpoint SHA-256
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Source metric CSV SHA-256:
  `ce7ba03f6dcb9f1d275b389c633e23dc544404eeac4ddf090e90a11ad278e081`.

The tested `native_gc3` and `native_gfl` profiles use the same object-specific
inputs and generation seed within each pair. Their contrasts describe these
specified native capped paths; they do not isolate a dose-independent causal
mechanism.

## Statistical method

The object is the inferential unit. Each endpoint uses 10,000 paired object
bootstrap draws and the B audit seed 20261002. Intervals are nominal percentile
95% CIs. Two-sided bootstrap sign-crossing p-values are reported at a minimum
resolution of 1/10,000; Holm adjustment across seven Core-7 endpoints is added
as an exploratory sensitivity. This post-hoc family correction does not
restore preregistration. Lower LPIPS and higher PSNR/SSIM/Edge-SSIM favor GC3.

| Endpoint | GC3 − GFL mean [95% CI] | Median | Objects favoring GC3 | Post-hoc Holm p |
|---|---:|---:|---:|---:|
| FG-PSNR (dB) | +0.5019 [0.3419, 0.6629] | +0.4911 | 100/150 | 0.0007 |
| FG-SSIM | +0.02380 [0.01911, 0.02901] | +0.01858 | 123/150 | 0.0007 |
| FG-LPIPS | −0.005127 [−0.006549, −0.003691] | −0.003776 | 107/150 | 0.0007 |
| Full-PSNR (dB) | +0.2250 [0.0948, 0.3578] | +0.1031 | 82/150 | 0.0007 |
| Full-SSIM | +0.005934 [0.004797, 0.007107] | +0.005073 | 130/150 | 0.0007 |
| Full-LPIPS | −0.004548 [−0.006102, −0.003009] | −0.003632 | 109/150 | 0.0007 |
| Edge-SSIM | +0.005034 [0.003348, 0.006753] | +0.004587 | 105/150 | 0.0007 |

All seven cohort means favor GC3, but object-level favorable rates range from
54.7% to 86.7%; a positive mean is not a universal object-level effect. No
composite score or equivalence/non-inferiority claim is formed.

## Reproduction

From the repository root, run:

```bash
python 1006/scripts/analyze_fresh_b_c3_gfl_posthoc.py
```

Inputs are `data/fresh_b/per_object_metrics.csv`; outputs are
`data/derived/fresh_b_c3_minus_gfl_posthoc.csv` and
`data/derived/fresh_b_c3_minus_gfl_object_deltas.csv`. The B3 comparison was
not a registered confirmatory comparison and must stay labeled post hoc.
