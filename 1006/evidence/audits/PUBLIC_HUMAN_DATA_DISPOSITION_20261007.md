# Public participant-level data disposition

**Final state: `PUBLIC_RAW_HUMAN_DATA = NO`.** This remains the release/data-governance decision. The 40-slot aggregate analysis was completed separately; it does not change the restriction on participant-level redistribution. Current results and permitted wording are in `../human_study/HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md`.

## Publication-risk audit

The public remote tree at `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` contains participant-level response, slot-assignment, pair-mapping, and object-UID files under `final/round2/scientific_validation_v3/human_study_results_20261006/`. This release audit reviewed the file list and schema/column structure only; the separate sensitivity analysis reads that specific commit and publishes only aggregate endpoint summaries in `1006`.

Participant identifiers are short pseudonymous tokens, with no direct name, email, or IP column in the reviewed schema. They cannot be treated as demonstrably anonymous: the public files connect participant tokens to slot, trial, object, pair, and stimulus identifiers. No consent language, ethics approval, or data-handling record establishing public redistribution permission was found in the reviewed public tree. Therefore public release permission and non-reidentifiability are not established.

## Disposition and remediation

- Keep all participant-level responses, assignments, stimulus links, and object-level human records out of any future public or anonymous supplementary package.
- `PUBLIC_RAW_HUMAN_DATA = NO` remains the release rule unless documentary permission is established.
- A future clean release should contain only approved aggregate endpoint summaries, analysis code, protocol, and summaries checked for re-identification risk. The analysis does not authorize public redistribution of participant-level responses or linkage tables.
- A separate remediation plan is required before any public-history rewrite: preserve an external audit copy, review repository/archive backups, prepare a clean release branch without participant-level records, and obtain the required author/data-governance approval. No destructive history rewrite or remote modification was performed.
