# Local data retention manifest

**Captured:** 2026-10-09T04:29:56Z UTC

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

The exact local-only split is in the CSV, not inferred from file extensions. One redundant `BASELINE_SOURCE_LOCK.json` remains in the worktree and is explicitly excluded; a text SHA-256 lock is used in the source package.


## Timestamped author-package backup

A separate local backup was created before commit/upload at `/4T/MV-Painter-main-consolidation-20261009/author_review_backup_20261009T042335Z/`. It contains the 33-file author-review package snapshot (66,525,632 bytes). Its `SHA256SUMS.txt` SHA-256 is `e90ce8ae55cb185a8b97d1765401ac82b745658fc357386c2aae29ed42d44b4e`; all entries passed verification. Its `BACKUP_MANIFEST.csv` SHA-256 is `711be37067e19923d53079cf06302871e40ba3aeb1b5fce15cb7a1a15ee859f9`. The active TeX hash recorded in the backup is `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525`.

## Other local worktrees and data

- `/4T/CXY/MV-Painter`: 581 untracked files, 236,808,554 bytes; old V3 branch remains a local evidence/data worktree.
- `/4T/CXY/MV-Painter-01549-surgical-20261008`: 53 modified paths plus 18 untracked files, 28,813,139 bytes; preserved.
- `/4T/CXY/MV-Painter-r1color`: 893 untracked files, 164,543,302 bytes; raw traces and generated images remain local.
- `/4T/CXY/MV-Painter-1008`: 1 untracked internal image file, 776,861 bytes; preserved.
- Other worktrees with staged historical deletions were not reset or cleaned. See `WORKTREE_DISPOSITION.csv`.

The previously cited 283 GB archive and 390 GB ignored-data estimates were not independently inventoried in this pass. No such archives or bulk ignored data were copied, deleted, or uploaded. The worktree ledger now includes ignored-status entries. Three worktrees that had zero tracked, untracked, and ignored entries were safely unregistered; all other roots with local or ignored data were retained.
