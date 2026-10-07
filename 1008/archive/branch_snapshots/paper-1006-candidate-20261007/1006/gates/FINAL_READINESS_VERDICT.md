# Historical readiness snapshot — updated 2026-10-06 18:10 UTC

> **Superseded on 2026-10-07.** Current status: scientific evidence freeze **YES for bounded claims**; reviewer closure **PARTIAL**; direct system upload **NO / HOLD**. The old 01549 3AFC remains complementary C3/TCAS preference evidence; the later 40-slot study is a confirmatory endpoint analysis with documented execution deviations and no Holm-supported endpoint. See [`FINAL_READINESS_VERDICT_20261007.md`](FINAL_READINESS_VERDICT_20261007.md) and [`SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md`](SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md). The historical snapshot below is retained for audit and should not be used as the current gate.

## Verdict: HOLD — Fresh C evidence is closed for image-space comparison; not cleared for final paper or system upload

### Completed continuation

E6 completed its calibration, technical checks, and all 288 frozen development rows, then stopped at the separate method-difference/value gate: full-LPIPS was adverse in 24/24 object-averaged comparisons and a substantive contribution was not established. No E6 Fresh D is launched.

Fresh C's original four-condition run passed its 300-object integrity gate and locked C3−GFL FG-PSNR analysis. The independent LLH/linear revision-era addendum then passed its own 300-object/600-row integrity gate and completed the frozen 21-test analysis. A separately coded direction/Holm audit rederived all 28 primary/addendum checks without discrepancy. The resulting comparisons support C3 over GFL on the registered foreground endpoint, while LLH, C3, and generic linear trade off by endpoint and object. No global strategy winner is claimed.

A GPU-lock handoff deadlock occurred after primary analysis but before addendum inference. The addendum had no method rows at that time. The incident, hashes, and recovery are preserved in `data/fresh_c/FRESH_C_ADDENDUM_GPU_LOCK_HANDOFF_INCIDENT_20261006.json`; after the primary process released its idle lease, the addendum ran unchanged and passed.

The final Fresh C 20-group gallery, rankings, and forest plot were generated after both integrity gates and analyses passed. The submitted 01549 files remain unchanged. See `evidence/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md` for the complete estimates, direction conventions, and figure index.

**Submission package technical readiness: NOT READY. Scientific evidence readiness: PARTIAL, not frozen.** This is not a claim that a reviewer or editor accepted the narrowed contribution. A user-supplied LLH preference export contains 40 represented slots and 37 field-valid respondents, but its task schedule and stimulus identities do not match or verify against the frozen site package. The separate sensitivity analysis has no Holm-significant endpoint and does not close human-fidelity evidence. New 24-object GLB baking has not passed a sampler/camera technical gate; strict-276 provenance remains incomplete; redistribution rights need resolution; and R2.1 contribution adequacy remains an editorial judgment.

The earlier LLH questionnaire remains archived as an unlaunched package. The supplied four-comparison export is recorded in `evidence/human_study/HUMAN_STUDY_RECEIPT_AND_DEVIATION_SENSITIVITY_ANALYSIS_20261006_ZH.md`, but it is sensitivity-only because its participant/task assignments and stimulus hashes cannot be reconciled with the frozen site package. Do not use it to claim perceptual fidelity or a C3 preference advantage. No further participant package may be distributed until its protocol, source rights, and ethics/consent records are resolved. Existing N=20 GLB-native results remain an unlit base-color supplement, not full PBR or human-fidelity evidence. No seam-improvement claim is supported.

The separate `1006` manuscript candidate compiles but is not the submitted revision. The 01549 manuscript and round-two source were not edited. This verdict is not journal submission or editor acceptance.

