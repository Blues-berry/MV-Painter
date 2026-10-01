# 01549-based Manuscript Narrative Redefinition and Audit-Contingent Decision Report

**Date:** 2026-10-01  
**Target manuscript baseline:** `CAG-S-26-01549`  
**Evidence branch:** `codex/round2-evidence-integrated-20261001`  
**Evidence snapshot reviewed:** `9388b83`  
**Purpose:** define the next manuscript narrative before editing the paper, maximize direct coverage of the current Reviewer 1 / Reviewer 2 concerns, and predefine safe narrative branches for audit outcomes that are not yet fully converged.  
**Status:** planning / release-gate document only. This report does **not** authorize any unsupported claim and does **not** itself modify `final_round2.tex`, the supplement, or the response letter.

---

## 1. Executive decision

The 01549 manuscript should **not** be revised by simply appending the new experiments to the old C3/CAI story. The current evidence changes the scientific object of the paper.

The 01549 version is centered on a scalar, time-only control

[
h'_t=h_t+s(p_t)A_phi(h_t,G),
]

with C3=((1.25,2.50,1.25)) presented as the main TCAS configuration and CAI presented as a formal route to the low-high-low schedule. This framing is precisely where Reviewer 2 remains unconvinced: it reads as a manually discretized three-stage schedule selected for one adapter family, while CAI appears post-hoc.

The recommended revision should instead make the **adapter residual allocation surface over network depth and denoising stage** the object of study. The most conservative mathematically complete definition is

[
h'_{l,t}=h_{l,t}+s_{l,k(t)}A_l(h_{l,t},G),
]

where (l) indexes adapter injection depth groups and (k(t)) indexes denoising stages. The collection

[
S=[s_{l,k}]in mathbb{R}_{+}^{L	imes K}
]

is the inference-time residual allocation matrix.

This definition yields four useful special cases without inventing a new mechanism:

- **global fixed scale:** (s_{l,k}=c);
- **shared-layer temporal TCAS:** (s_{l,k}=s_k), which contains the 01549 C3 schedule;
- **layer-only redistribution:** (s_{l,k}=a_l);
- **layer-wise stage-aware scaling:** both (l) and (k) vary.

The scientific question therefore becomes:

> **Where in the network, and when in denoising, should a frozen geometry-adapter residual be allocated?**

This reframing preserves the original topic and inference-time/training-free character of TCAS, but it is materially broader than “choose C3.” It also matches the strongest new experiments: same-runner Core-7, layer-fixed controls, layer-LHL / layer-LLH, the complete temporal-pattern development ablation, MV-Adapter layer-wise transfer, mapping sensitivity, and the MVDiffusion failure boundary.

### Recommended identity of the method

**Preferred manuscript name:** **Layer-wise Timestep-Conditioned Adapter Scaling (L-TCAS)**.

The original TCAS remains a shared-layer special case rather than being erased. This minimizes revision discontinuity while making the methodological expansion explicit.

**Preferred title if the editor permits a title refinement:**

> **Layer-wise Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation**

This is preferable to a completely new name such as “Factorized Residual Allocation,” because an aggressive renaming risks making the revision look like a different paper created after review.

A conservative fallback is to retain the 01549 title and introduce L-TCAS inside the paper as the generalized formulation.

---

## 2. Why the 01549 narrative must change

### 2.1 What should remain from 01549

The following core problem statement remains valid and should be preserved:

- adapter scale is an inference-time control variable rather than a trivial hyperparameter;
- aggressive residual injection can improve some structural metrics while degrading appearance fidelity;
- geometry-adapter scaling differs mechanistically from CFG score extrapolation;
- the method is training-free and does not modify the frozen UNet/VAE/adapter weights;
- the paper is a controlled study of an inference mechanism, not a new end-to-end texturing system.

### 2.2 What must be retired from 01549

The following statements should no longer be paper-facing claims:

