# Response to Reviewers — 1008 second-round revision

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The Reviewer 1–3 comments below are the subsequent review of that revision for CAG-D-26-00962. The preserved export labels its reviewer headers “Initial submission”; the author-confirmed round map identifies this packet as the second round. The headings quote the supplied review text. We retain relevant 01549 work, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision keeps Timestep-Conditioned Adapter Scaling (TCAS) as the method and narrows its claims to the evidence available. We now add the complete matched 300-object equal-applied-budget stage comparison, describe full-object figures and stronger fixed/linear controls, correct the stage-placement result, distinguish applied scale from residual magnitude, and replace an invalid interaction-bootstrap inference with the available exploratory object-cluster robust Wald analysis. We additionally complete a frozen fifty-object native MV-Adapter comparison and a calibrated ten-object unseen-view bake pilot, retaining endpoint losses and the non-separated second-interface primary. The second iteration also adds actual native-wrapper controls, a matched GT reference-gap context, and an explicit audit of sampling-protocol differences; details are given in the iteration addenda below. We also thank Reviewer 3 for the positive assessment; no additional technical change was requested.

## Reviewer 1

### Comment 1 — “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance.”

**Response.** We agree that the submitted panels did not establish appearance across complete objects or after texture projection. Figure 5 now pairs fixed-scale and Generic Linear comparisons with a shared target view and ROI; Figure 7 shows full-object context and the same ROI for favorable and adverse C3–GFL cases. Figure 8 adds actual full-object source and unseen-bake views, including the retained Tire color failure. Supplementary Figure S2 shows source/GT and every condition for seven rights-cleared objects; all ten enter metrics. The 22-second video presents actual discrete unseen-camera outputs without interpolated images. Figure 6 is a rights-cleared, hash-traced Fresh C example that was not selected for color; it is not a reconstruction of the two unmapped legacy pink-shift cases. Supplementary Figure S1 retains the six-view, seven-condition panel.

Fresh C's No Adapter condition suppresses adapter correction; it is not the unset-scale native-default path. The initial 24-object Fresh C bake failed its native-input gate. The earlier five-object bake has been rerun after correcting pole-mask orientation, REPEAT interpolation and scalar-alpha decoding; the superseded estimates are not used. Its corrected descriptive C3–GFH PSNR difference is +2.37 dB with lower SSIM. Separately, a newly frozen ten-object pilot evaluates all seven controls on eleven unseen cameras per object, with matched GT-256 resolution, source masks, atlas coverage and bake/render parameters. Late-high–Fixed Mean FG-LPIPS is −0.00265 (95% object-bootstrap CI [−0.00414,−0.00137], exact paired sign-flip p=0.00195; 10/10 favorable). C3–GFH PSNR is +0.19 dB with an interval crossing zero; C3 SSIM is lower (four-test Holm p=0.00781). We do not pool old five, historical N=20 or new ten. Only ten of 300 screened inputs passed the frozen technical criteria, below the target twenty: this remains a compatibility-selected pilot. The new source-traced video is locally playback-validated; prior reviewer-side access cannot be reconstructed.

The paired, failure-enriched 26-object color diagnosis shows that GFL reduces mean foreground CIEDE2000 relative to No Adapter by 19.65 (95% CI [−26.37, −13.25]; 24/26 objects), while pink/purple shifts remain in two legacy cases. LLH−GFL increases CIEDE2000 by 3.58 and lowers local gradient and high-frequency measures, consistent with detail suppression rather than a color repair. The additional appearance-pathway and P0 checks do not identify the full cause or validate a repair. These selected cases do not estimate prevalence, texture fidelity, or baked 3D/PBR quality.

**Location.** Main manuscript: Figures 5–8, color Table 8, bake Table 9, Limitations. Supplement: Figures S1–S2, S6–S8, S13/Table S18, S18 and attribution/provenance in Table S1 and the new bake credit CSV.

