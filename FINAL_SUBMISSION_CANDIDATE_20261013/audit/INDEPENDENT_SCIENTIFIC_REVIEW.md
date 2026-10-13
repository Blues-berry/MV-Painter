# Independent final scientific review

Date: 13 October 2026. Read-only review; manuscript, scripts and experimental records were not changed.

## Verdict

**SCIENTIFIC_ACCURACY_GATE = PASS** for the present bounded claims. No blocking scientific error was identified. This is an evidence-consistency decision, not acceptance of algorithmic novelty or author approval.

**R1_CLOSURE = PARTIAL. R2_CLOSURE = PARTIAL. AUTHOR_APPROVAL = PENDING.** The historical main checkpoint cannot be authenticated/replayed, material fidelity remains poor in visible examples, and broad methodological novelty and matched cross-backbone transfer remain unresolved.

## Material inspected

- Actual compiled main PDF (15 pages), including abstract, methods, results, discussion and captions; the source was used for precise locations.
- Actual compiled Supplement PDF (71 pages), its reader guide, primary-family definitions, historical records and protocol limits.
- Both original reviewer-comment files in `audit/reviewer_sources`, including the real second-round R1/R2 concerns and R3's positive assessment.
- Final reviewer-response Markdown and the compiled main/supplement label maps.
- `data/FACTS_round_014.json`, `data/original_applied_budget/VERIFIED_PRIMARY.json`, the retained protocol/report/CSV identities and Figure 1 source ledger.
- Figure 1 rendered image, editable control path, and actual local GeoTex wrapper code.

## Verified claims and locations

| Item | Evidence and finding |
|---|---|
| TCAS versus existing machinery | Main PDF pp. 3–4, source lines 111–165, equations and Figure 1: TCAS supplies the request; existing native cap determines applied scale; GeoTex residual is multiplied and added to frozen features. Existing cap is visually separate. The feature dependency matches `MVPainter/mvpainter/model_unet_geotex.py:143,343,349,364`. No invented controller or learned TCAS branch is shown. |
| Discrete schedule and clipping | Main PDF pp. 3–4: steps 0–16 / 17–32 / 33–49 have 17/16/17 updates and requests 1.25/2.50/1.25. Caps 3.0/3.5/0.8 preserve deep/middle requests and clip shallow to 0.8 for every phase. Deep/middle sums 82.5 and shallow sum 40 are consistent. |
| Scalar budget versus correction dose | Main PDF pp. 3–6 and 13 expressly distinguish requested, applied and trajectory-dependent residual quantities. Matched per-group sums are not asserted to equal residual norms or causal stage mechanisms. |
| Original timing primary preserved | Main PDF p. 6 and Supplement p. 5 retain Middle-high minus objectwise average(Early-high,Late-high): −0.0338774820 dB, percentile interval [−0.1171701311,+0.0514224487], raw p=0.4323783811, 119/300 positive. These match `VERIFIED_PRIMARY.json`. Middle–Fixed Mean −0.1332632542 and Middle–Late −0.5639459133 are separate later pair comparisons. |
| Fresh C competitive controls | Main PDF pp. 5–6, Table 2: C3–GFL +0.5223522385 dB (rounded +0.522), 206/300 favorable, changes deep/middle budgets 62.5→82.5. GFH and Linear have better means on four endpoints. Linear's 93.75/93.75/31.25 budget is explicitly unmatched. |
| Multiplicity and exposure | Main PDF pp. 5–6, Supplement pp. 5–6: retrospective same-cohort addendum, original primary and twelve-test secondary family, later 59-test descriptive family are distinguished. Pointwise intervals are not an overall error guarantee. Non-detection is not equivalence/non-inferiority. |
| Bake10 and GSO20 | Main PDF pp. 8–10, Tables 4–5: −0.0026516549 LPIPS, CI [−0.0041436636,−0.0013674424], exact p=.001953125 versus GSO +0.0000837924, CI [−0.0001030475,+0.0002859206], original Holm p=.7876460618. Values agree with frozen facts. Cohorts/protocols are not pooled; calibration after initial inspection and compatibility selection are disclosed. No attribution to backbone alone or PBR/seam validation is made. |
| Native MV-Adapter and other interfaces | Main PDF pp. 9–12, Tables 6–7: Native50 Middle–Mean +.0289863455 dB, CI [−.0194108101,+.0807386755], p=.2807471925, 29/50. GSO100 primary −.0136601936 is a separate same-interface cohort. MVDiffusion is a partial operator test. Native labels are not common doses or matched GeoTex replication. |
| Historical requested-slot sensitivity | Main PDF pp. 11–13, Table 8; Supplement S7 (Table S35, p. 58): unknown replacement UID prevents verified 276-unique-object holdout inference. C3–GFH +1.699 full-frame versus −1.314 foreground PSNR, LPIPS +.01127, SSIM −.05961 remain adverse foreground evidence. Known-slot exclusion is sensitivity, not a restored exact holdout. |
| Historical and FAC limits | Main PDF pp. 13–14, Supplement S7–S8: original +.96 dB is not replayed; historical human preference concerns original stimuli; seven FAC negatives −1.10 to −2.94 remain; 1,200 versus 1,706 training identities and missing manifest/weights prevent full replay certification. |
| Honest R2.1 positioning | Abstract, introduction, discussion and response agree on controlled task knowledge. Earlier C3 optimality/CAI derivation are withdrawn. Existing scheduling precedents are credited. Response retains `R2.1 = PARTIALLY ADDRESSED`; figure improvement is not used as novelty evidence. |

