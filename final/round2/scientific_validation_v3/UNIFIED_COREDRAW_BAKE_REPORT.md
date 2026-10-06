# UNIFIED_COREDRAW_BAKE_REPORT — Experiment F

One runner namespace, one bake pipeline (geotex/cpu_texture_bake.py in Blender
4.2.4, CPU, original-UV preservation, texture 1024, 11 unseen views), one
frozen input handoff (bake_handoff/BAKE_INPUT_HANDOFF_V3.json, byte-verified
panel SHA256s; same-draw = shared latents/reference per object, latent seed 42).

## Cohort

24 pre-frozen stratified objects; **4 excluded on a pre-generation technical
ground** (mesh without any UV layer — original-UV baking impossible;
excluded_uv_missing.json). Final N = 20. No object was replaced or dropped
for performance.

## Conditions baked

gt (sanity), no_adapter, native GFL/GFH/GC3, LFM-EXACT, LHL, LLH — 8 x 20.

## Unseen-view results (UNSEEN_OBJECT_METRICS.csv, UNSEEN_PAIRED_ANALYSIS.json)

Paired at object level, 10k bootstrap (seed 20261002):

- Method sanity: every adapter condition beats no_adapter by ~+3.6 dB masked
  PSNR on unseen views (CI [2.2, 4.7]); CIEDE2000 better by ~12. The adapter
  provides a large, unambiguous 3D-texturing gain.
- Schedule level is BOUNDED: LLH vs native GFL = +0.14 dB [−1.29, +1.65]
  (n.s.); vs GFH −0.18 (n.s.); vs GC3 −0.10 (n.s.); vs LFM-EXACT +0.08 (n.s.);
  vs LHL +0.06 (n.s.). FG-LPIPS consistently favors LLH over GFL
  (−0.024 [−0.032, −0.017]), GC3, LFM-EXACT, LHL. CIEDE2000 differences
  are within noise.

## UV-seam cross-view consistency (BAKE_SEAM_AUDIT_V3/, SEAM_PAIRED_ANALYSIS.json)

LLH has the LOWEST seam discontinuity of all adapter conditions — paired
deltas (LLH − other, negative = LLH better):
  * vs native GFL: mean dE00 −6.90 [−8.29, −5.47], p90 −17.44 [−21.12, −13.60]
  * vs GC3: −4.63 / −11.92; vs LHL: −1.88 / −4.92; vs LFM-EXACT: −1.42 / −3.85
  * vs GFH: −1.07 / −2.51
  * vs no_adapter: n.s. (flat textures are trivially smooth)
Coverage/inpaint fractions identical by construction (fixed geometry).

## Verdict (claim 9)

**Bounded support.** The method (adapter) clearly improves practical 3D
texturing over no-adapter on unseen views. Schedule-level differences on 3D
metrics are small: LLH is not separable from GFL/GFH/GC3/LFM/LHL on PSNR or
CIEDE2000, but delivers a consistent perceptual (FG-LPIPS) advantage AND
significantly better UV-seam cross-view consistency (lower p90 tail) than
every adapter schedule. No population-level LLH-superiority claim on PSNR is
permitted; perceptual + seam-consistency wording is allowed with the n=20
scope stated.