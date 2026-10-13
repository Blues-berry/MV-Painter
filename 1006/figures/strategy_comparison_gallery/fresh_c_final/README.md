# Fresh C six-strategy comparison atlas

The contact sheet contains 20 object groups, five selected for each frozen comparison: C3−GFL, LLH−C3, LLH−generic-linear, and C3−generic-linear. Every group uses a shared reference, the same six target views, and all six strategies: no adapter, GFL, GFH, C3, LLH, and generic linear. Per-image provenance and hashes are in `gallery_manifest.json` and `gallery_asset_sha256.csv`.

**Caption for later manuscript use:** “Examples were selected from predefined positions in the complete object-level ranking after the cohort-level analysis and were not used to define the statistical result.”

Selection positions follow the frozen per-contrast/per-endpoint ranking rule. They expose favorable, near-median, unfavorable, and endpoint-tradeoff examples; no post-viewing manual reranking or cross-metric composite score was used. The complete six-method index covers all 300 frozen UIDs and seven metrics; the paired comparison files cover each registered contrast. The contact sheet is a navigation aid, not an inferential result.

No individual object has a p-value or significance label. The images were not used to select human-study objects. Cohort-level effects, intervals, favorable-object fractions, and the registered Holm families are reported separately in `cohort_contrast_summary.csv`, `cohort_contrast_summary_ranked_within_family.csv`, and `cohort_contrast_forest.png`.

One stratum in the stored selection manifest records a fallback to the next pre-ranked UID when the first UID for that position was already used in an earlier panel; the selection remained within the predefined ranked order and unique-UID rule. See `gallery_manifest.json` for the exact selected UID and stratum per group.

The gallery demonstrates image-space outputs only. It is not evidence of human fidelity, a valid new GLB bake, full PBR quality, or seam improvement. Distribution remains subject to the 1006 asset-rights gate.
