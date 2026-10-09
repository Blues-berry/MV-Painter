# Main-backbone Robustness-1 audit

Source branch: `codex/main-backbone-robustness1-20260930`  
Archived source HEAD: `99d6c88f28050a3fb74a04d74f555ba30f27ff3e`  
Merge base: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`

## Disposition

`SELECTIVE_CONTENT_MERGE`; full-history merge rejected. The archived tree differs
from current main at 2,332 paths (1,312 added, 7 modified, 1,013 deleted),
including deletion of 253 active `1008/` paths and 307 `1009/` paths, plus 1,052
old `final/` paths. Its unique history contains 102 commits and 1,429 blobs
(665,718,360 uncompressed bytes), including 14 blobs at least 5 MiB. The
current source worktree is not registered, so this decision makes no claim
about uncommitted files outside the archived commit.

The selected material preserves the R1 per-object metric table, protocol and
input audit records, the original branch report, and the source runner/audit
scripts. Five R0 metric tables are reused from the already committed Core-7
evidence: the four original confirmation CSVs match `/4T/tmp` byte-for-byte;
the R0 Global-C3 completion CSV also matches byte-for-byte. No second copy of
those tables was added. The combined R1 CSV is retained instead of the
duplicate `rows.json` and five per-method CSVs. Per-object render images,
run/preflight logs, checkpoint/model data, caches, and the launch wrapper are
excluded. Historical run scripts are included for traceability only and were
not run during this audit.

## Result and validation

R1 contains 1,380 rows (276 objects × five frozen methods) under the source
protocol's `10042 + object_idx` reference-preprocessing seed namespace. Its
saved two-process preflight records 0 pass-to-pass mismatches and 0
cross-method mismatches; the recorded R0 comparison reports 500/500 matching
deterministic input components and 150/150 differing reference-derived
components.

`recompute_r0_r1_stability.py` recomputes the 28 paired R0/R1 cells from these
R1 rows and the R0 metric CSVs already in main. It uses the source analyzer's
10,000 object-level bootstrap resamples and seed `20260930`; it does not run
model inference or write files. The source branch reports 27
`STABLE_STRONG`, 1 `STABLE_DIRECTIONAL`, 0 `UNSTABLE`, and identical Core-5
rankings on all seven metrics. Independent reaggregation passed: the 28-cell
table matches 28/28, aggregate means 70/70, paired outputs 56/56, and all
seven rankings match. R1's primary LLH−GFL FG-PSNR delta is +3.233152 dB
(95% CI [+2.928141, +3.526766], 241/276 wins). Run the reproducer from the
repository root with Python 3.10 or newer. It fails if row coverage, protocol
hashes, the saved 28-cell table, aggregate means, paired outputs, or rankings
disagree.

## Evidence status limitation

The source report says `PROTOCOL_LOCK.md` was written before any R1 metric was
observed. Git history cannot independently establish that timing: both the
protocol lock and the R1 metric CSV first appear in the same source commit,
`99d6c88f` (2026-10-01 00:33 UTC). Therefore this audit preserves the result
as a retrospective robustness diagnostic; it does not upgrade it to
independently verified preregistered or confirmatory evidence. Reaggregation
validates saved metric rows and summaries, not model execution from raw inputs.

## Paper and conflict status

`PAPER_IMPACT=INDIRECT`. The archived branch has no manuscript, Supplement,
response-letter, figure, table, reference, or model implementation change
selected here. The R0/R1 result is not stated in the active 1008 manuscript,
so no claim was edited or newly promoted. Active TeX and response hashes and
the 1008 package checksums were checked separately and remain unchanged.

`NO_CONFLICT`: no Git merge or cherry-pick was attempted. Unsafe old code and
tree differences were excluded during pre-merge review; these are not
reported as resolved merge conflicts. No GPU job or journal submission was
started (`SUBMISSION_APPROVED=NO`).
