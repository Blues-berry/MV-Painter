# CROSS_BACKBONE_MECHANISM_REPORT — Experiment G

Question (per protocol): does ANOTHER additive-residual multi-view adapter
also exhibit a layer-dependent temporal response? NOT "does LLH transfer".

## Setup

Backbone: MV-Adapter (SD21-base i2mv). Injection: 4 down-block points scaled
by a per-step geometry_scale; frozen topology-derived mapping
(mv_adapter/layer_profile_transfer.json): shallow=pt0, middle=pt1,
deep=pts2+3. Conditions: g_baseline (0.75 all points/steps) + 15 window
interventions (1.00 on the group's points inside one 10-step window),
mirroring Experiment A. 50 DDPM steps, 512x512, 6 views, seed 42 shared per
object across conditions. Runner: run_validation_v3_g.py (monkeypatched
schedule_for_step + PerPointApplier; mechanism verified bit-exactly in the
pilot: deep-point norms scale by exactly 1/0.75, other points identical).

Cohort: 100 deterministic fresh objects (seed 20261002) rendered by the SAME
fresh tree; **1 object excluded** — GLB rejected by the upstream mesh loader
("Unknown mesh type", technical failure, documented in
mvadapter_manifest_v3.json). Final N = 99. This cohort is FRESH and disjoint
from every historical cohort (same audit chain as FRESH_CONFIRM_300).
Equal-scale dose ratio across groups is 1 : 0.57 : 1.46 (<2x) → per the
pre-registered rule, no dose-normalized second map.

## Result (g_formal/, layermap_g.json)

- Layer x Window interaction: **NOT supported** (p = 0.58).
- Effects are near-zero everywhere: deep/middle interventions change
  FG-LPIPS by ~0.00003–0.0003; only 3 shallow cells are Holm-rejected
  (~0.0005). Marginals: deep 7e-05, middle 3e-05, shallow 4e-04.
- For calibration, the main backbone's raw-map cell effects were 10–30x
  larger under the same design.

## Verdict (claim 8)

**Unsupported — option C.** Neither the layer x timestep interaction NOR a
meaningful layer redistribution effect transfers to MV-Adapter in the
protocol's scale range: its down-block residual pathway is nearly
scale-insensitive between 0.75 and 1.00 over single windows. L-TCAS must be
framed as **backbone-specific** (a property of the GeoTex adapter's
mid+up-block injection pathway), not as a general multi-view-adapter
principle. No mapping re-search was performed (frozen mapping; pilot only
verified instrumentation).