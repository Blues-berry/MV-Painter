# Response to Reviewers — 1008 second-round revision

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The R1/R2/R3 comments addressed here concern the subsequent second round. We retain the prior 01549 work that remains relevant, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision keeps Timestep-Conditioned Adapter Scaling (TCAS) as the method and narrows its claims to the evidence available. We now describe the actual Fresh C figures and controls, correct the stage-placement result, distinguish applied scale from schedule shape, and replace an invalid interaction-bootstrap inference with the available exploratory object-cluster robust Wald analysis. The revisions and remaining limits are detailed below.

## Reviewer 1

### Comment 1 — Visual artifacts, full-object comparisons, and 3D fidelity

**Response.** We agree that the earlier panels did not make it easy to compare the complete object and the same local detail. Figure 4 now shows Reference, GFL, GFH, and C3 for one C3–GFL endpoint-favorable case and one adverse case. Figure 5 preserves the fixed-scale comparison and adds a separate Generic Linear counterexample. Each panel pairs a full target-view context with one shared pixel ROI; the displayed RGB outputs are not independently adjusted. The full six-view, seven-condition comparison—including No Adapter, LLH, and Generic Linear—remains in Supplementary Figure S1. The selected panels illustrate outcomes and do not estimate artifact prevalence or texture fidelity.

The unmodified native-default adapter path is not represented by Fresh C's No Adapter condition: No Adapter sets scale to zero, while an unset scale field applies the geometry residual without a scale multiplier. Fresh C has no separate output for that native-default path, so this comparison remains unresolved. The historical N=20 unseen-view check uses unlit base color and has mixed endpoint directions. The attempted Fresh C bake did not pass its native-input gate; no valid Fresh C bake, seam, or PBR result is claimed. We also cannot verify whether the reviewer-facing portal exposed the supplied video.

**Location.** Main manuscript: Figures 4–5 (pp. 11–12) and Limitations (pp. 8–9). Supplement: Figure S1 (p. 9) and Sections S6–S8 (pp. 8–9). The figure-source and ROI manifest records image hashes and crop coordinates.

### Comment 2 — Held-out matched evaluation

**Response.** The earlier 01549 revision reported a probe-disjoint 276-object schedule-transfer analysis using a separate v2 strong-residual, per-layer-capped adapter. We retain that first-round result in Supplementary Section S9; it does not substitute for a matched comparison of the current main adapter.

Fresh C supplies a matched held-out image-space comparison on 300 UIDs disjoint from the earlier 24-object schedule-development probe and the original 300-object evaluation. Its primary four-condition run and same-cohort Generic Linear/LLH addendum share a frozen checkpoint, runner source, cohort, inputs, views, metric implementation, and per-object seed policy. The integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The registered C3−GFL FG-PSNR difference is +0.522352 dB (95% object-bootstrap CI [+0.404160,+0.640669]).

We report the counter-results alongside this positive contrast: GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. We also clarify that the comparison does not isolate schedule timing. The 50-step applied deep and middle scale sums are 82.5 each for C3 and 62.5 each for GFL; both have a shallow sum of 40 after the native 0.8 cap. Fresh C therefore supports the recorded C3 intervention relative to GFL under this wrapper, not a timing-only effect.

The Fresh C checkpoint is a controlled retraining; it is not presented as the unavailable historical 01549 main-table weight artifact or as a numerical reproduction of the submitted +0.96 dB estimate. The historical v1 main-table and v2 Table 9/FAC adapter identities remain separate. Core-7 is retained only as a retrospective Supplement diagnostic: it reports C3−GFH +0.725229 dB Full-view PSNR and −1.214235 dB FG-PSNR, but does not establish one shared runner or complete input identity.

**Location.** Main manuscript: Methods (pp. 4–5), Tables 3–4 (p. 7), stage analysis (p. 8), and Limitations (pp. 8–9). Supplement: S2 (p. 2), S5 (pp. 5–7), S8 (p. 8), and S9 (p. 9).

### Comment 3 — Texture variation versus texture fidelity

**Response.** We agree that larger gradients, RGB variation, or Laplacian variance do not establish faithful texture reproduction. The manuscript treats these as variation diagnostics only and does not use them to claim fidelity. Fresh C reports image-space agreement endpoints, not a validated texture-fidelity measure. The earlier 3AFC study remains a separate subjective-preference result for its original three conditions; it is not Fresh C evidence, a reference-fidelity measure, or a 3D-quality result.

**Location.** Main manuscript: metric definitions (p. 3), Figures 4–5 (pp. 11–12), preference Table 5 (p. 7), and Limitations (pp. 8–9). Supplement: S2 (p. 2) and S7 (p. 8).

