# Response to the Reviewers

**Manuscript:** CAG-D-26-00962  
**Title:** *Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: Control Allocation and Baked Appearance*

Dear Editor and Reviewers,

This manuscript originated from Paper 75 recommended by CAD/Graphics 2026 for Computers & Graphics. We thank the reviewers for the initial conference comments and the subsequent journal review. The response below addresses the actual second-round concerns, followed by a compact record of continuity with the first round.

The revised paper studies the historical TCAS/C3 profile as an inference-time intervention on an existing GeoTex geometry-residual interface. Its scientific contribution is a controlled account of what a geometry-control comparison identifies and how it relates to baked appearance. We distinguish requests, inherited wrapper-capped applied scales and state-dependent residual corrections; report competitive fixed and linear controls; preserve the declared matched-budget primary; and assess selected native-UV bakes and separate native conditioning interfaces. The evidence revises earlier schedule recommendations rather than establishing a universally preferred method. Remaining historical-reproduction, deployment and methodological-novelty limits are stated below.

## Reviewer 1 — second round

### Comment 1: Color shifts, full-object comparisons, native pipeline and competitive controls, baked unseen views, seams and video

**Changes and evidence.** Main Figure 2 shows three Fresh C objects, including Building 03 and Specimen 103, with Target, Fixed Low, C3, Fixed High and Generic Linear at the same camera. Main Figure 3 shows two objects at the same held-out camera (raw004), each with GT-256, Fixed Mean and Late-high rendered from shared mesh/UVs and a common within-object crop. Tire is selected by median source-foreground Laplacian variance among seven display-cleared assets. The carved font is explicitly post-outcome selected for the largest existing eleven-view LPIPS decrease among those seven; its PSNR also decreases. The examples show persistent reference-appearance mismatch and an endpoint tradeoff, not population prevalence. The complete ten-object effect distribution and values remain in Supplement S5, including objects without publication display rights. Figure 4 shows the pink Cap Test reference and its shared-view comparison with Fixed Low, C3 and layer LLH. The displayed Bake10 PNGs are 512×512 and have no method-specific recoloring.

The main text now places the native-pipeline quality boundary next to the bake results. On the same fifty inputs and five nonreference views, the new HF-based geometry checkpoint trails the recorded full-v29 ControlNet pipeline by 2.16 dB FG-PSNR and 0.0341 FG-LPIPS. A same-v29-base exploratory follow-up still trails full v29 by 0.0159 LPIPS although unscaled geometry improves over disabled geometry within that follow-up. These are deployment/protocol comparisons, not TCAS-only scale ablations: base weights differ in the first comparison, geometry architecture/training history differ in both, and the 50-step seed-42 protocol is not the official command-line default. The full nine-condition and same-base grids remain in Supplement S8.

The asset assessment exports native-UV meshes and averages eleven unseen unlit renders within each object, alongside matched GT-256 self-bakes. GeoTex10 Late-high minus Fixed Mean FG-LPIPS is −0.002652 (95% object-bootstrap interval [−0.004144,−0.001367]; exact sign-flip p=0.00195). The separate GSO20 difference is +0.00008379 (interval [−0.00010305,+0.00028592]; original-family Holm p=0.78765), which does not detect the same benefit. The GeoTex video presents two input-order, rights-cleared objects at eleven discrete unseen cameras. A separate GSO video illustrates the first source-ordered mouse at seed 42 across all twelve recorded conditions and eleven unseen cameras; its source-mesh column is not a GT self-bake. Neither video estimates population quality.

**Locations.** Main Figure 1 (p. 4), Figure 2 (p. 7), Figure 3 (p. 9) and Figure 4 (p. 10); Main Tables 2–5 (pp. 6–8), Table 6 (p. 10) and Table 7 (p. 11); Main Sections 3.5 (p. 5) and 4.4 (pp. 7–9); Supplement Sections S3–S6/S8/S9; separate `Supplementary_GeoTex_Baked_Comparison.mp4` and `Supplementary_GSO_Baked_Comparison.mp4`.

