# Manuscript impact review

## Frozen active files

| File | SHA-256 before branch review | SHA-256 after branch decision |
|---|---|---|
| 1008/manuscript/revision_01549_restored/manuscript_1008.tex | dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4 | unchanged |
| 1008/manuscript/revision_01549_restored/Supplementary_1008.tex | 59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed | unchanged |
| 1008/submission_1008/Response_to_Reviewers_1008.md | 1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb | unchanged |

## codex/cg-01549-surgical-revision-20261008

PAPER_IMPACT=DIRECT for review: the branch and its dirty historical worktree contain direct manuscript, supplement, reviewer-response, figure, and package candidates. The active main files were not changed. The candidate clean manuscript SHA at the archived branch tip was f9be5f926f85f339b16d5504047fb51ba42cfebe; the later uncommitted worktree candidate was 0f2a26a07924d3533b406c30536bf9e1f10b4803f408e7808640e5c8f60a94b1. The active main TeX remains the frozen dd7cb9... source.

### Content adjudication

- The author-confirmed history is that 01549 was submitted after the first review round and the current R1/R2/R3 packet concerns the second round. This wording is present in the current response. The branch's review-round mapping file is byte-identical to the document already in main.
- The candidate restores the reported first-round 3AFC preference result and controlled negative FAC re-examination. Current main already includes both as historical results, with the 3AFC task distinguished from texture fidelity and the FAC archive mismatch and missing run-bound provenance disclosed.
- Current Fresh C remains a 300-object matched image-space study. Its paired C3−GFL FG-PSNR estimate is +0.522352 dB; GFH and Generic Linear remain counter-results with more favorable means than C3 on the four displayed endpoints. No old candidate wording was used to replace current paired results.
- C3 remains (1.25, 2.50, 1.25), with the Fresh C shallow value capped at 0.8. CAI optimality and selector claims remain withdrawn.
- Strict-276 temporal L-L-H remains a separately bounded follow-up; no cross-cohort or equal-dose claim was imported from this branch.
- The invalid production additive-residual bootstrap remains excluded from evidence for a cross-backbone absence claim; the current response discloses the invalid null and does not use it.
- The C1/B2 color candidates remain failed repair gates; no validated Fresh C bake, seam, or PBR result is claimed.
- The candidate package under submission_1008_final is an alternate historical package. It does not match current canonical submission_1008 and was not imported.

### Build and package checks

- Current canonical submission source files match the active manuscript, Supplement and Response hashes listed above.
- SHA256SUMS.txt contains 48 rows and all checks pass.
- Current canonical PDF hashes are recorded in the sequential report. Since no TeX, figure, table or package file was changed by this branch decision, no active-editor compile or package rebuild was triggered.
- SUBMISSION_APPROVED=NO. No journal submission was made.


## codex/cg-01549-unified-20261009

`PAPER_IMPACT=DIRECT` for review: the archived branch and its preserved detached worktree contain direct main-text and response-letter candidates plus compiled PDFs. The nine tracked dirty paths were inspected; the worktree remains unchanged. Its dirty candidate hashes were manuscript `28c2cb0d4107ef592bd3891ab7265078b97dcba5ca19a9da84cf50448799a8e1`, Supplement `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f`, and response `911019dd0eab8877f386992e348519b88479e0520458ae5b1e9cee039eb5b281`. At the archived commit the main-text SHA is `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`, Supplement SHA is `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f`, and response SHA is `47d74ac5ed14b9c3b45d41e064c1da36219d49b7e872e7e4ba6bf340e2a243d5`.

### Content adjudication

- The candidate explicitly disclaims identity between Fresh C's controlled-retraining checkpoint and the unbound historical 01549 main-table artifact. Current main already states the controlled-retraining provenance and does not claim historical identity or numerical reproduction of +0.96 dB.
- Current main retains the N=300 matched study, the registered C3−GFL FG-PSNR difference of +0.522352 dB, GFH and Generic Linear counter-results, requested/applied/residual distinctions, and image-space-only scope.
- Current main retains C3=(1.25,2.50,1.25), the Fresh C shallow native cap, strict-276 as a separate supporting analysis, and the Core-7 retrospective limitations. No valid result or corrected claim unique to this candidate was identified.
- The candidate PDFs are outputs for alternate manuscript bytes and do not match the canonical package; they were not imported. Since no main manuscript, figure, table, bibliography, or package file changed, no new editor compile or package rebuild was needed. Phase A source hashes and 48/48 package checksums remain valid.

`SUBMISSION_APPROVED=NO`. No submission was made.


## codex/cg-round2-1008-revision-20261008

`PAPER_IMPACT=DIRECT`. The archived branch contains obsolete paper/package state and an internal candidate figure; none of that content was overlaid on main. A separate reviewer-requested C3−GFH audit was re-run against the original Fresh C data at `/4T/CXY/MV-Painter/1006/data/fresh_c` without changing that source. The raw CSV hash was `6967375a66a523beeab2089a9e51fbd68b756f2a07b13439d443078bd4482cd6`; all 23 pairing/source checks passed for 300 objects and 1,200 condition rows. The selective audit bundle at `1008/audits/source_evidence/r2/c3_gfh_posthoc_20261007/` records the script, integrity checks, and seven endpoint summaries; it does not include source images, embeddings, checkpoints, cache, or per-object raw CSV.

### Result and paper reconciliation

The audit is explicitly post-hoc and reports no p-values. Its C3−GFH point estimates and endpoint directions agree with the active paper. Its Edge-SSIM interval under the recorded 10,000-resample `numpy.default_rng(20261002)` is `[-0.020803,-0.016790]`; current active manuscript/response text uses `[-0.02084,-0.01683]`. Both support the same negative Edge-SSIM difference. The alternate resampling output is retained as an audit artifact and was not substituted into the current paper. Before future paper edits, verify the active table's exact bootstrap output/provenance.

No main-text, Supplement, response, figure, bibliography, or submission-package file changed. The active TeX hashes remain the Phase A values, and the 48-file package checksum check passes. No LaTeX rebuild was needed.

`SUBMISSION_APPROVED=NO`. No journal submission was made.

## codex/paper-1006-20261006

`PAPER_IMPACT=DIRECT`: the archived source contains a 1006 manuscript, supplement, figures, alternate submission outputs, and older claim/readiness snapshots. Those paper candidates were reviewed but not overlaid. Current 1008 retains the bounded schedule/no-winner interpretation, the absence of dose-independent support, withdrawn CAI optimality, separate strict-276 provenance, bounded N=20 GLB endpoints, and no human-preference/fidelity claim. The 1006 Fresh C “not yet confirmed” note is a stale 10/06 status; the later 300-object Fresh C run and addendum are the active evidence. No supported current claim was found to need replacement.

The selected E6 bundle records a stopped development candidate with unfavorable whole-image LPIPS on all 24 development objects and no independent confirmation; it is explicitly excluded from active-paper results. The only code addition is a startup/path guard for `geotex/eval_exploration.py`; it does not alter model or metric calculations. The older class-level `_skip_correction` implementation was rejected in favor of main's instance-level, `finally`-restored behavior.

No manuscript, Supplement, response, figure, table, bibliography, PDF, or canonical package file changed. Active manuscript, Supplement, and response SHA-256 remain the Phase A values; all 48 canonical package checksums pass. No TeX rebuild, response update, or package rebuild was required. `SUBMISSION_APPROVED=NO`; no submission was made.
