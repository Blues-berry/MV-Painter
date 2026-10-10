# Frozen Holm-family audit — 2026-10-06

This audit recomputes each stored Holm-Bonferroni adjustment from the
raw p-value (or the explicitly stored reporting-floor upper bound) in
the corresponding frozen family file. It does not pool cohorts or alter
the registered family definitions. Direction is audited separately
from paired raw rows in `data/derived/formal_pairwise_sign_audit.json`.

**Status: PASS** — 5 families; 28 tests.

| Family file | Cohort | Tests | Holm recomputation |
|---|---:|---:|---|
| `final/round2/scientific_validation_v3/formal/campaign_B1B2/HOLM_FAMILY_B1.json` | see file | 2 | PASS |
| `final/round2/scientific_validation_v3/formal/campaign_B1B2/HOLM_FAMILY_B2.json` | see file | 4 | PASS |
| `final/round2/scientific_validation_v3/formal/campaign_C/HOLM_FAMILY_C.json` | see file | 16 | PASS |
| `final/round2/scientific_validation_v3/formal/campaign_FRESH_CONFIRM_B_20261005/HOLM_FAMILY_B2_FRESH_CONFIRM_B.json` | FRESH_CONFIRM_B | 4 | PASS |
| `final/round2/scientific_validation_v3/formal/campaign_FRESH_CONFIRM_B_20261005/HOLM_FAMILY_HLL_LLL_EXPLORATORY.json` | FRESH_CONFIRM_B | 2 | PASS |

## Test-level values

| Family | Test | Paired result source | raw p / bound | Holm p / bound | Holm decision |
|---|---|---|---:|---:|---|
| `HOLM_FAMILY_B1.json` | `H2_fg_psnr` | `pairwise_layer_llh_vs_lfm_exact.json` | 0.0001 | 0.0002 | reject |
| `HOLM_FAMILY_B1.json` | `H2_fg_lpips` | `pairwise_layer_llh_vs_lfm_exact.json` | 0.0001 | 0.0002 | reject |
| `HOLM_FAMILY_B2.json` | `H3_LLH-HLL_fg_psnr` | `pairwise_layer_llh_vs_layer_hll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2.json` | `H3_LLH-HLL_fg_lpips` | `pairwise_layer_llh_vs_layer_hll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2.json` | `H3_LLH-LLL_fg_psnr` | `pairwise_layer_llh_vs_layer_lll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2.json` | `H3_LLH-LLL_fg_lpips` | `pairwise_layer_llh_vs_layer_lll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_linear_fg_psnr` | `pairwise_layer_llh_vs_gen_linear.json` | 0.8148 | 0.8148 | retain |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_linear_fg_lpips` | `pairwise_layer_llh_vs_gen_linear.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_linear_bm_fg_psnr` | `pairwise_layer_llh_vs_gen_linear_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_linear_bm_fg_lpips` | `pairwise_layer_llh_vs_gen_linear_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_cosine_bump_fg_psnr` | `pairwise_layer_llh_vs_gen_cosine_bump.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_cosine_bump_fg_lpips` | `pairwise_layer_llh_vs_gen_cosine_bump.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_cosine_bump_bm_fg_psnr` | `pairwise_layer_llh_vs_gen_cosine_bump_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_cosine_bump_bm_fg_lpips` | `pairwise_layer_llh_vs_gen_cosine_bump_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_trapezoid_fg_psnr` | `pairwise_layer_llh_vs_gen_trapezoid.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_trapezoid_fg_lpips` | `pairwise_layer_llh_vs_gen_trapezoid.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_trapezoid_bm_fg_psnr` | `pairwise_layer_llh_vs_gen_trapezoid_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_trapezoid_bm_fg_lpips` | `pairwise_layer_llh_vs_gen_trapezoid_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_gaussian_peak_fg_psnr` | `pairwise_layer_llh_vs_gen_gaussian_peak.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_gaussian_peak_fg_lpips` | `pairwise_layer_llh_vs_gen_gaussian_peak.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_gaussian_peak_bm_fg_psnr` | `pairwise_layer_llh_vs_gen_gaussian_peak_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_C.json` | `H4_LLH-gen_gaussian_peak_bm_fg_lpips` | `pairwise_layer_llh_vs_gen_gaussian_peak_bm.json` | 0.0001 | 0.0016 | reject |
| `HOLM_FAMILY_B2_FRESH_CONFIRM_B.json` | `H3_LLH-HLL_fg_psnr` | `paired_layer_llh_minus_layer_hll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2_FRESH_CONFIRM_B.json` | `H3_LLH-HLL_fg_lpips` | `paired_layer_llh_minus_layer_hll.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2_FRESH_CONFIRM_B.json` | `H3_LLH-LLL_fg_psnr` | `paired_layer_llh_minus_a3_baseline.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_B2_FRESH_CONFIRM_B.json` | `H3_LLH-LLL_fg_lpips` | `paired_layer_llh_minus_a3_baseline.json` | 0.0001 | 0.0004 | reject |
| `HOLM_FAMILY_HLL_LLL_EXPLORATORY.json` | `HLL-LLL_exploratory_fg_psnr` | `paired_layer_hll_minus_a3_baseline_exploratory.json` | 0.5696 | 0.5696 | retain |
| `HOLM_FAMILY_HLL_LLL_EXPLORATORY.json` | `HLL-LLL_exploratory_fg_lpips` | `paired_layer_hll_minus_a3_baseline_exploratory.json` | 0.0001 | 0.0002 | reject |
