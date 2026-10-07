# Fresh C reviewer visual candidate pool

This pool indexes all 300 frozen Fresh C objects and their six existing methods: no adapter, GFL, GFH, C3, LLH, and generic linear. The index records the six fixed reference views, all six existing prediction images and hashes, seven separate metric endpoints, endpoint-specific paired deltas and ranks, and the per-object rights disposition.

Only the 20 assets marked `FIGURE_ONLY` with attribution are copied into `panels/`. The other 280 objects remain in the full machine index, but their images are not copied into this candidate package. Row-level attributions are in `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`.

The 20 panels are exact copies of the already-generated Fresh C gallery panels. They retain the fixed views `0, 15, 12, 16, 13, 14`, the shared reference and six-method layout, and the source crop/normalization from the original gallery build. No diffusion was run; no prompt, seed, reference, crop, color, texture, or individual method image was changed in this step.

Group labels are qualitative curation metadata. The success group refers only to a clear visual contrast with the no-adapter condition. It does not establish reference fidelity or a winner among adapter methods. Trade-off selection uses the named Full-PSNR and Edge-SSIM endpoints separately; no cross-endpoint score is formed. No `REPEATED_PATTERN` tag was assigned because the current panels did not support a confident object-level label separate from the source geometry.

Qualitative examples illustrate selected behaviors. Quantitative conclusions remain based on the complete frozen cohort and endpoint-specific tables, intervals, medians, and favorable-object fractions.
