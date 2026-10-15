# TCAS Demo V5 — English narration script

Delivery: clear, neutral, steady pace. Speaker notes in the PowerPoint use the same text.
Voice: locally generated with Piper TTS, en_US-lessac-medium. The narration is AI-generated.

## 01 | Title

This demo uses AI-generated narration. This presentation summarizes the V5 journal study of timestep-conditioned adapter scaling for multi-view diffusion texture generation. The focus is what survives comparison with strong controls and evaluation on baked assets.

## 02 | The graphics task

For graphics, generated RGB views are intermediate. The deliverable is a textured mesh whose appearance should be checked from cameras not used to generate or bake its texture. Projection, UV coverage, and resampling can change the result. This study connects image-space scores to that asset-level outcome.

## 03 | The executed intervention

TCAS changes the requested multiplier on an existing GeoTex adapter residual; it does not add a learned module. The historical C3 profile requests 1.25, 2.50, and 1.25 across early, middle, and late windows. In Fresh C, the shallow group is capped at 0.80 throughout. The realized correction also depends on the evolving hidden state, so a scale label is not a residual-dose measurement.

## 04 | Strong controls on 300 objects

On 300 held-out objects, C3 improves foreground PSNR over Fixed Low by 0.522 decibels. That comparison also raises the deep and middle applied-scale sums from 62.5 to 82.5. Fixed High and Generic Linear have better means than C3 across all four evaluated image endpoints. This revises the interpretation of the original low-versus-high-versus-low result. The figure shows examples, not an estimate of typical appearance.

## 05 | Matched-budget timing test

The specified timing primary compares Middle-high with the object-wise average of Early-high and Late-high at matched per-group applied-scale sums. The mean difference is minus 0.0339 decibels, with a 95 percent interval from minus 0.1172 to plus 0.0514 and a p-value of 0.432. It detects no middle-window advantage and does not establish equivalence. Retrospective pairwise contrasts differ in opposite directions, indicating within-cohort placement sensitivity without selecting a preferred schedule.

## 06 | Native-UV baking

In the compatibility-selected GeoTex bake pilot, Late-high—not C3—reduces unseen-view LPIPS relative to Fixed Mean by 0.00265 on ten objects. The change closes about 3.7 percent of the mean reference self-bake gap, while substantial appearance error remains. A separate twenty-object GSO bake study does not detect the same benefit under its distinct protocol.

## 07 | Appearance boundary

The visual comparison makes the remaining reference-appearance gap concrete. Image-space improvements do not establish faithful color or material reproduction. The bake evaluation uses unlit base color; it does not test a physically based material or lighting pipeline.

## 08 | Native-interface boundaries

The two MV-Adapter timing primaries also do not detect their specified middle-window contrasts: plus 0.029 decibels on fifty objects and minus 0.014 on the GSO one-hundred-object cohort, with both intervals spanning zero. These are separate cohorts and primary comparisons. GSO one hundred uses the same MV-Adapter interface, so it is not an independent backbone replication.

## 09 | Graphics contribution

The contribution is an evidence chain for an implemented graphics control. We report requested values, cap-adjusted applied values, and state-dependent corrections; compare C3 with competitive fixed and linear controls and a matched scalar budget; then evaluate native UV bakes from unseen cameras and test boundaries across interfaces. The findings support reporting the executed interface and asset response, not a universal schedule recommendation.

## 10 | Data and conclusion

The limited public data release is archived as Zenodo version 1.0.1 at DOI 10.5281 slash zenodo dot 23383807. It contains selected derived metrics and attribution records. It excludes source meshes and textures, generated-image archives, model weights, checkpoints, and participant-level responses. Overall, the evidence does not identify a universally preferred schedule or establish faithful material reproduction. Thank you.
