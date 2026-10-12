# Response to Reviewers — empirical revision draft

Dear Editor and Reviewers,

The revision retains TCAS and its historical C3 profile and changes the conclusions to reflect the complete comparisons. We evaluate geometry-control allocation as an empirical question in multi-view texturing. Competitive fixed and linear controls, an equal-applied-budget stage comparison, calibrated unseen-view baking and native evaluation on a different backbone now determine the claim scope. We no longer use CAI as an independent derivation or present C3 as a generally preferred schedule. All valid adverse results remain reported.

## Reviewer 1

### 1. Practical quality, full-object comparisons and baked meshes

The main manuscript includes matched full-object views with shared crops and strong fixed/linear controls, together with explicit color/detail failures. The calibrated ten-object native-UV pilot evaluates eleven unseen cameras per object and includes a GT bake at the same source resolution and settings. Late-high reduces FG-LPIPS relative to Fixed Mean by 0.00265, about 2%, but leaves substantial reference-appearance error. C3's earlier PSNR advantage does not repeat stably and its SSIM is lower. We therefore report a small named application result and do not claim generally faithful materials, PBR quality or validated seam quality. Complete grids and source attribution remain in the Supplement.

The original GSO20 attempt stops at an input-only UV-ramp gate after fifteen objects. A documented GT-only calibration addendum subsequently completes all twenty fixed inputs and twelve existing methods, with740 unique bakes. The native projection is unchanged and all375 earlier GLB hashes and metric records reproduce exactly. RawUV aliasing, GT self-bake losses and incomplete coverage remain disclosed; this posthoc re-evaluation is not pristine confirmation. The actual exported-GLB video and complete data are included in the supplementary review evidence. The ten-object GeoTex pilot remains a separate domain/protocol.

### 2. Same-adapter held-out evaluation

Fresh C contains 300 UIDs disjoint from the original probe/evaluation and documented training lists, and all compared conditions use the same frozen checkpoint, runner, inputs, seed policy and metrics. C3 exceeds GFL by 0.522 dB on the registered FG-PSNR endpoint, while stronger controls exceed C3. Fresh C uses a controlled-retraining checkpoint. We cannot authenticate it as the historical main adapter's exact run or numerically reproduce the old +0.96 dB contrast. That headline is retired as current evidence. This addresses the revised claim with matched held-out data while retaining the remaining limitation of the requested historical replication.

### 3. Texture variation versus fidelity

The study distinguishes target-view image agreement, color agreement, variation statistics, subjective preference and baked appearance. Laplacian variance, gradient magnitude and RGB variation are descriptive and are not treated as faithful texture reproduction. A better image score can coexist with visible appearance errors; the main figures retain such examples.

### 4. Paired intervals and structural losses

Objects are the sampling unit; views and sampling seeds are averaged within object. Comparison families and adjustments retain their original classifications. C3 loses to Fixed High on the reported structural endpoints and to Fixed Mean/Late-high in the equal-budget matrix. Intervals crossing zero do not establish equivalence or non-inferiority. No post hoc margin is introduced.

### 5. FAC reproducibility

We retain FAC's previously reported negative re-examination and supply the available configuration and result authority. The recovered list and historical stated training-pool size differ, and the training seed/checkpoint/output manifest remains incomplete. We do not claim a full FAC training replay or a new learned extension. Available inference and statistics artifacts are described separately from the missing historical training records.

## Reviewer 2

### 1. Contribution beyond schedule selection

We agree that the general idea of layer/time strength scheduling is established, including geometry-conditioning schedules. The revised contribution is a controlled empirical account of an application problem: whether the selected operating point remains useful against strong controls, whether moving the same applied-scale budget changes the outcome, and whether the resulting image-space observations predict baked appearance or transfer to another interface.

The 300-object equal-budget comparison changes the original conclusion: the historical middle window is worse than a constant mean and late-high, despite its advantage over fixed low in the initial comparison. The calibrated ten-object bake result supports a small late-high–fixed-mean benefit with persistent quality failures. The native second-interface comparison does not support a stable middle-window advantage. These are task-specific findings backed by complete comparisons, rather than an optimal schedule inferred from CAI. We retain the intervention and its historical identity without proposing an additional algorithm.

The Introduction states these contributions directly. Detailed historical tuning, native-path diagnostics, training alternatives and auxiliary projection development are moved to the Supplement; their adverse outcomes remain disclosed. We recognize that the significance of this empirical contribution remains an editorial judgment and do not treat protocol documentation alone as methodological novelty.

### 2. CAI interpretation

The independent derivation, proposition and optimality interpretation are removed. The method section supplies the executable requested/applied-scale definitions and explains which comparisons identify strength or temporal-allocation effects. Equal applied-scale totals do not equalize state-dependent residual magnitudes, so the total allocation effect is distinguished from a residual-dose-independent mechanism.

### 3. Genuinely different backbone evaluation

The main manuscript supplies a complete native MV-Adapter matrix on fifty input-selected objects with native-camera targets and default-path identity checks. Middle-high minus Fixed Mean FG-PSNR is +0.029 dB, with 95% interval [−0.019,+0.081] and paired p=0.281. The full cohort retains thirteen legal constant-white targets; the thirty-seven textured objects form a descriptive subset rather than a replacement primary. The result is an effective evaluation with mixed endpoints, not evidence of successful C3 transfer.

The retained 75-object MVDiffusion panel supplies additional negative/mixed evidence. Its correspondence-block control differs from the GeoTex residual operator, and the native-mirror check does not cover a rerun of all seventy-five objects. Those limits are explicit.

A separate GSO100/MV-Adapter stress test completes 2,400 cells including APG baselines. All fifteen specified nonreference-LPIPS projection comparisons favor their baselines after the separate Holm9 and Holm6 corrections. It tests the earlier auxiliary corrections, not TCAS itself. Different cohorts and conditioning interfaces are not pooled, and input-domain/backbone differences are not assigned a single causal explanation.

## Reviewer 3

We thank the reviewer for the positive assessment. The revised manuscript retains the original work while bringing the new comparisons, limitations and reviewer responses into agreement.

---

Author-review status: source and PDFs are reviewable; the revised external GSO20 bake evaluation is complete and explicitly classified as posthoc supplementary evidence. This response is not a declaration that all requested experiments or final submission checks are complete.
