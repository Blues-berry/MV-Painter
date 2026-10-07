# Scientific readiness — 2026-10-06

## Verdict

`MORE_EVIDENCE_REQUIRED`

`SUBMISSION_READY=NO`

`SCIENTIFIC_EVIDENCE_FREEZE=NO`

`HUMAN_EVIDENCE_GATE=OPEN`

`PRE_ACCEPTANCE_P0=0`; `SCIENTIFIC_P1=0` for the explicitly scoped stored
N=20 GLB evaluation; `OPERATIONAL_P1=1` (P1-2).

The current provisional narrative remains `NARRATIVE_D`: adapter scaling and
residual allocation, with depth allocation primary and tested temporal
contrasts secondary on the primary backbone. Do not make the full Layer ×
Time interaction load-bearing. A2 is a native-dose discovery map. A3b has no
three-layer common support (0/2,250 rows) and does not identify a dose-free
interaction. MV-Adapter is a bounded intervention-specific boundary, not a
matched causal test of architecture.

## Decisions under the user's hard rules

- **Do not force a full Layer × Time interaction.** A2 supports a strong
  discovery response surface; A3b's unbalanced dose support and MV-Adapter's
  non-replication do not validate a universal interaction law. Use depth
  allocation and tested temporal contrasts as separately measured controls.
- **Do not claim a unique schedule winner.** B passed its 4,500/4,500
  integrity gate before condition-level analysis. LLH−LFM-EXACT is
  statistically detectable but inside the frozen practical margins; the
  LLH/HLL/LLL directional conjunction fails; `gen_linear` remains a credible
  primary-endpoint competitor. No FRESH_CONFIRM_C schedule search is
  indicated.
- **Keep the practical drift reference descriptive.** It comes from a
  development-only repeated-seed probe and was written after B exposure. It
  supplies effect-to-run-variation context, not a threshold or a prospective
  safeguard.
- **Keep MV-Adapter as a boundary result.** It has 98/99 planned objects and
  no corrected global interaction in its tested intervention range. MVDiffusion
  adds a separate 75-object mixed/negative result through CPBlock interpolation;
  its interface differs from both the primary backbone and MV-Adapter. Report
  each within its own cohort and do not infer architecture causality. Do not
  change groupings or scales to seek a positive; another backbone is not
  justified by these results.
- **Calibrate strict-276 C3 language.** A read-only paired re-evaluation gives
  GC3−GFL FG-PSNR +1.207771 dB (nominal object-bootstrap 95% CI
  [+1.116967,+1.294989], 259/276 favorable), but this pair was not a registered
  primary Core-7 contrast and the old GFL/GC3 tensor-hash/common-runner chain
  is incomplete. GC3−GFH is a trade-off: −1.214235 dB FG-PSNR, but +0.725229
  dB Full-PSNR and +0.001229 Full-SSIM; five of seven directions favor GFH.
  Treat these as retrospective same-cohort supplements with nominal unadjusted
  intervals, not a new independent held-out confirmation or replication of
  the submitted pooled +0.96 dB. FRESH_CONFIRM_B tests LLH contrasts and does
  not substitute for C3.
- **R2 novelty remains a blocking judgment.** The focused primary-source
  review found a close precedent in [Scheduled Style Injection, published in
  the CVPR 2026 NTIRE proceedings](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf),
  which varies strength across decoder layers and timesteps and also schedules
  geometric ControlNet scales. Its style-transfer/SD path differs from MVPainter, but the present
  paper cannot claim the general layer×time schedule idea as new. The candidate
  contribution is a bounded empirical characterization of MVPainter's residual
  path and 3D texture endpoint; that may still be insufficient for the venue.
