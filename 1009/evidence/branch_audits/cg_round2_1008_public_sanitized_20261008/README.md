# Selected audit records from the public-sanitized Round-2 branch

Source archive HEAD: `1f2448358537e2b038980496c10a6bb3de532b0f`  
Source ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/cg-round2-1008-public-sanitized-20261008`

This folder preserves a small, reviewable subset of the branch. It is not a copy of the branch's campaign archive. The source branch contains 5,824 non-image Fresh B campaign files (596,128,347 bytes) and records 5,700 omitted generated images; none of those campaign files or images were copied here. `PUBLIC_SNAPSHOT_IMPORT_MANIFEST.csv` is the source branch's 11,524-row path/hash/disposition inventory. Its README labels the inventory retrospective after outcome disclosure: it supports file provenance, not a pre-unblinding claim.

## Boundary sensitivity evidence

`FRESH_B_BOUNDARY_SENSITIVITY_ANALYSIS.json` is preserved byte-for-byte from the source. The existing main report, `1009/evidence/scientific_validation_v3/STAGE_BOUNDARY_EVIDENCE_REPORT.md`, already records its bounded, heuristic-only conclusion.

`FRESH_B_BOUNDARY_CIEDE2000_PER_OBJECT.csv` contains the 150 paired objects' baseline and four frozen-profile CIEDE2000 values from source file SHA-256 `78fb4bba23b7a46ccef997cf38ffac72148db07b7ef9eac2655d76df016b8952`. Reaggregating all four profile-minus-baseline means matches the saved analysis JSON within `7e-16`. The other 4,500-row Fresh B metric ledger is already byte-identical to the copy in the main evidence bundle; the four separate boundary metric CSVs are exact subsets of that ledger.

The original texture-extension CSV also carried `logerr_*` columns. The source analysis script does not use those columns: it recomputes symmetric absolute log errors from the paired metric ledger and GT values. All 1,800 stored `logerr_*` cells differ from that analysis definition, so this selected table retains only the CIEDE2000 columns consumed by the analysis. The original file remains recoverable from the source archive reference and the preserved source worktree.

The 1,200-row Generic-extension metric subset is already present in main with all keyed values equal, so it is not duplicated. Participant-level human-study files are absent from this public-sanitized source tree; this audit did not change any public or private remote ref.

`SHA256SUMS.txt` lists the SHA-256 digests for the other files in this selected package.
