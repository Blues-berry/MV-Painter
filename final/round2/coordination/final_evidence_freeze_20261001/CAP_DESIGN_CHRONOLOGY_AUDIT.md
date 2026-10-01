# Cap semantics and chronology audit — 2026-10-01

## Implementation

In `MVPainter/mvpainter/model_unet_geotex.py`, `GeoTexResnetWrapper.forward`
computes the adapter correction and, when `_adapter_scale` is set, applies
`effective_scale = min(requested_scale, self._max_scale)` before adding the
correction. `inject_adapters` maps `up_0 → deep`, `up_1 → middle`, and
`up_2 → shallow` (with `mid → deep`). The cap vector is:

| Group | Cap | Code comment |
|---|---:|---|
| deep | 3.0 | global structure |
| middle | 3.5 | primary shape lever |
| shallow | 0.8 | fine texture, minimal intervention |

The global and layer-wise Core-7 schedules use this same wrapper path. The
static-schedule implementation caps before the correction is added; the
optional controller path receives the same `_max_scale`. `no_adapter` does not
set wrapper geometry features, so it skips the correction path entirely; its
nominal `0.0` is unused and has no effective scale.

## Chronology and outcome information

| Date / commit | Evidence | Interpretation |
|---|---|---|
| 2026-07-01, `eb1a0a5911e75b38c260a71d174cddfce93f8eaf` | First tracked introduction found for `LAYER_MAX_SCALES={deep:3.0,middle:3.5,shallow:0.8}` and `min(scale,cap)` in the wrapper. | Predates the current strict-276 Core-7, but the commit is a broad cleanup and contains no cap-value preregistration or development-set selection record. |
| 2026-08-03, local artifacts `mvpoutput/explore_contradiction/cap_ablation_v2/` and `cap_ablation_v3/` | Existing cap vector was compared against an uncapped forward on the first four entries of the configured validation dataset (dataset length 300), 50 steps, with two checkpoint versions. | Outcome-aware mechanism diagnostic. It toggled the existing cap on/off; it did not sweep alternative numeric thresholds. Exact asset IDs were not serialized in the summary. |
| 2026-08-05, `92974a800ef5072b267b005d7c199349ff9bd328` | `explore_cap_ablation.py` and the H3 “scale semantics” investigation were added after the observed LapVar direction discrepancy. | Confirms the cap's effect was investigated in light of observed outcomes. The script compares current caps versus no cap, not candidate cap values. |
| 2026-09-30 to 2026-10-01 | The R0 strict-276 protocols lock the then-existing capped wrapper; no later cap-value change was found through task-entry HEAD `450389f`. | The current Core-7 confirmation did not tune the cap on its holdout. |

Thus the overall cap-design history is classified **`OUTCOME_INFORMED`** for
the implementation/mechanism investigation. This does **not** mean the final
strict-276 metrics were used to tune the caps: the numeric vector predates that
confirmation and no subsequent threshold change was found. The initial
selection rationale and any pre-July trial values remain undocumented, so the
three numbers must not be presented as an independently established optimum
or universal constants.

The saved summaries show materially different capped/uncapped LapVar behavior
on four-object development probes, and the direction/magnitude varies between
the two checkpoint versions. For example, the v2 summary reports fixed-high
mean LapVar `0.02401` capped vs `0.00571` uncapped, while the v3 summary reports
`0.02446` vs `0.02794`; these are descriptive probe values, not confirmatory
estimates. The v2 directory also contains an `OLD_POLLUTED` summary and a log
whose aggregate matches that older file rather than the later v2 summary, so
the v2 aggregate is not a clean quantitative basis for choosing cap values.
These outputs are development/mechanism evidence only; they do not constitute
a cap-threshold sensitivity sweep, and they are not pooled into Core-7. The
first-four object identities are not serialized, so “development set” is
limited to the configured validation dataset indices 0–3 (300 available
entries), not a named frozen subset.

## Core-7 requested and effective schedules

The full stage-resolved table is `CORE7_EFFECTIVE_SCALE_TABLE.csv`. The stage
partition is `step/49`: early `<1/3`, middle `<2/3`, late otherwise, giving
17/16/17 steps at 50 steps.

Key interpretation: global fixed-low, fixed-high, and global C3 all hit the
shallow cap; C3's shallow scale is therefore `0.8` at all three stages. The
layer fixed-mean, LHL, and LLH schedules remain below all caps. Comparing a
global and layer-wise condition changes both depth allocation and effective
shallow budget; nominal scales are not interchangeable with effective scales.

## Gate 1 disposition

`PASS_WITH_LIMITATION` for the frozen Core-7 semantics and chronology, with
the explicit outcome-informed development caveat above. All seven Core-7 arms
use the same capped implementation. The historical clean-v2 and global-stage
panels used an uncapped wrapper; absolute values and rank claims must not be
combined across those regimes. The active manuscript still contains
uncapped-era comparisons and requires correction in the later authorized
rewrite; no manuscript file was changed here.
