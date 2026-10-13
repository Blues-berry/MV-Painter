# Fresh C native glTF sampler audit

**Disposition: `SAMPLER_INVENTORY_COMPLETE`; `24-OBJECT_NATIVE_UV_BAKE_GATE=FAIL`.**

## Frozen panel inventory

The inventory covers the original frozen 24-object candidate list and emits one row per mesh primitive (18,730 rows). Every panel asset hash matched the frozen manifest. The table records mesh/primitive indices, material and base-color texture references, texture and sampler indices, wrap/filter values, `TEXCOORD_n`, UV bounds and outside-range fractions, texture dimensions/format, extension fields, alpha mode and base-color factor.

- 9/24 objects have UV vertices outside `[0,1]`. Per-object counts and fractions are in `FRESH_C_GLB_NATIVE_SAMPLER_INVENTORY.csv`.
- Observed effective samplers are `REPEAT` / `REPEAT`, `LINEAR_MIPMAP_LINEAR` minification, and `LINEAR` magnification.
- No `KHR_texture_transform` rows were observed in this frozen panel.
- 27 primitive rows use `BLEND`, across 5 assets. The existing panel renderer accepts only `OPAQUE` and does not implement glTF alpha compositing for these rows.
- The per-object primitive, mesh, material, and texture counts and texture/image metadata are in the inventory and its JSON summary.

## Synthetic sampler checks

`NATIVE_SAMPLER_SYNTHETIC_VALIDATION.json` records **11/11 expected-pixel checks passing** on synthetic geometry: in-range sampling, positive and negative REPEAT, MIRRORED_REPEAT, CLAMP_TO_EDGE, texture borders, high-frequency magnification, mipmapped minification, linear magnification, known UV discontinuity, and base-color factor with OPAQUE alpha. The measurements use analytical/ground-truth pixel references with a tolerance of two 8-bit code values.

This passes the renderer's synthetic sampler subset. It does not validate the missing original-UV-preserving view-to-texture baker, alpha `BLEND`, or a full panel render.

## Gate decision

The existing `call_bake` route invokes `mesh_uv_wrap`/xatlas and changes UV assignment/topology. That is disallowed for this frozen panel. A native-UV baker that preserves the original `TEXCOORD_0`, geometry, and island topology is not present. The 9 objects with out-of-range UVs make wrap behavior material, and 5 objects require unsupported `BLEND` handling. No final 24-object 3D panel was rendered and no output-dependent object exclusions or replacements were made.

Therefore, the new 24-object 3D endpoint is **not available**. The synthetic pass must not be represented as a full 3D gate pass. See `3D_CLAIM_RETIRED.md` for the final claim decision. Historical N=20 GLB-native results retain their separate bounded status: unlit base-color, not PBR, lighting, or seam evidence.
