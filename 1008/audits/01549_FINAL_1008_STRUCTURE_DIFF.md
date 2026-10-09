# 01549 → 1008 final structure and evidence diff

**Status:** current author-review revision, compiled 2026-10-09. This report describes the 13-page manuscript and 11-page supplement now on the private revision branch. The older 9-page candidate and 11-page manuscript package are preserved historical candidates and do not govern this report.

## Authenticated baseline and current output

- 01549 is the post-first-round version submitted on 2026-09-07; the current R1/R2/R3 packet is its second-round review.
- Official 01549 TeX SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`; it matches the `final_0903.tex` member of the official submission archive.
- Final active `manuscript_1008.tex` SHA-256: `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`.
- The authenticated baseline remains separately available at `manuscript/revision_01549_restored/final_0903.tex`; the active revision is `manuscript_1008.tex` in that same project directory.
- Main output: 13 pages, six figures, five tables. Supplement: 11 pages. Marked-up manuscript: 19 pages. Fresh C Figures 4–5 occupy pp. 11–12; the historical 24-object development plot (Fig. 6) occupies p. 13.
- The complete original-to-current paragraph, figure, and table mapping with TeX line numbers, final PDF pages, hashes, and disposition reasons is `ORIGINAL_CONTENT_DISPOSITION.csv`. Figure-specific review and asset hashes are in `01549_FIGURE_PRESERVATION_REVIEW.md` and `RESTORED_FIGURE_ASSET_MANIFEST.csv`.

## Section and experiment continuity

| 01549 material | 1008 final treatment | Reason / boundary |
|---|---|---|
| Abstract, Introduction, Related Work | Locally rewritten; the TCAS problem and task context remain. | Replace old pooled headline and unsupported broad fidelity/generalization language; add the direct SSI comparison and current scope. |
| Geometry-residual pipeline, TCAS equation, three stages, C3 profile | Retained, with requested scale, applied scale, and residual magnitude distinguished. | CAI selector/proposition/proof and independent optimality claim are removed; the criticism is specific to CAI. |
| GeoTex implementation and optional FAC branch | The original Fig. 1 and FAC pipeline context remain; the negative FAC controlled re-examination is reported in the main text and Supplement S11. | FAC is historical first-round evidence, not a new 1008 run. The 1,200-versus-1,706 training-list mismatch and missing run-bound seed/output manifest are disclosed. |
| Fixed-scale 50-object × 13-scale sweep and 24-object / 17-variant C3 development record | Original Table 1, Table 2, Figures 2–3, and the development plot (final Fig. 6) remain. | Labeled historical/development evidence; no unsupported re-ranking, population inference, or unique-optimum claim. |
| 26-object texture proxy audit and original Fig. 5 ratio chart | The figure and unsupported prevalence/fidelity inference are removed; variation metrics remain described only as diagnostics. | Selection trace, row-level inputs, and definitions cannot support the old prevalence or fidelity conclusion. |
| Original qualitative Fig. 4 and Fig. 6 questions | Updated with selected, matched Fresh C full-object image-space comparisons in final Figures 4–5. | Includes an adverse case and Generic Linear counterexample; selected panels do not estimate prevalence or validate baking, seams, PBR, or unseen-view quality. |
| Original pooled Table 4 and texture / CLIP-IQA tables | Fresh C Tables 3–4 replace the old pooled headline; unsupported texture/CLIP-IQA claims are removed. | Preserve the registered C3−GFL result and GFH/Generic Linear counter-results; no equivalence or texture-fidelity inference. |
| Original Table 8 three-condition preference study | Retained as final Table 5, a separately scoped first-round subjective-choice result. | Not evidence of Fresh C, texture fidelity, or 3D quality; no participant-level records are included. |
| Original adapter-dependence and strict-276 Table 9 analysis | Bounded summaries remain in the main text; Table 9 is transcribed in Supplement S9; additional analyses remain in the supplement. | Different adapter/run identities and interface limits are not represented as matched cross-backbone validation. |
| Limitations and Conclusion | Locally rewritten, with unresolved gaps stated directly. | R1.1 bake/seam, R1.5 FAC provenance, R2.1 editorial novelty, and R2.3 matched cross-backbone validation remain bounded/open. |

## Figure and table totals

- **Figures:** 01549 had seven. Final 1008 has six. Original Figures 1–3 are retained (Fig. 1 byte-identical; Figures 2–3 hash-identical). Original Figure 4 is replaced by Fresh C context-plus-shared-ROI panels; original Figure 5 proxy chart is withdrawn; the original Figure 6 comparison question is answered in final Fig. 5 with Fresh C fixed-scale and Generic Linear panels; original Figure 7 becomes final Figure 6 with only local label/caption corrections.
- **Tables:** 01549 had nine. Final 1008 has five main tables. Original Tables 1–2 remain as historical diagnostics; original Table 3 moves to Supplement S10; original Table 4 is replaced by Fresh C Tables 3–4; original Tables 5–7 are removed with their unsupported interpretations; original Table 8 is retained as final Table 5; original Table 9 moves to Supplement S9 with its adapter/run boundary.

## Page-count change

The authenticated 01549 main manuscript is 15 pages; final 1008 is 13 pages. The net two-page reduction reflects removal of unsupported proxy/prevalence, CLIP-IQA, and texture-retention presentations and replacement of the old pooled comparison with Fresh C tables. Relative to the older 11-page main-text candidate, the restored context-plus-ROI Fresh C Figures 4–5 each use a full page so texture detail is readable at normal paper size. The fixed-scale scan, C3 development evidence, first-round preference result, and FAC negative re-examination remain. The supplement carries the complete six-view/seven-condition panels and supporting analyses. A retrospective Core-7 strict-276 summary appears in S5, pp. 6–7; it reports opposing Full-view and foreground C3−GFH PSNR directions and explicitly states that the seven conditions do not establish common runner/input identity. Fresh C remains the primary R1.2 comparison. The 9-page historical candidate is not the structure used for this revision.

No blanket “identity preserved” claim is inferred from the paper title or a successful build. The source hash, active source hash, rendered page counts, and every original item’s current disposition are provided above and in the linked ledgers.
