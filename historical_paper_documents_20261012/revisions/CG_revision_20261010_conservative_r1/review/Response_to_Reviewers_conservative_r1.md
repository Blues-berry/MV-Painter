# Response to Reviewers — conservative_r1

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The Reviewer 1–3 comments below are the subsequent review of that revision for CAG-D-26-00962. The preserved export labels its reviewer headers “Initial submission”; the author-confirmed round map identifies this packet as the second round. The headings quote the supplied review text. We retain relevant 01549 work, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision keeps Timestep-Conditioned Adapter Scaling (TCAS) as the method and narrows its claims to the evidence available. We now add the complete 300-object matrix with four equal-applied-budget stage controls and two separate strength controls, describe full-object figures and stronger fixed/linear controls, correct the stage-placement result, distinguish applied scale from residual magnitude, and replace an invalid interaction-bootstrap inference with the available exploratory object-cluster robust Wald analysis. We additionally complete a frozen fifty-object native MV-Adapter comparison and a calibrated ten-object unseen-view bake pilot, retaining endpoint losses and the non-separated second-interface primary. We also thank Reviewer 3 for the positive assessment; no additional technical change was requested.

## Summary of changes and remaining scope

| Request | Evidence and change | Remaining boundary |
|---|---|---|
| R1.1 Practical quality | Complete-object figures, GT-256 projection control, unseen-view bake pilot and actual-output video | True unset-scale GeoTex output, validated seams/PBR and usable appearance improvement are not supplied |
| R1.2 Holdout comparison | Input-disjoint Fresh C with paired strong baselines | Retrained checkpoint; the original main-adapter +0.96 dB estimate is not directly confirmed |
| R1.3–1.4 Interpretation/statistics | Variation separated from fidelity; paired intervals and endpoint losses reported | No equivalence, non-inferiority or perceptible-gain claim |
| R1.5 FAC reproduction | Executed inference/statistics materials and historical negative results retained | Missing FAC manifests and weights prevent full replay |
| R2.1 Contribution | Controlled equal-budget allocation, calibrated bake endpoints and native second-interface evidence | An empirical system study; no new general scheduling algorithm |
| R2.2 CAI | Independent derivation, proof and optimality removed | C3 remains a historically selected profile |
| R2.3 Second backbone | Fifty-object native MV-Adapter matrix, valid cameras and full contrasts | Different scaling interface; the primary gain is not separated |

The main text now prioritizes the scientific question, three principal evidence sets and practical interpretation. Detailed checkpoint/recovery and appearance-diagnostic limits are consolidated in Supplementary Section S19. This is a presentation change; cohort membership, frozen conditions, statistics and effective negative results are preserved.

## Reviewer 1

### Comment 1 — “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance.”

**Response.** We agree that the submitted panels did not establish appearance across complete objects or after texture projection. Figure 5 now pairs fixed-scale and Generic Linear comparisons with a shared target view and pixel ROI; Figure 7 shows shared full-object frames for favorable and adverse C3–GFL cases. Figure 8 adds actual full-object source and unseen-bake views, including the retained Tire color failure. Supplementary Figures S2–S8 show source/GT and every condition for seven rights-cleared objects; all ten enter metrics. The 22-second video presents actual discrete unseen-camera outputs without interpolated images. Figure 6 is a rights-cleared, hash-traced Fresh C example that was not selected for color; it is not a reconstruction of the two unmapped legacy pink-shift cases. Supplementary Figure S1 retains one six-view, seven-condition adverse Boat panel. We have shortened figure-internal labels and moved selection, camera and interpretation details into captions. The new native MV-Adapter illustration is Figure 9; the bake main figure focuses on Source/GT/Fixed Mean/Late-high, while each rights-cleared bake object has a balanced full-condition supplementary matrix. Figure S9 supplies every native MV-Adapter control.

