# 01549 → 1008 change log

## Version basis

`CAG-S-26-01549` is the revised manuscript submitted on 2026-09-07 after first-round revisions. The current R1/R2/R3 packet is the second-round review; 1008 is the response to that round. The working manuscript was restored from the authenticated `final/submission_new_0907/latex.zip` member `final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`). The previous candidate in `revision_1008/` remains untouched.

The delivered main manuscript is 11 pages; the Supplement is 10 pages; the marked-up comparison against 01549 is 20 pages.

## Section-level changes

| Manuscript area | 01549 baseline | 1008 action | Reason and scope |
|---|---|---|---|
| Abstract and Introduction | Geometry-conditioned multi-view texturing, TCAS motivation, and broader pooled texture claims | Retains the task and TCAS contribution; reports bounded Fresh C evidence and GFH/Generic Linear counter-results; narrows image-quality and transfer claims | Fresh C is an internally matched 300-object comparison, not a numerical reproduction of the historical Table 4 estimate |
| Related Work | 3D texturing, adapter, and diffusion-scheduling background | Retains first-round literature changes and adds direct SSI comparison | Frames novelty as task- and interface-specific; does not claim a general scheduling primitive |
| Method and pipeline | Geometry-adapter residual path, TCAS equation, three stages, C3, CAI rationale, and optional FAC branch | Preserves the base pipeline, TCAS equation, three-stage profile, C3, and original Fig. 1; removes only CAI's independent derivation/proof/selector/optimality claim; retains the reported negative FAC re-examination as an auxiliary historical result | R2.2 targets CAI's post-hoc derivation, not TCAS. FAC stays clearly distinguished from the training-free TCAS method and includes its archival limits |
| Fixed-scale diagnostics | 13-scale scan, Tables 1–2 and Figures 2–3 | Retains the fixed-scale question and original diagnostic figures/tables with historical-evidence labels | The submitted values are not independently recomputed from row-level outputs; they remain useful development context, not current population inference |
| Full-object appearance and texture audit | Crop examples and texture-variation/fidelity interpretations | Adds outcome-selected, full-object Fresh C panels across reference, No Adapter, GFL, GFH, C3, LLH, and Generic Linear; removes untraceable pooled variation/fidelity claims | Panels include favorable and adverse cases, do not estimate frequency, and are not baked-mesh/PBR evaluations |
| C3 development | 24-object, 17-variant probe and C3 figure; CAI selection argument | Retains the development table/figure and labels them as historical probe evidence; withdraws unique-optimum and independent-selector claims | Candidate-level rows and selection-time provenance remain incomplete |
| Main quantitative comparison | Historical pooled Table 4 headline (+0.96 dB) | Uses Fresh C Tables 3–4 for the current matched comparison and preserves the Generic Linear, GFH, and LLH endpoint counter-results | Fresh C conditions share one frozen checkpoint, runner source, per-object seed policy, inputs, target views, metrics, and actual recorded cap semantics. No old Table 4 checkpoint-hash gate is imposed; the historical v1/v2 distinction and lack of numerical reproduction are disclosed |
| Subjective preference | First-round 3AFC study, 30 objects and 24 participants | Retains the aggregate counts and two-level participant/object-bootstrap overall-preference result as a separate historical subsection | Preserves acknowledged first-round work while stating that subjective choice is not texture fidelity, Fresh C evidence, or 3D quality |
| FAC | First-round controlled negative re-examination | Retains the seven-configuration dose-response report and untrained control in the main text/Supplement S11 | It is reported as prior evidence, not a new 1008 run. The recovered configuration/list mismatch (1,200 vs. reported 1,706), missing run-bound seed/output manifest, and no-public-release status are disclosed |
| Adapter dependence and schedule transfer | Section 4.7, Table 9, and probe-disjoint 276-object schedule results using a separate v2 adapter | Retains these results in Supplement S9 and related supplementary discussion, explicitly separate from Fresh C and the v1 main tables | Preserves completed first-round analyses recognized in round two while maintaining the v1/v2 and cohort distinctions |
| Cross-backbone and limitations | Within-family adapter-dependent behavior | Reports the actual MV-Adapter and MVDiffusion probes, including sample counts/statistics and interface-specific boundaries | These probes do not share a matched conditioning path/runner and do not establish cross-backbone generalization |
| Conclusion | Broad texture-preservation and practical-quality language | Retains task-specific TCAS while stating unresolved novelty, fidelity, baking/seam, and cross-backbone boundaries | Does not claim a universal schedule or an overall winner across endpoints |

## Figure and table disposition

- Figure 1 is the original 01549 diagram. Its caption makes the FAC branch an auxiliary, previously reported extension and distinguishes pipeline context from validated Fresh C outcomes.
- Figures 2–3 retain the original fixed-scale diagnostics and their historical status.
- Original Figures 4–5 are replaced by full-object Fresh C 2D examples because the old crops/metric support do not establish broad fidelity. Their comparison purpose is preserved, including adverse cases.
- The original C3-versus-fixed-scale research question remains represented by matched Fresh C comparisons. The original 24-object, 17-variant development plot is retained as the final C3-development figure with corrected probe-only labels.
- Original fixed-scale and C3-development tables remain in the main text. The old pooled Table 4 is replaced by Fresh C tables. Unsupported pooled texture-variation/retention and CLIP-IQA results are not used as current evidence. The first-round 3AFC preference counts are retained separately. The historical 276-object schedule-transfer table remains in Supplement S9, and FAC dose response is retained in Supplement S11.

## Round-specific response map

- **R1.1:** matched full-object 2D comparisons added; bake/seam/PBR and portal-video limits are explicit.
- **R1.2:** answered with author-specified paired Fresh C protocol; C3−GFL FG-PSNR is +0.522352 dB (95% CI [+0.404160,+0.640669]); historical Table 4 checkpoint identity is not an added gate.
- **R1.3:** texture variation is separated from fidelity; the earlier 3AFC result remains subjective preference only.
- **R1.4:** paired intervals and the Edge-SSIM trade-off are reported; no equivalence/non-inferiority claim is made.
- **R1.5:** first-round FAC negative results remain, with the archival reproducibility gap disclosed; no code-release claim is made.
- **R2.1:** TCAS is retained and compared with SSI; novelty sufficiency remains an editorial judgment.
- **R2.2:** CAI's invalid derivation/optimality claims are removed without removing TCAS or C3.
- **R2.3:** actual interface probes and their limits are reported; cross-backbone generalization remains unestablished.
- **R3:** positive assessment acknowledged; no new technical change or experiment is attributed to this reviewer.

The manuscript and response use the official 0907 submission package as the first-round history. They do not describe 01549 as an initial submission or conflate first- and second-round requirements.