### Comment 2 — “Please evaluate the main adapter and relevant baselines under the same held-out protocol.”

**Response.** Fresh C evaluates the current adapter on 300 frozen object IDs disjoint from both the earlier 24-object schedule-development probe and the original 300-object evaluation. The primary run and same-cohort addendum share the checkpoint, runner, inputs, target views, metrics, and per-object seed policy; the integrity gates pass for 1,200/1,200 primary rows and 600/600 addendum rows. The registered C3−GFL FG-PSNR difference is +0.52 dB (95% object-bootstrap CI [+0.40, +0.64]).

We report the counter-results alongside it: GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. C3 and GFL also differ in applied deep/middle scale sums (82.5 versus 62.5), so this is not a timing-only comparison. Fresh C is a controlled retraining, not the historical 01549 checkpoint or a numerical reproduction of its +0.96 dB estimate. The older strict-276 and Core-7 analyses remain separately labeled retrospective diagnostics; neither replaces this matched current-adapter comparison.

**Location.** Main manuscript: Methods, Tables 3–4, stage placement, Limitations. Supplement: S2, S3, S4–S5, S8, and S9.

### Comment 3 — “Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”

**Response.** We agree that larger gradients, RGB variation, or Laplacian variance do not establish faithful texture reproduction. The revision defines these as variation diagnostics and does not use them as fidelity endpoints. Fresh C reports image-space agreement, not validated texture fidelity. The 01549 3AFC study is retained only as a subjective preference result for its original conditions. The retrospective texture-complexity analysis in Supplement S12 is noncausal and is not used as a fidelity measure, schedule selector, or result for C3.

**Location.** Main: metrics; Figures 4–8; preference Table 12; Limitations. Supplement: S2, S7, S12, S18.

### Comment 4 — “A confidence interval crossing zero for the FG-SSIM difference does not establish equivalence or non-inferiority.”

**Response.** We agree that an interval crossing zero does not establish equivalence or non-inferiority. Table 4 reports paired Fresh C intervals. C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084,−0.01683]), which we describe as an endpoint trade-off. No non-inferiority margin was prespecified, and we make no equivalence or non-inferiority claim. The historical 0.529-versus-0.559 values are not presented as a replicated Fresh C comparison.

**Location.** Main manuscript: Table 4 and endpoint interpretation. Supplement: Section S2.

### Comment 5 — “It is still hard to reproduce the FAC experiments. The code is encouraged to be released.”

**Response.** We retain the seven-configuration FAC negative re-examination and separate untrained control as results reported in the first-round 01549 revision, not as new 1008 experiments. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained 12-object control reported ΔFG-PSNR −0.18 dB (95% CI [−0.42, +0.05]). We disclose that the recovered configuration references a 1,200-object list rather than the reported 1,706-object pool, and that no run-bound manifest links the training seed, outputs, and runtime. The delivered reproduction archive includes the actually executed inference and evaluation scripts, frozen configuration and identity records, and a standalone object-paired statistics workflow. It does not supply missing FAC training manifests or weights; we make no claim of a full FAC replay or public code release.

**Location.** Main manuscript: FAC discussion and Limitations. Supplement: S11/Table S16.

## Reviewer 2

### Concern 1 — “The core methodological contribution remains quite limited.”

**Response.** We agree that schedule selection for an existing adapter has limited algorithmic novelty. ControlNet/T2I-Adapter expose conditioning-strength controls; SSI already schedules layer and denoising axes and geometry-conditioned ControlNet strength. GeoTex in 01549 already supplied a fixed residual multiplier. TCAS reuses it for a three-stage request. Its bounded task-specific contribution is to measure requested values, native-cap applied values, activation-dependent residual corrections, and paired multi-view outcomes. It adds no learned branch or selector; scale values are not common doses across interfaces.

