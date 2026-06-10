# GeoTex Paper Deliverables — 2026-06-10

## Overview

GeoTex-Adapter 300-object evaluation results, visual comparison figures, and code audit for paper submission.

**Verdict:** CONDITIONAL PASS — suitable as main paper direction with multi-view consistency limitation.

## Contents

```
paper_deliverables_20260610/
├── README.md                          # This file
├── result_claim_audit.md              # Claim audit: what to write / not write
├── final_visual_refactor_summary.md   # Complete summary of results + figures
├── eval.py                            # Evaluation script (442 lines)
├── train.py                           # Training script (231 lines)
├── make_comparison_figures.py         # Visual figure generation (220 lines)
├── analyze_300obj.py                  # 300-object analysis (317 lines)
├── comparison_figures_v2/             # Paper-ready figures
│   ├── main_visual_comparison_clean.png
│   ├── edge_zoom_clean.png
│   ├── paper_main_qualitative_candidate.png
│   ├── manual_visual_candidates.md
│   └── visualization_bug_audit.md
├── original_auth_audit/               # Original baseline authenticity check
│   ├── original_baseline_authenticity_report.md
│   └── obj_XXX/                       # Raw images for 6 objects
└── refactor/                          # Code structure docs
    ├── code_structure_final.md
    ├── model_unet_geotex_refactor_plan.md
    ├── refactor_round3_summary.md
    └── smoke_test_report.md
```

## Key Numbers

| Region | Metric | Original | GeoTex | Δ |
|--------|--------|----------|--------|---|
| Foreground | PSNR | 6.41 | 12.41 | **+6.00** |
| Foreground | SSIM | 0.392 | 0.470 | **+0.078** |
| Foreground | LPIPS | 0.232 | 0.173 | **-0.059** |
| Edge | PSNR | 9.31 | 12.23 | **+2.91** |
| Edge | SSIM | 0.448 | 0.514 | **+0.065** |
| Edge | LPIPS | 0.101 | 0.075 | **-0.026** |

## Main Claim

> GeoTex improves foreground reconstruction, edge fidelity, and perceptual quality.

## Limitation

> GeoTex improves per-view fidelity but may introduce view-dependent color correction, increasing cross-view color variance.

## Checkpoint

`mvpoutput/geotex_checkpoints/geotex_step_0002000.pt`

## Branch

`new0529`
