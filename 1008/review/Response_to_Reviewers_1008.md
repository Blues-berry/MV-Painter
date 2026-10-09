# Response to Reviewers — 1008 second-round revision

**Round framing.** The 01549 manuscript submitted on 7 September 2026 is the post-first-round revised version. The present R1/R2/R3 comments are the second-round reviews of that version. We used the official 0907 package—Manuscript, Marked-up Manuscript, Response Letter, Supplement, and LaTeX source—as the historical record. This response preserves the first-round changes that the reviewers recognized and describes only the additional second-round actions.

Dear Editor and Reviewers,

We thank the reviewers for their careful assessment. We have revised the 01549 manuscript for the second round while preserving its TCAS method, the first-round disjoint-holdout analyses, cluster-aware preference study, FAC controlled re-examination, and implementation details. The changes below address the remaining second-round concerns. Fresh C is interpreted as a matched held-out study under one frozen checkpoint and common execution protocol; we do not require its checkpoint hash to equal the historical Table 4 checkpoint. The historical v1/v2 differences remain explicitly documented.

## Reviewer 1

### Comment 1 — Visible artifacts and broader visual evidence

**Response.** We agree that cropped examples were insufficient. Figure 4 now presents selected full-object Fresh C target-view comparisons across the reference, No Adapter, GFL, GFH, C3, LLH, and Generic Linear. It includes a near-median case, an adverse C3–GFL case, and a Generic Linear counterexample; Figure 5 retains the original C3-versus-fixed-scale question with a favorable example and a GFH endpoint trade-off. These panels are outcome-selected illustrations, not an estimate of artifact prevalence.

We also report the bounded historical N=20 unseen-view check using unlit base color. It has mixed endpoint directions. The attempted Fresh C bake did not pass its native-input gate, so no valid Fresh C bake or seam result is claimed. The manuscript makes no PBR/material-fidelity claim. We cannot verify whether the reviewer-facing portal exposed the supplied video.

**Location.** Main manuscript: Figures 4–5 and the limitations discussion. Supplement: Sections S6–S7 and Table S8.

### Comment 2 — Held-out evaluation and matched main comparison

**Response.** The 01549 first-round revision already reported schedule transfer on the probe-disjoint 276-object holdout using its separate v2 strong-residual, per-layer-capped adapter (retained in Supplementary Section S9). We agree that this historical Table 9 result does not itself answer the present comparison because it uses a different adapter instance from the v1 main tables.

Fresh C supplies the held-out comparison requested here. Its N=300 cohort is UID-disjoint from the original 24-object schedule-selection probe and the original 300-object evaluation. The primary four-condition run and same-cohort Generic Linear/LLH addendum share one frozen checkpoint (SHA-256 0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0), runner source (SHA-256 e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3), cohort, inputs, views, metrics, and per-object seed policy (42 + object_idx). All compared conditions share the seed and initial latent for each object. Integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The recorded native caps are deep/middle/shallow = 3.0/3.5/0.8; the submitted scale request, applied scale, and residual correction are reported separately.

The registered primary C3–GFL FG-PSNR difference is +0.522352 dB (95% object-bootstrap CI [+0.404160,+0.640669]). This is the primary R1.2 evidence. We do not impose an additional requirement that Fresh C have the same checkpoint hash as historical 01549 Table 4. We retain the historical distinction: 01549 names v1 weights for its main tables and a separate v2 adapter for Section 4.7/FAC; Fresh C is a controlled retraining and is not presented as a numerical reproduction of the old +0.96 dB estimate.

The counter-results remain visible. GFH and Generic Linear have more favorable means than C3 on all four displayed endpoints. LLH trades endpoint means and object-level responses against C3 and Generic Linear; these outcomes do not support a universal winner.

**Location.** Main manuscript: Experimental protocol and implementation details, Tables 3–4, and limitations. Supplement: Sections S2, S4, S8–S9.

### Comment 3 — Distinguish texture variation from texture fidelity

**Response.** We agree. Laplacian variance, RGB standard deviation, and gradient magnitude are described only as texture-variation diagnostics; higher values may reflect artifacts and do not establish fidelity. Fresh C reports named image-space agreement endpoints, not a validated texture-fidelity measure. We retain the earlier three-condition preference study as a separate subjective-choice result, not as evidence of reference fidelity, baked-texture quality, or Fresh C performance. The unsupported pooled texture-retention claims are not revived.

**Location.** Main manuscript: metric interpretation, Figures 4–5, the retained preference-study subsection, and limitations. Supplement: Sections S2 and S7.

### Comment 4 — Paired intervals and Edge-SSIM trade-off

