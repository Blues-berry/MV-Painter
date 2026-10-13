# Response to Reviewers — Round Two Working Package

## Editorial note

We thank the reviewers for identifying that the method contribution and its
practical evidence were not sufficiently visible. We revised the paper around
layer-wise stage-aware adapter scaling: a training-free control that assigns
different residual strengths to UNet depth groups and denoising stages. The
revision adds a shared-input 24-object, three-seed ablation, retains the
strict-276 layer-LHL transfer record as a separately labeled result, restores
complete-object comparisons, and reports fixed-mean and layer-LLH counterexamples.
The paper no longer presents C3, LHL, or layer-LHL as a universal optimum.
The 12-object baking result remains a descriptive case study and TRB remains an
additional stopped exploration.

All legacy numbers below remain frozen in
coordination/E1_CLAIM_EVIDENCE_FREEZE_20260929.md and the linked E0 audit
reports. New layer-wise numbers are frozen in
coordination/layer_lhl_v1/ablation_summary.json and the accompanying raw CSV,
manifest, and hash files.

## Reviewer 1 — practical quality and complete 3D output

### R1.1: Does the proposed layer-wise control improve practical image quality over a competitive fixed-low baseline?

We agree that the earlier wording was too strong, while clarifying the
specific operating range of the method. The clean-v2 strict-276
panel does not show uniform superiority. Fixed-low is higher than C3 on
Full-PSNR (15.086 versus 14.875), FG-PSNR (7.030 versus 6.763), and FG-SSIM
(0.355 versus 0.348), while C3 is close on FG-LPIPS (0.201 versus 0.202) and
Edge-SSIM (0.500 versus 0.500). We now describe this as a non-dominance
result and retain fixed-low as a competitive baseline (manuscript Sections
``Visible complete-object evidence'' and ``Strict holdout and stage-placement
evidence''; Supplementary S4a contains the full contact sheet).

The new shared-input development ablation directly tests the added layer-wise
component. Across 24 objects and three seeds, layer-LHL improves over fixed-low
by +3.083 dB FG-PSNR and -0.0267 FG-LPIPS with paired 95% intervals excluding
zero. It also shows the limit of the claim: layer-fixed-mean is better than
layer-LHL on FG-LPIPS, and layer-LLH is better than layer-LHL on all seven
reported metrics. We therefore claim a layer-wise operating range and
metric-dependent trade-off, not a single best schedule.

The earlier strict-276 stage-placement follow-up remains separately reported.
LLH is better than LHL on all six non-SSIM metrics, and the saved-artifact
Full-SSIM means are 0.88313 for LLH and 0.88144 for LHL. This is consistent
with the new ablation and rules out a unique LHL selection.

### R1.2: Does the result survive into a real 3D output?

We added an auditable CPU bake on a stratified 12-object cohort. Four
conditions produced 48 object--condition GLBs and 528 unseen-view rows (11
views per export). The path is therefore operational, but the result does not
show a C3 advantage: descriptive masked PSNR is 5.638 for C3, 6.001 for
fixed-low, and 11.824 for no adapter; CIEDE2000 and FG-LPIPS likewise favor
no adapter in this cohort. We consequently do not claim population-level 3D
superiority. The manuscript records that there is no generated 12-object GT
bake, DISTS was unavailable, cross-view/source-fusion colour inconsistency
was observed, and Blender reindexed vertices for obj_0048. These limitations
are also listed in supplementary Section S4.

We also added object-level failure boundaries in supplementary Section S4.
For obj_0078 and obj_0082, raw texture coverage is 0.0328 and 0.0286,
respectively, with inpainted fractions of 0.2802 and 0.4951. For obj_0048,
raw coverage is 0.1547 and the inpainted fraction is 0.8441; its fixed-low/C3
masked-PSNR means are 5.090/4.927 dB and its CIEDE2000 means are
53.328/54.339. These are failure-boundary examples, not selected success
cases.

### R1.3: Are the metrics and saved artifacts reproducible?

The evidence package now records exact object IDs, schedule names, record/CSV
and PNG pairing, checkpoint/object-list hashes, and the source of each metric.
The strict-276 freeze contains 276 objects for each of four stage schedules,
with the six target views explicitly fixed. The saved-artifact Full-SSIM branch
uses PNG-reloaded float32 predictions and the original RGBA ground truth
composited over white in float32.

To isolate serialization effects without rerunning the model, we used the
saved 12-object tensors. With the GT fixed, converting prediction A from
float16 to float32 changes mean SSIM by +0.03198; prediction PNG
quantization changes it by -0.00036; and GT PNG serialization changes it by
-0.00007. The revised text does not use this decomposition to retrofit the
historical 300-object table.

### R1.4: What happened to the learned FAC extension?

FAC is now presented as a separate strong-residual extension, not as evidence
for TCAS superiority. Under the controlled paired protocol, no trained FAC
variant reached the training-free schedule. The earlier positive comparison
used a different protocol/adapter instance and is explicitly marked
superseded rather than used as a current result.