Fresh C favors C3 over GFL on registered FG-PSNR, while GFH and Generic Linear have stronger means on all four endpoints; C3/GFL applied deep/middle sums also differ. The fully matched 300-object equal-applied-budget addendum favors Late-high over C3 by 0.56 dB FG-PSNR, and Fixed Mean over C3 by 0.13 dB; both also favor the alternatives on FG-LPIPS, FG-SSIM and Edge-SSIM. C3 wins FG-PSNR on none of the 300 objects among these six controls. This same-cohort post-inspection comparison measures the total effect of stage allocation, while state-dependent residual amplitudes limit mechanism attribution. The older strict-276 study remains separate. We claim neither C3 optimality nor a residual-dose-independent law. The evidence still does not establish a new general scheduling algorithm; novelty sufficiency remains an editorial judgment.

The new ten-object bake pilot adds a bounded deployment result rather than a new algorithm: Late-high–Fixed Mean unseen LPIPS is −0.00265, favorable on ten of ten, with C3–GFH PSNR not stably positive and C3 SSIM lower. The fifty-object native MV-Adapter primary is also not separated. Across seven controls, mean image/bake rank correlations are positive; the LPIPS winning condition changes in seven objects. Thus we do not claim a general ranking reversal. The revised contributions focus on controlled task-specific evidence, a limited named deployment candidate and interface limits, with reproducibility supporting the conclusions. Late-high is not renamed C3, and no deployable selector is inferred from an oracle upper bound.

Because A3b's support calculation and probe-24 calibration compare raw $L_2$ across feature maps of different spatial dimensions (with channel counts unlogged), we withdraw cross-layer support and equal-dose interpretations. Values remain tested settings; S4's per-entry magnitudes are descriptive. A3b supports response heterogeneity under these settings, not a dose-independent effect.

**Location.** Main: Introduction/Related Work, Method, results, Limitations. Supplement: S3–S5, S9/Table S14, S12.

### Concern 2 — “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”

**Response.** We agree that the CAI proposition and proof formalized an empirically selected profile rather than deriving it independently. We remove the selector, proposition, proof, and optimality claim. TCAS's residual-injection equation, three-stage profile, C3 definition, and 24-object development record remain, labeled as historical development evidence rather than a verified ranking or unique optimum.

**Location.** Main manuscript: TCAS Method, development Table 2, Figure 4. Supplement: S10/Table S15.

### Concern 3 — “Cross-backbone generalization remains the most important missing experiment.”

**Response.** We withdraw the invalid 98/99-probe interaction bootstrap. The subsequent seven-object native temporal archive passed output-path identity but used target cameras and mesh normalization inconsistent with the native pipeline. Its old quality estimates are therefore not active cross-backbone evidence. Native identity and quality-evaluation validity are separate checks. We disclose this calibration failure in Supplement S16. An exploratory object-cluster Wald reanalysis detected no Holm-adjusted interaction across four metrics (adjusted $p=0.156$–$0.868$); non-detection is not equivalence. The 76-object MV-Adapter panel scales condition-guider features before UNet down-block residual injection. MVDiffusion instead interpolates CPBlock outputs; its depth condition is concatenated into the latent and left unscaled. Neither intervention reproduces the GeoTex per-ResNet residual correction. The MV-Adapter endpoint results are mixed, and each temporal contrast has only one of six unadjusted intervals excluding zero.

We now add fifty objects with previously uninspected MV-Adapter outputs, selected in fixed UID order by inputs only after excluding all recorded prior MV-Adapter objects. The seven frozen conditions share input, seed and native-camera evaluation. Actual official/deployed and constant-1 paths match RGB pixels, condition features and injected residuals on three textured new objects. The complete matrix has 350 rows. Low/high are 0.75/1.0, stage-high segments have sixteen steps and Fixed Mean is 0.83; mean-matched controls sum to 41.5 per feature. Thirteen texture-absent source assets retain white-albedo targets in the primary fifty; the textured 37-object subset is descriptive. This is an internal protocol freeze, not public preregistration.

