# Response to the Editor and Reviewers

Manuscript: **Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: A Controlled Empirical Study**

Dear Editor and Reviewers,

We have revised the paper around the complete evidence for geometry-control allocation in multi-view texturing. TCAS remains the inference intervention, and C3 remains its historical middle-high profile. The revised contribution is a controlled empirical assessment of strength, temporal allocation and actual baked appearance, together with the boundaries observed on different conditioning interfaces. We no longer present C3 as generally preferred or use CAI to derive an optimum.

The new evidence changes the practical conclusions. Competitive fixed and linear controls outperform C3 on the displayed Fresh C image means; equal-budget fixed mean and late-high also outperform its middle window. Native MV-Adapter evaluations do not detect the specified middle-window advantage. A small late-high bake benefit on ten compatible GeoTex objects is reported beside a separate twenty-object GSO comparison that does not detect that benefit. All valid adverse outcomes remain included.

The manuscript, question-grouped Supplement, object-level records, runnable statistical code and actual exported-mesh video accompany the revision. The marked manuscript is compared with the authenticated submitted source, rather than only with an intermediate revision. Historical checkpoint and FAC training-record limitations remain explicit.

## Reviewer 1

### 1. Practical quality, full-object comparisons, strong controls and unseen baked views

**Comment.** The displayed outputs have color shifts, repeated patterns and discrepancies from the reference; broader full-object comparisons, the unmodified pipeline, strong fixed controls, unseen baked views and consistency/seam evidence are needed.

**Response.** The main text retains full-object examples, identical pixel crops, a strong fixed-scale comparison, a Generic Linear counterexample and a color/detail failure. The favorable/adverse weak-control examples are retained in Supplementary Section S9. Each display states its selection rule and preserves recorded RGB contents; outcome-selected illustrations do not estimate failure prevalence. We adopted clearer shared full-object frames from the conservative visual revision, added the matched GT-256 bake beside source/Fixed Mean/Late-high, and show the native MV-Adapter cases with their complete seven-control Supplement display. Conspicuously malformed No Adapter visual columns are omitted for legibility; all conditions, negative results and numerical comparisons remain reported. Source-image hashes, crops and object/condition identities are preserved, and a vision-capable assistant checked the actual figures and rendered PDFs for label, caption and appearance consistency. This presentation check is not a validation of texture fidelity or a substitute for author assessment.

The ten-object GeoTex study retains original geometry, native UVs and legal base-color material semantics. All conditions share the six bake cameras, 256-pixel source resolution, masks, atlas resolution, fill settings and eleven unseen evaluation cameras. GT-256 is baked with the same inputs and settings; unseen cameras do not contribute to the bake. Late-high minus Fixed Mean unseen-view foreground LPIPS is -0.002652, with pointwise 95% interval [-0.004144,-0.001367] and exact paired sign-flip p=0.00195. This is approximately a 2% reduction, closing only 3.7% of the gap to the matched GT reference bake. Reference-appearance failures remain visible, and C3's earlier small-pilot PSNR advantage does not repeat stably; its SSIM is lower than Fixed High.

We also report the complete separate GSO20 application evaluation in the main text: twelve conditions, three seeds and twenty GT self-bakes produce 740 unique meshes and 8,140 unseen-view records. Late-high minus Fixed Mean LPIPS is +0.000084, with interval [-0.000103,+0.000286] and original-family Holm p=0.788. It does not detect the GeoTex pilot's benefit. The domain, conditioning and projection protocol differ, so this is not a direct same-protocol replication.

The original GSO attempt stopped at a UV-ramp gate after fifteen objects. Subsequent GT-only diagnostics validate continuous nonlinear surface-color fields, an independent analytic multi-island fixture and a deliberate image-flip negative control. The revised calibration is post hoc. The fixed objects, projection, cameras, masks, material semantics and resolutions remain unchanged; all 375 earlier GLB hashes and metric records reproduce exactly. The failure and calibration addendum are both retained in Supplementary Section S4. GT self-bake error and incomplete coverage remain reported, with all foreground scored and no GT-error subtraction.

