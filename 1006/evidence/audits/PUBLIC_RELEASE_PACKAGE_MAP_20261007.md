# Public package map and release disposition

The proposed reviewer-facing tree is scaffolded in `1006/submission_package/` as `code/`, `configs/`, `analysis/`, `protocols/`, `frozen_tables/`, `figures/`, `supplementary/`, and `archive/`. It is not populated with raw assets or participant records.

Potentially eligible after clean rebuild and final approval: analysis code, frozen protocols, aggregated numerical authority, synthetic sampler validation, and Figures A–C/E/G. Figure D may be included with the row-level credits in `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`; all 20 source models currently verify as CC BY. Source GLBs, the 9 `UNKNOWN` Fresh C assets, and UID-linked per-object tables are excluded. The 300-row rights inventory is an audit artifact, not a package manifest. All participant-level response/assignment/linkage files are excluded. Debug logs, failed attempts, locks, and historical forensic payloads belong in `archive/` or outside the submission-facing repository.

The proposed README states the bounded main claim, Fresh C cohort, conditions, commands, regeneration process, and known limitations. It is not a release clearance. Candidate figure rights are `CLOSED_WITH_EXCLUSIONS`; `PUBLIC_RELEASE=FAIL` pending a clean rebuild, package checksums, and remediation of the public human-data history.
