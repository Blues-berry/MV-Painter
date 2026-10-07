# Fresh C input-screen audit — 2026-10-06

**Stage:** asset identity and basic geometry screen complete; rendering and
cohort freeze remain in progress. No method output or comparative score exists.

## Frozen source and download record

The candidate queue is pinned to Objaverse v1 revision
`21e4e142159e2153706c23a3a02e55cec5591cea`. Its 1,000-row queue hash is
`1cee99e215aaeb2d9f8d6491928280e5fb0424bfef7b92cfd41014d49899c859`; ranks
1–600 were the fixed screen block and ranks 601–1,000 remain reserve. The
screen block was selected from the locked license allowlist before any method
outputs. All 600 downloaded successfully, with zero download failures. The
download manifest SHA-256 is
`4f93ebc44e90b2f259739f4b44fdb3ae9a372a37c62d2ad8835d97d268500df8`.

The downloader process had loaded its original code before the source file was
updated to add reserve-batch provenance. The original code hash was recovered
from the pre-outcome package commit and recorded in
`data/fresh_c/ASSET_DOWNLOAD_STATUS.json`. The process's legacy status label
said “complete with recorded failures” while its counters were 600 successful,
zero failed. The status metadata now records `DOWNLOADS_COMPLETE`, preserves
the counters and manifest hash, and documents this normalization. The CSV
manifest remains unchanged.

## Basic asset integrity

The asset audit checked all 600 downloaded files against their manifest
hashes, compared their byte hashes with 1,965 locally available historical
GLBs, and attempted geometry loading. It found:

- 594 assets with valid, non-empty geometry;
- 6 assets with invalid geometry;
- 0 byte-identical matches to the historical GLB inventory;
- 0 duplicate-byte groups within the new candidate block.

The 594 valid assets exceed both the target cohort size of 300 and the minimum
of 276. The frozen reserve block is therefore not needed at this stage. This
does not yet establish a 276-object usable cohort: all 17 views, normals,
cameras, depth maps, foreground coverage, historical decoded-pixel signatures,
and duplicate signatures within the new rendered pool must still pass.

During pre-output code review, the cohort-freeze branch was found to stop at
N=276–299 instead of screening the remaining frozen queue as required by the
protocol. Before freeze or inference, that branch was corrected: any pool
below 300 now requests the next 200-candidate reserve block until the 1,000-ID
queue is exhausted; only then can 276–299 freeze as a reduced cohort, and
fewer than 276 blocks. Boundary tests cover N=275, 276, 299, and 300 before
and after reserve exhaustion. Candidate order, render settings, and analysis
rules are unchanged.

The screen block contains 585 BY, 13 BY-SA, and 2 CC0 assets. Individual
attribution records are retained. Raw meshes and rendered panels remain local
until redistribution terms are checked; the two separate license-uncertain
objects in the existing 24-object visual supplement remain an open release
gate.

## Next locked steps

Render the 594 geometry-valid assets with the frozen Blender 4.2.4 script,
HDRI, 512×512 resolution, and 17-view setup; convert depth maps; then run the
predeclared coverage and exact decoded-RGBA duplicate screen against the two
historical render roots. Freeze the resulting 276–300 object cohort, full
attribution, and per-file hashes before inference. If fewer than 276 survive,
stop before method outputs. No candidate is chosen based on generated quality
or method outcomes.

Primary machine-readable records are `data/fresh_c/ASSET_DOWNLOAD_STATUS.json`,
`data/fresh_c/asset_download_manifest.csv`,
`data/fresh_c/ASSET_IDENTITY_TECHNICAL_AUDIT.json`, and
`data/fresh_c/candidate_asset_technical_audit.csv`.
