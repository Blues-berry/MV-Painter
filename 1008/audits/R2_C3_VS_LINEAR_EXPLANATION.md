# R2.1 C3 versus Generic Linear: explanation and limits

## Direct Fresh C result

Fresh C uses the same 300 objects, input hashes, per-object seeds, and target views for C3 and Generic Linear. Generic Linear is a separate revision-era addendum run on the same frozen cohort, not a second independent cohort. Differences below are C3 minus Generic Linear; higher PSNR/SSIM is better and lower LPIPS is better.

| Endpoint | C3 mean | Generic Linear mean | C3 − Linear mean [95% CI] | Objects favoring C3 |
|---|---:|---:|---:|---:|
| FG-PSNR (dB) | 11.8301 | 12.4230 | -0.593 [-0.837,-0.351] | 51.7% |
| FG-LPIPS | 0.1998 | 0.1862 | +0.013512 [+0.011601,+0.015487] | 25.7% |
| FG-SSIM | 0.3746 | 0.4026 | -0.02810 [-0.03197,-0.02439] | 20.0% |
| Edge-SSIM | 0.4773 | 0.4880 | -0.010693 [-0.013004,-0.008495] | 33.7% |

Generic Linear has more favorable cohort means on all four displayed endpoints. For FG-PSNR, however, the median paired difference is +0.073956 dB and C3 is higher on 155/300 objects. The negative mean is therefore driven by the distribution of object effects; it is not a statement that every typical object loses under C3. LPIPS, FG-SSIM, and Edge-SSIM favor Generic Linear at both cohort-mean and most-object levels.

The primary C3--GFL result is positive but does not isolate schedule timing: C3's deep/middle applied-scale sums are 82.5 each versus GFL's 62.5, while both are 40 in shallow after the cap. Fresh C confirms the named C3 intervention against GFL; it does not prove a timing-only gain.

## Why the comparison is not a same-budget schedule-shape experiment

The profile totals over 50 steps are:

| Profile | Deep applied sum | Middle applied sum | Shallow applied sum | Cap behavior |
|---|---:|---:|---:|---|
| C3 | 82.50 | 82.50 | 40.00 | Shallow requested values clipped to 0.8 at all 50 steps. |
| Generic Linear | 93.75 | 93.75 | 31.25 | Its maxima 2.5/2.5/0.75 remain below all three caps. |

So Generic Linear applies a larger requested/applied scalar sum in deep and middle and a smaller one in shallow. Both temporal shape and layer allocation differ. This explains why the observed linear advantage cannot be attributed to linearity alone or read as a dose-matched shape result. It still answers a practically relevant question: under the named implementable profiles and this protocol, Generic Linear gives better Fresh C cohort means.

The logged correction norms show that scale and residual state both matter. At step 24, C3 has applied deep/middle scale 2.50, while Generic Linear is 1.86224; median post-scale correction norms are 2006.94 vs 1479.39 (deep) and 1551.26 vs 1426.02 (middle). In shallow, C3 is capped at 0.8 while Generic Linear applies 0.62245, with medians 52.51 vs 43.03. At other steps the schedule values and norm order vary. These are medians over nested wrapper records, not object-level cumulative dose. Equal scalar sums would still not guarantee equal residual-norm exposure because the residual itself depends on the earlier generated state.

No post-treatment regression is used to explain away the Generic Linear result. The residual norm is affected by the schedule and by the evolving features, and the layer/window data do not provide cross-layer dose support. There is no audited per-object residual-dose model that independently explains why Generic Linear performs better on the four means.

## Evidence that stage allocation matters, and why it does not rescue C3 optimality

The separate `MAIN-STAGE-276` run compared temporal profiles under the same runner, object inputs, seed, initial latents, and 50-step setup. C3 and temporal L--L--H are near-matched in applied scalar sum: 82.50 versus 83.75 for deep/middle, both 40 for shallow. C3 versus fixed mean 5/3 is also near-matched: 82.50 versus 83.33 deep/middle, both 40 shallow. In this run, C3--fixed-mean FG-PSNR is +0.502875 dB [+.462018,+.542244]; temporal L--L--H is favored over C3 on all six formal endpoints. The follow-up was specified after earlier clean-v2 inspection, not blind, and does not equalize post-scale residual norms.

