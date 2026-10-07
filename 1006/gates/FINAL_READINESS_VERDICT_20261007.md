# Final readiness verdict — updated 2026-10-07

## Current decision

| Gate | Status | Meaning |
|---|---|---|
| Scientific evidence freeze | **YES — bounded claims only** | The four P0 evidence gates pass under the revised human-study policy. See `SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md`. |
| Confirmatory human endpoint analysis | **PASS — documented execution deviations** | The owner-confirmed study retains its prespecified confirmatory status; 37 valid participants, all eight endpoints and the Holm family are analyzed. No endpoint supports an adjusted LLH preference advantage. Assignment/stimulus provenance limitations are disclosed and do not downgrade the analysis to sensitivity evidence. See `HUMAN_STUDY_GATE_VERDICT_20261007.md`. |
| Manuscript rewrite | **AUTHORIZED; NOT COMPLETE** | Use a separate revision candidate. Preserve the submitted 01549 files and include the old C3 3AFC only within its original scope. |
| Reviewer closure | **PARTIAL** | R1 claims are evidence-bounded, but the final manuscript and point-by-point response still need edits and a fresh reviewer pass. R2.1 contribution sufficiency remains an editorial risk. |
| Scientific claim readiness | **YES, with explicit limits** | No universal winner, LLH human-preference advantage, direct reference-fidelity claim from the new export, dose-independent mechanism, seam gain, broad 3D/PBR claim, or cross-interface transfer law. |
| Public release | **NO — governance review open** | The aggregate confirmatory endpoint table/plot and analysis code are prepared for the evidence branch. The anonymous participant-level CSVs were already uploaded on the source branch by explicit instruction; this update does not copy them again. Continued public availability, consent/ethics documentation, and source-image attribution remain separate release checks. |
| Direct system upload | **NO — HOLD** | Final revised source, response, clean package rebuild, page/line mapping, attribution/data checks, and the R2.1 venue decision are incomplete. |

## Human evidence in the final narrative

The existing 24-participant, 30-object 3AFC is the primary complementary perceptual-preference evidence for the original C3/TCAS comparison. It reports C3 overall-quality preference of 58.1% (95% participant×object cluster-bootstrap CI [50.1%, 65.8%]); conservative scale leads on texture naturalness and aggressive scale on shape consistency. It supports a preferred balance among those original conditions, not direct reference fidelity or any later LLH result.

The uploaded 40-slot response set has a complete analysis of the pre-specified confirmatory endpoint family with documented execution deviations: 37 valid respondents, 24 objects, eight paired preference endpoints, two-way participant/object bootstrap, pointwise intervals, and one Holm family. All point estimates favor LLH, none passes Holm, and the generic-linear endpoints are near 0.54 with intervals crossing 0.5. The result supports no adjusted LLH preference advantage, equivalence, or non-inferiority claim. Exact assignment/stimulus provenance and ethics/consent records remain limited. Full results and allowed wording are in `evidence/human_study/HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md`.

## Frozen empirical basis

- **Fresh C:** N=300 revision-era cohort; original four-condition primary and separate LLH/linear addendum both pass integrity. C3−GFL FG-PSNR is +0.522 dB [0.404, 0.641], with 68.7% favorable objects. The chronology label and object/endpoint heterogeneity remain in the narrative.
- **Qualitative:** the pre-outcome GT-only Visualization-24 archive includes the reference, no-adapter, fixed-scale controls and C3 across six views; it also records visible color/material and detail failures. It is descriptive, not a blinded human estimate.
- **Historical evidence:** strict-276 remains retrospective with incomplete legacy runner/input hashes. The N=20 GLB-native result is an unlit base-color unseen-view supplement with mixed endpoints. The proposed new 24-object bake and seam claim are retired.
- **Statistics:** Fresh C direction/multiplicity checks pass. Zero-crossing intervals are “not detected,” not equivalence. Endpoint trade-offs, including Edge-SSIM and generic-linear LPIPS, stay visible.

The submitted 01549 PDF/source remain preserved and unchanged as verified at the time of this update. The `1006` candidate is not itself an authorized upload package until it is rewritten from the frozen sources and rebuilt cleanly.