1. **The historical +0.96 dB result.** It must not appear in the abstract, introduction, tables, cover letter, conclusion, or response letter. The active evidence is the frozen same-runner strict-276 matrix.
2. **“C3 is the main/optimal schedule.”** C3 becomes a shared-layer temporal baseline/special case.
3. **“CAI derives/selects the schedule.”** CAI becomes a descriptive diagnostic only.
4. **“A CI crossing zero establishes equivalence/non-inferiority.”** Replace with “no detected difference under this test” unless a pre-specified non-inferiority margin exists.
5. **Texture variation equals texture fidelity.** Laplacian/gradient/RGB/HF magnitudes are variation descriptors; fidelity requires GT-relative or perceptual/color-error evidence.
6. **Universal or all-backbone generalization.** The current cross-backbone evidence is explicitly bounded.
7. **The 300-object pooled evaluation as the primary confirmation set.** The primary confirmation set is the probe-disjoint strict 276-object cohort.
8. **Human preference as headline evidence for the final layer-wise method.** The existing preference study evaluates the earlier shared-layer conditions. It may remain as scoped secondary evidence or move to the supplement, but it must not be used as validation of layer-LLH/L-TCAS.
9. **FAC as a parallel methodological contribution.** FAC is a negative learned-extension study; it should not compete with the main method in the contribution list.

---

## 3. Recommended conceptual hierarchy

The final paper should have one clear causal/evidential hierarchy.

### Level A — Problem

A single scalar adapter scale conflates two control dimensions:

- **where:** which network depth receives residual strength;
- **when:** which denoising stage receives residual strength.

This is the methodological gap.

### Level B — Formulation

Define (S=[s_{l,k}]) as a layer × stage residual allocation matrix. Do not claim that the matrix is learned or universally optimal. It is a training-free inference control surface over a frozen adapter.

### Level C — Controlled decomposition

Use paired shared-input experiments to separate:

- layer redistribution;
- temporal placement;
- their interaction.

The contribution is not a claim that one symbolic schedule is universally optimal. It is the controlled decomposition and the evidence that these axes behave differently.

### Level D — Primary confirmation

Use the **strict-276 same-runner Core-7 matrix** as the primary quantitative table. This table directly answers Reviewer 1’s baseline and protocol concerns.

The paper should emphasize the primary fidelity surfaces on which layer-LLH is strongest, while explicitly reporting the reverse cells:

- no-adapter can score best on FG-SSIM because blur/smoothing can inflate structural similarity;
- global-fixed-high can retain small advantages on Full-LPIPS / Edge-SSIM;
- therefore the method is a fidelity trade-off, not metric domination.

### Level E — Mechanistic interpretation

Use the new GT-relative texture diagnostics to explain why raw SSIM or raw high-frequency variation can be misleading.

CAI belongs here as an **interpretive diagnostic**, not as the derivation of the method.

### Level F — Transfer and applicability boundary

- **MV-Adapter:** layer redistribution transfers on selected fidelity/texture metrics; temporal placement is not consistently separated; SSIM can reverse; LPIPS may be non-significant.
- **MVDiffusion:** the layer-wise benefit does not replicate under the non-isomorphic CPBlock interface; preserve this as negative boundary evidence.

This is a stronger scientific story than forcing a universal replication.

### Level G — 3D practical evidence

Use the 12-object stratified baking study as a **case study**, not population inference.

- UV seam ΔE00 can be described as a direct texture-space seam discontinuity descriptor if the final audit keeps the current implementation.
- the cross-view metric should be called a **render-time cross-view color stability descriptor**, not a direct texture-fidelity metric, because the current implementation uses vertex-colored rendering.

---

## 4. Method-definition changes from 01549

### 4.1 Section 3.1 — replace scalar-only injection with layer-indexed injection

01549 currently introduces the scalar form first and makes the entire method temporal. The revised paper should introduce the general layer-indexed form immediately:

[
mathbf h'_{l,t}
=
mathbf h_{l,t}
+
	ilde s_{l}(p_t)
A_l(mathbf h_{l,t},mathbf G),
]

where (	ilde s_l) is the effective residual multiplier at depth group (l).

