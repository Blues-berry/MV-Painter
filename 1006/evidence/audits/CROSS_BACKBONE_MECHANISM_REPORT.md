# CROSS_BACKBONE_MECHANISM_REPORT — Experiment G

## Question

Does a second additive-residual multi-view adapter show the same layer- and
time-dependent response to adapter-scale changes? This experiment tests
response transfer; it does not test direct transfer of GeoTex schedules.

## Frozen design and cohort

The backbone is MV-Adapter (SD21-base image-to-multiview). Four down-block
injection points use the frozen topology map: shallow=point 0, middle=point 1,
deep=points 2 and 3. The 16 conditions are a 0.75 baseline and 15 one-window
interventions that set one group's points to 1.00 for one of five 10-step
windows. Each object uses six views, 50 DDPM steps, 512×512 inference, and
seed 42 shared across conditions. Instrumentation was verified in the frozen
pilot: a point's recorded residual norm scales by exactly 1/0.75 when its
scale is raised; other points are unchanged.

The planned G holdout contains 99 objects after its pre-registered exclusion.
The initial ledgers contained 1,600 rows: 81 unique objects, with 304 repeated
object-condition rows. All repeats matched on source UID and every metric;
runtime was the only ignored field. The locked completion run added 17 objects
and 272 rows. The merged analysis therefore has **98 objects × 16 conditions
(1,568 object-condition rows)**. The last planned object, `g_0098`, could not
be run: its frozen source GLB loads as `trimesh.Path3D` with 93,387 path
vertices, 444 path entities, and no triangle faces; the unchanged G surface
mesh loader raises `Unknown mesh type`. Its GLB SHA256 is
`290da5fe6a3047416111e100c3141933f6c18989c7f234363ac8f4312141ad59`.
The failure is documented in `g_formal_complete/TECHNICAL_EXCLUSION_G_0098.json`.
No replacement input or loader conversion was used.

The 98 analyzed source UIDs are from the fresh cohort and are disjoint from
the historical cohorts. The unequal residual-dose ratio across mapped groups
remains 1 : 0.57 : 1.46; under the frozen rule, no dose-normalized second map
is reported.

## Results

The primary metric is FG-LPIPS; positive treatment-minus-baseline deltas are
worse because LPIPS is lower-is-better. The 15-cell paired bootstrap family
shows small but Holm-significant adverse changes in shallow W3, W4, and W5
(mean deltas +0.000464, +0.000450, +0.000457; adjusted p=0.0016 for each).
The remaining cells do not survive family-wise correction. Deep and middle
marginal FG-LPIPS changes are +0.000054 and −0.000004; the shallow marginal is
+0.000399.

The production additive-residual bootstrap interaction statistic is retained
in `g_formal_complete/layermap_g_complete.json` for reproducibility, but its
null distribution is centered at or above the observed statistic, as in the
prior audits. It is not treated as a valid interaction test. The cluster-
robust Wald reanalysis is exploratory because it was selected after the
zero-power defect was discovered. It gives:

| Metric | Wald statistic (8 df) | Raw p | Holm p across four metrics |
|---|---:|---:|---:|
| FG-LPIPS (primary) | 13.322 | 0.101 | 0.303 |
| PSNR | 7.995 | 0.434 | 0.868 |
| FG-SSIM | 16.243 | 0.039 | 0.156 |
| CIEDE2000 | 3.945 | 0.862 | 0.862 |

No metric is significant after this exploratory four-metric correction.
FG-SSIM's unadjusted result is recorded as a signal for future preregistered
confirmation, not as evidence of a confirmed interaction.

## Interpretation and scope

The frozen G scale range produces near-zero deep and middle responses and
small late-window worsening in shallow FG-LPIPS. It does not reproduce the
large, broad response map measured on the GeoTex backbone. The evidence
supports a **bounded, backbone-specific result for this scale range and
single-window intervention**. It does not establish universal insensitivity
of MV-Adapter, nor does it establish a confirmatory no-interaction result.
The interaction analysis and cross-metric signal remain exploratory; no
mapping re-search was performed.

## Reproducibility artifacts

- Frozen completion lock and hashes: `g_completion18/`
- Immutable original rows: `g_formal/`
- Deduplicated, completed analysis rows: `g_formal_complete/rows_shard0.json`
- Recomputed cell map and Holm family: `g_formal_complete/layermap_g_complete.json`
- Exploratory Wald analysis: `g_formal_complete/AUDIT_INTERACTION_VALID_TEST_G_COMPLETE.json`
- Merge and exclusion record: `g_formal_complete/MERGE_AUDIT.json` and
  `g_formal_complete/TECHNICAL_EXCLUSION_G_0098.json`
