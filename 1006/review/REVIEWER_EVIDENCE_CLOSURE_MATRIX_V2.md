# Reviewer evidence closure matrix V2 — 2026-10-07

**Scope:** supplied R1–R3 set only; non-human evidence only. The 01549 main source and supplement have been revised and compiled; the external response now points to verified locations. Evidence statuses retain the controlled values from the plan, and no reviewer item is marked closed. `READY_TO_EDIT` remains the allowed manuscript-status label; it does not assert reviewer closure.

## R1.1 — Visual artifacts, broader comparisons, unseen views, seams, and video

- **Exact reviewer concern:** “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance.” The reviewer requests whole-object comparisons with the unmodified pipeline and a competitive fixed-scale baseline, baked unseen views, and seam/cross-view assessment; the supplementary video could not be assessed.
- **Direct evidence:** [Formal visual evidence report](../evidence/audits/FORMAL_VISUAL_EVIDENCE_REPORT.md); [rights-cleared Fresh C visual candidate pool audit](REVIEWER_VISUAL_CANDIDATE_POOL_AUDIT.md); [candidate pool index](REVIEWER_VISUAL_CANDIDATE_INDEX.csv).
- **Supporting evidence:** [retired 3D claim disposition](../evidence/audits/3D_CLAIM_RETIRED.md); [final seam disposition](../evidence/audits/SEAM_CLAIM_FINAL_DISPOSITION_20261007.md); [asset-rights disposition](../evidence/audits/FINAL_ASSET_RIGHTS_DISPOSITION_20261007.md).
- **Evidence role:** selected rights-cleared image-space panels can illustrate the visible behavior and include the unmodified and tested strategies; claim withdrawal resolves unsupported 3D/seam superiority claims.
- **Evidence limitation:** panels are curated illustrations, not a statistical sample. The available native-UV/sampler validation does not support a valid new bake comparison; the historical unlit base-color result does not establish PBR fidelity or seam consistency. Visual inspection is descriptive and not cohort-wide evidence.
- **Final response logic:** acknowledge visible failures and metric/fidelity separation; explain that selected panels are illustrative; withdraw unsupported 3D/seam claims; limit any video to demonstration.
- **Manuscript action:** implemented: added the selected, attributed side-by-side image-space examples; removed unsupported 3D/seam superiority claims; bounded image-space and video evidence. Main-paper locations: p. 2, lines 66–69; p. 4, lines 279–289 and 318–325; Fig. 4, p. 8.
- **Remaining blocker:** unseen-view, baked-texture, material, and seam quality remain unvalidated; the revision explicitly withdraws those claims. No item-specific edit remains.
- **Evidence status:** PARTIAL.
- **Manuscript status:** READY_TO_EDIT.

## R1.2 — Main-adapter evaluation beyond schedule-selection data

- **Exact reviewer concern:** the pooled evaluation included schedule-selection objects, while the earlier probe-disjoint table changed the adapter and competitors; “Please evaluate the main adapter and relevant baselines under the same held-out protocol.”
- **Direct evidence:** Fresh C registered C3−GFL FG-PSNR row in [numerical authority](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv): N=300, +0.522 dB, 95% object-bootstrap CI [+0.404, +0.641], 68.7% object-favorable fraction.
- **Supporting evidence:** Fresh C four-condition paired source, integrity-gated analysis, and comparator results in [result authority registry](../evidence/audits/RESULT_AUTHORITY_REGISTRY.csv); historical strict-276 remains classified as retrospective support.
- **Evidence role:** revision-era direct evaluation of the main adapter on one frozen cohort, with the registered primary contrast separated from retrospective estimates.
- **Evidence limitation:** follow-up was motivated by earlier results; it is not a replication under the original registration and does not validate the historical +0.96 dB estimate or establish portability beyond the tested cohort and implementation.
- **Final response logic:** report Fresh C with its cohort, adapter, comparator, registration status, endpoint, and uncertainty; retain historical estimates only as retrospective support.
- **Manuscript action:** implemented: Fresh C protocol and registration caveat on p. 3, lines 195–212; primary result on p. 4, lines 248–255. Full comparator results are in the main text and supplement.
- **Remaining blocker:** none item-specific; final package/reproducibility gate remains open.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R1.3 — Texture variation versus texture fidelity

