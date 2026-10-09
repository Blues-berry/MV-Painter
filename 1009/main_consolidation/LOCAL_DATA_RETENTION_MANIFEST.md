# Local data retention manifest

**Captured:** 2026-10-09T04:42:50Z UTC

## Byte-preserved staged snapshot

- Source worktree: `/4T/CXY/MV-Painter`, branch `codex/scientific-validation-v3-20261002`, captured HEAD `5c2c8829a1e19b42837761160dc4c14cf8f09045`.
- Exact staged-path inventory: `STAGED_7230_FILES_DISPOSITION.csv` (7,230 rows). Its source SHA-256, backup SHA-256, index object ID, byte count, local backup location, and decision are per row.
- Local backup: `/4T/MV-Painter-main-consolidation-20261009/preflight_scientific-validation-v3/byte_backup/`; 7,824 SHA entries passed. Total backup directory size 1,005,063,786 bytes.
- Backup manifest SHA-256: `23c811d93dd12b33405023fdf1f063eaae85f5402ade8c4eaf8a878deee62f11`. Checksum list SHA-256: `cbbd0e9bb68739b36f773ac3f01e6d4c978cf9bffedce999fde30408ffdcf663`.
- After recording the disposition and confirming all hashes, the staged index was restored to the branch HEAD. All 7,205 files present in the worktree matched their captured worktree SHA-256; the 25 absent historical files matched the backup. No file contents were changed by unstaging.

## Retained local data classes

| Class | Count from the staged inventory | Handling |
|---|---:|---|
| Generated JSON records | 6922 | Local-only; not added to main.
| Metric CSV files | 114 | Local-only unless an explicit reviewed copy is identified in the correspondence ledger.
| Raw/private outputs and keys | 10 | Local-only; no participant-level records or keys were uploaded.
| Caches, predictions, residual logs | 0 | Kept local; no bulk cache was copied.
| Historical/deprecated archives | 26 | Retained in branch history/byte backup.
| Other reviewed reports/protocol/code | 158 | Selected items copied only when present in the curated manifest.

The exact local-only split is in the CSV, not inferred from file extensions. The V3 release source and selected metrics have exact path/hash entries; runner/runtime JSON and generated JSON outputs remain local, with only relevant provenance summarized in Markdown. One redundant `BASELINE_SOURCE_LOCK.json` remains in the worktree and is explicitly excluded.


## Timestamped author-package backup

A separate local backup was created before commit/upload at `/4T/MV-Painter-main-consolidation-20261009/author_review_backup_20261009T042335Z/`. It contains the 33-file author-review package snapshot (66,525,632 bytes). Its `SHA256SUMS.txt` SHA-256 is `e90ce8ae55cb185a8b97d1765401ac82b745658fc357386c2aae29ed42d44b4e`; all entries passed verification. Its `BACKUP_MANIFEST.csv` SHA-256 is `711be37067e19923d53079cf06302871e40ba3aeb1b5fce15cb7a1a15ee859f9`. The active TeX hash recorded in the backup is `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`.

## Other local worktrees and data

- `/4T/CXY/MV-Painter`: 581 untracked files, 236,808,554 bytes; old V3 branch remains a local evidence/data worktree.
- `/4T/CXY/MV-Painter-01549-surgical-20261008`: 53 modified paths plus 18 untracked files, 28,813,139 bytes; preserved.
- `/4T/CXY/MV-Painter-r1color`: 893 untracked files, 164,543,302 bytes; raw traces and generated images remain local.
- `/4T/CXY/MV-Painter-1008`: 1 untracked internal image file, 776,861 bytes; preserved.
- Other worktrees with staged historical deletions were not reset or cleaned. See `WORKTREE_DISPOSITION.csv`.

The previously cited 283 GB archive and 390 GB ignored-data estimates were not independently inventoried in this pass. No such archives or bulk ignored data were copied, deleted, or uploaded. The worktree ledger now includes ignored-status entries. Three worktrees that had zero tracked, untracked, and ignored entries were safely unregistered; all other roots with local or ignored data were retained.

## Current preserved-worktree inventory — 2026-10-09T07:12Z

A fresh Git status inventory was taken after the r1color and strict-276 review. It found no running agent or GPU experiment. Fourteen worktrees remain registered; no worktree, branch ref, or stash was removed in this follow-up. The five `/tmp` reference worktrees all contain ignored local files, so they were retained even though tracked/untracked Git status is otherwise clean.

