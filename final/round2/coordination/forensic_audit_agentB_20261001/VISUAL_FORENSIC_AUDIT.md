# VISUAL_FORENSIC_AUDIT.md (Phase 2 — agent B)

Constraint discovered up front: the formal strict-276 runs archived **metrics
only** (no prediction PNGs), so the pre-registered 20-30-object visual set on
the main method cannot be executed from formal artifacts. Executed instead:
(a) view-mapping and GT-correspondence checks, (b) metric-vs-image agreement
checks on the images that DO exist (stage-placement uncapped panels; robustness
R1 capped images; dev-24 panels), (c) a bounded capped-layer-LLH visual check.
Image sources and their regime are disclosed per item.

## 1. View mapping / GT correspondence (trigger 3) — PASS

Checked obj_0081, obj_0130, obj_0106 (stage-placement panels, 512x768 3x2,
six views) and obj_0024 (robustness R1):

- Silhouette correspondence between prediction panels and GT panels is
  correct in all six views; no reversed orientation, no camera swap.
- Panel foreground fractions match dataset alpha fractions
  (obj_0081: panel 0.213 vs dataset alpha 0.186; obj_0024: 0.183 vs 0.19;
  differences consistent with compositing/rounding).
- Dataset GT is stored as RGBA with transparent-black background; composited
  GT panels reconstruct the object faithfully (clean-v2 audit MAE 2.19e-4).
  An apparent "dark GT" reading of raw dataset stats is the uncomposited
  alpha=0 background, not a data bug.

**No view-mapping P0 found.**

## 2. Metric-vs-image agreement (trigger 1) — metric suite exonerated

The uncapped global-LLH stage-placement images show severe tone collapse on
light-gray objects (obj_0081 predicted near-black vs GT 0.75 gray; per-object
FG-PSNR 6.0; obj_0130 6.55; obj_0106 dark-on-dark 14.44). The images and the
per-object metrics AGREE — low PSNR where the image is visibly wrong. This is
the opposite of a metric/visual disagreement: it independently corroborates
the CROSS_RUNNER_SCALE_SEMANTICS_AUDIT finding that the uncapped regime
damages global schedules, and it confirms the FG-PSNR metric tracks visible
failure.

## 3. Capped main method (layer-LLH) — bounded visual check

Only obj_0024/obj_0025 R1 images exist for capped layer-LLH
(`realization1_core5/`). obj_0024: six-view silhouettes match GT; generation
is a plausible, multi-view-consistent textured animal with a warm-brown tint
(object mean RGB [0.73, 0.68, 0.63] vs GT ~[0.73-0.79] gray); FG-PSNR 15.09
is consistent with the visible moderate tint deviation. No repeated-pattern
or structural artifact at panel scale. The warm-tint-vs-gray-GT observation
is the visual face of the "texture variation vs GT fidelity" gap that
Reviewer 1 probe — worth one honest sentence in the revision, not a
metric bug.

## 4. Fixed visual sets for any future visual claim

From `phase1a_llh_gfl_per_object_deltas.csv` (no aesthetics-based re-picking):

- top-12 wins: obj_0081 0066 0051 0100 0063 0101 0091 0099 0076 0067 0110 0064
- median band: obj_0130 0261 0205 0150 0277 0140
- bottom-12 losses: obj_0106 0062 0124 0086 0027 0178 0080 0208 0096 0266 0204 0227

## 5. Identical-image check (trigger 2) — PASS

No byte-identical predictions across methods in any archived image set; the
R0/R1 hash audit (Phase 7) shows hash-distinct, ~45 dB self-similar pairs.
The bake contact sheet covers the full 12-object cohort (no selection).

## 6. Verdict

`VALIDATED_WITH_LIMITATIONS` — no view, mask, or GT-correspondence defect;
metrics track visible failures; the main method's holdout-scale visual audit
is `ARTIFACT_INSUFFICIENT` because formal runs archived no prediction PNGs
(remediation: archive PNGs in any future formal run; use the fixed sets above;
rely on dev-24 panels and the bake case study for current visual claims, with
their development-set labels).