### Comment 4 — Paired uncertainty and Edge-SSIM

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. Table 4 reports paired Fresh C intervals. C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084,−0.01683]), which we describe as an endpoint trade-off. No non-inferiority margin was prespecified, and we make no equivalence or non-inferiority claim. The historical 0.529-versus-0.559 values are not presented as a replicated Fresh C comparison.

**Location.** Main manuscript: Table 4 and endpoint interpretation (p. 7). Supplement: Section S2 (p. 2).

### Comment 5 — FAC reproducibility and code availability

**Response.** We retain the negative FAC controlled re-examination reported in the first-round 01549 revision, including its seven-configuration results and untrained control. The stated study used roughly 6×10³ trainable controller parameters, AdamW with a peak learning rate of 10⁻⁴, 100 warm-up steps, 2,000 training steps, a reported 1,706-object training pool, and a paired 300-object evaluation. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained 12-object C3-envelope control had ΔFG-PSNR −0.18 dB (95% CI [−0.42,+0.05]).

We disclose that the recovered configuration points to a 1,200-object list rather than the 1,706-object pool stated in 01549, and the available archive does not bind the training seed, outputs, and runtime in a single run manifest. These remain previously reported results, not a new 1008 experiment. The earlier reviewer encouraged code release; we do not claim a public release.

**Location.** Main manuscript: FAC discussion (p. 7) and Limitations (pp. 8–9). Supplement: Section S11 (pp. 10–11) and Table S13 (p. 11).

## Reviewer 2

### Concern 1 — Methodological contribution beyond schedule selection

**Response.** We recognize the novelty concern and do not claim that the piecewise schedule is a general algorithmic contribution. TCAS is retained as a task-specific, training-free control on the existing GeoTex-Adapter residual in multi-view texture generation. We define the requested scale, wrapper-applied scale under native caps, and resulting residual magnitude separately. The matched Fresh C comparison provides a bounded result for C3 against GFL, while GFH and Generic Linear are stronger on all four displayed cohort means; the applied-scale sums also show why the C3−GFL estimate cannot be attributed to timing alone.

We now compare the scope directly with Scheduled Style Injection (SSI), which studies style-injection schedules across layers and denoising time and also schedules geometry-conditioned ControlNet strength. SSI establishes that schedule design is not new in general. TCAS addresses a different task and residual interface, and its contribution here is the tested intervention plus its paired image-space and execution-semantics analysis. The stage-placement analysis further shows that temporal L--L--H is favored over C3 on all six formal endpoints in a separate post-inspection follow-up, so we do not present C3 as a universal winner. We acknowledge that the remaining task-specific contribution may not meet the journal's novelty threshold; that judgment is for the editor.

**Location.** Main manuscript: Introduction and Related Work (pp. 1–3), TCAS Method (pp. 3–5), Tables 3–4 (p. 7), stage analysis (p. 8), and Limitations (pp. 8–9). Supplement: S3 (p. 3), S4–S5 (pp. 5–7), and S9 (p. 9).

### Concern 2 — CAI and empirical schedule selection

**Response.** We agree that the CAI proposition and proof did not independently derive C3. We remove CAI's selector, proposition, proof, and optimality claim. We retain the TCAS residual-injection equation, three-stage profile, C3 definition, and 24-object development record, now identified as historical development evidence rather than a verified ranking or unique optimum. This correction concerns CAI's rationale and does not remove TCAS.

**Location.** Main manuscript: TCAS Method (pp. 3–4) and development subsection/Table 2/Figure 6 (p. 6). Supplement: historical development diagnostics in S10 (pp. 9–10).

### Concern 3 — Cross-backbone generalization and interaction inference

**Response.** We agree that adapter variations within one MVPainter-style family do not establish cross-backbone generalization. The MV-Adapter probe analyzed 98 of 99 planned inputs; the omitted frozen GLB had path geometry but no triangle faces, and no substitute was used. The production additive-residual bootstrap had an invalid null for interaction inference and is not used as evidence.

The post hoc exploratory object-cluster robust Wald reanalysis (8 degrees of freedom) found no interaction surviving Holm correction across four metrics: FG-LPIPS raw p=0.101, Holm p=0.303; PSNR p=0.434, Holm p=0.868; FG-SSIM p=0.039, Holm p=0.156; and CIEDE2000 p=0.862, Holm p=0.862. These results are not proof that interaction is absent or that conditions are equivalent. The separate MVDiffusion probe covered 75 objects through a different correspondence-aware interface and produced mixed or negative endpoint results. Because the probes use different conditioning paths and runners, they are interface checks rather than a matched architecture comparison; cross-backbone generalization remains unestablished.

**Location.** Main manuscript: stage/applicability analysis (p. 8) and Limitations (pp. 8–9). Supplement: Section S5 (pp. 5–7).

## Reviewer 3

We thank Reviewer 3 for the positive assessment. No new technical change or experiment was requested.