This is positive evidence that placement of a high stage changes outcomes in the tested pipeline. It also shows that the preferred placement is not fixed: C3 performs well against a near-mean fixed profile on several endpoints, but a late-high temporal profile outperforms it on the six formal strict-276 endpoints. These are not Fresh C Generic Linear data and are not pooled with them.

## Keep cohort/profile names distinct

- **Fresh C C3:** requested temporal deep/middle profile (1.25, 2.50, 1.25); shallow is clipped to 0.8.
- **Fresh C LLH:** layer-conditioned temporal profile; deep/middle requests match C3, while shallow requests are (0.50, 0.75, 0.50). Its comparison with C3 changes shallow intervention and is not a pure temporal placement contrast.
- **Fresh B temporal LLH/HLL/LLL:** different N=150 cohort and temporal comparisons. They provide LLH-specific evidence, not C3 validation.
- **Strict-276 temporal L--L--H:** low in early/middle and high in late stages; this is the named `llh` schedule in `MAIN-STAGE-276`, not the Fresh C layer-conditioned condition.
- **FRESH_CONFIRM_300:** disjoint N=300 cohort; its texture-boundary analysis is LLH--GFL, not C3--Generic Linear.

Fresh B values illustrate why cohort boundaries matter: LLH--LFM-EXACT is +0.325 dB FG-PSNR [+.209,+.446] and -0.00460 FG-LPIPS [-.00563,-.00357], within predeclared practical margins but with different realized residual dose. LLH--HLL has +0.687 dB mean PSNR but a -0.104 dB median and only 45.3% object wins; LPIPS favors LLH. The post-lock same-cohort endpoint-matched linear extension has LLH-minus-linear FG-PSNR -0.0373 dB [-0.0829,+0.0086] and FG-LPIPS +0.00109 [+0.0004,+0.0019]. This is a sensitivity analysis, not independent confirmation.

The GT texture-complexity result is the association between texture descriptors and the **LLH--GFL effect**. On Fresh B, the per-object FG-PSNR effect versus GT foreground high-frequency energy has Spearman rho -0.624 [-0.714,-0.513], Holm p=.002; the disjoint FRESH_CONFIRM_300 cohort shows the same direction. It is non-causal and says nothing directly about C3 versus Generic Linear.

## Reviewer-safe interpretation

The strongest defensible statement is: “On Fresh C, Generic Linear has more favorable cohort means than C3 on all four displayed image-space endpoints. Their per-layer scale sums differ, so this comparison does not isolate schedule shape at fixed applied scale or residual dose. A separate near-matched strict-276 follow-up shows that temporal placement changes outcomes, while its preferred profile differs from C3.”

Do not claim that C3 dominates, is Pareto-optimal, is equivalent to Generic Linear, or is a typical-object winner on FG-PSNR. Do not use a high p-value as equivalence. Do not use texture-complexity associations or Fresh B LLH outcomes to explain C3's Generic Linear contrast.

### Evidence sources

- Fresh C paired results: `1008/audits/source_evidence/r2/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md` and the claim ledger/numerical authority.
- Requested/applied/correction rows: `1008/audits/source_evidence/r2/accounting/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv`.
- Stage-placement follow-up: `final/round2/stage_placement_276_20260929/final_manifest.json`, `per_object_metrics.csv`, and `final/round2/coordination/C3_TCAS_FULL_BASELINE_AUDIT_20260929.md`.
- Fresh B and texture boundary: `final/round2/scientific_validation_v3/FRESH_B_TEMPORAL_CONFIRMATION_REPORT.md` and `PROSPECTIVE_FAILURE_BOUNDARY_REPORT.md`.
