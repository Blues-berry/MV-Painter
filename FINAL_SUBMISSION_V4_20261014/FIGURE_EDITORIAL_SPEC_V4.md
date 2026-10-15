# Figure editorial specification — concrete changes for the revised V4 text

Authority: V4 PR #1 at 84d4b0da (14-page manuscript). Editorial companion: `FINAL_V4_MANUSCRIPT_EDITORIAL_DRAFT.tex`. **This is a figure construction brief, not permission to replace data or fabricate visuals.** Keep all native files, samples, licenses, cameras, and quantitative results unchanged.

## Figure 1 — KEEP
Existing `figures/fig1_tcas_control.pdf` explains source input, geometry conditions, frozen GeoTex residual path, native cap and applied scalar `s_app`. Preserve it. Optional readability-only correction: enlarge the shallow-group clipping annotation if space permits. Do not add unmeasured model pathways.

Suggested caption opening:
"Implemented geometry-control interface. TCAS changes the requested multiplier on an existing frozen GeoTex residual branch; wrapper-specific native caps determine the applied multiplier before feature addition. This intervention does not train a new adapter, change the base U-Net, or implement UV baking."

## Figure 2 — REBUILD VISUALLY, retain validated scientific meaning
Current p. 7 has five columns (Target, Fixed Low, C3, Fixed High, Generic Linear) and three rows: Green Iguan, Mosque, Specimen 103. The GT images are strongly blue/green while outputs are largely brown, and differences among schedule outputs are difficult to see.

Preferred construction:
- Keep exactly those five columns and one camera (raw view 000) for every method within a row.
- Enlarge readable object crops in a TWO-ROW main figure if a clean source-property-selected example is available. Use one source-property-selected textured object plus one case illustrating competing controls. Both must be matched by UID, checkpoint, seed, camera, output tile, and crop; do not recalculate or improve images.
- Place the third, deliberately adverse example in Supplement S9 with its complete five-column comparison if page area is limiting.
- If an alternative rights-cleared object lacks an intact provenance chain or has equal/worse visibility, keep the validated current three-row figure rather than presenting a visually attractive unauthenticated output.
- Labels must explicitly distinguish source-property selection from post-outcome selection. Target is a source conditioning render, not physical albedo. No image-specific color correction.

Ready-to-use caption template, to finalize only AFTER freezing the actual displayed UIDs:
"Generated-view comparison on matched Fresh C inputs and camera 000. Columns show the source RGB target and four settings executed with the same frozen checkpoint, input, and object seed. Each row uses a shared full-object framing and no method-specific color adjustment. [Row A selection rule and UID]. [Row B selection rule and UID]. These illustrations do not estimate cohort prevalence; Table 2 reports the complete paired evaluation."

## Figure 3 — REPLACE THE CURRENT TIRE+TINY-DOT-PLOT COMPOSITION
Existing p. 9 combines a large but severely mismatched tire with a very small ten-object LPIPS strip. It is scientifically honest but not a good main method/asset figure. **Keep the full ten-object strip in Supplement S5** and present two larger same-camera asset rows in the main figure if their rendered quality is acceptable.

Source-verified candidates from the V4 seven-rights-cleared-asset ranking (11-view mean foreground LPIPS; Late-high minus Fixed Mean):
- Tire (`21678bd623654182b52c11d013de4e71`): 0.171982 -> 0.169192, change -0.002791; PSNR +0.257 dB. Its original p.9 matched-camera outputs are visibly brown against dark gray GT. Use as an honest limitation only, not the positive headline image.
- Eastern Box Turtle Shell (`85a7df80b79a4ba9b8c3a175de0dbce6`): 0.109641 -> 0.105189, change -0.004452; PSNR 12.161 -> 12.827 dB. Potential candidate to INSPECT, not a pre-approved final row.
- LG Remote (`1dc2c857f7614caeb6c2aa0559ccf973`): 0.153067 -> 0.148982, change -0.004085; PSNR 11.711 -> 12.135 dB. Potential candidate to INSPECT.
- Baptisimal Font (`2dd9bc8172c6461797947cc7214db399`): 0.237632 -> 0.229822, change -0.007810; PSNR 15.520 -> 15.249 dB. This is the largest LPIPS benefit among seven but has an opposite PSNR direction. If shown, mark as POST-OUTCOME tradeoff, not typical.
- Stone (`238ff3e41c964655b83aa9c8770cc766`): 0.058953 -> 0.058489, change -0.000464. Lowest absolute LPIPS but almost no schedule difference; do not choose it solely for lowest LPIPS.

Display priority is recognizability of source material and readable error diagnosis, never artificial performance improvement. Use two large rows of "GT-256 reference bake | Fixed Mean | Late-high" at the SAME actual held-out camera per row, same mesh/UV, common crop and output resolution. Source input at raw000 must be kept in a separate inset or in Supplement when the unmatched camera causes confusion. Each displayed method must use its ORIGINAL rendered RGB pixels. All candidate UIDs/rights must be checked again for exact cameras and image hashes before publication.

Recommended caption template:
"Native-UV appearance at held-out cameras. For each selected object, GT-256 is the resolution-matched reference self-bake, followed by Fixed Mean and Late-high rendered from the same unseen camera using identical mesh, UV coordinates, and crop. The displayed objects were chosen by [explicit per-row criterion]; any outcome-selected example is labelled as such. Although the ten-object pilot shows a small average LPIPS benefit for Late-high (Table 5; full per-object distribution in Supplement S5), these images do not demonstrate faithful color, surface material, seam, or PBR reproduction."

When Figure 3 is updated, replace in the editorial TeX:
"Figure~\\ref{fig:baked-context} connects a matched-camera texture example with the full ten-object effect distribution"
with
"Figure~\\ref{fig:baked-context} illustrates matched-camera texture appearance on two audited objects; the complete ten-object distribution is retained in Supplementary Section~S5".
Also update the figure caption and asset credits to match selected UIDs.

## Figure 4 — KEEP as a specific failure diagnostic
Current Figure 4 shows a shared frame/crop and a gray-to-brown reference mismatch. This is directly responsive to the reviewer concern. Keep one failure panel with brief mechanism-neutral caption; do not imply that color failure is solved or that texture-variation proxies measure fidelity. Prefer placement near Section 4.3, rather than having it appear amid the MV-Adapter section due to float movement.

## DO NOT DO
Do not reuse unverified 01549 output pixels; invent albedo or PBR ground truth; show a projection input as if camera-matched to unseen bake renders; interpolate scores for unrecorded views; crop one method differently; publish a best case as typical; or change frozen confidence intervals and test families. If two sufficiently readable, traceable Bake10 assets cannot be found, keep one validated example and state explicitly that usable material appearance remains limited.
