# Branch-unique work and live worktree report

**Snapshot:** 2026-10-09T06:06:08Z
**Intake main:** `7397fca31998901ca6048375f0e96ffb4a42e5e7`  
**Registered worktrees:** 14  
**Local branch refs:** 28  
**Hashed non-main status paths:** 1,636
**Stashes audited and retained:** 2.

The branch table reports commit reachability and changed-path counts against intake main. It is a scope index, not a wholesale merge recommendation. Prior copy history remains in `MERGED_BRANCH_FILE_CORRESPONDENCE.csv` and `MAIN_INTEGRATION_COPY_MANIFEST.csv`.

| Local branch | HEAD | Main-only commits | Branch-only commits | Paths from merge base |
|---|---|---:|---:|---:|
| `backup/geotex-before-cleanup` | `61f628bb6a13` | 23 | 0 | 0 |
| `codex/cg-01549-surgical-revision-20261008` | `06cac81de239` | 9 | 165 | 34573 |
| `codex/cg-01549-surgical-upload-20261008` | `dad083206254` | 9 | 155 | 27142 |
| `codex/cg-01549-unified-20261009` | `284cd252b8b3` | 9 | 166 | 27178 |
| `codex/cg-01549-unified-audit-f8ff09d2-20261009` | `f8ff09d26f82` | 9 | 179 | 34610 |
| `codex/cg-ltcas-narrative-convergence-20261007` | `bf1dc3d41edd` | 9 | 141 | 2751 |
| `codex/cg-revision-evidence-closure-20261007` | `d59c4606ad54` | 9 | 131 | 2728 |
| `codex/cg-round2-1008-public-sanitized-20261008` | `1f2448358537` | 9 | 131 | 26950 |
| `codex/cg-round2-1008-revision-20261008` | `3e592037d5fd` | 9 | 141 | 27058 |
| `codex/evidence-closure-audit-20261005` | `7e659c7e5695` | 9 | 161 | 42244 |
| `codex/final-evidence-freeze-20261001` | `29b3a0a6ec00` | 9 | 125 | 2081 |
| `codex/human-confirmatory-analysis-20261007` | `86292c8b5822` | 9 | 145 | 3088 |
| `codex/main-backbone-robustness1-20260930` | `99d6c88f2805` | 9 | 102 | 1785 |
| `codex/next-review-response-20260930` | `4f312566ed42` | 9 | 102 | 1795 |
| `codex/paper-1006-20261006` | `a9ac1459b3d6` | 9 | 143 | 3067 |
| `codex/public-round2-evidence` | `78c871ffb4a9` | 9 | 80 | 1663 |
| `codex/r1-color-cast-repair-v2-20261009` | `bd9d436c2f13` | 9 | 148 | 3906 |
| `codex/r1-color-root-cause-20261008` | `7311b9446733` | 9 | 142 | 3734 |
| `codex/r1-color-root-cause-20261008-local-history` | `5fb32c1676a6` | 9 | 164 | 42513 |
| `codex/r1-fidelity-validation-48h-20261008` | `46e741180a2f` | 9 | 146 | 3798 |
| `codex/round2-evidence-integrated-20261001` | `ce4831f40c72` | 9 | 118 | 2061 |
| `codex/round2-final-forensic-audit-20261001` | `450389fb8232` | 9 | 119 | 2061 |
| `codex/scientific-validation-v3-20261002` | `5c2c8829a1e1` | 9 | 163 | 42279 |
| `codex/scientific-validation-v3-20261006` | `12da08c7056f` | 9 | 126 | 2606 |
| `gh-pages` | `5f203f83e818` | 62 | 6 | 1201 |
| `main` | `7397fca31998` | 0 | 0 | 0 |
| `new0528` | `3f5202cf5ab0` | 40 | 0 | 0 |
| `new0529` | `d9379fe93e51` | 9 | 79 | 711 |

## Current registered worktrees (pre-commit snapshot)