**Remaining limitation.** The S8 full-v29 comparison is input/seed matched under a recorded protocol but is not an architecture- and base-weight-matched TCAS-only comparison or the official default command-line run. Native/unset residual and capped Constant 1.0 controls do not equal the complete pipeline. The bake cohorts are small and compatibility-selected; unfilled coverage and sampling/UV limitations remain, and no validated seam-quality endpoint or PBR/material-fidelity result is claimed. Full-object displays and the video illustrate errors, not their prevalence.

### Comment 2: Same-protocol held-out comparison of the original main adapter and baselines

**Changes and evidence.** Fresh C contains 300 UIDs disjoint from the historical selection/evaluation pool and recorded training lists. Conditions share a frozen retrained checkpoint, inputs, targets and paired seeds. Its original C3−Fixed Low FG-PSNR primary is +0.522 dB (95% object-bootstrap interval [+0.404,+0.641]; 206/300 favorable). Strong fixed and linear controls are reported on this same cohort. The paper explicitly separates this controlled retraining from numerical reproduction of the historical +0.96 dB result.

The separate historical-request retraining excludes recorded training-list intersections. However, a failed input was replaced without recording its actual UID. Its 276 records are therefore requested slots, not a verified 276-unique-object holdout. C3−Fixed High is +1.699 dB full-frame PSNR but −1.314 dB foreground PSNR; foreground LPIPS worsens by 0.01127 and foreground SSIM by 0.05961. This adverse foreground evidence remains reported, along with exclusion of the known failed requested slot as sensitivity rather than outcome filtering.

**Locations.** Main Table 1 (p. 6); Main Section 4.1 (p. 5); Main Table 2 (p. 6); Main Section 4.6 (p. 11); Supplement Sections S1/S2/S7, including Supplement Table S35 (p. 58).

**Remaining limitation.** The original main checkpoint cannot be authenticated from the retained archive. Fresh C cannot be called an exact reproduction of it, and the unknown substituted UID prevents certified independent-object inference for the 276-request record. The request for an exact historical-checkpoint holdout is therefore not fully resolved.

### Comment 3: Texture variation versus faithful texture reproduction

**Changes and evidence.** We separate target-view image agreement, reference-color agreement, variation diagnostics, historical preference and actual baked appearance. Gradients, RGB standard deviation and Laplacian variance may increase through detail or artifacts and are not fidelity measures. The 26-object color diagnosis is failure-enriched and has no prevalence interpretation. Complete-object displays explicitly preserve the discrepancy between generated patterns and reference appearance. The asset results contextualize the small GeoTex bake change relative to the matched GT reference bake; substantial error remains.

**Locations.** Main Section 3.2 (p. 3); Main Section 4.3 (p. 7); Main Figure 4 (p. 10); Main Figure 3 (p. 9) and Section 4.4 (pp. 7–9); Main Section 5 (pp. 11–12); Supplement Sections S5–S7.

**Remaining limitation.** Unlit base-color scores and variation proxies do not establish faithful materials or appearance under changing illumination. We do not replace that missing validation with better diagram presentation or the historical preference result.

### Comment 4: Paired intervals, Edge-SSIM and non-inferiority/equivalence

**Changes and evidence.** Validated cohorts use paired object-level intervals and retain Edge-SSIM. C3−Fixed High Edge-SSIM is −0.01881 (95% interval [−0.02083,−0.01678]; frozen Holm p=0.00059); foreground SSIM is −0.04553 (interval approximately [−0.04937,−0.04165]). These losses remain visible in the competitive-control results. We state that an interval crossing zero does not establish equivalence or non-inferiority. The 276-slot diagnostics have a separate, explicitly weaker identity.

**Locations.** Main Table 2 (p. 6); Main Section 4.1 (p. 5); Main Section 4.2 (pp. 5–6); Main Section 3.5 (p. 5); Supplement Section S2 and Supplement Table S2 (p. 5); Section S7 for requested-slot sensitivity.

**Remaining limitation.** No non-inferiority margin was prespecified. Pointwise intervals and separate correction families do not provide one global experiment-wide guarantee; non-detection is not equivalence.

### Comment 5: FAC reproducibility and release of code

