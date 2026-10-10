> **Superseded on 2026-10-08.** The author-confirmed correction in [ROUND1_01549_TO_ROUND2_1008_MAPPING.md](ROUND1_01549_TO_ROUND2_1008_MAPPING.md) and the updated [01549 reviewer reanalysis](01549_REVIEWER_REANALYSIS_20261008.md) now govern this task. Do not follow any older statement that treats 01549 as an initial submission, leaves the round mapping formally open, requires Fresh C to match the historical Table 4 checkpoint hash, removes the reported FAC negative re-examination, or discards the first-round cluster-aware preference result. This file is retained as a dated audit trail.

# Joint R1/R2 targeted revision decision

**Decision: CASE B — evidence supports a truthful, selective revision with
explicit open limitations.** The paper identity remains TCAS/C3 on the
existing MVPainter-style geometry-adapter path. Do not start a new GPU run,
new bake, human study, or seam experiment for this pass. This decision report
does not edit the TeX or mark either reviewer concern closed.

## Answers to the seven revision questions

### 1. Which R2 evidence strengthens TCAS without changing its identity?

- A2 and Fresh B A3b show measurable response heterogeneity across the tested
  layer/window interventions. A3b is bounded; its raw-$L_2$ common-support
  test is dimension-confounded across groups, so it cannot establish or rule
  out equal-dose support, a dose-independent law, or C3 optimality.
- Fresh B LLH profile comparisons show that timing placement can matter on
  named contrasts: LLH−LFM-EXACT is within prespecified practical margins,
  LLH−HLL is heterogeneous on FG-PSNR, and LLH−LLL changes requested
  intensity as well as placement. In the post-lock same-cohort generic
  schedule extension, LLH beats four nominal-budget-matched schedules on
  paired means, but endpoint-matched linear favors on FG-LPIPS. The
  post-scale norms remain different, and a post-outcome dose-conditioned
  analysis is inconclusive. These are evidence about LLH comparisons, not C3.
- Fresh C provides a revision-era N=300 image-space follow-up for
  C3−GFL FG-PSNR (+0.522 dB, 95% object-bootstrap CI [+0.404,+0.641]) and a
  separate LLH/linear addendum. These data strengthen the bounded test of
  C3's motivation, but they do not make TCAS a new general scheduling
  algorithm.

The actual method claim stays: a specific, training-free low-high-low
inference profile on the already described adapter path. Keep the name
TCAS, the three-stage `s(p)`, and C3=(1.25, 2.50, 1.25). Reframe the schedule
as a hypothesis tested against data; do not rename it or enlarge the symbol
set.

### 2. Which R1 evidence supports texture fidelity or unseen-view claims?

- Fresh C target-view PSNR/LPIPS and same-view panels support **image-space
  endpoint comparisons only**. They do not establish human-perceived material
  fidelity.
- The historical N=20 GLB-native results support a **bounded stored
  unlit-base-color unseen-view comparison** across 11 fixed cameras. They
  have mixed endpoints and do not establish overall 3D superiority.
- No valid full PBR or seam endpoint is available. The Fresh C 24-object
  bake is retired after its technical gate failed.

### 3. Which evidence is only image-space evidence?

All Fresh C N=300 numerical results, the Fresh C 20-object visual gallery,
and the Formal Visual-24 panels are image-space comparisons of reference and
generated target views. Their PSNR, LPIPS, SSIM, CLIP-IQA, and texture
variation metrics must stay attached to their named image endpoint. They do
not test UV addressing, exported GLB appearance, unseen cameras, PBR, seams,
or human perception.

### 4. Which results weaken C3 and must appear in the revision?

- On Fresh C, C3 is below Generic Linear by −0.593 dB FG-PSNR on the mean
  and is worse by +0.013512 FG-LPIPS; retain this main-text counter-result.
- LLH improves FG-LPIPS over C3 but has a heterogeneous FG-PSNR distribution
  and is not a unique winner over Generic Linear.
- In historical N=20 unseen views, C3 has no detected FG-PSNR advantage over
  GFL; LPIPS favors C3 while CIEDE2000 does not. GFH has lower LPIPS than C3.
- The Formal Visual-24 audit still records color/material mismatch and
  fine-detail loss across the schedule conditions. The artifact review does
  not identify these as C3-only failures.
- No validated seam, PBR, or updated human-preference advantage supports the
  old broad claims. The original 3AFC, if retained, is limited to its original
  conditions and questions.

These counter-results belong in the main paper's Results/Limitations. Generic
Linear must not be hidden in a hard-to-find appendix.

### 5. Is a new GPU experiment necessary?

**No, for the truthful bounded revision selected here.** Existing Fresh C
comparisons and the independently checked historical N=20 renders give
reviewable positive and negative evidence. Their limits can be stated
directly. Fully resolving seams, PBR material fidelity, or broader
population-level 3D performance would require a separately specified,
technically gated project; no such work is authorized or started in this
pass.

### 6. Which 01549 sections, tables, and figures should change?