| Gate | State | Basis |
|---|---|---|
| Prior manuscript preservation | PASS | Hashes match the recorded entry values; see `MANUSCRIPT_PRESERVATION_AUDIT.md`. |
| Candidate narrative bounded to available evidence | PASS | No universal winner, dose-independent Layer × Window law, human-fidelity claim for LLH, seam claim, or broad transfer claim. |
| Main and supplementary LaTeX build | PASS | Candidate PDFs compile with the supplied Elsevier/CAG source format. |
| Fresh-B core temporal evidence | PASS WITH CHRONOLOGY LIMIT | 4,500/4,500 rows passed integrity; cohort is disjoint, but B's safeguard locks followed prior outcome exposure. The paper states this. |
| C3/GFL held-out comparison | PARTIAL | FRESH_CONFIRM_B provides a disjoint N=150 object cohort, but the C3−GFL comparison is post hoc after unblinding. It is supplemental evidence, not a registered confirmation. |
| Fresh C3/GFL follow-up | PASS — REVISION-ERA CONFIRMATION WITH CHRONOLOGY LIMIT | Frozen N=300, 1200/1200 rows; identity, inputs, caps, predictions, and residual logs passed. C3−GFL FG-PSNR = +0.522 dB, 95% object bootstrap CI [+0.404,+0.641], primary paired p=5.70e−16; FG-LPIPS = −0.005345 (lower favors C3). This is a new revision-era cohort, not an original-preregistration replication. |
| Historical strategy sign and Holm audit | PASS — HISTORICAL ONLY | All 19 archived pairwise JSONs reproduced from source rows; 5 stored Holm families/28 tests recomputed. B3 shard-count disagreement remains a provenance warning; the audit adds no new cohort or ranking across metrics. |
| Revision-era LLH/linear addendum | PASS WITH ENDPOINT/HETEROGENEITY LIMIT | N=300, 600/600 rows; same input identity and cap semantics. Six primary tests over LLH−C3, LLH−linear, C3−linear passed the separate Holm audit. LLH−linear FG-LPIPS is +0.001372 (95% CI [+0.000762,+0.002081], Holm p=1.14e−4), favoring generic linear; FG-PSNR interval crosses zero and no equivalence margin exists. |
| Final comparison gallery | PASS — AFTER BOTH GATES | Twenty unique groups across four locked comparisons; separate endpoint/multiplicity rankings, cohort forest plot, all-object deltas and asset hashes. No per-object p-values or cross-metric winner score. |
| Claim/evidence authority ledger | PASS — E0 BOOKKEEPING ONLY | Nineteen claims link to 169 hash-checked sources, including the protocol-deviation human sensitivity record. This bookkeeping update does not freeze science or close reviewer judgments. |
| Dose-normalized Layer × Window mechanism | NOT ESTABLISHED | E5 passed numerical implementation checks, but at alpha=0.005 the shallow group exceeded its native cap on 30.4% of wrapper steps. The pilot used six reused development objects and collected no quality metrics. Keep interaction claims conditional on the measured profile and cap. |
| strict-276 C3 provenance | PARTIAL | Seven endpoints are paired and reported, including the GC3/GFH trade-off, but runner identity and complete legacy input-tensor hashes are unavailable. |
| Human/perceptual fidelity | OPEN / SENSITIVITY ONLY; CLAIM WITHDRAWN | The supplied export yields 37 field-valid respondents, but 0/40 assignments match the frozen schedule and 96/96 object-comparison cells keep one fixed left/right orientation across participants. No endpoint survives Holm correction; asset hashes and closure records are missing. The candidate makes no human-preference or human-fidelity claim. |
| Three-dimensional appearance | BOUNDED HISTORY; NEW PANEL OPEN | Existing GLB-native result covers N=20 stored outputs and 11 unseen views, unlit base-color only. An input-only 24-object, UV-complete subset is frozen by first-eligible cohort order; it is not stratified or independent. The existing project bake path re-UVs through xatlas, which would change 9/24 selected assets' out-of-range native UV behavior; a preserving bake implementation and camera/sampler gate do not exist. CC BY tags do not clear attribution or redistribution. No seam or full-PBR claim. See `evidence/protocols/FRESH_C_GLB_BAKE_FEASIBILITY_AUDIT_20261006.md`. |
| Cross-interface generalization | BOUNDED | MV-Adapter and MVDiffusion are separately reported interface-boundary results, not matched causal architecture tests. |
| Novelty and contribution sufficiency | BLOCKING JUDGMENT | Scheduled Style Injection is close prior work. The narrowed MVPainter-specific empirical contribution may still be judged too incremental; additional wording cannot settle that editorial question. |
| Asset redistribution | OPEN / PUBLIC BRANCH NOT LICENSE-CLEARED | Direct official API recheck returned an empty `license` object for Panel 02 and HTTP 404 for Panel 05. The public task branch contains contact-sheet and supplement derivatives. Obtain source-level terms/permission or remove and rebuild all affected derivatives before treating any branch/package as release-ready. See `licenses/ASSET_SOURCE_LICENSE_RECHECK_20261006.json`. |
| Portable paper-wide rebuild | PARTIAL — COMPACT CHECKOUT REBUILD PASS | A fresh sparse checkout of published commit `00c4891` passed all 401 package checksums and rebuilt the included analyses, tables/figures, and both LaTeX PDFs. Extracted PDF text matched byte-for-byte; five regenerated figures rasterized identically at 150 dpi. Omitted historic prediction/residual/render payloads still prevent end-to-end regeneration of every GPU result. |
| Final reviewer response and submission metadata | PARTIAL | A point-by-point candidate with page/line references exists; final author review, title-page metadata, and a post-freeze pagination check remain. No editor decision is represented. |

