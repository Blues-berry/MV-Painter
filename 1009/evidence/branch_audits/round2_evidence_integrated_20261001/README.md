# Round-2 evidence integrated branch audit

## Source state

- Branch: `codex/round2-evidence-integrated-20261001`
- Local archived HEAD: `ce4831f40c723631e395f86268dca13afe9d07e9`
- Archived private-remote HEAD: `5a059b30eba959e69a2f36f484f06807e5c2c152` (five commits after and descended from the local HEAD)
- Merge base against main before this audit: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`
- No registered worktree or WIP archive ref exists for this branch; only committed archive content was reviewed.

The remote snapshot's five extra commits edit only `final/round2/final_round2.tex`, `final/round2/supplementary_round2.tex`, and `final/round2/response_letter_round2.md`. Those are historical paper candidates. They were reviewed against the current 1008 manuscript/reply and were not imported.

## Decision

`SELECTIVE_CONTENT_MERGE`; `FULL_MERGE_REJECTED`. The source tree deletes 253 current `1008/` paths and 353 current `1009/` paths, while adding 1,256 paths under historical `final/round2/` plus archived submissions, generated outputs, and old code. It also changes `.gitignore` to drop current evidence/generated-output exceptions and changes the wrapper's `_skip_correction` to unsafe class-level shared state without `try/finally` restoration. Main's instance-scoped behavior and precise ignore rules remain. No merge or cherry-pick was run; actual Git conflicts: `NO_CONFLICT` (0).

Core-7, the cross-backbone MVDiffusion panel, and other selected evidence from this history already have audited equivalents in main. This branch uniquely retains two MV-Adapter mapping sensitivity analyses. Their compact result rows, run configurations, protocols, source reports, and adapted CPU-only reproducers are under [`mvadapter_mapping/`](mvadapter_mapping/README.md). B′ is a budget-neutral sensitivity with a protocol commit predating the result commit. The separate M3 test changes the total residual budget; its protocol and results first appear in the same commit, so its timing cannot be independently verified. Keep the two analyses distinct and do not use M3 to claim budget-neutral mapping robustness.

The old 12-object bake/seam package and its paper claims were not selected: current main has a later native-sampler GLB audit and an explicit retirement of the older seam claim. The candidate round-2 manuscript, Supplement, and response do not replace the active C&G 1008 package.

`PAPER_IMPACT=DIRECT` because the archived branch contains manuscript and response edits. The active manuscript, Supplement, Response, figures, and canonical submission package were not changed. No LaTeX build, GPU run, push, or journal submission was performed. `SUBMISSION_APPROVED=NO`.
