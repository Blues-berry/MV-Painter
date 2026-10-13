# 01549 evidence-to-narrative decision map

Date: 2026-10-06. State: pre-freeze; submitted manuscript preserved.

This map treats `final/submission_new_0907/Manuscript 0907.pdf` as the 01549
submission baseline (SHA256
`fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da`). It is
a reviewer-facing change specification, not a rewritten manuscript. No
submission source or PDF was edited.

The current claim-level authority is the hash-validated
`CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`. It keeps historical and retrospective
results visible without allowing them to replace the current claim-specific
cohort. Ledger validation does not change the evidence-freeze verdict.

## Evidence-led claim decisions

| Submitted claim | Evidence now available | Decision for a post-freeze revision |
|---|---|---|
| Layer-by-timestep adapter allocation is a new general diffusion control space. | *Scheduled Style Injection* studies training-free schedules over decoder layers and denoising steps, including geometric ControlNet schedules, and is published in the [CVPR 2026 NTIRE proceedings](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf). Its task and injection path differ, but it is close prior art. | Withdraw “first,” general novelty, and broad control-space language. Compare directly with SSI and distinguish only the tested MVPainter residual path, cap/dose semantics, object heterogeneity and baked-texture endpoints. Novelty adequacy remains open. |
| A stage-utility/CAI argument derives an optimal C3 schedule. | The schedule was selected among tested variants; the current evidence does not prospectively validate CAI. A3b's adjusted interaction has no common dose support (0/2250), so its regression cannot identify an equal-dose mechanism. | Keep CAI descriptive or remove it from the core. Describe C3/LLH as a tested operating point, not a derived optimum. |
| A low-high-low schedule establishes a general temporal conflict and the value of timing itself. | Fresh B: LLH−LFM-exact is +0.325 dB PSNR [0.209, 0.446], −0.00460 LPIPS [−0.00563, −0.00357], both within the registered practical bounds. LLH−HLL has a positive mean PSNR difference but only 45.3% favorable objects and a negative PSNR median. LLH−LLL changes overall strength as well as placement. HLL−LLL is exploratory: PSNR uncertain; LPIPS favors LLL. | Report the four contrasts separately, distinguish registered from exploratory, and avoid a four-direction temporal law. Describe only the tested schedule contrasts and their object heterogeneity. |
| LLH is the unique or broadly superior schedule. | E1 passed a 576-row integrity audit. On its fixed 48-object subset averaged over seeds 42–44, LPIPS favors LLH over GFL, GC3, and LFM-exact after the planned Holm correction, but not over GFH or the generic linear schedule. PSNR is mixed. For LLH−LFM-exact, the mean effect is only 0.58× the median within-object seed range for PSNR and 0.68× for LPIPS; these ratios are descriptive and do not test a seed-population effect. The estimates use reused objects, not a new cohort. | Do not select one winner. Use comparator-specific mean effects, intervals, favorable-object fractions, seed means, and effect-to-seed-range context. E1 is realization sensitivity, not independent-object confirmation. |
| The interaction proves layer-by-time allocation is a strong, dose-independent mechanism. | A2 is a corrected discovery result. Fresh B/A3b interaction magnitudes are modest (LPIPS interaction RMSE 0.000342; PSNR 0.0205 dB). The dose-adjusted model has zero common-support rows. E2 passed its 576-row integrity gate. Increasing deep+middle from 1.25 to 1.675 improved LPIPS by −0.00666 (95% CI [−0.00887, −0.00452], 81.2% favorable objects; Holm p=0.00030) and PSNR by +0.544 dB ([+0.329, +0.763], 72.9%; p=0.00030). Raising shallow from 0.50 to 0.80 worsened LPIPS (+0.00584, [+0.00251, +0.00927], p=0.00160) but did not resolve PSNR (−0.116 dB, [−0.655, +0.399], p=0.668). The factor interaction was negligible for LPIPS (p=0.719) and positive for PSNR (+0.365 dB, [+0.243, +0.486], p=0.00030). E2 moves deep and middle together, holds time fixed, and uses the same selected 48 B objects over three fixed seeds. | Treat E2 as a bounded static layer-scale sensitivity, not an equal-dose or layer×time mechanism test. The PSNR interaction is metric-specific and its mean magnitude is about 0.85× the median within-object seed range; its LPIPS counterpart is about 0.03×. Seed-42 F01 is reused from capped `native_gfl` (requested shallow 1.25, applied 0.80); seeds 43/44 request and apply 0.80. Cite the alias erratum and describe F01 by effective scale. |
| 0.96 dB is an independently confirmed held-out gain. | The submitted number comes from the old pooled evaluation and is not a fresh confirmation. The strict-276 GC3−GFL retrospective re-evaluation is +1.207771 dB FG-PSNR [1.116967, 1.294989], 259/276; this pair was not a registered primary Core-7 contrast and has incomplete legacy input-hash/common-runner provenance. FRESH_CONFIRM_B has 150 disjoint objects but its registered contrasts test LLH, not C3. | Withdraw the old number as independent confirmation. If reporting strict-276, label it a retrospective same-cohort supplement; do not substitute LLH for C3. |
| The image evidence establishes general texture fidelity and superior 3D quality. | The submitted paper reports an earlier 24-participant, 30-object 3AFC study for s=1.25/s=2.50/C3. The newly frozen LLH comparison package has 0 responses and requires at least 36 valid completions. The stored GLB audit covers 20 UV-supported objects and base-color renders only; endpoint results are mixed. Four no-UV objects are excluded, and the old seam metric is not reproducible. | Keep appearance fidelity separate from texture variation. Do not transfer the old preference result to LLH, claim unseen-view or full-PBR fidelity, or generalize the N=20 stored base-color endpoints to all 24 objects. |
| Main-backbone findings transfer or establish architecture dependence. | MV-Adapter has 98/99 evaluable objects and no corrected global interaction in its tested range. MVDiffusion adds a separate 75-object mixed/negative result using CPBlock output interpolation. Both interfaces and interventions differ; a significant result in one and a nonsignificant result in another is not a between-backbone test. | State only that transfer was not established across the tested interfaces. Report each backbone within its own cohort; do not pool scores or claim causal architecture dependence or zero interaction. |
| FAC supports a learned extension or can be omitted as an unhelpful result. | Current V3 records FAC as a negative extension with partial reproduction and packaging closure still outstanding. | Retain the negative result and close its artifact lineage during final reconstruction; do not omit it because it fails to improve the schedule. |

