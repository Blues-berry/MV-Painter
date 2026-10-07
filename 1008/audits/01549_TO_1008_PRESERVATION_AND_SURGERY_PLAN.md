# 01549 → 1008 preservation and surgery plan

Status: Phase A proposal; no manuscript text has been edited.  
Baseline: verified 01549 package in `1008/manuscript/source_01549/`.  
Evidence ceiling: d59 authority summarized in
`1008/audits/CLAIM_CEILING_REFERENCE.md`.

Action values are restricted to the six requested values. For historical
results without a hash-pinned data/protocol chain in the current authority,
the manuscript source itself is not treated as proof of the result.

## Manuscript identity and sections

| Item | 01549 content | Reviewer concern | Current verified evidence | 1008 action | Why |
|---|---|---|---|---|---|
| Title | “Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation” | R2.1 questions novelty and contribution scope | TCAS remains a bounded tested strategy; scheduling prior art exists | `KEEP_01549` | Preserve identity while narrowing novelty language in the body |
| Abstract | Frames TCAS as a shape/texture balance and includes broad superiority language | R1 asks for held-out evidence and honest endpoint limits; R2.1 challenges novelty | Fresh C supports one registered C3−GFL foreground-PSNR endpoint; stronger schedules create trade-offs | `KEEP_WITH_WORDING_FIX` | Retain the TCAS paper, replace historical headline claims with Fresh C and scoped conclusions |
| Introduction | Motivates stage-dependent adapter response and introduces TCAS | Avoid universal stage-law and “first schedule” claims | Stage-dependent heterogeneity is only supported within tested regimes; layer/time schedules are prior art | `KEEP_WITH_WORDING_FIX` | Preserve the original problem statement and explicitly bound the inference |
| Related Work | 3D texture generation, multi-view diffusion, adapters/control, guidance scheduling | R2.1 asks how the work differs from prior scheduling | Scheduled Style Injection is direct prior art; task, injected signal, architecture, and objective differ | `KEEP_WITH_WORDING_FIX` | Keep the section order and add a direct SSI comparison; remove broad novelty claims |
| Base pipeline / task | Geometry-controlled multi-view diffusion and adapter residual injection | Method must remain clear and reproducible | 01549 source package verifies the method description and original diagram | `KEEP_01549` | This is central to the original method identity |
| TCAS definition | Three-stage low–high–low schedule, C3=(1.25, 2.50, 1.25) | Explain selection without presenting CAI as proof | C3 is an empirically selected, frozen schedule; Fresh C is the new load-bearing validation | `KEEP_WITH_WORDING_FIX` | Preserve C3 and the method; call it tested/frozen, not optimal or universal |
| CAI | Formal derivation/proposition used to motivate schedule selection | R2.2 says CAI may formalize a post-hoc choice | Authority does not support a predictive unique selector | `MOVE_TO_SUPPLEMENT` | Main method should state empirical probe selection; any retained CAI is descriptive only |
| GeoTex-Adapter / FAC | Adapter details followed by learned FAC extension | R1.5 requests reproducibility; FAC provenance fails the current gate | FAC disposition is `REMOVED_FROM_REVISION` | `REMOVE` | Remove FAC method, training, results, contribution, and conclusion claims |
| Experimental setup | Cohorts, seed, metrics, checkpoints, and pooled reporting | R1.2 asks for one held-out main-adapter protocol and paired uncertainty | Fresh C has a hash-pinned N=300 source and paired object-level authority; it is a revision-era follow-up | `KEEP_WITH_WORDING_FIX` | Preserve setup flow; update cohort identity, checkpoint/protocol labels, unit, CIs, and registration status |
| Uniform-scale motivation | 13-scale 50-object sweep and 26-object texture audit | R1.3 warns that variation is not fidelity; historic source/protocol may be incomplete | The old paper contains values/plots, but no matching old result row is in the current numerical authority | `KEEP_WITH_WORDING_FIX` | Keep the development motivation; do not carry unverified old numbers as current confirmatory evidence |
| 24-object / 17-variant probe | Development comparison used to select C3 | Do not present selection data as independent confirmation | User-directed role is development evidence; current primary validation is Fresh C | `KEEP_WITH_WORDING_FIX` | Preserve the schedule-selection narrative, mark it development-only, and avoid “independent proof” language |
| Large-scale validation | Pooled 300-object comparison includes probe objects and historical primary claims | R1.2 requires fresh held-out validation; old +0.96 dB is unsupported as current | Fresh C registered C3−GFL FG-PSNR: +0.522352 dB, 95% CI [+0.404160,+0.640669], N=300 | `KEEP_LAYOUT_REPLACE_DATA` | Retain the main comparison role but replace load-bearing old values with authority-backed Fresh C values |
| Strong schedule comparators | Original paper centers uniform scales and selected variants | R1.4 asks for endpoint-aware comparison; generic linear must not be hidden | Fresh C comparator authority includes GFH, LLH, and generic linear; no cross-endpoint winner | `ADD_MINIMAL_NEW` | Add compact comparator evidence where it answers reviewers; keep LLH as comparator, not a new method |
| Texture diagnostics | Laplacian variance, RGB standard deviation, gradient magnitude | R1.3 separates variation from fidelity | These are diagnostics; not sufficient as GT-relative fidelity or perception evidence | `KEEP_WITH_WORDING_FIX` | Rename as variation/high-frequency diagnostics and use only if their data source is independently verified |
| Qualitative results | Original 26-object and probe-set panels | R1.1 questions visible artifacts and asks for whole-object comparisons | Fresh C rights-cleared candidate pool is available; selected examples remain illustrative, not a cohort estimate | `KEEP_LAYOUT_REPLACE_DATA` | Preserve the original visual role and continuity while replacing stale/uncleared assets with attributed candidates |
| Human study | 3AFC table and claimed overall preference advantage | Human claims require authentic assignments, presentation order, governance, and reproducibility | 1008 has no authorized confirmatory human result; the later branch has protocol deviations and public-data concerns | `REMOVE` | Remove preference claims and table; do not copy participant-level records |
| 3D bake / unseen-view / seam | Historical 3D/bake content and possible N=20 base-color evidence | R1.1 requests unseen views and seams; current stronger evidence retires population-level claims | New Fresh C 24-object 3D and seam claims are retired; historical N=20 results are mixed and bounded | `MOVE_TO_SUPPLEMENT` | At most retain separately authenticated historical unlit base-color evidence with mixed endpoints; no main superiority claim |
| Cross-interface boundary | Not a main 01549 experiment | R2.3 requests a different backbone/interface | d59 supports only qualified within-interface diagnostics with pretraining/protocol limits | `ADD_MINIMAL_NEW` | Add a short boundary paragraph and, only if space requires, one compact table; put detailed results in Supplement |
| Limitations | Notes model and metric limitations | Must align with withdrawals and protocol limits | Current audits prohibit universal, fidelity, non-inferiority, human, and 3D/seam claims | `KEEP_WITH_WORDING_FIX` | Retain the section but state the tested scope and remaining limitations explicitly |
| Conclusion | Concludes TCAS balances geometry and texture | Avoid implying universal superiority or optimality | Fresh C supports fixed-baseline value on its registered endpoint; stronger comparators expose trade-offs | `KEEP_WITH_WORDING_FIX` | Keep TCAS as the subject and state that benefit depends on endpoint/comparator |
| Data availability / declarations | Original declarations and availability text | Release package and rights must be accurate | Public release currently fails; participant-level data and some assets are excluded | `KEEP_WITH_WORDING_FIX` | Preserve structure, update availability and rights language to match the actual releasable package |

