# GLB-native unseen-view audit — 2026-10-06

## Decision

The old software renderer's clamp-versus-repeat and bilinear-versus-mipmap
mismatch is resolved for the **stored N=20, eight-condition GLB outputs**.
All 1,760 exported GLB renders were reevaluated with the embedded glTF
base-color sampler. This is a renderer correction and an evaluation of the
existing output files; **no texture was rebaked** and no source bake code or
manuscript was changed.

The results do not establish a unique Layer-LLH advantage. Against
`native_gfl`, LLH has lower FG-LPIPS but no FG-PSNR advantage, and CIEDE2000
does not favor LLH. The strict 24-object 3D scope remains unsupported because
four source objects without UVs were excluded before baking. Base-color
rendering also does not establish human-perceived material fidelity.

## Reproducible rendering path

`audit_scripts/render_glb_native_egl.py` reads positions, indices, UVs,
materials, images, and sampler fields from each exact exported GLB. It applies
the GLB scene-node transforms, maps GLB Y-up coordinates back to the frozen
handoff camera basis, applies the frozen normalization and orthographic camera,
then samples the embedded base-color image in a depth-tested OpenGL pass. The
coordinate mapping was checked against each frozen Blender bounding box; the
largest absolute axis error across the 20 objects is 0.00279 source units.

All 160 GLBs have one baked base-color texture and sampler, `magFilter=9729`
and `minFilter=9987`. They omit `wrapS` and `wrapT`; under the [glTF 2.0
sampler defaults](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html),
both address modes are REPEAT. The renderer uses `GL_SRGB8_ALPHA8`, the
embedded UV values without a V flip, top-down PNG upload, linear magnification,
trilinear mipmapped minification, and the frozen 24-bit depth buffer. A
synthetic asymmetric 2×2 texture probe passed the four orientation samples
and negative/>1 repeat samples before the study render.

Runtime: NVIDIA GeForce RTX 5090, EGL, OpenGL 4.1. The renderer is deliberately
**unlit base-color-only**, matching the texture-only endpoint definition; it is
not a full PBR viewer render. The exact run, input hashes, per-image hashes,
camera hashes, sampler records, and bounding-box errors are in
`bake_handoff/GLB_NATIVE_EGL_RENDER_V1/GLB_NATIVE_EGL_RENDER_MANIFEST.json`.
The 1,760 output PNGs occupy about 111 MB.

The 1,760 new alpha masks differ from the former CPU masks by 1,456 pixels in
total (0.0003156% of compared pixels); minimum view-level IoU is 0.999768.
This checks the scene, normalization, camera and depth mapping. The old CPU
RGB values are not used as a reference because their UV and minification
semantics were the issue under audit.

## Object-level metrics

The existing metric definitions were reused without changes. Each table entry
is the mean of 20 object means, where each object mean pools its 11 frozen
unseen views. LPIPS was available; DISTS is unavailable in this environment.

| Condition | FG-PSNR (dB) | FG-LPIPS ↓ | CIEDE2000 ↓ |
|---|---:|---:|---:|
| GT texture sanity reference | 17.640 | 0.0801 | 11.91 |
| No adapter | 6.942 | 0.1488 | 39.98 |
| `native_gfl` | 10.143 | 0.1390 | 27.34 |
| `native_gfh` | 9.993 | 0.1265 | 28.50 |
| `native_gc3` | 10.077 | 0.1342 | 27.47 |
| `lfm_exact` | 9.717 | 0.1296 | 29.54 |
| `layer_lhl` | 9.673 | 0.1311 | 29.53 |
| `layer_llh` | 9.721 | 0.1272 | 29.90 |

The descriptive `layer_llh − native_gfl` contrast changes under the corrected
renderer as follows. Intervals resample objects (10,000 percentile bootstrap
draws, seed 20261005); they are not multiplicity-adjusted.

| Endpoint | Old CPU estimate [95% CI] | GLB-native estimate [95% CI] | GLB-native N=19 excluding the preidentified extreme-UV UID |
|---|---:|---:|---:|
| FG-PSNR | +0.144 [−1.316, +1.653] dB | −0.422 [−1.361, +0.652] dB | −0.487 [−1.469, +0.631] dB |
| FG-LPIPS | −0.0239 [−0.0319, −0.0166] | −0.01175 [−0.01988, −0.00564] | −0.01129 [−0.01975, −0.00507] |
| CIEDE2000 | +1.302 [−3.540, +5.769] | +2.563 [−1.007, +5.893] | +2.970 [−0.689, +6.421] |

Negative LPIPS favors LLH; positive CIEDE2000 favors `native_gfl`. FG-PSNR
has no supported direction. This is an endpoint tradeoff, not a general
quality win. The N=19 row is a fixed sensitivity omitting the UID already
flagged by `UV_ADDRESSING_AUDIT.json` for finite UV magnitudes above 1e6; all
objects remain in the primary N=20 evaluation.

Against `lfm_exact`, LLH FG-PSNR is +0.004 dB [−0.219, +0.270] and FG-LPIPS
is −0.00241 [−0.00429, −0.00090]. These differences are small relative to
the retrospective same-condition development drift: 0.0013/0.0004 of median/
P95 FG-PSNR drift and 0.090/0.021 of median/P95 FG-LPIPS drift. For LLH versus
`native_gfl`, the corresponding absolute ratios are 0.137/0.044 for FG-PSNR
and 0.439/0.104 for FG-LPIPS. This drift distribution is a descriptive scale
reference written after B exposure, not an acceptance threshold or a
pre-unblind safeguard.

## Closure and scope

- **P1-9 renderer validity:** closed for evaluation of the stored N=20/8 GLBs.
  The source bake remains clamp-based; these metrics describe the GLBs as
  actually exported and rendered, not a hypothetical repeat-aware rebake.
- **C12 / 3D claim:** bounded. Report the supported N=20 scope and separate
  endpoints. Do not claim a unique LLH 3D quality winner or infer a seam
  mechanism from the invalid legacy seam analyzer.
- **Four no-UV exclusions:** still prevent strict N=24 coverage. They were
  excluded before bake generation and are not silently replaced or unwrapped.
- **Extreme UV:** included in N=20 under the actual RTX sampler; N=19 is shown
  only as the fixed sensitivity. Very large-coordinate repeat precision may
  differ by graphics implementation.
- **Human fidelity:** remains open. No participant responses were collected;
  the frozen 40-slot study requires at least 36 valid completions and now
  includes the locked `gen_linear` comparator. No recruitment or distribution
  occurred during this audit.
- **Broader readiness:** unchanged. No third backbone, FRESH_CONFIRM_C
  schedule search, source bake rerun, participant contact, or manuscript edit
  was performed. The B practical-scale and narrative safeguards remain
  retrospective because B was already exposed.

Machine analysis: `bake_handoff/GLB_NATIVE_EGL_RENDER_V1/GLB_NATIVE_EGL_ANALYSIS.json`.
Metric files: `UNSEEN_PER_VIEW_METRICS.csv` and `UNSEEN_OBJECT_METRICS.csv`
in the same directory. The analyzer also verifies every render hash and all
160 input GLB hashes.
