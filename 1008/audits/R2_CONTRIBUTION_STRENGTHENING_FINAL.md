# R2.1 contribution-strengthening decision

> **Historical planning snapshot.** This recommendation was written for an earlier candidate. The current 1008 manuscript restores the official post-first-round 01549 base and includes later corrections to figures, preference/FAC disposition, and second-round mapping; use the final submission package and current reviewer map as authority.

## Selected route: Version A+

Keep the original 01549 identity: title, TCAS, C3, and the MVPainter geometry-adapter path. Use the method-centered Version A as the manuscript spine, with one carefully bounded empirical contribution from Version B: matched schedule evidence shows that placement changes outcomes in this pipeline, but no stage is universally best and actual residual dose is not matched.

This is the strongest supportable route for the current revision. Version B as a new “layer × time” method would collide directly with SSI, lean on A2/A3b heterogeneity without a dimension-aware cross-layer dose test, and drift away from the submitted C3 method. A residual-budget-aware controller is not validated. No new method component or GPU experiment is justified for this R2.1 revision.

## Final contribution statement for the paper

1. **TCAS method:** a training-free, three-stage requested-scale intervention on the existing geometry-conditioned adapter residual path for multi-view texture generation. C3 is the fixed profile evaluated; it is not claimed to be optimal.
2. **Controlled design evidence:** a strict-276 follow-up compares stage placements under near-matched per-layer applied-scale sums; outcomes change and the preferred schedule differs by comparison. Fresh C separately shows C3's benefit over GFL on its registered primary endpoint and its limits against Generic Linear and GFH.
3. **Execution and applicability boundaries:** the paper distinguishes requested scales, native-cap applied scales, and post-scale residual corrections; it reports object/endpoint heterogeneity and does not infer dose-independent mechanism, a content selector, cross-backbone generality, or downstream 3D quality.

The evidence chain is:

`geometry-conditioned multi-view texturing → existing residual strength is an inference control → near-matched stage placements change image-space outcomes in the tested pipeline → define a reproducible TCAS intervention → evaluate its gains and counter-results under the native caps`

This chain addresses why the task needs explicit inference-time control and shows that the choice matters. It does **not** prove that C3's middle-high-middle design is uniquely necessary: C3 is not supported as the best general profile, and the historical development evidence is not fully recoverable.

## Version comparison

| Choice | Value | Main risk | Decision |
|---|---|---|---|
| **A+ — strengthen submitted TCAS** | Preserves continuity; ties the method to measurable task-specific results; acknowledges SSI; integrates stage-placement and execution evidence with limits. | A reviewer can still regard the contribution as an incremental profile on an existing adapter. | **Select.** |
| B — add a new residual-budget or adaptive control component | Could become a distinct method in a future paper if an independently validated rule is developed. | No working component, no stability evidence, no independent outcome evidence; adds parameters and a new claim set; not a surgical 01549 revision. | **Do not select.** |

## What changed in the real manuscript

The original submitted source remains protected and unchanged at `1008/manuscript/source_01549/final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`). The revision candidate [`final_0903.tex`](../manuscript/revision_1008/final_0903.tex) was edited to:

- retain the explicit SSI prior-art acknowledgment and reject a first/general schedule claim;
- add the 50-step executable stage bins, native cap execution, and no-extra-U-Net-call statement;
- correct the texture-complexity statement to the LLH--GFL paired effect, not raw FG-PSNR or C3;
- clarify that Fresh C LLH is layer-conditioned and differs from strict-276 temporal L--L--H;
- state the actual C3, GFL, Generic Linear, temporal L--L--H, and fixed-mean scale sums and where comparisons are/are not matched;
- add strict-276 placement evidence and its non-blind, near-matched-dose limits;
- state plainly that Generic Linear has better means than C3 on all four Fresh C endpoints.

Supplementary Table S7 was added to [`supplement_1008.tex`](../manuscript/revision_1008/supplement_1008.tex) to report all six formal C3--temporal-L--L--H and C3--fixed-mean paired endpoints. The added table is traceable to an existing accepted run and audit; no new plot or computational script was necessary. The full evidence sources and execution chain are in `R2_MECHANISM_AND_MATH_AUDIT.md` and `R2_C3_VS_LINEAR_EXPLANATION.md`.

The historical Table S8 N=20 unseen-view analysis is separately traceable to `final/round2/scientific_validation_v3/GLB_NATIVE_EGL_RENDER_REPORT_20261006.md` (SHA-256 `3a28469e45efa89b677b8ed95d008e1707ce276d5b5c55744ff44ba67c28230c`), `bake_handoff/GLB_NATIVE_EGL_RENDER_V1/GLB_NATIVE_EGL_ANALYSIS.json` (SHA-256 `bcb1c52c0efc6662cc95b3514c4eae9f91f60e82208468b6f422cc3acccea916`), `UNSEEN_OBJECT_METRICS.csv` (SHA-256 `b00e44f3c1f2555f5ab1de511437be6b77af694da2d0e5eb5c10fd42664c7057`), and `UNSEEN_PER_VIEW_METRICS.csv` (SHA-256 `dd5273b1a4072f7893c1d13767eccd9e838dad98dfc20a03195cb1edc014ede4`). The N=20 result is historical and bounded; its source assets and render images are not included in the submission package.

## Final build record

The candidate main manuscript and supplement compile successfully to 9-page and 8-page PDFs. The final artifacts are [`final_0903_R2_1.pdf`](../manuscript/revision_1008/compiled_R2_1/final_0903_R2_1.pdf) and [`supplement_1008_R2_1.pdf`](../manuscript/revision_1008/compiled_R2_1/supplement_1008_R2_1.pdf). Final logs contain no unresolved citations/references or LaTeX errors; the C&G class and narrow tables retain non-fatal box warnings, including minor overfull and underfull line breaks.

## Final decision flags

| Required flag | Value | Reason |
|---|---|---|
| `METHOD_CONTRIBUTION_DEFENSIBLE` | **PARTIAL** | Concrete task-specific intervention and evidence; no new general scheduling algorithm. |
| `DESIGN_RATIONALE_SUPPORTED` | **PARTIAL** | Near-matched stage evidence and fixed-mean comparison support stage sensitivity; C3's exact shape is not optimally justified and residual norms are not matched. |
| `DISTINCTION_FROM_SSI` | **TASK_AND_EVIDENCE** | Signal/interface, graphics task, and validation differ; SSI already covers layer/time scheduling and geometric ControlNet strength. |
| `C3_VS_STRONG_BASELINE_EXPLAINED` | **YES** | Fresh C favors Generic Linear on all four means; the profile sums and object distributions are stated. No unsupported causal explanation is offered. |
| `DOSE_INDEPENDENT_MECHANISM_PROVEN` | **NO** | A3b raw-$L_2$ dose support is dimension-confounded across feature groups; the fixed-map outcomes are not an equal-dose intervention. |
| `NEW_METHOD_COMPONENT_JUSTIFIED` | **NO** | Candidate control is not implemented or independently validated. |
| `NEW_GPU_EXPERIMENT_NEEDED` | **NO** | A new run cannot resolve the core prior-art novelty question for this scoped revision. |
| `R2_1_REJECTION_RISK` | **HIGH** | The reviewer may still require a substantive algorithm beyond task-specific schedule application. |

## Release boundary

These edits and evidence support a more direct and technically accurate response. They do not let the authors promise acceptance or claim Reviewer 2.1 is fully closed. The final response should acknowledge that sufficiency is an editorial judgment and emphasize the measured task-specific method question, not a priority claim.
