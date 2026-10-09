# C&G 1008 R2.1 novelty and contribution audit

**Status: partial strengthening; R2.1 remains open.** This is a planning and
evidence report only. The sole body source remains
`1008/manuscript/source_01549/final_0903.tex` (SHA-256
`203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`). No
TeX was edited and no experiment was launched for this report.

## Strongest supportable contribution

The evidence supports TCAS/C3 as a **specific, training-free inference
schedule tested on the existing MVPainter geometry-residual path**. The
strongest scientific contribution is a bounded empirical characterization of
how the named adapter's scale, native caps, denoising-stage allocation, and
object-dependent image-space endpoints relate. It does not establish a new
general scheduling primitive, a dose-independent mechanism, or a universally
best schedule.

The new analysis improves the method motivation: the layer/window maps show
measurable response heterogeneity in the tested adapter, and the Fresh C
follow-up reports a positive C3-minus-GFL result on its primary image-space
endpoint. Those
findings do not rescue the original CAI optimality argument. Generic linear
and LLH produce material counter-results, and the A3b dose map has no common
support. The contribution therefore remains implementation-specific and may
be judged incremental for *Computers & Graphics*.

## Difference from prior work and from the original claim

| Method or evidence | Control signal and location | Training and schedule precedent | Task, baselines, and 3D endpoint | Applied-scale / residual evidence | Defensible difference here |
|---|---|---|---|---|---|
| MVPainter Geometry Adapter | Normal, depth, and foreground geometry are encoded and injected as residuals into UNet features. | The adapter is trained; its ordinary inference scale is not itself a new temporal scheduling method. | Geometry-conditioned multi-view texture generation with projection/baking. The base paper is the task and pipeline, not a controlled TCAS comparison. | The new Fresh C accounting records requested scale, native-cap application, and post-scale correction norms for this wrapper. | This study asks how inference-time strength behaves inside that already-existing residual path. It does not introduce a new generator or adapter. |
| Scheduled Style Injection (SSI) | Style strength is allocated across decoder/network layers and denoising time; the work also tests geometry-conditioned ControlNet scale scheduling. | Training-free; it directly establishes layer-by-time scheduling as prior art. | Primarily 2D style transfer, with broad schedule/configuration comparisons and checks across diffusion backbones; it does not validate this paper's baked texture endpoint. | Its control signal and execution path are not the MVPainter residual/cap wrapper measured here. | The task, signal semantics, and endpoint differ. They do **not** make a layer-by-time schedule or a two-axis control space novel. [Official CVF paper](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf). |
| Dynamic CFG / limited-interval guidance | Changes the weight between conditional and unconditional predictions, at the denoising-score level. | Training-free timestep guidance is established prior art; the submitted manuscript already cites limited-interval CFG. | Targets image guidance/diversity/fidelity, not a geometry-adapter residual in a multi-view 3D texturing pipeline. | Does not measure this adapter's applied per-layer scale or residual correction norm. | TCAS changes a different control signal. That mechanism distinction narrows the comparison; it does not establish scheduling novelty. |
| ControlNet / T2I-Adapter scale control | Scales condition-branch features or residual outputs. | Controllable condition strength is established; generic schedules are an obvious baseline family. | Broad conditional image generation; no assumption that a given scale schedule improves baked multi-view textures. | The wrapper-specific clipping and residual magnitudes here are not inferred from a nominal user scale. | C3 is one tested profile on the paper's adapter path, not a new general scale operator. |
| 01549 TCAS / C3 | A three-stage scale on the existing geometry-adapter residual. | No new weights or parameters; C3 is manually discretized as low-high-low. Stage scheduling has direct prior art. | Original probe and fixed-scale comparisons; the original text claims a broad transfer and texture advantage. | Original paper did not establish the present requested/applied/residual accounting. | Keep the TCAS name and C3 definition. Recast C3 as a **testable fixed schedule hypothesis**, not a derived optimum. |
| A2 / A3b / Fresh B / Fresh C | Controlled layer/window or profile changes on named adapter interfaces. | No new training for these controls; Fresh C is a revision-era follow-up, not a replication of the original preregistration. | Stronger same-cohort comparisons now include generic linear and LLH. N=20 baked results remain a separate, bounded endpoint. | The analyses explicitly expose caps and the absence of common dose support. | Adds implementation-specific empirical knowledge and more honest boundaries; it does not prove a general layer-time law or unique winner. |

