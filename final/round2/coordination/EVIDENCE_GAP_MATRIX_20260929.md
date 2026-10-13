# Evidence–claim matrix for the targeted C&G revision

Date: 2026-09-29 UTC  
Status: working audit; claims are frozen only after the consistency checks.

| Reviewer concern | Evidence currently available | What it can support now | Remaining gap / action | Paper treatment |
|---|---|---|---|---|
| R1: complete-object practical quality | strict-276 metrics; full-object comparison panels; 12-object exact-GLB/unseen-view case study | TCAS changes appearance and the operational GLB path runs on a stratified cohort | fixed-low remains competitive; no population-level baked-texture superiority; restore/verify comparison grids and failure cases | main results + explicit limitation |
| R1: fidelity vs variation | FG-PSNR/SSIM/LPIPS, Edge-SSIM, colour/SSIM provenance; LapVar diagnostics | separates structural/texture signals and exposes trade-offs | visual inspection must accompany variation metrics; diagnose brown cast before interpretation | main text and supplement |
| R1: unseen views/seams/coverage | existing 48-object/528-view records and 12 exact-GLB cohort | pipeline feasibility and selected failure boundaries | verify object–condition–view pairing and report missing values as missing, not zero | main figure + supplement |
| R2: contribution beyond manual schedule | explicit residual scaling, stage-placement tables, paired comparisons | reproducible training-free inference-time intervention; measurable stage sensitivity | no universal selector; no unique CAI winner; strict equal-effective-budget evidence incomplete | contribution narrowed, mechanism as empirical hypothesis |
| R2: cross-backbone generality | MV-Adapter 76-object audit and provenance files | stage effects can be measured on another backbone; implementation transfer is possible | no same-direction practical gain or absolute cross-backbone comparison; pretraining overlap unknown | bounded cross-backbone subsection |
| First-round: generic schedule comparison | fixed-low/high, C3, HLL/LLH/fixed-mean records in main and MV-Adapter packages | no single schedule dominates all metrics; LHL is not universally best | ensure schedule semantics, nominal vs actual budget, and condition names are consistent | results table + response |
| Historical preference/FAC claims | partial archives without fully recoverable checkpoint/protocol | contextual or negative supplement evidence only | no core claim from unverifiable numbers | remove from active core claims |
| TRB pilot | 12-object pilot and visual grid | exploratory controller signal only | legacy duplicate view mode and incomplete RNG control; rerun strict development pilot or stop | internal until gate passes |

## Claim freeze rules

- “Demonstrated”: a result has a protocol, object list, source hashes, and
  paired comparison semantics that can be reconstructed.
- “Exploratory”: a result is retained for diagnosis but has a used holdout,
  incomplete control, or post-hoc choice.
- “Not claimed”: unsupported historical or causal statements are removed from
  the active manuscript, even if the old files remain archived.

The first method sentence must not say “optimal”, “universal”, “predicted by
CAI”, or “unconditionally improves quality”.
