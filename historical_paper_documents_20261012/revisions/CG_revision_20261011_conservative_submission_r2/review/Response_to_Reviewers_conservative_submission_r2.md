# Response to Reviewers

**Round framing.** The manuscript designated 01549 was submitted on 7 September 2026 after the first review round. The Reviewer 1–3 comments below are the subsequent review of that revision for CAG-D-26-00962. The preserved export labels its reviewer headers “Initial submission”; the author-confirmed round map identifies this packet as the second round. The headings quote the supplied review text. We retain relevant 01549 work, including the preference study, FAC re-examination, original 276-object analysis, and historical adapter results; none is presented as a new Fresh C result.

Dear Editor and Reviewers,

We thank you for the careful assessment. This revision retains TCAS and the historical C3 profile, and brings together the original preference study, a matched 300-object Fresh C evaluation with fixed and linear controls, calibrated unseen-view baking, and a native fifty-object MV-Adapter test. A separate post-submission follow-up on per-view guidance projection is documented in Supplementary Section S22 and kept distinct from the TCAS evidence. We report paired object-level results, show complete objects with shared local crops, and distinguish the primary composite endpoint from display-view diagnostics. We also thank Reviewer 3 for the positive assessment.

## Summary of changes and remaining scope

**R1.1, practical quality.** We add full-view comparisons with shared crops, a calibrated GT-256 bake control, a ten-object unseen-view pilot, and an actual-output video. The bake set is compatibility-selected; unset-scale GeoTex, validated seam quality, and PBR/relighting remain outside this evaluation.

**R1.2, held-out comparison.** Fresh C supplies a UID-disjoint paired study with fixed and linear controls. It uses a separately retrained checkpoint; the historical pooled result has no retained object-paired rows for a new interval.

**R1.3–1.4, interpretation and statistics.** We distinguish variation from fidelity and report paired intervals, including endpoint losses. No equivalence, non-inferiority, or perceptible-gain claim is made.

**R1.5, FAC reproducibility.** The package includes executable inference/statistics materials and retains the earlier reported negative results. Missing FAC training manifests and weights prevent full replay.

**R2.1, contribution.** We present TCAS as a task-specific control studied through matched image-space, preference, bake, and native-interface comparisons. Supplementary Section S22 separately reports a pre-specified 64-object source-view comparison for a different projection intervention. Its nonreference-view outcomes do not establish noninferiority, its APG development comparisons do not show a separated advantage, and it is not used as evidence for TCAS. We do not infer an architecture-general schedule law.

**R2.2–2.3, formulation and second interface.** The independent CAI derivation and optimality claim are removed. The native fifty-object MV-Adapter matrix supplies a distinct interface test, whose primary interval includes zero.

The main text now moves from the texturing problem and TCAS control to quantitative/preference evidence, then to baking and the native second-interface test. The Supplement separately records the new projection follow-up, including its full primary and development comparisons. Checkpoint history, earlier exploratory interface panels, recovery records and full statistics remain in the Supplement.

## Reviewer 1

### Comment 1 — “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance.”

**Response.** Figures 6 and 8 show complete Fresh C views with shared local crops. Figure 8 presents two rights-cleared examples selected from five previously illustrated objects under a fixed rule: C3 is favorable to Fixed Low on FG-PSNR, FG-LPIPS and FG-SSIM both on the frozen six-view composite and on displayed view 0. The caption gives the composite-level differences; view-level scores are a display check only. Figure 5 shows all 300 object-level differences and named paired comparisons. The six-view Boat panel is retained in Supplementary Figure S1 as a concrete counterexample.

