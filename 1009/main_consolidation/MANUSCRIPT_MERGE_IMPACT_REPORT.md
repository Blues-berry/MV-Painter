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

## codex/cg-ltcas-narrative-convergence-20261007

`PAPER_IMPACT=DIRECT`: the source branch contains a complete 10/07 candidate manuscript, Supplement, reviewer response, generated figures, and numerical authority. Current 1008 already contains the later bounded Fresh C and Generic Linear results, endpoint-specific Fresh B/strict-276/cross-backbone limits, no CAI optimality claim, and no human/material-fidelity superiority claim. The candidate's removal of FAC differs from current 1008's limited historical treatment; that candidate wording was not used to replace the active text. No old PDF or alternate package was copied.

A 42-row, 10/07 numerical reaggregation and its four compact metric inputs were preserved under `1009/evidence/branch_audits/cg_ltc_as_narrative_20261007/`; the script reran all 42 rows and reproduced its stored output byte-for-byte. This is historical cross-validation, not a new independent experiment and not a change to current 1008 claims. The exact sanitized public-human-data disposition cited by the current claim ledger is present at its original path; it contains no participant responses and retains `PUBLIC_RAW_HUMAN_DATA=NO`.

No main text, Supplement, response, figure, table, bibliography, or canonical package file changed. Active manuscript/Supplement/response hashes remain Phase A values; all 48 package checksums pass. No LaTeX rebuild was required. `SUBMISSION_APPROVED=NO`; no submission was made.

## codex/scientific-validation-v3-20261002

`PAPER_IMPACT=DIRECT`: the branch includes scientific narrative/readiness edits and MVDiffusion evidence cited by the current 1008 paper. Current 1008 already contains the Fresh C N=300 result and bounded cross-backbone wording. The selected 75-object MVDiffusion metrics support that interface-specific description; E1/E2 are fixed-subset sensitivity results and do not establish a temporal or dose-independent schedule effect. The candidate manuscript and Supplement were not imported.

The updated readiness note summarizes a 37-valid-response human analysis with no Holm-adjusted endpoint. Its source, execution deviations, and data-governance limits remain for the separate human-study branch audit before any text change. The selected evidence package contains no participant-level rows.

The active manuscript, Supplement, and response SHA-256 remain at their Phase A values; all 48 canonical package checksums pass. No manuscript, figure, table, reference, or submission package file changed, so no editor compile or package rebuild was triggered. `SUBMISSION_APPROVED=NO`; no journal submission was made.


## codex/evidence-closure-audit-20261005

PAPER_IMPACT=DIRECT. The archived branch contains a Fresh Confirm 300 LLH−GFL failure/applicability analysis. The active manuscript search found no matching report of the specific GT-HF-energy association or Q1-to-Q3/Q4 reversal; the reviewer evidence matrix’s Fresh Confirm B descriptor entry is a separate N=150 cohort and is not a substitute. The current main C13 evidence matrix already summarizes the Fresh Confirm 300 boundary, but the archived paired data and protocol inputs were absent from the compact release.

The result was selectively added as an auditable 300-row table and CPU analysis bundle. It supports a scoped applicability limitation. Do not import the source report’s “all ten Holm tests rejected” statement: corrected reaggregation gives 9/10 and an adjusted p=0.050795 for FG-LPIPS versus coverage. The protocol timing also remains qualified by the current main retrospective family-lock status.

No main text, Supplement, response letter, figure, reference, or submission package file changed. Active SHA-256 values remain manuscript dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4, Supplement 59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed, and response 1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb; the submission directory verifies 48/48. No LaTeX rebuild was triggered because no TeX changed. SUBMISSION_APPROVED=NO.


## codex/cg-revision-evidence-closure-20261007

`PAPER_IMPACT=DIRECT`：来源包含旧 `final/` 候选论文、回复草稿及复现/证据闭合报告。它们不对应当前认证的 1008 投稿包，且其完整树会删除活动 1008 内容；因此没有将候选文本、旧图池或包文件导入 main。

与本轮科学主张有关的 C3−GFH 结果 CSV 与当前 1008 审计 CSV 字节一致；JSON 差异限于临时工作目录路径及相应来源哈希，统计 payload 相同。Fresh C 执行语义、sampler、seam、资产权利和数值权威材料已存在于 main。未发现需更新当前论文的独有结果。参与者级响应 CSV 未打开或读取，不能据该分支改变 human-study 表述。

活动主文 SHA-256 `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`、Supplement `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`、Response `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb` 均未改变；投稿目录 48/48 校验通过。无 TeX 变化，不需重新编译；`SUBMISSION_APPROVED=NO`，未投稿。


## codex/round2-final-forensic-audit-20261001

