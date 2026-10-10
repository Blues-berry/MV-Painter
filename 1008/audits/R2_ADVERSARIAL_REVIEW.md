# R2.1 adversarial review after manuscript edits

> **Historical review snapshot.** This pass reviewed the earlier 9-page candidate and predates the corrected 01549-first package, retained first-round preference/FAC evidence, and current 11-page manuscript. Its page references and evidence dispositions do not describe the current 1008 submission. See `submission_1008_final/Manuscript_1008.pdf` and `01549_TO_1008_CHANGELOG.md`.

**Review stance:** assess the current A+ manuscript as a skeptical Reviewer 2.1 deciding whether the revision has moved beyond “schedule selection for an existing adapter.” This is a post-edit adversarial pass, not evidence that the editor will accept the paper.

## Strongest rejection case

> TCAS does not introduce a new adapter, objective, training procedure, or general control operator. It multiplies an existing geometry-adapter residual by a manually chosen three-stage profile. SSI has already scheduled strengths across layers and timesteps and has applied those schedules to geometric ControlNet conditioning. The original C3 selection cannot be independently reconstructed from the available probe records. Fresh C shows Generic Linear outperforming C3 on all four reported means. The stage-placement follow-up favors another profile, was run after earlier results were inspected, and only near-matches scalar sums; A3b cannot distinguish layer/time response from realized dose. The manuscript reports image-space comparisons without valid new bake, seam, PBR, human, or matched-backbone evidence. The revision therefore documents a useful implementation-specific ablation, but has not shown a sufficiently substantial new methodological contribution for this journal.

This is a serious, evidence-based rejection argument. The manuscript must not answer it by renaming the scheduler, omitting counter-results, or implying SSI did not study geometric scale scheduling.

## Point-by-point response supported by the record

| Skeptical point | Strongest honest answer | What remains unresolved |
|---|---|---|
| “It is still schedule selection.” | The revision defines the exact operator on a geometry-conditioned multi-view adapter, the step bins and cap behavior, and evaluates a frozen profile under matched object inputs. It now distinguishes the method's task-specific intervention from the general prior-art schedule family. | C3 is a profile/configuration, not a new general algorithm; prior 24×17 ranking is not fully auditable. |
| “SSI already did layer/time scheduling and geometry conditioning.” | Acknowledge this directly. SSI uses attention-style mixing and also schedules ControlNet geometry scale for single-image style transfer. TCAS scales an existing GeoTex geometry residual for multi-view texture generation. This is a signal/interface and task/evidence distinction, not a first-principles scheduling novelty claim. | Task difference may still be judged insufficient by the editor. |
| “C3 is just empirically selected.” | The revision says it is the historical development choice and does not claim a verified optimum. A later fresh 300-object study evaluates it without additional search. The 276 stage follow-up and fixed-mean contrast support that stage allocation is consequential. | The exact C3 choice is not derived; stage follow-up is post-inspection and near-, not exactly, scale-sum matched. |
| “Generic Linear is better.” | Agree. On Fresh C, Generic Linear has more favorable cohort means on all four displayed metrics. The paper reports its paired differences and object distribution and explains that the profiles also differ in layer-wise scale sums. | There is no audited mechanism explaining the linear advantage; do not call the comparison dose-matched. |
| “The method's temporal mechanism is unproven.” | Agree that dose-independent mechanism is unproven. The strict-276 profile comparison indicates stage sensitivity under near-matched scalar sums; layer-wise post-scale corrections vary with the state. A3b's raw-$L_2$ common-support calculation is dimension-confounded across groups, so cross-layer dose support is unresolved. | No equal-realized-dose mechanism claim can be made. |
| “C3's late/middle rationale is inconsistent with LLH.” | Keep cohort and profile names explicit. Strict-276 temporal L--L--H beats C3 on six endpoints; Fresh C LLH is a layer-conditioned schedule with a different shallow profile; Fresh B LLH is another cohort and temporal comparison. The direction depends on profile, endpoint, and protocol. | There is no universal early/middle/late ordering, and C3 is not shown to be generally best. |
| “The texture-complexity analysis is a post hoc explanation.” | The revision correctly attributes it to the LLH--GFL per-object effect and GT-only texture descriptors, reports separate cohorts, and labels the association non-causal. It is not used to explain C3--Linear. | It does not establish a selector, threshold, or causal failure mechanism. |
| “No other backbone or 3D evidence.” | State this plainly: MV-Adapter and MVDiffusion are bounded, non-matched interface checks; Fresh C is image-space only and its bake gate failed. | Transfer, seams, PBR, and human preference remain open. |

## Claims to challenge in final proof reading

Reject or revise any instance of:

- “first” or “novel layer × time scheduling”;
- “C3 selected/derived/optimal” without the historical-provenance caveat;
- “equal dose,” “dose-independent mechanism,” or “temporal effect independent of scale”;
- “Generic Linear is equivalent to C3,” “C3 is best overall,” or a Pareto claim based on selected endpoints;
- “late-high improves texture” as a universal conclusion;
- attributing GT texture association to raw FG-PSNR, C3, or a causal selector;
- “cross-backbone generalization,” “PBR improvement,” “seam quality,” or “human preference” based on unavailable/invalid evidence.

