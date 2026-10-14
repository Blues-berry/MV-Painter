# Figure 3 decision — V5

## Evidence checked

All seven display-cleared GeoTex Bake10 objects were reviewed at the same held-out raw camera 004, with GT-256 self-bake, Fixed Mean, and Late-high shown under the same mesh/UV and within-object crop. Every source render is 512×512 pixels; each display crop is pixel-identical to its source render. No method-specific color edit or output-pixel change was made. The license for each source is listed below; display permissions and required attributions are recorded in the asset ledgers and Supplement S9. The actual V5 page-9 comparison is `FIGURE3_AB_ACTUAL_PAGES_FINAL_V5.pdf` and `.png`.

LPIPS values below are the existing eleven-view means against the source target. The GT column is the matched reference self-bake's own target error, not a direct pairwise distance between the GT and generated bakes.

| Asset | Input-property rank | Source license | GT self-bake FG-LPIPS | Fixed Mean | Late-high | Late−Mean | Same-camera appearance |
|---|---:|---|---:|---:|---:|---:|---|
| LG Remote | 1 | CC BY, attribution required | 0.076739 | 0.153067 | 0.148982 | −0.004084 | Buttons and gray shell are identifiable in GT; generated versions turn brown and schedule changes are small. |
| Bricks on news boxes | 2 | CC BY, attribution required | 0.055970 | 0.177575 | 0.174395 | −0.003180 | Source colors and lettering are clear; generated conditions lose them, with little visible schedule separation. |
| Eastern Box Turtle Shell | 3 | CC BY, attribution required | 0.040515 | 0.109641 | 0.105189 | −0.004452 | Yellow shell panels are recognizable in GT; generated brown texture does not restore that material. |
| Tire | 4 | CC BY, attribution required | 0.073667 | 0.171982 | 0.169192 | −0.002791 | Dark tire and silver wheel are clear in GT; generated outputs turn brown, while Fixed Mean and Late-high stay close. |
| Pittsburgh Bridge Collapse | 5 | CC BY, attribution required | 0.065250 | 0.093194 | 0.093169 | −0.000026 | Sparse scan detail limits object/material recognition; the two schedules are nearly identical. |
| Stone | 6 | CC BY, attribution required | 0.023278 | 0.058953 | 0.058489 | −0.000464 | Lowest absolute FG-LPIPS among the seven, but almost no schedule change and weak material discrimination. |
| Baptisimal Font | 7 | CC0, public domain | 0.141099 | 0.237632 | 0.229822 | −0.007810 | Gray carved relief is clear in GT; the generated version remains brown. It has the largest LPIPS decrease, alongside a 0.271 dB PSNR decrease. |

Input-property rank is based on source foreground Laplacian variance. It is an editorial display descriptor, not a material-quality rank or a representative population sample. All seven objects remain in their original statistical roles and queues; the complete ten-object numerical cohort is unchanged in S5.

Candidate A's shared source crop is 299×118 pixels. Candidate B uses 392×372 for Tire and 469×222 for the Font. Each crop is the same exact pixel region across that object's GT-256, Fixed Mean and Late-high renders.

## Candidate comparison

**A — Stone.** Stone has the lowest absolute FG-LPIPS, but its Late-high−Fixed Mean change is only −0.000464 FG-LPIPS and +0.001 dB FG-PSNR. The actual page shows a low-profile scan with a barely visible schedule difference. Enlarging its crop cannot make the asset's material or schedule effect more legible.

**B — Tire plus Baptisimal Font.** Tire is selected before inspecting bake outcomes by median source foreground Laplacian variance among the seven display-cleared assets. The Font is explicitly selected post hoc because it has the largest existing eleven-view LPIPS decrease; its PSNR also declines by 0.271 dB. Both use the same held-out camera within object and show GT-256, Fixed Mean, and Late-high. The larger, more recognizable geometry makes the persistent appearance mismatch legible, while the Font demonstrates why an LPIPS-only improvement is not a general schedule benefit.

**Decision: retain B in the V5 main manuscript.** B has better scientific explanatory value and page-level readability. Its caption discloses the post-outcome selection, opposite PSNR change, source resolution, common camera and crop, and limits on prevalence/generalization. A is retained as a review alternative. Neither candidate modifies pixels or statistical selection.