**Response.** We agree that a confidence interval crossing zero does not establish equivalence or non-inferiority. Table 4 reports paired Fresh C contrasts. C3–GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084, −0.01683]), which we state as an endpoint trade-off. We use no non-inferiority margin and make no equivalence claim. The historical 0.529-versus-0.559 comparison is not represented as a replicated Fresh C estimate.

**Location.** Main manuscript: Table 4 and the endpoint interpretation in the large-scale evaluation section. Supplement: Section S2.

### Comment 5 — FAC reproducibility and code availability

**Response.** The first-round 01549 revision added the FAC training description and a controlled negative re-examination; the current R2 review expressly recognized that work. We therefore retain the reported FAC results and full seven-configuration dose-response table in Supplementary Section S11 rather than deleting this first-round contribution. The reported setup specifies roughly 6×10³ trainable controller parameters, the enhanced latent denoising objective, AdamW, peak learning rate 10^-4, 100 warm-up steps, 2,000 training steps, a 1,706-object training pool, and a paired 300-object evaluation. All trained configurations were reported below TCAS by 1.10–2.94 dB FG-PSNR; the untrained 12-object C3-envelope control had ΔFG-PSNR −0.18 dB (95% CI [−0.42,+0.05]).

We disclose a remaining archive limitation: the recovered local configuration references a 1,200-object list rather than the 1,706-object pool stated in 01549, and the available archive does not bind the training seed, outputs, and runtime in one run manifest. The results are retained as reported first-round evidence, not as a newly reproduced 1008 experiment. The reviewer encouraged code release; we do not claim that code has been publicly released.

**Location.** Main manuscript: Geometry Adapter and Inference Interface, FAC subsection, Limitations. Supplement: Section S11 and the FAC dose-response table.

## Reviewer 2

### Concern 1 — Methodological contribution beyond schedule selection

**Response.** We recognize the concern and retain TCAS as the paper's method. We define it as a training-free, three-stage requested-scale intervention on the existing GeoTex-Adapter residual path and distinguish requested scale, wrapper-applied scale, and residual magnitude. We add no trained parameters and do not modify the base model.

We preserve the first-round changes that Reviewer 2 recognized: the disjoint-holdout evidence, adapter-dependent failure analysis, and FAC controlled re-examination. We also sharpen the task-specific distinction from Scheduled Style Injection (SSI), which already studies layer/time schedules and geometry-conditioned ControlNet strength. We therefore do not claim a new general scheduling primitive or universal schedule. Fresh C contributes the registered C3–GFL result, while GFH, Generic Linear, and LLH provide material endpoint counter-results. The stage-placement and layer-window analyses are reported with their cohort, cap, and dose limitations. We acknowledge that the contribution remains task-specific and that its sufficiency for the journal is an editorial judgment.

**Location.** Main manuscript: Introduction and Related Work, TCAS method, Tables 3–4, stage/applicability analysis, and Limitations. Supplement: Sections S3–S5 and S9.

### Concern 2 — CAI may formalize an empirical schedule

**Response.** We agree. The 01549 first-round revision introduced CAI as a response to the schedule-rationale concern. The second-round criticism shows that its proposition and proof do not establish an independent derivation of C3. We remove the CAI selector, proposition, proof, and optimality claim. We retain the TCAS residual-injection equation, three-stage profile, C3 definition, and the 24-object development record, now labeled as development history rather than a verified ranking or unique optimum. This correction is limited to CAI and does not remove or weaken the TCAS method.

**Location.** Main manuscript: TCAS Method and the 24-object development subsection. Supplement: historical development diagnostics in Section S10.

### Concern 3 — Cross-backbone generalization

**Response.** We agree that changing adapters within the MVPainter-style family does not establish transfer to another backbone. We retain the first-round adapter-dependence analysis as within-family evidence and report the available MV-Adapter and MVDiffusion interface probes with their actual scope.

The MV-Adapter probe contained 98 of 99 planned inputs. Its global interaction cluster-bootstrap test was not significant (p=0.6523); the exploratory object-cluster FG-LPIPS test was p=0.1012 and the four-metric Holm value was p=0.3037. The MVDiffusion probe covered 75 objects using a different correspondence-aware conditioning interface and produced mixed or negative endpoint results. These probes use different conditioning paths and runners, so they are not a matched shared-interface comparison and do not establish general transfer. We state this limitation directly and make no universal cross-backbone claim.

**Location.** Main manuscript: Stage Sensitivity and Applicability Boundaries and Limitations. Supplement: Section S5.

## Reviewer 3

We thank Reviewer 3 for the positive assessment. No new technical change or experiment was requested.
