# V4 Figure 3 selection record

## Decision

The previous three-row Figure 3 was visually busy and did not give the Bake10 result enough image area. V4 shows one rights-cleared best-case object at the same held-out camera across GT-256, Fixed Mean and Late-high. The source projection image is shown separately because its raw view 000 is not pose-matched to unseen raw view 004.

## Selection rule

The candidate frame is the seven Bake10 assets cleared for publication display. We ranked the existing object-level 11-view mean foreground LPIPS values for Fixed Mean and Late-high. The selected UID `238ff3e41c964655b83aa9c8770cc766` has the lowest existing value for each schedule among those seven: Fixed Mean `0.05895328`, Late-high `0.05848895`. No score, metric, experiment or inferential test was recomputed. The table retains the original ten-object bake results. This post-outcome best-case illustration is not a prevalence estimate or a claim of general material fidelity.

## Display and provenance

- Asset: `หิน`; UID `238ff3e41c964655b83aa9c8770cc766`; creator `suntaree`; CC Attribution; [source record](https://sketchfab.com/3d-models/238ff3e41c964655b83aa9c8770cc766).
- Source input: 512×512 at projection raw view 000. It is not pose-matched to the unseen render panels.
- GT-256, Fixed Mean and Late-high: 512×512 native-UV GLB renders at held-out unseen raw view 004. Those three panels use one shared pixel crop; display uses white-background compositing and scale-to-fit, without per-method recoloring or image editing.
- GT-256 is a reference self-bake, not an upper bound. Within this UID, the three output GLBs share the source mesh and UV coordinates.
- Source bytes, crop coordinates, image hashes, camera/protocol identifiers, selection rank and license are in `FIGURE3_SELECTION_PROVENANCE_V4.csv` and `BAKE10_CANDIDATE_RANKING_V4.csv`.

## Interpretation

The selected case has the strongest available reference-relative image match in this display-eligible set, yet the bake panels still show color and texture differences. It is useful as a best-case illustration only. The manuscript continues to state that lower LPIPS does not establish faithful materials, seams or PBR quality. No 01549 image pixels were reused and no GPU experiment was run.
