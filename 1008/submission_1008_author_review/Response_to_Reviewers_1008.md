# Response to Reviewers — 1008 second-round revision

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The R1/R2/R3 comments addressed here concern the subsequent second round. We retain the prior 01549 work that remains relevant, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

> **Author verification required before submission.** The retained `CAG-D-26-00962-reviews.pdf` is labeled as initial-submission reviews, and no exact second-round export or editor email is available in this workspace. The round mapping is author-confirmed in the retained issue map; the headings below paraphrase that map and are not represented as verbatim reviewer quotations. Compare them with the editor's original second-round decision before finalizing this response.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision keeps Timestep-Conditioned Adapter Scaling (TCAS) as the method and narrows its claims to the evidence available. We now describe the actual Fresh C figures and controls, correct the stage-placement result, distinguish applied scale from schedule shape, and replace an invalid interaction-bootstrap inference with the available exploratory object-cluster robust Wald analysis. The revisions and remaining limits are detailed below.

## Reviewer 1

### Comment 1 — Visual artifacts, full-object comparisons, and 3D fidelity

**Response.** We agree that the earlier panels did not make it easy to compare the complete object and the same local detail. Figure 7 now shows reference, GFL, GFH, and C3 for a C3–GFL endpoint-favorable case and an adverse case, with each full target-view context paired with the same pixel ROI. Figure 4 preserves the fixed-scale comparison and adds a separate Generic Linear counterexample; its RGB outputs are not independently adjusted. Figure 6 reproduces the historical pink/purple failure from the submitted 01549 Figure 4, but its original panel-level object/run mapping is unavailable, so we use it only to document the historical failure. Supplementary Figure S1 shows two selected examples across six views and seven conditions, including No Adapter, LLH, and Generic Linear. These outcome-selected examples do not estimate artifact prevalence or texture fidelity.

The unmodified native-default adapter path is not represented by Fresh C's No Adapter condition: No Adapter sets scale to zero, while an unset scale field applies the geometry residual without a scale multiplier. Fresh C has no separate output for that native-default path, so this comparison remains unresolved. The historical N=20 unseen-view check uses unlit base color and has mixed endpoint directions. The attempted Fresh C bake did not pass its native-input gate; no valid Fresh C bake, seam, or PBR result is claimed. We also cannot verify whether the reviewer-facing portal exposed the supplied video.

A later four-object color-pathway development audit further distinguishes a control channel from a repair. Perturbing the global appearance embedding shifted chroma in the registered directions on all four selected objects. The Fresh B input-only audit found that stored embeddings matched neither compared source-conditioning reconstruction within 0.03 for 150/150 inputs, but did not establish that this discrepancy causes the artifacts. The C1 chroma anchor met its numeric gate (mean unseen-view ΔFG-CIEDE2000 −1.5602; 95% CI [−2.2621, −0.6299]) but failed locked visual review: one case showed no clear gain, while the other retained mismatch and showed a faint cyan/blue rim. B2's selected raw-source embedding substitution also failed its numeric gate (mean object-level change +0.1729; 95% CI [−0.2044, +0.6810]; one of four improved) and showed no clear visual correction. No independent Fresh B repair validation was performed. These development findings identify a controllable appearance pathway and a plausible cache-alignment contributor, not a validated color fix or complete root cause.

We also completed a separate, failure-enriched 26-object color diagnosis using paired No Adapter, GFL, and LLH outputs with six unique target views per object. GFL reduced mean reference-relative foreground CIEDE2000 versus No Adapter by 19.65 (95% paired object-bootstrap CI [−26.37, −13.25]; 24/26 objects), but the two cases shown in the submitted 01549 Figure 4 retained visible pink or purple hue shifts across all three conditions. LLH minus GFL increased mean CIEDE2000 by 3.58 (95% CI [+0.46, +6.71]) and reduced local gradient and high-frequency measures, consistent with detail suppression rather than a color correction. A decoded RGB snapshot showed the hue shift before baking; a ground-truth VAE round trip did not reproduce the same direction or magnitude in the selected case. Because this diagnostic subset was failure-enriched, it is not an independent population confirmation. The complete color-generation cause remains unidentified, and no repair is validated.

**Location.** Main manuscript: Figure 4 (p. 13), the archival color-shift Figure 6 (p. 15), full-object Figure 7 (p. 16), the color results and Table 7 (pp. 8–9), and Limitations (p. 11). Supplement: selected six-view/seven-condition examples in Figure S1 (p. 10), Sections S6–S8 (pp. 9–10), and the paired color diagnosis in S13 (p. 13). The Fresh C figure-source and ROI manifest records image hashes and crop coordinates.

### Comment 2 — Held-out matched evaluation

