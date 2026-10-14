# Figure 3 scientific decision — final text revision V4

**Authority:** PR #1 branch `codex/cg-final-v4-20261014`, starting source HEAD `11006e003842b25976e20cafd51a7970770f269f`. The final comparison uses the same revised main text, changing only the Figure 3 candidate, its aligned sentence, and its caption. Actual rendered page 9 for each candidate is in `FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.pdf` and the side-by-side image `FIGURE3_AB_ACTUAL_PAGES_FINAL_V4.png`.

## Evidence checked across the seven display-cleared Bake10 assets

All seven objects were reviewed at held-out raw camera 004 against their GT self-bake and the seven recorded generated settings. The review sheet `BAKE10_ALL_CONDITIONS_VIEW004.png` shows the same camera across columns; `BAKE10_SEVEN_COMPARISONS_VIEW004.png` compares GT self-bake, Fixed Mean and Late-high for all seven. `BAKE10_ELEVEN_VIEW_REVIEW_V4.pdf` preserves the same seven assets across all eleven unseen views. Every source render is 512×512. Figure 3 display panels use exact, pixel-identical crops from those source renders: candidate A uses 299×118 pixels; candidate B uses 392×372 for Tire and 469×222 for the font. Each object's crop is identical across its GT, Fixed Mean and Late-high panels. The six selected candidate-B source/display identities are hash-checked in `FIGURE3_B_SELECTION_V4.json` and `FIGURE3_IDENTITY_VALIDATION_V4.json`. Every asset has publication permission recorded in the source/credit manifests; Tire is CC BY 4.0 with attribution and the Baptisimal Font is CC0. No method-specific color adjustment or altered output pixel is used in either candidate.

The LPIPS values below are the existing eleven-view means against the source target. The GT column is the error of the matched reference self-bake; it is **not** a direct pairwise LPIPS between the self-bake and a generated bake. `Fixed−GT` and `Late−GT` in the assessment CSV are differences between those source-target errors.

| Asset | Input-property rank | GT self-bake FG-LPIPS | Fixed Mean | Late-high | Late−Mean | Reading of the same-camera renders |
|---|---:|---:|---:|---:|---:|---|
| LG Remote | 1 | 0.076739 | 0.153067 | 0.148982 | −0.004084 | Buttons and gray shell are identifiable in GT; generated textures turn brown and the schedule change is small. |
| Bricks on news boxes | 2 | 0.055970 | 0.177575 | 0.174395 | −0.003180 | Source colors and lettering are clear; generated conditions lose them, with little visible schedule separation. |
| Eastern Box Turtle Shell | 3 | 0.040515 | 0.109641 | 0.105189 | −0.004452 | Yellow shell panels are recognizable in GT; generated brown texture does not restore that material. |
| Tire | 4 | 0.073667 | 0.171982 | 0.169192 | −0.002791 | Dark tire and silver wheel are clear in GT; generated outputs become brown, while Fixed Mean and Late-high remain close. |
| Pittsburgh Bridge Collapse | 5 | 0.065250 | 0.093194 | 0.093169 | −0.000026 | Sparse scan detail limits object/material recognition; the two schedule outputs are nearly identical. |
| Stone | 6 | 0.023278 | 0.058953 | 0.058489 | −0.000464 | Lowest absolute FG-LPIPS among these seven, but near-zero schedule change and weak material discrimination. |
| Baptisimal Font | 7 | 0.141099 | 0.237632 | 0.229822 | −0.007810 | Gray carved relief is recognizable in GT; the generated version remains brown. This is the largest LPIPS decrease, with PSNR decreasing by 0.271 dB. |

Input-property rank uses source raw000 foreground Laplacian variance; it is an editorial display descriptor, not a material-quality rank or a representative population sample. All seven objects remain in their original statistical roles and queues. The full ten-object numeric cohort and generated conditions remain in Supplement S5.

## Candidate comparison and decision

**A — single Stone example.** The held-out-view Stone crop is enlarged to the maximum available panel width with the same crop for GT-256, Fixed Mean and Late-high; it uses the original display pixels without method-specific edits. This makes the object as legible as its low-profile scan permits, but the lowest absolute LPIPS still does not imply a larger schedule effect: Late-high−Fixed Mean is only −0.000464 FG-LPIPS and +0.001 dB FG-PSNR. The displayed schedule difference remains nearly imperceptible, and the similar earth-tone renders add little explanation of material preservation.

**B — input-property example plus declared post-outcome example.** The first row is Tire, selected before inspecting bake outcomes by the median source-foreground Laplacian variance among seven display-cleared assets. The second is the Baptisimal Font, explicitly selected after outcomes because it has the largest existing eleven-view LPIPS decrease among those seven. Its simultaneous −0.271 dB PSNR change makes the endpoint tradeoff visible. Both rows show GT-256, Fixed Mean and Late-high at the same raw004 unseen camera for that object, with a common within-object crop and original rendered pixels.

**Decision: use B in the main manuscript.** B has better explanatory evidence and page-level readability for this paper: it distinguishes an input-selected case from a post-outcome case and shows why the LPIPS change does not imply consistent improvement. B is not evidence of a cohort-wide visual benefit. Its caption and nearby prose label the post-outcome selection and the opposite PSNR direction; the full ten-object distribution remains in S5. Candidate A is retained as a review alternative. Neither the statistical queue nor any inferential result changed.

The final Figure 3 is `figures/fig3_bake10_two_object_v4.pdf`; the original pixels and file hashes are recorded in the candidate manifest. The prior one-object-plus-effect-strip candidate remains an archived review option and is not the current main figure.
