# CAG-D-26-00962 Review Constraints

Audit date: 2026-09-29 UTC

## Material provenance

The attached review PDF is preserved verbatim at:

- `reviewer_materials/CAG-D-26-00962-reviews.pdf`
- `reviewer_materials/CAG-D-26-00962-reviews.txt`

SHA-256:

- PDF: `fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb`
- extracted text: `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5`

## Distinction between document and user instructions

The review PDF contains reviewer concerns and publication conditions. It does
not authorize a GPU run, a dataset change, a checkpoint change, a metric patch,
or a manuscript edit by itself. The user's current instruction is to preserve
the reviews on the server and coordinate the remaining agents using the reviews,
the paper, and the actual repository evidence. The agent orders in
`AGENT_ORDERS.md` are the operational decisions for this workspace.

## Reviewer-to-evidence matrix

| Reviewer request | What the review actually requires | Current evidence | Decision gate |
|---|---|---|---|
| R1: broader full-object comparisons | Show unmodified/no-adapter, competitive fixed-scale baseline, and TCAS across whole objects; visible artifacts must not be hidden by crops. | Clean-v2 panels exist for 300 objects; a 12-object Exact cohort exists. | A panel audit can support qualitative coverage; final practical claim still waits for D's real baked unseen views. |
| R1: same main adapter on strict holdout | Evaluate the main adapter and relevant baselines under one held-out protocol. | Clean-v2 is UID-disjoint from the historical 1,118 list and has complete four-condition 300-object output; controlled retraining is not the missing original checkpoint. | Use clean-v2 as a controlled UID-disjoint rerun with explicit checkpoint label; never call old nominal-276 numbers strict independent evidence. |
| R1: baking/unseen views/seams | Demonstrate a real textured mesh rendered from views not used for baking and report seam/cross-view behavior. | The two-object CPU bake smoke and the completed 12-object CPU bake are available; the latter has 48 GLB records and 528 unseen-view rows with finite enabled metrics and semantic mesh/UV checks. | D's result is accepted only as stratified descriptive evidence, with exporter reindexing, unavailable DISTS, absent 12-object GT bake, and COLOR/SOURCE-FUSION inconsistency disclosed. |
| R1: variation versus fidelity | Laplacian/RGB/gradient changes are diagnostics, not GT-relative fidelity. | Raw and GT-relative metric helpers exist; B has GT-relative texture error for MV-Adapter. | Paper may call variation metrics diagnostics; no fidelity claim without GT-relative metric and protocol label. |
| R1: paired uncertainty and Edge-SSIM trade-off | A CI crossing zero is not equivalence/non-inferiority; disclose lower Edge-SSIM where present. | Paired bootstrap artifacts exist; main clean-v2 C3 has lower FG metrics than fixed-low and the Full-SSIM ordering is representation-sensitive. | Report paired CI and win rate; no “equivalent”, “non-inferior”, or blanket “preserves structure” language without a prespecified margin. |
| R1: FAC reproducibility | Give enough protocol/code detail to reproduce the controlled FAC negative result. | Supplementary and response working draft contain protocol details; code release metadata is still pending. | C can prepare a reproducibility checklist only after numerical entries are frozen; no new FAC GPU work now. |
| R2.1: methodological novelty | Explain why the work is more than an arbitrary schedule choice. | Main-adapter 276-object equal-mean stage-placement test is complete; serialized Full-SSIM shows C3/LHL above fixed-mean and HLL but below LLH. MV-Adapter also shows position effects without a unique winner. | Frame the contribution as bounded adapter-scoped stage-utility/mechanism analysis, not universal optimization. |
| R2.2: CAI may be post-hoc | Separate empirical interpretation from a predictive/unique selection rule. | Selected-pair Exact calibration is `undefined_set_valued`; LHL is only direct shape-transfer. | Remove any unique CAI-winner implication; report CAI as a frozen empirical diagnostic with adapter-dependent limits. |
| R2.3: different backbone | Test a genuinely different geometry-conditioned multi-view backbone. | B completed MV-Adapter Exact 76-object experiments and unified paired statistics; official pretraining UID disjointness remains unknown. | This is partial cross-backbone evidence: report within-backbone effects, no absolute cross-backbone comparison, disclose pretraining limitation. |
| R3 | Reviewer considers the revision publishable. | No additional scientific requirement. | Do not treat R3 as evidence that unresolved R1/R2 gates are waived. |

## Paper-claim hazards identified by the matrix

The current `final/round2/final_round2.tex` still contains text that must be
held back from Codex C until the gates are resolved:

- the old `0.96 dB` pooled claim in the abstract/prose;
- “strictly disjoint” statements that refer to the historical pool rather than
  the clean-v2 controlled retraining artifact;
- the claim that middle-stage concentration is stable across all tested
  adapter regimes;
- the existing prose/table values for the 276-object stage-placement transfer
  and the statement that C3 wins over generic schedules; replace them with the
  serialized PNG/raw-GT Full-SSIM branch and the qualified LLH counterexample;
- “baking-based evidence” before the 12-object bake is accepted;
- any implication that C3 is better than fixed-low on Full-SSIM or foreground
  fidelity;
- any universal or unique CAI-selection statement.