- **Human study is the remaining high-value evidence gate.** The submitted
  manuscript reports an earlier 24-participant, 30-object 3AFC study comparing
  s=1.25, s=2.50, and C3. That result is not a human comparison of the current
  LLH condition against the four frozen comparators. The new package remains
  pre-collection: 40 assignment slots, fixed stop, 24 comparisons per
  participant, at least 36 valid completions, and LLH versus GFL, GFH, GC3,
  and `gen_linear`. It separates appearance fidelity from texture/shape
  naturalness. No responses have been collected.

## Next-stage GPU and statistical results

E1 used two RTX 5090 GPUs to generate 576 rows for seeds 43 and 44 on the
locked 48-object B subset. Its integrity gate passed before analysis; all
576 prediction and residual-trace pairs were hashed, and the shared reference
inputs matched. The 48 seed-42 cells reuse official B outputs. Across the
three fixed seeds, LLH improved LPIPS over GFL, GC3, and LFM-exact after the
planned five-comparison Holm correction, but not over GFH or generic linear.
PSNR is mixed. For LLH−LFM-exact, mean effects are −0.00391 LPIPS and +0.329 dB
PSNR, while the descriptive ratios to the median within-object seed range are
0.68 and 0.58. E1 is realization sensitivity on a reused fixed cohort, not
independent-object confirmation. See `next_stage_20261006/MULTISEED_ANALYSIS.md`
and its integrity/provenance gates.

E2 generated 480 new rows across seeds 42–44 and reused 96 verified seed-42
aliases. The 576-row logical matrix passed checks of shared inputs, unique
latents, all 50-step residual traces, 1,152 prediction/trace file hashes, and
the pre-generation design/runner lock before the factorial analysis ran.
Increasing deep and middle scales together (1.25→1.675) favored both FG-LPIPS
and FG-PSNR on this subset. Increasing shallow scale (0.50→0.80) worsened
LPIPS, with no supported PSNR main effect. A deep+middle-by-shallow interaction
appeared for PSNR (+0.365 dB, 95% CI [+0.243, +0.486], Holm p=0.00030), not
LPIPS (p=0.719). These estimates average three fixed seeds within object and
are not independent-object or random-seed-population inference. Deep and
middle were moved together and no equal-realized-dose claim is supported.
Seed-42 F01 reuses `native_gfl`: requested shallow scale 1.25 is capped to
effective 0.80, while seeds 43/44 request and apply 0.80. Predictions and
effective traces match; the request-field difference is recorded in
`next_stage_20261006/STATIC_SEED42_ALIAS_ERRATUM_20261006.md`.

E2 strengthens a narrow, static layer-scale response characterization. It
does not vary time and cannot establish the layer×window effect or a
dose-independent mechanism. A3b's 0/2,250 shared-support result remains the
identification boundary.

## GLB-native 3D reevaluation

The old CPU renderer's clamp and non-mipmapped sampling did not match the
exported GLBs. On 2026-10-06 the exact stored GLBs were rendered under their
embedded base-color sampler and evaluated on 20 objects × 8 conditions × 11
unseen views. All 1,760 render hashes and all 160 source GLB hashes passed.
The synthetic UV orientation/repeat probe passed; camera/normalization checks
match the legacy foreground masks at 99.9997% of pixels (minimum view IoU
0.999768). See `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md` and
`bake_handoff/GLB_NATIVE_EGL_RENDER_V1/GLB_NATIVE_EGL_ANALYSIS.json`.

For `layer_llh − native_gfl`, the object-bootstrap estimates are:

| Endpoint | N=20 mean [95% CI] | N=19 excluding the preidentified extreme-UV UID |
|---|---:|---:|
| FG-PSNR | −0.422 dB [−1.361, +0.652] | −0.487 dB [−1.469, +0.631] |
| FG-LPIPS | −0.01175 [−0.01988, −0.00564] | −0.01129 [−0.01975, −0.00507] |
| CIEDE2000 | +2.563 [−1.007, +5.893] | +2.970 [−0.689, +6.421] |

