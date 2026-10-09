# R1.1 3D, seam, and delivery blockers

**Decision for this revision pass: no new experiment is required to make a
truthful, bounded response.** The current evidence does not fully close R1.1.
This file records what remains open; it is not a proposal to start a new bake.

| Gate | Current evidence | Blocker / permitted statement |
|---|---|---|
| 2D whole-object comparison | Fresh C has 20 six-view, same-object panels comparing the reference with No adapter, GFL, GFH, C3, LLH, and Generic linear. All 240 source-image hashes, 20 panel hashes, and 20 figure-only licenses/attributions passed. | The pool is post-metric ranked, so it supports illustrative cases only. Color/material mismatch and detail failures remain; the panel set does not establish human or 3D fidelity. |
| Baked unseen views | Historical N=20 has 160 stored GLBs and 1,760 native-sampler renders over 11 frozen unseen views. All referenced GLBs, bake metadata, render PNGs, method pairing, and camera groups passed hash checks. | Four of the original 24 lacked UVs. This is not Fresh C N=300 or a random 24-object estimate. Endpoint directions are mixed; claim only a bounded unlit base-color comparison. |
| Full PBR appearance | No full PBR render result is present in the current evidence set. | Do not write PBR quality, material fidelity, or perceptual appearance superiority. |
| Fresh C 24-object bake | The technical gate failed: the production bake path re-unwraps via xatlas; 9/24 source meshes have out-of-range native UVs; 5 assets / 27 primitives use unsupported BLEND. No valid 24-object method outputs were generated. | The new bake result is retired. The 11/11 synthetic sampler checks do not override this failure or validate a real mesh bake. Do not repair inputs and describe them as the frozen protocol. |
| UV seams | Prior seam metric is retired. The native sampler audit verifies GLB sampler interpretation; it is not a seam endpoint. | There is no verified ground-truth seam-free texture, inserted known seam, UV-island boundary test, repeat/mirrored-repeat/clamp truth set, mip/minification seam test, or rerun-determinism result. No seam score or seam-improvement claim is allowed. |
| N=20 figure redistribution | The source GLBs are on the local evidence store; the rights audit for these mesh sources is not complete. | The generated `R1_3D_N20_UNLIT_BASECOLOR_INTERNAL.png` is an internal candidate and is excluded from the commit. Clear source rights before paper or public distribution. |
| Formal Visual-24 redistribution | The 24 panels are valid for the internal pre-outcome visual audit. This pass did not clear every source mesh for figure redistribution. | Use the Fresh C CC-BY-cleared 20-object panel candidates for paper figures. Keep the Formal-24 panels internal until their rights are verified. |
| Supplementary-video access | The original `Supplementary material 0907.pdf`, `Demo 0907.mp4`, and `demo with narration 0907.mp4` are present in the local 0907 submission package with their hashes. | The reviewer portal and rendered proof are not available here, so prior external upload and playback cannot be verified. Do not report this item as resolved until the files are reattached/relinked and access is checked in the submission system. |
| Historical renderer/report consistency | The earlier CPU report has a clamp/mipmap mismatch and was superseded. The current GLB-native EGL report uses the stored GLB sampler behavior. | Do not mix earlier CPU metrics or retired seam statistics with the current native-render N=20 results. |

## Existing records checked for a no-new-output seam validation

The current reports establish sampler parsing and stored-render integrity,
not the requested seam truth table. The required independently defined
inputs/expected outcomes are absent: known seam-free material, an inserted
seam, UV-island boundary, addressing-mode edge cases, minification/mipmap
behavior, and a deterministic rerun check. Therefore a new seam claim cannot
be recovered from the existing files without adding a separately validated
protocol. No synthetic or real-asset seam test was started for this pass.

## Gate values

`R1_BAKED_UNSEEN_VIEW=VALID_BOUNDED`  
`R1_SEAM_ENDPOINT=RETIRED`  
`NEW_EXPERIMENT_REQUIRED=NO` for a revision that states these boundaries; a
future full PBR or seam claim would require a separately specified and
approved validation.