**Changes and evidence.** We retain the seven previously reported FAC configurations and their adverse FG-PSNR changes (−1.10 to −2.94 dB relative to TCAS). Recovered controller code, entry points and bounded execution/source records are supplied; the twelve-object untrained comparison remains a separate reported historical analysis. Component checks exercise synthetic tensors and state serialization rather than the complete historical diffusion training run.

**Locations.** Main Section 4.6 (p. 11); Supplement Section S7; Supplement Table S30 (p. 50); recovered-source and component-validation records in the accompanying evidence package.

**Remaining limitation.** The submitted training pool states 1,706 objects, whereas a recovered configuration lists 1,200; run-bound training identities, seeds and historical weights remain incomplete. We do not claim exact full-model replay or reclassify those historical negative results as newly confirmed experiments.

## Reviewer 2 — second round

### Concern 1: The methodological contribution remains limited

The revised paper is presented as a controlled empirical study of geometry-control allocation and the resulting textured asset. Its three contributions connect implementation, asset evaluation and interface-dependent response; novelty of temporal scheduling itself is not claimed.

**Changes and distinction from prior work.** We agree that adding a temporal scale profile does not establish a new general scheduling method. The official ControlNet depth-to-image demo assigns a fixed thirteen-block profile in guess mode according to block index; it is not adaptive to the depth-map contents. Diffusers v0.21.0 exposes start/end temporal gates. SSI is a closer joint layer/time precedent: it varies StyleID query blending and separately schedules geometric ControlNet conditioning. The revised Related Work distinguishes these mechanisms and credits those precedents. [Official ControlNet source](https://github.com/lllyasviel/ControlNet/blob/f2e1bc38dc8d925fb542be4c138c46013ace1988/gradio_depth2image.py#L49), [versioned Diffusers documentation](https://huggingface.co/docs/diffusers/v0.21.0/api/pipelines/controlnet), [SSI original paper](https://arxiv.org/html/2605.26538).

TCAS changes the requested scale on the existing GeoTex residual path. Native caps belong to the evaluated wrapper, not to a new TCAS clipping design. The applied multiplier is the minimum of the request and that group cap before addition to frozen features. The resulting correction still depends on the evolving state. This identifies the tested operator; it does not add a learned branch, selector, objective or general theory.

**Evidence-backed contribution and graphics relevance.** The revised study establishes what can be concluded about this geometry-control setting that a C3-versus-weak-fixed comparison alone could not establish. C3's +0.522 dB foreground-PSNR gain changes deep/middle applied sums from 62.5 to 82.5 each, while shallow remains 40. It therefore cannot identify an advantage from temporal placement alone. Strong Fixed High and Generic Linear controls have better means on the four reported Fresh C endpoints. At matched per-group applied sums, the preserved timing primary Middle−average(Early,Late) is −0.0338775 dB (95% interval [−0.117170,+0.051422], p=0.432378), which does not detect the proposed middle-window advantage. Main Table 7 reports this original contrast first, followed by the two study-specific native-interface FG-PSNR primaries. Main Table 5 retains the separate Bake10 and GSO20 unseen-view FG-LPIPS primaries. The PSNR and LPIPS endpoints remain separate and are not pooled. A later retrospective all-pair analysis within the same Fresh C cohort finds Middle-high above Early-high by 0.496 dB and below Late-high by 0.564 dB in FG-PSNR (both Holm-adjusted p=0.00059 in its separate 59-test family); its corresponding Middle−Early and Middle−Late FG-LPIPS differences are −0.00472 and +0.00466 (both adjusted p=0.00059). The intervals reported for these contrasts are pointwise, not multiplicity-adjusted. These comparisons support a bounded finding of placement-sensitive response at matched applied sums within this cohort. They are retrospective, do not replace the specified timing primary, and establish neither a residual-dose mechanism nor a preferred late schedule. The separate Middle−Fixed Applied Mean FG-PSNR contrast (−0.13326 dB) is explicitly exempt from that Holm family and remains descriptive. Full contrasts and comparison families are reported in Supplementary Section S2.

For graphics researchers the output of interest is a textured asset, and the generated RGB views are intermediate products. Selected native-UV bakes with matched ground-truth self-bakes and eleven unseen cameras quantify the appearance effect under fixed evaluation protocols. The local GeoTex10 LPIPS gain is small relative to remaining error and heterogeneous across all ten objects; it is not detected in the separate GSO20 study. The S8 full-native and same-base comparisons explain why a within-checkpoint geometry benefit cannot establish competitive deployed quality. A separate retrospective FRESH_CONFIRM_300 analysis relates LLH--GFL response to input texture complexity (Laplacian-variance quartile PSNR means +4.140 to −0.029 dB), without establishing a causal descriptor, threshold or adaptive algorithm. Native conditioning-interface comparisons further limit treating a shared scale label as a transferable dose. These findings correct the earlier C3 recommendation and identify when a control comparison can support a timing interpretation or an asset-quality claim. Their value rests on this controlled task knowledge, rather than experimental volume or statistical significance alone.

**Locations.** Main Sections 1, 2.3, 3.1, 3.3, 4.2, 4.4 and 5; Main Figure 3 and Tables 2, 5–7; Supplement Sections S1–S5, S7 (retrospective texture complexity) and S8 (full-native and same-base comparisons).

**Remaining limitation.** TCAS remains a manually specified intervention on an existing adapter. The equal-budget addendum reuses previously inspected Fresh C objects and is not independent prospective confirmation; equal applied sums do not establish equal residual dose. Cohort, interface and projection differences prevent causal assignment of the varying effects, and unlit rendering does not establish material fidelity.

**Contribution and scope.** Within these boundaries, the revision contributes a controlled empirical account that separates applied-strength comparisons from the matched-applied-sum timing test and evaluates both alongside strong fixed and linear controls. It treats native-UV bake appearance as a distinct asset-level endpoint instead of inferring fidelity from generated-view metrics. The prespecified timing contrast did not detect the proposed middle-window advantage; retrospective pairwise contrasts support only cohort-specific placement sensitivity. We therefore present TCAS as the intervention under study and make no claim of a universally optimal or transferable schedule.

### Concern 2: CAI formalizes a selected schedule rather than deriving it

**Changes and evidence.** The independent CAI derivation and optimality claims are removed. C3 is described as the recorded choice from the historical 24-object/17-variant development probe and carried forward without a new schedule search. One-third windows are operational partitions of sampling progress, not a universal semantic decomposition. The preserved matched-budget primary does not detect the proposed middle-window advantage.

**Locations.** Main Section 3.3; Main Section 4.2 (pp. 5–6); Main Section 5 (pp. 11–12); Supplement Section S7, Supplement S7 (C3 Development Record), p. 52 and Supplement Table S33, p. 54.

**Remaining limitation.** Historical candidate-level records cannot reconstruct the original ranking. C3 is neither independently derived nor verified as unique or optimal; no causal stage-utility theory is claimed.

### Concern 3: Missing cross-backbone validation

**Changes and evidence.** A native-camera MV-Adapter comparison evaluates fifty input-selected objects with seven shared conditions. Its specified Middle−Fixed Mean foreground-PSNR primary is +0.029 dB (95% object interval [−0.019,+0.081]; paired p=0.281; 29/50 favorable). A separate GSO100 study uses this same MV-Adapter interface on different inputs and does not detect its specified middle-window advantage; it is not an independent third backbone. Its primary compares Middle with Fixed Mean, whereas the GeoTex timing primary compares Middle with mean(Early,Late). The retained 75-object MVDiffusion study scales a partial correspondence-block operator while leaving depth concatenation unscaled. We report these study-specific, endpoint-dependent results separately and do not pool them as equal-dose replications.

**Locations.** Main Section 4.5 (pp. 9–11); Main Table 6 for native MV-Adapter means; Main Table 7 for the specified native-interface FG-PSNR primaries; Supplement Sections S3/S4/S8 and Supplement Table S15.

**Remaining limitation.** Native MV-Adapter is a different conditioning-interface test, not an architecture-matched replication of GeoTex residual scaling. GSO100 is not another backbone, and MVDiffusion tests a partial operator. The studies expand empirical scope without establishing a general cross-backbone schedule advantage; the reviewer's broad generalization concern remains unresolved.

## Reviewer 3 — second round

Reviewer 3 reports that the prior revision is suitable for publication and raises no new technical request. We thank the reviewer. The present manuscript preserves the historical preference and FAC records at their stated evidence levels and adds the controlled findings and limitations described above. The positive assessment is not used as evidence that the remaining R1/R2 gaps are resolved.

## Continuity with the first CAD/Graphics review

The following records the actual first-round items without repeating the full historical response or treating previously reported evidence as newly reproduced.

|First-round concern|Retained clarification or change|Current locations and remaining boundary|
|---|---|---|
|R1.1: split identities and FAC objective/train/tuning/test separation|New validated cohorts have explicit UID/input/seed/statistical identities; historical FAC objective, configurations and adverse re-examination remain archived.|Main Table 1, p. 6; Main Section 3.5, p. 5; Supplement S1/S7 and Supplement Table S30, p. 50. Historical FAC split/run authentication remains incomplete.|
|R1.2: exact implementation, checkpoints, conditions, resolution, sampler and references|Executed protocol and current checkpoint/source identities are supplied; complete-default and controlled paths are distinguished.|Main Section 3.4, p. 5; Main Section 3.5, p. 5; Supplement S1/S6. Original main checkpoint and complete historical replay remain unauthenticated.|
|R1.3: participant/object clustering and study design|The reported two-level participant/object bootstrap, 10,000 draws, instructions/randomization and original 3AFC counts remain historical preference evidence.|Supplement S7, Supplement S7 (Historical preference), p. 53. Participant-level responses are unavailable; this is not Fresh C or baked-fidelity validation.|
|R2.1: generalizability of stages/control|Fresh C retrospective pairwise contrasts show within-cohort placement sensitivity; native conditioning interfaces test transfer boundaries without establishing common schedule effects.|Main Sections 4.2 and 4.5, pp. 5–6 and 9–11; Supplement S2–S4/S8. General stage roles or common-dose transfer are unestablished.|
|R2.2: heuristic three-stage novelty and boundaries|Prior schedules are explicitly credited; the contribution is reformulated as controlled task knowledge; universal scheduling and independent derivation claims are withdrawn.|Main Section 2.3; Main Section 3.3; Main Section 5, pp. 11–12. The methodological novelty concern remains unresolved.|
|R2.3: cohort overlaps and learned FAC reproducibility|Current cohort identities are separated from the historical 24/300 overlap and 276-request substitution; FAC negative results and identity gaps remain disclosed.|Main Table 1, p. 6; Main Section 4.6, p. 11; Supplement S1/S7. Source recovery and component checks do not verify historical training.|
|R3.1: large-cohort generic timing competitors|Fresh C includes Generic Linear and strong fixed controls; equal-applied-budget allocations test the preserved timing primary. Earlier generic-schedule studies remain separate historical/supporting evidence.|Main Table 2, p. 6; Main Section 4.2, pp. 5–6; Supplement S2/S7. These do not establish C3 superiority; the timing addendum is same-cohort, not a new holdout.|
|R3.2: retention-ratio aggregation order|The historical 26-object ratio display is no longer an active result because object IDs, selection and metric lineage are incomplete. Variation proxies are explicitly separated from fidelity.|Main Section 3.2, p. 3; Supplement S7, Supplement S7 (C3 Development Record), p. 52. We do not claim to have independently resolved the old mean-of-ratios versus ratio-of-means discrepancy.|
|R3.3: meaning of ± and paired/perceptual/bootstrap procedures|Current validated comparisons specify object pairing, resample counts, percentile intervals and sign-flip/correction families. Historical preference remains explicitly reported evidence.|Main Section 3.5, p. 5; Supplement S2/S7. The old perceptual aggregate is not silently promoted to a newly reproduced paired result; incomplete rows prevent replay of all historical statistics.|
|R3.4: dataset composition/selection/overlap, implementation and FAC parameters/training separation|Current cohort/source/protocol maps and recovered controller parameter/execution records are delivered; historical and current identities remain separate.|Main Table 1, p. 6; Supplement S1/S6/S7. Historical subset and training-run gaps are disclosed, not inferred from later configuration files.|