## Figure 1 source recheck

All 12 CSV source rows were independently SHA-256 checked against both their packaged originals and their display files: **zero mismatches across 24 source/display comparisons**. Fresh C input/output UID is `0571e6db30c84b1593bc55a8e145a430`; recorded output order is **014, 015, 000, 016, 012, 013**. Reference is 014. The separate Bake10 UID is `3c83796ca5f043f1beb8044dd2e51a0d`; the displayed UV atlas and unseen 004 are explicitly independent. No connecting main-sample arrow implies shared object identity. Caption discloses representative maps, lossless transparent-margin crop and preserved appearance discrepancy. Source/display transforms remain indexed, rather than being presented as raw model tensors.

## Final-reference checks

The response locations agree with current compiled main labels: Figure 1 p.4; Figure 2 p.7; Figure 3 p.8; Figure 4 and Tables 5–6 p.10; Figure 5 p.11; Table 7/Figure 6 p.12; Table 8 and Discussion p.13. Supplement's original timing primary is p.5; C3 development record p.52 and Table S33 p.54. No blocking stale figure/table reference was found in the inspected response.

## Remaining scientific limits

1. This review checks the documented evidence and internal consistency; it does not rerun inference, authenticate missing weights or independently generate experiment outcomes.
2. Compatible small bake samples and convenience GSO sampling do not yield population claims or same-protocol replication. Unlit base color cannot validate material appearance under lighting.
3. A manually specified profile and an empirical boundary study may remain insufficient for R2's requested methodological contribution. The response acknowledges this; submission suitability remains the authors' decision.
4. Accuracy PASS does not certify visual approval, formal technical readiness or reviewer acceptance. No further manuscript redesign is recommended by this audit.

## Final compiled-response and S2 repair recheck

The completed five-page `review/Response_to_Reviewers.pdf` was read after compilation. Its actual PDF text preserves the original timing primary −0.0338775 / [−0.117170,+0.051422] / p=.432378, Native50 +.029 interval crossing zero, requested-slot unknown UID, opposite full-frame/foreground results, and R2.1 PARTIALLY ADDRESSED. Its citations agree with the final label maps: historical requested-slot panel is **Supplement S7, Table S35 p.58**, and historical FAC is **Table S30 p.50**. The earlier review-report reference to S8 for the requested-slot panel has been corrected.

The final Table S2 repair was independently checked using both recorded before/after scientific rows and the actual compiled Supplement pp.5–6. All **28 rows retain identical numeric token sequences**, including signed means, CI endpoints, medians, percentages and adjusted p values. The six-column split separates the mean from its interval and keeps negative signs with the numbers; the scientific values, caption, label and font size are unchanged. Actual PDF text shows intact interval endpoints and negative signs. This is a presentation repair, not a new analysis.

`audit/NUMERICAL_VERIFICATION.json` was inspected: original primary verification reports all 300 deltas exact, exact original 10,000-resample interval and 20,000 sign-flip result, and all twelve original secondary tests exact. Other named cohort mean/contrast checks report PASS at their documented scope. These reproducibility records support the scientific-consistency gate without resolving the historical missing-checkpoint or methodological novelty limits.
