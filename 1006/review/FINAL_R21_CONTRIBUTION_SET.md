# R2.1 final contribution set

**Status: two bounded empirical contributions retained in the revised manuscript; `R2.1 = OPEN / VENUE RISK`.** This contribution set does not claim that the journal's novelty threshold is settled. The revised manuscript acknowledges prior work on scheduled injection and timestep-dependent guidance, including [Scheduled Style Injection](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf) and [Dynamic Classifier-Free Diffusion Guidance via Online Feedback](https://arxiv.org/abs/2509.16131). It makes no novelty claim for layer-by-timestep scheduling itself.

## Retained contribution 1 — implementation-aware execution semantics

Characterize how requested scales pass through the existing MVPainter residual-adapter wrapper's layer rules and native caps, and report the resulting applied correction magnitudes separately from image-space outcomes. The Fresh C accounting records 750 strategy/group/timestep rows over five strategies, three depth groups, and 50 steps. For example, GFL requests 1.25 at each layer group, but the shallow cap applies 0.8; its shallow cap is active for all recorded wrappers. The correction norm also depends on the residual being scaled.

This is a bounded account of one implementation. It does not introduce a scale operator, establish equal-realized-dose comparisons, or show that correction magnitude causes a quality change.

Evidence and manuscript mapping:

- [Fresh C execution-semantics report](../evidence/audits/FRESH_C_EXECUTION_SEMANTICS_FINAL_REPORT.md)
- [Execution-semantics summary](../evidence/audits/FRESH_C_EXECUTION_SEMANTICS_FINAL_REPORT.md) and [representative logged rows](../evidence/audits/FRESH_C_EXECUTION_SEMANTICS_REPRESENTATIVE.csv)
- [Numerical authority entries](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv), especially the `EXEC_*` rows
- Revised manuscript placement: method semantics on p. 3, lines 151–158; execution-accounting results and Fig. 1 on p. 4, lines 228–246 (figure p. 5).

## Retained contribution 2 — object- and endpoint-dependent Fresh C evidence

Report the frozen revision-era Fresh C cohort as a paired empirical comparison of the six tested strategies, with object-level uncertainty and endpoint-specific conclusions. Its registered primary C3−GFL foreground-PSNR difference is +0.522 dB (95% object-bootstrap CI [+0.404, +0.641]); 68.7% of objects favor C3 on this endpoint. This is a Fresh C result, not a replication of the original registration or historical +0.96 dB estimate.

The separate post-hoc Fresh C addendum makes the comparator and endpoint limits visible: C3−generic-linear FG-PSNR is −0.593 dB [−0.837, −0.351], while C3−generic-linear FG-LPIPS is +0.01351 [+0.01160, +0.01549] (both directions favor generic linear). These results are not pooled with the registered primary contrast. They support endpoint- and object-dependent characterization, not a universal winner or a typical-object claim.

Evidence and manuscript mapping:

- [Fresh C numerical authority](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv), including `FRESHC_C3_GFL_*` and `FRESHC_ADD_C3_linear_*`
- [Fresh C C3−GFH post-hoc audit](R1_4_FRESHC_C3_minus_GFH_posthoc_audit_20261007.md); this remains explicitly post hoc and separate from the registered primary family.
- Revised manuscript placement: Fresh C cohort and registration caveat on p. 3, lines 195–212; primary result on p. 4, lines 248–255; generic-linear and C3−GFH comparisons on p. 4, lines 256–278. Full endpoint tables are in Supplementary Sections S2–S5.

## Compression test

| Required condition | Contribution 1 | Contribution 2 |
|---|---|---|
| 1. Prior work does not fully cover the bounded claim | Pass: the claim is measured execution semantics for this wrapper, not a scheduling primitive. | Pass: the exact frozen Fresh C cohort and its paired endpoint results are specific to this tested intervention. |
| 2. Direct evidence exists | Pass: logged scale, cap, and residual-accounting records. | Pass: paired object-level Fresh C authority rows and post-hoc addendum. |
| 3. Maps to a main-paper experiment | Pass: Fresh C strategy execution. | Pass: Fresh C registered primary comparison and separately labeled addendum. |
| 4. Independent of human results | Pass. | Pass. |
| 5. Independent of retired 3D claims | Pass. | Pass. |
| 6. Independent of seam claims | Pass. | Pass. |
| 7. Independent of E6 | Pass. | Pass. |
| 8. Independent of CAI optimality | Pass. | Pass. |
| 9. Independent of a universal Layer×Window mechanism | Pass: no mechanism claim is made. | Pass: cohort outcomes are reported without a universal mechanism claim. |
| 10. Independent of historical statistics with missing provenance | Pass: uses Fresh C execution records. | Pass: uses Fresh C, not strict-276 or other historical estimates. |

## Claims not retained as separate contributions

- **A new layer×timestep control primitive, first method, or universal schedule:** rejected by the prior-work comparison.
- **A separate boundary/generalization contribution:** not elevated to a core contribution. MV-Adapter and MVDiffusion remain interface-specific boundary evidence and limitations; they do not establish architecture causality or universal transfer.
- **Texture-complexity response as a general predictor:** not retained as a contribution; any report remains bounded to the tested regime.
- **CAI schedule selection/optimality, FAC learned extension, human preference, retired 3D/seam evidence, E6, or historical strict-276 estimates:** not used to support either retained item.

The revised manuscript presents these two items as a compact empirical study of one existing adapter implementation and one frozen image-space cohort. Broader practical or venue significance remains open for editorial judgment.