The primary Middle-high–Fixed Mean FG-PSNR is +0.029 dB (95% object-bootstrap CI [−0.019,+0.081], 100,000-draw paired sign-flip p=0.281; 29/50 favorable). The other 104 tests are Holm-adjusted together and all are reported in S17. There are endpoint-specific differences, including lower Middle-high Edge-SSIM than Fixed Mean; neither a universal middle-window advantage nor equivalence is supported. This supplies valid second-interface evidence, but the feature-scaled MV-Adapter intervention is not architecture-matched GeoTex residual transfer.

Audit of 525 rows reproduced all 30 raw A−B contrasts (12 views generated; six scored). In P1 (L–LLH−G–FL), PSNR −0.453828, FG-SSIM −0.019393, and Edge-SSIM −0.005941 favor G–FL (higher is better); FG-LPIPS +0.002745 is not separated. CIEDE2000 +1.373021 (95\% CI [+0.418244,+2.374678]) means worse color error under L–LLH; archived −1.373 was improvement-coded. GT-relative texture error −0.082286 means closer to recorded variation statistics, not greater fidelity. In P5, only FG-LPIPS excludes zero, favoring G–LLH. All intervals are pointwise and unadjusted. The compatibility-base panel was not rerun on the native mirror; its separate check covered one object. Table S12 gives all contrasts. These probes do not establish matched transfer.

**Location.** Main: Cross-Interface Evaluation, Tables 10–11, Limitations; Supplement S5, S16–S17 and the complete native fifty-object contrast table. The separate bake evidence is Table 9/Figure 8, Supplement S18.

## Delivery and consistency checks

The local author-review package includes clean and marked manuscripts, Supplement, response, actual-output video, source archive and a separate weights-free reproduction archive. Object is the statistical unit; intervals are pointwise, and primary/secondary families are named explicitly. Native GeoTex's unset scale and an explicit capped 1.0 request are not equivalent; all new bake labels use Constant 1.0 (capped). The second iteration adds native-unset and No Adapter controls on the same ten previously inspected bake objects, with a separate exploratory 15-test family; it does not alter the original seven-condition primary. The main Figure 1 conceptual artwork and manuscript/code assistance are disclosed; its research thumbnails are actual rights-cleared outputs, and new experiment figures are unretouched actual renders. Source hash/configuration details are concentrated in the Supplement/reproduction archive. Author metadata and carried-forward administrative declarations remain subject to author review before submission; no journal upload has been made.


# Round 001 reviewer-response addendum

R1.1 — Practical appearance. The main pilot table now includes the measured GT-256 reference bake, with the same source resolution, masks and baking settings. Its mean FG-LPIPS is 0.0590, compared with 0.1303 for Fixed Mean and 0.1277 for Late-high. The named Late-high gain is stable in direction but small in context: a post hoc ratio of paired means is 3.7% of the Fixed Mean–GT reference gap (pointwise object-bootstrap CI 2.3–5.3%). The empirical reference is not a theoretical bound or a material-quality threshold. The substantial appearance failure remains visible. We do not infer acceptable PBR fidelity from the separated LPIPS contrast.

R1.4 — Uncertainty. The previous frozen primary and its interval are unchanged. The descriptive context resamples paired objects jointly; it is not added to the confirmatory test family. Leaving out each object keeps the mean difference negative, between −0.00294 and −0.00208, but does not supply new independent evidence or an equivalence test.

R2.1 — Contribution. This round improves the interpretation and evidence completeness; it does not add a new scheduling algorithm or claim to resolve novelty. No acceptance probability is inferred.


# Round 002 reviewer-response addendum