## Original figures

| Item | 01549 content | Reviewer concern | Current verified evidence | 1008 action | Why |
|---|---|---|---|---|---|
| Figure 1 | Geometry adapter + TCAS pipeline; optional FAC branch | Preserve recognizable method diagram without retaining unsupported FAC | Figure is part of verified source package; FAC is removed | `KEEP_WITH_WORDING_FIX` | Retain the pipeline and TCAS visual anchor; remove the FAC branch and edit caption claims |
| Figure 2 | FG-SSIM / Crop-SSIM curves for 13 uniform scales | Old scale-sweep data are not in current numerical authority | Historical plot exists in submission package; no matching pinned result row found in d59 authority | `MOVE_TO_SUPPLEMENT` | Keep only as historical development context after provenance check; do not lead with unsupported values |
| Figure 3 | 50-object heatmap across 13 scales | Avoid treating the same development pool as held-out confirmation | Historical image exists; it is not Fresh C and has no current result-authority row | `MOVE_TO_SUPPLEMENT` | Preserve provenance without presenting it as independent validation |
| Figure 4 | 26-object uniform-scale texture examples | R1.1 asks for full-object, visible comparisons; rights and cohort identity must be clear | Fresh C candidate assets are rights-cleared for selected examples; all panels remain curated illustrations | `KEEP_LAYOUT_REPLACE_DATA` | Retain comparison layout while replacing old assets with attributed whole-object examples |
| Figure 5 | 26-object RGB-std and gradient ratios with “texture loss” interpretation | R1.3: variation is not fidelity | Old numbers are not in current authority; these measures are diagnostics only | `MOVE_TO_SUPPLEMENT` | Detailed legacy diagnostics belong in Supplement and require verified source/provenance |
| Figure 6 | C3 versus two fixed scales on probe objects | Keep qualitative explanation of C3 while avoiding average-object implication | New Fresh C rights-cleared candidates can illustrate selected differences | `KEEP_LAYOUT_REPLACE_DATA` | Preserve C3 visual continuity; use whole-object, attributed Fresh C cases and a descriptive caption |
| Figure 7 | Pareto plot for 17 schedule variants | Probe is development evidence, not confirmation | The user directs preserving selection narrative; no independent-confirmation role | `MOVE_TO_SUPPLEMENT` | Retain complete development comparison outside the main claim-bearing results |

