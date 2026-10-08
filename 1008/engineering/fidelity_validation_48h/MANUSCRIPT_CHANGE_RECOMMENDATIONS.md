# Manuscript change recommendations for R1 color/detail claims

This is a handoff for the paper agent. It does not modify the source manuscript, figures, or response letter. The inspected baseline is `/4T/CXY/MV-Painter-1008/1008/manuscript/source_01549/final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`); original `fig4.pdf` and `fig6.pdf` hashes are recorded below. The reviewer asks for broader full-object comparisons including the unmodified pipeline and fixed-scale baseline, and asks authors to distinguish texture variation from fidelity.

## Recommended disposition: decision B

Retain the tested stage-dependent control facts and the separately reported average cohort results, but narrow broad claims that C3/LLH reliably preserves color or texture fidelity. Place the high-texture limitation alongside the average result. Do not present the present color evidence as a repair or as proof that artifacts are physically impossible.

## Source-specific edits

| Source location | Existing claim | Evidence and risk | Recommended edit |
|---|---|---|---|
| § Texture Audit, `final_0903.tex:270`; Fig. 4 caption at line 275 | Higher adapter scale progressively removes color variation and high-frequency detail; conservative scale better preserves local texture. | The original scale comparison can support a local visual observation for the shown objects. The newer saved-RGB cohorts show that visible variation is not identical to GT fidelity, and the selected original Fig. 4 cases show pink/purple mismatch under No Adapter, GFL, and LLH. | Keep the local scale comparison, but say it illustrates the shown crops/objects. Add that local color variation and high-frequency response are not stand-alone fidelity measures. Avoid generalizing from the image to absolute RGB accuracy. |
| § C3, `final_0903.tex:318–322`; Fig. 6 caption at line 327 | C3 is the only promising variant and retains more local color/material texture while keeping strong geometry. | The 300/150-object LLH/GFL results are average effects; Fresh B Q4 reverses color and PSNR direction. Existing R1 views also show color shift. | Preserve the schedule description as the selected tested strategy, but replace “retains” with a bounded phrase such as “shows less flattening in the illustrated regions.” Add an explicit sentence that this does not imply per-object color fidelity. Do not use C3's local appearance as evidence that purple shifts are solved. |
| § Texture Audit and Fig. 5, `final_0903.tex:279–288` | Texture loss prevalence and proxy ratios are used to infer degradation. | The metric audit confirms that raw texture magnitude is not fidelity. The locked RGB endpoint uses GT-relative Laplacian error; that error improves for LLH on all Fresh C/B objects while high-texture Q4 CIEDE/PSNR worsens. Different endpoints answer different questions. | Keep “texture degradation” only where the endpoint measures a GT-relative error or the claim is visibly scoped. Call RGB std, gradient, and Laplacian variance “texture-response proxies,” and state that higher response can also be artifact. Report target-relative error where available. |
| § Limitations, `final_0903.tex:532–536` | C3 alleviates texture degradation; schedule is stable across tested regimes. | The held-out Fresh B Q4 result identifies a specific complexity boundary; color root cause remains unresolved and the saved inference runtime for Fresh C/B is not fully pinned in run manifests. | Add a limitation: average improvements do not guarantee color/detail fidelity for texture-rich objects; the mechanism behind visible pre-bake RGB shifts is unresolved; conditioning provides one appearance view plus a global embedding, not six per-view color targets. Qualify schedule robustness to the studied pipeline and cohorts. |
| Conclusion, `final_0903.tex:544–550` | TCAS balances shape-texture trade-off and is broadly useful. | The result remains useful but has object-dependent color/detail limits, and the residual-gating prototype is negative. | Keep the training-free schedule contribution, but state that evidence supports cohort-average improvement under the tested pipeline rather than universal color fidelity; mention the high-texture failure boundary and unresolved generation artifact. Do not recast the negative gate as a new contribution. |

## Suggested insertion for the texture-fidelity discussion

> The reported texture statistics measure response magnitude or deviation from the rendered target and should not be interpreted as fidelity in isolation. In a separate saved-RGB analysis, LLH improved the cohort-average CIEDE2000, FG-PSNR, and FG-LPIPS relative to GFL on Fresh C (300 objects) and the disjoint Fresh B holdout (150 objects). This average did not hold uniformly: in Fresh B's GT-defined highest-texture quartile (38 objects), LLH increased CIEDE2000 by 3.624 and reduced FG-PSNR by 0.770 dB relative to GFL. Therefore, the schedule is a useful inference-time control for the evaluated cohort, with an observed high-texture fidelity limitation; it is not a per-object color correction.

Use the full interval and method details in the response or supplement, or add a compact table. Do not combine Fresh C, Fresh B, and diagnostic-26 into one estimate.

## Figure plan

1. **Main Fig. 4 and Fig. 6:** retain the original figures unless the paper agent has independent reason to redraw them. This task did not edit or replace them. Revise captions so the examples are explicitly local illustrations and do not imply absolute color accuracy.
2. **Supplementary qualitative evidence:** use the new Fresh B GT/GFL/LLH gallery for fixed GT-only Q1/Q3/Q4 examples, and the existing 10-page `../color_failure/final_closure/COLOR_FAILURE_CASEBOOK.pdf` for the full diagnostic-case comparisons including No Adapter. Label the first gallery as three illustrative objects selected by a GT-only rule and the casebook as a failure-audit set, not a random sample.
3. **Broad held-out evidence:** cite the full 150-object paired results and the exact RGB/input hash audit. Do not imply three gallery objects visually represent the entire holdout. If space allows, provide a supplementary per-object montage/index generated from the same frozen RGB source, without cherry-picking by output.
4. Baked mesh views, unseen-view quality, seams, and cross-view consistency are outside this RGB audit. Cite separate bake/render evidence only if its object identity, view protocol, and hashes are linked; this packet cannot answer those points by itself.

## Identity of inspected original paper files

| File | SHA-256 |
|---|---|
| `final_0903.tex` | `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` |
| `fig4.pdf` | `0e7def3143698b3ba322e13f869f810717abfc36cf0dc608a15e4820f6b44620` |
| `fig6.pdf` | `585af2af647e9f169cb98320fb5779aaba158b3493ea054bea2ff8eef675546c` |
| `01549_submitted_manuscript_0907.pdf` | `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da` |