### What is actually beyond ordinary schedule selection?

The evidence adds two bounded observations: (1) requested scale can be
clipped by native per-layer caps, and the logged correction norm depends on
both the residual and applied scale; and (2) response varies by layer,
denoising window, object, and endpoint under the tested interface. These are
useful measurements of this implementation. Because the comparisons do not
hold realized residual dose constant, they are not a dose-controlled causal
law. The schedule itself remains empirical.

## Evidence sequence and claim ceiling

### 1. Fixed scales motivate a trade-off, not a fidelity proxy

The original scale sweep and texture audits may motivate why a single scale
deserves study. Laplacian variance, RGB standard deviation, and gradient
magnitude measure image statistics; their increase is **not** by itself proof
of faithful texture or material appearance. Keep them as diagnostics and
pair them with PSNR/LPIPS, direct visual comparisons, and clear endpoint
labels.

### 2. Layer and denoising-window allocation changes responses, with dose limits

The A2 3×5 object-cluster analysis reports FG-LPIPS interaction
W(8)=481.081, p=8.04e-99, 43.5% interaction share, and 0.001695 cell RMSE;
FG-PSNR W(8)=1879.963, p<1e-300, 56.8% share, and 0.1222 dB cell RMSE.
A2 is exploratory. A3 is a higher-dose stress on the same cohort, not an
independent replication.

Fresh B A3b (N=150) reports Holm-adjusted object-cluster interaction
p=5.37e-43 for FG-LPIPS and p=3.43e-107 for FG-PSNR. The corresponding
interaction shares are 14.0% and 36.0%, with cell RMSE 0.000342 and 0.0205
dB. The required common support is **0/2,250 rows**; central 90% realized-dose
ranges do not overlap (deep 56,359–79,927; middle 11,421–19,336; shallow
2,816–5,193). The allowed wording is: “Within the tested primary adapter,
layer and denoising-stage interventions show measurable response
heterogeneity.” This is not evidence that C3 is optimal or that the
interaction is dose-independent.

### 3. Schedule profiles are not interchangeable with equal dose

On Fresh B, LLH and LFM-EXACT have the same requested per-layer time means.
LLH-minus-LFM-EXACT is +0.325 dB FG-PSNR [0.209, 0.446] and −0.00460
FG-LPIPS [−0.00563, −0.00357]. Those intervals fall within the protocol's
practical margins; this does not prove equality or isolate a dose-free
mechanism. LLH-minus-HLL is +0.687 dB FG-PSNR [0.404, 0.981] but only 45.3%
of objects favor LLH and the median is −0.104 dB; FG-LPIPS favors LLH on
80.7%. Registered LLH-minus-LLL is +0.734 dB FG-PSNR [0.597, 0.875]
(79.3% favor LLH) and −0.00845 FG-LPIPS [−0.01029, −0.00659] (82.0% favor
LLH); this comparison also changes requested intensity, so it does not isolate
timing. These are specific LLH profile comparisons, not evidence for C3.

The post-lock FRESH_CONFIRM_B generic-schedule extension is a same-cohort
sensitivity analysis, not an independent confirmation. In its locked paired
eight-schedule family, LLH had positive FG-PSNR and negative FG-LPIPS mean
differences against all four nominal-budget-matched schedules:

