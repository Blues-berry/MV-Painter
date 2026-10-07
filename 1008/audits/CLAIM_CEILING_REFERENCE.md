# Claim-ceiling reference for 1008

Audit date: 2026-10-07 UTC  
Authority commit: `d59c4606ad54239bf4df4f20067bcc54989404f7`

> 1008 preserves the scientific identity and presentation continuity of
> 01549, while the d59 evidence-safe rewrite is used only as a ceiling on
> claim strength.

The d59 manuscript candidate is not the 1008 manuscript base. The controlling
numeric sources are its reviewer-closure records and machine-readable
authority tables, especially:

- `1006/evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv`
- `1006/evidence/audits/RESULT_AUTHORITY_REGISTRY.csv`
- `1006/review/REVIEWER_EVIDENCE_CLOSURE_MATRIX_V2.md`
- `1006/review/READY_FOR_MANUSCRIPT_REVISION_VERDICT.md`
- `1006/evidence/audits/PUBLIC_HUMAN_DATA_DISPOSITION_20261007.md`

## Permitted numerical anchor

The registered Fresh C primary contrast is C3 minus GFL on foreground PSNR:

- N=300 objects; mean difference **+0.522352 dB**.
- 95% object-bootstrap CI **[+0.404160, +0.640669] dB**.
- Median difference **+0.554514 dB**; 68.7% of objects favor C3.
- The authority labels this a registered primary endpoint in a
  revision-era Fresh C follow-up, not an original-preregistration replication.

The authority row points to the hash-pinned object-delta input
`1006/review/numerical_inputs/fresh_c_c3_minus_gfl_object_deltas.csv`
and the analysis script/output hashes. Fresh C is not the v3
`FRESH_CONFIRM_300` cohort: the two 300-object UID sets have zero
intersection. They must remain separate and must not be pooled or described
as a replication of one another.

## Boundaries that govern all paper-facing wording

| Topic | Allowed interpretation | Do not claim |
|---|---|---|
| C3 / TCAS | A tested, frozen, training-free low–high–low schedule; empirical value within the tested adapter and protocol | Universal optimum, unique winner, model-independent stage law, or a schedule uniquely derived by CAI |
| Comparator strength | Fresh C is positive against GFL on its registered foreground-PSNR endpoint; generic schedules expose endpoint-specific trade-offs | Overall superiority across endpoints or concealment of generic-linear results |
| Texture measures | Variation / high-frequency diagnostics, when their source and metric provenance are verified | Texture fidelity, naturalness, or preservation inferred from RGB standard deviation, gradients, or Laplacian variance alone |
| Historical `+0.96 dB` | Historical provenance only; original checkpoint/protocol limitations remain | Current headline, Fresh C replication, or strict independent holdout result |
| CAI | At most a descriptive post-hoc supplement interpretation | Predictive selector, proof of optimality, or unique derivation of C3 |
| FAC | Removed from this revision because run provenance does not meet the current reproducibility gate | FAC method/result/contribution as current evidence |
| Human preference | No human superiority result is authorized for 1008 | “Blinded readers prefer TCAS” or significant perceptual superiority |
| 3D / seams | Historical bounded evidence only if separately authenticated and explicitly scoped | PBR, seam, or population-level unseen-view superiority |
| Cross-interface | A scoped boundary/diagnostic with protocol limitations | Architecture-invariant transfer or direct absolute-score comparison |
| Prior art | Layer/timestep scheduling is established prior art; discuss Scheduled Style Injection directly | “First layer × timestep schedule” or broad control-space novelty |

The Fresh C C3–GFH Edge-SSIM contrast is post hoc: mean −0.018814, nominal
95% CI [−0.020803, −0.016790], with 47/300 objects favoring C3. It must be
paired with the endpoint-specific counterevidence in the authority and must
not be described as preregistered, equivalent, non-inferior, or evidence of
an overall winner. Generic linear also remains visible: LLH minus generic
linear FG-LPIPS is +0.001372 (95% CI [+0.000762, +0.002081]); because lower
LPIPS is better, this endpoint favors generic linear.

## D59 PDF discrepancy

The d59 tree contains the restructured TeX candidate but no corresponding
`final/round2/final_round2.pdf`. Its source could not be built from that clean
checkout because required style/class and figure inputs were absent. A
separately named eight-page d59 PDF was not authenticated. Do not use its
page count or structure as authority for the 1008 manuscript.

## Human-data governance boundary

The public v3 ancestry contains participant-linked responses, assignments,
object IDs, and stimulus links. The d59 disposition says public
redistribution permission and non-reidentifiability are not established and
sets `PUBLIC_RAW_HUMAN_DATA = NO`. A separate 1006 branch reports an analysis
with execution deviations, while d59 does not authorize human results for
paper claims. 1008 therefore excludes the result and does not copy
participant-level rows. The public-history remediation remains a separate,
unresolved repository-governance task; no history rewrite was performed.