If the implementation uses per-group caps, define them separately as an implementation semantic:

[
	ilde s_l(p_t)=min(s_l(p_t),c_l).
]

Do **not** present the cap values as a universal property of L-TCAS; they are properties of the evaluated adapter implementation.

### 4.2 Add an explicit allocation-matrix definition

For three depth groups and three denoising stages,

[
S=
egin{bmatrix}
s_{	ext{deep},e} & s_{	ext{deep},m} & s_{	ext{deep},l}\
s_{	ext{mid},e} & s_{	ext{mid},m} & s_{	ext{mid},l}\
s_{	ext{shallow},e} & s_{	ext{shallow},m} & s_{	ext{shallow},l}
end{bmatrix}.
]

This single definition makes the novelty legible. It allows the reader to see that “global fixed,” “TCAS/C3,” “layer-fixed,” “layer-LHL,” and “layer-LLH” are all points/subfamilies in the same control space.

### 4.3 Redefine TCAS as a special case

The old C3 schedule is:

[
s_e=1.25,quad s_m=2.50,quad s_l=1.25.
]

In the new notation it is a shared-layer row-constant specialization:

[
s_{l,k}=s_kquad orall l.
]

This preserves continuity with 01549 while preventing the paper from being trapped by the claim that C3 itself is the main novelty.

### 4.4 Define the two experimental axes, not an “optimal schedule”

The paper should explicitly state:

- **depth redistribution axis:** change (s_l) while controlling the temporal aggregate;
- **temporal placement axis:** change the stage assignment while controlling the layer profile/budget;
- **full allocation:** allow both to vary.

Where equal-budget controls exist, say exactly how the budget is matched. Do not generalize a budget-normalization rule to experiments that did not use it.

### 4.5 CAI: remove theorem-like authority

The 01549 “Proposition 1 / guardrailed epsilon-optimal selector” framing is now too strong. Reviewer 2’s criticism is correct: the current evidence shows that CAI is not an independent derivation of a unique schedule.

Recommended main-text role:

> CAI summarizes stage-specific correction/alignment/interference tendencies observed under a fixed adapter regime. It is used to interpret why a stage placement may help or hurt, not to guarantee a unique schedule.

The theorem/proof/epsilon-selection machinery should either be removed or moved to the supplement as a historical diagnostic formulation with explicit limitations. CAI should not appear in the contribution bullets.

---

## 5. Recommended title / naming choices

### Option A — Conservative continuity

**Title:** keep “Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation.”

**Method wording:** “we generalize TCAS to a layer-indexed scale (s_l(p)).”

**Advantages:** minimal editorial drift, clear continuity with 01549.

**Risk:** Reviewer 2 may still perceive the paper as schedule selection with an extra ablation.

### Option B — Recommended

**Title:** “Layer-wise Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation.”

**Method name:** L-TCAS; original TCAS/C3 is the shared-layer special case.

**Advantages:** directly reflects the actual methodological object; strengthens the response to novelty without pretending the paper is a new system; preserves lineage.

**Risk:** requires careful explanation in the response letter that this is a formal generalization prompted by the reviewer’s methodological concern, not post-hoc renaming.

### Option C — Aggressive reframing

**Title:** “Factorized Layer–Time Residual Allocation for Geometry-Controlled Multi-view Diffusion Texturing.”

**Advantages:** strongest novelty framing.

**Risk:** highest chance that reviewers/editors perceive the revision as a different paper; not recommended unless the final audits produce much broader cross-backbone evidence.

**Recommendation: Option B.**

---

## 6. Section-by-section rewrite plan from 01549

### Abstract

The 01549 abstract should be rewritten completely. It currently over-centers C3, CAI derivation, +0.96 dB, the pooled 300-object result, and preference evidence.

Recommended abstract logic:

1. problem: a global adapter scale conflates depth and denoising-stage control;
2. formulation: layer-wise timestep-conditioned residual allocation (s_l(p));
3. evidence: shared-input decomposition + strict-276 same-runner confirmation against unmodified and competitive fixed-scale baselines;
4. metric nuance: primary fidelity gains coexist with explicit SSIM/perceptual trade-offs;
5. transfer: layer redistribution partially transfers to MV-Adapter, temporal placement does not consistently transfer, MVDiffusion defines a negative boundary;
6. practical case study: texture-fidelity and 3D baking/seam evidence;
7. scope: no universal schedule claim.

A safe abstract sentence template is:

> We formulate adapter scaling as a layer-by-stage residual allocation problem rather than a single global magnitude. On a pre-registered 276-object strict holdout, the selected layer-wise allocation improves the primary reference-fidelity metrics over both the unmodified pipeline and competitive fixed-scale controls under the same runner and shared inputs, while several structural/perceptual metrics retain trade-offs. Cross-backbone experiments show that layer redistribution transfers to one additional adapter architecture but temporal placement is architecture-dependent, and a third non-isomorphic control interface provides a negative applicability boundary.

Do not insert exact “best of seven” language until the final release gate confirms every table/metric presentation convention.

### Introduction

Keep the first part of the 01549 problem setup, but replace the “when should residuals dominate?” question with:

> the adapter scale is not a single scalar decision: residuals enter at multiple network depths and denoising stages, so global scaling conflates **where** and **when** control should act.

The novelty paragraph should explicitly distinguish this paper from CFG scheduling:

- CFG: score extrapolation over time;
- conventional adapter scale: one residual magnitude;
- this paper: residual allocation over **depth × time**.

### Contributions

Recommended four contributions:

1. **Problem / measurement:** identify the shape–texture/reference-fidelity trade-off and show why structural metrics and texture-variation metrics alone are insufficient.
2. **Formulation:** formulate a training-free layer × timestep adapter residual allocation control (S=[s_{l,k}]), with TCAS/C3 as a shared-layer special case.
3. **Causal experimental decomposition + strict confirmation:** separate layer redistribution and temporal placement with shared-input paired controls, then confirm the development-selected configuration on the strict-276 same-runner Core-7 protocol.
4. **Transfer/boundary/practical evidence:** evaluate one additional adapter architecture, preserve the negative MVDiffusion result, and provide bounded 3D baking/seam evidence.

Do not list CAI as a contribution.

### Related Work

Retain the 01549 CFG-vs-adapter distinction, but add a sharper novelty sentence:

> Prior scheduling work primarily varies control strength along the denoising trajectory. Our formulation additionally treats network depth as an independent inference-time allocation axis and experimentally separates depth redistribution from temporal placement.

Do not claim no prior work ever varies layer scales unless a literature audit verifies it.

### Method

Recommended order:

- 3.1 Base pipeline and residual injection;
- 3.2 Layer × timestep residual allocation matrix;
- 3.3 L-TCAS specializations and implementation semantics;
- 3.4 Evaluation dimensions / shape-texture diagnostics;
- 3.5 CAI as descriptive stage-utility interpretation;
- optional FAC moved out of the main method or reduced to one paragraph with full detail in supplement.

### Experimental Setup

Make the evidence hierarchy explicit:

- **development:** 24-object / multi-seed paired ablations;
- **primary confirmation:** strict 276, pre-registered, same runner/shared-input;
- **robustness:** R0/R1 independent realization sets;
- **transfer:** MV-Adapter and MVDiffusion;
- **practical case study:** 12-object baking.

This hierarchy is much more defensible than the 01549 “300-object pooled evaluation” emphasis.

### Main results

The first main quantitative table should be Core-7, not the old pooled C3 table.

Core-7 should include all seven conditions under one protocol:

- no_adapter;
- global_fixed_low;
- global_fixed_high;
- global_c3;
- layer_fixed_mean;
- layer_lhl;
- layer_llh.

The text should state both the primary gains and the reverse cells. Never summarize the table as “dominates all metrics.”

### Texture-fidelity section

Replace raw “more texture = better” logic with distance-to-GT framing.

Recommended hierarchy:

- CIEDE2000 / masked perceptual/reference-fidelity metrics;
- GT-relative gradient/Laplacian/RGB-std/HF errors;
- raw variation metrics only as diagnostics.