Fresh C's No Adapter condition suppresses adapter correction; it is not the unset-scale native-default path. The initial 24-object Fresh C bake failed its native-input gate. The earlier five-object bake has been rerun after correcting pole-mask orientation, REPEAT interpolation and scalar-alpha decoding; the superseded estimates are not used. Its corrected descriptive C3–GFH PSNR difference is +2.37 dB with lower SSIM. Separately, a newly frozen ten-object pilot evaluates all seven controls on eleven unseen cameras per object, with matched GT-256 resolution, source masks, atlas coverage and bake/render parameters. Late-high–Fixed Mean FG-LPIPS is −0.00265 (95% object-bootstrap CI [−0.00414,−0.00137], exact paired sign-flip p=0.00195; 10/10 favorable). C3–GFH PSNR is +0.19 dB with an interval crossing zero; C3 SSIM is lower (four-test Holm p=0.00781). We do not pool old five, historical N=20 or new ten. Only ten of 300 screened inputs passed the frozen technical criteria, below the target twenty: this remains a compatibility-selected pilot. The unset-scale GeoTex default has not been generated in this comparison: Constant 1.0 (capped) and No Adapter do not meet that part of the unmodified-pipeline request. Broad brown-pattern appearance failures persist across several displayed objects, so the small relative LPIPS result is not claimed as usable texture recovery. The new source-traced video is locally playback-validated; prior reviewer-side access cannot be reconstructed.

The paired, failure-enriched 26-object color diagnosis shows that GFL reduces mean foreground CIEDE2000 relative to No Adapter by 19.65 (95% CI [−26.37, −13.25]; 24/26 objects), while pink/purple shifts remain in two legacy cases. LLH−GFL increases CIEDE2000 by 3.58 and lowers local gradient and high-frequency measures, consistent with detail suppression rather than a color repair. The additional appearance-pathway and P0 checks do not identify the full cause or validate a repair. These selected cases do not estimate prevalence, texture fidelity, or baked 3D/PBR quality.

**Location.** Main manuscript: Figures 5–8, color Table 9, bake Table 10, Limitations. Supplement: Figures S1–S9, Sections S6–S8, S13/Table S18, S18 and attribution/provenance in Table S1 and the new bake credit CSV.

### Comment 2 — “Please evaluate the main adapter and relevant baselines under the same held-out protocol.”

**Response.** Fresh C evaluates the current adapter on 300 frozen object IDs disjoint from both the earlier 24-object schedule-development probe and the original 300-object evaluation. The primary run and same-cohort addendum share the checkpoint, runner, inputs, target views, metrics, and per-object seed policy; the integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The registered C3−GFL FG-PSNR difference is +0.52 dB (95% object-bootstrap CI [+0.40, +0.64]).

We report the counter-results alongside it: GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. C3 and GFL also differ in applied deep/middle scale sums (82.5 versus 62.5), so this is not a timing-only comparison. Fresh C is a controlled retraining, not the historical 01549 checkpoint or a numerical reproduction of its +0.96 dB estimate. The older strict-276 and Core-7 analyses remain separately labeled retrospective diagnostics; neither replaces this matched current-adapter comparison.

**Location.** Main manuscript: Methods, Tables 4–5, stage placement, Limitations. Supplement: S2, S3, S4–S5, S8, and S9.

### Comment 3 — “Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”

**Response.** We agree that larger gradients, RGB variation, or Laplacian variance do not establish faithful texture reproduction. The revision defines these as variation diagnostics and does not use them as fidelity endpoints. Fresh C reports image-space agreement, not validated texture fidelity. The 01549 3AFC study is retained only as a subjective preference result for its original conditions. The retrospective texture-complexity analysis in Supplement S12 is noncausal and is not used as a fidelity measure, schedule selector, or result for C3.

**Location.** Main: metrics; Figures 4–8; preference Table 13; Limitations. Supplement: S2, S7, S12, S18.

### Comment 4 — “A confidence interval crossing zero for the FG-SSIM difference does not establish equivalence or non-inferiority.”

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. Table 5 reports paired Fresh C intervals. C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084,−0.01683]), which we describe as an endpoint trade-off. No non-inferiority margin was prespecified, and we make no equivalence or non-inferiority claim. The historical 0.529-versus-0.559 values are not presented as a replicated Fresh C comparison.

**Location.** Main manuscript: Table 5 and endpoint interpretation. Supplement: Section S2.

### Comment 5 — “It is still hard to reproduce the FAC experiments. The code is encouraged to be released.”

