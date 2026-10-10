# Response to Reviewers — 1008 second-round revision

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The Reviewer 1–3 comments below are the subsequent review of that revision for CAG-D-26-00962. The preserved export labels its reviewer headers “Initial submission”; the author-confirmed round map identifies this packet as the second round. The headings quote the supplied review text. We retain relevant 01549 work, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision keeps Timestep-Conditioned Adapter Scaling (TCAS) as the method and narrows its claims to the evidence available. We now describe the actual Fresh C figures and controls, correct the stage-placement result, distinguish applied scale from schedule shape, and replace an invalid interaction-bootstrap inference with the available exploratory object-cluster robust Wald analysis. We also thank Reviewer 3 for the positive assessment; no additional technical change was requested.

## Reviewer 1

### Comment 1 — “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance.”

**Response.** We agree that the submitted panels did not establish appearance across complete objects or after texture projection. Figure 5 now pairs fixed-scale and Generic Linear comparisons with a shared target view and ROI; Figure 7 shows full-object context and the same ROI for favorable and adverse C3–GFL cases. Figure 6 is a rights-cleared, hash-traced Fresh C example that was not selected for color; it is not a reconstruction of the two unmapped legacy pink-shift cases. Supplementary Figure S1 retains the six-view, seven-condition panel.

Fresh C's No Adapter condition sets adapter scale to zero; it is not the unset-scale native-default path. The attempted Fresh C bake failed its native-input gate, so we report no valid Fresh C baked mesh, seam, or PBR result. We also could not verify reviewer-side access to the supplementary video.

The paired, failure-enriched 26-object color diagnosis shows that GFL reduces mean foreground CIEDE2000 relative to No Adapter by 19.65 (95% CI [−26.37, −13.25]; 24/26 objects), while pink/purple shifts remain in two legacy cases. LLH−GFL increases CIEDE2000 by 3.58 and lowers local gradient and high-frequency measures, consistent with detail suppression rather than a color repair. The additional appearance-pathway and P0 checks do not identify the full cause or validate a repair. These selected cases do not estimate prevalence, texture fidelity, or baked 3D/PBR quality.

**Location.** Main manuscript: Figure 5 (p. 9), color results/Table 7 (p. 11), Figure 6 (p. 12), Figure 7 (p. 13), Limitations (p. 15). Supplement: Figure S1 (p. 12), S6–S8 (pp. 12–13), S13/Table S18 (p. 16), and figure attribution/provenance in Table S1 (pp. 1–2).

### Comment 2 — “Please evaluate the main adapter and relevant baselines under the same held-out protocol.”

**Response.** Fresh C evaluates the current adapter on 300 frozen object IDs disjoint from both the earlier 24-object schedule-development probe and the original 300-object evaluation. The primary run and same-cohort addendum share the checkpoint, runner, inputs, target views, metrics, and per-object seed policy; the integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The registered C3−GFL FG-PSNR difference is +0.522352 dB (95% object-bootstrap CI [+0.404160, +0.640669]).

We report the counter-results alongside it: GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. C3 and GFL also differ in applied deep/middle scale sums (82.5 versus 62.5), so this is not a timing-only comparison. Fresh C is a controlled retraining, not the historical 01549 checkpoint or a numerical reproduction of its +0.96 dB estimate. The older strict-276 and Core-7 analyses remain separately labeled retrospective diagnostics; neither replaces this matched current-adapter comparison.

**Location.** Main manuscript: Methods (pp. 3–5), Tables 3–4 (p. 8), stage placement (pp. 10–11), Limitations (p. 15). Supplement: S2 (p. 2), S3 (pp. 3–5), S4–S5 (pp. 6–11), S8 (p. 13), and S9 (p. 13).

### Comment 3 — “Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”

**Response.** We agree that larger gradients, RGB variation, or Laplacian variance do not establish faithful texture reproduction. The revision defines these as variation diagnostics and does not use them as fidelity endpoints. Fresh C reports image-space agreement, not validated texture fidelity. The 01549 3AFC study is retained only as a subjective preference result for its original conditions. The retrospective texture-complexity analysis in Supplement S12 is noncausal and is not used as a fidelity measure, schedule selector, or result for C3.

**Location.** Main: metrics (p. 3); Figures 4–7 (pp. 8–13); Table 9 (p. 14); Limitations (p. 15). Supplement: S2 (p. 2), S7 (p. 12), S12 (p. 15).

### Comment 4 — “A confidence interval crossing zero for the FG-SSIM difference does not establish equivalence or non-inferiority.”

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. Table 4 reports paired Fresh C intervals. C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084,−0.01683]), which we describe as an endpoint trade-off. No non-inferiority margin was prespecified, and we make no equivalence or non-inferiority claim. The historical 0.529-versus-0.559 values are not presented as a replicated Fresh C comparison.