Explicitly state that high-frequency energy can represent detail **or** artifact.

### Robustness / reproducibility

Include:

- pre-registration/frozen protocols;
- object-level paired bootstrap;
- R0/R1 result stability;
- metric-direction convention;
- hash/manifests;
- exclusion of the historical archived LHL record from active quantitative evidence.

Do not try to explain an unreconstructible historical record more strongly than the final provenance audit permits.

### Cross-backbone section

This section should be titled around **transferability and applicability boundary**, not “generalization.”

Recommended structure:

1. MV-Adapter interface and identity gate;
2. layer-wise vs global paired panel;
3. mapping sensitivity;
4. temporal placement non-separation;
5. MVDiffusion non-isomorphic interface and negative result.

This directly answers Reviewer 2 without overclaiming.

### 3D baking section

Use a case-study label in the section title or first sentence.

State:

- 12 stratified objects;
- same-draw controls where applicable;
- textured GLB + unseen-view renders;
- UV seam ΔE00;
- cross-view **render-time stability** descriptor;
- no population inference / no “seam-free” claim.

### FAC

FAC should be demoted. The most acceptance-friendly structure is:

- one short main-text paragraph: learned modulation was re-examined and did not outperform the training-free method under strict paired/disjoint controls;
- training details and dose-response table in Supplement.

This retains the transparency appreciated by Reviewer 2 without diluting the new main story.

### Limitations

The new limitations should explicitly state:

- no universal optimal matrix/schedule;
- layer and temporal effects are architecture/interface dependent;
- MV-Adapter transfer is metric-dependent;
- MVDiffusion is a negative boundary;
- mapping robustness is limited to the tested partition family and budget convention;
- 3D baking evidence is a 12-object case study;
- texture descriptors do not replace human/material-aware assessment.

### Conclusion

The conclusion should not end with C3.

Preferred final message:

> A geometry adapter should not be treated as having one inference-time strength. Its residuals can be allocated differently across network depth and denoising time. On the primary pipeline, layer-aware allocation materially improves reference fidelity under a strict same-runner holdout; across other interfaces, the layer and temporal components transfer differently. This establishes residual allocation as a useful inference control and also defines its architecture-dependent limits.

---

## 7. Reviewer 1 response-maximization plan

### R1.1 Full-object quality / unmodified pipeline / fixed baseline / bake / unseen views / seams

Use the Core-7 no-adapter + fixed-high controls for the requested baselines, and add full-object qualitative panels selected by a **predefined stratification rule**, not success-only examples.

For 3D evidence:

- show the whole 12-object cohort in the supplement;
- include unseen viewpoints;
- use UV seam ΔE00 as the direct seam descriptor if the audit remains valid;
- call the cross-view value a render-time stability descriptor.

Do not claim a broad population-level 3D quality improvement.

### R1.2 Same held-out protocol for the main adapter

This is now answered primarily by Core-7.

The response letter should explicitly say that the prior +0.96 dB pooled result is retired and **replaced** by the strict-276 same-runner comparison. This is stronger than trying to rescue the old number.

### R1.3 Texture variation versus fidelity

Lead with the GT-relative diagnostics and CIEDE2000, not raw Laplacian/gradient magnitude.

Use the raw variation descriptors only to interpret blur/overshoot.

### R1.4 CI crossing zero / Edge-SSIM trade-off

Use the phrase **“no detected difference”**, not equivalence.

Report the reverse cells openly. This should be presented as evidence that the paper no longer optimizes one structural metric at the expense of honest reporting.

### R1.5 Reproducibility / FAC code

The strongest response is a release package containing:

- evaluation scripts;
- protocol files;
- per-object records;
- hash manifests;
- analysis scripts;
- FAC training/evaluation configuration.

If double-anonymous review prevents a normal GitHub URL, prepare an anonymized archive/repository snapshot. A request-only availability statement is defensible but weaker than the reviewer’s explicit encouragement to release code.

---

