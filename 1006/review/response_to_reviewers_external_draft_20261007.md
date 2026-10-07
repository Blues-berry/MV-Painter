# Point-by-point response to reviewers

**External working draft.** Page and line references below point to the compiled revised manuscript; supplementary section and page references point to the compiled supplementary material.

## Reviewer 1

### R1.1 — Visual artifacts, broader comparisons, unseen views, seams, and video

**Reviewer comment**

The reviewer asks for broader full-object comparisons including the unmodified pipeline and a fixed-scale baseline, and requests evidence about baked unseen views and seam or cross-view consistency. The reviewer also notes color shifts, repeated patterns, and difficulty assessing the supplementary video.

**Response**

We agree that image-space metrics and selected image panels cannot establish unseen-view or baked-texture quality. The revised manuscript acknowledges that color/material mismatch and fine-detail loss remain visible in some selected outputs, including outputs with favorable image-space metrics. The new panels are selected illustrations, not a representative sample or cohort-wide visual-performance evidence.

The native-UV and sampler validation did not support a technically valid new 3D or seam comparison. We therefore removed the proposed 3D and seam-superiority claims. The revised manuscript states directly that the available image-space evidence does not establish material correctness, unseen-view quality, baked-texture quality, or seam consistency.

**Changes in revised manuscript:** The scope limitation is stated on p. 2, lines 66–69 and p. 4, lines 318–325. Selected side-by-side image-space examples are described on p. 4, lines 279–289 and shown in Fig. 4 (p. 8).

### R1.2 — Main-adapter evaluation beyond schedule-selection data

**Reviewer comment**

The reviewer notes that the earlier pooled evaluation included schedule-selection objects and that a separate probe-disjoint comparison changed the adapter and schedules. The reviewer asks for the main adapter and relevant baselines under one held-out protocol.

**Response**

We agree that the earlier strict-subset comparison does not directly establish the main-adapter result under a matched protocol. The revised manuscript reports a revision-era Fresh C follow-up using the main GeoTex-Adapter checkpoint on a frozen cohort of 300 objects. Its registered primary C3−GFL foreground-PSNR difference is +0.522 dB (95% object-bootstrap CI [+0.404, +0.641]); 68.7% of objects favor C3 on this endpoint.

This follow-up was motivated by results observed in the earlier work. It is not a replication under the original registration and does not verify or replace the historical gain estimate. The revised manuscript keeps the revision-era result separate from retrospective historical estimates.

**Changes in revised manuscript:** The cohort, checkpoint, paired protocol, and registration caveat are described on p. 3, lines 195–212; the primary result is on p. 4, lines 248–255 and Fig. 2 (p. 6).

### R1.3 — Texture variation versus texture fidelity

**Reviewer comment**

The reviewer asks us to distinguish texture variation from texture fidelity because larger gradients or Laplacian variance may reflect artifacts as well as meaningful detail.

**Response**

We agree. Gradient magnitude, Laplacian variance, color variation, and related quantities measure image variation; by themselves they do not show faithful reproduction. The revised manuscript reports image-space endpoints separately and states that neither these diagnostics nor the image-space results establish perceptual or material fidelity.

**Changes in revised manuscript:** Variation diagnostics and their limits are defined on p. 3, lines 159–177 and p. 4, lines 318–325. No author-inspection count is presented as a population rate.

### R1.4 — Paired intervals, Edge-SSIM trade-off, and non-inferiority

**Reviewer comment**

The reviewer notes that an interval crossing zero does not establish equivalence or non-inferiority and asks us to report paired intervals and acknowledge the Edge-SSIM trade-off.

**Response**

A confidence interval crossing zero does not establish equivalence or non-inferiority, and no non-inferiority margin was prespecified.

In the frozen Fresh C cohort (N=300), the reviewer-requested C3−GFH Edge-SSIM contrast is −0.01881 (nominal 95% paired object-bootstrap CI [−0.02080, −0.01679]); 47 objects favor C3 and one is tied, so the object-level direction favors GFH. Full-image PSNR shows a trade-off in the other direction: +0.6607 dB (95% CI [+0.5858, +0.7358]), with 252 of 300 objects favoring C3. This comparison was computed post hoc within the frozen Fresh C cohort and was not part of its registered confirmatory family.

