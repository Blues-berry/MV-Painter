# Draft response to the supplied reviewer comments

**Status: working response only.** This response is aligned to the evidence-first manuscript in `manuscript/main_1006.tex`. It is not a claim that every reviewer gate has closed. The user-supplied review file retains “Initial submission” labels; this draft responds to the substantive R1/R2/R3 comments present in that file and makes no inference about an unprovided editor decision or later review.

## Editorial note

We have reframed the manuscript as a bounded empirical study of inference-time geometry-adapter scaling in one MVPainter-style pipeline. We removed claims that layer-by-time scheduling is a new general diffusion control space, that CAI derives an optimum, that one schedule is universally best, or that results transfer broadly across backbones. We added the directly related work *Scheduled Style Injection*, which studies layer/time control and geometric ControlNet schedules. We distinguish requested scale, cap-applied scale, and measured post-scale correction norms, and preserve the retrospective chronology of FRESH_CONFIRM_B: it is a disjoint object cohort with a passing output-integrity gate, but its comparison and safeguard locks followed prior outcome exposure.

The revision reports metric- and object-specific results rather than a single winner. Several requests remain unresolved: no new LLH human responses exist; the valid GLB-native endpoint covers N=20 and does not assess seams or full PBR; the strict-276 C3 comparison is retrospective with incomplete input-hash/common-runner provenance; and methodological contribution adequacy remains an open editorial judgment. We have not described this package as ready for system upload.

## Reviewer 1

### R1.1 — Full-object quality, color shifts, baking, unseen views, and seams

**Response.** We agree that image-space metrics cannot establish complete 3D appearance. The revised package includes the full GT-stratified 24-object contact sheet, which contains the unmodified pipeline and fixed-scale controls, together with a sampler-conformant re-evaluation of the exact stored GLBs on 20 UV-supported objects and 11 unseen views per object-condition. The GLB results are mixed across FG-PSNR, FG-LPIPS, and CIEDE2000. Four no-UV objects remain excluded, no texture was rebaked, and the render is unlit base-color rather than full PBR. The former seam analyzer is invalid for the exported UV mapping, so we remove seam-quality claims rather than retain its numbers.

The new LLH human study has zero responses. The manuscript does not transfer the earlier 01549 preference result to LLH or unseen-view material fidelity. Accordingly, this response is **partial** for the request to establish perceived fidelity and seams. The paper is not ready to claim that broader practical-value gate is closed.

**Manuscript changes.** Sections 3.3, 4.4, and 5; Supplementary S5 and S8; Fig. S1; Table 3.

### R1.2 — Same-protocol disjoint evaluation of the main adapter and the historical +0.96 dB gain

**Response.** We retire the pooled +0.96 dB claim as an independently confirmed effect. On strict-276, GC3−GFL FG-PSNR is +1.207771 dB (nominal 95% CI [1.116967, 1.294989], 259/276 favorable) and Edge-SSIM is +0.007760 [0.006773, 0.008746] (233/276). This pair was not a registered primary Core-7 contrast, and complete legacy input-tensor hashes and common-runner identity are unavailable. We label it a retrospective same-cohort supplement. On the disjoint FRESH_CONFIRM_B objects, a post-hoc native-GC3−native-GFL analysis gives FG-PSNR +0.501881 dB [0.341873, 0.662862] (100/150) and Edge-SSIM +0.005034 [0.003348, 0.006753] (105/150); all seven Core-7 endpoint means favor GC3 in this pair. The B cohort used one runner and passed the input-integrity audit, but B had already been unblinded and this B3 pair was not registered. We therefore describe it as retrospective evidence on a disjoint object cohort, not prospective or registered confirmation. GC3−GFH remains a trade-off: on strict-276, foreground PSNR and Edge-SSIM favor GFH while full-image PSNR and SSIM favor GC3.

This addresses the reviewer’s request with an additional disjoint-cohort result while retaining the chronology and registration limits. If the reviewer requires a newly registered C3 pair on an untouched cohort, that stricter request remains open; the frozen 508-candidate pool has already been partitioned into prior Fresh300 and B cohorts, so such a run would require a separately sourced and audited cohort rather than reusing objects.

**Manuscript changes.** Sections 3.2 and 4.5; Supplementary S6; strict-276 row audit and provenance files in `data/strict276/`.

### R1.3 — Texture variation versus texture fidelity