## Original tables

| Item | 01549 content | Reviewer concern | Current verified evidence | 1008 action | Why |
|---|---|---|---|---|---|
| Table 1 | 13-scale sweep on 50 objects | Historical values lack current authority rows | Values are in submitted TeX but source rows/protocol are not authenticated in d59 | `MOVE_TO_SUPPLEMENT` | Keep as historical development only if the source can be recovered and checked |
| Table 2 | Eight representative variants from 17 schedules on 24 objects | Selection data must not masquerade as independent confirmation | C3 is retained as empirically selected/frozen; probe is development evidence | `MOVE_TO_SUPPLEMENT` | Preserve the full probe record outside the main validation claim |
| Table 3 | Extended texture diagnostics for representative probe variants | Variation is not fidelity; table is probe-scoped | No matching current numerical-authority rows; diagnostics need scoped interpretation | `MOVE_TO_SUPPLEMENT` | Keep only as a bounded diagnostic record after provenance check |
| Table 4 | Pooled 300-object metrics, including the probe cohort | R1.2 requires a fresh cohort; old +0.96 dB is retired | Fresh C authority pins the N=300 primary endpoint and paired interval | `KEEP_LAYOUT_REPLACE_DATA` | Reuse the main comparison slot for Fresh C and endpoint-specific comparator results |
| Table 5 | Pooled texture variation metrics on the same 300-object pool | R1.3 requires variation/fidelity separation | Authority-backed metrics must be used; old pooled values are not Fresh C confirmation | `MOVE_TO_SUPPLEMENT` | Keep only as explicitly labeled variation diagnostics after row-level verification |
| Table 6 | Texture retention ratios and win rates | Ratios can overstate “preservation” and inherit the old cohort limitations | No current authority row for these ratios | `MOVE_TO_SUPPLEMENT` | Do not let derived ratios carry a main-paper fidelity claim |
| Table 7 | CLIP-IQA results on 50 objects | A no-reference score does not establish human preference or fidelity | No current authority row or verified source package for reuse | `REMOVE` | It is not needed for TCAS identity and does not close the reviewer concern |
| Table 8 | Blinded 3AFC preference counts and significance claims | Human provenance and governance are unresolved | No human result is authorized for 1008 | `REMOVE` | Withdraw human superiority claims and do not reproduce the table |
| Table 9 | Historical strict-276 schedule transfer on a separate adapter | Must not be confused with Fresh C or presented as a registered primary result | d59 classifies strict-276 as retrospective support | `MOVE_TO_SUPPLEMENT` | Preserve only as clearly labeled retrospective evidence, if its full provenance remains auditable |

## Minimal additions and global guardrails

| Addition | Reviewer concern | Current verified evidence | 1008 action | Why |
|---|---|---|---|---|
| Scheduled Style Injection comparison | R2.1 novelty | Scheduling prior art is established | `ADD_MINIMAL_NEW` | Add a direct, accurate prior-art paragraph without claiming a new scheduling primitive |
| Implementation-aware scale execution | Nominal versus applied adapter scale can differ | d59 records requested/applied/cap/residual accounting | `ADD_MINIMAL_NEW` | Use one short subsection and a compact table; put full traces in Supplement |
| “What TCAS does and does not establish” | Claim boundaries and endpoint trade-offs | Fresh C and comparator authority are explicit | `ADD_MINIMAL_NEW` | Make supported and unsupported claims easy to audit |
| Fresh C primary result | R1.2 held-out validation | Hash-pinned N=300 paired object-level result | `ADD_MINIMAL_NEW` | Insert the registered C3−GFL endpoint and uncertainty in the existing main-results flow |

No main-text addition should displace the pipeline/schedule figures or turn
the paper into a general residual-accounting audit. The matrix is the Phase A
decision record; implementation begins only in a later phase.