An earlier, disjoint Fresh B cohort provides a separate retrospective/post-hoc supporting sensitivity analysis: Edge-SSIM −0.018486 (95% CI [−0.021465, −0.015527]) and full-image PSNR +0.7490 dB (95% CI [+0.6548, +0.8414]). We keep the cohorts separate and do not pool or combine them.

**Changes in revised manuscript:** The post-hoc status is stated on p. 3, lines 223–227; the endpoint-specific Fresh C trade-off and the removal of equivalence/non-inferiority language are on p. 4, lines 268–278. The complete seven-endpoint Fresh C and Fresh B tables are in Supplementary Sections S4 and S5 (p. 2).

### R1.5 — Reproducibility and release of FAC

**Reviewer comment**

The reviewer says that the FAC experiments remain difficult to reproduce and encourages code release.

**Response**

We agree that the historical FAC experiment does not meet the reproducibility standard adopted for this revision. Because FAC is not required for the bounded main contribution, we removed it from the revised manuscript and supplement rather than present it as a reproducible or released result.

**Changes in revised manuscript:** The revised scope and conclusion no longer rely on FAC (p. 2, lines 51–69; p. 5, lines 342–357). The revised supplementary material contains no FAC result or dose-response section (pp. 1–4).

## Reviewer 2

### R2.1 — Methodological contribution and novelty

**Reviewer comment**

The reviewer is not convinced that a manually selected schedule is a sufficiently substantial contribution beyond an existing adapter and questions whether CAI independently derives the schedule.

**Response**

We agree that layer-by-timestep scheduling itself is not a new control primitive. The revised manuscript acknowledges prior work on scheduled style injection and timestep-dependent guidance. It describes C3 as a tested configuration on the existing MVPainter adapter path, not as a new scheduling primitive or an independently derived optimum.

The contribution is now bounded to implementation-aware scale execution and object- and endpoint-dependent Fresh C evidence. The generic-linear addendum is reported alongside C3: its mean foreground-PSNR difference favors generic linear (C3−linear −0.593 dB, 95% CI [−0.837, −0.351]), while the median is +0.074 dB and 51.7% of objects favor C3, showing object-level heterogeneity. Mean foreground LPIPS also favors generic linear (C3−linear +0.01351, 95% CI [+0.01160, +0.01549]). These results do not support a universal winner.

**Changes in revised manuscript:** Prior work and the bounded contribution statement appear on p. 2, lines 43–65 and 116–138. Requested scale, applied scale, and correction magnitude are distinguished on p. 3, lines 151–158. Generic-linear results are reported on p. 4, lines 256–267 and Supplementary Section S3 (pp. 1–2).

### R2.2 — CAI as a post-hoc rationale

**Reviewer comment**

The reviewer argues that CAI appears to formalize a schedule selected empirically rather than derive it independently.

**Response**

We agree that CAI does not prospectively derive or validate the schedule. We removed the CAI model and formal selection rule from the revised manuscript and supplement, and removed predictive, derivation, and optimality claims. C3 is presented only as a tested configuration.

**Changes in revised manuscript:** The tested-configuration scope is stated on p. 3, lines 178–191 and reiterated in the conclusion on p. 5, lines 342–357; no CAI section remains in the revised supplementary material (pp. 1–4).

### R2.3 — Generalization to a different backbone

**Reviewer comment**

The reviewer says that the single MVPainter-style architecture family does not establish cross-backbone generality and asks for evaluation on a genuinely different geometry-conditioned multi-view diffusion backbone.

**Response**

We agree that the primary-system experiments do not establish cross-backbone generality. The revised manuscript reports MVDiffusion and MV-Adapter as interface-specific boundary tests, not matched replications of the same residual-adapter intervention. For MVDiffusion, the schedule acts on correspondence-aware decoder-side CPBlocks; official SD2-depth weights were unavailable, so the within-panel comparison used the same compatibility base. The MV-Adapter analysis is exploratory and does not confirm the broad interaction observed on the primary system. We do not infer architecture-level causation or universal transfer.

**Changes in revised manuscript:** The boundary tests and their limits appear on p. 4, lines 290–309 and 327–335, with a separate summary in Supplementary Section S6 (p. 2).

## Reviewer 3

### R3 — Positive assessment

**Reviewer comment**

The reviewer considers the revision suitable for publication.

**Response**

We thank the reviewer for the positive assessment and for recognizing the work invested in the revision.

**Changes in revised manuscript:** No additional technical change was required in response to this comment.
