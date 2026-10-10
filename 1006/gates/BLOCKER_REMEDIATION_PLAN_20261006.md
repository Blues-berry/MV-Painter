# Reviewer-blocker remediation and current disposition — updated 2026-10-06 17:10 UTC

> **Human-gate update — 2026-10-07:** no additional human collection is required for the current bounded evidence freeze. The original 01549 3AFC is complementary C3/TCAS preference evidence; the uploaded 40-slot study is analyzed as a prespecified confirmatory endpoint family with documented execution deviations. Exact assignment/hash recovery is not a prerequisite to reporting it, but assignment, stimulus, closeout, and consent/ethics limitations remain explicit. See `../evidence/human_study/HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md` and `SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md`. Other delivery and R2.1 items remain open.

This plan separates problems that can be resolved with evidence already
authorized in this revision from those that need user data, a new method study,
or editorial acceptance. It does not authorize manuscript edits before the
scientific evidence freeze. The submitted 01549 source and PDF remain
preserved.

| Gate | What currently blocks closure | Action in progress or feasible remedy | Decision rule and honest fallback |
|---|---|---|---|
| R1.2 — held-out C3 evidence | strict-276 is retrospective and has an incomplete common-runner/input-hash chain; Fresh B's C3−GFL pair was selected after unblinding. | **Completed:** Fresh C ran the four locked conditions (`no_adapter`, `native_gfl`, `native_gfh`, `native_gc3`) on frozen N=300. The full input, row, cap-trace, prediction, residual, and finite-metric gate passed. The separately frozen LLH/linear addendum also passed and was audited independently. | Report C3−GFL FG-PSNR as a revision-era cohort comparison (+0.522 dB; 95% CI [+0.404,+0.641]), with the chronology limit and object heterogeneity. Do not call this an original-preregistration replication. Retain all endpoint trade-offs; no cohort or strategy changes. |
| R1.1/R1.3 — perceptual fidelity, unseen views, seams | No genuine human responses; stored GLB evidence is N=20, base-color only, mixed endpoints, and four no-UV exclusions; no valid seam result. | Keep the response guide ready for user-supplied data. The planned study requires 36 valid responses from 40 locked slots and participant/object two-way bootstrap with eight-endpoint Holm. The 24-object follow-up list is first-eligible by cohort order, not stratified or independent. Retain the existing GLB result only within its unlit base-color scope. | Analyze only genuine responses after the final stimulus/assignment lock, source-rights checks, and ethics/consent record. Without those, remove LLH perceptual claims and keep human fidelity and seams unverified. Human 2D results do not establish unseen-view or material fidelity. |
| R2.1 — contribution adequacy | Scheduled Style Injection directly studies layer/timestep scheduling and geometric ControlNet strength scheduling; its controlled configuration/metric/backbone sweep is more extensive than the current method evidence. The remaining MVPainter-specific characterization may still be judged incremental. | The primary-source comparison is complete in `evidence/audits/REVISION_STRATEGY_COMPARATIVE_EVIDENCE_20261006_ZH.md` and linked from C13 in the authority ledger. Retain only the concrete MVPainter residual/cap path, object heterogeneity, and measured endpoint boundaries. E5 is closed as a technical feasibility pilot: shallow cap overrun prevents the frozen three-layer dose match, so it cannot support an equal-dose mechanism. | Keep R2.1 as a blocking venue judgment unless a genuinely new method is separately defined, shown feasible on development data, frozen before outcomes, and tested on an untouched cohort. Do not add a post-hoc cap-aware method to this revision or claim that more statistical significance resolves novelty. If no such study is justified, disclose the venue risk and consider a venue whose contribution criteria fit a bounded empirical evaluation. |
| R2.2 — CAI and post-hoc optimum | No independent prospective evidence that CAI predicts the best schedule. | Remove CAI-derived optimum language; if retained, label it descriptive and post hoc. | Close only the overclaim, not the existence of a predictive rule. |
| R2.3 — cross-backbone transfer | MV-Adapter and MVDiffusion use different conditioning interfaces and intervention semantics. | Report both as separate interface-boundary observations with their own cohort and endpoints. | Withdraw transfer/generalization and architecture-causal claims; no pooled effect. |
| R1.5 — reproducibility and provenance | Historical GFL/GC3 input hashes are incomplete and some historic prediction/residual/render payloads are absent. | A fresh sparse checkout of published commit `00c4891` now passes all 401 package checksums and rebuilds included analyses, tables/figures, and LaTeX. Before evidence freeze, inventory which historic claims depend on omitted outputs; supply permitted raw payloads and regenerate where feasible, otherwise remove dependent claims and disclose the campaign-level boundary. | Compact package rebuild is PASS; full historic GPU-generation reconstruction remains PARTIAL. Do not claim historic arms share an identical runner or full bit-level realization. |
| Asset redistribution | Two images in the existing 24-object panel have only snapshot-level licensing support; the public branch includes their contact-sheet and compiled-supplement derivatives. | Official API recheck at 08:58 UTC returned an empty `license` object for Panel 02 and HTTP 404 for Panel 05. Preserve response hashes in `licenses/ASSET_SOURCE_LICENSE_RECHECK_20261006.json`. Before final release, obtain source terms or remove/rebuild every derivative using those assets. Keep attribution records. Raw Fresh C GLBs/renders stay local pending individual rights review. | Rights remain OPEN; API absence is not permission. If source terms cannot be confirmed, remove affected images and derivatives from the release package. |
| Human data / final author decisions | User will provide responses later; final authorship/title-page metadata and final response review are not supplied. | Keep the ingest template and locked analysis guide in `1006`; validate a supplied file without contacting participants. At freeze, compare each response claim against the matching endpoint and rebuild page/line references after final pagination. | Until data and final author metadata arrive, keep human and submission gates open. No participant outreach or journal-system action is authorized by this plan. |

