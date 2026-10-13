# Final Evidence Authority Ledger — 2026-10-06

> **Historical snapshot superseded on 2026-10-07.** It records the prior `SCIENTIFIC_EVIDENCE_FREEZE=NO` gate. The current run ledger and PASS validation are `FINAL_EVIDENCE_AUTHORITY_LEDGER_20261007.json` and `FINAL_EVIDENCE_AUTHORITY_LEDGER_VALIDATION_20261007.json`; current claim wording is in `next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`.

**State:** `CANONICAL_RUN_INDEX_WITH_EXPLICIT_PROVENANCE_GAPS`; `SCIENTIFIC_EVIDENCE_FREEZE=NO`.
**Run coverage:** 26 execution directories and 243 method-condition records; 19 claims and 169 hash-addressed sources in the linked claim ledger.

This is the condition-level provenance index. The linked E0 ledger is the claim-level wording authority. Both must be consulted before using a number in manuscript text, a figure, or a reviewer response.

## Authority and scope rules

- Per-object paired rows and locked protocols/manifests are numerical authority; old summaries do not overwrite them.
- Never pool cohorts, seeds, runners, cap semantics, or measurement endpoints into one ranking.
- Positive lower-is-better metric differences favor the second condition when contrasts are A minus B.
- A missing provenance field is represented as null with an explicit reason; it is not reconstructed by guesswork.
- Manuscript tables, figures, and reviewer responses must cite this run ledger and the claim-centric E0 ledger.

## Fresh C authority

The unchanged four-condition Fresh C run is the only locked primary comparison in this revision stage: `native_gc3 − native_gfl`, FG-PSNR. The LLH/linear addendum is separate, revision-era prospective, on the same frozen cohort, and uses its own six-test primary and 15-test secondary Holm families. Its positive `LLH − linear` LPIPS favors generic linear because lower is better.

## Human-response update — sensitivity only

A user-supplied export from commit `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` represents all 40 slots; 37 pass the encoded completeness and comprehension fields. The same equal-object, participant×object bootstrap estimator was applied in a separately versioned sensitivity script. No endpoint survives Holm correction. The uploaded participant/task schedules do not match any frozen assignment, left/right placement is fixed within each object-comparison cell, and the stimulus-hash crosswalk and closure registry are missing. Keep the human-fidelity gate open and make no perceptual-fidelity claim. Full record: `1006/evidence/human_study/HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md`.

## Condition fields and provenance gaps

Each JSON condition record contains requested profile, cap-applied profile, residual-trace availability, cohort/N, seed policy, checkpoint, runner/source hashes, input/output provenance, metric implementation hash, lock and outcome-exposure timing, evidence class, allowed/prohibited claim, and superseded artifact pointers. Unknown commit or exact first-unblind times remain explicitly null; the ledger does not infer them.

## Open evidence gates

- reconcile the supplied human export to a contemporaneous frozen package or formally withdraw all perceptual-fidelity claims; current export remains sensitivity-only
- new 24-object GLB bake/unseen-view gate or explicit exclusion of new 3D claim
- source-level redistribution rights for included assets and derivatives
- R2.1 adversarial contribution/venue review after available R1 fidelity decisions
- paper-wide raw-to-table provenance rebuild and final manuscript/response mapping

Machine-readable condition records: `FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`.
Claim-centric E0 ledger: `next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`.