`PAPER_IMPACT=DIRECT`: the archived branch contains an old `final_round2.tex`, Supplement, response, figures, and numerical interpretations. Its old strict-276 table warnings, LHL value, object-caption audit, and gradient wording concern that historical candidate; they are not active 1008 content. The current manuscript has a separately bounded post-inspection strict-276 follow-up, and the Supplement labels Core-7 as retrospective with incomplete common-runner/input identity. Neither makes an equal-realized-dose causal or optimal-schedule claim.

The branch's 276-row LLH-versus-GFL delta source was independently compared with main's retained R0 per-object tables: all 276 object IDs and 2,760 numeric cells matched exactly. Its R0/R1 result is already covered by branch 10. The approximate additive budget/placement decomposition was not adopted because its contrasts mix endpoints and do not identify a pure allocation effect. No unique valid result was missing from main.

The active manuscript `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, Supplement `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and response `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb` are unchanged; the canonical submission package passes 48/48 checks. No active TeX changed, so there was no rebuild. `SUBMISSION_APPROVED=NO`.



## codex/final-evidence-freeze-20261001

PAPER_IMPACT=DIRECT: this archived branch supplied a unique paired-statistics file and condition-level source rows used by the current Supplement's retrospective Core-7 table. The compact row/protocol bundle and exact paired result were added under the Core-7 audit paths; no candidate manuscript or package was imported.

The 7×276 CPU reaggregation reproduced the stored aggregate, paired statistics, and row audit byte-for-byte and reconciled 42/56 earlier pair/metric rows. The displayed seven means, LLH−GFH and LLH−C3 contrasts match. C3−GFL FG-PSNR was independently recomputed from the indexed C3/GFL rows (+1.207771 dB, 95% CI [1.116967, 1.294989], 259/276). Keep Core-7 explicitly retrospective: conditions do not establish common runner or complete tensor-input identity and are not independent of Fresh C's cohort/checkpoint lineage.

No active manuscript, Supplement, figure, Response, or submission file changed. Main and Supplement source hashes remain Phase A values; the 1008 package passes 48/48 SHA checks. Built-in main compilation timed out after failing to locate the project cag.sty; built-in Supplement compilation failed at its relative figure path because standalone project assets are unavailable. There was no TeX repair attempt and no alternate PDF output. SUBMISSION_APPROVED=NO; no journal submission was made.


## codex/main-backbone-robustness1-20260930

`PAPER_IMPACT=INDIRECT`. The branch supplies an R1 strict-276 Core-5 re-realization and a 28-cell R0/R1 stability audit. Active 1008 does not state this robustness result, so it was retained as an audit record without revising or extending paper claims. The timing of the claimed pre-run protocol lock is not independently supported by Git history; preserve the result as retrospective.

The 1,380 R1 rows and saved statistics were reaggregated from compact CSV inputs. The 28-cell table matched 28/28; aggregate means matched 70/70; paired outputs matched 56/56; all seven method rankings matched across R0/R1. No new inference or GPU run was performed. Current manuscript `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, Supplement `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and Response `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb` remain unchanged. The canonical submission package verifies 48/48. No LaTeX rebuild was needed because no paper source changed. `SUBMISSION_APPROVED=NO`; no submission was made.


## codex/human-confirmatory-analysis-20261007

`PAPER_IMPACT=DIRECT`. The archived source contributes a later 40-slot, two-question human-preference analysis that could inform R1, but it does not establish a positive LLH preference claim: 37 participants were valid, all eight prespecified point estimates exceeded 0.5, and none survived the single eight-endpoint Holm correction. The largest raw p-values below .05 were GFL texture (raw .0123, Holm .0984) and GC3 texture (raw .0183, Holm .1281). The study-owner confirmatory classification was assigned after data export and is explicitly limited to the pre-specified endpoints with execution deviations. Fixed within-cell left/right orientation, the prior 0/40 schedule-match audit, missing stimulus-hash/question-order/seed records, and unresolved consent/ethics and coordinator-closeout documentation prevent a claim of full protocol adherence or a broad fidelity conclusion.

The analysis was not added to active 1008 TeX or the reviewer response. The original 01549 3AFC remains scoped to its original C3/TCAS comparison; the later study is not pooled with it. A dated audit supplement corrects the historical pre-collection status, while preserving `PUBLIC_RAW_HUMAN_DATA=NO`. The aggregate package and safe adapted reproducer are in `1009/evidence/branch_audits/human_confirmatory_analysis_20261007/`. E5 feasibility evidence is stored separately as development-only technical evidence and does not affect a paper claim.