We have corrected baseline names. GeoTex Constant 1.0 (capped) differs from the unset-scale Native residual branch; both belong to the controlled sampler and are not labeled the complete unmodified pipeline. Complete native-base/v29 diagnostics retain their actual weights, guidance and preprocessing settings. Native MV-Adapter has a separate actual default-path identity check. These distinctions prevent inference-path checks from being mistaken for proof of texture quality or full GeoTex default equivalence.

Image/bake rankings are broadly positively associated. The post hoc seven-schedule GSO sensitivity has mean Spearman 0.396 and a changing minimum-mean LPIPS condition on 11/20 objects; this is not evidence of a general rank reversal or statistically resolved winners. We additionally replay the shared-UV incoming-camera RGB variance: all 80 archived values reproduce exactly, and known-color controls check its formula/path. Late-high minus Fixed Mean is -0.002448 (descriptive 95% interval [-0.003473,-0.001604]; additional exploratory Holm21 p=0.041). Fixed High has lower disagreement yet higher baked LPIPS than Late-high. A shared constant-black control has zero variance, so consistency alone does not establish fidelity. Natural texture, resampling and UV overlap remain contributors. No validated quantitative seam endpoint or PBR-fidelity claim is made. Real local/whole-object displays and the eleven-camera exported-GLB video provide the available qualitative evidence.

**Locations.** Main: “Appearance and Color Failure Analysis,” “Actual Baked Appearance: Local Benefit and External Limits,” and “Discussion and Limitations.” Supplement: S4-S6 and S9. Video: Real_Baked_Comparison_round_015.mp4; its input selection and hashes are recorded in the delivered provenance file.

### 2. Same-adapter evaluation outside the schedule-selection objects

**Comment.** The main pooled evaluation includes selection objects, while the strict holdout changes adapter and schedules; it does not directly confirm the historical 0.96 dB gain.

**Response.** Fresh C is a matched comparison on 300 UIDs with zero overlap with the historical evaluation/probe pool, the recorded 1,118-object training list and the earlier clean-v2 evaluation list. All compared conditions within each run share the frozen checkpoint, runner, inputs, targets, seed policy and metric code. The internally specified C3-minus-GFL primary foreground-PSNR difference is +0.522 dB, with the original pointwise interval approximately [+0.404,+0.641]. Strong controls and the equal-budget addendum are fully reported.

The checkpoint is a controlled retraining. The historical main adapter and its complete run/metric identity have not been recovered, so Fresh C is not an exact same-checkpoint reproduction of the old +0.96 dB estimate. That number is removed from the current headline evidence and retained only with its historical qualification. We have made this limitation visible in the main study design and discussion. Matching the new conditions establishes an internally valid held-out comparison; it does not by itself fulfill an exact historical replay.

**Locations.** Main: “Study Cohorts, Sampling and Statistical Units,” “Competitive Controls and Matched Temporal Allocation,” and “Quality, selection and replication limits.” Supplement: S1-S2 and S7.

### 3. Texture variation versus faithful appearance

**Comment.** Larger gradients or Laplacian variance can represent artifacts; the connection between metric gains and faithful texture reproduction is unclear.

**Response.** The paper uses separate terms for image-space agreement, reference-color agreement, texture variation, historical preference and baked appearance. Gradient magnitude, Laplacian variance, RGB spread and entropy are descriptive variation statistics, not fidelity measures. Their values do not validate a faithful material.

The selected color diagnosis remains failure-enriched and descriptive. LLH lowers variation while increasing mean reference-color error relative to GFL. Visible color shifts persist before baking, and the tested interventions do not establish a repair. The unrecoverable historical audit's prevalence and “true shape gain” classifications are withdrawn. The actual meshes preserve source geometry; unchanged silhouettes are not evidence of geometric reconstruction improvement.

**Locations.** Main: “Image-Space Metrics and Texture-Variation Diagnostics,” “Appearance and Color Failure Analysis,” and the two bake evaluations. Supplement: S5-S7.

