# Branch-unique work and live worktree report

**Snapshot:** 2026-10-09T06:26:00Z
**Comparison main:** `c910ded7aa80a6e601e1d5035f77e0b9218c7c06`
**Intake source-comparison base:** `7397fca31998901ca6048375f0e96ffb4a42e5e7`
**Registered worktrees:** 14
**Local branch refs:** 28
**Current non-main Git status paths:** 779
**Newly ignored but hash-preserved paths:** 856 (166,583,423 bytes)
**Total current/hidden manifest entries:** 1,654
**Stashes audited and retained:** 2.

The branch table reports commit reachability and changed-path counts against the current main HEAD shown above. It is a scope index, not a wholesale merge recommendation. Prior curated-copy history remains in `MERGED_BRANCH_FILE_CORRESPONDENCE.csv` and `MAIN_INTEGRATION_COPY_MANIFEST.csv`.

| Local branch | HEAD | Main-only commits | Branch-only commits | Paths from merge base |
|---|---|---:|---:|---:|
| `backup/geotex-before-cleanup` | `61f628bb6a13` | 28 | 0 | 0 |
| `codex/cg-01549-surgical-revision-20261008` | `06cac81de239` | 14 | 165 | 34570 |
| `codex/cg-01549-surgical-upload-20261008` | `dad083206254` | 14 | 155 | 27139 |
| `codex/cg-01549-unified-20261009` | `284cd252b8b3` | 14 | 166 | 27175 |
| `codex/cg-01549-unified-audit-f8ff09d2-20261009` | `f8ff09d26f82` | 14 | 179 | 34607 |
| `codex/cg-ltcas-narrative-convergence-20261007` | `bf1dc3d41edd` | 14 | 141 | 2750 |
| `codex/cg-revision-evidence-closure-20261007` | `d59c4606ad54` | 14 | 131 | 2727 |
| `codex/cg-round2-1008-public-sanitized-20261008` | `1f2448358537` | 14 | 131 | 26947 |
| `codex/cg-round2-1008-revision-20261008` | `3e592037d5fd` | 14 | 141 | 27055 |
| `codex/evidence-closure-audit-20261005` | `7e659c7e5695` | 14 | 161 | 42243 |
| `codex/final-evidence-freeze-20261001` | `29b3a0a6ec00` | 14 | 125 | 2080 |
| `codex/human-confirmatory-analysis-20261007` | `86292c8b5822` | 14 | 145 | 3085 |
| `codex/main-backbone-robustness1-20260930` | `99d6c88f2805` | 14 | 102 | 1784 |
| `codex/next-review-response-20260930` | `4f312566ed42` | 14 | 102 | 1794 |
| `codex/paper-1006-20261006` | `a9ac1459b3d6` | 14 | 143 | 3064 |
| `codex/public-round2-evidence` | `78c871ffb4a9` | 14 | 80 | 1662 |
| `codex/r1-color-cast-repair-v2-20261009` | `32bb9106fa0e` | 14 | 150 | 3910 |
| `codex/r1-color-root-cause-20261008` | `7311b9446733` | 14 | 142 | 3733 |
| `codex/r1-color-root-cause-20261008-local-history` | `5fb32c1676a6` | 14 | 164 | 42512 |
| `codex/r1-fidelity-validation-48h-20261008` | `46e741180a2f` | 14 | 146 | 3797 |
| `codex/round2-evidence-integrated-20261001` | `ce4831f40c72` | 14 | 118 | 2060 |
| `codex/round2-final-forensic-audit-20261001` | `450389fb8232` | 14 | 119 | 2060 |
| `codex/scientific-validation-v3-20261002` | `5c2c8829a1e1` | 14 | 163 | 42278 |
| `codex/scientific-validation-v3-20261006` | `12da08c7056f` | 14 | 126 | 2605 |
| `gh-pages` | `5f203f83e818` | 67 | 6 | 1210 |
| `main` | `c910ded7aa80` | 0 | 0 | 0 |
| `new0528` | `3f5202cf5ab0` | 45 | 0 | 0 |
| `new0529` | `d9379fe93e51` | 14 | 79 | 710 |

## Current registered worktrees