The active manuscript, Supplement, and Response remain at SHA-256 `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; canonical submission package checks remain 48/48. No LaTeX compile was required because no TeX source changed. Consent/ethics and data-governance gates remain open; `SUBMISSION_APPROVED=NO`.


## codex/round2-evidence-integrated-20261001

`PAPER_IMPACT=DIRECT`: the archived remote-only commits add a historical Round-2 manuscript, Supplement, and response candidate. They were compared against the current C&G 1008 package and were not adopted. The branch's unique B′ and M3 MV-Adapter mapping sensitivities are preserved as bounded audit evidence only. B′ has a budget-neutral per-point mean of 1 and mixed results; its protocol commit predates result rows. M3 changes the total residual budget (mean multiplier ≈0.8065), and its protocol/results first appear in the same commit, so it is retrospective. Neither supports an architecture-general mapping claim or changes an active 1008 statement.

No active manuscript, Supplement, response, figure, bibliography, or canonical submission file changed. The manuscript, Supplement, and response remain at Phase A SHA-256 values `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`. The canonical submission package verifies 48/48. Since no active TeX changed, no LaTeX rebuild or response/package update was needed. `SUBMISSION_APPROVED=NO`; no journal submission was made.


## codex/scientific-validation-v3-20261006

`PAPER_IMPACT=DIRECT`: the archived V3 snapshot adds the A3 condition-level rows that were missing from main's evidence tree but are needed to reproduce the interaction statistics already reported in the active 1008 Supplement. The retained CSVs validate the existing FG-LPIPS and FG-PSNR Wald values exactly to reported precision. They do not support a dose-independent interaction claim: current A3 classification limits remain deep confirmation, middle approximate diagnostic, and shallow stress-only.

The active manuscript, Supplement, Response, figures, and canonical submission package did not change. Their SHA-256 values remain `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; package checks remain 48/48. No TeX changed, so no LaTeX rebuild was needed. `SUBMISSION_APPROVED=NO`; no submission was made.


## codex/cg-01549-surgical-revision-20261008 (private remote archive HEAD `dad08320625431acf439ed5bfb86c6a9252353a4`)

`PAPER_IMPACT=DIRECT`: the selected A3b per-object rows and post-lock Fresh B Generic sensitivity rows provide direct source-level support for values already presented in the active Supplement. Reaggregation preserved the existing bounded-map and post-lock sensitivity interpretations; it did not establish equal-dose causality or independent confirmation. The source's older manuscript and response candidates were reviewed and left out.

The activity manuscript, Supplement, response and canonical 1008 submission directory are unchanged. Main, Supplement, and response hashes still equal the Phase A values; the submission package verifies 48/48. Since no active TeX/figure changed, no LaTeX rebuild was required. `SUBMISSION_APPROVED=NO`; no push or journal submission occurred.


## codex/r1-fidelity-validation-48h-20261008

`PAPER_IMPACT=DIRECT`. The source contains saved-RGB CIEDE/texture reanalysis for the separate `LLH` versus `native_gfl` schedule and a GT-defined Fresh B high-texture boundary. The 150-object mean favors LLH on several endpoints, while its Q4 (`n=38`) has worse CIEDE2000 and FG-PSNR. This result concerns LLH, not the current C3 claim, and the source does not validate a color repair. It can inform a narrow response/limitation only as retrospective sensitivity evidence: the claimed protocol-lock time occurs after the source commit that first contains the protocol and outputs, and the bootstrap-seed description does not match the script/output sequence.

The current 1008 Response already says no color repair passed, but it does not report this separate Fresh B Q4 reanalysis. No claim was extended because the analysis chronology is unresolved and no C3 comparison is present. The active manuscript, Supplement, Response, figures, and canonical submission files remain unchanged at their Phase A hashes; package verification remains 48/48. No LaTeX compilation was triggered. Any later decision to cite this result should label it post hoc and preserve Fresh B/LLH scope.


## codex/cg-01549-unified-audit-f8ff09d2-20261009

`PAPER_IMPACT=DIRECT`. The archived tree contains alternate main-text, Supplement, response, reviewer matrix, source baseline and rendered package versions. The main manuscript's primary result and counter-results remain broadly aligned, but the source authority matrix upgrades Core-7 to `CONFIRMATORY` and asserts a shared runner/input identity that the current provenance audit does not establish. Its response also quotes the production additive-residual bootstrap `p=0.6523` without the current finding that its null is invalid for interaction inference. Current main's retrospective Core-7 classification and explicit invalid-test disposition were retained. The historical source's author-review PDFs are not the current package artifacts.

The branch's 42-row numerical authority, reaggregation JSON and Fresh B C3−GFH supporting CSV match the already retained `cg-ltcas-narrative-convergence` package byte-for-byte; the authenticated 01549 TeX baseline matches the current source SHA. No unique valid result required a new content commit. The old `1008` manuscript candidates and generated/compiled author-review package were not overlaid.

The active manuscript, Supplement and Response hashes remain `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`, `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`, and `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`. Canonical `1008/submission_1008/SHA256SUMS.txt` passes 48/48. No active TeX, figure, response or package file changed, so no LaTeX rebuild was needed. `SUBMISSION_APPROVED=NO`; no submission was made.