**Response.** The earlier 01549 revision reported a probe-disjoint 276-object schedule-transfer analysis using a separate v2 strong-residual, per-layer-capped adapter. We retain that first-round result in Supplementary Section S9; it does not substitute for a matched comparison of the current main adapter.

Fresh C supplies a matched held-out image-space comparison on 300 UIDs disjoint from the earlier 24-object schedule-development probe and the original 300-object evaluation. Its primary four-condition run and same-cohort Generic Linear/LLH addendum share a frozen checkpoint, runner source, cohort, inputs, views, metric implementation, and per-object seed policy. The integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The registered C3−GFL FG-PSNR difference is +0.522352 dB (95% object-bootstrap CI [+0.404160,+0.640669]).

We report the counter-results alongside this positive contrast: GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. We also clarify that the comparison does not isolate schedule timing. The 50-step applied deep and middle scale sums are 82.5 each for C3 and 62.5 each for GFL; both have a shallow sum of 40 after the native 0.8 cap. Fresh C therefore supports the recorded C3 intervention relative to GFL under this wrapper, not a timing-only effect.

The Fresh C checkpoint is a controlled retraining; it is not presented as the unavailable historical 01549 main-table weight artifact or as a numerical reproduction of the submitted +0.96 dB estimate. The historical v1 main-table and v2 Table 9/FAC adapter identities remain separate. Core-7 is retained only as a retrospective Supplement diagnostic: it reports C3−GFH +0.725229 dB Full-view PSNR and −1.214235 dB FG-PSNR, but does not establish one shared runner or complete input identity. Fresh B and A3b results are also retained as sensitivity evidence rather than preregistered confirmation because the lock text's stated freeze time (2026-10-05 08:40 UTC) predates the earliest preserved commit containing that file (2026-10-06 00:52 UTC), so the retained history does not authenticate pre-run availability.

**Location.** Main manuscript: Methods (pp. 3–5), Tables 3–4 (p. 8), temporal-placement analysis (pp. 7–9), and Limitations (p. 11). Supplement: S2 (p. 2), S3 (pp. 3–5), S4–S5 (pp. 6–8), S8 (p. 10), and S9 (p. 11).

### Comment 3 — Texture variation versus texture fidelity

**Response.** We agree that larger gradients, RGB variation, or Laplacian variance do not establish faithful texture reproduction. The manuscript treats these as variation diagnostics only and does not use them to claim fidelity. Fresh C reports image-space agreement endpoints, not a validated texture-fidelity measure. A separate retrospective analysis on FRESH_CONFIRM_300 found a 9/10 plus-one-corrected Holm association family between LLH−GFL image-space deltas and ground-truth descriptors; its Laplacian-variance strata range from a +4.14 dB FG-PSNR mean (92% LLH-favorable) in Q1 to slightly negative means in Q3 and Q4. The only non-rejecting test was FG-LPIPS versus foreground coverage (Holm-adjusted p=0.0508). This is a noncausal, post-outcome sensitivity result, not a fidelity measure, a selector, or evidence for C3. The earlier 3AFC study remains a separate subjective-preference result for its original three conditions; it is not Fresh C evidence, a reference-fidelity measure, or a 3D-quality result.

**Location.** Main manuscript: metric definitions (p. 3), Figures 4–7 (pp. 13–16), preference Table 9 (p. 10), and Limitations (p. 11). Supplement: S2 (p. 2), S7 (pp. 9–10), and the retrospective complexity analysis in S12 (p. 12).

### Comment 4 — Paired uncertainty and Edge-SSIM

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. Table 4 reports paired Fresh C intervals. C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084,−0.01683]), which we describe as an endpoint trade-off. No non-inferiority margin was prespecified, and we make no equivalence or non-inferiority claim. The historical 0.529-versus-0.559 values are not presented as a replicated Fresh C comparison.

**Location.** Main manuscript: Table 4 and endpoint interpretation (p. 8). Supplement: Section S2 (p. 2).

### Comment 5 — FAC reproducibility and code availability

**Response.** We retain the negative FAC controlled re-examination reported in the first-round 01549 revision, including its seven-configuration results and untrained control. The stated study used roughly 6×10³ trainable controller parameters, AdamW with a peak learning rate of $10^{-4}$, 100 warm-up steps, 2,000 training steps, a reported 1,706-object training pool, and a paired 300-object evaluation. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained 12-object C3-envelope control had ΔFG-PSNR −0.18 dB (95% CI [−0.42,+0.05]).

We disclose that the recovered configuration points to a 1,200-object list rather than the 1,706-object pool stated in 01549, and the available archive does not bind the training seed, outputs, and runtime in a single run manifest. These remain previously reported results, not a new 1008 experiment. The earlier reviewer encouraged code release; we do not claim a public release.

