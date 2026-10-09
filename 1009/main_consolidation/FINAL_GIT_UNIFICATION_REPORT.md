# Final Git Unification Report

Date: 2026-10-09  
Authoritative worktree: `/4T/MV-Painter-main`  
Authoritative branch and permitted push target: `main` / `mvpainter`

## Result

The repository is back to one normal development branch, `main`. The retained local branches are `main`, `gh-pages`, `codex/r1-color-cast-repair-v2-20261009`, and `codex/next-review-response-20260930`. The latter is the protected cross-backbone results branch. No experiment process was running during the check; both experiment refs were retained as requested.

| Measure | Before cleanup | After cleanup |
|---|---:|---:|
| Local branch refs | 28 | 4 |
| Private `mvpainter` branch refs | 7 | 2 (`main` and `codex/next-review-response-20260930`) |
| Registered worktrees | 14 | 13 |
| Ordinary local branches removed | — | 24 |
| Private remote branches removed | — | 5 |
| Worktrees safely removed | — | 1 |

All five remote deletions were preceded by an exact `ls-remote` SHA comparison against a local archive ref. `origin` and `upstream` were not pushed to, pruned, or deleted. Only `mvpainter` was fetched/pruned. The private `main` was not reset or force-pushed.

## WIP commits retained

Each commit contains only the index that was already staged in its original worktree. Its tree was checked against the pre-commit index tree. The original pre-WIP HEADs and the new commit tips are both recoverable locally.

| Branch at snapshot | Original HEAD | WIP commit | Files |
|---|---|---|---:|
| `codex/paper-1006-20261006` | `a9ac1459b3d6d4312dab8dbd17534403133fb922` | `34d15cab5f2d4312d75e6921efb60eaad62c53c2` | 26 |
| `codex/cg-round2-1008-revision-20261008` | `3e592037d5fdf1c01a5052780e6203ed3d373846` | `5e3e88e95c81e28200704988e4aaa7ef88239b1b` | 27 |
| `codex/cg-ltcas-narrative-convergence-20261007` | `bf1dc3d41edd597421c067a972c82abfb4b8fdf7` | `ecbb246b76cccf148dfbbdfa85515b53590aa584` | 31 |

The staged historical deletions in these WIP commits were not replayed on `main`. No blanket `git add -A` was used. The other dirty worktrees were detached without changing their tracked or untracked status; their files remain at their original paths and their status/diff snapshots are in the local archive.

## Branch integration decisions

No whole historical branch was merged in this pass, and no merge commit was manufactured. The historical branches have large, divergent trees containing old submissions, archived outputs, and obsolete runners. Direct tree comparisons showed tens of thousands of branch-only paths in some candidates, so a full merge would risk replacing or deleting current main content.

The prior main consolidation remains the source of selective integration: its existing manifest records 58 selected files already in `main` (53 color-evidence/protocol files and 5 strict-276/V3 files). The current main also contains the reviewed cross-backbone analysis and selected scripts, recorded as `MERGED_TO_MAIN` in `MAIN_INTEGRATION_COPY_MANIFEST.csv`. This pass found no additional validated source or result that needed a second copy. The two preserved experiment branches remain recoverable and were not included in a main merge.

Specific exclusions:

- The old paper branches contain alternate TeX, response letters, build products, and historical submission files. They were not used to overwrite the current 1008 source. Their uncommitted candidates remain intact in locked historical worktrees and in the archived diff/status manifests for the next, main-only paper revision.
- The color-repair handoff reports that the C1/B2 gates did not validate a repair. No color-repair implementation was added to the default inference path. The current color branch and its local research outputs remain intact.
- An older GeoTex branch version uses a class-global `_skip_correction` flag and resets it without `try/finally`; the current main implementation keeps instance-local state with cleanup in `finally`. The older implementation was excluded to avoid shared-request state leakage.
- No source-level merge conflict occurred because no full branch merge was attempted. The implementation divergence above was resolved by retaining the safer main implementation.

## Generated output rules

Four path-specific rules were added to the main `.gitignore` for:

- `1008/engineering/color_failure/raw_rgb/`
- `1008/engineering/color_failure/masks/`
- `1008/engineering/color_failure/runs/`
- `1008/engineering/color_failure/final_closure/evidence_rgb/`

These paths match generated-file examples. Protocol JSON, result CSV, report PDF, and other useful research records remain trackable. No currently tracked file was found under those four output paths, so no `git rm --cached` action was needed. No global `*.json`, `*.csv`, or `*.pdf` rule was added.

## Worktree disposition and data

One worktree, `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence`, was removed with ordinary `git worktree remove` after confirming it had no tracked, untracked, or ignored files. Ten historical worktrees remain detached and Git-locked with a reason not to use or clean them. The original repository metadata anchor `/4T/CXY/MV-Painter` is an eleventh retained historical worktree; Git cannot lock it because it contains the common `.git` directory, so it is detached and designated historical-only. `/4T/CXY/MV-Painter-r1color` remains attached to its retained experiment branch. `/4T/MV-Painter-main` remains the only ordinary development worktree.

The roughly 394 GB ignored V3 data and all other local untracked/ignored research files remain in their original worktrees. No full data copy, file move, cleanup, or all-data hash pass was run. The archive contains Git patches, status/path manifests, prior hash manifests, stash patches, and an empty copy dry-run destination; it contains no copied worktree research files. See `FINAL_LOCAL_ARCHIVE_AND_RECOVERY_INDEX.md` and `FINAL_BRANCH_AND_WORKTREE_DISPOSITION.csv`.

## Verification and submission state

- `.gitignore` samples: all four generated directories are ignored; representative protocol JSON, summary CSV, and PDF paths are not ignored.
- `git diff --check`: passed.
- No application source code was changed in this Git pass, so no model/runtime test suite was needed.
- The current activity manuscript, Supplement, response letter, submission PDFs, and LaTeX source ZIP matched their latest SHA-256 entries in `1008/MANUSCRIPT_REVISION_INTEGRITY.csv` at the Git-phase checkpoint.
- Main-to-private-remote equality and the final pushed SHA are recorded in `FINAL_MAIN_VERIFICATION.md` and the final handoff.
- `SUBMISSION_APPROVED = NO`; no journal submission was performed.