**Response.** We retain the seven-configuration FAC negative re-examination and separate untrained control as results reported in the first-round 01549 revision, not as new 1008 experiments. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained 12-object control reported ΔFG-PSNR −0.18 dB (95% CI [−0.42, +0.05]). We disclose that the recovered configuration references a 1,200-object list rather than the reported 1,706-object pool, and that no run-bound manifest links the training seed, outputs, and runtime. The delivered reproduction archive includes the actually executed inference and evaluation scripts, frozen configuration and identity records, and a standalone object-paired statistics workflow. It does not supply missing FAC training manifests or weights; we make no claim of a full FAC replay or public code release.

**Location.** Main manuscript: FAC discussion and Limitations. Supplement: S11/Table S16.

## Reviewer 2

### Concern 1 — “The core methodological contribution remains quite limited.”

**Response.** We agree that schedule selection for an existing adapter has limited algorithmic novelty. ControlNet/T2I-Adapter expose conditioning-strength controls; SSI already schedules layer and denoising axes and geometry-conditioned ControlNet strength. GeoTex in 01549 already supplied a fixed residual multiplier. TCAS reuses it for a three-stage request. Its bounded task-specific contribution is to measure requested values, native-cap applied values, activation-dependent residual corrections, and paired multi-view outcomes. It adds no learned branch or selector; scale values are not common doses across interfaces.

Fresh C favors C3 over GFL on registered FG-PSNR, while GFH and Generic Linear have stronger means on all four endpoints; C3/GFL applied deep/middle sums also differ. The matched 300-object addendum (four equal-budget allocation controls plus two separate strength controls) favors Late-high over C3 by 0.56 dB FG-PSNR, and Fixed Mean over C3 by 0.13 dB; both also favor the alternatives on FG-LPIPS, FG-SSIM and Edge-SSIM. C3 wins FG-PSNR on none of the 300 objects among these six controls. This same-cohort post-inspection comparison measures the total effect of stage allocation, while state-dependent residual amplitudes limit mechanism attribution. The older strict-276 study remains separate. We claim neither C3 optimality nor a residual-dose-independent law. The evidence still does not establish a new general scheduling algorithm; Its scientific case is the measured response of this graphics system under strong controls, including the falsification of the historical middle-window preference and the limits of image metrics for interpreting baked appearance.

The new ten-object bake pilot adds a small relative baked-image result rather than a new algorithm: Late-high–Fixed Mean unseen LPIPS is −0.00265, favorable on ten of ten, with C3–GFH PSNR not stably positive and C3 SSIM lower. The fifty-object native MV-Adapter primary is also not separated. Across seven controls, mean image/bake rank correlations are positive; the LPIPS winning condition changes in seven objects. Thus we do not claim a general ranking reversal. The revised contributions focus on controlled task-specific evidence, a small relative baked-image finding and interface limits, with reproducibility supporting the conclusions. Late-high is not renamed C3, and no deployable selector is inferred from an oracle upper bound.

Because A3b's support calculation and probe-24 calibration compare raw $L_2$ across feature maps of different spatial dimensions (with channel counts unlogged), we withdraw cross-layer support and equal-dose interpretations. Values remain tested settings; S4's per-entry magnitudes are descriptive. A3b supports response heterogeneity under these settings, not a dose-independent effect.

**Location.** Main: Introduction/Related Work, Method, results, Limitations. Supplement: S3–S5, S9/Table S14, S12.

### Concern 2 — “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”

**Response.** We agree that the CAI proposition and proof formalized an empirically selected profile rather than deriving it independently. We remove the selector, proposition, proof, and optimality claim. TCAS's residual-injection equation, three-stage profile, C3 definition, and 24-object development record remain, labeled as historical development evidence rather than a verified ranking or unique optimum.

**Location.** Main manuscript: TCAS Method, development Table 3, Figure 4. Supplement: S10/Table S15.

### Concern 3 — “Cross-backbone generalization remains the most important missing experiment.”

