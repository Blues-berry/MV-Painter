# Reviewer-blocker remediation plan — 2026-10-06

This plan separates problems that can be resolved with evidence already
authorized in this revision from those that need user data, a new method study,
or editorial acceptance. It does not authorize manuscript edits before the
scientific evidence freeze. The submitted 01549 source and PDF remain
preserved.

| Gate | What currently blocks closure | Action in progress or feasible remedy | Decision rule and honest fallback |
|---|---|---|---|
| R1.2 — held-out C3 evidence | strict-276 is retrospective and has an incomplete common-runner/input-hash chain; Fresh B's C3−GFL pair was selected after unblinding. | Finish the frozen Fresh C asset screen, then run only the four locked conditions (`no_adapter`, `native_gfl`, `native_gfh`, `native_gc3`) on the separately sourced cohort. Require the full input, row, cap-trace, prediction, and residual integrity gate before analysis. | If integrity passes, report a revision-era prospective C3 comparison with endpoint-specific estimates and intervals. If N<276 or integrity fails, stop and mark R1.2 partial. If C3 does not improve the registered endpoint, withdraw C3 superiority; do not change schedule, endpoint, or cohort. This cannot restore the original preregistration. |
| R1.1/R1.3 — perceptual fidelity, unseen views, seams | No current LLH human responses; stored GLB evidence is N=20, base-color only, mixed endpoints, and four no-UV exclusions; no valid seam result. | Keep the frozen human-response guide ready for the dataset the user will provide. It requires at least 36 valid responses from 40 locked slots and the two-way participant/object bootstrap with the eight-endpoint Holm family. Separately retain only the supported GLB unseen-view endpoint. | With valid human data, analyze the frozen pair and report that endpoint only; it does not establish unseen-view or material fidelity. Without data, remove LLH perceptual claims and state that human fidelity and seams remain unverified. Do not convert image variation or 2D metrics into fidelity evidence. |
| R2.1 — contribution adequacy | Scheduled Style Injection directly precedes generic depth/time scheduling; the remaining pipeline-specific characterization may be judged incremental. | Add the direct prior-work comparison and retain only the concrete MVPainter residual/cap path, object heterogeneity, and measured endpoint boundaries. E5 is closed as a technical feasibility pilot: shallow cap overrun prevents the frozen three-layer dose match, so it cannot support an equal-dose mechanism. | Keep R2.1 as a blocking venue judgment unless a genuinely new method is separately defined, shown feasible on development data, frozen before outcomes, and tested on an untouched cohort. Do not add a post-hoc cap-aware method to this revision or claim that more statistical significance resolves novelty. If no such study is justified, disclose the venue risk and consider a venue whose contribution criteria fit a bounded empirical evaluation. |
| R2.2 — CAI and post-hoc optimum | No independent prospective evidence that CAI predicts the best schedule. | Remove CAI-derived optimum language; if retained, label it descriptive and post hoc. | Close only the overclaim, not the existence of a predictive rule. |
| R2.3 — cross-backbone transfer | MV-Adapter and MVDiffusion use different conditioning interfaces and intervention semantics. | Report both as separate interface-boundary observations with their own cohort and endpoints. | Withdraw transfer/generalization and architecture-causal claims; no pooled effect. |
| R1.5 — reproducibility and provenance | Historical GFL/GC3 input hashes are incomplete; paper-wide reconstruction and a portable clean-clone rebuild are partial. | Preserve each campaign's source/hash chain; after evidence freeze rebuild every retained figure/table from the package, check a clean clone, and remove claims whose raw inputs cannot be made available. | Do not claim the historic arms share an identical runner or full bit-level realization. If an artifact cannot be released or rebuilt, disclose that limit or omit the dependent claim. |
| Asset redistribution | Two images in the existing 24-object panel have only snapshot-level licensing support; the repository is public and the current package branch includes the rendered panel and compiled supplement. | Before any final public or submission release, verify source terms or remove/rebuild every derivative using those assets. Keep attribution records. Raw Fresh C GLBs/renders stay local pending individual rights review. | Do not mark the package license-cleared based on attribution alone. Sketchfab's official guidelines say a model's license and attribution follow it wherever used and call for creator and model-link attribution ([official guidelines](https://sketchfab.com/developers/download-api/guidelines)). |
| Human data / final author decisions | User will provide responses later; final authorship/title-page metadata and final response review are not supplied. | Keep the ingest template and locked analysis guide in `1006`; validate a supplied file without contacting participants. At freeze, compare each response claim against the matching endpoint and rebuild page/line references after final pagination. | Until data and final author metadata arrive, keep human and submission gates open. No participant outreach or journal-system action is authorized by this plan. |

## Current execution state

- Fresh C: 600/600 source assets downloaded; 594 pass basic geometry and there
  are no byte-identical matches among 1,965 locally available historical GLBs.
  Seventeen-view rendering, depth conversion, exact decoded-pixel duplicate
  checks, coverage checks, and cohort freeze are in progress. No method output
  has been generated.
- E5: numerical implementation passed, but no quality metric was computed and
  the shallow cap was exceeded at every frozen test magnitude. The scientific
  dose-independent mechanism claim is therefore withdrawn for this revision.
- Manuscript: the 01549 source/PDF and the 1006 manuscript candidate are not
  being edited while evidence is still open.
- Readiness: **HOLD**. The experiment can improve R1.2; it cannot close R1.1,
  R2.1, source-level asset terms, or the clean-clone/submission gates by itself.
