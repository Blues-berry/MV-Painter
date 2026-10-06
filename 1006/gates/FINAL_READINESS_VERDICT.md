# Final readiness verdict — 2026-10-06

## Verdict: HOLD — evidence package reviewable; not cleared for direct system upload

The separate `1006` candidate is complete enough for scientific and editorial
review and compiles to a main paper and supplement. It preserves the
previously submitted 01549 files. This verdict does **not** authorize a claim
that all reviewer concerns have been accepted, and it does not represent a
journal submission.

| Gate | State | Basis |
|---|---|---|
| Prior manuscript preservation | PASS | Hashes match the recorded entry values; see `MANUSCRIPT_PRESERVATION_AUDIT.md`. |
| Candidate narrative bounded to available evidence | PASS | No universal winner, dose-independent Layer × Window law, human-fidelity claim for LLH, seam claim, or broad transfer claim. |
| Main and supplementary LaTeX build | PASS | Candidate PDFs compile with the supplied Elsevier/CAG source format. |
| Fresh-B core temporal evidence | PASS WITH CHRONOLOGY LIMIT | 4,500/4,500 rows passed integrity; cohort is disjoint, but B's safeguard locks followed prior outcome exposure. The paper states this. |
| C3/GFL held-out comparison | PARTIAL | FRESH_CONFIRM_B provides a disjoint N=150 object cohort, but the C3−GFL comparison is post hoc after unblinding. It is supplemental evidence, not a registered confirmation. |
| Fresh C3/GFL follow-up | IN PROGRESS | All 600 frozen screen assets downloaded with zero failures; 594 pass the initial GLB geometry screen and are undergoing the locked 17-view render, pixel-deduplication, and coverage checks. No method outputs exist. It can strengthen new-object evidence but cannot restore the original preregistered status. |
| Dose-normalized Layer × Window mechanism | NOT ESTABLISHED | E5 passed numerical implementation checks, but at alpha=0.005 the shallow group exceeded its native cap on 30.4% of wrapper steps. The pilot used six reused development objects and collected no quality metrics. Keep interaction claims conditional on the measured profile and cap. |
| strict-276 C3 provenance | PARTIAL | Seven endpoints are paired and reported, including the GC3/GFH trade-off, but runner identity and complete legacy input-tensor hashes are unavailable. |
| Human/perceptual fidelity | OPEN / CLAIM WITHDRAWN | The new human study has zero responses. The candidate makes no LLH human-preference or human-fidelity claim. This is a defensible scope limit only if the editor accepts it; no reviewer waiver is available. |
| Three-dimensional appearance | BOUNDED | Stored GLBs were evaluated on 20 UV-supported objects and 11 unseen views, with mixed endpoints. Four no-UV objects remain excluded; no rebake, seam validation, or full PBR evaluation is established. |
| Cross-interface generalization | BOUNDED | MV-Adapter and MVDiffusion are separately reported interface-boundary results, not matched causal architecture tests. |
| Novelty and contribution sufficiency | BLOCKING JUDGMENT | Scheduled Style Injection is close prior work. The narrowed MVPainter-specific empirical contribution may still be judged too incremental; additional wording cannot settle that editorial question. |
| Asset redistribution | OPEN / PUBLIC BRANCH NOT LICENSE-CLEARED | Two visual-panel licenses are supported only by the Objaverse snapshot; one record includes a personal-project-use description and another model endpoint is unavailable. The public task branch currently contains the contact sheet and compiled supplement with these derivatives. Obtain source-level terms/permission or remove and rebuild those artifacts before treating any branch/package as release-ready. |
| Portable paper-wide rebuild | PARTIAL | The compact analyses and candidate figures/tables are reproducible from included data, but the omitted render/residual payloads prevent a clean clone from rebuilding every generation result. |
| Final reviewer response and submission metadata | PARTIAL | A point-by-point candidate with page/line references exists; final author review, title-page metadata, and a post-freeze pagination check remain. No editor decision is represented. |

## Why this does not pass the upload gate

The strongest current positive evidence is carefully bounded: FRESH_CONFIRM_B
supports several mean image-space differences, but not a universal temporal
rule or a typical-object PSNR advantage for LLH over HLL. The C3−GFL result on
that cohort was added after unblinding. The older strict-276 comparison also
has provenance limits and trade-offs. The GLB-native endpoint is an
unlit base-color evaluation on N=20, not a comprehensive 3D fidelity study.

The revision appropriately removes claims that these experiments cannot
support. However, R1 may still require perceptual evidence, and R2 explicitly
questions whether the remaining empirical contribution is substantial
enough. E5's numerical PASS does not repair the dose-support gap: the shallow
cap was exceeded at the smallest tested perturbation. The candidate cannot
state these objections are resolved by claim reduction alone. Publicly
redistributing the two license-uncertain visual assets also remains unresolved.
The task branch is publicly visible and currently contains the candidate contact
sheet and compiled supplement that include those two assets; it must be treated
as a review snapshot with an open rights gate, not as a cleared public release.

## Release decision

`CANDIDATE_DRAFT_COMPILES=YES`

`CLAIM_SCOPE_BOUNDED=YES`

`SCIENTIFIC_EVIDENCE_FREEZE=NO`

`REVIEWER_CLOSURE=PARTIAL`

`DIRECT_SYSTEM_UPLOAD=NO`

No journal system action has been taken. Reopen this gate after asset terms
are resolved, the author decides whether to collect the frozen human study
or retain the reduced claim scope, a venue/contribution decision is made,
and the response and package are rechecked after the scientific text is
frozen.