| Path | Branch / state | HEAD | Staged | Unstaged | Untracked | Untracked bytes | Staged deletes | Unstaged deletes | Disposition |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `/4T/CXY/MV-Painter` | `codex/scientific-validation-v3-20261002` | `5c2c8829a1e1` | 0 | 30 | 581 | 236,808,554 | 0 | 26 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | `codex/cg-01549-surgical-revision-20261008` | `06cac81de239` | 0 | 53 | 18 | 28,868,139 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-1006-wt` | `codex/paper-1006-20261006` | `a9ac1459b3d6` | 26 | 0 | 0 | 0 | 25 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-1008` | `codex/cg-round2-1008-revision-20261008` | `3e592037d5fd` | 27 | 0 | 1 | 776,861 | 22 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence` | `codex/cg-ltcas-narrative-convergence-20261007` | `bf1dc3d41edd` | 31 | 0 | 0 | 0 | 25 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-r1color` | `codex/r1-color-cast-repair-v2-20261009` | `bd9d436c2f13` | 0 | 6 | 852 | 164,150,269 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/MV-Painter-01549-unified-20261009` | `codex/cg-01549-unified-20261009` | `284cd252b8b3` | 0 | 9 | 0 | 0 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/MV-Painter-main` | `main` | `7397fca31998` | 0 | 42 | 9 | 1,485,202 | 0 | 0 | ACTIVE_MAIN |
| `/4T/tmp/01549-clean-checkout-20261008` | `DETACHED` | `fb0b24cba203` | 0 | 2 | 0 | 0 | 0 | 0 | PRESERVE_DIRTY |
| `/tmp/MV-Painter-evidence-closure` | `codex/evidence-closure-audit-20261005` | `7e659c7e5695` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/MV-Painter-human-confirmatory-20261007` | `codex/human-confirmatory-analysis-20261007` | `86292c8b5822` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/MVPainter-cg01549-private-upload` | `codex/cg-01549-surgical-upload-20261008` | `dad083206254` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/cg-closure-clean-audit` | `DETACHED` | `e267b2d59bbb` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/mvpainter-cg-evidence-closure` | `codex/cg-revision-evidence-closure-20261007` | `d59c4606ad54` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |

## Concurrent r1color branch publication

The retained r1color branch is at `bd9d436c2f13c00de36a64cb42e807da558ef5c4`; a concurrent workflow pushed the same head to `origin/codex/r1-color-cast-repair-v2-20261009`. Its 108 committed campaign files remain outside `mvpainter/main` and are recorded as `NEEDS_AUTHOR_DECISION`. This task did not publish to that remote or alter the branch. The 76 ignored Phase B/C image intermediates remain local and checksum-verified. The subsequent B2 proposal had three concurrent launch attempts; each stopped before diffusion generation, with zero calls and zero prediction PNGs. Attempt 03 loaded the model and LPIPS evaluator before stopping at the embedding-shape guard; no Fresh B predictions or metrics were read.

## Individual disposition

The ledger records 1,636 current non-main status paths, 108 committed r1color files, 76 verified ignored outputs, and 6 stash file changes. Disposition counts: ALREADY_PRESENT=26, ARCHIVED_LOCAL=1,604, MERGED_MAIN=1, NEEDS_AUTHOR_DECISION=119, SUPERSEDED=76. Source trees and stash refs were preserved.

- `ALREADY_PRESENT` rows match intake-main counterparts; the accurate unified Response passage informed the rewritten response and is `MERGED_MAIN`.
- Older TeX/PDF/build products remain superseded; worktree-local deletions remain local.
- Color-cast evidence supports a partial causal pathway, not a validated repair. The C1 candidate failed its locked visual gate; the B2 intervention has no generated result.
- `MAIN_SINGLE_EDITING_AUTHORITY=PARTIAL`: `/4T/MV-Painter-main` is the only designated daily worktree, but historical/data trees remain and the open editor folder cannot be inspected.