## Why this does not pass the upload gate

Fresh C materially strengthens the C3−GFL image-space evidence, but the named
comparisons do not support one schedule across both endpoints and typical
objects. LLH−C3 foreground PSNR has a positive cohort mean while its median is
negative and fewer than half of objects favor LLH; its full-image endpoints
include adverse changes. LLH−linear FG-PSNR is inconclusive, while FG-LPIPS
favors linear. These estimates describe the tested cohort and cap profiles, not
a dose-independent layer/time mechanism. Historical B, strict-276, and N=20
GLB results keep their separate cohort/provenance limits.

The narrowed text must still answer R1 with direct perceptual evidence or an
explicitly accepted scope reduction. The supplied human export is not adequate
to close that gate because its assignment/stimulus provenance does not match
the lock, and its eight endpoints have no Holm-significant result. The new 3D
endpoint must not be claimed until the fixed-camera bake and native glTF sampler
pass integrity. R2.1 remains a venue judgment after close prior work. The public
task branch already contains two license-uncertain visual derivatives and is
not a cleared release.

## Release decision

`CANDIDATE_DRAFT_COMPILES=YES`

`CLAIM_SCOPE_BOUNDED=YES`

`SCIENTIFIC_EVIDENCE_FREEZE=NO`

`REVIEWER_CLOSURE=PARTIAL`

`DIRECT_SYSTEM_UPLOAD=NO`

No journal system action has been taken. The remaining sequence is: complete a
valid 24-object GLB bake/render or retain the bounded historic N=20 endpoint;
reconcile the supplied human export to a pre-collection assignment/stimulus
package or keep the human claim withdrawn; document rights and ethics; update
the manuscript and point-by-point response after evidence freeze; then rebuild
the package and rerun the page/line audit. R2.1 remains explicitly open for
venue-level judgment.

## Closeout evidence index

The final image-space evidence packet and every primary/addendum artifact are
indexed in `evidence/audits/FRESH_C_EVIDENCE_PACKET_INDEX_20261006.md`. The
condition-level authority ledger covers 243 records in 26 run directories; its
claim-level companion tracks the image-space claims separately from the new
protocol-deviation human sensitivity record. The 28-check direction audit
reports `SIGN_DIRECTION_ERROR=0`, and the complete
six-method index covers 1,800 method/object rows. The reviewer action map is
`gates/REVIEWER_CLAIM_IMPACT_MATRIX_20261006.md`; novelty remains an interim
`OPEN / VENUE_RISK` judgment in
`evidence/audits/next_stage_20261006/NOVELTY_AUDIT_POST_FRESH_C_20261006_ZH.md`.
The explicit science-freeze decision is in
`gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261006.md`. These closeout artifacts
do not change the HOLD decision, the open rights/3D/human limits, or the
01549 manuscript freeze.