Figure 9 presents source, GT-256 and generated unseen-camera bakes; Supplementary Figures S2–S8 show all seven generated conditions for each of seven rights-cleared objects, and the video contains recorded outputs. The ten-object pilot uses matched resolution, masks, coverage and bake/render settings. Its frozen Late-high–Fixed Mean FG-LPIPS difference is −0.00265 (95% object-bootstrap CI [−0.00414, −0.00137], exact paired sign-flip p=0.00195; 10/10 favorable). Figure 9 also shows the remaining source-to-output appearance differences. An unset-scale GeoTex output is not available in this bake set; No Adapter and capped Constant 1.0 are distinct controls. Calibration and sample eligibility are documented in Supplement S18.

A selected 26-object color diagnosis remains in the Supplement: GFL lowers CIEDE2000 relative to No Adapter by 19.65 (95% CI [−26.37, −13.25]; 24/26), while LLH raises it relative to GFL by 3.58. This selected diagnostic is not a population estimate or texture-fidelity endpoint. Figure sources, shared crops and asset credits are recorded with the images.

**Location.** Main manuscript: Figures 5–9, Tables 9 and 11, Discussion and Limitations. Supplement: Figure S1 and Figures S2–S9, Sections S7–S8, S13, S18–S21, and source/asset records in Table S1 and the bake credit CSV.

### Comment 2 — “Please evaluate the main adapter and relevant baselines under the same held-out protocol.”

**Response.** The authenticated 01549 main-table result reports pooled full-image PSNR of 18.86 dB for C3 and 17.90 dB for Fixed High on its original 300-object pool, which includes the 24 development objects. We retain the resulting +0.96 dB as a historical pooled result. The surviving archive does not contain the object-paired rows needed to reconstruct a paired confidence interval.

Fresh C is a separate, controlled retraining on 300 object IDs disjoint from the earlier development probe and original evaluation cohort. Its frozen primary comparison is C3 minus Fixed Low on foreground-masked PSNR: +0.522 dB (95% object-bootstrap CI [+0.404, +0.641]). The checkpoint, comparator, metric scope and object cohort differ from 01549, so this is a new matched result, not a numerical reproduction of the historical pooled result. Fixed High, Generic Linear and equal-budget controls are reported alongside it.

**Location.** Main manuscript: historical main-table result, Fresh C paired tables and effect figure. Supplement: S2, S3, S4–S5, S8, and S9.

### Comment 3 — “Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”

**Response.** The revision distinguishes image-space agreement, subjective preference, texture variation and baked appearance throughout. Gradient and Laplacian values are identified as variation diagnostics. The 01549 3AFC result concerns its original stimuli; Fresh C reports target-view image metrics; the bake pilot reports unseen-view metrics. We use these endpoints for the outcomes they measure and do not treat any one of them as a direct texture-fidelity score.

**Location.** Main: metrics, Figures 5–9, preference results and Limitations. Supplement: Sections S2, S7, S12, S13 and S18.

### Comment 4 — “A confidence interval crossing zero for the FG-SSIM difference does not establish equivalence or non-inferiority.”

**Response.** Table 5 reports paired Fresh C intervals, including the C3−Fixed High Edge-SSIM difference of −0.01881 (95% object-bootstrap CI [−0.02083, −0.01678]). We report this as an endpoint difference. No non-inferiority margin was prespecified, so the revision makes no equivalence or non-inferiority claim. Historical SSIM values remain identified separately from Fresh C.

**Location.** Main manuscript: paired Fresh C table and endpoint interpretation. Supplement: Section S2.

### Comment 5 — “It is still hard to reproduce the FAC experiments. The code is encouraged to be released.”

**Response.** The seven-configuration FAC re-examination and untrained control remain identified as results reported in the first-round 01549 revision. The reported trained configurations were 1.10–2.94 dB below TCAS on FG-PSNR; the untrained twelve-object control reported ΔFG-PSNR −0.18 dB (95% CI [−0.42, +0.05]). The reproduction archive contains the executed inference/evaluation scripts, frozen configuration and identity records, and standalone paired-statistics workflow. A recovered configuration points to a 1,200-object list rather than the stated 1,706-object pool, and the archive lacks a run-bound training manifest and weights; these materials therefore do not constitute a full FAC replay.