- **Exact reviewer concern:** “Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”
- **Direct evidence:** [149-row sentence-level fidelity-language audit](R1_3_FIDELITY_LANGUAGE_AUDIT.csv); descriptive artifact findings in [formal visual evidence report](../evidence/audits/FORMAL_VISUAL_EVIDENCE_REPORT.md).
- **Supporting evidence:** Fresh C metric authority and selected panels are kept endpoint-specific; no author-inspection count is treated as a population rate.
- **Evidence role:** identifies where variation metrics were interpreted too strongly and supplies the concrete wording correction.
- **Evidence limitation:** this phase does not inspect or analyze participant-level human responses and does not verify any human-preference claim.
- **Final response logic:** agree that variation is not fidelity; describe texture statistics as variation diagnostics; state that image metrics and illustrative panels do not establish perceptual fidelity.
- **Manuscript action:** implemented: variation metrics and image-space endpoints are separated on p. 3, lines 159–177; fidelity limits are stated on p. 4, lines 318–325.
- **Remaining blocker:** no participant-level responses were analyzed; this matrix makes no human-preference claim. No item-specific text edit remains.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R1.4 — Paired intervals, Edge-SSIM trade-off, and non-inferiority

- **Exact reviewer concern:** a confidence interval crossing zero does not establish equivalence or non-inferiority; Table 4 shows lower Edge-SSIM for TCAS than aggressive scaling; report paired intervals, acknowledge the trade-off, or moderate the preservation claim.
- **Direct evidence:** Fresh C C3−GFH post-hoc Edge-SSIM and Full-PSNR rows in [numerical authority](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv), [result authority registry](../evidence/audits/RESULT_AUTHORITY_REGISTRY.csv), and the [Fresh C paired audit](R1_4_FRESHC_C3_minus_GFH_posthoc_audit_20261007.md). Edge-SSIM is −0.01881 (nominal 95% paired object-bootstrap CI [−0.02080, −0.01679]); 47/300 favor C3. Full-PSNR is +0.6607 (95% CI [+0.5858, +0.7358]); 252/300 favor C3.
- **Supporting evidence:** the separate Fresh B analysis is retained as a retrospective/post-hoc supporting sensitivity and is not pooled with Fresh C. Its seven machine-readable rows are now in both authority tables and link to the pinned-source analysis; source-integrity and sign-direction audits are also recorded.
- **Evidence role:** direct reviewer-requested paired, endpoint-specific post-hoc comparison on the same frozen Fresh C cohort; the opposite Full-PSNR direction documents the trade-off.
- **Evidence limitation:** the C3−GFH analysis is post hoc, its intervals are nominal, and no non-inferiority margin was prespecified. It cannot support equivalence, non-inferiority, or a universal/typical-object claim.
- **Final response logic:** explicitly reject equivalence/non-inferiority, report the Edge-SSIM loss and Full-PSNR trade-off, and label both as post hoc.
- **Manuscript action:** implemented: Fresh C C3−GFH post-hoc status on p. 3, lines 223–227; Edge-SSIM/full-PSNR trade-off and limits on p. 4, lines 268–278; full tables in Supplement S4–S5, p. 2.
- **Remaining blocker:** none item-specific; final package/reproducibility gate remains open.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R1.5 — FAC reproducibility and code release

- **Exact reviewer concern:** “it is still hard to reproduce the FAC experiments. The code is encouraged to be released,”
- **Direct evidence:** artifact-level [FAC final disposition](FAC_FINAL_DISPOSITION.md), which selects REMOVED_FROM_REVISION.
- **Supporting evidence:** [current clean-checkout audit](CLEAN_CHECKOUT_REPRODUCIBILITY_ADDENDUM_20261007.md), the historical snapshot report (../evidence/audits/FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md), FAC config/training-pool mismatch, missing run-bound manifests, and absent training-seed provenance.
- **Evidence role:** supports a concrete removal decision instead of a reproducibility or release claim.
- **Evidence limitation:** historical artifacts exist, but the exact run cannot be reconstructed from a clean checkout; this is a provenance audit, not a recomputation of FAC results.
- **Final response logic:** agree that the historical FAC evidence does not meet this revision’s reproducibility standard and state that it will be removed.
- **Manuscript action:** implemented: FAC methods, results, dose-response material, and reproducibility claims are absent from the revised main manuscript and supplement.
- **Remaining blocker:** none item-specific; final package/reproducibility gate remains open.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R2.1 — Methodological contribution and novelty

