# Human-study data authority and gate verdict — 2026-10-07

## Decision

`HUMAN_CONFIRMATORY_ENDPOINT_ANALYSIS = PASS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS`.
The uploaded 40-slot study remains confirmatory for its prespecified endpoint
family. It is not downgraded to sensitivity or exploratory evidence. This gate
passes the analysis and evidence-authority requirements; it does not certify
that every operational detail followed the frozen package or establish a
positive LLH preference effect. The executable authority validator reports
all checks passing in `../evidence/human_study/HUMAN_STUDY_GATE_VALIDATION_20261007.json`.

## Gate checks

| Check | Verdict | Evidence and scope |
|---|---|---|
| Study classification | **PASS — confirmatory** | The study owner confirmed that this response set is the confirmatory human study. The four comparisons, two separate questions, eight-endpoint family, estimand, exclusion rules, and analysis were specified before collection. See `../evidence/human_study/HUMAN_STUDY_CLASSIFICATION_OVERRIDE_20261007.json` and `../evidence/protocols/HUMAN_STUDY_FINAL_PAIR_LOCK.md`. |
| Source and row integrity | **PASS** | The source is pinned to commit `f5bad8a1e6ca4265c1823eaa26b2775313de4c96`; four input CSVs have recorded SHA-256 values. All 960 response rows join to assignment and pair maps; all 24 object IDs map uniquely; the export covers 40 slots and all 96 object-by-comparison cells. |
| Prespecified sample and estimator | **PASS** | Thirty-seven participants pass the locked whole-participant completeness/comprehension rules, above the 36-person threshold. Each endpoint has 24 objects and 222 valid judgments. The analysis uses equal-object estimates, ties=0.5, 10,000 two-way participant/object bootstrap draws with seed `20261005`, and the frozen two-sided plus-one test. |
| Multiplicity and completeness | **PASS** | All eight planned comparison-by-question endpoints are reported in one Holm family. No endpoint is omitted or selected by its result. The reproduced estimates match the source-pinned analysis output. No Holm-adjusted p-value is below 0.05. |
| Execution and provenance conformance | **DEVIATIONS RECORDED; full adherence not established** | The prior schedule audit records 0/40 frozen-schedule matches and includes the frozen private-key hash. The current endpoint reanalysis package does not contain that key and correctly marks a new key audit unavailable. Left/right orientation is fixed within 96/96 object-by-comparison cells, though balanced across objects. The export lacks a randomization seed, question order, raw comprehension answers, and stimulus-file hash crosswalk; coordinator closeout and consent/ethics records were not provided. These are reported as execution/provenance limitations, not used to discard the study or change its confirmatory classification. |

## Authority chain

1. `../evidence/protocols/HUMAN_STUDY_FINAL_PAIR_LOCK.md` is the unchanged
   historical lock for the estimand, planned endpoint family, estimator, and
   numerical validity threshold. Its hash is recorded in the classification
   override and analysis provenance.
2. The response export is the four-file set in source commit
   `f5bad8a1e6ca4265c1823eaa26b2775313de4c96`; `HUMAN_STUDY_CONFIRMATORY_PROVENANCE_20261007.json`
   records each input hash and the row-level checks. The earlier
   `HUMAN_STUDY_ANALYSIS_PROVENANCE_20261006.json` records the frozen-key
   schedule comparison (0/40 and 0/40) and its private-key SHA-256. The newer
   endpoint provenance does not claim to repeat that private-key comparison.
3. `../evidence/human_study/analyze_confirmatory_human_study_20261007.py`
   reproduces the complete endpoint family and writes the aggregate table and
   forest plot. No participant-level rows are needed to read the results in
   this evidence package.
4. `../evidence/human_study/HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md`
   is the detailed result and interpretation authority;
   `HUMAN_STUDY_CLASSIFICATION_OVERRIDE_20261007.json` records the current
   classification and prior-classification supersession.
5. `SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md` and
   `FINAL_READINESS_VERDICT_20261007.md` inherit this gate. Older
   sensitivity-only language is an explicitly historical snapshot and must
   not override the 2026-10-07 classification.
6. `../evidence/human_study/validate_human_study_authority.py` checks the
   source/protocol hashes, endpoint completeness, unchanged estimates after
   reclassification, carried-forward schedule audit, and status consistency.

## Allowed interpretation

Treat the eight endpoint estimates as confirmatory observations of relative
judgments on the displayed 2D stimuli. All point estimates are above 0.5, but
none shows a Holm-adjusted LLH preference advantage. Intervals crossing 0.5 do
not establish equivalence or non-inferiority. The study does not establish
absolute reference fidelity, unseen-view quality, baked-mesh quality, seams,
or full-PBR quality.

The execution deviations limit what can be said about assignment
randomization and exact participant-side stimulus identity. They do not make
the response export a sensitivity dataset and do not change the frozen
estimand, endpoint family, or observed responses. Consent/ethics, retention,
and continued public availability of participant-level source files remain
separate data-governance gates; passing this analysis gate does not pass those
release checks.

## Gate inheritance

- The bounded scientific evidence freeze may pass with this confirmatory
  endpoint analysis and its limitations disclosed.
- R1's human-preference-evidence subissue is addressed by direct relative 2D
  judgments; absolute fidelity and 3D concerns remain outside this study.
- Reviewer closure remains **PARTIAL** until the other reviewer issues and
  final-delivery work close.
- Direct journal-system upload remains **HOLD** while the separate readiness
  blockers remain open.
