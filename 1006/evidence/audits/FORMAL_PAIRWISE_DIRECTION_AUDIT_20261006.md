# Formal pairwise direction and row-reproduction audit — 2026-10-06

**Status: PASS** — 18 registered/formal and 1 explicitly exploratory pairwise files; 19 of 19 reproduced from raw shard rows.

Each contrast is condition A minus condition B. Higher FG-PSNR favors A; lower FG-LPIPS favors A, so a positive LPIPS delta favors B. The reported A-favorable fraction is direction-aware; the archived `win_rate` field is only the positive-delta fraction and must not be read as A wins for LPIPS.

The audit rechecks paired UID count, disjoint count, object index, seed, six input hashes, mean, median, percentile object-bootstrap interval, two-tail bootstrap sign p-value, and positive/negative fractions. A p-value at 0.0001 is at the stored 10,000-draw reporting floor, not an exact zero.

| Pairwise file | N | Source rows A / B | Metric | A−B mean | 95% object-bootstrap CI | A-favorable objects | Raw bootstrap p |
|---|---:|---|---|---:|---:|---:|---:|
| `pairwise_layer_hll_vs_layer_lll_EXPLORATORY.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_psnr | -0.0130891 | [-0.127848, +0.0978042] | 62.0% | 0.824 |
| `pairwise_layer_hll_vs_layer_lll_EXPLORATORY.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_lpips | +0.00187144 | [+0.00120325, +0.00255766] | 43.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_hll.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_psnr | +0.853483 | [+0.657974, +1.05235] | 58.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_hll.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_lpips | -0.0116117 | [-0.0130694, -0.0101992] | 80.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_lhl.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_psnr | +0.647211 | [+0.560988, +0.736417] | 81.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_lhl.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_lpips | -0.00692784 | [-0.00780843, -0.00608195] | 83.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_lll.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_psnr | +0.840394 | [+0.746774, +0.934358] | 81.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_layer_lll.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_lpips | -0.0097403 | [-0.0108144, -0.00869572] | 86.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_lfm_exact.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_psnr | +0.434477 | [+0.355881, +0.516238] | 68.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_lfm_exact.json` | 300 | campaign_B1B2 / campaign_B1B2 | fg_lpips | -0.00452305 | [-0.00518905, -0.00387034] | 77.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_native_gfl.json` | 300 | campaign_B1B2 / campaign_B3 | fg_psnr | +1.28774 | [+0.938272, +1.63459] | 57.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_native_gfl.json` | 300 | campaign_B1B2 / campaign_B3 | fg_lpips | -0.0165016 | [-0.0188661, -0.0141292] | 73.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_true_global_1p675.json` | 300 | campaign_B1B2 / campaign_B3 | fg_psnr | +3.42866 | [+2.80525, +4.04436] | 69.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_true_global_1p675.json` | 300 | campaign_B1B2 / campaign_B3 | fg_lpips | -0.0175122 | [-0.0212534, -0.0136581] | 67.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_true_global_2p50.json` | 300 | campaign_B1B2 / campaign_B3 | fg_psnr | +4.57112 | [+3.90702, +5.22205] | 77.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_true_global_2p50.json` | 300 | campaign_B1B2 / campaign_B3 | fg_lpips | -0.0184118 | [-0.0226526, -0.0140318] | 67.3% | ≤0.0001 |
| `pairwise_lfm_exact_vs_true_global_1p675.json` | 300 | campaign_B1B2 / campaign_B3 | fg_psnr | +2.99418 | [+2.42523, +3.55026] | 69.7% | ≤0.0001 |
| `pairwise_lfm_exact_vs_true_global_1p675.json` | 300 | campaign_B1B2 / campaign_B3 | fg_lpips | -0.0129892 | [-0.0163323, -0.00956268] | 66.0% | ≤0.0001 |
| `pairwise_native_gfh_vs_true_global_2p50.json` | 300 | campaign_B3 / campaign_B3 | fg_psnr | +4.65882 | [+4.06662, +5.22761] | 80.0% | ≤0.0001 |
| `pairwise_native_gfh_vs_true_global_2p50.json` | 300 | campaign_B3 / campaign_B3 | fg_lpips | -0.0168967 | [-0.0208409, -0.0128202] | 68.0% | ≤0.0001 |
| `pairwise_native_gfl_vs_true_global_1p25.json` | 300 | campaign_B3 / campaign_B3 | fg_psnr | +1.60332 | [+1.37321, +1.8229] | 78.7% | ≤0.0001 |
| `pairwise_native_gfl_vs_true_global_1p25.json` | 300 | campaign_B3 / campaign_B3 | fg_lpips | -0.00447817 | [-0.00593154, -0.002975] | 65.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_cosine_bump.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.455518 | [+0.373302, +0.540664] | 70.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_cosine_bump.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00463646 | [-0.00545806, -0.00380781] | 76.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_cosine_bump_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.577376 | [+0.498975, +0.658826] | 81.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_cosine_bump_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00601862 | [-0.00684129, -0.00521347] | 80.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_gaussian_peak.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.530712 | [+0.448494, +0.616169] | 77.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_gaussian_peak.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00532339 | [-0.00613836, -0.00451941] | 77.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_gaussian_peak_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.590193 | [+0.509689, +0.673392] | 81.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_gaussian_peak_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00600724 | [-0.00683093, -0.00520276] | 80.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_linear.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.00488542 | [-0.0349945, +0.0468884] | 45.0% | 0.8148 |
| `pairwise_layer_llh_vs_gen_linear.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | +0.00122627 | [+0.000691576, +0.00181628] | 45.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_linear_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.145339 | [+0.117207, +0.175034] | 76.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_linear_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.000841693 | [-0.00119173, -0.000474388] | 65.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_trapezoid.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.30448 | [+0.21872, +0.392247] | 57.7% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_trapezoid.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00348336 | [-0.00430445, -0.00263425] | 71.0% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_trapezoid_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_psnr | +0.550257 | [+0.474477, +0.628723] | 80.3% | ≤0.0001 |
| `pairwise_layer_llh_vs_gen_trapezoid_bm.json` | 300 | campaign_B1B2 / campaign_C | fg_lpips | -0.00590804 | [-0.00670011, -0.00512897] | 81.0% | ≤0.0001 |

## Provenance findings

- `campaign_B3` has 750 identical duplicate raw rows across five conditions (150 per condition); duplicate scientific fields match after excluding elapsed time. Unique paired N remains 300. Its shard manifests disagree on `num_shards` (2 versus 4), so retain this as a provenance warning.
- The 300-object LLH-versus-generic comparisons source LLH from `campaign_B1B2` and generic conditions from `campaign_C`. All paired UIDs, indices, seeds, and six input hashes match; both run manifests omit a configuration hash. These remain same-cohort retrospective paired comparisons, not independent confirmation.
- Pairwise bootstrap p-values above are not a substitute for the frozen multiplicity families. Recomputed Holm adjustments for all five archived families and 28 tests are in `FORMAL_HOLM_FAMILY_AUDIT_20261006.md`.
- These tables preserve endpoint-specific differences; no weighted cross-metric score or overall winner is computed.

Machine-readable result: `../../data/derived/formal_pairwise_sign_audit.json`.
