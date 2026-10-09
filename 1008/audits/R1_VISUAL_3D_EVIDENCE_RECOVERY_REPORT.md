# C&G 1008 R1.1 visual and 3D evidence recovery

**Disposition: partial evidence recovery; no new bake or rendering was run.**
The 01549 body file and its submitted figure sources remain unchanged. This
report separates 2D target-view comparisons, baked GLB unseen-view renders,
full PBR output, and UV-seam evidence; these are different endpoints.

## Evidence inventory

| Evidence item | Source identity / hash | Methods, views, seed, camera | UV / material / GT source | Validation and paper-use decision |
|---|---|---|---|---|
| Submitted 01549 Fig. 4 | `fig4.pdf`, SHA-256 `0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620` | Original local scale comparison; object/view-level source map is not recoverable from the PDF by itself. | 2D target-view figure; no UV/material sampler endpoint. | Hash verified. Preserve its original argumentative role, but do not present it as a newly verified or resolved example. |
| Submitted 01549 Fig. 6 | `fig6.pdf`, SHA-256 `585af2af647e9f169cb98320fb5779aaba158b3493ea054bea2ff8eef675546c` | Original C3 versus fixed-scale illustration; object/view/seed mapping is not recoverable from this PDF by itself. | 2D target-view figure; no baked-mesh or seam endpoint. | Hash verified. Keep the schedule-comparison role; replacement candidate should use the licensed Fresh C panels below. |
| Original 0907 supplementary files | Supplementary PDF `844af4caadd254548ee3b38c96916dcdb62d3e4d4ada6db5cff8bd1230fadfdd`; demo MP4 `54858b6b64679969c9e4a129a4dd5aeb69eecca1b3bb3322084a8c5a70370b8b`; narrated MP4 `520387e1e33cc952c4a172aac4ec17b0426f8a0eddd167a2da119ff7be441c39`. | Original 0907 submission package; not evidence for a new method comparison. | Supplementary/video assets. | The files are present and hash-verified locally. Reviewer-portal availability and playback are not verifiable from this workspace. |
| Fresh C whole-object visual pool | Gallery manifest SHA-256 `7b530ec596c1fb830c1f93618bd7dde86cae0ad4feb7f426efbe300e5376d548`; source image hash table `aceb48f5fdb48c47081b0c01143edd55fce536b6c1bfd389be4b653bbd0014f8`. | 20 object UIDs; Reference, GFL, GFH, No adapter, C3, LLH, and Generic linear; six frozen target views `0,15,12,16,13,14`; seed 42; same view IDs and source policy within object. | 2D RGB predictions and reference images only; UV/sampler not applicable. 240 reference/method source images and 20 generated panel hashes verified. | All 20 selected assets have `FIGURE_ONLY` disposition and verified CC-BY attribution. Use with the supplied credit lines. This is an outcome-ranked, illustrative pool, not a representative estimate. The 9 other cohort assets with unknown rights are excluded. |
| Formal Visual-24 panels | Archive manifest SHA-256 `7e127be130f3b7107e57b4b83c1e065c2185a717eef3a522c48d79461dcecf9c`; example panel `panel_11_00e2a79774964cb08f38c4406407300b.png` SHA-256 `968f0512cfbcaca5f71f1905c73975e13e8376b9eb3c2c3957babe1e6f56b4f8`. | GT-only stratified before outcomes, 24 objects, selection seed 20261002; generation seed 42; six target views; GT, No adapter, GFL, GFH, C3, LFM-EXACT, LHL, and LLH. Same reference draw/latent within object. | 2D target-view comparisons; UV/sampler not applicable. | Manual audit records color/material mismatch in 18/24, fine-detail loss in 21/24, thin-part readability issues in 3/24, small-part issues in 1/24, and cross-view readability concerns in 1/24. Internal descriptive evidence; publication rights were not cleared in this pass. It does not test baking or seams. |
| Historical GLB-native N=20 | Render-manifest SHA-256 `ba0f0e56efbac825c5a3d584bb3ef8a2699967b1063044287b39d2136235e550`; object metrics SHA-256 `b00e44f3c1f2555f5ab1de511437be6b77af694da2d0e5eb5c10fd42664c7057`; lineage SHA-256 `b3d93f401393933c60b787b4d10068b02fdaeceb27af958dbb5f381f98e44e9e`. | 20 UV-supported objects × 8 conditions (GT, No adapter, GFL, GFH, C3, LFM-EXACT, LHL, LLH); 160 GLBs; 11 frozen unseen views per object; seed 42; checkpoint `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`. Per-object/view camera hashes match across methods. | Historical CPU bake preserved source UVs; one base-color texture; GLB sampler `magFilter=LINEAR`, `minFilter=LINEAR_MIPMAP_LINEAR`, `wrapS/T=REPEAT`. GT is the reference-textured GLB. Renderer is unlit base-color only, not PBR. | All 160 GLB references, 1,760 render PNGs, 1,760 bake-metadata records, and 1,760 render hashes verified; 220 object/view camera groups have no camera disagreement. Use only as a bounded historical unseen-view endpoint. Population-level 3D superiority and perceptual material fidelity are not supported; redistribution rights for these mesh assets are unresolved. |
| Proposed Fresh C 24-object GLB bake | Fresh C cohort manifest SHA-256 `0f2c50f0bcce6678d578bd7ec4e8931e39606045b1b105ccbdae7546556a3859`; bake feasibility audit copied under `source_evidence/r1/`. | GT-only technical list of 24; no new method outputs or renders exist. | The planned bake could not preserve the frozen native UV/sampler behavior with the existing path; 9/24 inputs have out-of-range UVs and 5 assets / 27 primitives use unsupported BLEND. | Gate failed and the proposed result is retired. Eleven synthetic sampler checks do not validate a full asset bake, seams, or PBR. Do not use as positive evidence. |
| Old CPU / seam reports | Historical `FINAL_UNIFIED_3D_VALIDATION` SHA-256 `7de865dead0b72d0a2a25c676ee002520374e54c4f6b4c450c3b4b95590f5f2a`; `UNIFIED_COREDRAW_BAKE_REPORT` SHA-256 `9a6f3d07aae79508a465e2ea17f1b3b7ecc19e06b7b83cf46b49fbf06a0a489`. | Old CPU renderer and old seam metrics. | Clamp/mipmap behavior did not match the final GLB sampler semantics. | Superseded. Preserve the reports for provenance only; do not reuse their seam or unseen-view metrics. Current native renderer report SHA-256 is `3a28469e45efa89b677b8ed95d008e1707ce276d5b5c55744ff44ba67c28230c`. |

