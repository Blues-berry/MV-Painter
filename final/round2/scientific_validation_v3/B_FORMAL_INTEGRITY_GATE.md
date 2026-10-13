# FRESH_CONFIRM_B formal integrity gate

**FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS**

This gate was run before condition-level statistical analysis. It checked row keys, source inputs, manifests, shards, finite metrics/residuals, image/log presence, and CSV/ledger agreement. It did not calculate or inspect condition means or contrasts.

| Check | Result |
|---|---:|
| Frozen objects | 150/150 |
| Unique object-condition rows | 4500/4500 |
| Raw rows, shard 0 / shard 1 | 2250 / 2250 |
| Frozen rendered input files byte/hash verified | 13888 |
| Prediction PNGs present | 4500/4500 |
| Per-step residual logs present | 4500/4500 |
| Duplicate keys / missing condition pairs / non-finite values | 0 / 0 / 0 |
| Runner / config / checkpoint / effective data root | MATCH |
| Recorded inference/metric source files matching current bytes | 11/11 per shard |
| Raw ledgers ↔ rebuilt combined/condition CSV values | EXACT |

Condition-level outputs remain unopened until this PASS gate is committed.