## 8. Reviewer 2 response-maximization plan

### R2.1 “Contribution is only schedule selection”

Do not answer this with more C3 experiments. Answer by changing the formal object of study.

Core response:

> We agree that the previous scalar TCAS presentation read as schedule selection. The revised formulation exposes the adapter residual scale as a two-dimensional inference control over network depth and denoising stage, and the experiments separately identify the effect of depth redistribution, temporal placement, and their interaction.

Then point to layer-fixed controls, temporal factorial, Core-7, and strict confirmation.

### R2.2 “CAI is post-hoc”

Agree and narrow.

Do not defend CAI as a derivation. State that it is an empirical diagnostic retained for interpretation, while method selection is supported by the pre-registered development/confirmation protocol.

This is more credible than trying to win an argument the new data no longer supports.

### R2.3 “Cross-backbone validation is missing”

Answer with the full bounded evidence:

- MV-Adapter is a genuine additional adapter architecture;
- layer-wise transfer is supported on selected metrics;
- temporal placement is not consistently supported;
- mapping sensitivity tests whether the result depends on one arbitrary partition;
- MVDiffusion is explicitly negative under its non-isomorphic interface.

The response should emphasize that the revision **did not search until every backbone became positive**. The negative result defines the applicability boundary.

---

## 9. Audit-contingent narrative decision tree

The manuscript should not wait until all audits finish to define its logic. Instead, use the following predeclared branches.

### Scenario A — mapping audit remains strongly stable

Condition:

- all reasonable budget-neutral contiguous mappings are bitwise/statistically consistent;
- M3, if validly comparable, does not reverse the central layer-redistribution conclusion.

Allowed wording:

> “The MV-Adapter layer-redistribution effect is robust across the tested contiguous mapping choices.”

Still avoid “mapping invariant” unless every tested mapping has matched budget and no important metric reverses.

### Scenario B — M3 differs because it changes total residual budget

Condition:

- budget-neutral B′/C are stable;
- M3 diverges and its mean/budget differs.

Allowed wording:

> “The transfer is robust to budget-neutral repartitioning but sensitive when repartitioning also changes the total residual budget.”

This outcome actually strengthens the mechanistic story by separating **partition** from **budget**.

### Scenario C — a defensible equal-budget mapping reverses the MV-Adapter result

Allowed wording:

> “Layer redistribution transfers to MV-Adapter only under specific mappings; the effect is mapping-dependent.”

Do not use mapping robustness as a reviewer defense. Retain MV-Adapter as partial transfer evidence, not a generalization result.

### Scenario D — archived LHL root cause remains unreconstructible

Use the Case-B sentence only:

> “The historical record is excluded from quantitative claims because complete execution provenance cannot be guaranteed.”

Do not name an unproven runtime mechanism.

### Scenario E — archived LHL root cause is later identified conclusively

Only then state the exact mechanism, with a reproducible discriminating experiment and hashes. The historical number should still remain outside the main evidence unless it is re-generated under the frozen protocol.

### Scenario F — seam audit survives final technical review

Use:

> “On the 12-object case study, layer-LLH shows the lowest absolute UV-seam color discontinuity among the tested variants.”

Keep the descriptive scope.

### Scenario G — seam/cross-view audit is found implementation-sensitive

Drop the scalar seam/cross-view claim entirely. Retain:

- textured GLB exports;
- full cohort contact sheet;
- unseen-view qualitative renders;
- explicit limitation.

Do not delay the whole paper for this secondary case-study metric.

### Scenario H — Core-7/statistics audit finds a direction or protocol defect

This is a **hard stop**. No manuscript freeze is permitted until all primary tables are recomputed from frozen per-object records. The narrative must never be used to paper over a primary-evidence defect.

---

## 10. Three complete paper narratives to choose from after audit convergence

### Narrative N1 — Recommended / bounded mechanism study

Use when Core-7 passes, MV-Adapter layer-wise transfer remains positive/mixed, and MVDiffusion remains negative.