**Location.** Main manuscript: Table 4 and endpoint interpretation (p. 8). Supplement: Section S2 (p. 2).

### Comment 5 — “It is still hard to reproduce the FAC experiments. The code is encouraged to be released.”

**Response.** We retain the seven-configuration FAC negative re-examination and separate untrained control as results reported in the first-round 01549 revision, not as new 1008 experiments. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained 12-object control reported ΔFG-PSNR −0.18 dB (95% CI [−0.42, +0.05]). We disclose that the recovered configuration references a 1,200-object list rather than the reported 1,706-object pool, and that no run-bound manifest links the training seed, outputs, and runtime. We make no claim of a full replay or public code release.

**Location.** Main manuscript: FAC discussion and Limitations (p. 15). Supplement: S11/Table S16 (p. 14).

## Reviewer 2

### Concern 1 — “The core methodological contribution remains quite limited.”

**Response.** We agree that timestep- or layer-dependent scheduling is not new by itself. The revision states this directly and positions TCAS as a graphics-task-specific intervention on the existing GeoTex-Adapter residual path. Its contribution is the operational distinction between requested scale, scale after native caps, and the resulting residual correction, together with paired measurements of fixed and scheduled controls on multi-view texture outputs.

Fresh C favors C3 over GFL on registered FG-PSNR, but GFH and Generic Linear have stronger means on all four displayed endpoints; C3/GFL also differ in applied deep/middle sums. Post-inspection strict-276 favors L–L–H, but its layer-wise correction summaries are unmatched. We claim neither C3 optimality nor a timing-only effect. SSI prior art is acknowledged; training-free implementation is not offered as the sole novelty argument. Novelty sufficiency remains an editorial judgment.

Re-audit showed that the A3b support calculation and probe-24 calibration used raw $L_2$ across feature maps of different spatial size; channel counts were not logged. We withdraw their cross-layer support and equal-dose/imbalance interpretations. The fixed A3b values remain as tested settings. Supplementary S3 states this limit; S4 reports per-entry magnitudes descriptively. A3b supports response heterogeneity under those settings, not an equal-dose or dose-independent effect.

**Location.** Main manuscript: Introduction/Related Work (pp. 1–2), TCAS Method (pp. 3–5), Tables 3–4 (p. 8), Tables 5–7 (p. 11), Tables 8–9 (p. 14), stage analysis (pp. 10–11), Limitations/Conclusion (p. 15). Supplement: S3 (pp. 3–5), S4–S5 (pp. 6–11), S9/Table S14 (p. 13), and S12 (p. 15).

### Concern 2 — “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”

**Response.** We agree that the CAI proposition and proof formalized an empirically selected profile rather than deriving it independently. We remove the selector, proposition, proof, and optimality claim. TCAS's residual-injection equation, three-stage profile, C3 definition, and 24-object development record remain, labeled as historical development evidence rather than a verified ranking or unique optimum.

**Location.** Main manuscript: TCAS Method (pp. 3–5), development Table 2 (p. 7), Figure 4 (p. 8). Supplement: S10/Table S15 (p. 14).

### Concern 3 — “Cross-backbone generalization remains the most important missing experiment.”

**Response.** We withdraw the invalid 98/99-probe interaction bootstrap. An exploratory object-cluster Wald reanalysis detected no Holm-adjusted interaction across four metrics (adjusted $p=0.156$–$0.868$); non-detection is not equivalence. The retrospective 76-object MV-Adapter panel scales condition-guider features rather than GeoTex residual corrections. Its endpoint results are mixed, and each temporal contrast has only one of six unadjusted intervals excluding zero.

We rechecked all 525 rows and reproduced the 30 archived MVDiffusion means and intervals as raw A-minus-B; the run generated 12 views and scored six per object. L--LLH minus G--FL CIEDE2000 is $+1.373021$ (95\% CI [$+0.418244,+2.374678$]), indicating higher color error; the archived $-1.373$ was improvement-coded. PSNR, FG-SSIM, and Edge-SSIM are lower, while FG-LPIPS is not separated. Among P5’s six endpoints, only FG-LPIPS has an interval that excludes zero, favoring G--LLH; all 30 intervals are pointwise and unadjusted. This compatibility-base panel was not rerun on the native mirror; its separate check covered one object. Table S12 gives the complete results. Neither auxiliary panel establishes matched cross-backbone transfer.

**Location.** Main: Cross-Interface Evaluation/Table 8 (pp. 13–14) and Limitations (p. 15). Supplement: S5 (pp. 6–11) and Tables S10–S12 (pp. 10–11).