**Response.** We withdraw the invalid 98/99-probe interaction bootstrap. The subsequent seven-object native temporal archive passed output-path identity but used target cameras and mesh normalization inconsistent with the native pipeline. Its old quality estimates are therefore not active cross-backbone evidence. Native identity and quality-evaluation validity are separate checks. We disclose this calibration failure in Supplement S16. An exploratory object-cluster Wald reanalysis detected no Holm-adjusted interaction across four metrics (adjusted $p=0.156$–$0.868$); non-detection is not equivalence. The 76-object MV-Adapter panel scales condition-guider features before UNet down-block residual injection. MVDiffusion instead interpolates CPBlock outputs; its depth condition is concatenated into the latent and left unscaled. Neither intervention reproduces the GeoTex per-ResNet residual correction. The MV-Adapter endpoint results are mixed, and each temporal contrast has only one of six unadjusted intervals excluding zero.

We now add fifty objects with previously uninspected MV-Adapter outputs, selected in fixed UID order by inputs only after excluding all recorded prior MV-Adapter objects. The seven frozen conditions share input, seed and native-camera evaluation. Actual official/deployed and constant-1 paths match RGB pixels, condition features and injected residuals on three textured new objects. The complete matrix has 350 rows. Low/high are 0.75/1.0, stage-high segments have sixteen steps and Fixed Mean is 0.83; mean-matched controls sum to 41.5 per feature. Thirteen texture-absent source assets retain white-albedo targets in the primary fifty; the textured 37-object subset is descriptive. This is an internal protocol freeze, not public preregistration.

The primary Middle-high–Fixed Mean FG-PSNR is +0.029 dB (95% object-bootstrap CI [−0.019,+0.081], 100,000-draw paired sign-flip p=0.281; 29/50 favorable). The other 104 tests are Holm-adjusted together and all are reported in S17. There are endpoint-specific differences, including lower Middle-high Edge-SSIM than Fixed Mean; neither a universal middle-window advantage nor equivalence is supported. This supplies valid second-interface evidence, but the feature-scaled MV-Adapter intervention is not architecture-matched GeoTex residual transfer.

Audit of 525 rows reproduced all 30 raw A−B contrasts (12 views generated; six scored). In P1 (L–LLH−G–FL), PSNR −0.453828, FG-SSIM −0.019393, and Edge-SSIM −0.005941 favor G–FL (higher is better); FG-LPIPS +0.002745 is not separated. CIEDE2000 +1.373021 (95\% CI [+0.418244,+2.374678]) means worse color error under L–LLH; archived −1.373 was improvement-coded. GT-relative texture error −0.082286 means closer to recorded variation statistics, not greater fidelity. In P5, only FG-LPIPS excludes zero, favoring G–LLH. All intervals are pointwise and unadjusted. The compatibility-base panel was not rerun on the native mirror; its separate check covered one object. Table S12 gives all contrasts. These probes do not establish matched transfer.

**Location.** Main: Cross-Interface Evaluation, Tables 11–12 and Figure 9, Limitations; Supplement S5, S16–S17 and the complete native fifty-object contrast table. The separate bake evidence is Table 10/Figure 8, Supplement S18.

## Conservative iteration 1

This iteration clarifies the temporal C3 request and the distinction between four equal-budget allocation controls and the two strength baselines. The abstract now reports the limited prespecified C3–Fixed Low gain alongside all strong-baseline counterevidence. It does not recover the original main-checkpoint estimate or promote the same-cohort addendum to an independent holdout. No new inference, training, object selection or statistical family is introduced.

## Delivery and consistency checks

The local author-review package includes clean and marked manuscripts, Supplement, response, actual-output video, source archive and a separate weights-free reproduction archive. Object is the statistical unit; intervals are pointwise, and primary/secondary families are named explicitly. Native GeoTex's unset scale and an explicit capped 1.0 request are not equivalent; all new bake labels use Constant 1.0 (capped). No additional eighth condition is introduced. Figure 1 is now a reproducible vector schematic with separate reference and geometry paths; manuscript/code assistance is disclosed; the schematic contains no experimental thumbnails, and new experiment figures are unretouched actual renders. Source hash/configuration details are concentrated in the Supplement/reproduction archive. Author metadata and carried-forward administrative declarations remain subject to author review before submission; no journal upload has been made.
