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
