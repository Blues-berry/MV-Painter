# Local asset retention and worktree protection

**Captured:** `2026-10-09T06:06:08Z` UTC
**Active worktree:** `/4T/MV-Painter-main`
**Registered worktrees:** 14
**Local branch refs:** 28
**Hashed non-main status paths:** 1,636
**Comparison base:** intake main `7397fca31998901ca6048375f0e96ffb4a42e5e7`.

## Untracked source assets retained in place

| Source worktree | Files | Bytes | Retention note |
|---|---:|---:|---|
| `/4T/CXY/MV-Painter` | 581 | 236,808,554 | V3 experiment history and source materials remain in place; the curated frozen snapshot is already in main. |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | 18 | 28,868,139 | Surgical manuscript drafts and local evidence remain preserved for historical review. |
| `/4T/CXY/MV-Painter-1008` | 1 | 776,861 | Historical figure/material remains preserved in its source tree. |
| `/4T/CXY/MV-Painter-r1color` | 852 | 164,150,269 | Color-cast diagnostics and B2 attempt records remain local; no generated prediction PNGs were produced by B2. |
| **Total** | **1,452** | **430,603,823** | Current non-main untracked status files only. |

## Verified ignored campaign outputs

- The r1color campaign retains 76 local-only image/intermediate files (19,944,261 bytes), each verified against `1009/engineering/color_cast_repair_v2/LOCAL_ONLY_SHA256SUMS.txt`. They remain on disk under the branch-local ignore policy. Other ignored data trees were not re-enumerated.
- The campaign’s 108 source/protocol/result files are committed on r1color and mirrored on its `origin` branch by a concurrent workflow. This task did not initiate that push or merge those files into `mvpainter/main`; their remote placement is flagged for author review.

## Protection decisions

- No local source tree, ignored prediction image, stash, or branch was removed/reset by this consolidation. No forced worktree operation or destructive Git maintenance was run.
- Current dirty/untracked paths are SHA-256 inventoried; the 108 branch-committed files and 76 ignored local images have separate dispositions.
- The C1 candidate failed its locked visual repair gate. Three B2 attempts stopped before diffusion generation (0 calls, 0 prediction PNGs); the third loaded the model before a shape guard failed. No Fresh B predictions or metrics were read.
- Both stashes remain untouched. The D19 note references an unavailable result directory; its numbers were not promoted.