The native sampler audit (`4d466767c69403b86a3f7c0c16758595d2742971f61fd0f6ee9ed97d304e035f`), 3D-claim retirement (`c791ac437fbfa191302568e1ad8d1980e5ef110b85072d95ef28299d8b8973ea`), and seam disposition (`fd965968486973431634083cebdc8c99341904bc34696eb4114006b6ddef0aca`) are copied byte-identically under [`source_evidence/r1`](source_evidence/r1/). All copied sources and their source paths are listed in [`R1_SOURCE_EVIDENCE_MANIFEST.csv`](R1_SOURCE_EVIDENCE_MANIFEST.csv).

## Paired N=20 unseen-view results

The reanalysis uses one mean per object across the same 11 frozen unseen
views, then pairs methods by object. The 95% intervals are percentile
bootstraps over objects (10,000 draws, seed 20261005); the interval family is
descriptive and unadjusted. Positive PSNR favors C3; negative LPIPS and
CIEDE2000 favor C3.

| Contrast | Endpoint | Paired mean difference (95% object-bootstrap CI) | Objects favoring C3 | Result |
|---|---|---:|---:|---|
| C3−GFL | FG-PSNR | −0.066 dB [−0.413, +0.290] | 5/20 (25%) | No unseen-view PSNR advantage detected. |
| C3−GFL | FG-LPIPS | −0.004719 [−0.007504, −0.002544] | 17/20 (85%) | LPIPS favors C3. |
| C3−GFL | CIEDE2000 | +0.133 [−1.161, +1.319] | 6/20 (30%) | Color-difference endpoint does not favor C3 overall. |
| C3−GFH | FG-PSNR | +0.084 dB [−0.290, +0.426] | 14/20 (70%) | Interval crosses zero. |
| C3−GFH | FG-LPIPS | +0.007709 [+0.004230, +0.012101] | 4/20 (20%) | LPIPS favors GFH. |
| C3−GFH | CIEDE2000 | −1.027 [−2.224, +0.229] | 14/20 (70%) | Mean interval crosses zero. |
| C3−No adapter | FG-PSNR | +3.135 dB [+1.721, +4.493] | 18/20 (90%) | C3 is higher on this endpoint in this subset. |
| C3−No adapter | FG-LPIPS | −0.014519 [−0.029860, −0.001326] | 16/20 (80%) | LPIPS favors C3. |
| C3−No adapter | CIEDE2000 | −12.508 [−18.556, −6.529] | 18/20 (90%) | Color-difference favors C3 in this subset. |

