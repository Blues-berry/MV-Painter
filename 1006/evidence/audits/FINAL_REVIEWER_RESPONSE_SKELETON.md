# Reviewer response skeleton

This is a structure for later author review, not a final response letter. Every item follows the required chain: **Reviewer concern → Evidence → Manuscript action → Remaining limitation**.

## R1 held-out evidence

- **Reviewer concern:** The schedule result may depend on the observed development cohort.
- **Evidence:** Fresh C is a revision-era N=300 object cohort; original four-condition run passed 1200/1200 rows and the LLH/generic-linear addendum passed 600/600. The C3−GFL FG-PSNR contrast is +0.522 dB (95% object bootstrap CI [+0.404,+0.641]); strict-276 remains retrospective only.
- **Manuscript action:** Use Fresh C as the primary revision-era image-space evidence; keep strict-276 as retrospective support.
- **Remaining limitation:** Fresh C was not an original-preregistration replication. Human preference evidence applies to the original C3/TCAS conditions only and does not establish LLH preference or direct reference fidelity.

## R1 visual fidelity

- **Reviewer concern:** Image metrics or texture variation may not establish perceptual fidelity.
- **Evidence:** The GT-only 24-object visual audit includes controls and failure cases. The original 01549 3AFC reports C3 overall-quality preference 58.1% (95% participant×object bootstrap CI [50.1%, 65.8%]) among its original three conditions. The later prespecified four-comparator study has 37 valid respondents and eight confirmatory endpoints; none survives Holm correction. Assignment, side-order, stimulus-hash, closeout, and consent/ethics provenance limitations are disclosed. Historical N=20 GLB-native results are unlit base-color only with mixed endpoints.
- **Manuscript action:** Retain the old 3AFC as C3/TCAS complementary preference evidence; do not transfer it to LLH. Include the complete confirmatory endpoint table and execution deviations in Supplement S8. The appearance item asked about relative matching to the visible reference, but the estimates do not support an adjusted LLH-preference advantage or broad fidelity claim. Separate image metrics and variation diagnostics; remove unsupported seam/full-PBR claims.
- **Remaining limitation:** No adjusted LLH preference advantage or absolute human reference-fidelity claim is established. Unseen-view evidence remains limited to stored unlit base-color outputs.

## R1 fairness

- **Reviewer concern:** Comparisons may omit strong or generic controls.
- **Evidence:** Fresh C reports no-adapter, GFL, GFH, C3, LLH, and generic linear on the frozen comparison cohort and analysis family.
- **Manuscript action:** Present all six methods and endpoint-specific results together, including adverse and mixed comparisons.
- **Remaining limitation:** No method is a cross-metric unique winner; no equal-realized-dose comparison exists.

## R1 statistical reporting

- **Reviewer concern:** Object dependence, multiplicity, or sign interpretation may be unclear.
- **Evidence:** The numerical authority table records N, mean, median, object bootstrap CI, raw/adjusted p-values, multiplicity family, favorable-object fraction, and the direction audit. Eleven views, where applicable to legacy 3D work, are not treated as independent objects.
- **Manuscript action:** Use object as the inferential unit, name each Holm family, state lower-is-better LPIPS direction, and show paired distributions.
- **Remaining limitation:** Non-significance is not equivalence; mean effects do not imply a typical-object gain.

## R2.1 novelty and contribution

- **Reviewer concern:** The contribution may be incremental relative to layer/timestep scheduling work.
- **Evidence:** Scheduled Style Injection is direct prior work for layer-by-timestep style-strength schedules. Fresh C and execution logs support bounded MVPainter-specific intervention accounting and endpoint/object heterogeneity.
- **Manuscript action:** Acknowledge SSI and related precedents; remove “first,” “novel control space,” and schedule-optimality claims. Describe the contribution as implementation-aware empirical characterization.
- **Remaining limitation:** R2.1 remains open as a venue-level judgment; the data do not demonstrate equal-realized-dose causal effects.

## R2.2 CAI

- **Reviewer concern:** CAI may be post-hoc and not predictive.
- **Evidence:** No prospective independent-cohort prediction is established; the disposition is `DESCRIPTIVE_ONLY`.
- **Manuscript action:** Remove CAI from load-bearing contributions and move the complete formulation to supplement.
- **Remaining limitation:** CAI does not select a unique schedule or independently predict a Fresh C winner.

## R2.3 cross-backbone/interface generality

- **Reviewer concern:** The primary-backbone result may be asserted as universal.
- **Evidence:** MV-Adapter and MVDiffusion use different tested interfaces and have bounded, non-identical results.
- **Manuscript action:** Report each interface separately as a boundary case; do not pool or infer architecture causality.
- **Remaining limitation:** The evidence supports only the tested interfaces, not universal transfer or universal absence of interaction.

## Rights and release hygiene

- **Reviewer concern:** Asset and participant data may not be cleared for public redistribution.
- **Evidence:** The asset ledger contains UNKNOWN and attribution-dependent records; participant-level human files are present in the public remote tree without located consent/ethics/data-handling records.
- **Manuscript action:** Keep source GLBs and participant-level records out of any new public package; use only cleared aggregate material.
- **Remaining limitation:** Rights and public-release review are not closed; no history rewrite has been performed.