**Location.** Main manuscript: FAC discussion (p. 10) and Limitations (p. 11). Supplement: Section S11 and Table S13 (pp. 11–12).

## Reviewer 2

### Concern 1 — Methodological contribution beyond schedule selection

**Response.** The contribution is a task-specific study of how geometry-residual strength can be controlled and measured inside a multi-view texturing system. TCAS makes the requested intervention explicit, while the execution analysis distinguishes requested scale, wrapper-applied scale under native caps, and the resulting residual magnitude. Fresh C then compares that intervention with fixed and scheduled alternatives under matched inputs and object-paired image-space endpoints. This combination provides reproducible evidence about what the control changes in this pipeline and about where interpretation fails: GFH and Generic Linear have more favorable means than C3 on all four displayed cohort endpoints, and C3/GFL differ in applied deep- and middle-layer scale sums, so their contrast does not isolate timing alone. We therefore retain TCAS as the named task-specific intervention and empirical comparison framework, without claiming that piecewise scheduling itself is a new general algorithm or that C3 is optimal.

We now compare the scope directly with Scheduled Style Injection (SSI), which studies style-injection schedules across layers and denoising time and also schedules geometry-conditioned ControlNet strength. SSI establishes that schedule design is not new in general. TCAS addresses a different task and residual interface. Its contribution is the operational specification of this intervention, the paired comparison of fixed and scheduled controls, and the resulting account of cap-, dose-, endpoint-, and object-dependent behavior in multi-view texture generation. The stage-placement analysis further shows that temporal L--L--H is favored over C3 on all six formal endpoints in a separate post-inspection follow-up. Fresh B's lock chronology is not authenticated, so those temporal and A3b findings are presented as sensitivity evidence; the retrospective texture-complexity analysis likewise identifies boundaries rather than a schedule selector. These results support an empirical system contribution, not a universal schedule law or a claim that C3 is the overall winner.

**Location.** Main manuscript: Introduction and Related Work (pp. 1–2), TCAS Method (pp. 3–4), Tables 3–8 (pp. 8–10), stage analysis (pp. 7–9), and Limitations/Conclusion (p. 11). Supplement: S3 (pp. 3–5), S4–S5 (pp. 6–8), S9 (p. 11), and the retrospective complexity boundary in S12 (p. 12).

### Concern 2 — CAI and empirical schedule selection

**Response.** We agree that the CAI proposition and proof did not independently derive C3. We remove CAI's selector, proposition, proof, and optimality claim. We retain the TCAS residual-injection equation, three-stage profile, C3 definition, and 24-object development record, now identified as historical development evidence rather than a verified ranking or unique optimum. This correction concerns CAI's rationale and does not remove TCAS.

**Location.** Main manuscript: TCAS Method (pp. 3–4), development subsection/Table 2 (p. 7), and Figure 5 (p. 14). Supplement: historical development diagnostics in S10/Table S12 (p. 11).

### Concern 3 — Cross-backbone generalization and interaction inference

**Response.** We agree that adapter variations within one MVPainter-style family do not establish cross-backbone generalization. The MV-Adapter probe analyzed 98 of 99 planned inputs; the omitted frozen GLB had path geometry but no triangle faces, and no substitute was used. The production additive-residual bootstrap had an invalid null for interaction inference and is not used as evidence.

The post hoc exploratory object-cluster robust Wald reanalysis (8 degrees of freedom) found no interaction surviving Holm correction across four metrics: FG-LPIPS raw p=0.101, Holm p=0.303; PSNR p=0.434, Holm p=0.868; FG-SSIM p=0.039, Holm p=0.156; and CIEDE2000 p=0.862, Holm p=0.862. These results are not proof that interaction is absent or that conditions are equivalent. A separate 76-object MV-Adapter layer-mapping study found mixed metric directions under a budget-neutral $B^{\prime}$ partition; its M3 companion changed both grouping and total nominal residual budget (mean multiplier 0.8065) and was classified as retrospective because the protocol and results first appear in the same preserved commit. The two mapping analyses do not establish a general mapping law or generalize TCAS across backbones. The separate MVDiffusion probe covered 75 objects through a different correspondence-aware interface and produced mixed or negative endpoint results. Because these probes use different conditioning paths and runners, they are interface checks rather than a matched architecture comparison; cross-backbone generalization remains unestablished.

**Location.** Main manuscript: Cross-Interface Evaluation/Table 8 (p. 10) and Limitations (p. 11). Supplement: Section S5 (pp. 6–8).

## Reviewer 3

We thank Reviewer 3 for the positive assessment. No new technical change or experiment was requested.
