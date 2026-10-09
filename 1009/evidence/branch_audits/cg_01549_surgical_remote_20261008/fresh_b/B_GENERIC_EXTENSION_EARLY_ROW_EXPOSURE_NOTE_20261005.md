# B generic-extension execution and exposure notes — 2026-10-05

## Early raw-row exposure

During a metadata-only check of the incomplete extension ledger, a shell
command accidentally included the ledger tail in its output. One raw
per-object record was therefore visible to the analysis agent before the
extension integrity gate. No condition identity was deliberately extracted,
no outcome was summarized or interpreted, and no analysis, selection,
exclusion, or protocol change was made from that record.

The extension had already been frozen as a post-lock, same-cohort sensitivity
analysis, not independent confirmation. Its comparisons and eight-test Holm
families remain those in
`FRESH_CONFIRM_B_GENERIC_EXTENSION_LOCK_20261005.md`. All rows will be
completed and passed through the independent integrity gate before the locked
aggregate analysis. The early exposure is retained as a provenance
limitation; the extension will not be represented as blinded or confirmatory.

## Duplicate-launch interruption

At 15:19:59 UTC, after the original shard processes were mistakenly missed by
a filtered process query, two duplicate runner processes were started. They
were terminated before an inference run began. Their captured stdout contains
only pipeline component-loading progress and no run banner or object progress;
the contemporaneous GPU-process query listed only the original shard PIDs.
The ledgers remained valid JSON with unique `(object_idx, condition)` keys
(222 and 219 rows at the check). The original shard processes remain the sole
active generators. This incident did not change the frozen runner, conditions,
cohort, seeds, analysis, or row selection; the integrity gate will verify all
final artifacts before any aggregate extension analysis.
