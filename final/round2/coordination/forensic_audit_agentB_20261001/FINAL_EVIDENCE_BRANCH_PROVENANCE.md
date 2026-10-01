# FINAL_EVIDENCE_BRANCH_PROVENANCE.md (forensic_audit_agentB_20261001)

Audit session: Round-2 Final Forensic Audit, agent B (parallel-isolated session).
Date: 2026-10-01. Working tree shared with an active parallel audit session
(`final_audit_20261001/`); isolation rule for this session: **write only inside
`forensic_audit_agentB_20261001/`**, never pull/checkout/commit the shared tree
mid-session, and never touch the files the parallel session is editing.

## 1. Branch / commit baseline (verified 2026-10-01 ~04:05 UTC)

| item | value |
|---|---|
| current branch | `codex/round2-evidence-integrated-20261001` |
| local tip at audit start | `9388b83` ("phase-4 baking consistency report + FINAL_REVIEWER_READINESS_REPORT") |
| remote tip (`mvpainter/codex/round2-evidence-integrated-20261001`) | `5be573d` ("docs: add 01549-based manuscript narrative decision report") — **local behind 1** |
| behind-by-1 resolution | `5be573d` is a docs-only commit by the parallel session. Pull deferred to landing time to avoid mutating the shared tree under an active session. No experiment evidence is expected in `5be573d` (re-verify at landing before any conclusion depends on it). |

## 2. Evidence-branch containment (all formal experiments are pushed)

| evidence line | commit | branches containing it | remote |
|---|---|---|---|
| base (technical acceptance, paper sync) | `edfb8d0` | integrated branch history | — |
| cross-backbone validation | `4f31256` | `codex/next-review-response-20260930` (local + `mvpainter`), integrated | **pushed** |
| robustness-1 (Core-5 R0/R1) | `99d6c88` | `codex/main-backbone-robustness1-20260930` (local + `origin`), integrated | **pushed** (on `origin`, not `mvpainter`) |
| integration merge | `9f57192` (merge of `4f31256` + `99d6c88`) | integrated | **pushed** |
| merge-base of the two evidence branches | `edfb8d0` | — | — |

Conclusion: **no formal experiment evidence exists only on this server**; every
evidence commit is reachable from a pushed remote branch. The only local-only
content is (a) the parallel session's uncommitted editorial edits to files in
`final/round2/coordination/final_audit_20261001/` and (b) untracked `.codex/`,
`.trae/` — neither is experiment evidence.

## 3. Manuscript files untouched (gate precondition)

Blob SHAs verified identical to the 0930 acceptance values:

| file | blob |
|---|---|
| `final/round2/final_round2.tex` | `06b93afc910545b85b972109608ac6a8936946a8` |
| `final/round2/supplementary_round2.tex` | `d8be7f8516acb2d00bf7cc2e2ea861c3bd6562b2` |
| `final/round2/response_letter_round2.md` | `194d32d35d1e25eac28874bd0bb49db3f52537bf` |

Last paper commit: `2b788e6`. `git status` shows no modification to any of the
three manuscript files. The task-document prohibition on editing them is honored
by both this session and (as of this writing) the parallel session.

## 4. Phase-coverage boundary between the two audit sessions

Already delivered (and still being actively extended) by the parallel session in
`final_audit_20261001/`: Phase-4 metric-direction & statistics reproducibility,
Phase-8 strict-276 texture fidelity, Phase-10 bake-consistency descriptors,
Phase-12 MV-Adapter mapping sensitivity, LHL Case-B provenance forensics,
Phase-19-partial reviewer readiness, Phase-21-partial narrative recommendation,
claim–evidence matrix, evidence inventory + reproducibility manifest.

This session (agent B) owns the remaining phases, deliverables in this directory:
Phase 0 (this file), Phase 1 (intuition / large-effect / LLH effective control),
Phase 2 (visual + FG/BG metric), Phase 3 (table numerical), Phase 5 (dataset),
Phase 6 (runner), Phase 7 (R0/R1 output sensitivity), Phase 9 (Full-SSIM
provenance), Phase 11 (figure selection), Phase 13 (MVDiffusion intervention
equivalence), Phase 14 (cross-backbone claim boundary), Phase 15 (residual
budget confound), Phase 16 (failure modes), Phase 17 (number traceability),
Phase 18 (evidence authority), Phase 19 (skeptical reviewer), Phase 21
(narrative study), and the final report. Cross-references to the parallel
session's files are by path; no content duplication.

## 5. Data sources used by this audit (read-only)

- `final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv` (same-runner 4-schedule strict-276 per-object metrics)
- `layer_confirmation_20260930/layer_{llh,lhl,fixed_mean}_per_object_metrics.csv` (+ per-object GT-statistics columns)
- `core7_same_runner_completion_20261001/formal_{no_adapter,global_fixed_high}/per_object_metrics.csv`
- `main_backbone_robustness1_20260930/` (R0/R1 per-object metrics, manifests, image dirs)
- `BAKE_SEAM_AUDIT_20261001/`, `bake_layerwise_20260930/` (bake artifacts)
- MV-Adapter / MVDiffusion panels under `final/round2/` (cross-backbone deliverables)
- `final/round2/final_round2.tex` / `supplementary_round2.tex` (read-only)