## Current execution state

- Fresh C image-space stage: primary N=300, 1,200/1,200 rows; LLH/linear
  addendum N=300, 600/600 rows. Both independent integrity gates passed. The
  direction/Holm audit passed 28/28 checks. Twenty comparison groups,
  endpoint-specific rankings, cohort deltas, and a forest plot are indexed.
  Full estimates and limits are in `evidence/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md`.
- Fresh C orchestration: a GPU-lock handoff incident occurred before addendum
  inference and is preserved. The unchanged addendum then completed. The stale
  wait state is archived and transparently reconciled in
  `data/fresh_c/FRESH_C_CLOSURE_FINAL_RECONCILIATION_20261006.json`.
- GLB follow-up: 24 UV-eligible, allowlist-tagged assets are frozen using the
  first-eligible cohort-order rule. This is same-cohort and non-stratified;
  source attribution remains pending. No new bake/camera/sampler analysis has
  passed. The current bake entry rewrites UVs through xatlas and is therefore
  incompatible with preserving nine selected assets' out-of-range native UV
  coordinates. Do not promote this list to independent 3D confirmation or run
  the old bake path as if it were the frozen panel.
- Portable rebuild: exact public commit `00c4891` passed 401/401 recorded
  checksums in a fresh sparse checkout. Compact analyses, tables/figures, and
  both LaTeX PDFs rebuilt; full historical generation reconstruction remains
  partial because selected raw output payloads are not included.
- Asset rights: direct source API recheck did not resolve either
  snapshot-only model. Panel 02 has no license field; Panel 05 is unavailable.
  Rights remain an explicit release blocker until source terms are confirmed
  or derivatives are removed and rebuilt.
- E5: numerical implementation passed, but no quality metric was computed and
  the shallow cap was exceeded at every frozen test magnitude. The scientific
  dose-independent mechanism claim is therefore withdrawn for this revision.
- Manuscript: the 01549 source/PDF and the 1006 manuscript candidate are not
  being edited while evidence is still open.
- Readiness: **HOLD**. Fresh C materially strengthens the bounded R1.2
  image-space evidence, but it cannot close human fidelity, new GLB/seam
  validation, R2.1 contribution adequacy, source-level asset terms, or the
  final submission gates by itself. The 01549 manuscript remains frozen until
  the evidence disposition is complete.

Current closeout references: condition-level provenance ledger at
`../evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`; Fresh C
packet index at `../evidence/audits/FRESH_C_EVIDENCE_PACKET_INDEX_20261006.md`;
linear/sign audit at `../evidence/audits/DIRECTION_AND_SIGN_AUDIT_20261006.md`;
and reviewer action matrix at `REVIEWER_CLAIM_IMPACT_MATRIX_20261006.md`. The
current final decision remains in `FINAL_READINESS_VERDICT.md`.