R1.1 — Default controls and practical appearance. We added the actual unset-scale GeoTex wrapper residual and No Adapter on the same ten previously inspected pilot objects. The regenerated capped 1.0 control reproduces all ten previous RGB outputs bitwise; new controls preserve mesh bytes, camera/mask settings and raw atlas coverage. Repeated GT endpoints match exactly. The native residual branch has unseen-view FG-PSNR 11.13 dB, FG-LPIPS 0.1372, FG-SSIM 0.3376 and CIEDE2000 26.47. No Adapter has 5.92 dB, 0.1600, 0.3829 and 40.92, respectively. All valid failures remain displayed in complete six-view grids.

These are controls inside the frozen 50-step sampling protocol, not a replay of the complete default pipeline. A read-only source audit establishes that the frozen loop uses 256-pixel views, cached image embeddings and conditional-only score predictions; the full pipeline defaults to 512-pixel views, online image embeddings and classifier-free guidance 2.0. The model validation call uses 75 steps and does not explicitly bind geometry features. We state this distinction in the methods and Supplement S20. It does not by itself identify the cause of poor appearance or validate a repair.

R1.4 — Complete statistics. The added analyses are explicitly post hoc, with three named comparisons on five endpoints in one 15-test Holm family. Late-high–native residual PSNR is +1.79 dB (pointwise 95% object-bootstrap CI +0.46 to +3.06), and LPIPS is −0.00951 (−0.01772 to −0.00263); the respective adjusted p values are both 0.297. C3–native residual has +1.35 dB and−0.00699, also adjusted p 0.297. None of the ten schedule contrasts separates after correction; only No Adapter–native residual Edge-SSIM does (−0.218; adjusted p 0.0293). The older primary, cohort, strong-baseline results and GT reference context remain unchanged. Non-rejection is not equivalence.

R2.1 — Contribution boundary and next decision. This round closes the capped/unset branch ambiguity within the tested sampling stack; it does not establish full-pipeline equivalence, a new algorithm or generally acceptable baked appearance. Complete default-path quality now has higher priority than another schedule search. Novelty remains a substantive limitation, and no acceptance probability is inferred.


# Round 003 reviewer-response addendum

R1.1 — Full-path quality diagnostic. We now execute the complete native base pipeline on the two previously displayed failure objects, without GeoTex, at 50 and 75 steps. All four calls complete; actual UNet calls and two-member CFG batches are logged, and paired initial latents match. Source correspondence is checked against the previous conditioning hashes. Complete grids retain visible imperfections, while their front-looking views preserve reference colors/details that were lost in the controlled generator.

The native API requires RGBA, and its preprocessing mutates some bright foreground pixels. The initial RGB attempt failed before generation and is retained. The valid rerun uses the same original single-reference RGBA sources. The native pipeline differs in resolution, feature computation, guidance and scheduler; camera equivalence is unverified. We therefore do not compute cross-protocol paired GT metrics or attribute the difference to one cause. These are two seen failure cases, not independent quality confirmation or complete GeoTex deployment validation.

R1.4 — Evidence scope. No inferential tests are added for the qualitative diagnostic. All prior paired results and their multiplicity families remain unchanged. The inverse image-scaling formulas are algebraically equivalent, so we do not claim a decoding bug from their names.

R2.1 — Priority and limitation. The low-cost diagnostic changes the next action: separate the sampling differences before attempting another schedule or developing a new algorithm. It does not establish algorithmic novelty, overall material fidelity or a calibrated acceptance probability.


# Round 004 reviewer-response addendum

R1.1 — Controlled failure diagnosis. We hold 256-pixel views, 50-step Euler sampling, conditioning RGB and the seed policy fixed, crossing cached/online global image features with conditional-only/sequential CFG2. All eight calls complete. The cached conditional-only control reproduces both previous No Adapter outputs bitwise; positive reference-noise RNG trajectories match across arms. Online-to-cache feature cosines are 0.863 and 0.899, but neither online features nor guided prediction restores the source appearance. Guided dark outputs contain fewer colored patterns, not a validated quality improvement. Every grid is retained in S22.

