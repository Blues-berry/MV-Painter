# Scientific evidence freeze verdict — 2026-10-07

## Verdict

`SCIENTIFIC_EVIDENCE_FREEZE = YES` for the bounded claims and endpoint scope recorded below. The original 01549 3AFC remains complementary evidence for C3/TCAS. The later 40-slot study is now classified as a prespecified confirmatory human-preference analysis with documented execution deviations; its null multiplicity-adjusted findings and limited 2D scope do not expand the paper's positive claims or block the other evidence gates.

This verdict freezes the evidence base and authorizes the post-freeze manuscript rewrite. It does **not** mean that R1/R2 are fully closed, that R2.1 contribution sufficiency is settled, or that the paper is ready for system upload. The submitted 01549 source and PDF remain unchanged.

## Four P0 gates

| P0 gate | Status | Evidence and allowed scope |
|---|---|---|
| Held-out fairness | **PASS — revision-era, scope-limited** | Fresh C uses an independently frozen 300-object cohort. The original four conditions passed 1,200/1,200 rows; the separately locked LLH/linear addendum passed 600/600 rows on the same cohort, runner, checkpoint, seed, inputs and native-cap semantics. The primary C3−GFL FG-PSNR estimate is +0.522 dB (95% object-bootstrap CI [+0.404, +0.641]); 68.7% of objects favor C3. The 28-check sign/multiplicity audit found no direction errors. This is a revision-era follow-up, not a replication of the original 01549 preregistration; LLH/linear results remain endpoint- and object-dependent. See `evidence/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md` and `data/fresh_c/`.
| Broader full-object qualitative | **PASS — descriptive, fixed sample** | The GT-only Visualization-24 cohort was stratified and frozen before method metrics; its complete six-view panels include GT, no-adapter, fixed-low, fixed-high, C3, and temporal profiles with shared latents. It documents color/material mismatch in 18/24, fine-detail loss in 21/24, and visible small/thin-part failures. This provides failures and controls without using the outcome-ranked Fresh C gallery as the sole qualitative evidence. It is a bounded author visual audit, not a blind human or population estimate. See `formal_qualitative_archive/archive_manifest.json`, `contact_sheet_24.png`, `FORMAL_VISUAL_EVIDENCE_REPORT.md`, and `1006/data/visual_panel_classification.csv`.
| Metric interpretation | **PASS — claim boundary fixed** | The post-freeze candidate states that Laplacian variance, color spread, gradient magnitude and high-frequency energy are variation diagnostics, not direct fidelity measures; PSNR/SSIM/LPIPS remain distinct image-space endpoints. Human preference is not called reference fidelity. The original manuscript will be edited only after this evidence freeze, using the bounded wording in `evidence/human_study/HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md` and the current 1006 claim candidate (`manuscript/main_1006.tex`, § Image and appearance metrics). No broad material-fidelity claim is authorized.
| Statistical claims | **PASS — with endpoint/provenance limits** | Fresh C paired estimates, intervals, object summaries, metric direction and Holm families pass the independent 28-check audit. The strict-276 re-evaluation is retrospective and incomplete in runner/input provenance; its Edge-SSIM improvement is reported alongside the opposing GC3−GFH trade-off. LLH−linear FG-PSNR crosses zero without an equivalence margin; it is described as “not detected,” never equivalent or non-inferior. Fresh C LLH−linear FG-LPIPS favors linear after Holm correction. See `DIRECTION_AND_SIGN_AUDIT_20261006.md`, `FORMAL_HOLM_FAMILY_AUDIT_20261006.md`, and the Fresh C report.

## Human-study disposition

- `EXISTING_3AFC_HUMAN_STUDY = PRIMARY_COMPLEMENTARY_PERCEPTUAL_EVIDENCE`: the submitted 01549 study reports 24 participants, 30 objects, 720 choices per criterion, participant×object bootstrap, and C3 overall-quality preference 58.1% [50.1%, 65.8%]. It supports a perceived balance among the original C3, conservative-scale and aggressive-scale conditions. It does not test LLH or directly measure reference fidelity, unseen views, baked meshes, seams, or full PBR.
- `UPLOADED_20261006_HUMAN_STUDY = CONFIRMATORY_ENDPOINT_ANALYSIS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS`: 37 field-valid respondents; all eight point estimates favor LLH, none passes Holm. The exact task assignment schedule, within-cell side randomization, question order, stimulus hashes, closeout record, and consent/ethics documentation are not fully verifiable. It supports reporting the prespecified relative 2D judgments but does not establish an LLH preference advantage, equivalence, absolute reference fidelity, or 3D quality. See `evidence/human_study/HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md`.
- `NEW_CONFIRMATORY_HUMAN_GATE = NOT_REQUIRED` for the current bounded manuscript. No further recruitment or reconstruction of historical human-study package files is required to freeze these claims.

Detailed results and permitted wording are in `evidence/human_study/HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md`. The 40-slot response analysis does not certify consent/ethics or authorize redistribution of participant-level rows; those are handled as separate submission/data-governance checks.

## Non-blocking evidence limits and separate submission gates

The existing N=20 GLB-native result remains supplementary evidence for stored, unlit base-color outputs over 11 unseen views; its endpoints are mixed and do not establish an overall 3D winner. The proposed new 24-object bake is retired. Seam-improvement, full-PBR, and new broad 3D-fidelity claims are withdrawn. FAC is outside the candidate's scientific claim set.

The scientific evidence freeze does not close the remaining delivery work: rewrite the paper and response letter from the frozen ledger; resolve R2.1 venue/contribution risk; finish source-level figure attribution and participant-data handling; and complete a clean final-package rebuild, pagination check and reviewer-response audit. Those items keep `REVIEWER_CLOSURE = PARTIAL` and `DIRECT_SYSTEM_UPLOAD = NO` until completed.

## Preservation and authority

`DO_NOT_EDIT_01549` applied until this verdict; submitted manuscript/PDF hashes were not changed in this update. After this verdict, create a separate revision candidate and keep the source submission archived. The current human disposition and all allowed/prohibited language are summarized in `evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json` and the dated human disposition above.
