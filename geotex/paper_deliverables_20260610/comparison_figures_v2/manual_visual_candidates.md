# Manual Visual Candidates
**Purpose:** 20 candidate objects for paper qualitative figures
**Selection criteria:** Top improvements, median, worst cases
**Total objects evaluated:** 300

## Summary Table

| # | Object | ΔFG PSNR | ΔFG SSIM | ΔFG LPIPS | ΔEdge SSIM | Category | Suitable Main? | Reason |
|---|--------|----------|----------|-----------|------------|----------|----------------|--------|
| 1 | 110 | +13.40 | +0.175 | -0.141 | +0.075 | top_psnr | 是 | 边缘改善 / 纹理改善 |
| 2 | 008 | +11.49 | +0.170 | -0.081 | +0.143 | top_psnr | 是 | 边缘改善 / 纹理改善 |
| 3 | 098 | +10.49 | +0.191 | -0.104 | +0.080 | top_psnr | 是 | 边缘改善 / 纹理改善 |
| 4 | 038 | +10.40 | +0.152 | -0.165 | +0.061 | top_psnr | 是 | 边缘改善 / 纹理改善 |
| 5 | 025 | +8.01 | +0.332 | -0.064 | +0.099 | top_ssim | 是 | 结构改善 / 纹理改善 |
| 6 | 010 | +9.42 | +0.288 | -0.084 | +0.112 | top_ssim | 是 | 结构改善 / 纹理改善 |
| 7 | 026 | +10.01 | +0.235 | -0.170 | +0.130 | top_ssim | 是 | 结构改善 / 纹理改善 |
| 8 | 007 | +7.85 | +0.228 | -0.054 | +0.092 | top_ssim | 是 | 结构改善 / 纹理改善 |
| 9 | 241 | +6.10 | +0.123 | -0.089 | +0.096 | median | 是 | 中位数提升，代表性案例 |
| 10 | 012 | +6.12 | +0.053 | -0.075 | +0.077 | median | 是 | 中位数提升，代表性案例 |
| 11 | 087 | +6.19 | -0.019 | -0.053 | +0.020 | median | 是 | 中位数提升，代表性案例 |
| 12 | 065 | +6.19 | +0.058 | -0.034 | +0.075 | median | 是 | 中位数提升，代表性案例 |
| 13 | 268 | +0.32 | -0.056 | -0.049 | +0.063 | worst_psnr | 否 (supplementary) | PSNR 回退或微弱提升 |
| 14 | 031 | +0.19 | +0.002 | -0.028 | -0.001 | worst_psnr | 否 (supplementary) | PSNR 回退或微弱提升 |
| 15 | 245 | -0.36 | -0.077 | -0.036 | -0.017 | worst_psnr | 否 (supplementary) | PSNR 回退或微弱提升 |
| 16 | 029 | -0.50 | +0.011 | +0.001 | -0.013 | worst_psnr | 否 (supplementary) | PSNR 回退或微弱提升 |
| 17 | 161 | +0.95 | -0.076 | -0.058 | +0.127 | worst_ssim | 否 (supplementary) | SSIM 回退，可能平滑失败 |
| 18 | 252 | +0.54 | -0.091 | -0.009 | +0.013 | worst_ssim | 否 (supplementary) | SSIM 回退，可能平滑失败 |
| 19 | 184 | +4.22 | -0.097 | -0.042 | +0.008 | worst_ssim | 否 (supplementary) | SSIM 回退，可能平滑失败 |

## Category Breakdown

### top_psnr (4 objects)

- **obj_110**: FG_PSNR=+13.40, FG_SSIM=+0.175, FG_LPIPS=-0.141
- **obj_008**: FG_PSNR=+11.49, FG_SSIM=+0.170, FG_LPIPS=-0.081
- **obj_098**: FG_PSNR=+10.49, FG_SSIM=+0.191, FG_LPIPS=-0.104
- **obj_038**: FG_PSNR=+10.40, FG_SSIM=+0.152, FG_LPIPS=-0.165

### top_ssim (4 objects)

- **obj_025**: FG_PSNR=+8.01, FG_SSIM=+0.332, FG_LPIPS=-0.064
- **obj_010**: FG_PSNR=+9.42, FG_SSIM=+0.288, FG_LPIPS=-0.084
- **obj_026**: FG_PSNR=+10.01, FG_SSIM=+0.235, FG_LPIPS=-0.170
- **obj_007**: FG_PSNR=+7.85, FG_SSIM=+0.228, FG_LPIPS=-0.054

### median (4 objects)

- **obj_241**: FG_PSNR=+6.10, FG_SSIM=+0.123, FG_LPIPS=-0.089
- **obj_012**: FG_PSNR=+6.12, FG_SSIM=+0.053, FG_LPIPS=-0.075
- **obj_087**: FG_PSNR=+6.19, FG_SSIM=-0.019, FG_LPIPS=-0.053
- **obj_065**: FG_PSNR=+6.19, FG_SSIM=+0.058, FG_LPIPS=-0.034

### worst_psnr (4 objects)

- **obj_268**: FG_PSNR=+0.32, FG_SSIM=-0.056, FG_LPIPS=-0.049
- **obj_031**: FG_PSNR=+0.19, FG_SSIM=+0.002, FG_LPIPS=-0.028
- **obj_245**: FG_PSNR=-0.36, FG_SSIM=-0.077, FG_LPIPS=-0.036
- **obj_029**: FG_PSNR=-0.50, FG_SSIM=+0.011, FG_LPIPS=+0.001

### worst_ssim (3 objects)

- **obj_161**: FG_PSNR=+0.95, FG_SSIM=-0.076, FG_LPIPS=-0.058
- **obj_252**: FG_PSNR=+0.54, FG_SSIM=-0.091, FG_LPIPS=-0.009
- **obj_184**: FG_PSNR=+4.22, FG_SSIM=-0.097, FG_LPIPS=-0.042

## Recommended for Paper Main Figure (6 objects)

From the 20 candidates, select:
1. **2 clear improvements**: obj_110 (PSNR 13.4), obj_008 (PSNR 11.5)
2. **2 good improvements**: obj_025 (SSIM 0.332), obj_010 (SSIM 0.288)
3. **2 marginal/failure**: obj_268 (PSNR 0.32), obj_031 (PSNR 0.19)

**Note:** Only objects 0-9 have saved visualization images. Objects 10+ need re-eval with --save_vis.