R1.4 — Intervention scope. CFG2 uses the standard 2εc−εu formula through sequential batch-one calls, with independent negative-branch randomness that leaves positive reference-noise states unchanged. This is a controlled diagnostic, not pixel-equivalence to the native batched API, independent confirmation, or a general fidelity benchmark. No new inferential family is created; previous paired results remain unchanged.

R2.1 — Priority. This round reports a useful negative diagnostic, not a new algorithm. It narrows the next test to resolution and other full-path differences; repeated feature replacement or further schedule search has lower priority. Earlier C1/B2 failures remain in the evidence record. Novelty and broad application quality remain unresolved; no 90% acceptance claim is made.


# Fifth-round response addendum

We retain the previous negative controls and add a target-resolution diagnostic on the same two seen cases. With online image features, 256-pixel reference encoding, frozen weights, training time IDs and 50-step Euler sampling fixed, we cross target-view resolution (256/512) with conditional-only/sequential CFG2 prediction. The 256 arms reproduce the previous online-feature RGB outputs bitwise; within each resolution initial latents and all fifty positive-branch RNG states match.

The larger target grids restore six-position arrangements in these examples, while appearance defects and repeated views remain. Six positions do not verify camera identities or overall fidelity. Initial tensors differ in size across resolutions; only their seed policy is shared. No cross-camera GT scores, inferential tests or geometry-adapter deployment claim is made. S23 preserves all eight complete outputs, source identities and credits. The earlier 256-pixel comparisons remain valid only within their stated protocol; this diagnostic strengthens the need for native-path and camera calibration before extending deployment claims. Novelty and independent practical quality remain unresolved.


# Sixth-round reviewer response addendum

We add a source-derived camera-contract audit and complete native-loop implementation checks. The official inference and bake permutations are inverses; actual metadata from all ten baking objects matches the nominal directions after conditioning-anchor rotation. This does not verify pole-image roll, pixel registration or generated-view correctness. Immutable official source snapshots and per-object records are provided.

Loading the frozen GeoTex weights while clearing geometry reproduces both prior bare-native base grids bitwise. The subsequent sixteen-call matrix keeps native512/CFG2/EulerAncestral inference fixed, with trained256 geometry encoding and the frozen historical schedules. Actual hooks confirm all nine reference-write skips/read corrections, common within-object inputs, features, initial latents and outer-call RNG states. Geometry broadcasts to both CFG branches; this branch policy and the unresolved encoding-resolution compatibility are explicit.

All real outputs are retained. Geometry-enabled remote outputs lose most reference content, and several tire outputs blur detail. These are seen-case negative findings, not a validated quality repair or independent deployment result. Historical C3 and scalar Fixed Mean do not share every layer budget in this native diagnostic; no matched-budget claim is made for that contrast. The failed pre-loading registry import is preserved separately. S24, the main text and abstract disclose the practical appearance limitation. Novelty and independent native-deployment quality remain unresolved.


# Seventh-round response addendum

We separate geometry-encoding size (256/512) and CFG correction policy (both, conditional-only, conditional-only half amplitude) in twelve seen-case native-loop calls. The256/both arm reproduces both preceding original-residual grids bitwise; every conditional-only correction records a zero negative branch. Inputs/noise match across arms and geometry features match within encoding size. Half-amplitude conditional correction retains more tire detail, but neither factor restores the remote reference content. All outputs and negative findings are retained in S25.

The recorded custom training entry uses conditional inputs throughout and does not read the conditioning-drop probability declared in its model configuration. This entry differs from the model-class training method. The audit also records256 training, historical repeated-top targets, checkpoint/list/source hashes and complete2,000-step loss rows. The1,118-object training list has no Fresh C UID overlap;1,112 have the six checked input sets. Missing seed/list-override records and the changed surviving dataset source prevent an exact-replay claim. These observations are not restoration of historical FAC or causal proof of the failure. Removing the unconditioned correction alone does not repair appearance. Protocol-consistent training checks now take priority over further schedule sweeps; independent native deployment benefits and novelty remain unresolved.
