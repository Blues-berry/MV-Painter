# Corrected bake seam metric — final validation — 2026-10-01

No real bake was rerun. The validation script used two temporary synthetic
GLBs and rechecked the existing 96 rows (8 methods × 12 already-baked objects)
from `BAKE_SEAM_AUDIT_20261001/SEAM_AUDIT_PER_OBJECT.csv`.

## Controls

| Control | Valid sampled seam pairs | Mean ΔE00 | Result |
|---|---:|---:|---|
| Positive: two UV charts with a fixed red/blue color split | 1 | 52.8814 | PASS (threshold >20) |
| Negative: same detectable chart seam on a uniform gray texture | 1 | 0.0000 | PASS (threshold <0.1) |

The synthetic fixture exercises the actual `audit_glb` seam-detection and
sampling path, not only a standalone color-distance helper.

## Existing bake-row integrity

All 96 existing rows contain at least one detected seam and a finite mean,
median, p90, and UV-separation statistic. Every condition has the same
12-object bake cohort:

`obj_0013, obj_0015, obj_0038, obj_0048, obj_0054, obj_0066, obj_0068,
obj_0078, obj_0082, obj_0083, obj_0110, obj_0111`.

For each object/method, `n_detected_seams` equals the number of valid sampled
chart-side seam pairs in this implementation. Each side is a 3×3-mean color
sample at the UV midpoint of the same 3-D edge; thus the surface-point pair
distance is zero while the UV-chart coordinates differ. The interior control
uses a fixed 2-pixel offset. Per-row counts and sample semantics are in
`SEAM_METRIC_FINAL_OBJECT_VALIDATION.csv`.

Empty seam sets are invalid, never zero. The old 48/48 zero result came from
index-keyed pairing that could not observe UV-chart vertex splits and admitted
degenerate sub-texel pairs; it remains `INVALID / SUPERSEDED`.

## Claim boundary and gate

The corrected metric is technically valid for the existing stratified
12-object case study. This does not turn the cohort into a population-level
3-D claim or justify pooling different bake generations. The corrected
within-generation ΔE00 evidence may be retained as a bounded case study;
unseen-view evidence remains separately reported.

`PASS` — positive/negative controls pass and actual rows are non-empty. No
re-bake, rendering, or model inference was performed. Machine-readable
control results are in `SEAM_METRIC_FINAL_VALIDATION.json`.
