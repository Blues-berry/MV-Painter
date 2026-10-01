# PROTOCOL LOCK — MV-Adapter 4→3 mapping sensitivity (2026-10-01)

Written BEFORE any M3 (alternative-mapping) MV-Adapter metric was observed.
Branch codex/round2-evidence-integrated-20261001. Task boundary: experiment +
audit + experiment report ONLY.

## Question

Reviewer-2 risk: the frozen mechanical 4→3 mapping (shallow={p0}, middle={p1},
deep={p2,p3}) is one of several topologically defensible contiguous
partitions. If the layer-wise effect on MV-Adapter depends on the choice,
the cross-backbone layer-transfer evidence is mapping-fragile. This run
tests the ONLY distinct alternative mapping under the SAME frozen profile.

## Enumeration (complete, no cherry-picking possible)

Contiguous monotone partitions of the 4 ordered injection points into 3
non-empty groups — exactly C(3,2) = 3:

| ID | shallow | middle | deep | per-point vector (frozen profile) |
|---|---|---|---|---|
| M1 (frozen) | {0} | {1} | {2,3} | [0.41953, 1.19349, 1.19349, 1.19349] |
| M2 | {0} | {1,2} | {3} | [0.41953, 1.19349, 1.19349, 1.19349] |
| M3 | {0,1} | {2} | {3} | [0.41953, 0.41953, 1.19349, 1.19349] |

Because the frozen normalized profile has middle == deep (both 1.65/1.3825),
M1 and M2 give the IDENTICAL per-point vector — running M2 would be a
bit-level duplicate of M1 and is skipped by construction. M3 is therefore
the ONLY information-bearing alternative. Non-contiguous or non-monotone
assignments (e.g. deep={p0}) are topology-absurd and excluded a priori.

## Frozen run matrix

Profile JSON: final/round2/mv_adapter/layer_profile_transfer_mappingM3.json
(only target_mapping differs from the frozen profile; normalization and
source values untouched). Everything else byte-identical to the frozen
layer-wise protocol (MVADAPTER_LAYERWISE_PROTOCOL.md):

- runner: final/round2/mv_adapter/run_layerwise_experiment.py
- manifest final/round2/mv_adapter/data_manifest.json, split holdout,
  geometry exact, 76 objects
- base model final/round2/mv_adapter/models/sd21_base, adapter
  final/round2/mv_adapter/models/mv-adapter
- seed 20260928, steps 50, low 0.75, high 1.00
- schedules: L-LLH, L-LHL, L-FIX (canonical labels) — all three so the
  P1/P2/P4 family can be re-evaluated under M3
- output: final/round2/mv_adapter/results/holdout_exact_mapM3_{llh,lhl,fix}_76/

## Analysis plan (fixed before M3 results)

Against the EXISTING global rows (unchanged, no rerun): G-FL, G-LLH, G-LHL.
Per (mapping, comparison, metric): paired object-level deltas over the 76
common objects; benefit-oriented transform identical to
analyze_layerwise_panel_20260930.py (LOWER_BETTER = fg_lpips, ciede2000,
gt_relative_texture_error); 10k percentile bootstrap seed 20260930.

Comparisons: P1 = L-LLH − G-FL, P2 = L-LLH − G-LLH, P4 = L-LHL − G-LHL,
each under M1 (existing rows) and M3 (new rows). Outcome labels:
- MAPPING_STABLE: same sign and CI-excludes-zero status on the primary
  fidelity metrics for the layer-vs-global direction in both mappings;
- MAPPING_SENSITIVE: sign flip on any P1/P2/P4 primary metric between
  mappings (report honestly; layer-transfer claim on MV-Adapter must then
  be downgraded to mapping-dependent).

No other condition, scale, or profile may be added. No re-selection.

## Chronology audit (selection-time evidence)

- The frozen profile derives from MAIN-backbone frozen layer_fixed_mean
  values + point-count normalization; no MV-Adapter metric enters it.
- MVADAPTER_LAYERWISE_PROTOCOL.md (incl. the M1 mapping) was written before
  the first layer-wise MV-Adapter row existed (pre-registered; identity and
  smoke gates preceded formal runs).
- The global 76-object results (G-*) predate the layer-wise protocol but
  contain no layer-vs-layer contrast, hence could not inform a 4→3 mapping
  choice.
- M3 variant created 2026-10-01 in this task, after seeing M1 layer-wise
  results — this is BY DESIGN (sensitivity analysis of an existing
  conclusion, not a selection). M3 results must not be used to re-select
  the mapping post hoc in either direction.

## Status

- [x] Protocol frozen before any M3 observation
- [x] Formal 3 x 76 = 228 rows (results/holdout_exact_mapM3_{llh,lhl,fix}_76/)
- [x] Direction-stability analysis M1 vs M3: 16/18 STABLE, 1 ATTENUATED (tiny edge_ssim), 1 magnitude-trivial LPIPS flip (MAPPING_SENSITIVITY_REPORT.md)