## Reviewer 2 — novelty, mechanism, and generality

### R2.1: Is the layer-wise method more than an empirical schedule choice?

We define the contribution as layer-wise stage-aware residual control rather
than a learned selector. The method applies an explicit scale function
$s_l(p)$ to existing adapter residuals at deep, middle, and shallow UNet
groups, requires no retraining, and adds only scale assignment during
inference. The shared-input ablation separates layer strength from temporal
placement: layer-wise controls improve foreground fidelity over fixed-low,
while layer-fixed-mean and layer-LLH show that no single temporal schedule is
uniquely selected. This is a concrete inference-control contribution, not a
theoretically derived optimum.

The revised manuscript explicitly distinguishes the CAI interpretation from a
selector. CAI is used to describe empirical stage utility; layer-fixed-mean and
layer-LLH counterexamples prevent us from claiming that it uniquely predicts
LHL or layer-LHL.

### R2.1b: How does TCAS compare with generic schedules requested in the first round?

We retained the original-protocol linear warm-up and cosine-bump comparison in
Supplementary S5 and refer to it from the main results. The audit shows C3
minus linear warm-up of $+0.323$ dB PSNR (95\% CI $[+0.263,+0.386]$) and C3
minus cosine bump of $+0.902$ dB (95\% CI $[+0.824,+0.981]$). These rows use
the documented strong-residual adapter/protocol and are not mixed with the
clean-v2 strict-276 panel. We therefore use them to establish a schedule-family
comparison within that protocol, not to claim cross-protocol or universal
superiority. The MVDiffusion deployment is reported only as compatibility
evidence because no controlled TCAS stage comparison was completed there.

### R2.2: Is the stage ablation strictly controlled?

No. We now state this directly. The 50 steps are partitioned as 17/16/17.
The fixed-mean schedule has mean scale 1.6667 and squared-scale sum 138.8889;
HLL and LLH have mean 1.675 and squared-scale sum 157.8125; LHL has mean
1.650 and squared-scale sum 153.125. Actual residual L2 summaries also
differ. The result therefore supports stage-placement sensitivity, but not a
strict equal-effective-budget causal isolation.

### R2.3: Does the fixed-GT SSIM analysis change the conclusion?

It makes the provenance explicit without requiring model reruns. The
prediction-dtype effect is much larger than the prediction/GT PNG effects in
the saved 12-object trace, so the revised paper reports the branches
separately. On the full saved-artifact stage follow-up, C3 is above fixed mean
and HLL but below LLH; the C3-minus-LLH 95% bootstrap CI is
[-0.00205, -0.00134]. We do not interpret a CI crossing zero as
equivalence.

### R2.4: Does the method generalize to another backbone?

The MV-Adapter audit uses a 76-object, 11-evaluated-condition/schedule cohort and keeps high scale
1.50 separate from high scale 1.00. It does not establish universal transfer:
the pre-specified CAI rule is undefined/set-valued, and the official
pretraining UID list was unavailable. The revised manuscript reports this
audit as a contribution boundary and does not make an absolute cross-backbone
claim.

For reproducibility, the original results/holdout_exact_76/PROTOCOL.json is
absent. The available run_config.json and paired_bootstrap_exact.json are
identified as partial replacement provenance in the supplementary material.
The GT-to-GT bake sanity check was only a two-object smoke (obj_0013 and
obj_0015); the 12-object generated bake has no GT condition. We do not present
the evaluator's bookkeeping field as 12 GT bake records.

### R2.5: Did we test whether a more adaptive controller resolves the limitation?

We retain one pre-specified 24-object development pilot for a residual-budget
TRB extension as an additional exploration, not as a main method result. TRB
did not improve C3 on the primary FG-LPIPS gate (0.1349 versus 0.1336), had
lower PSNR (22.700 versus 22.971), and approximately doubled calibration
cost. The branch was stopped before holdout evaluation and is not used to
define the TCAS contribution.

## Changes to the manuscript package

- final_round2.tex: layer-wise stage-aware method framing added; shared-input
  ablation and complete-object success/failure panels are visible in the main
  text; strict tables, generic-schedule scope, limitations, and conclusion are
  aligned.
- supplementary_round2.tex: frozen protocol, full 12-object contact sheet,
  original-protocol warm-up/cosine audit, shared-input layer-wise ablation and
  hash manifest, stage metrics, fixed-GT decomposition, baking audit,
  MV-Adapter audit, and FAC/TRB extensions.
- coordination/E1_CLAIM_EVIDENCE_FREEZE_20260929.md: claim--evidence map
  and prohibited wording.
- coordination/E0A_EVIDENCE_FREEZE_20260929.md,
  coordination/E0_B_AUDIT_20260929.md, and
  coordination/E0_D_AUDIT_20260929.md: evidence audits.
- coordination/TRB_DEV24_GATE_20260929.md: bounded negative controller pilot
  and stop decision.

This is an author-review package. We have not submitted or automatically
posted a revision.
