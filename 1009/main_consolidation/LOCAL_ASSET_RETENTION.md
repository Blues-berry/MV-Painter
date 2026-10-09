# Local asset retention and worktree protection

**Captured:** `2026-10-09T06:26:00Z` UTC
**Active worktree:** `/4T/MV-Painter-main`
**Registered worktrees:** 14
**Local branch refs:** 28
**Current non-main Git status paths:** 779
**Newly ignored paths retained with matching hashes:** 856 (166,583,423 bytes)
**Comparison main:** `c910ded7aa80a6e601e1d5035f77e0b9218c7c06`

## Current untracked source assets retained in place

| Source worktree | Files | Bytes | Retention note |
|---|---:|---:|---|
| `/4T/CXY/MV-Painter` | 581 | 236,808,554 | V3 experiment history remains local; curated frozen snapshot is in main. |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | 18 | 28,868,139 | Surgical manuscript drafts and local evidence remain preserved. |
| `/4T/CXY/MV-Painter-1008` | 1 | 776,861 | Historical figure/material remains preserved in its source tree. |
| `/4T/CXY/MV-Painter-r1color` | 1 | 1,528 | One untracked file remains; 856 prior files are ignored and separately hash-preserved. |
| **Total** | **601** | **266,455,082** | Current non-main untracked status files only. |

## Ignored local assets retained

- A concurrent committed `.gitignore` change causes 856 paths already present in the prior worktree manifest to be ignored. All 856 files remain on disk, total 166,583,423 bytes, and match their prior SHA-256 entries.
- The 856 paths include B2 attempt/evidence-named artifacts. Their contents, metrics, and images were not reviewed; current B2 call count and outcome remain unknown in this audit.
- Separately, 76 previously ignored r1color image/intermediate files (19,944,261 bytes) remain on disk and matched their retained checksum inventory at the earlier check. Other ignored roots were not enumerated.
- The r1color branch has 114 inventoried committed paths on its `origin` ref after concurrent handoff commits; this task did not push to that remote.

## Protection decisions

- No local source tree, ignored prediction image, stash, or branch was removed/reset. No destructive Git maintenance was run.
- Current dirty paths, ignored assets, and external branch commits have separate dispositions.
- Both stashes remain untouched; the D19 follow-up directory was unavailable at its stash base.