| LLH minus schedule (N=150) | FG-PSNR Δ [95% CI]; Holm p | FG-LPIPS Δ [95% CI]; Holm p | Favorable objects (PSNR / LPIPS) |
|---|---:|---:|---:|
| Budget-matched linear | +0.0967 [+0.0594, +0.1357]; ≤0.0008 | −0.0009 [−0.0013, −0.0004]; 0.0008 | 65.3% / 65.3% |
| Budget-matched cosine | +0.4629 [+0.3526, +0.5780]; ≤0.0008 | −0.0059 [−0.0071, −0.0046]; ≤0.0008 | 74.7% / 80.0% |
| Budget-matched trapezoid | +0.4404 [+0.3334, +0.5521]; ≤0.0008 | −0.0057 [−0.0070, −0.0045]; ≤0.0008 | 74.0% / 78.0% |
| Budget-matched Gaussian | +0.4711 [+0.3584, +0.5892]; ≤0.0008 | −0.0058 [−0.0071, −0.0045]; ≤0.0008 | 74.7% / 79.3% |

The endpoint-matched linear schedule is a counterexample to a broad LLH
advantage: LLH-minus-linear FG-PSNR is −0.0373 dB [−0.0829, +0.0086]
(Holm p=0.1150), while FG-LPIPS is +0.0011 [+0.0004, +0.0019]
(Holm p=0.0024), favoring linear on LPIPS. Nominal per-layer means were
matched for the four budget-matched profiles, but their mean integrated
post-scale correction norms were still about 0.5%–2.1% above LLH. No cap
activated in this extension. A post-outcome pairwise common-support analysis
did not find any of the four budget-matched conditional contrasts significant
after its eight-slot Holm correction; its intervals were wide. Thus the raw
profile comparisons do not identify a schedule-shape effect independent of
realized dose, and they do not strengthen C3 specifically.

The Fresh C accounting defines applied scale as the requested value after
native-cap clipping; the recorded correction norm is downstream of that
scale. For example, the shallow C3 request of 1.25 is applied as 0.8 at the
cap. A scalar sum or requested mean is not an independent measure of realized
dose. The LLH-versus-generic-linear comparison likewise does not constitute
an exact realized-dose match.

### 4. Fresh C supports one advantage and several counter-results

Fresh C is a frozen revision-era N=300 image-space follow-up. Its four
conditions passed 1,200/1,200 rows; the separate LLH/linear addendum passed
600/600 rows on that cohort. Paired object-level results are:

| Contrast and endpoint | Mean difference (A−B), 95% object-bootstrap CI | Object distribution | Interpretation |
|---|---:|---:|---|
| C3−GFL FG-PSNR | +0.522 dB [0.404, 0.641] | 68.7% favor C3 | Registered positive primary result for this image-space endpoint. |
| C3−GFL FG-LPIPS | −0.005345 [−0.006326, −0.004403] | 71.0% favor C3 | Secondary endpoint favors C3. |
| C3−generic-linear FG-PSNR | −0.593 dB [−0.837, −0.351] | Median +0.074 dB; 51.7% favor C3 | Mean favors generic linear; object distribution is heterogeneous. |
| C3−generic-linear FG-LPIPS | +0.013512 [0.011601, 0.015487] | 74.3% favor generic linear | Clear counter-result to a unique C3-winner claim. |
| LLH−C3 FG-PSNR | +0.621 dB [0.391, 0.855] | Median −0.153 dB; 46.7% favor LLH | Positive mean is not a typical-object result. |
| LLH−C3 FG-LPIPS | −0.012140 [−0.013861, −0.010480] | 75.0% favor LLH | LLH is a competitive alternative. |
| LLH−generic-linear FG-PSNR | +0.028 dB [−0.015, 0.070] | 52.3% favor LLH | No difference detected; not equivalence or non-inferiority. |
| LLH−generic-linear FG-LPIPS | +0.001372 [0.000762, 0.002081] | 53.3% favor linear | LPIPS favors generic linear; Holm p=0.000114. |

