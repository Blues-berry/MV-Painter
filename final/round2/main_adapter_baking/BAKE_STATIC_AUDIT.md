# Bake Input Static Audit

Date: 2026-09-29  
Input: `BAKE_INPUT_HANDOFF.json`  
Scope: read-only D3 handoff synchronization; no bake output was produced.

## Result

**PASS for frozen-input integrity; BAKE NOT RUN.** The handoff contains 12 objects and the referenced input bundle is complete under the checks below.

## Verified invariants

- 12 unique object IDs and 12 unique exact GLB paths.
- Every exact GLB exists and matches the handoff SHA-256.
- Every object has 17 camera-pose files, 17 GT RGBA images, and 17 foreground-mask images.
- Camera files load as serialized pose dictionaries.
- GT RGBA and foreground-mask images are 512×512.
- Each of `no_adapter`, `fixed_low`, `fixed_high`, and `c3` has a frozen 512×768 panel plus six 256×256 target-view PNGs.
- Every frozen generated panel and target-view PNG matches its handoff SHA-256.
- Target view order is `unique6 = [0, 15, 12, 16, 13, 14]`; raw views 1–11 are reserved as unseen views.
- All normalization metadata paths exist, and every referenced path in the checked handoff bundle exists.
- The 12-object handoff cohort has zero UID overlap with `train_objects_full_1118.txt`.

## Constraints that the implementation must preserve

- Use the original UVs; do not re-unwrap or mutate the exact GLBs.
- Use camera-depth/z-buffer visibility.
- Use one recorded blending rule shared by GT and all four generated conditions.
- Report uncovered texels and any inpainting explicitly; never silently fill them.
- Treat unseen evaluation as raw views not present in the six-view generated input. No generated unseen PNG is assumed.
- Keep the handoff's `do_not_modify` files and frozen inputs byte-preserving.

## CPU feasibility boundary

Blender 4.2.4 starts successfully in background mode on CPU. The existing differentiable baking path in `MVPainter/mvpainter/differentiable_renderer/mesh_render.py` defaults to the custom rasterizer (`raster_mode='cr'`) and allocates tensors on `device='cuda'`; it is therefore not a CPU fallback. A future CPU implementation must supply an independent z-buffer/UV rasterization path, preserve the handed-off UVs and camera convention, and emit coverage/trust maps before any optional inpainting.

This audit does not claim that a CPU bake is implemented or numerically validated.
