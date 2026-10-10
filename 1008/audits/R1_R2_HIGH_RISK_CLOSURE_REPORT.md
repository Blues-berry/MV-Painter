# R1/R2 high-risk closure report — C&G 1008

**Captured:** 2026-10-09 UTC  
**Review-source boundary:** The retained PDF says “initial-submission reviews”; no authenticated second-round export or editor-system connector/credentials are available here. The issue summaries below follow the current task and existing response matrix, not verbatim authenticated comments.

## R1.1 — Visual artifacts, color fidelity and 3D quality

**Disposition: PARTIAL; material risk remains.** Main Figures 4–5 retain paired full-object context and same-ROI crops, including favorable and adverse cases, and now explicitly identify them as qualitative rather than colorimetric evidence. The new failure-enriched 26-object diagnostic compares No Adapter, GFL and LLH across six unique target views. GFL reduces mean reference-relative foreground CIEDE2000 versus No Adapter by 19.65 (95% object-paired bootstrap CI [−26.37, −13.25]; 24/26 objects), but the two original Figure 4 examples keep visible pink/purple hue shifts in all three conditions. LLH raises mean CIEDE2000 versus GFL by 3.58 [0.46, 6.71] while local gradient, high-frequency energy and color entropy fall. A decoded RGB snapshot shows the shift before baking; a VAE round trip of ground-truth RGB does not reproduce the same direction/magnitude in the selected GFL case.

This narrows the location and rules against simple explanations but does not identify the complete cause. The set is failure-enriched and is not a new independent confirmation cohort. C1 failed locked visual review, including a cyan/blue rim; B2 failed its numeric gate and improved only one of four cases. No color repair is validated, and no new repair search was started because there is no isolated, causally supported control point. The native-default adapter comparison remains absent; No Adapter (scale zero) is not native-default (unset scale). The 24-object Fresh C bake gate failed, and no valid bake, seam, or PBR result is claimed. Human evidence is not used to close this issue because ethics/data-use records are absent.

**Locations:** Main manuscript stage/applicability Results and Limitations; Supplement S13; response Reviewer 1, Comment 1.  
**Residual risk:** High. Relative 2D diagnostics do not resolve absolute color fidelity, repeated texture, native-default comparison, or baked 3D quality.

## R1.2 — Matched held-out comparison and historical results

**Disposition: ADDRESSED WITH LIMITS.** Fresh C is a matched 300-object image-space follow-up, separate from the historical 01549 evaluation. C3−GFL FG-PSNR is +0.522352 dB (95% object-bootstrap CI [+0.404160,+0.640669]); GFH and Generic Linear have more favorable means than C3 on all four displayed endpoints. C3 and GFL differ in applied deep/middle scale sums (82.5 vs 62.5), so the contrast is not timing-only. Fresh C is a controlled retraining and does not numerically reproduce the historical +0.96 dB estimate. Core-7 remains a retrospective endpoint-opposed diagnostic with incomplete common-runner/input identity.

Fresh B temporal and A3b results are explicitly downgraded to retrospective sensitivity because the lock text's 2026-10-05 08:40 UTC freeze time predates the earliest preserved commit containing the file (2026-10-06 00:52 UTC). The record cannot authenticate pre-run availability. No Fresh B result is treated as a verified preregistered confirmation or as validation of C3.

**Locations:** Main Abstract, matched Results, stage/applicability Results and Limitations; Supplement S2–S5; response Reviewer 1, Comment 2.  
**Residual risk:** Medium. Fresh C supports the named paired image-space contrast, not the unavailable historical checkpoint result or 3D claims.

## R2.1 — Contribution beyond choosing a piecewise schedule

**Disposition: PARTIAL; editorial novelty risk remains.** The response and Introduction now make a positive, bounded argument: the paper operationalizes an existing geometry-residual control with distinct requested, applied-under-cap and residual-magnitude records, then measures it against fixed and scheduled alternatives on paired multi-view image endpoints. The study contributes task-specific knowledge about cap effects, endpoint/object variation and the limits of apparent schedule contrasts. It does not claim that piecewise scheduling is new in general, that C3 is optimal, or that C3's contrast with GFL isolates timing.

The manuscript reports the Fresh C counter-results, the post-inspection L--L--H outcome and the FRESH_CONFIRM_300 texture-complexity boundary. The latter is a separate retrospective cohort: CPU reaggregation reproduced 9/10 plus-one-corrected Holm rejections, with the FG-LPIPS/coverage test at adjusted p=0.0508 and heterogeneous Laplacian-variance quartiles. Fresh B's lock chronology is unresolved, and A3b's raw-$L_2$ cross-layer support test is dimension-confounded; neither establishes dose-independent scheduling. These details support an empirical system contribution while leaving the editor's novelty threshold open.

**Locations:** Main Introduction/contributions, Results, stage/applicability discussion and Conclusion; Supplement S3, S4, S5 and S12; response Reviewer 2, Concern 1.  
**Residual risk:** Medium-high. The paper offers a task-specific empirical contribution, but not a new general algorithm or a confirmed independent temporal mechanism.

## R2.3 — Cross-backbone generalization

**Disposition: NOT FULLY ANSWERED.** The MV-Adapter probe covers 98 of 99 planned objects; its production additive-residual bootstrap is invalid for interaction inference. The exploratory object-cluster robust Wald family has no Holm-corrected interaction result, which is not evidence of absence or equivalence. MVDiffusion covers 75 objects through a different correspondence-aware interface and has mixed/negative endpoints. A raw-direction recheck shows L−LLH has higher CIEDE2000 than G−FL (+1.373, pointwise 95% CI [+0.418,+2.375]); the old negative value was improvement-coded. A separate 76-object MV-Adapter mapping audit shows mixed metrics for budget-neutral B′; its M3 companion changes both grouping and total nominal dose (mean multiplier about 0.8065) and is retrospective because protocol and results first appear in the same preserved commit. Neither supplies a matched second-backbone comparison of native, fixed-low/high, C3 and a competitor.

**Locations:** Main stage/applicability Results and Limitations; Supplement S5; response Reviewer 2, Concern 3.  
**Residual risk:** High. Cross-interface behavior is documented; general TCAS transfer remains unestablished.

## Overall risk and next gate

The new GPU experiment was a No-Go under the observed resource state in this turn. At inspection, the two RTX 5090s reported 24,852/32,607 MiB and 25,404/32,607 MiB memory used, with 73%/63% utilization; no compute-process owner was visible to this process. No active job was interrupted, and no inference was launched. The package can be built for author review with these boundaries, but reviewer closure remains `PARTIAL`; no result supports guaranteed acceptance. The exact second-round reviewer export should be authenticated before final response page/line claims are treated as verbatim closure.