**Location.** Main manuscript: FAC discussion and Limitations. Supplement: S11/Table S16.

## Reviewer 2

### Concern 1 — “The core methodological contribution remains quite limited.”

**Response.** TCAS addresses a concrete graphics problem: how geometric-conditioning strength across denoising stages affects generated multi-view texture images and their projected appearance. It exposes a piecewise temporal multiplier on the existing GeoTex-Adapter residual path, with requested scale, cap-adjusted applied scale and resulting residual correction defined separately. The inference-time control adds no learned parameters and requires no additional training.

Prior work already studies layer/time scheduling, including SSI's geometry-conditioned ControlNet strength schedule. We therefore state the contribution as a controlled evaluation of this GeoTex residual-path intervention for multi-view texturing. Fresh C compares carried-forward C3 with fixed and linear controls and reports a paired C3--Fixed Low FG-PSNR gain; its strong controls and equal-applied-budget analysis identify comparator- and endpoint-dependent rankings. The original preference study, calibrated bake and native N=50 interface test extend the evaluation to subjective preference, projected appearance and a distinct geometry-conditioning interface.

Together, the paper contributes an executable control definition and matched evidence about its image-space, preference, bake and second-interface outcomes. A separate follow-up in Supplementary Section S22 tests a per-view projection of a geometry-related CFG interaction: its two prespecified source-view outcomes improve over native on 64 objects, while its descriptive nonreference outcomes do not establish noninferiority. The cohort was previously exposed in Fresh C research; this intervention is distinct from TCAS, its APG development comparisons show no separated advantage, and it is not used as evidence for the TCAS estimates. We do not claim that C3 is a theorem-derived optimum or that its schedule law transfers across architectures.

**Location.** Main: Introduction/Related Work, Method, Fresh C and application results, Discussion. Supplement: S3–S5, S9/Table S14, S12, S17, and S22.

### Concern 2 — “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”

**Response.** The CAI proposition and proof have been removed from the claim of an independently derived selector. The manuscript retains the executable TCAS scaling definition and the historical C3 profile and development record; it treats that profile as an empirical candidate carried into matched evaluation.

**Location.** Main manuscript: TCAS Method, development Table 3, Figure 4. Supplement: S10/Table S15.

### Concern 3 — “Cross-backbone generalization remains the most important missing experiment.”

**Response.** We add a native-camera MV-Adapter test on fifty inputs whose MV-Adapter outputs had not been inspected during selection. The seven conditions share inputs, seed, geometry and evaluation; the complete 350-row matrix includes all fifty objects, and the frozen primary result is reported in the main text. Three new textured objects pass official/deployed path identity checks for 18 RGB images, conditioning features and injected residuals. The older seven-object archive used inconsistent target-camera calibration and is separately documented rather than pooled; earlier N=98 and N=76 exploratory probes are in Supplement S17, and the compatibility-base MVDiffusion panel is in S12.

The primary Middle-high−Fixed Mean FG-PSNR is +0.029 dB (95% object-bootstrap CI [−0.019, +0.081], paired Monte Carlo sign-flip p=0.281; 29/50 favorable). This is valid native-interface evidence for the tested comparison; its primary interval includes zero. The 104 remaining pair–metric tests use one Holm family and are reported in S17, including endpoint-specific differences. The result tests a feature-scaled MV-Adapter interface, distinct from GeoTex residual scaling.

**Location.** Main: Second-Interface Evaluation, native MV-Adapter condition table and Figure 10; Supplement S16–S17 and the complete native fifty-object contrast table. The separate bake results are Figure 9 and its results table, with protocol in Supplement S18.


We hope the revised presentation makes the TCAS control, its measured outcomes, and the limits tied to each evaluation domain clear. The clean and marked manuscripts, Supplement, source archive, and playback-checked video are supplied as separate files.