**Response.** We separate structural/reference metrics, texture-variation proxies, visual inspection, and stored 3D endpoints. Laplacian variance, RGB spread, gradients, and high-frequency energy are not interpreted as fidelity on their own. The GT-stratified visual review found color/material mismatch in 18/24 objects and fine-detail loss in 21/24; it is identified as a descriptive author audit, not a human study. The GLB-native endpoint is reported metric by metric and has mixed directions. No human-fidelity claim is made for LLH.

**Manuscript changes.** Sections 1, 2.3, 4.4, and 5; Supplementary S5 and S8.

### R1.4 — Paired confidence intervals, Edge-SSIM, and non-inferiority

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. The revised text uses paired object-bootstrap intervals and never labels a zero-crossing interval as equivalence. The strict-276 supplement now reports Edge-SSIM for both GC3−GFL (+0.007760, 95% CI [0.006773, 0.008746]) and GC3−GFH (−0.026012, [−0.028044, −0.023991]); the separate Fresh-B post-hoc pair reports +0.005034 [0.003348, 0.006753]. These are endpoint-specific effects, not preservation or non-inferiority claims. The LLH−LFM-exact margins remain the previously frozen ±0.5 dB and ±0.01 bounds and apply only to those endpoints and that contrast.

**Manuscript changes.** Section 3.4; Supplementary S6 Tables S6–S7; object-level strict-276 and Fresh-B paired statistics in `data/derived/`.

### R1.5 — FAC experiment reproducibility

**Response.** FAC is removed from the revised paper's method and contribution claims because it is not needed to support the bounded scaling characterization and the available FAC reconstruction is not fully closed for portable reproduction. We do not use the prior negative FAC result to support this manuscript's claims. This is a scope reduction; it does not constitute a reproducibility package for FAC if the reviewer expects that extension to remain in the paper.

**Manuscript changes.** FAC is absent from the revised manuscript; the archive audit and existing release materials are retained separately. If FAC is reinstated, its complete training code, source rows, checkpoint identity, and clean-clone reconstruction must be added before submission.

## Reviewer 2

### R2.1 — Contribution beyond manual schedule selection

**Response.** We agree that the earlier framing overstated the methodological novelty. The revision withdraws “first” and general control-space claims and cites *Scheduled Style Injection*, which already schedules style and geometric ControlNet strength over depth/time. We limit the contribution to an audited empirical account of one MVPainter-style residual/cap implementation, object-level heterogeneity, measured dose boundaries, and a bounded baked-texture endpoint. We do not claim that the new evidence establishes sufficient methodological novelty for the venue.

**Disposition.** The scientific scope is corrected, but contribution adequacy remains **open/blocking** for final readiness and requires editorial judgment. A narrow narrative cannot guarantee that the work meets the journal's novelty threshold.

### R2.2 — CAI as post-hoc explanation

**Response.** CAI is removed from the revised paper's contribution and method claims. No independent predictive test supports treating it as a schedule derivation. The manuscript presents profiles as tested operating conditions and does not describe an optimum derived from CAI.

### R2.3 — Cross-backbone generalization

**Response.** We report MV-Adapter (98 evaluable objects) and MVDiffusion (75 objects) separately as bounded interface results. They use different interventions and cohorts. We neither pool absolute metrics nor infer that architecture caused the difference. The conclusion is limited to “transfer was not established across the tested interfaces.”

## Reviewer 3

We thank Reviewer 3 for the favorable assessment. No separate actionable concern appears in the supplied comments. This does not waive the unresolved R1/R2 items above.

## Conditions before this response can be finalized

1. Resolve the human-fidelity gate with the frozen LLH responses, or obtain an explicit editorially acceptable claim reduction that removes the need for a human-fidelity conclusion.
2. Confirm whether the editor accepts the explicitly retrospective, disjoint Fresh-B GC3−GFL comparison as sufficient for the revised scope. If a prospective C3 confirmation is required, acquire and freeze a new disjoint cohort; do not substitute LLH for C3.
3. Complete a portable clean-clone reconstruction of every included table, figure, and data-availability artifact, or remove any unverified element.
4. Obtain a final contribution/venue decision after explicit comparison with *Scheduled Style Injection*; this remains the principal reviewer-readiness blocker.
5. Re-run pagination and replace section references with final page and line numbers after the text is frozen.
