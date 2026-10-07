# Final clean-checkout reproducibility report

**Current candidate status: `FAIL` for submission-grade clean-checkout reproducibility.**

## Repository identity and package state

The public branch currently points to `f5bad8a1e6ca4265c1823eaa26b2775313de4c96`; local HEAD is the older `5c2c8829a1e19b42837761160dc4c14cf8f09045`. The local HEAD is an ancestor of the public tip, while the working tree is heavily staged/dirty and contains local `1006/` material. There is no clean, committed final candidate containing the current evidence closure package. A clean clone of the intended final candidate therefore cannot be performed without first creating and reviewing that candidate.

## Existing evidence, by reproducibility level

- **Generation reproducibility:** not established end to end. The release bundle does not contain every historical model prediction, residual, and render payload required to reproduce all GPU-generated outputs from raw inference inputs. No new GPU work was run for this report.
- **Analysis reproducibility:** a prior published compact bundle (`00c48915877f592c725d5b13be90905eab347b0a`) passed its documented checksum/rebuild audit for included analyses, tables, figures, and candidate PDFs. That is a historical package result, not a clean rebuild of the current uncommitted closure candidate.
- **Historical reconstruction:** strict-276 paired statistics can be reconstructed from stored object rows, but complete original runner/input-tensor provenance is unavailable. It remains retrospective support.
- **Current Fresh C tables and figures:** frozen source tables and generated figures exist locally. Figures B/C were generated from the canonical paired-delta CSVs and frozen analysis JSONs; this has not yet been reproduced from a clean checkout of a final candidate commit. The numerical authority table preserves all source file hashes, but the standalone source script for the historical MV-Adapter cluster-bootstrap scalar is not present in the portable tree.
- **Figure asset scope:** Figure D's 20 sources currently verify as CC BY, and a row-level attribution table is prepared. Source GLBs, 9 unknown cohort assets, and UID-linked per-object tables are excluded from the proposed package. This closes candidate figure rights with exclusions but does not create a release package.
- **LaTeX and supplementary:** the prior 1006 candidate compiled in the earlier audit. The current 01549 source remains frozen; no post-closure candidate manuscript/supplement build was authorized or performed.

## Required before a PASS

Create a compact, rights-cleared candidate commit; clone that exact commit into a clean directory; install the recorded environment; regenerate the Fresh C and addendum tables, figures A–E/G where approved, numerical authority table, atlas index, and supplementary files; compile the candidate LaTeX; compare all declared checksums; and record generation, analysis, and historical-reconstruction limits separately.

Until then `REPRODUCIBILITY=FAIL` for the submission package. No remote push or submission action was performed.
