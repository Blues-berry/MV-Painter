# Abstract review and update — V4

## Version check

The authoritative target was the latest PR #1 head `1b46e166` on `codex/cg-final-v4-20261014`, fast-forwarded from `84d4b0da`. The official source is `FINAL_V4_MANUSCRIPT.tex`; `FINAL_V4_MANUSCRIPT_EDITORIAL_DRAFT.tex` and `EDITORIAL_REWRITE_REVIEW_ONLY.tex` are separate review candidates and remain untouched. Only the official abstract was revised in this pass.

## Assessment of the two supplied abstracts

Both proposed summaries correctly organize the work around control semantics, stronger comparators, matched-applied-budget allocation, baked appearance and transfer limits. The more quantitative draft is stronger for this paper because it gives C3's +0.522 dB foreground-PSNR change and the specified matched-budget estimate/interval. Its statements that Fixed High and Generic Linear have better means on all four image endpoints, that GeoTex Bake10 gains 0.00265 LPIPS, and that the separate GSO20 protocol does not detect the same benefit agree with current Tables 2, 5 and 7. “Does not detect” is retained instead of treating non-detection as proof of no effect.

The supplied drafts predate the newest V4 evidence reintegration and omit the S8 full-v29 boundary now present in the official main text. The abstract therefore adds one short, explicitly limited statement: a separate matched-input comparison under a recorded non-default protocol places the new geometry checkpoint below full v29 in FG-PSNR and FG-LPIPS, but does not isolate schedule effects. This is not described as a fair TCAS-only ablation or an official default-CLI comparison. The retrospective S7 texture-complexity association is omitted from the abstract because it is supporting heterogeneity evidence, not a central confirmation.

## Final abstract

Geometry-conditioned multi-view diffusion generates images that are baked onto 3D meshes, yet better image scores need not yield better textured assets. We study Timestep-Conditioned Adapter Scaling (TCAS) on an existing GeoTex residual interface, distinguishing requested scales, native-cap-adjusted applied scales, and state-dependent corrections. On 300 held-out objects, historical C3 improves foreground PSNR over Fixed Low by 0.522 dB but also increases the applied budget; Fixed High and Generic Linear have better means on all four image endpoints. At matched per-group applied-scale sums, the specified Middle-high minus mean(Early-high, Late-high) contrast is −0.0339 dB (95% interval [−0.1172,+0.0514]), with no detected middle-window advantage. Native-UV baking on ten compatible GeoTex objects finds a small Late-high unseen-view LPIPS reduction (−0.00265) alongside substantial reference-appearance error; a separate twenty-object GSO protocol does not detect the same benefit. Native-interface tests do not establish a transferable middle-window gain. A separate matched-input comparison under a recorded non-default protocol finds that the new geometry checkpoint remains below full v29 in FG-PSNR and FG-LPIPS, but does not isolate schedule effects. These findings support task-specific evaluation of control allocation and textured assets, not a universally preferred schedule or faithful material reproduction.

No experiment, endpoint, cohort, or inferential result was added or recalculated. The rebuilt abstract contains 189 words; the manuscript remains 14 pages.