| Path | Branch / state | HEAD | Staged | Unstaged | Untracked | Untracked bytes | Staged deletes | Unstaged deletes | Disposition |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `/4T/CXY/MV-Painter` | `codex/scientific-validation-v3-20261002` | `5c2c8829a1e1` | 0 | 30 | 581 | 236,808,554 | 0 | 26 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | `codex/cg-01549-surgical-revision-20261008` | `06cac81de239` | 0 | 53 | 18 | 28,868,139 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-1006-wt` | `codex/paper-1006-20261006` | `a9ac1459b3d6` | 26 | 0 | 0 | 0 | 25 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-1008` | `codex/cg-round2-1008-revision-20261008` | `3e592037d5fd` | 27 | 0 | 1 | 776,861 | 22 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence` | `codex/cg-ltcas-narrative-convergence-20261007` | `bf1dc3d41edd` | 31 | 0 | 0 | 0 | 25 | 0 | PRESERVE_DIRTY |
| `/4T/CXY/MV-Painter-r1color` | `codex/r1-color-cast-repair-v2-20261009` | `32bb9106fa0e` | 0 | 0 | 1 | 1,528 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/MV-Painter-01549-unified-20261009` | `codex/cg-01549-unified-20261009` | `284cd252b8b3` | 0 | 9 | 0 | 0 | 0 | 0 | PRESERVE_DIRTY |
| `/4T/MV-Painter-main` | `main` | `c910ded7aa80` | 0 | 19 | 0 | 0 | 0 | 0 | ACTIVE_MAIN |
| `/4T/tmp/01549-clean-checkout-20261008` | `DETACHED` | `fb0b24cba203` | 0 | 2 | 0 | 0 | 0 | 0 | PRESERVE_DIRTY |
| `/tmp/MV-Painter-evidence-closure` | `codex/evidence-closure-audit-20261005` | `7e659c7e5695` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/MV-Painter-human-confirmatory-20261007` | `codex/human-confirmatory-analysis-20261007` | `86292c8b5822` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/MVPainter-cg01549-private-upload` | `codex/cg-01549-surgical-upload-20261008` | `dad083206254` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/cg-closure-clean-audit` | `DETACHED` | `e267b2d59bbb` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |
| `/tmp/mvpainter-cg-evidence-closure` | `codex/cg-revision-evidence-closure-20261007` | `d59c4606ad54` | 0 | 0 | 0 | 0 | 0 | 0 | PRESERVE_CLEAN_REFERENCE |

## Concurrent r1color publication and ignore-state change

The r1color HEAD and `origin/codex/r1-color-cast-repair-v2-20261009` both resolve to `32bb9106fa0ea6199e6a16f9279343c0b21581a6`. A concurrent workflow added two commits after `bd9d436c2f13c00de36a64cb42e807da558ef5c4`; 18 paths changed, six new to the branch disposition ledger. This task did not initiate either push and did not read those file contents. The committed ignore rule hides 856 prior status files (166,583,423 bytes); every file is still present and hash-matches its earlier entry. The files are `IGNORED_LOCAL`, not lost or merged. The 76 older ignored image intermediates remain a separate inventory. B2 evidence remains unreviewed.

## Individual disposition

The ledger records 779 current non-main Git status paths, 856 ignored files hash-matched to the prior inventory, 114 r1color committed paths, 76 earlier ignored outputs, and 6 stash file changes. Disposition counts: ALREADY_PRESENT=26, ARCHIVED_LOCAL=1,611, MERGED_MAIN=1, NEEDS_AUTHOR_DECISION=117, SUPERSEDED=76. Source trees and stash refs were preserved.

- `ALREADY_PRESENT` rows match intake-main counterparts; the accurate unified Response passage informed the rewritten response and is `MERGED_MAIN`.
- Older TeX/PDF/build products remain superseded; worktree-local deletions remain local.
- C1 failed its locked visual gate. New B2 paths are unreviewed; no result is inferred from file names.
- `MAIN_SINGLE_EDITING_AUTHORITY=PARTIAL`: `/4T/MV-Painter-main` is the only designated daily worktree; historical/data trees remain and editor selection is unverifiable.
