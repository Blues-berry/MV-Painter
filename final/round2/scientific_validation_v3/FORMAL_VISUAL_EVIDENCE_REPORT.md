# Formal visual evidence report — Experiment D

## Frozen sample and panels

The 24-object Visualization cohort was selected before outcomes from GT-only
texture, coverage, and geometry strata (seed 20261002). Each panel contains
the fixed six target views for GT and same-draw predictions for no-adapter,
native GFL, native GFH, native GC3, LFM-EXACT, LHL, and LLH. The archive has
24/24 panels and a complete contact sheet. Predictions are byte-frozen formal
campaign outputs; conditions share the same reference draw and latent seed.

- Full fixed-sample sheet: `formal_qualitative_archive/contact_sheet_24.png`
- Per-object visual labels and notes: `FORMAL_VISUAL_PANEL_CLASSIFICATION.csv`
- Deterministic rank selections and metric provenance:
  `formal_visual_evidence/VISUAL_RANK_SELECTIONS.json`
- Rank rule: `FORMAL_VISUAL_RANK_PROTOCOL.md`

## Metric-ranked examples

The three additional examples apply the locked H4 primary FG-PSNR rule to
LLH−native GFL within the already frozen 24 objects. They are selected
illustrations from an observed cohort, not independent estimates.

| Rank | UID | LLH−GFL FG-PSNR | Panel |
|---|---|---:|---|
| Strongest win | `028ca741606e480884f69d6df12553df` | +6.291 dB | `formal_visual_evidence/strongest_win.png` |
| Median effect | `00002bcb84af4a4781174e62619f14e2` | −0.775 dB | `formal_visual_evidence/median_effect.png` |
| Strongest loss | `0253574c1a8f432797a7fcef9546ce75` | −3.803 dB | `formal_visual_evidence/strongest_loss.png` |

The median example is the UID closest to the ordinary median of the 24 paired
FG-PSNR deltas; tied choices use the smallest UID. The extreme examples use
the largest and smallest paired deltas, with the same tie rule.

## Texture-rich failure sheet

The six highest GT Laplacian-variance objects in the fixed 24 are shown in
`formal_visual_evidence/texture_rich_failure_sheet.png`. This subset is
selected only by the frozen GT texture statistic. It is descriptive and does
not estimate a population failure rate.

## Manual findings

All 24 fixed panels were manually inspected at full panel resolution, and
the three ranked examples plus the six-object texture-rich sheet were
visually checked. The existing classification records visible properties
only:

| Visible class | Panels |
|---|---:|
| Color/material mismatch | 18/24 |
| Fine-detail loss | 21/24 |
| Thin-part readability issue | 3/24 |
| Small-part readability issue | 1/24 |
| Cross-view readability concern | 1/24 |

Common failures include muted tan/brown outputs replacing varied reference
colors and the loss or smoothing of fine surface patterns. Coarse object form
is often recognizable. The schedule columns do not show a stable visible
winner across the fixed sample. The strongest metric-ranked win still has a
visible material mismatch; therefore its scalar PSNR rank cannot establish
faithful material reproduction. These labels come from the images, not from
scalar metrics.

## Evidence boundary

This is a descriptive review of a preselected 24-object set, not a blinded
human preference study or a population estimate. The 2D panels do not test UV
seams, unseen cameras, or final baked 3D quality; those are reported
separately in `UNIFIED_COREDRAW_BAKE_REPORT.md`. A metric-ranked panel is not
evidence of perceptual superiority. The remaining metric/visual gap means
texture fidelity is only partially supported without human evaluation.

## Human preference study status

The earlier 72-item-per-participant draft was superseded before distribution
or response collection. A balanced 40-slot design now assigns 24 items per
participant (8 per method pair; all objects and GT texture strata balanced).
The amended protocol and participant site are SHA-frozen in
`HUMAN_PREFERENCE_STUDY_PROTOCOL_AMENDMENT_20261005.md` and
`human_study_site/HUMAN_STUDY_SITE_FREEZE.md`. No participant responses have
been collected; this does not yet close the perceptual evidence gap.