### 4. Paired intervals, structural tradeoffs and non-inferiority

**Comment.** A confidence interval crossing zero does not establish equivalence or non-inferiority; lower Edge-SSIM requires a paired analysis and moderated preservation claim.

**Response.** Paired object-level differences and pointwise intervals are reported with their original comparison families. In Fresh C, C3 minus Fixed High FG-SSIM is -0.04553, with interval [-0.04937,-0.04167]; Fixed High has better means on all four displayed image endpoints. In the ten-object bake, C3 minus Fixed High SSIM is -0.05274, with interval [-0.07459,-0.03170] and four-test secondary Holm p=0.00781. These losses remain explicit.

No non-inferiority margin has been selected after observing the data. Intervals crossing zero and unseparated corrected tests are described as non-detection, not equivalence or preservation without loss. Native-interface and bake views, and GSO seeds, are averaged within object; Fresh C's image endpoints are computed once on its six-view composite. They are not independent samples. Separate correction families retain their stated scope.

**Locations.** Main: “Competitive Controls and Matched Temporal Allocation,” “Actual Baked Appearance,” and “Quality, selection and replication limits.” Supplement: S2-S5.

### 5. FAC reproduction and code

**Comment.** FAC experiments remain difficult to reproduce and code release is encouraged.

**Response.** The package contains the statistical code, frozen object-level results and the available recorded inference/configuration components. Statistical recomputation does not require model weights; fresh inference requires the specified assets, source data and environment.

FAC remains a historical negative re-examination. The recovered configuration refers to a 1,200-object list, whereas the submitted paper reported 1,706 objects. The training seed, checkpoint identity and sampled-run manifest remain incomplete. We now supply a separate byte-preserved FAC source archive, including two distinct recovered training entries, their configuration/dependency files and per-file hashes. The earlier entry needs an explicit flag to freeze the base adapter; the later one is controller-only. Their controller source is byte-identical; three distinct standalone CPU controller fixtures pass forward, gradient-path and state-roundtrip checks. These do not authenticate the historical executed source/CLI or establish isolated full-model replay. We cannot claim a complete FAC training replay or substitute the later new geometry-training studies for FAC reproduction. The delivered README distinguishes verified recomputation, recovered code/component execution, available inference records and missing historical training artifacts. The new Supplement S7 and source audit give the explicit executed-test scope and source-entry differences.

**Locations.** Main: “Historical Preference and Training Evidence” and “Data availability.” Supplement: S7-S8; reproduction instructions and source manifest in the review package.

## Reviewer 2

### 1. Contribution beyond schedule selection

**Comment.** A manually selected three-stage schedule for an existing adapter may not constitute a sufficiently substantial methodological contribution.

**Response.** The revision claims a controlled empirical contribution to geometry-guided texturing rather than an independently new scheduling principle. Prior work, including SSI, already varies strength across layers and time and schedules geometry conditioning. We have removed the argument that introducing a time function alone provides methodological novelty.

The task-specific findings are:

1. C3's gain over fixed low combines a larger deep/middle applied-scale budget with timing. Competitive fixed/linear controls change its practical standing; equal-budget C3-minus-Mean and C3-minus-Late PSNR are -0.133 and -0.564 dB.
2. Actual baking limits the application meaning of image effects. A small ten-object late-high LPIPS benefit is reported beside the separate twenty-object non-detection, persistent appearance errors and matched GT self-bake losses.
3. Native conditioning interfaces and protocol sensitivities expose endpoint-dependent effects. Neither native middle-window primary detects an advantage; GSO late-high has a small secondary PSNR increase of 0.045 dB without a nonreference LPIPS benefit, and a changed reference-conditioned checkpoint shows a different direction.

