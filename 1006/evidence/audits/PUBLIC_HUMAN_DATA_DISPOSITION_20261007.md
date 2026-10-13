# Public participant-level data disposition

**Final state: `PUBLIC_RAW_HUMAN_DATA = NO`.** The aggregate 40-slot analysis and its later confirmatory reassessment are documented separately under `1006/evidence/human_study/`; neither permits redistribution of participant-level records.

## Publication-risk audit

The public remote tree at `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` contains participant-level response, slot-assignment, pair-mapping, and object-UID files under `final/round2/scientific_validation_v3/human_study_results_20261006/`. This release audit reviewed only the file list and schema/column structure; it did not inspect response values or recompute any human-study result. Separate analyses read that source and publish aggregate endpoint summaries under `1006/evidence/human_study/`.

Participant identifiers are short pseudonymous tokens, with no direct name, email, or IP column in the reviewed schema. They cannot be treated as demonstrably anonymous: the public files connect participant tokens to slot, trial, object, pair, and stimulus identifiers. No consent language, ethics approval, or data-handling record establishing public redistribution permission was found in the reviewed public tree. Therefore public release permission and non-reidentifiability are not established.

## Disposition and remediation

- Keep all participant-level responses, assignments, stimulus links, and object-level human records out of any future public or anonymous supplementary package.
- `PUBLIC_RAW_HUMAN_DATA = NO` remains the release rule unless documentary permission is established.
- A future clean release should contain only approved aggregate endpoint summaries, analysis code, protocol, and summaries checked for re-identification risk. Existing aggregate analyses do not authorize release of participant-level records.
- Any future history rewrite that touches participant-level records requires an external audit copy, review of repository/archive backups, a clean release branch without those records, and the required author/data-governance approval.
