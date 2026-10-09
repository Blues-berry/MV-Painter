> **Superseded on 2026-10-08.** The author-confirmed correction in [ROUND1_01549_TO_ROUND2_1008_MAPPING.md](ROUND1_01549_TO_ROUND2_1008_MAPPING.md) and the updated [01549 reviewer reanalysis](01549_REVIEWER_REANALYSIS_20261008.md) now govern this task. Do not follow any older statement that treats 01549 as an initial submission, leaves the round mapping formally open, requires Fresh C to match the historical Table 4 checkpoint hash, removes the reported FAC negative re-examination, or discards the first-round cluster-aware preference result. This file is retained as a dated audit trail.

# 01549-first surgical review — 2026-10-08

Status: **review plan only; no manuscript TeX edited.**  This record is an
independent review of the prior preservation plan, not an execution checklist.

## Baseline and review set

- Organizing baseline: branch `codex/cg-round2-1008-revision-20261008`, HEAD
  `20dff3e791adabb8ee45a8746b79716dd3ed9c74`.
- Sole body source: `1008/manuscript/source_01549/final_0903.tex`, SHA-256
  `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.
  The worktree copy and `git show 20dff3e7:...` hash match.
- Page mapping: `1008/manuscript/source_01549/01549_submitted_manuscript_0907.pdf`,
  15 pages. `01549_SOURCE_BASELINE_VERIFICATION.md` records that the source
  archive rebuild raster-matches the submitted PDF on all pages.
- Reviewer source: `final/round2/coordination/reviewer_materials/CAG-D-26-00962-reviews.pdf`
  and its text companion. This is the supplied R1/R2/R3 set dated 14, 24, and
  28 September 2026; all three sections are labelled “Initial submission.”
  The source-provenance audit pairs that set with CAG-S-26-01549. R3 is
  positive and asks for no technical change.
- The previous staged repository-cleanup changes were already present when
  this review began. No cleanup, TeX, figure, table, or experiment file was
  changed for this review.

## Paragraph-level comparison and proposed action

Page numbers below are the submitted-PDF pages. TeX line numbers point to the
verified base source. Every operation other than `KEEP` is tied to the
reviewer concern or evidence gate shown in the row.

| 01549 page / section / TeX | Original paragraph or object purpose | Reviewer issue / evidence reason | Action | Surgical proposal | Evidence to use | Figures/tables retained in main text |
|---|---|---|---|---|---|---|
| p.1 / Title | Identifies the paper and TCAS method | Preserve identity | `KEEP` | Keep title verbatim. | Verified 01549 source and submitted PDF | — |
| p.1 / Abstract / l.33 | Summarizes motivation, CAI derivation, C3, +0.96 dB, texture and human-preference gains | R1.2, R1.3, R1.4; CAI and human results do not pass current evidence ceiling | `REPLACE_EVIDENCE` | Keep TCAS and C3 identity; replace the headline with the Fresh C registered endpoint, the visible comparator trade-offs, and the follow-up/limited-scope qualification. Remove +0.96 dB, CAI derivation, texture-fidelity inference from variation scores, and human superiority. | Fresh C authority; CAI and human dispositions | Abstract only |
| p.2 / Introduction / ll.48–52 | 3D texturing context and inference-time adapter scale motivation | No identified defect in the basic task setup | `KEEP` | Retain the original motivation and order. | 01549 text and cited task literature | — |
| p.2 / Introduction / ll.54–56 | Stronger control can affect geometry and texture; motivates study | R1.3: variation is not fidelity; avoid a universal causal statement | `LOCAL_REWRITE` | Preserve the trade-off motivation, but describe visible/metric changes as tested outcomes and distinguish texture variation diagnostics from fidelity. | R1.3; figure and endpoint limits | — |
| p.2 / Introduction / l.58 | Positions TCAS against CFG and monotonic schedules | R2.1: scheduling has direct prior art; current broad “not solved” framing is too strong | `LOCAL_REWRITE` | Keep the signal-mechanism distinction. Add the direct Scheduled Style Injection comparison and narrow what is specific to this tested geometry-residual setting. | R2.1; `FINAL_R21_CONTRIBUTION_AUDIT.md` and its primary SSI citation | — |
| p.2 / Introduction / l.60 | Defines paper scope as inference-time scaling in a fixed pipeline | This is the original paper identity | `KEEP` | Retain. | 01549 source | — |
| p.2 / Contributions / l.64 | Claims broad diagnosis across flattening, artifact amplification, and no-effect regimes | R1.3/R2.3; regimes are implementation/interface-specific | `LOCAL_REWRITE` | Retain the contribution, but state the tested scope and avoid generalizing across adapter families. | Cross-interface and A2/A3b boundary reports | — |
| p.2 / Contributions / l.66 | Introduces three-stage TCAS | Preserve the paper’s central method | `KEEP` | Retain TCAS and its low–high–low form; do not relabel it. | 01549 method definition | — |
| p.2 / Contributions / l.68 | Describes the 24-object probe and 300-object pooled evaluation as transfer support | R1.2: pooled set includes probe; old main-adapter comparison was not on an independent held-out cohort | `LOCAL_REWRITE` | Keep the probe as development/selection evidence; describe Fresh C separately as revision-era, same-protocol evidence and disclose its relationship to the earlier results. | Fresh C cohort/protocol hashes and R1.2 authority | Table 2, Fig. 7, revised Table 4 |
| p.2 / Contributions / l.70 | Claims 87.7/95.0/83.0% texture-retention wins and structural non-difference | R1.3/R1.4; old pooled ratios do not establish fidelity or equivalence | `REPLACE_EVIDENCE` | Replace with endpoint-specific Fresh C and comparator findings; do not infer fidelity, equivalence, or non-inferiority from these statistics. | Fresh C authority; no NI margin | Revised Table 4 |
| p.3 / Related Work / §2.1 / ll.78–80 | Organizes 3D texturing and multi-view methods | No identified defect in section organization | `KEEP` | Preserve the organization and task context. | Submitted text and current citations | — |
| p.3 / Related Work / §2.2 / ll.85–87 | Reviews adapters and geometric control | No identified defect in section organization | `KEEP` | Preserve. | Submitted text and current citations | — |
| p.3 / Related Work / §2.3 / ll.92–96 | Reviews guidance scheduling and differentiates TCAS | R2.1: direct schedule prior art is missing; avoid “dedicated” or novelty implication | `LOCAL_REWRITE` | Keep this subsection in place. Add a concise SSI comparison and describe the specific residual path, task, and tested evidence without claiming a new scheduling primitive. | `FINAL_R21_CONTRIBUTION_AUDIT.md`; primary SSI citation | — |
| pp.3–4 / Method / §3.1 / ll.104–123 | Defines MVPainter-style pipeline, geometric inputs, residual injection and scaling variable | Core base pipeline and method identity | `KEEP` | Retain the task, base pipeline, equations, and six-view projection/baking description. | 01549 source and Fig. 1 package | Fig. 1 |
| p.4 / Fig. 1 / l.109 | Shows GeoTex-Adapter → TCAS → multi-view output; caption includes FAC | FAC is excluded from this revision; preserve pipeline figure | `LOCAL_REWRITE` | Keep the diagram’s base pipeline and TCAS role; remove the optional FAC branch and FAC wording only. | FAC reproducibility disposition; source figure | Fig. 1 |
| p.4 / Method / §3.2 / ll.125–134 | Defines shape, image-fidelity and texture-diagnostic metrics | R1.3: RGB std, gradients and Laplacian variance are not fidelity measures | `LOCAL_REWRITE` | Preserve metric definitions, but split ground-truth-relative endpoints from variation/high-frequency diagnostics. State that variation alone cannot establish fidelity or naturalness. | R1.3; Fresh C endpoint specification | Table 3 and Fig. 5, with diagnostic captions |
| pp.4–5 / Method / §3.3 / ll.136–153 | Defines the three denoising stages, scale function and C3 schedule | Preserve the three-stage C3 definition; avoid an optimality interpretation | `LOCAL_REWRITE` | Retain stage boundaries, schedule equation, and C3 = (1.25, 2.50, 1.25). Describe C3 as an empirically selected, frozen schedule for the tested setup. | 24-object development record; Fresh C validation | Fig. 1, Table 2, Fig. 7 |
| p.5 / Method / CAI / ll.154–172 | Claims measured CAI utility and proves a guardrailed epsilon-optimal selector for C3 | R2.2 directly questions post-hoc formalization; current disposition rejects predictive/unique selection | `REMOVE` | Remove the CAI model, proposition, proof, remarks, and all claims that CAI derives or guarantees C3. The empirical probe remains the schedule-selection record. | `CAI_FINAL_DISPOSITION.md`; R2.2 | Keep empirical Table 2/Fig. 7 for selection history |
| p.6 / Method / §3.4 / ll.174–179 | Describes GeoTex-Adapter’s input channels and UNet residual injection | Reproducibility/base-pipeline detail | `KEEP` | Retain adapter details that define the fixed pipeline. | 01549 source and implementation description | Fig. 1 |
| p.6 / Method / §3.4 / ll.180–183 | Introduces FAC modules and extension rationale | R1.5; FAC provenance/reproduction gate fails, and FAC is not a current method | `REMOVE` | Remove FAC method description; retain no FAC contribution or claim elsewhere. | `FAC_FINAL_DISPOSITION.md`; R1.5 | — |
| pp.6–7 / Experiments / §4.1.1 / ll.191–198 | Describes comparisons and protocol, including the historical probe/holdout structure | R1.2: the old main-adapter result is pooled and the strict-276 comparison changed adapter | `REPLACE_EVIDENCE` | State the Fresh C cohort, matched conditions, object-level unit, and revision-era follow-up status. Keep old probe and separate-adapter holdout labelled as development/retrospective only. | Fresh C protocol, 1200-row gate, R1.2 numerical authority | Revised Table 4; Table 9 only if moved to supplement |
| pp.6–7 / Experiments / §4.1.2 / ll.199–206 | Defines evaluation sets and metrics | R1.2/R1.3; cohort identities and metric roles need to be explicit | `LOCAL_REWRITE` | Separate the 24-object C3-selection probe, Fresh C N=300, and the unrelated FRESH_CONFIRM_300 cohort; define fidelity endpoints and variation diagnostics separately. | Fresh C identity/hash crosswalk below; R1.3 | Tables 1–4 and Figs. 2–7 retain their distinct roles |
| p.7 / Experiments / §4.1.3 / ll.207–214 | Records implementation and dataset settings | No reason to remove fixed-pipeline details; Fresh C provenance needs to be traceable | `LOCAL_REWRITE` | Preserve reproducible setup details; update only values/labels needed to identify the Fresh C checkpoint, conditions, cap semantics, and source hashes. | Fresh C runner/config/checkpoint records | — |
| p.7 / Experiments / statistical reporting / ll.215–216 | Specifies object-level paired statistics and uncertainty | R1.4: zero-crossing CI is not equivalence or non-inferiority | `LOCAL_REWRITE` | Retain paired object-level intervals; explicitly prohibit equivalence/non-inferiority wording absent a prespecified margin. Mark reviewer-requested GFH analyses post hoc. | Fresh C analysis JSON; R1.4 audit | Revised Table 4 |
| pp.7–8 / Experiments / §4.2 / ll.218–265; Table 1; Figs. 2–3 | Uses the 13-scale/50-object sweep, curves, and per-object heatmap to motivate the trade-off | Core original evidence chain; values are historical development results, not Fresh C confirmation | `LOCAL_REWRITE` | Keep the sweep, Table 1, and both plots in the main paper. Label them development evidence, retain only the original metric interpretation, and do not use them as independent confirmation. Do not move them en masse to Supplement. | Original 01549 table/figures; recoverable source rows/logs remain a pre-edit provenance check | Table 1 and Figs. 2–3 stay in main text |
| p.8 / Experiments / §4.3 / ll.270–276; Fig. 4 | Shows selected 26-object crops; reviewers report purple shifts, repeated patterns, and reference mismatch | R1.1 directly requests whole-object, unmodified-pipeline and fixed-scale comparisons | `REPLACE_EVIDENCE` | Preserve Fig. 4’s comparison purpose, but use rights-cleared Fresh C whole-object panels with the no-adapter pipeline, GFL/fixed baseline, and C3. Identify panels as curated illustrations, not a cohort estimate. | Formal visual evidence report; Fresh C figure rights/attribution records | Fig. 4 remains in main text with new panel assets |
| p.8 / Experiments / §4.3 / ll.279–288; Fig. 5 | Reports “24/26 (92%)” texture-loss/manual “true shape gain” and variability ratios | R1.3; no objective/manual threshold supports the 92% claim; variation metrics do not establish fidelity | `LOCAL_REWRITE` | Remove the 92% and “true shape gain” classification. Keep Fig. 5’s diagnostic role only if its 26-object source rows are authenticated; relabel it as a variation/high-frequency diagnostic and remove fidelity conclusions. | Submitted source; R1.3; source-row audit required before reusing numbers | Fig. 5 stays in main text as a bounded diagnostic pending source verification |
| pp.9–10 / Experiments / §4.4 / ll.293–325; Table 2; Fig. 6 | Describes 17 variants, selects C3 on 24-object probe, and shows C3 vs two scales | R1.1/R1.2/R2.2; selection data are not held-out validation; original qualitative examples were challenged | `LOCAL_REWRITE` | Keep C3’s empirical selection history and Table 2 in the main text as development evidence. Remove any implication of independent confirmation or CAI optimality. Replace Fig. 6’s assets with Fresh C rights-cleared whole-object comparisons while retaining its C3-vs-baseline role. | Probe record; Fresh C visual candidate pool; R1.1/R1.2 | Table 2 and Fig. 6 stay in main text; Fig. 6 panel data replaced |
| p.10 / Experiments / §4.4 / ll.336–365; Table 3; Fig. 7 | Pareto plot and extended probe metrics support schedule selection | R1.2/R1.3; these are probe diagnostics, not fidelity proof or confirmation | `LOCAL_REWRITE` | Keep Table 3 and Fig. 7 in the main paper to preserve the original selection argument. Call the metrics diagnostics, remove “verifies advantage”/“Promising vs Trap” as a fidelity ranking, and label the probe as development-only. | Original probe results; R1.2/R1.3 | Table 3 and Fig. 7 remain in main text |
| pp.11–12 / Experiments / §4.5 / ll.368–395; Table 4 | Pooled old N=300 absolute scores and +0.96 dB headline | R1.2/R1.4: probe included; old holdout changed adapter; no current support for +0.96 dB | `REPLACE_EVIDENCE` | Reuse Table 4’s main-comparison slot for Fresh C N=300. Report C3−GFL registered FG-PSNR +0.522 dB [0.404, 0.641], with follow-up status; add Generic Linear, LLH, GFH and no-adapter/fixed baseline rows or paired columns sufficient to show endpoint-specific outcomes. | `FRESH_C_INTEGRITY_GATE.json`; Fresh C authority and addendum; GFH post-hoc audit | Table 4 remains in main text with new rows/results |
| p.11 / Experiments / §4.5 / ll.397–435; Tables 5–6 | Reports pooled RGB/Laplacian/gradient values and ratios as texture preservation | R1.2/R1.3; pooled set includes probe and variation does not prove fidelity | `MOVE` | Move the original pooled diagnostic tables to Supplement as historical descriptive records only, after source-row audit. The main text must not quote the old ratios as validated fidelity. Table 4 carries the current endpoint comparisons. | Original 01549 tables; R1.2/R1.3; current numerical authority does not validate these old ratios | Tables 5–6 move to Supplement; their evidence role is replaced in the main text by revised Table 4 |
| p.11 / Experiments / CLIP-IQA / ll.437–456; Table 7 | Uses a 50-object no-reference score as perceptual support | R1.3; no matching current numerical-authority/source row; does not establish human fidelity | `REMOVE` | Remove the CLIP-IQA claim and table from the revision; do not use it as human or fidelity evidence. | Numerical authority/source audit; R1.3 | Table 7 removed |
| pp.11–12 / Experiments / blinded preference / ll.458–480; Table 8 | Claims C3 has significantly higher overall human preference | Human data are not authorized for this revision; source/assignment/governance gate fails | `REMOVE` | Remove the human-study method, results, table, and all preference-superiority wording. | `PUBLIC_HUMAN_DATA_DISPOSITION_20261007.md`; review source provenance; 1008 claim ceiling | Table 8 removed |
| p.12 / Experiments / §4.6 / ll.482–493 | Reports FAC training and controlled re-examination | R1.5; run/config/training-pool provenance does not meet reproduction gate | `REMOVE` | Remove the FAC experiment subsection and every FAC result/future-work inference. | `FAC_FINAL_DISPOSITION.md`; R1.5 | — |
| pp.12–14 / Experiments / §4.7 / ll.498–506 | Claims adapter-dependent high-scale outcomes and that C3 wins across all regimes | R2.3; user forbids treating boundary evidence as generalization success | `LOCAL_REWRITE` | Keep this existing subsection as a boundary discussion. Replace “C3 best in every regime” with the actual bounded/mixed outcomes; integrate A2/A3b only as secondary explanation, not a new method or causal rule. | A2/A3b reports; MV-Adapter/MVDiffusion boundary reports | No new method figure/table required |
| pp.13–14 / Experiments / §4.7 / ll.508–526; Table 9 | Reports a disjoint-276 schedule comparison on a different strong-residual, capped adapter | R1.2: it does not validate the main adapter; retrospective, different adapter instance | `MOVE` | Move Table 9 and its full numeric comparison to Supplement, clearly labelled retrospective and adapter-specific. Keep at most a sentence in §4.7 stating that it is not the Fresh C main-adapter validation. | Strict-276 provenance disposition; R1.2 | Table 9 moves to Supplement |
| p.14 / Limitations / ll.532–538 | Notes metric and backbone limits but also repeats FAC and broad C3 robustness | R1.1/R1.3/R2.3; missing unseen-view/seam evidence; unsupported FAC and cross-interface generality | `LOCAL_REWRITE` | Preserve the limitations section. Explicitly state that unseen-view/bake/seam and human fidelity are not established; limit A2/A3b and other interfaces to the tested boundary. Remove FAC and “best in every regime.” | R1.1/R1.3/R2.3; retired 3D/seam claims; interface reports | — |
| p.14 / Conclusion / ll.544–550 | Repeats 92%, +0.96 dB, broad superiority, and FAC conclusion | R1.2–R1.5 and R2.1–R2.3; current evidence is endpoint-specific and mixed | `REPLACE_EVIDENCE` | Keep the TCAS conclusion and original role. State the Fresh C primary result plus Generic Linear/LLH/GFH counterevidence; conclude that C3 is a tested schedule with bounded scope, not a universal winner. Remove 92%, +0.96 dB, human advantage, FAC and cross-backbone success. | Fresh C numerical authority; claim ceiling | Conclusion only |
| p.14 / Data availability / ll.552–554 | Says all data are available on request | Current public-release gate is not passed; asset rights and human-data history constrain release | `LOCAL_REWRITE` | Replace with an accurate description of the actual code, scripts, aggregate CSVs, logs and rights-cleared artifacts available at revision release; do not promise all raw data or all source assets. | `PUBLIC_RELEASE_PACKAGE_MAP_20261007.md`; rights and clean-checkout gates | — |
| pp.14–15 / Declarations and references / ll.556 onward | Competing-interest declaration and bibliography | No identified reason to reorganize either | `KEEP` | Keep the declaration and citation organization; add the verified direct scheduling prior-art citation in §2.3. | 01549 source; SSI primary source cited by contribution audit | — |

## Evidence rows required in the revised main comparison

All contrasts below use paired object-level data. Positive/negative direction
is stated explicitly; none implies an overall winner.

| Contrast | Verified result to expose | Status and interpretation |
|---|---|---|
| C3 − GFL, FG-PSNR | +0.522 dB, 95% CI [+0.404, +0.641], N=300; 68.7% of objects favor C3 | Fresh C registered primary endpoint in a revision-era follow-up, not an original-preregistration replication |
| C3 − Generic Linear, FG-PSNR | −0.593 dB, 95% CI [−0.837, −0.351]; median +0.074 dB; 51.7% object-favorable for C3 | Mean and median/favorable fraction differ; do not hide Generic Linear’s mean advantage or collapse the distribution to one winner |
| C3 − Generic Linear, FG-LPIPS | +0.01351, 95% CI [+0.01160, +0.01549] | Lower is better, so this endpoint favors Generic Linear |
| LLH − C3 | FG-PSNR +0.621 dB [+.391, +.855], but median −0.153 and 46.7% favor LLH; FG-LPIPS −0.01214 [−.01386, −.01048] | Endpoint/object-dependent; LLH helps LPIPS while the PSNR mean is heterogeneous |
| LLH − Generic Linear | FG-PSNR +0.0276 dB [−.0148, +.0698]; FG-LPIPS +0.001372 [+.000762, +.002081] | PSNR interval crosses zero; LPIPS favors Generic Linear. Addendum, same Fresh C cohort, separate run/hash |
| C3 − GFH | Edge-SSIM −0.01881 [−.02080, −.01679]; Full-PSNR +0.6607 [+.5858, +.7358] | Reviewer-requested post-hoc comparison: GFH wins Edge-SSIM while C3 wins Full-PSNR; no non-inferiority or equivalence claim |

The working result sources are `1006/evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv`,
`1006/review/numerical_inputs/fresh_c_c3_minus_gfl_analysis.json`,
`1006/review/numerical_inputs/FRESH_C_ADDENDUM_ANALYSIS.json`, and
`1006/review/R1_4_FRESHC_C3_minus_GFH_posthoc_results.json`.

## Separate Fresh C identity, repeated-content, and hash gate

This gate must be reported separately from result direction. It is not the
same object set as `FRESH_CONFIRM_300`.

| Gate item | Verified finding | Manuscript consequence |
|---|---|---|
| Fresh C candidate queue | Frozen 1,000-entry queue (600 initial screen + 400 reserve), queue SHA-256 `1cee99e215aaeb2d9f8d6491928280e5fb0424bfef7b92cfd41014d49899c859`; selected UID-list SHA-256 `d93881865b6478dd31222a51c7d3ebafe44839fd5e1b76c5eb9605d3f1fdfa58` | Identify the queue/final cohort separately; do not substitute a neighboring manifest hash for these identities |
| Candidate-level repeated render | Screened UIDs `4354de9478524bedbd3a5a90414effae` and `9f2cce019c8f47cc9ed156ebd0a1b4b4` have different GLB SHA-256 values (`f7059dbbacc81dafaa6c1505d25aca8ee210f9dde891aafc540c56a5dbc4f3d8` and `4b9d15866593fdc605a8fcc31716559329f232e75411a814cdc3496f96dda31b`) but the same decoded 17-view signature (`2438eec354833a286483258152857b0d260248eda903e84d9f6f3a1fde8254e2`). Both are excluded from the final 300. Three screen candidates also matched historical decoded signatures and were excluded. | Disclose as a candidate-screen duplicate-content check; do not count the excluded pair as two Fresh C study objects |
| Selected Fresh C identity | Selected cohort manifest SHA-256 `0f2c50f0bcce6678d578bd7ec4e8931e39606045b1b105ccbdae7546556a3859`; 300/300 selected UIDs, 300 unique asset hashes, and 300 unique decoded 17-view signatures. Primary four-condition gate SHA-256 `8365d846eb8c6fdf208ae3c416f580b69e678b67ff0311d0130e6d4e58abeeac`; 1200/1200 rows. | Fresh C identity gate passes with the exclusions above; keep the selection and output hash manifests with its evidence package |
| Fresh C addendum | Same selected UID list and cohort manifest; separate addendum gate/CSV hashes; 600/600 rows for Generic Linear and LLH | Treat as a separate revision-era addendum on the same object cohort, not an independent confirmation |
| FRESH_CONFIRM_300 crosswalk | UID-list SHA-256 `b81bd142c0dbe04b6adaef1260a61c33eb1ef93b85c8a7cf5dba2244710f0673`; manifest CSV SHA-256 `e17c390beb3fddbbd399a0437185da3b9fb60e42efdf759ede79a0fe21f864c3`; zero UID overlap with Fresh C | Do not pool the sets or call them replications. The separate 299-distinct-visual-content finding belongs to FRESH_CONFIRM_300, not the Fresh C selected cohort |

The detailed Fresh C screen/freeze records are under the original evidence
workspace `1006/data/fresh_c/` (`CANDIDATE_QUEUE_LOCK.json`,
`FRESH_C_COHORT_MANIFEST.json`, `FRESH_C_COHORT_AUDIT.json`, and
`FRESH_C_INTEGRITY_GATE.json`). The paper-facing numerical authority copy
records the primary and addendum output hashes. Before section edits, the
private 1008 evidence tree should retain the small text/JSON/CSV audit records
needed to reproduce this crosswalk; the GLBs and render images need not be
uploaded for the paper-facing table.

## Structure delta from the submitted 01549

The submitted top-level order remains **Introduction → Related Work → Method →
Experiments → Limitations → Conclusion → Data availability → Declarations and
References**. The title, TCAS name, three-stage C3 definition, base pipeline,
motivation, related-work organization, and central scale/probe figures remain
recognizable. No L-TCAS framing, “implementation-aware empirical analysis”
repositioning, or 10-page rewrite structure is proposed.

The changes are limited to removing the CAI proof and unsupported FAC/human
claims; replacing the challenged qualitative and pooled headline evidence;
keeping the scale-sweep and C3-selection chain in the main paper; relocating
only the old pooled variation tables and the different-adapter retrospective
holdout table; and adding a short, explicit comparator/boundary account inside
the existing results flow. Figures 2–3, Tables 1–3, and Figure 7 remain in the
main paper pending their source-row provenance check; Fig. 4 and Fig. 6 keep
their argumentative roles with new, cleared panels.

**Review gate for this phase:** TeX body not edited. Section-by-section edits
should begin only after review of this table and the separate Fresh C identity
gate.