New post-inspection analyses also quantify objectwise limits. In Fresh C, at least one other tested control weakly dominates C3 on all four recorded point-estimate endpoints for 270/300 objects; this is neither resolved per-object superiority nor material quality. GSO100 Late--Mean PSNR is positive on average at all three fixed seeds, while only 27/100 objects improve at every seed and 68/100 have mixed/tied signs. Nonreference LPIPS changes average direction across seeds, and only 1/20 GSO bake objects improves at all three. These findings distinguish small average effects from repeatable objectwise benefit, retaining all seeds and outcomes. Together with the new incoming-view diagnostic, these comparisons produce quantitative operating-point conclusions that differ from the original C3 recommendation. Complete adverse results remain in the main findings and Supplement. Projection development, lightweight-module timing and archival training details are auxiliary evidence and are not presented as new successful methods. Protocol documentation supports the results rather than replacing the contribution.

We recognize that the significance of this empirical contribution remains an editorial assessment; we do not claim that more experiments alone establish new methodology.

**Locations.** Main: revised Abstract, Introduction/contributions, competitive controls, both bake studies, transfer evaluation, Discussion and Conclusion. Supplement: S1-S8.

### 2. CAI appears to formalize the selected schedule

**Comment.** CAI appears to formalize an empirically chosen schedule rather than derive it independently.

**Response.** The independent derivation, proposition and optimality interpretation are removed from the active manuscript and Supplement. C3's origin is historical selection, not a proved optimum. The method supplies executable scale and execution-progress definitions, native caps and comparison logic.

Requested strength, applied strength and state-dependent residual correction are distinguished. Equal applied per-group sums support the total effect of moving the high segment. They do not imply equal residual dose or a mechanism independent of the changing trajectory. The original submitted formulation remains only in the authenticated comparison baseline.

**Locations.** Main: “Study Design and Control Interface” and “Competitive Controls and Matched Temporal Allocation.” Supplement: S1-S2 and the explicitly historical selection record in S7.

### 3. Evaluation on a genuinely different backbone

**Comment.** Different adapters inside the same architecture family do not substitute for another geometry-conditioned multi-view backbone.

**Response.** Native MV-Adapter supplies a different condition-guider/additional-feature interface. The fifty-object matrix includes seven controls and all 350 rows. Its input-only selection excluded previously inspected MV-Adapter outputs. Official/deployed and constant-default identity checks reproduce all eighteen RGB images and measured features/residuals on three checked objects. Native cameras and source-UV target checks establish the evaluation contract. Middle-high minus Fixed Mean PSNR is +0.029 dB, interval [-0.019,+0.081], paired p=0.281. Thirteen legal constant-white targets remain in the primary cohort; the thirty-seven textured objects are descriptive sensitivity, not a replacement cohort.

The GSO100 native-interface extension retains seven original scale/time profiles, three seeds and shared reference/geometry inputs. Its specified Middle-high-minus-Fixed-Mean all-six PSNR result is -0.014 dB, interval [-0.031,+0.004], p=0.122. The complete matrix has 3,600 cells: the original 2,400 scale/projection/APG cells plus 1,200 inherited-profile cells. Four new profile outputs were frozen before execution after earlier baseline exposure. This is external sensitivity on an exposed convenience cohort, not pristine independent confirmation.

The 75-object MVDiffusion panel is retained as retrospective third-interface evidence. Its control interpolates correspondence-block outputs while concatenated depth remains unscaled. A later mirror check matches 1,552 tensors and twelve outputs for one object; all seventy-five objects were not rerun on that mirror. Negative/mixed endpoints and this scope remain explicit.

These are genuine different-backbone/interface evaluations with valid bounded results. They do not demonstrate stable C3 transfer, and the different input cohorts prevent assigning all variation exclusively to backbone.

**Locations.** Main: “Transfer to other conditioning interfaces,” study design and named-effects table. Supplement: S3-S4 and S8.

## Reviewer 3

We thank the reviewer for the positive assessment. The revised version retains the study identity and historical evidence while updating the main conclusions to include stronger controls, native-interface evaluation and the complete application comparisons.

---

All completed supplementary experiments are included with their validity and chronology limits. The historical adapter replay, FAC training archive, validated seam endpoint and physical-material fidelity remain outside the verified evidence. The revision does not assert that these unresolved requests have been satisfied.
