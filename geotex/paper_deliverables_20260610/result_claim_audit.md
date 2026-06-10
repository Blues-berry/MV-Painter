# GeoTex-Adapter Result Claim Audit

## Verdict: CONDITIONAL PASS

---

## Main Claim (USE THIS)

> **GeoTex improves foreground reconstruction, edge fidelity, and perceptual quality.**

## Disallowed Claims (DO NOT USE)

| Claim | Reason |
|-------|--------|
| ~~GeoTex improves multi-view consistency.~~ | FALSE. Multi-view color consistency is NOT improved. |
| ~~GeoTex is universally better.~~ | 37/300 objects have FG SSIM regression. |
| ~~GeoTex preserves all edge structure.~~ | 12/300 objects have edge LPIPS regression. |
| ~~Background improvement is a core contribution.~~ | Background metrics are dominated by trivial white→white matching. |

---

## 300-Object Main Results

### Core Results (Foreground + Edge)

| Region | Metric | Original | GeoTex | Δ | Improved |
|--------|--------|----------|--------|---|----------|
| **Foreground** | PSNR ↑ | 6.41 | 12.41 | **+6.00** | 298/300 (99%) |
| **Foreground** | SSIM ↑ | 0.392 | 0.470 | **+0.078** | 263/300 (88%) |
| **Foreground** | LPIPS ↓ | 0.232 | 0.173 | **-0.059** | 299/300 (100%) |
| **Edge** | PSNR ↑ | 9.31 | 12.23 | **+2.91** | 291/300 (97%) |
| **Edge** | SSIM ↑ | 0.448 | 0.514 | **+0.065** | 292/300 (97%) |
| **Edge** | LPIPS ↓ | 0.101 | 0.075 | **-0.026** | 288/300 (96%) |

### Supplementary Results (Full + Background)

| Region | Metric | Original | GeoTex | Δ | Improved |
|--------|--------|----------|--------|---|----------|
| Full | PSNR ↑ | 10.07 | 20.23 | +10.15 | 300/300 (100%) |
| Full | SSIM ↑ | 0.793 | 0.909 | +0.117 | 300/300 (100%) |
| Full | LPIPS ↓ | 0.628 | 0.200 | -0.428 | 300/300 (100%) |
| Background | PSNR ↑ | 11.38 | 26.72 | +15.34 | 300/300 (100%) |

---

## Failure Points

| Issue | Count | Details |
|-------|-------|---------|
| FG SSIM regression | **37/300 (12%)** | Objects with minimal foreground or complex geometry |
| Edge LPIPS regression | **12/300 (4%)** | Minor, typically <0.03 increase |
| Multi-view consistency worsened | **32/50 (64%)** | View-dependent corrections increase color variance |

---

## Limitation: Multi-View Consistency

**GeoTex improves per-view fidelity but increases view-dependent color variance.**

This must be stated as a limitation, NOT as a contribution.

| Metric | Original | GeoTex | Interpretation |
|--------|----------|--------|----------------|
| Cross-view color std | 0.080 ± 0.039 | 0.107 ± 0.063 | Higher = worse cross-view consistency |
| Per-view color variance | 0.254 ± 0.060 | 0.205 ± 0.070 | Lower = cleaner per-view texture |
| Consistency improved | — | 18/50 (36%) | Minority of objects |

**Root cause:** The adapter adds geometry-aware residuals that are inherently view-specific (normal/depth vary per view), introducing color correction differences across views.

---

## Paper Claim Recommendations

### USE in Main Paper
- "GeoTex improves foreground reconstruction, edge fidelity, and perceptual quality."
- "FG PSNR improves by +6.00 dB on average across 300 test objects."
- "GeoTex produces sharper foreground textures and more accurate edge details."
- "Edge SSIM improves by +0.065, indicating better structural fidelity at object boundaries."

### DO NOT USE
- ❌ "GeoTex improves multi-view consistency."
- ❌ "GeoTex is universally better on all metrics."
- ❌ "Background improvement is a core contribution."
- ❌ "GeoTex preserves all edge structure perfectly."

### State as Limitation
- "GeoTex improves per-view fidelity but may introduce view-dependent color correction, increasing cross-view color variance."
- "37/300 objects show minor FG SSIM regression, typically for objects with minimal foreground."

---

## Figures Status

### comparison_figures/ (v1 — debug, not paper-ready)

| Figure | Status | Notes |
|--------|--------|-------|
| main_qualitative_comparison.png | ⚠️ Debug | 10 objects, has error maps — use v2 instead |
| foreground_edge_zoom_comparison.png | ❌ Debug | Crop quality poor, rainbow error — not paper-ready |
| worst_case_comparison.png | ⚠️ Debug | Has amplified error maps |
| paper_figure_contact_sheet.png | ⚠️ Debug | Combination of v1 figures |
| method_overview_geotex.md | ✅ Draft | Architecture diagram text |
| figure_caption_drafts.md | ✅ Draft | Updated for v2 figures |

### comparison_figures_v2/ (paper-ready)

| Figure | Status | Location |
|--------|--------|----------|
| main_visual_comparison_clean.png | ✅ Paper-ready | 6 objects, GT|Orig|GeoTex|Zoom×3 |
| edge_zoom_clean.png | ✅ Paper-ready | 6 objects, grayscale error, unified scale |
| paper_main_qualitative_candidate.png | ✅ Paper-ready | Final 6-object candidate |
| manual_visual_candidates.md | ✅ | 20 candidate objects for selection |
| visualization_bug_audit.md | ✅ | Audit confirming source images correct |
