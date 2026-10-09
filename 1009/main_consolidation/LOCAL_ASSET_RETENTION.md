# Local asset retention and worktree protection

**Captured:** `2026-10-09T06:15:26Z` UTC
**Active worktree:** `/4T/MV-Painter-main`
**Registered worktrees:** 14
**Local branch refs:** 28
**Hashed non-main status paths:** 1,652
**Comparison base:** intake main `7397fca31998901ca6048375f0e96ffb4a42e5e7`.

## Untracked source assets retained in place

| Source worktree | Files | Bytes | Retention note |
|---|---:|---:|---|
| `/4T/CXY/MV-Painter` | 581 | 236,808,554 | V3 experiment history remains local; curated frozen snapshot is in main. |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | 18 | 28,868,139 | Surgical manuscript drafts and local evidence remain preserved. |
| `/4T/CXY/MV-Painter-1008` | 1 | 776,861 | Historical figure/material remains preserved in its source tree. |
| `/4T/CXY/MV-Painter-r1color` | 862 | 166,638,634 | Color-cast diagnostics and new B2 attempt/evidence files remain local; contents were not evaluated. |
| **Total** | **1,462** | **433,092,188** | Current non-main untracked status files only. |

## Previously verified ignored campaign outputs

- The 76 previously inventoried r1color image/intermediate files (19,944,261 bytes) remain on disk and matched their recorded hashes at the prior check. Newly appeared B2 paths were not inspected for ignored outputs or visual quality.
- The 108 source/protocol/result files are committed on r1color and mirrored to its `origin` branch by a concurrent workflow. This task did not initiate that push or merge those files into `mvpainter/main`; remote placement remains for author review.

## Protection decisions

- No local source tree, ignored prediction image, stash, or branch was removed/reset. No destructive Git maintenance was run.
- All current non-main status paths are SHA-256 inventoried; the 108 branch-committed files and previously verified ignored images have separate dispositions.
- New attempt_04/B2 evidence paths remain unreviewed and local; no scientific result or repair claim was inferred from their presence.
- Both stashes remain untouched; the D19 follow-up directory was unavailable at its stash base.
