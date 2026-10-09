# Final Main Verification

**Captured:** `2026-10-09T08:13:59Z` UTC  
**Worktree:** `/4T/MV-Painter-main`  
**Git-consolidation base commit:** `ed7471ee57351d7c8d4600d43d2c63bd44d01725`  
**Paper/package refresh commit:** `9c3e6bdcc4115cf3ac4b153c6e879439a5ca9a1f`

## Main and branch state

At this checkpoint, local `main` and private `mvpainter/main` both resolved to `9c3e6bdcc4115cf3ac4b153c6e879439a5ca9a1f`. The push was a normal fast-forward from `ed7471ee57351d7c8d4600d43d2c63bd44d01725`; no force push or reset was used.

| Check | Result |
|---|---|
| Local branches | 4: `main`, `gh-pages`, color-cast experiment, cross-backbone experiment |
| Private `mvpainter` branches | 2: `main`, `codex/next-review-response-20260930` |
| Local/remote `main` equal at checkpoint | `YES` — both `9c3e6bdcc4115cf3ac4b153c6e879439a5ca9a1f` |
| Main worktree clean after paper/package commit | `YES` |
| Other remotes pushed, pruned, or deleted | `NO` — `origin` and `upstream` untouched |
| Git unification report | `1009/main_consolidation/FINAL_GIT_UNIFICATION_REPORT.md` |
| Journal submission | `NO`; `SUBMISSION_APPROVED=NO` |

The final manuscript/package commit changed only the 1008 prose, author-review materials, refreshed submission files, integrity records, and the package assembler's CSV line-ending setting. No research data was added, moved, deleted, or copied. The approximately 394 GB ignored V3 files and other untracked/ignored evidence remain at their original paths.

## Branch and worktree disposition

- The three WIP snapshot commits remain preserved: `34d15cab5f2d4312d75e6921efb60eaad62c53c2`, `5e3e88e95c81e28200704988e4aaa7ef88239b1b`, and `ecbb246b76cccf148dfbbdfa85515b53590aa584`.
- Local branch refs were reduced from 28 to 4; five redundant private remote branches were deleted after exact SHA checks. One empty worktree was safely removed. Ten historical worktrees remain detached and Git-locked; the original `.git` metadata anchor remains detached, and the color experiment worktree stays on its retained branch.
- No full historical branch merge was appropriate because the candidates include large divergent archives. Existing reviewed selective integrations are documented in the main integration manifest; this pass added no duplicate branch content. No merge conflict occurred.
- Git's automatic maintenance printed a warning about the existing `gc.log` and unreachable loose objects. No manual `git gc` or `git prune` was run.

## Manuscript and package verification

- Active manuscript, author-review TeX, package TeX, and source-ZIP manuscript member match at SHA-256 `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`.
- Project LaTeX builds produced a 13-page manuscript, 13-page marked-up manuscript, and 11-page Supplement. Clean source-ZIP extraction rebuilt all three, and normalized extracted text matched the delivered PDFs.
- The 44-entry source archive passed CRC and excludes JSON, NPZ, checkpoints, GLB files, and raw experiment collections. The 47-row submission manifest and 48-entry checksum file passed verification.
- The editor's built-in LaTeX compiler returned `Unable to find standard directories for platform`; the repository's project scripts compiled successfully. This limitation is recorded in `1008/submission_1008/FINAL_CG_SUBMISSION_READINESS.md`.

## Report closeout note

This file records the exact main-ref comparison at the package-refresh checkpoint above. The verification closeout and regenerated package metadata were subsequently committed and pushed as a normal fast-forward. The completion handoff reports the final post-report local and remote `main` SHA.
