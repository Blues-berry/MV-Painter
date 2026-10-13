# View-wise Counterfactual Geometry-Control Protocol

## Question and status

This independent study tests one falsifiable mechanism: whether the sign of a small, view-specific redistribution of geometry-adapter scale can be predicted from the known reference-view appearance error, and whether the resulting action changes unseen-view quality after the six generated views are baked onto the original UV mesh.

The earlier BAVGC STOP remains in force and is preserved. This protocol does not re-open its static-feedback result. It tests a new paired intervention on the real GeoTex generator; it is not a completed algorithm or a claim of novelty.

## Frozen intervention

The base is the existing `budget_fixed_mean` profile: requested scale 1.65 for every sampler step and each of the deep, middle and shallow groups. The sampler has 50 EulerDiscreteScheduler updates. Only steps 34–49, inclusive, are intervened on; no time window, layer group or perturbation size will be searched.

Let slot 0 be the reference camera in the six-view input mosaic, and let each listed vector be ordered by the model's 3-row by 2-column mosaic (`slot = row * 2 + column`). The fixed perturbation is δ = 0.20:

| Condition | Deep and middle scales at steps 34–49 | Shallow request |
|---|---|---:|
| B0 | `[1.65, 1.65, 1.65, 1.65, 1.65, 1.65]` | 1.65 |
| B+ | `[1.85, 1.61, 1.61, 1.61, 1.61, 1.61]` | 1.65 |
| B− | `[1.45, 1.69, 1.69, 1.69, 1.69, 1.69]` | 1.65 |

At all other steps, all three conditions request 1.65 in all groups. The six-view applied-scale sum for every affected deep/middle step and group is 9.9. This is a view-to-view transfer: individual views do not keep equal budgets. Deep and middle caps are 3.0 and 3.5, respectively, and do not bind these values. Shallow is not reallocated; its 1.65 request is capped at 0.8 in all three conditions. The runtime audit records requested and applied scales separately.

Scale vectors are retained in FP32 for cap and budget accounting; the scaled correction is cast back to the original UNet feature dtype before injection. B0 retains the frozen scalar multiplication code path.

## Objects, seeds and budget

The development cohort has six previously exposed GeoTex objects selected before new outputs: two with favorable baseline baked LPIPS, two typical, and two difficult. Their full-cohort indices are `[0, 1, 2, 3, 4, 7]`, preserving the frozen object seed `42 + full_cohort_index`. Initial latent seed 42 is reset immediately before each generation. The same condition image, target views, geometry, depth, mask, text/image embeddings and initial latent must hash identically across B0/B+/B−.

The maximum is 30 new generations. Six B0 generations first verify identity; one B+ run is an intervention-injection smoke gate. If both gates pass, the remaining paired B+/B− cells are completed for six objects (18 total generations). Expansion to the remaining four exposed objects is allowed only if the first six give credible evidence that reference error selects the better direction. No training and no hyperparameter search are allowed.

## Evaluation and information boundary

The reference image and its foreground mask are legal inference inputs, so slot-0 RGB MAE and CIEDE2000 may be measured against that known reference. Also record generated-view foreground PSNR, LPIPS and SSIM per view, plus the six-view aggregate.

For every condition, use the frozen, original GLB, camera poses, native UV coordinates, bake resolution, rasterization, fill and rendering procedures. Render and score the eleven unseen cameras. Record baked foreground LPIPS, UV consistency and coverage, full-object visual outputs, and generation/bake/render time. Preserve failed or incomplete outputs.

Ground-truth texture and unseen-camera renders are evaluation-only. They may not select B+ or B−, set scale values, or tune a policy. Direction analyses use objects as the unit; camera views, adapter blocks and sampler steps are not treated as independent objects.

## Frozen questions and stop gates

1. Does lower reference-view error between B+ and B− align with lower eleven-view baked LPIPS across objects?
2. How often does a source-view improvement accompany degradation in the other five generated views or the unseen bake? Show every such counterexample.
3. Does either direction improve baked quality over B0 by a practical amount, and is that improvement spread across objects?
4. If both B+ and B− are generated and selected by reference error, how does that two-call rule compare with an equal-call-count simple candidate-selection baseline and the one-call B0 fixed policy?

Stop before quality generations if any camera identity, tile map, budget, shared-state, feature-shape, precision, cache or realized-residual gate fails. Stop after six objects if the action direction is not useful. Do not add another control rule, feedback feature, scale, time window or layer group.

Formal controller development is allowed only if direction is useful on multiple objects, beats the simple equal-cost candidate rule on unseen baked quality, shows no systematic structure/color/other-view damage, is not driven by a few objects, offers a defensible distinction from existing online scale selection and 3D texture guidance, and pays for its extra inference cost. Otherwise issue STOP and return to the final 1014 empirical revision.

## Equal-generation-cost add-on

Phase C requires a simple baseline with the same number of complete generations as the B+/B− selector. On the same six objects only, one additional Fixed Mean B0 candidate was therefore generated with latent seed 43; the original Fixed Mean seed-42 candidate serves as the other draw. All inputs except the initial latent were hash-identical. The two Fixed Mean candidates were selected by the same legal reference RGB MAE and CIEDE2000 scores used for the action rule. This adds six generations, for 24/30 total. It does not change δ, the sampler window, adapter groups or the six-object cohort, and it is explicitly a two-call best-of-two baseline rather than a proposed controller.
