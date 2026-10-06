# Response to the supplied reviewer comments — 1006 candidate

This response is mapped to the compiled 1006 candidate. The review file
retains “Initial submission” labels while discussing a revision; we respond
to the supplied substantive comments without inferring an unprovided editor
decision or later review. Page and line references below refer to
`manuscript/main_1006.pdf`; supplement references use its printed page
numbers. This is a submission-ready response **candidate**, not evidence that
the remaining editorial questions have been accepted.

## General revision

We reframed the paper as a bounded empirical characterization of inference-
time geometry-adapter scaling in one MVPainter-style residual path. The
revision distinguishes requested scales, implementation caps, and measured
post-scale residual norms; reports four FRESH_CONFIRM_B temporal contrasts
separately; and states that B's locks followed prior outcome exposure. It
withdraws the universal schedule winner, a dose-independent Layer × Window
mechanism, CAI-derived optimality, human-validated LLH fidelity, seam
improvement, and broad cross-backbone transfer claims. We added
*Scheduled Style Injection* as the closest prior work and discuss why this
limits any claim of general scheduling novelty.

## Reviewer 1

### R1.1 — Visible appearance errors, full-object comparisons, unseen views, seams

We agree that image-space metrics do not establish complete 3D appearance.
The supplement now shows a GT-stratified 24-object panel with the unmodified
pipeline and fixed-scale controls (Supplement S5, pp. 2–8). A sampler-
conformant evaluation of the exact stored GLBs covers 20 UV-supported objects,
eight stored conditions, and 11 unseen views per object-condition (main
Section 4.4, p. 4, lines 240–261; Supplement S5). Its FG-PSNR, FG-LPIPS, and
CIEDE2000 results are mixed, so we claim no overall 3D winner. Four no-UV
objects are excluded; the textures were not rebaked; the render is unlit
base-color rather than full PBR; and the legacy seam analyzer is invalid for
these exported UVs. We therefore remove the seam claim. No LLH human responses
were collected, and the earlier 01549 study is not transferred to LLH or
unseen-view fidelity (Supplement S8, p. 9).

**Disposition:** the candidate adds the requested unseen-view endpoint and
full-object comparisons, while perceived material fidelity and seam
consistency remain unverified. We do not claim those gates are closed.

### R1.2 — Main adapter and baselines on a disjoint held-out set

We retire the submitted pooled +0.96 dB result as an independently confirmed
effect. On strict-276, retrospective GC3−GFL FG-PSNR is +1.208 dB (nominal
95% object-bootstrap CI [1.117, 1.295], 259/276 favorable) and Edge-SSIM is
+0.00776 [0.00677, 0.00875] (233/276). The comparison was not a registered
primary Core-7 contrast, and the legacy input-tensor hash chain and common
runner identity are incomplete. GC3 also trades endpoints against GFH: five
of seven directions favor GFH, including FG-PSNR and Edge-SSIM (main
Section 4.5, pp. 4–5, lines 263–282; Supplement S6, pp. 9–11).

We additionally report native-GC3−native-GFL on disjoint FRESH_CONFIRM_B
objects: FG-PSNR +0.502 dB [0.342, 0.663] (100/150) and Edge-SSIM +0.00503
[0.00335, 0.00675] (105/150), with all seven Core-7 cohort means favoring
GC3. This pair was selected after B had been unblinded and was not registered.
We label it retrospective evidence on a separate object cohort, not a
prospective or registered confirmation (main Section 4.5, p. 5, lines
263–282; Supplement S6, pp. 9–11). We do not substitute LLH for C3.

**Disposition:** the new disjoint-object comparison strengthens the
descriptive evidence, but strict prospective confirmation remains open if
the editor requires it. The previously screened 508-object candidate pool
has no eligible unused subset; a prospective run would require a newly
sourced and audited cohort.

### R1.3 — Texture variation versus fidelity

We now treat Laplacian variance, color spread, gradients, and high-frequency
energy as variation diagnostics, not as stand-alone fidelity measures (main
Sections 1–2, pp. 1–2). The author-only visual audit found color/material
mismatch in 18/24 panels and fine-detail loss in 21/24; it is explicitly
descriptive and not a participant study (main Section 4.4, p. 4, lines
240–261). GLB endpoints are reported separately, and no LLH human-fidelity
claim is made.

**Disposition:** addressed by separating the evidence types and narrowing
the claim. The present work does not establish human-perceived material
fidelity.

### R1.4 — Paired intervals, Edge-SSIM, and non-inferiority

We agree that a confidence interval crossing zero does not establish
equivalence. The candidate reports paired object-bootstrap intervals and
Edge-SSIM for both strict-276 GC3 comparisons (Supplement S6, pp. 9–11).
The frozen ±0.5 dB and ±0.01 practical margins apply only to the specified
LLH−LFM-exact FG-PSNR and FG-LPIPS endpoints (main Section 3.4, p. 3,
lines 157–171). We make no general non-inferiority or equivalence claim.

**Disposition:** addressed for the candidate's stated scope; historical C3
comparisons remain retrospective and nominal.

### R1.5 — FAC reproducibility

FAC is absent from the revised method and contribution claims and is not used
as evidence for the current paper. We have not presented its archived
reconstruction as a portable reproduction package.

**Disposition:** removed by scope reduction. If FAC is reinstated, its
training code, source rows, checkpoint identity, and clean-clone results must
be released and audited.

## Reviewer 2

### R2.1 — Contribution beyond schedule selection

We agree that the earlier novelty framing was too broad. The paper now cites
*Scheduled Style Injection*, which varies parameters across layer depth and
denoising time and also studies geometric ControlNet schedules. We do not
claim novelty for the axes or the general scheduling idea (main Sections 1
and 2.2, pp. 1–2, lines 22–24 and 71–83). The contribution is narrowed to a
measured account of requested-scale/cap semantics and post-scale correction
norms in this MVPainter-style path, object-level response heterogeneity,
bounded static-scale and realization sensitivity, and the tested GLB-native
endpoint (main Discussion, pp. 5–6, lines 305–315 and 332–355).

We recognize that this scope may still be too incremental for the journal.
The experiments do not independently establish that the remaining empirical
contribution meets the venue's novelty threshold; we do not use claim
reduction as a substitute for that judgment.

### R2.2 — CAI as a post-hoc explanation

CAI is not presented as a predictive derivation, a source of the selected
schedule, or evidence for an optimum. We removed the CAI-based optimality
claim from the candidate.

**Disposition:** addressed by claim reduction; no prospective CAI prediction
test is claimed.

### R2.3 — Cross-backbone generalization

MV-Adapter and MVDiffusion are reported separately as boundary evidence for
their tested interfaces. The candidate gives the 98/99 evaluable MV-Adapter
objects and the 75-object MVDiffusion CPBlock result, explains that the
interventions differ, and does not pool metrics or infer an architecture-
caused schedule effect (main Section 4.5, p. 5, lines 283–304; Supplement S7,
p. 9).

**Disposition:** broad transfer claims are withdrawn. Transfer across these
tested interfaces has not been established.

## Reviewer 3

We thank Reviewer 3 for the favorable assessment. No separate actionable
concern appears in the supplied comments. This does not waive the R1/R2
limitations described above.

## Remaining decision points

The candidate is not represented as fully reviewer-closed. Human-perceived
fidelity and seams remain unsupported; the C3−GFL B analysis is retrospective;
asset release has two snapshot-only license records; and R2.1 remains an
editorial contribution judgment. The final readiness gate records these
limits and currently does not clear direct system upload.