**Story:** adapter residual strength is a 2D layer × stage control; layer redistribution is strongly useful on the main pipeline and partially transferable, while temporal placement is architecture-dependent.

This is the current recommended route.

### Narrative N2 — Main-pipeline method + transfer boundary

Use if mapping sensitivity weakens MV-Adapter substantially.

**Story:** L-TCAS is strongly validated on the main pipeline under strict holdout; additional backbones reveal that transfer depends on interface/mapping semantics.

This is still publishable because Reviewer 2 explicitly asked for cross-backbone evidence, not necessarily positive replication.

### Narrative N3 — Conservative TCAS revision

Use only if a later audit invalidates the layer-wise cross-backbone story or the method definition cannot be cleanly reproduced.

**Story:** keep the original TCAS title and treat layer-wise experiments as a mechanistic ablation/extension; focus the paper on strict-276 protocol correction, metric fidelity, and bounded stage effects.

This has the lowest method-drift risk but the highest residual novelty risk with Reviewer 2.

---

## 11. Recommended main-paper evidence allocation

### Main paper

Prioritize:

1. residual-allocation formulation;
2. strict-276 Core-7 table;
3. layer/time decomposition;
4. one compact texture-fidelity table;
5. one robustness summary;
6. MV-Adapter transfer + mapping sensitivity;
7. MVDiffusion boundary;
8. concise 3D bake case-study figure/table.

### Supplement

Move or keep:

- full temporal factorial;
- full per-metric paired CIs/win rates;
- R0/R1 tables;
- full texture diagnostics;
- all 12 bake objects/contact sheet;
- full mapping sensitivity;
- FAC details and negative dose-response;
- hash/provenance manifests;
- historical-record exclusion audit;
- detailed protocol locks.

This prevents the main paper from becoming an audit log.

---

## 12. Recommended abstract draft skeleton

The final numbers should be inserted only after the release gate, but the prose structure can be frozen now:

> Geometry-conditioned multi-view diffusion pipelines typically control adapter residuals with a single inference-time scale, even though the residuals enter at multiple network depths and denoising stages. We formulate adapter scaling as a layer-by-stage residual allocation problem and introduce a training-free layer-wise timestep-conditioned control that assigns stage-dependent multipliers to depth-specific residual groups without modifying model weights. Controlled shared-input ablations separate depth redistribution from temporal placement, and a pre-registered 276-object strict holdout evaluates the selected allocation together with the unmodified pipeline and competitive fixed/global controls under the same runner. The layer-wise allocation improves the primary reference-fidelity metrics while retaining explicit metric-dependent trade-offs, and GT-relative texture diagnostics distinguish faithful detail from high-frequency artifacts. On MV-Adapter, the layer-redistribution effect transfers on selected fidelity/texture metrics whereas temporal placement is not consistently separated; on a non-isomorphic MVDiffusion control interface the benefit does not replicate, defining an architecture-dependent applicability boundary. A stratified 3D baking case study further evaluates unseen-view and seam/stability behavior. These results support adapter residual allocation as a useful training-free inference control, while rejecting a universal schedule claim.

---

## 13. Recommended contribution bullets draft

> **(1)** We identify adapter residual allocation as a distinct inference-time control problem in geometry-conditioned multi-view texturing and show why structural scores and raw texture variation alone can misrepresent reference fidelity.

> **(2)** We formulate layer-wise timestep-conditioned adapter scaling as a depth × denoising-stage residual allocation matrix, with no additional training or network forward; conventional global scaling and the original shared-layer TCAS schedule are special cases.

> **(3)** We use shared-input paired ablations and a pre-registered strict-276 same-runner confirmation to separate layer redistribution from temporal placement and compare the selected allocation against the unmodified pipeline, competitive fixed scales, global temporal scaling, and layer-only controls.

> **(4)** We evaluate transfer and limits rather than assuming universality: layer redistribution partially transfers to MV-Adapter, temporal placement is architecture-dependent, MVDiffusion provides a negative interface boundary, and a 12-object 3D bake study reports bounded seam/unseen-view evidence.

---