Fresh C therefore supports a C3-versus-GFL result, **not** universal
optimality. The addendum is a separate analysis on the same cohort, not a new
independent replication. Keep the negative generic-linear result and LLH
trade-off in the main results where readers can see them.

## Surgical manuscript map (proposal only)

| 01549 source location | Existing claim to address | Proposed local action | Evidence and boundary |
|---|---|---|---|
| Abstract, p.1 / l.33 | CAI-derived schedule, +0.96 dB, broad texture and human-preference advantage, and architecture-family implication. | `REPLACE_EVIDENCE`: retain TCAS/C3; summarize C3−GFL image-space result and the Generic Linear/LLH counter-results; call the evidence a revision-era follow-up and state the task-specific scope. Remove the optimality, human-superiority, and broad-transfer language. | Fresh C primary and addendum analyses; claim ceiling; human results remain restricted to the original conditions. |
| Introduction, §1 / ll.54–70 | Strong causal/mechanistic wording, broad “not solved” framing, and “only promising” contribution language. | `LOCAL_REWRITE`: retain the problem and paper identity; state a tested hypothesis and distinguish diagnostics from fidelity. Recast contributions as a controlled evaluation of the existing adapter path and measured endpoint boundaries. | A2/A3b heterogeneity with dose limits; Fresh C positive and negative results. |
| Related Work, §2.3 / ll.89–96 | Schedule comparison understates direct layer/time prior art. | `LOCAL_REWRITE`: cite SSI directly and acknowledge that layer-by-time allocation is established. Keep the distinction between CFG score extrapolation and geometry-adapter residual scaling. | SSI official paper; existing CFG/ControlNet/T2I references. |
| Method, §3.2 / ll.139–153 | Stage roles are stated as deterministic facts. | `LOCAL_REWRITE`: retain the TCAS name, exact `s(p)` equation, and C3=(1.25, 2.50, 1.25); describe low-high-low as an adapter-specific, testable inference hypothesis. | Existing schedule definition; new response maps support heterogeneity only. |
| Method, CAI paragraph / ll.154–172 | Proposition/proof and finite-difference claims assert a post-hoc selection rule and C3 optimality. | `REMOVE` the proof as a selector/optimality claim; if retained for record, move only its descriptive measurements to a clearly labeled historical note. Do not replace it with a new theory. | A2/A3b do not identify a dose-independent mechanism; direct Fresh C comparisons show non-unique winners. |
| Results, Fig. 4 / ll.270–286 | Scale-related local texture illustration and 26-object audit are presented as broad visual proof. | Preserve the figure's local-comparison role; use same-object, same-view, licensed Fresh C candidate material and a caption that says it is illustrative. Keep texture diagnostics as proxies. | Rights-cleared 20-object Fresh C gallery; no population inference from selected panels. |
| Results, probe / Fig. 6 / ll.290–331 | “Only promising,” C3 shape/texture optimality, and confident stage-mechanism text. | `REPLACE_EVIDENCE` in the prose/table claims; preserve the original figure's purpose of comparing schedules. Report the measured scope and point readers to the 300-object primary/negative comparator table. | A2/A3b; Fresh B; Fresh C; no optimality inference. |
| Main comparison, §5 / ll.368–456 | Original pooled 300 results, variation-as-fidelity wording, and CLIP-IQA perceptual language. | Replace headline comparisons with the frozen Fresh C result table. Retain endpoint names and adverse comparator results. Do not call PSNR/LPIPS or variation metrics human-perceived material fidelity. | Fresh C analysis, addendum, gates, and requested/applied/residual accounting. |
| Human preference, §5 / ll.458–480 | The original three-condition 3AFC is used to claim a new general preference advantage. | Remove the broad advantage claim. Any retained 3AFC result must be limited to its original objects, methods, and question; it cannot support LLH, generic linear, unseen-view, or 3D claims. | Original 01549 experiment only; no new preference claim is supported here. |
| FAC and adapter-dependence / ll.482–526 | FAC expansion and “C3 best in every regime” broaden the paper and imply transfer. | Retain the 01549-reported negative FAC re-examination as auxiliary first-round evidence with its provenance limits; do not present FAC as part of TCAS or as a new 1008 run. Narrow adapter tests to their stated within-family/interface scope. | Current author instruction preserves the recognized first-round FAC re-examination; cross-interface analyses remain limited and mixed. |
| Limitations and Conclusion / ll.532–550 | C3 is called best among all tested variants and likely robust beyond the pipeline. | `LOCAL_REWRITE`: add the Generic Linear/LLH trade-offs, N=20 mixed unseen-view endpoints, and the unverified seam/PBR boundary. Conclude with the tested strategy and its scope, not a universal rule. | Fresh C, N=20 native GLB, seam disposition, and R1 blocker report. |

