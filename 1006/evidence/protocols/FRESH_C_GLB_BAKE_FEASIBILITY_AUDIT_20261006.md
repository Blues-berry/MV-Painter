# Fresh C GLB bake feasibility check — 2026-10-06

## Decision

The new 24-object GLB panel has **not** passed a bake or unseen-view technical gate. Do not reuse the current MVPainter production bake entry point unchanged for this evaluation: it rewrites UVs before baking. A new implementation that preserves each source asset's UVs and sampler semantics would need its own frozen protocol and synthetic/real-GLB validation before method outputs.

## Read-only findings

- `MVPainter/mvpainter/bake_pipeline.py::BakePipeline.call_bake` invokes `mesh_uv_wrap(mesh)` before `load_mesh` and projection.
- `MVPainter/mvpainter/uv_warp_utils.py::mesh_uv_wrap` uses `xatlas.parametrize`, then replaces mesh vertices, faces, and `visual.uv`. That changes the source UV parameterization, so outputs would no longer test the frozen GLB's original texture coordinates.
- Nine of the 24 frozen GLBs contain finite vertex UV coordinates outside `[0,1]`. This includes large values. The exported result must preserve the original glTF wrap behavior rather than silently clamp or re-unwrap those coordinates.
- `render_glb_native_egl.py` renders already-stored baked GLBs. Its asymmetric-texture orientation/repeat probe is useful for validating the renderer, but it is not a view-to-UV baker and does not validate a new bake path.
- The 24-object selection is a same-cohort, first-eligible input subset; it is neither stratified nor an independent held-out 3D sample. All current license tags are CC BY, while creator attribution/source-level redistribution terms are still pending.

## Gate required before any new comparison

1. Freeze an implementation that leaves vertex identity, faces, UV values, UV transforms, and the glTF base-color sampler unchanged.
2. On a synthetic known atlas, bake from locked camera images and reproduce the expected atlas under the native glTF sampler, including repeat behavior at negative and above-one UV coordinates.
3. Validate the exact 11 unseen camera transforms against the stored geometry/depth products and retain per-view camera hashes.
4. Run an input-only one-object smoke with every condition using the same bake settings. Verify source-asset hashes, UV equality, glTF re-import, sampler settings, finite outputs, and repeatable rendered pixels before starting the fixed 24-object panel.
5. Freeze all 24 outputs and failures. Do not replace objects after comparative outputs; report only unlit base-color results. Seam analysis requires a separate validated real-glTF boundary protocol.

If an original-UV-preserving implementation cannot pass those gates, stop the new panel and retain only the historical N=20 GLB-native result within its bounded unlit base-color scope. This feasibility check changed no source asset, method output, or submitted manuscript.
