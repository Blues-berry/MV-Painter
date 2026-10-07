# R1.4 post-hoc paired audit: Fresh C C3 versus high fixed scale

## Status and purpose

**Status: `PASS` — `POST_HOC WITHIN FROZEN FRESH-C COHORT`.** This reviewer-requested comparison uses already-generated non-human outputs. It was not part of Fresh C's registered confirmatory family and is not a replacement for the original N=300 Table 4 contrast.

The contrast is `native_gc3 − native_gfh` (C3 minus global high fixed scale). The inferential unit is the object; each object contributes one paired difference. We used 10,000 paired object-bootstrap resamples, `numpy.default_rng(20261002)`, and a two-sided percentile 95% interval. No p-values were computed. Positive differences favor C3 for PSNR/SSIM; negative differences favor C3 for LPIPS.

## Source integrity and pairing

The full machine-readable gate is [`R1_4_FRESHC_C3_GFH_SOURCE_INTEGRITY.json`](R1_4_FRESHC_C3_GFH_SOURCE_INTEGRITY.json). All required checks passed:

- The prior Fresh C integrity gate is `PASS`; the combined source has 1,200 rows and 300 unique objects per original condition.
- C3 and GFH each have 300 unique UIDs, with exact UID-set agreement to each other and the frozen cohort manifest; there are no duplicate condition × UID keys.
- The recorded generation seed policy and object index match for every paired UID.
- The reference target and all five additional input identity hashes match within every C3/GFH pair.
- Both completed run shards record the same runner, checkpoint, metric implementation, and metric path.
- The observed raw CSV, cohort manifest, input-embedding manifest, and output-hash-manifest hashes match the hashes recorded by the existing Fresh C gate.

Key hashes:

| Source | SHA-256 |
|---|---|
| Raw per-object CSV | `6967375a66a523beeab2089a9e51fbd68b756f2a07b13439d443078bd4482cd6` |
| Frozen cohort manifest | `0f2c50f0bcce6678d578bd7ec4e8931e39606045b1b105ccbdae7546556a3859` |
| Input embeddings manifest | `50f28b3f17ef5537ec0ab56a36c3c3c142486e5a7333adaf2a51d87cc83c8a2f` |
| Runner | `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` |
| Checkpoint | `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` |
| Metric implementation | `adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5` |
| Analysis script | `ec87a8b5b729b198a501d66a49850bac3b54bc7a090b9d33e7e50050b59a251d` |

The source CSV originated at `/4T/CXY/MV-Painter/1006/data/fresh_c/runs/c3_confirmation/per_object_metrics.csv`. A byte-identical copy is now bundled at [`numerical_inputs/fresh_c_c3_confirmation_per_object_metrics.csv`](numerical_inputs/fresh_c_c3_confirmation_per_object_metrics.csv) with the recorded SHA-256. Its paired summaries can be reaggregated from a clean checkout; full run-identity and generation provenance remain a separate audit scope.

## Results

All estimates are C3 minus GFH. “C3-favorable objects” applies the endpoint direction convention to each paired object difference; ties are shown separately.

| Endpoint | Mean difference | Paired object-bootstrap 95% CI | Median | C3-favorable objects |
|---|---:|---:|---:|---:|
| FG-PSNR (dB; higher better) | −0.7477 | [−0.8881, −0.6050] | −0.8804 | 97/300 (32.3%) |
| FG-SSIM (higher better) | −0.04553 | [−0.04943, −0.04166] | −0.04098 | 26/300 (8.7%) |
| FG-LPIPS (lower better) | +0.01070 | [+0.00891, +0.01262] | +0.01126 | 82/300 (27.3%) |
| Full-PSNR (dB; higher better) | +0.6607 | [+0.5858, +0.7358] | +0.7019 | 252/300 (84.0%) |
| Full-SSIM (higher better) | +0.000264 | [−0.000948, +0.001354] | +0.002143 | 192/300 (64.0%) |
| Full-LPIPS (lower better) | +0.000345 | [−0.001315, +0.002068] | −0.000503 | 153/300 (51.0%) |
| Edge-SSIM (higher better) | −0.01881 | [−0.02080, −0.01679] | −0.01904 | 47/300 (15.7%); 1 tie |

The Edge-SSIM estimate and interval favor GFH. Full-image PSNR favors C3, while foreground PSNR/SSIM/LPIPS favor GFH. Full-image SSIM and LPIPS intervals include zero. The endpoint pattern is mixed; these object fractions do not establish a typical-object or universal benefit.

The seven-endpoint machine-readable table is [`R1_4_FRESHC_C3_minus_GFH_posthoc_results.csv`](R1_4_FRESHC_C3_minus_GFH_posthoc_results.csv), with full precision and provenance in [`R1_4_FRESHC_C3_minus_GFH_posthoc_results.json`](R1_4_FRESHC_C3_minus_GFH_posthoc_results.json).

## Relationship to the existing Fresh B audit

The existing [`R1_4_C3_minus_GFH_posthoc_audit_20261007.md`](R1_4_C3_minus_GFH_posthoc_audit_20261007.md) remains intact as the separate N=150 `FRESH_CONFIRM_B` supporting sensitivity. It also reports an Edge-SSIM cost for C3 and a full-image PSNR advantage for C3. The cohorts are not pooled, meta-averaged, or treated as independent replications; the Fresh B result is supporting post-hoc evidence only.

## Interpretation limits

This result is a reviewer-requested post-hoc analysis within a frozen cohort. It is not preregistered, confirmatory, registered-primary, an independent replication, or a verification of the original Table 4 result. A confidence interval crossing zero does not establish equivalence or non-inferiority; no non-inferiority margin was prespecified. The evidence supports endpoint-specific wording and explicit disclosure of the Edge-SSIM trade-off, not equivalence, non-inferiority, broad structure preservation, or a single overall winner.