## 14. Claim vocabulary release rules

### Preferred terms

- “strict-276 same-runner confirmation”
- “shared-input paired comparison”
- “reference fidelity”
- “GT-relative texture error”
- “layer redistribution”
- “temporal placement”
- “transferability”
- “tested mapping choices”
- “architecture/interface-dependent boundary”
- “no detected difference”
- “12-object stratified case study”

### Terms requiring qualification

- “robust” → state the exact axis (R0/R1, mapping family, seeds);
- “consistent” → state whether this means directionally or statistically consistent;
- “best” → name the exact candidate set and metric;
- “cross-view consistency” → for the current bake audit, prefer “render-time cross-view color stability descriptor.”

### Forbidden without new evidence

- “universal”
- “optimal schedule” / “the optimal LLH”
- “generalizes across backbones”
- “CAI derives/discovers”
- “equivalent/non-inferior” from a CI crossing zero
- “seam-free”
- “texture fidelity” inferred only from larger Laplacian/gradient/HF energy
- historical +0.96 dB / archived 14.78 as active evidence

---

## 15. Response-letter strategy

The response letter should be evidence-first and shorter than the internal audit.

For each reviewer comment use the same four-step pattern:

**Concern → What changed → Evidence → Claim boundary.**

Example for Reviewer 2 cross-backbone:

> We agree that the previous revision remained inside one MVPainter-style architecture family. We therefore added a genuine second-adapter evaluation and a third interface-boundary study. On MV-Adapter, layer redistribution improves PSNR/color/GT-relative texture metrics under the frozen paired protocol, while SSIM shows a small reverse and temporal placement is not separated; mapping sensitivity tests whether the effect depends on one arbitrary partition. On MVDiffusion’s non-isomorphic control interface, the layer-wise benefit does not replicate. We therefore do not claim universal generalization; the revised manuscript states a bounded transfer result and an explicit applicability boundary.

This is more persuasive than claiming every new experiment “closes” the concern.

---

## 16. Acceptance-oriented priority order

Before editing prose, the branch must converge on one authoritative evidence state.

**Gate 1 — evidence convergence:** merge/record the final status of parallel M3 and LHL-forensics work; remove contradictions among inventory, claim matrix, and readiness report.

**Gate 2 — statistical presentation convergence:** choose one paper-facing delta convention. Internally raw or benefit-oriented values may coexist, but a reader should not have to infer why positive LPIPS means “better” in one table and negative means “better” in another.

**Gate 3 — claim freeze:** issue one final claim matrix containing allowed wording, forbidden wording, and exact evidence source.

**Gate 4 — manuscript rewrite:** modify 01549 in the section order defined above.

**Gate 5 — response-letter rewrite:** answer the current R1/R2 comments from the final manuscript, not from old audit reports.

**Gate 6 — final reviewer simulation:** search the final manuscript for every high-risk word (“optimal,” “derive,” “generalize,” “equivalent,” “preserve,” “robust,” “cross-view”) and verify each occurrence against the claim matrix.

---

## 17. Final recommendation

The most defensible and acceptance-oriented revision is **not** to try to preserve the 01549 C3/CAI narrative verbatim and not to claim that the new evidence proves a universal method.

The recommended final story is:

> **A global adapter scale conflates residual allocation across network depth and denoising time. We generalize TCAS to a layer-wise timestep-conditioned residual allocation surface, experimentally separate where/when effects, validate the selected allocation on a strict same-runner holdout against the unmodified and strong fixed baselines, and then use cross-backbone positive/mixed/negative evidence to define what transfers and what does not.**

This directly answers Reviewer 1 with protocol rigor, fidelity-aware metrics, baselines, and 3D evidence; it answers Reviewer 2 by broadening the methodological object beyond schedule selection, conceding CAI’s descriptive role, and adding genuine cross-backbone evidence without forcing a false generalization claim.

The audit-dependent branches above should be treated as a pre-committed narrative decision tree: when the remaining audit results converge, choose the corresponding wording branch rather than redesigning the scientific story after seeing the result.
