# Final V4 layout and science check

## Build and placement

The V4 source and PDFs were rebuilt after confirming that the archived V3 manuscript TeX and PDF match the V3 manifest. The V4 main manuscript is 13 pages, with the complete reference list through [41] on page 13. The Supplement is 71 pages; Table S35 remains on page 58 and the original four-condition means in Table S36 remain on page 59. The response is 5 pages and the marked manuscript is 20 pages. The build logs report no LaTeX errors, undefined citations or undefined references.

| Content | V4 location |
|---|---:|
| Figure 3 and Table 5 | Main p. 9 |
| Table 6 | Main p. 10 |
| Figure 4 color/material failure | Main p. 10 |
| Table 7 | Main p. 11 |
| Final reference [41] | Main p. 13 |
| Supplement Table S35 | Supplement p. 58 |
| Supplement Table S36 | Supplement p. 59 |

Tables 1–2 retain the verified two-column layout. Tables 3–7 retain the V3 single-column layout. Table 5 carries the two distinct bake FG-LPIPS primaries; Table 7 keeps the original GeoTex Fresh C `Middle-high − mean(Early-high, Late-high)` FG-PSNR test as its first row. Table 8 remains out of the main text; its original means are in S36 without recalculation.

## Figure 3 visual review

The former three-row example used a small amount of page area for three low-saturation objects and made the principal bake comparison hard to inspect. V4 uses one rights-cleared object selected with an explicit criterion: lowest existing 11-view FG-LPIPS among the seven display-cleared objects for both Fixed Mean and Late-high. The selected values are 0.058953 and 0.058489. The three unseen-view panels share one crop and camera. The source projection view 000 is kept separate because it is not pose-matched to unseen view 004.

The selected bake remains visibly different from the GT-256 self-bake in color and texture. The figure is labelled as a post-outcome best-case illustration, not a representative result. Its source UID, author, CC Attribution license, URL, pixel hashes, camera/protocol identity and crop coordinates are recorded in the V4 selection files. No image was generated, recolored or selectively altered by method.

The source PNGs used for the figure are 512×512. The EGL render manifest's top-level renderer setting is also 512, and the hashed output PNGs are 512×512. The per-render `image_size` field says 1024×1024 for those same files; this inconsistency is preserved in the build report and not silently treated as source resolution.

## Scientific consistency

- The frozen primary remains −0.0338775 dB, 95% CI [−0.117170, +0.051422], paired sign-flip p = 0.432378. Its frozen-data validation remains PASS.
- No experiment result or inferential statistic was recomputed. No GPU supplementary experiment was run.
- R1's visual source explanation and inspectability improve. The figure does not establish faithful material color, texture, seams or PBR behavior; that limitation remains.
- R2.1 remains partly answered. The manuscript argues for a task-specific empirical contribution and does not claim a new general scheduling method, unique optimum or broad transfer result.
- No 01549 visual pixels were reused as current evidence.

These checks establish an internally consistent author-review package. They do not claim journal acceptance or replace author review.