The N=20 pool is the UV-compatible subset of a frozen 24-object technical
pool; four objects were excluded before baking because they lacked UVs. It is
not a random sample, not the Fresh C N=300 cohort, and not a complete
24-object estimate. The endpoints are mixed: C3 does not outperform GFL in
unseen-view PSNR or CIEDE2000, and GFH has lower LPIPS than C3. Do not
describe it as an overall 3D winner.

## Figure candidates and proposed placement

### 2D main-text candidates

[`R1_VISUAL_FIGURE_SELECTION.csv`](R1_VISUAL_FIGURE_SELECTION.csv) records all
20 Fresh C candidates, their metrics, source-image hashes, permissions,
attribution, and selection role. Six exact-byte panels were copied for
review; their source panel hashes match the gallery manifest:

| Proposed use | Candidate panel | Why it is included |
|---|---|---|
| Fig. 4 main comparison | [`main_candidate_typical_c3_gfl.png`](figure_candidates/main_candidate_typical_c3_gfl.png) | Near-median C3−GFL foreground PSNR; seven conditions and Reference in the same six-view layout. |
| Fig. 4 or Fig. 6 | [`main_candidate_c3_gfl_favorable.png`](figure_candidates/main_candidate_c3_gfl_favorable.png) | C3-favorable C3−GFL example. |
| Fig. 6 main comparison | [`main_candidate_c3_gfh_endpoint_tradeoff.png`](figure_candidates/main_candidate_c3_gfh_endpoint_tradeoff.png) | Shows opposing C3/GFH endpoint directions. |
| Fig. 6 main comparison | [`main_candidate_generic_linear_counterexample.png`](figure_candidates/main_candidate_generic_linear_counterexample.png) | Preserves a strong counterexample where generic linear is better. |
| Supplement / failure case | [`supplement_candidate_c3_gfl_adverse.png`](figure_candidates/supplement_candidate_c3_gfl_adverse.png) | C3 loses to GFL on both listed endpoints. |
| Supplement / appearance failure | [`supplement_candidate_color_pattern_detail_failure.png`](figure_candidates/supplement_candidate_color_pattern_detail_failure.png) | Shows muted color/detail mismatch and repeated vertical artifacts in the No-adapter column; these are not C3-specific claims. |

The Fresh C pool is selected after metric ranking. Every caption must say
“Illustrative selection, not a representative cohort estimate.” No manual
brightness, hue, sharpness, or per-method crop change was made; these six are
byte-identical copies of licensed source panels. Fig. 4 can retain its role
of showing local texture differences, and Fig. 6 can retain its schedule
comparison role, while the new table carries the numerical results. The
20-object pool can be supplied as a supplemental atlas if the authors choose;
the images are already recorded in the selection register and do not need to
be committed again here.

### Optional bounded 3D display