## Overall adversarial verdict

The revision is now materially stronger as a scientific account: it adds a supported stage-sensitivity comparison, exact applied-scale arithmetic, a complete paired counter-result against Generic Linear, and a correction to the texture-boundary attribution. These additions increase the contribution's auditability and task relevance. They do **not** remove the core novelty risk: SSI pre-exists the general control idea, and the TCAS component remains a simple schedule applied to an existing adapter.

**Recommended decision posture:** submit the A+ response only if the authors are willing to defend a task-specific method/evidence contribution and accept a high rejection risk. Do not spend the remaining revision effort trying to manufacture an unvalidated algorithmic distinction. If the journal requires a new general method beyond schedule selection, the current evidence does not close that requirement.

## Independent reviewer pass and exact anchors

A separate read-only Reviewer 2.1 pass reached the same high-risk conclusion and checked the revised manuscript against the seven requested challenges. The current page references are for the compiled 9-page main PDF; the supplement is 8 pages.

1. **Manual schedule choice remains unresolved.** The paper identifies C3 as a 24-object/17-variant development choice, with incomplete historical row-level provenance and no validated selector (main pp. 4–5, lines 236–249 and 331–339). Fresh C tests the fixed profile but does not derive why this exact profile should be selected. The later placement follow-up favors temporal L--L--H over C3 on all six formal endpoints; it was specified after earlier results were inspected and near-matches scalar sums only (Supplementary Material, pp. 5–6, Section S5 and Table S7).

2. **SSI is a direct conceptual precedent.** The manuscript acknowledges layer/time schedules and geometry-conditioned ControlNet strength, then limits its distinction to the existing GeoTex residual interface and multi-view texturing evidence (main p. 3, lines 157–177; closest-prior-art audit, lines 5–22). This is task/interface distinction, not a new scheduling primitive.

3. **Temporal mechanism claims are bounded.** The Related Work now says denoising interval is a testable control coordinate and explicitly rejects a fixed semantic partition (main p. 2, lines 138–146). The Method labels the stage profile implementation- and endpoint-dependent, while the placement follow-up is non-blind and the A3b raw-L2 support calculation is dimension-confounded across feature groups (main pp. 3 and 6, lines 228–235 and 421–427; Supplementary Material, pp. 5–6, Section S5). A dose-independent mechanism remains unproven.

4. **C3's loss to Generic Linear has no established cause.** Generic Linear has more favorable means on all four displayed Fresh C endpoints; C3's FG-PSNR median is slightly positive and it wins 155/300 objects. The scale sums differ, so this is not a dose-matched temporal-shape test (main p. 5, lines 363–383, and p. 6, Table 2; `R2_C3_VS_LINEAR_EXPLANATION.md`, lines 14–31). The reply reports the counter-result without inventing a causal explanation.

5. **C&G contribution sufficiency is still uncertain.** The graphics-task relevance and paired evidence are concrete, but the method remains a residual multiplier with a manually selected profile. Fresh C is image-space only; the bake gate failed, and seams/PBR/human outcomes remain unavailable (main p. 2, lines 48–65; p. 7, lines 439–477). Whether this clears the journal's method threshold remains an editorial decision.

6. **Multiple audits could be over-counted as novelty.** The contribution statement groups stage placement, layer/window response, caps, and correction logs (main p. 2, lines 53–65). The revision partly mitigates this by treating most as supporting analyses, keeping cohorts and profiles separate, and avoiding claims of independent replication (main pp. 5–7, lines 320–330, 384–389, 390–427, and 428–477). They should read as one bounded schedule study, not several new algorithms.

7. **Object-level recalculation is possible internally, but not from the submission package.** The paper specifies shared Fresh C identifiers, inputs, seeds, object-paired intervals, and 10,000 bootstrap resamples (main p. 4, lines 261–294; p. 5, lines 303–311). The workspace retains the row-level authorities and the N=20 render analysis; Table S8's separate source paths and hashes are recorded in `R2_CONTRIBUTION_STRENGTHENING_FINAL.md` and Supplementary Section S8. However, Data Availability states that no public code/data package exists (main p. 8, lines 502–507), so an external reader cannot independently reproduce the object-level calculations from the submitted files alone.

## Final verdict

The revision is more auditable and now states a bounded stage-sensitivity result, exact cap behavior, object-level counter-results, and the comparison's limits. It does not remove the core novelty risk: SSI pre-exists the general control idea, C3 remains manually selected, and the strongest baselines do not establish C3 as the preferred profile. Keep the final status at **HIGH / OPEN** rejection risk. The source authorities are [`R2_MECHANISM_AND_MATH_AUDIT.md`](R2_MECHANISM_AND_MATH_AUDIT.md), [`R2_C3_VS_LINEAR_EXPLANATION.md`](R2_C3_VS_LINEAR_EXPLANATION.md), and [`R2_CLOSEST_PRIOR_ART_COMPARISON.md`](R2_CLOSEST_PRIOR_ART_COMPARISON.md).