| 01549 location | Proposed work |
|---|---|
| Abstract, p.1 / l.33 | Replace the +0.96 dB, CAI-optimality, texture-superiority, human-preference, and architecture-family claims with the Fresh C C3−GFL result, the Generic Linear/LLH trade-offs, and the limited endpoint scope. |
| Introduction §1 / ll.54–70 | Preserve the original problem and TCAS paper identity; narrow causal wording and contribution claims. State that scale diagnostics are not fidelity and the supported result is a bounded study of an existing adapter path. |
| Related Work §2.3 / ll.89–96 | Add a direct SSI comparison and acknowledge established layer/time scheduling. Retain the signal distinction from CFG and adapter residuals without claiming schedule-space novelty. |
| Method §3.2 / ll.139–153 | Keep TCAS, `s(p)`, and C3 exactly; rewrite stage explanations as an adapter-specific testable hypothesis. Remove the CAI proposition/proof as an optimality selector (ll.154–172). |
| Fixed-scale/texture results, including Fig. 4 / ll.270–286 | Preserve the original local texture-comparison purpose; replace or rebuild the visual evidence from the attribution-cleared Fresh C pool. Use texture statistics as diagnostics, not texture-fidelity proof. |
| Schedule comparison, Table `tab:probe` and Fig. 6 / ll.290–331 | Preserve the schedule-comparison purpose. Remove “only promising” and optimality language. Add the registered Fresh C result and show adverse Generic Linear and LLH endpoints in the main comparison. |
| Main 300-object result and diagnostics / ll.368–456 | Replace the old headline table/paragraph with Fresh C C3−GFL and the visible Generic Linear/LLH results. Keep each metric's scope explicit; do not use proxy diagnostics as perceptual proof. |
| Human preference / ll.458–480 | Remove the general preference-advantage claim. Any retained historic 3AFC result must stay limited to its original three methods, objects, and questions. |
| FAC and adapter dependence / ll.482–526 | Do not restore FAC as a contribution. Narrow retained interface checks to their own scope; remove “C3 wins in every regime” and any cross-backbone-success implication. |
| Limitations and Conclusion / ll.532–550 | State the Generic Linear/LLH counter-results, mixed N=20 endpoints, residual-dose limitations, and unvalidated seam/PBR endpoints. Conclude with a tested task-specific strategy rather than a general optimum. |

The proposed main visual layout keeps both original figure roles in the main
paper: Fig. 4 for same-view texture/appearance comparisons; Fig. 6 for the
schedule trade-off. The Fresh C candidates supply Reference, No adapter, GFL,
GFH, C3, LLH, and Generic Linear under one shared six-view layout. Use the
typical and favorable C3/GFL panels plus the GFH trade-off and Generic Linear
counterexample in the main figures. Keep the adverse C3/GFL and
color/pattern/detail failure panels in the supplement. Every selected panel
is illustrative, not representative.

The N=20 unlit-base-color figure can be a compact supplemental comparison
only if source-asset rights are cleared. It currently remains a local,
internal-only candidate. Preserve the original 01549 figures, supplement,
and audit archives; do not move the argument wholesale into supplementary
material or adopt the L-TCAS structure.

### 7. Which reviewer concerns can be answered fully or only partly?

| Concern | Status after bounded revision |
|---|---|
| R2.1 novelty | **Partially answered.** SSI is acknowledged and the claim narrowed; algorithmic novelty is not established. Journal contribution sufficiency remains an open editorial risk. |
| R1 color shifts / repeated patterns | **Partially answered.** Same-view full-object examples and fixed visual audit document both strengths and failures. No validated repetition measure or resolved color-fidelity claim exists. |
| R1 whole-object comparison | **Improved, still illustrative.** The 20 rights-cleared Fresh C panels are hash-verified but outcome-ranked. |
| R1 unmodified/competitive baselines | **Substantially answered in 2D.** No adapter, GFL, GFH, Generic Linear, and LLH appear; adverse Generic Linear results stay visible. |
| R1 baked unseen views | **Partially answered with valid bounded evidence.** Historical N=20 passes native render/hash/camera checks; endpoints are mixed, non-random, unlit base-color only. |
| R1 seams and PBR | **Open.** Seam endpoint is retired; no full PBR evidence. |
| R1 supplementary video access | **Open pending portal check.** The original files exist locally and hash correctly, but reviewer-side access cannot be verified from this workspace. |

## Final gates

`R2_NOVELTY_STRENGTH=PARTIAL`  
`R1_VISUAL_EVIDENCE=PARTIAL`  
`R1_BAKED_UNSEEN_VIEW=VALID_BOUNDED`  
`R1_SEAM_ENDPOINT=RETIRED`  
`NEW_EXPERIMENT_REQUIRED=NO`  
`01549_IDENTITY_PRESERVED=YES`  
`R2_1_VENUE_RISK=OPEN`

The evidence reports, paired CSVs, source manifests, and analysis scripts are
listed in the R1/R2 reports and source-evidence manifests. No status is
`CLOSED` or `SUBMISSION_READY`.
