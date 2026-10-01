# AUDIT — MV-Adapter 4→3 mapping selection chronology (2026-10-01)

Reviewer-2 risk: was the frozen mechanical mapping (shallow={p0}, middle={p1},
deep={p2,p3}) chosen AFTER observing 76-object MV-Adapter outcomes?

## Timeline (established from git history and file mtimes)

| time (UTC) | event |
|---|---|
| 2026-09-28 18:35 | MV-Adapter global-scale 76-object holdout rows finalized (results/holdout_exact_76/per_object_metrics.csv mtime). These contain ONLY global conditions (R0/G-FL/G-LHL/G-LLH constant or temporal-global scale) — no per-layer contrast exists in them, so they cannot discriminate between 4→3 mappings. |
| 2026-09-29 (main-backbone) | Main-backbone frozen layer_fixed_mean profile {deep 1.65, middle 1.65, shallow 0.58} + point-count normalization frozen (main-backbone protocol locks); this — not any MV-Adapter metric — is the profile source. |
| 2026-09-30 | MVADAPTER_LAYERWISE_PROTOCOL.md written (pre-registration): injection-point topology, mechanical mapping rule, identity gate and smoke gate BEFORE any layer-wise run. Runner + identity audit confirm 9/9 bitwise identity with multipliers 1.0. |
| 2026-10-01 00:29 | Layer-wise rows committed (4f31256): 3 × 76 rows (L-FIX/L-LHL/L-LLH), results mtimes 10-01 00:40. |
| 2026-10-01 (this task) | M3 alternative-mapping sensitivity run PRE-REGISTERED (MAPPING_SENSITIVITY_PROTOCOL.md) and only then executed. |

## Findings

1. The mapping rule was fixed in the pre-registration file BEFORE the first
   layer-wise MV-Adapter row existed; the only MV-Adapter results that
   existed at that time were global-scale rows, which carry no
   layer-mapping information.
2. The profile VALUES come from the main backbone's frozen layer_fixed_mean
   + count normalization; no MV-Adapter outcome enters the values.
3. The M3 sensitivity variant was created AFTER seeing M1 results — by
   design, as a sensitivity analysis of an existing conclusion; its
   protocol forbids post-hoc selection in either direction.

Conclusion: no evidence that the mapping was selected from MV-Adapter
outcomes. Residual exposure is the mapping-space restriction to contiguous
monotone partitions (complete enumeration: 3 partitions, of which 2 are
identical under the frozen profile — see MAPPING_SENSITIVITY_PROTOCOL.md).