## Provisional post-freeze narrative

The defensible center is a bounded empirical characterization of how fixed,
inference-time geometric-residual scale interventions in the MVPainter pipeline
change paired structure and appearance metrics, with explicit requested versus
effective scale semantics and stated limits. The paper can present temporal
contrasts as one part of that characterization, alongside object heterogeneity,
realization sensitivity, static scale sensitivity, and the bounded 3D endpoint.
It cannot present a universal temporal law, a unique winner, an equal-dose
mechanism, or broad architecture transfer. This narrower study may still be
judged insufficiently novel for the venue; claim reduction cannot resolve that
reviewer concern by itself.

After evidence freeze, rebuild the paper in this order: (1) precise question and
scope; (2) pipeline and requested/effective residual intervention; (3) frozen
cohorts, comparator definitions, and statistical units; (4) the four B
contrasts followed by E1 realization and E2 static-factor sensitivity; (5)
stored GLB base-color results and the completed, separately reported human
appearance/texture judgments if collected; (6) MV-Adapter and FAC boundary
results; (7) limitations, contribution comparison with SSI, and reproducibility
artifacts. Rebuild every table and figure from the audited source rows. Do not
edit the 01549 manuscript before the remaining evidence gates are closed.

## Open gates

- E2 formal generation and pre-analysis integrity audit have passed; the
  factorial results and object-level seed-range supplement are recorded in
  `STATIC_FACTORIAL_ANALYSIS.md` and `STATIC_FACTORIAL_SEED_VARIATION_NOTE_20261006.md`.
- New LLH human responses remain absent; the pre-existing submitted 3AFC study
  is not a substitute for the four-pair frozen LLH evaluation.
- Seam reproducibility, portable clean-clone reconstruction, final manuscript
  integration, and contribution adequacy remain open.
- The current verdict is **NOT READY / HOLD**. Technical PASS results do not
  close the human, contribution, seam-reproducibility, or final-review gates.