- **Exact reviewer concern:** “The core methodological contribution remains quite limited” beyond schedule selection for an existing adapter; “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”
- **Direct evidence:** bounded two-item [final contribution set](FINAL_R21_CONTRIBUTION_SET.md); Fresh C registered and post-hoc results in [numerical authority](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv); requested/applied/residual accounting in the [execution-semantics summary](../evidence/audits/FRESH_C_EXECUTION_SEMANTICS_FINAL_REPORT.md) and [representative logged rows](../evidence/audits/FRESH_C_EXECUTION_SEMANTICS_REPRESENTATIVE.csv).
- **Supporting evidence:** prior-work comparison in the contribution audit and citations to Scheduled Style Injection and timestep-dependent guidance in the response draft.
- **Evidence role:** supports a narrower empirical contribution: implementation-aware scale execution and object-/endpoint-dependent Fresh C evidence. Generic linear remains visible as a comparator that outperforms C3 on two reported endpoints.
- **Evidence limitation:** the work does not introduce the scheduling primitive, establish equal-realized-dose causality, derive a unique optimum, or establish that the contribution meets the venue’s novelty threshold.
- **Final response logic:** acknowledge prior art; remove first/novelty/optimality claims; state the two bounded empirical contributions; preserve generic-linear counterevidence and endpoint-specific interpretation.
- **Manuscript action:** implemented: revised title, abstract, prior-work framing, contributions, results, and conclusion; generic linear is reported alongside C3. Main locations: p. 2, lines 43–69 and 116–138; p. 3, lines 151–158; p. 4, lines 256–267.
- **Remaining blocker:** formal rewrite; editorial significance remains an open venue risk, not an evidence-generation task.
- **Evidence status:** PARTIAL.
- **Manuscript status:** READY_TO_EDIT.

## R2.2 — CAI as a post-hoc rationale

- **Exact reviewer concern:** “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”
- **Direct evidence:** final CAI disposition in [CAI manuscript action](CAI_MANUSCRIPT_ACTION.md) and [CAI evidence disposition](../evidence/audits/CAI_FINAL_DISPOSITION.md).
- **Supporting evidence:** predictive-value decision in the scientific-validation archive; no new experiment is required or authorized.
- **Evidence role:** supports removing CAI from the core. Although the planning disposition permits supplement-only treatment if useful, no CAI diagnostic is retained in this revision.
- **Evidence limitation:** CAI is not prospective, predictive, unique, or independently validated as a schedule selector.
- **Final response logic:** agree with the reviewer and remove derivation, selection-rule, predictive, and optimality claims.
- **Manuscript action:** implemented: removed the CAI model, proposition, selector, and optimality framing from the main source; no CAI description remains in the supplement.
- **Remaining blocker:** none item-specific; final package/reproducibility gate remains open.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R2.3 — Generalization to a different backbone

- **Exact reviewer concern:** cross-backbone generalization is “the most important missing experiment”; the primary architecture family does not establish generality.
- **Direct evidence:** existing MVDiffusion and MV-Adapter boundary reports in the read-only source workspace at /4T/CXY/MV-Painter/1006/evidence/audits/MVDIFFUSION_STANDARD_PANEL_REPORT.md and /4T/CXY/MV-Painter/1006/evidence/audits/CROSS_BACKBONE_MECHANISM_REPORT.md.
- **Supporting evidence:** current internal response wording distinguishes the MVDiffusion compatibility-base panel from the primary residual-adapter intervention and records the exploratory MV-Adapter interaction result.
- **Evidence role:** identifies the limits and mixed behavior across tested interfaces; supports a boundary statement, not a generalization claim.
- **Evidence limitation:** these studies are not matched replications of the same intervention; official MVDiffusion depth weights were unavailable; they do not establish universal transfer or architecture-level causality.
- **Final response logic:** agree that generality is unestablished, report the existing studies as interface-specific boundary tests, and withdraw universal-transfer/architecture-causal language.
- **Manuscript action:** implemented: interface-specific boundary tests and compatibility-base limitation appear on p. 4, lines 290–309 and 327–335, and Supplement S6, p. 2.
- **Remaining blocker:** broader transfer remains unestablished; no item-specific edit remains and no new backbone experiment is planned.
- **Evidence status:** READY.
- **Manuscript status:** READY_TO_EDIT.

## R3 — Positive assessment

- **Exact reviewer concern:** “The revision now looks good for publication.”
- **Direct evidence:** the supplied CAG-D-26-00962 reviewer export.
- **Supporting evidence:** none needed.
- **Evidence role:** positive assessment; no technical claim or experiment is requested.
- **Evidence limitation:** does not remove the need to address R1/R2.
- **Final response logic:** thank the reviewer.
- **Manuscript action:** no additional manuscript change required; the external response thanks the reviewer.
- **Remaining blocker:** none for this item.
- **Evidence status:** READY.
- **Manuscript status:** NOT_STARTED.

## Closure rule

No item is marked CLOSED. The manuscript edit, compilation, and page/line-linked external response are complete. Reviewer closure still requires final evidence/package review, including the open clean-checkout reproducibility gate.