| Worktree | Ignored files | Ignored bytes | Current other local state | Handling |
|---|---:|---:|---|---|
| `/4T/CXY/MV-Painter` (V3) | 330,633 | 394,882,142,333 | 30 modified/deleted tracked paths; 581 untracked files / 236,808,554 bytes | Preserved; includes the strict-276 raw run and larger inherited local archives |
| `/4T/CXY/MV-Painter-01549-surgical-20261008` | 241 | 120,977,297 | 53 modified tracked paths; 18 untracked files / 28,868,139 bytes | Preserved |
| `/4T/CXY/MV-Painter-1006-wt` | 11 | 169,292 | 26 staged paths, including 25 deletions | Preserved; staged historical deletions untouched |
| `/4T/CXY/MV-Painter-1008` | 0 | 0 | 27 staged paths, including 22 deletions; 1 untracked image / 776,861 bytes | Preserved |
| `/4T/CXY/MV-Painter-cg-ltcas-narrative-convergence` | 0 | 0 | 31 staged paths, including 25 deletions | Preserved; staged historical deletions untouched |
| `/4T/CXY/MV-Painter-r1color` | 1,048 | 2,379,764,671 | 1 untracked test file / 1,528 bytes | Preserved at HEAD `32bb9106`; 856 paths match the earlier inventory, while 192 additional paths were newly surfaced by the current ignore rules and individually SHA-256 captured at 2026-10-09T07:04:47Z as `POST_SNAPSHOT`. |
| `/4T/MV-Painter-01549-unified-20261009` | 17 | 12,256,121 | 9 modified tracked paths | Preserved |
| `/4T/MV-Painter-main` | 45 | 12,448,831 | Active main; final follow-up snapshot captured with changes pending commit | Sole designated day-to-day authority, but not yet the only registered/editor-open worktree |
| `/4T/tmp/01549-clean-checkout-20261008` | 17 | 20,917,123 | 2 modified tracked paths | Preserved detached checkout |
| `/tmp/MV-Painter-evidence-closure` | 2 | 41,127 | No tracked or untracked changes | Preserved; ignored analysis JSON and script |
| `/tmp/MV-Painter-human-confirmatory-20261007` | 10 | 132,129 | No tracked or untracked changes | Preserved; ignored LaTeX build artifacts |
| `/tmp/MVPainter-cg01549-private-upload` | 38 | 12,692,085 | No tracked or untracked changes | Preserved; ignored LaTeX build artifacts |
| `/tmp/cg-closure-clean-audit` | 4 | 118,258 | No tracked or untracked changes | Preserved; ignored C&G style/class/logo files |
| `/tmp/mvpainter-cg-evidence-closure` | 6 | 7,776,423 | No tracked or untracked changes | Preserved; ignored style/class/logo files and revision PDFs |

This is a status/size inventory, not a full rehash of all ignored data. Every one of the 58 evidence files actually copied into main was individually SHA-256 checked against its source at the pinned worktree HEAD. The additional 192 r1color files were hash-captured in `LOCAL_CHANGE_SOURCE_MANIFEST.csv` and separately classified in `FINAL_LOCAL_CHANGE_DISPOSITION.csv` as `POST_SNAPSHOT`; together they total 2,213,181,248 bytes. Unselected generated data remain in place and were not opened, rewritten, or deleted. The V3 ignored tree's 330,633 entries are represented here by path count and byte total, not a new full-file rehash.


## Final follow-up capture — 2026-10-09T07:12:56Z

The follow-up capture remained on `/4T/MV-Painter-main`, branch `main`, HEAD `8cf02b797c5d467db764d05ea4940937c207fe96`, matching `mvpainter/main` before the delivery commits. At capture there were 29 changed tracked paths, 60 untracked paths / 9,588,891 bytes, no staged paths, and 45 ignored paths / 12,448,831 bytes. The untracked paths are the 58 manifest-tracked, hash-verified evidence payload files plus two README summaries in their evidence directories. The ignored entries include disposable build outputs and remain local.

The source worktree `/4T/CXY/MV-Painter-r1color` remained at `32bb9106fa0ea6199e6a16f9279343c0b21581a6`, with one untracked test file and 1,048 ignored paths / 2,379,764,671 bytes. The 192 paths newly surfaced by the current ignore rules were captured separately as `POST_SNAPSHOT` with per-file SHA-256 (2,213,181,248 bytes); none was copied to main. The V3 worktree remained at `5c2c8829a1e19b42837761160dc4c14cf8f09045`; its 330,633 ignored paths / 394,882,142,333 bytes were preserved and not rehashed in this capture.

No other source worktree HEAD or recorded status changed since the 07:03–07:04 inventory. No GPU generation, training, Git commit, or push process was active at capture. Fourteen registered worktrees, all 28 local branch refs, both stash entries, and `gh-pages` remain. No worktree, ref, stash, or raw experiment output was removed.
