# Local-to-private-main consolidation report

**Captured:** 2026-10-09T04:16:30Z UTC  
**Private repository:** `Blues-berry/MVPainter`  
**Active branch/worktree:** `main` at `/4T/MV-Painter-main`  
**Private main baseline:** `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`  
**Publication state:** pushed to private `main` and verified. Content commit: `14ff9472df0281267c966b29210d63297ccfcfd7`; remote SHA-256-matched on 2026-10-09T04:26:29Z UTC.

## Result

- Local `main` was safely fast-forwarded to the existing private `mvpainter/main` before integration; it had no local-only commits. The authenticated 01549 and second-round 1008 sources, code, selected evidence, and author-review package are now curated in the `/4T/MV-Painter-main` worktree.
- The 166-commit `codex/cg-01549-unified-20261009` line was not merged wholesale: its full history includes a much larger generated V3 archive. Instead, the correspondence ledger records 296 reviewed files selected across the unified, surgical, and V3 sources. One redundant baseline JSON lock remains local.
- The 7,230 staged paths in `/4T/CXY/MV-Painter` were classified individually in `STAGED_7230_FILES_DISPOSITION.csv`. After a verified byte backup and classification, only the index was unstaged. All 7,205 present source files still match their captured SHA-256; 25 previously absent archive files match the verified backup. The root worktree now has zero staged paths; its remaining modified/deleted and untracked files remain untouched.
- The 7,824 backup checksum entries passed. Backup directory size: 1,005,063,786 bytes. A timestamped 33-file author-review snapshot was also created at `/4T/MV-Painter-main-consolidation-20261009/author_review_backup_20261009T042335Z/` and its checksums passed. `BYTE_BACKUP_MANIFEST.csv` SHA-256 `23c811d93dd12b33405023fdf1f063eaae85f5402ade8c4eaf8a878deee62f11`; `SHA256SUMS.txt` SHA-256 `cbbd0e9bb68739b36f773ac3f01e6d4c978cf9bffedce999fde30408ffdcf663`.
- Current residual status in the old V3 worktree: {' D': 26, ' M': 4, '??': 581}. No raw experiment collection was copied to main.

## Branch/file correspondence

See `MERGED_BRANCH_FILE_CORRESPONDENCE.csv` and `MAIN_INTEGRATION_COPY_MANIFEST.csv`. Their source/destination paths, source and destination SHA-256, branch tip, disposition, and reasons are recorded. Totals: 40 source paths copied from staged V3, 7046 kept local, 80 historical-only, and 64 not selected.

## Paper chain and build

The official 01549 source remains immutable at `1008/manuscript/source_01549/final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`), independently matching the 0907 LaTeX archive member. 01549 is the post-first-round 2026-09-07 version; the current R1/R2/R3 packet is the second round. The active 1008 TeX hash is `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525` and matches the author-review copy. Main/Supplement/marked-up/response PDFs compile to 13/11/13/3 pages. The source ZIP clean-extraction build and figure visual check passed.

## Checks and safety

- Python compile check passed; 15 selected statistics/texture tests passed.
- Fresh C primary CSV was re-analyzed by the included script: N=300, C3−GFL FG-PSNR +0.522352 dB, bootstrap 95% CI [+0.404160,+0.640669], seed 20261006; CSV SHA-256 `33f1153632963e33a887d6b852b2d60e8be2086bb2c948ebd27029933eba1bd2`.
- Fresh C figure source manifest records one checkpoint `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` and runner `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`; all 16 records use the same seed policy. Fig. 4 and Fig. 5 output PDF hashes match the figure manifest.
- No participant-level identity keys, 283 GB estimated archive, 390 GB estimated ignored collections, checkpoints, cache, or bulk raw renders were copied to the main integration. Large-size estimates were not independently remeasured.
- `origin` and `upstream` remain read-only; only private `mvpainter` is authorized for a normal push. No force-push, reset, merge, public upload, or source-baseline modification was performed.

## Delivery status

The exact author-package files and disposition report were fetched from private `mvpainter/main` and matched local SHA-256. The delivery-status document records the author-review links and content commit; the current final branch SHA is reported after the status-only update is pushed.


`AUTHOR_REVIEW_READY`. This is not `SUBMISSION_APPROVED`; author sign-off is still required before journal submission.