[`R1_3D_N20_UNLIT_BASECOLOR_INTERNAL.png`](figure_candidates/R1_3D_N20_UNLIT_BASECOLOR_INTERNAL.png)
is a review-only composition made from stored files. Its object rule is
explicit: the minimum, closest-to-median, and maximum object-level
C3-minus-GFL FG-PSNR deltas over the 11-view N=20 cohort, with UID tie-break.
The selected deltas are −1.860 dB, −0.286 dB, and +1.834 dB. Each object
shows one view-0 reference context and the same two unseen cameras (raw views
1 and 11) for GT/reference texture, No adapter, GFL, GFH, and C3. The
selection and all 30 render/GLB source hashes are in
[`R1_3D_FIGURE_SELECTION.csv`](R1_3D_FIGURE_SELECTION.csv). The montage only
arranges stored renders and uniformly resizes them for layout; it does not
alter method output color or regenerate any output.

The 3D source-asset redistribution rights were not verified, so this PNG is
local and internal-only, not included in the commit. It must not enter the
paper until rights are cleared. Its intended caption is: “Unlit base-color
renders of stored baked GLBs; three cases selected by the minimum,
median-nearest, and maximum C3−GFL unseen-view FG-PSNR differences. This
illustrative historical N=20 UV-supported subset does not establish PBR,
seam, perceptual-fidelity, or population-level 3D superiority.”

### Proposed response to Reviewer 1.1 (not filed)

1. **Purple color shifts.** “We now include side-by-side, same-view panels with the reference, no-adapter output, fixed low/high controls, C3, LLH, and generic linear. The panels and source hashes are recorded, and the selected Fresh C images have verified figure-only licenses with attribution. Color/material mismatch remains visible in the broader fixed Visual-24 audit; we do not claim that the shift is solved or unique to C3.”
2. **Repeated patterns.** “We retain a failure example that shows repeated vertical artifacts in the no-adapter output and report fine-detail loss in the fixed visual audit. We did not define a validated repetition-specific metric, so we do not claim that the schedule eliminates repeated patterns.”
3. **Whole-object comparisons.** “We provide same-object, same-view, six-view context for the seven image-space conditions and the reference. The 20 selected figure assets are hash-verified and attribution-cleared; because the gallery is post-metric ranked, it is explicitly illustrative rather than representative.”
4. **No-adapter and competitive fixed baselines.** “The comparisons include the unmodified no-adapter pipeline, native fixed-low GFL and fixed-high GFH, plus generic linear and LLH. We report the primary C3−GFL result and retain the negative Generic Linear and endpoint-dependent LLH results in the main comparison.”
5. **Baked unseen views.** “We independently verified the historical UV-preserving N=20 stored GLB set with the native GLB sampler and 11 fixed unseen views. The paired result is mixed: C3 has no detected GFL PSNR advantage, LPIPS favors C3, and CIEDE2000 does not. This is unlit base-color evidence from a technical subset, not full PBR or a claim of overall 3D superiority.”
6. **UV seams.** “We could not validate a seam endpoint. The earlier seam metric is retired; we therefore make no seam-improvement claim. The prior synthetic sampler checks are not a real-asset seam test.”
7. **Supplementary video access.** “The original 0907 supplementary PDF and both demo videos remain in the local submission package with their hashes recorded. We cannot verify the reviewer-portal copies or playback from this workspace, so we will reattach or relink them in the revision system and check the rendered proof before claiming access is resolved.”

## Evidence boundary

The 2D Fresh C and Formal Visual panels are image-space comparisons. They do
not establish UV seam quality, unseen-camera behavior, exported-material
PBR, or human-perceived reference fidelity. The N=20 GLB result is a valid,
bounded unlit base-color unseen-view endpoint with mixed results. The proposed
Fresh C 24-object bake did not pass its technical gate and produced no valid
panel. No validated seam endpoint is available.

**Gate:** `R1_VISUAL_EVIDENCE=PARTIAL`; `R1_BAKED_UNSEEN_VIEW=VALID_BOUNDED`;
`R1_SEAM_ENDPOINT=RETIRED`.
