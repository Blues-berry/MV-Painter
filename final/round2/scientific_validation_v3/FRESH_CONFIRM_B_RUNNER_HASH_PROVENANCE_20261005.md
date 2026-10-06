# FRESH_CONFIRM_B runner-hash provenance note

Date: 2026-10-05. This note preserves the original protocol-lock files and
records the runner-hash discrepancy before FRESH_CONFIRM_B outcome analysis.

## What the locks say

- `FRESH_CONFIRM_B_FORMAL_PROTOCOL_LOCK.md` froze the combined 30-condition
  run with runner SHA256
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` at
  08:40 UTC, before any method output on this cohort.
- `A3B_PROTOCOL_LOCK.md` identifies the byte-pinned residual-only development
  runner as `bcf49f4bdb3995ae80c0e2bd70b04c31936a2fb3347dd9642172b19f27b9c0ae`
  for the 24-object dose-feasibility calibration, and separately identifies
  the combined B runner as `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
- `STAGE_BOUNDARY_PROTOCOL_LOCK.md` and
  `CAP_BUDGET_DIAGNOSTIC_PROTOCOL_LOCK.md` retain the older `bcf49f...` hash
  in their runner field. Those two references are stale for the combined B
  execution and are not silently rewritten here.

## Source comparison

The pinned development runner and the combined-run runner were compared
directly. The diff contains only these additions or replacements:

1. capture the runner SHA256 at import/launch rather than reading the live
   source file at process completion;
2. record the configured/effective data roots and source-code hashes in the
   completion manifest; and
3. record config provenance and use the launch-captured runner hash.

No generation, schedule, seed, sampler, metric, object-selection, or
per-condition inference code changed between those two files. The complete B
protocol lock independently freezes the newer runner hash before B output.

## Closure status

Both B shards completed with 2,250/2,250 rows. The pre-unblinding integrity
gate passed and verified each completion manifest against the combined lock:
runner, config, checkpoint, UID list, effective data root, shard identity,
30-condition registry, and row count. Both manifests record the same 11
inference/metric source-file hashes, and all 11 match the current source
bytes. Manifest SHA256 values are:

- shard 0: `ae4d241ccaeda03b886dd403823b3af654bf6afda4d90a206e98fe3c732cc827`
- shard 1: `593d6dae6ddb801882f8747716cbbd10348bf586f94861e2a686dbe3e68c371a`

One transitive metric dependency, `geotex/metrics_extended.py`, is not in the
runner's 11-file source-hash registry. Its current SHA256 is
`ee32281fbee97e71050e8b2d74bbf6bc476efd372f6a898f1e0a3078863bb2b5`, which
matches `HEAD` and has no working-tree modification. The completion manifest
does not provide a process-time hash for this dependency; the snapshot records
the gap rather than implying it was independently pinned.

The stale `bcf49f...` entries in the stage-boundary and cap/budget sub-locks
are therefore closed as documentation references to the development-runner
version. The combined B lock and both runtime manifests prove that B used the
pre-output-frozen `e5c28e...` runner. No outcome statistics were opened in
reaching this closure.