The title, TCAS name, base pipeline, section order, three-stage definition,
and existing figure purposes can remain. This proposal does not adopt the
1007/L-TCAS structure or move the argument wholesale into supplementary
material. The previous page-by-page action register is
[`01549_FIRST_SURGICAL_REVIEW_20261008.md`](01549_FIRST_SURGICAL_REVIEW_20261008.md).

## Proposed response to Reviewer 2.1 (not filed)

> We thank the reviewer for questioning whether a manually discretized
> three-stage schedule constitutes sufficient methodological novelty. We
> re-examined this point against prior work and will cite Scheduled Style
> Injection directly. SSI already studies layer- and timestep-dependent
> injection strength, including geometry-conditioned ControlNet scales; we
> therefore no longer describe layer-by-time scheduling as a new control
> space or claim that TCAS is a generally new scheduling primitive.
>
> We retain TCAS and the fixed C3 profile as a low-cost, training-free
> inference strategy for the existing MVPainter geometry-residual path. The
> revision will state its low-high-low form as a testable, adapter-specific
> hypothesis. The A2 and Fresh B layer/window analyses detect response
> heterogeneity, but the A3b realized-dose ranges have no common support, so
> we do not treat them as proof of a dose-independent law or of C3
> optimality. We also report that Fresh C supports C3 over GFL on the
> primary FG-PSNR endpoint in a revision-era follow-up while generic linear
> is stronger than C3 on the mean FG-PSNR and FG-LPIPS comparisons, and LLH
> is competitive on other endpoints. The separate Fresh B LLH and
> budget-matched generic-schedule results are identified as LLH comparisons,
> not C3 evidence. These counter-results are kept with the main comparisons.
>
> We have consequently narrowed the contribution to a controlled empirical
> characterization of this adapter path, including native-cap/applied-scale
> accounting and endpoint- and object-dependent results. We recognize that
> the significance of this task-specific empirical contribution for the
> journal remains an editorial judgment; we do not claim that the evidence
> closes that question automatically.

## Source provenance

Byte-identical source reports, paired analyses, cohort/gate files, and
requested/applied/residual accounting are copied under
[`source_evidence/r2`](source_evidence/r2/). Their original paths and hashes
are in [`R2_SOURCE_EVIDENCE_MANIFEST.csv`](R2_SOURCE_EVIDENCE_MANIFEST.csv).
This includes the Fresh B profile and generic-schedule reports, paired
object-level summaries, integrity records, and the analysis scripts and CSV
needed to audit those comparisons.
The 01549 base hash is recorded above. Fresh C primary analysis SHA-256:
`fd5422de055dfde6f82d65091f1cfcec26823a7757a1e09c76a4067984d5cd58`;
Fresh C addendum analysis SHA-256:
`8dc691c7533cf30d0368f35f1851f15b9049e8b587d5c39509583ccb2be58a8c`;
Fresh C requested/applied/residual accounting SHA-256:
`dc0f03ce9164c3b66558ed21e6362406a68cffd0dd663b87768edcb18e74a8a1`.

**Gate:** `R2_NOVELTY_STRENGTH=PARTIAL`; `R2_1_VENUE_RISK=OPEN`.
