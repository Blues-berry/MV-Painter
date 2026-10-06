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
  no corrected global interaction in its tested intervention range. Do not
  change groupings or scales to seek a positive; a third backbone is not
  justified by these results.
- **Human study is now the next high-value evidence gate.** B is complete and
  unblinded. The site and final four-pair lock are ready: 40 assignment slots,
  fixed stop, 24 comparisons per participant, at least 36 valid completions,
  and LLH versus four comparators including `gen_linear`. No responses have
  been collected; recruitment and the CSV return route remain to be arranged.

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
| Scientific issue ledger | **P0=0; scoped scientific P1=0** | Preserve the N=20 GLB and four no-UV limits; operational P1-2 remains open. |
| Causal identification | **BOUNDED** | Keep A3b dose scope explicit; no dose-independent interaction or equal-dose wording. |
| Independent confirmation | **PARTIAL** | Additional practical/narrative safeguards postdate B exposure; label that chronology. |
| Perceptual validity | **OPEN** | Recruit fixed 40 slots, stop when resolved, and report all eight endpoints; minimum 36 valid participants. |
| Strict 3D cohort coverage | **OPEN for N=24** | Four no-UV sources were excluded before bake; either preserve N=20 scope or justify a separate UV policy. |
| Generalization | **BOUNDED** | Keep the MV-Adapter result scoped; no third backbone. |
| Reproducibility | **PARTIAL** | Full paper-wide table/figure reconstruction and portable clean-clone rebuild remain incomplete. |
| Reviewer closure | **PRE-REWRITE** | Only initial R1/R2/R3 comments are archived; no separate round-two report was found. |
| Manuscript forensic audit | **OPEN** | Manuscript remains unchanged; after evidence closure and an authorized rewrite, rebuild every table/figure and run the post-rewrite review. |

No human responses, participant contact, study distribution, third-backbone
campaign, FRESH_CONFIRM_C search, bake regeneration, manuscript edit, or remote
push occurred in this audit. Manuscript files remain byte-identical to the
prior freeze check.