The signs are mixed: LPIPS favors LLH, PSNR does not support an LLH advantage,
and the CIEDE2000 point estimate favors GFL. These values do not establish
overall 3D quality superiority. They replace the old renderer's invalid
metrics only for the stored outputs; the textures were not rebaked and the
renderer is unlit base-color, not full PBR.

P1-9 is closed for this supported N=20/eight-condition evaluation. Four
source objects without UV layers remain excluded, so strict N=24 3D coverage
is unsupported. The current C12 claim is `PARTIAL`, not a positive win.
Human-perceived material fidelity remains open.

## Remaining closure gates

| Gate | State | What remains |
|---|---|---|
| Scientific issue ledger | **E0 authority bookkeeping PASS; P0=0; scoped scientific P1=0** | The 14-claim/38-source ledger validates locally, including registration, cohort selection, intervention profiles, estimators and multiplicity fields. This bookkeeping pass does not close human, novelty, seam, or paper-wide reconstruction gates; preserve N=20 GLB and four no-UV limits. |
| Causal identification | **BOUNDED** | Keep A3b dose scope explicit; no dose-independent interaction or equal-dose wording. |
| E1 realization sensitivity | **PASS / BOUNDED** | Integrity passed; effects are conditional on the reused 48-object subset and three fixed seeds. |
| E2 static factorial | **PASS / BOUNDED** | 576 logical rows audited; deep+middle and shallow effects are profile-specific; no temporal variation or equal-dose identification. |
| Independent confirmation | **PARTIAL** | Additional practical/narrative safeguards postdate B exposure; label that chronology. |
| Perceptual validity | **OPEN** | Recruit fixed 40 slots, stop when resolved, and report all eight endpoints; minimum 36 valid participants. |
| Strict 3D cohort coverage | **OPEN for N=24** | Four no-UV sources were excluded before bake; either preserve N=20 scope or justify a separate UV policy. |
| Generalization | **BOUNDED** | Report MV-Adapter (98/99) and MVDiffusion (75) separately as interface-specific results; no pooled scores or causal architecture claim. |
| Reproducibility | **PARTIAL** | Full paper-wide table/figure reconstruction and portable clean-clone rebuild remain incomplete. |
| Reviewer closure | **PRE-REWRITE; SOURCE MAPPED** | User-designated second-round source matches the archived substantive R1/R2/R3 comments. R1 human fidelity remains open; R2 contribution adequacy remains blocking. |
| Manuscript forensic audit | **OPEN** | Manuscript remains unchanged; after evidence closure and an authorized rewrite, rebuild every table/figure and run the post-rewrite review. |

No responses to the new LLH study, participant contact, study distribution,
third-backbone campaign, FRESH_CONFIRM_C search, bake regeneration, submitted
manuscript edit, or remote push occurred in this audit. Manuscript files remain
byte-identical to the prior freeze check.

## Credibility continuation refresh — 2026-10-06

See `continuation_20261006/REVIEWER_CONTINUATION_PLAN.md` for the reviewer-led
next steps and `continuation_20261006/EVIDENCE_REFRESH.json` for the separate
read-only refresh. The user will supply real human responses later; the
human gate remains open. A new coordinator-only entry checks all 40 slots
are resolved and at least 36 responses are valid before invoking the unchanged
frozen analyzer. No human outcomes or manuscript edits were made. The supplied
reviewer source closes the missing-source bookkeeping issue, not substantive
reviewer acceptance or methodological novelty.

The subsequent E1 multi-seed and E2 static-factor campaigns, their integrity
and provenance gates, the 01549 narrative disposition, and the claim-to-evidence
map are recorded in `next_stage_20261006/MULTISEED_ANALYSIS.md`,
`next_stage_20261006/STATIC_FACTORIAL_ANALYSIS.md`,
`next_stage_20261006/NARRATIVE_DECISION_MAP.md`, and
`next_stage_20261006/EVIDENCE_CHAIN_20261006.md`.
