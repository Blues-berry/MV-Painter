# Local-to-private-main consolidation report

**Captured:** 2026-10-09T04:46:15Z UTC  
**Private repository:** `Blues-berry/MVPainter`  
**Active branch/worktree:** `main` at `/4T/MV-Painter-main`  
**Private main baseline:** `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`  
**Publication state:** pushed to private `main` and verified. Content commit: `14ff9472df0281267c966b29210d63297ccfcfd7`; handover commits: `b02a64102a40c83370902486d47b1ffad217a49e`, `814652a953d9563b7ab271fed36a8bb40c23d11b`, `bbd66249360d1613c22c6d5f86605e2a8caa6041`; frozen V3 snapshot commit: `2fc3e7f1c338338dfd2d63e4f6977bac77976979`; latest verified handover commit: `788e08d503a7bef6a61a57dd3526ac6fdd17b8b9`. Local and live remote `main` matched at `788e08d503a7bef6a61a57dd3526ac6fdd17b8b9` at 2026-10-09T04:44:33Z UTC.

## Result

- Local `main` was safely fast-forwarded to the existing private `mvpainter/main` before integration; it had no local-only commits. The authenticated 01549 and second-round 1008 sources, code, selected evidence, and author-review package are now curated in the `/4T/MV-Painter-main` worktree.
- The 166-commit `codex/cg-01549-unified-20261009` line was not merged wholesale: its full history includes a much larger generated V3 archive. Instead, the correspondence ledger records 296 reviewed files selected across the unified, surgical, and V3 sources. One redundant baseline JSON lock remains local.
- The 7,230 staged paths in `/4T/CXY/MV-Painter` were classified individually in `STAGED_7230_FILES_DISPOSITION.csv`. After a verified byte backup and classification, only the index was unstaged. All 7,205 present source files still match their captured SHA-256; 25 previously absent archive files match the verified backup. The root worktree now has zero staged paths; its remaining modified/deleted and untracked files remain untouched.
- The 7,824 backup checksum entries passed. Backup directory size: 1,005,063,786 bytes. A timestamped 33-file author-review snapshot was also created at `/4T/MV-Painter-main-consolidation-20261009/author_review_backup_20261009T042335Z/` and its checksums passed. `BYTE_BACKUP_MANIFEST.csv` SHA-256 `23c811d93dd12b33405023fdf1f063eaae85f5402ade8c4eaf8a878deee62f11`; `SHA256SUMS.txt` SHA-256 `cbbd0e9bb68739b36f773ac3f01e6d4c978cf9bffedce999fde30408ffdcf663`.
- Current residual status in the old V3 worktree: {' D': 26, ' M': 4, '??': 581}. No raw experiment collection was copied to main.

## Branch/file correspondence

See `MERGED_BRANCH_FILE_CORRESPONDENCE.csv` and `MAIN_INTEGRATION_COPY_MANIFEST.csv`. Their source/destination paths, source and destination SHA-256, branch tip, disposition, and reasons are recorded. Final 7,230-row disposition after the curated V3 release was added: 105 merged to main, 7026 kept local, 77 historical-only, and 22 rejected with reason.

## V3 reproducibility snapshot

The previous V3 release README referred to per-object data and source files that were absent from the curated main tree. The gap is now closed in `1009/evidence/scientific_validation_v3/reproducibility_release/`: a frozen source snapshot, runner, analysis scripts, tested requirements/configuration, ordered UID lists, 20 per-object metric CSVs (3,465,132 bytes), protocol/provenance text, license, and SHA-256 inventory. Total package payload is under 4 MB; no JSON, generated RGB/GLB, checkpoint, cache, participant record, or residual dump was added. The source snapshot remains separate from the current active implementation. Hash checks passed for all 41 source manifest entries; the A2 evidence table rebuilt byte-identically and the B paired analysis returned N=150 with no unmatched objects. No GPU generation was run. A narrow `.gitignore` exception explicitly admits only these frozen V3 CSV/UID inputs and the runner’s dataset loader; other data directories and JSON remain ignored/local.

## Paper chain and build

The official 01549 source remains immutable at `1008/manuscript/source_01549/final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`), independently matching the 0907 LaTeX archive member. 01549 is the post-first-round 2026-09-07 version; the current R1/R2/R3 packet is the second round. The active 1008 TeX hash is `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525` and matches the author-review copy. Main/Supplement/marked-up/response PDFs compile to 13/11/13/3 pages. The source ZIP clean-extraction build and figure visual check passed.

## Checks and safety

- Python compile check passed; 15 selected statistics/texture tests passed.
- Fresh C primary CSV was re-analyzed by the included script: N=300, C3−GFL FG-PSNR +0.522352 dB, bootstrap 95% CI [+0.404160,+0.640669], seed 20261006; CSV SHA-256 `33f1153632963e33a887d6b852b2d60e8be2086bb2c948ebd27029933eba1bd2`.
- Fresh C figure source manifest records one checkpoint `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` and runner `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`; all 16 records use the same seed policy. Fig. 4 and Fig. 5 output PDF hashes match the figure manifest.
- No participant-level identity keys, 283 GB estimated archive, 390 GB estimated ignored collections, checkpoints, cache, or bulk raw renders were copied to the main integration. Large-size estimates were not independently remeasured.
- `origin` and `upstream` remain read-only; only private `mvpainter` is authorized for a normal push. No force-push, reset, merge, public upload, or source-baseline modification was performed.

## Worktree and editor handover

The audited inventory contained 17 worktrees. Three clean worktrees were unregistered after full status checks, leaving 14 registered worktrees including `/4T/MV-Painter-main`. The status ledger includes ignored-artifact counts; those roots were retained. The seven-thousand-plus staged index in `/4T/CXY/MV-Painter` is resolved, while residual files in that data worktree remain untouched. Only the selected daily worktree is `main`; multiple historical or data branches remain locally checked out. VS Code/Trae still requires the manual Open Folder switch, so the single-visible-repository gate is not yet verified.

## Delivery status

The exact author-package files and disposition report were fetched from private `mvpainter/main` and matched local SHA-256. The current final branch SHA is `b02a64102a40c83370902486d47b1ffad217a49e`. Three worktrees with no tracked, untracked, or ignored files were then unregistered with ordinary (non-force) removal; their branch refs remain. Other dirty or ignored-data worktrees remain registered and preserved. The editor could not be switched through the available CLI, so `EDITOR_ROOT_SWITCH_VERIFIED=NO`; the author must open `/4T/MV-Painter-main` in the editor to complete the UI handoff. The separate R1 color-cast intervention queue remains incomplete in its local worktree; only the already-frozen diagnostic evidence is authoritative in main.


## Final gates

| Gate | State | Evidence/limit |
|---|---|---|
| `MAIN_IS_ONLY_ACTIVE_BRANCH` | NO | Main is the selected daily worktree, but 13 historical/data worktrees remain registered and the editor UI root switch is unverified. |
| `LOCAL_7230_STAGED_CHANGES_DISPOSED` | YES | Index cleared only after a byte backup and 7,230-row classification; local contents remain preserved. |
| `ALL_UNIQUE_SOURCE_CHANGES_INTEGRATED` | NO | Selected source/evidence paths are mapped and the frozen V3 release is now included. Dirty surgical, color-repair, and data worktrees still contain unique uncommitted work retained for review, not wholesale-integrated. |
| `NONESSENTIAL_JSON_EXCLUDED` | YES | No JSON is in the curated V3 snapshot or this commit; original JSON stays local. |
| `IMPORTANT_LOCAL_DATA_PRESERVED` | YES | Backups, checksums, and local worktree inventories verified; no ignored-data worktree was removed. |
| `VSCODE_SINGLE_ACTIVE_REPOSITORY` | NO | No editor switch API or working IPC connection was available; manual Open Folder remains. |
| `OFFICIAL_01549_BASELINE_PRESERVED` | YES | Authenticated source hash remains unchanged. |
| `ACTIVE_MANUSCRIPT_COMPILES` | YES | Previously verified 13-page build and clean-source-package build passed; this snapshot did not alter the manuscript. |
| `PRIVATE_MAIN_PUSHED` | YES | Normal push to private `mvpainter/main`; public remotes untouched. |
| `LOCAL_REMOTE_MAIN_MATCH` | YES | Local `HEAD`, fetched tracking branch, and live `ls-remote` matched at the recorded check. |
| `UNRESOLVED_FILE_CONFLICTS` | 0 | No unmerged index entries; preserved dirty worktrees are review items, not Git merge conflicts. |
| `SUBMISSION_APPROVED` | NO | Author approval remains required. |

`AUTHOR_REVIEW_READY`. This is not `SUBMISSION_APPROVED`; author sign-off is still required before journal submission.


## 2026-10-09 final local-change and 1008 package closeout

- Intake main and mvpainter/main were both `7397fca31998901ca6048375f0e96ffb4a42e5e7` before this task’s edits; the private remote is `mvpainter` only.
- Current registry snapshot: 14 worktrees and 28 local branch refs. The active main worktree was clean at intake; it now contains only the planned 1008 revision/package and closeout reports before the three commits.
- The intake snapshot contained 1,671 non-main status entries. The source manifest was refreshed after an externally launched r1color Phase B run completed; it now contains 1,762 hashed non-main status paths, compared against intake main, including the added local run outputs. Ignored files are not included.
- 1,584 untracked files (452,803,353 bytes) across source trees remain in place. Detailed per-tree worktree counts and staged/unstaged/untracked status are refreshed in `WORKTREE_DISPOSITION.csv`; dispositions are in `FINAL_LOCAL_CHANGE_DISPOSITION.csv`.
- Two stashes were inspected per path and remain intact. 6 stashed file changes have patch/content hashes. The D19 note references follow-up output not present under its named path at the stash base; that result was not treated as evidence.
- Current paper/source/package outputs and the reviewer response have been rebuilt and checked; no experiment or bulk asset was uploaded. See `1008/submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md`, `1009/main_consolidation/COLOR_REPAIR_CAMPAIGN_REVIEW.md`, and `1008/submission_1008/CAG_SUBMISSION_FINAL_ACCEPTANCE.md`.
- The final pushed main SHA is reported at task completion; this snapshot is anchored to the pre-task intake main recorded above.


### Refreshed source status at 2026-10-09T05:38:30Z

- 1,762 current non-main status paths are hashed and individually disposed; 1,584 are untracked (452,803,353 bytes). The new Phase B run outputs are local-only.
- The external Phase B process completed 64 generation calls on four prelocked development cases. It met the `a*` embedding-only directional threshold, but not `b*`; VAE-only did not pass. Two failure-enriched cases failed cache/recompute identity. A C1 candidate subsequently passed numeric means but failed the locked visual failure-case gate; Fresh B was not run, so the manuscript claim ceiling is unchanged.


### Refreshed local inventory at 2026-10-09T05:45:56Z

- Rechecked all 14 registered worktrees and 28 local branch refs against the retained intake-main baseline `7397fca31998901ca6048375f0e96ffb4a42e5e7`. The 13 non-main worktrees expose 1,769 current dirty/untracked status paths; all are individually SHA-256 inventoried and disposed. Four new r1color paths were added to the ledger and one source-view audit hash/size was refreshed.
- Current retained untracked status files total 1,591 files (455,129,145 bytes) across source worktrees. The updated per-tree status counts, bytes, and dispositions are in `WORKTREE_DISPOSITION.csv`; ignored files remain on disk and outside this status-path total.
- The additional Phase B comparison documents a cache-refresh effect in opposite directions on two failure examples, not a stable repair. The Phase C C1 visual gate remains failed; no Fresh B repair run or manuscript claim was added.
- All 14 worktrees and 28 branch refs are retained in this snapshot. The only designated daily editing directory remains `/4T/MV-Painter-main`; editor-folder selection cannot be inspected.


### Final pre-commit inventory at 2026-10-09T05:49:16Z

- Rechecked all 14 registered worktrees and 28 local branch refs against intake main `7397fca31998901ca6048375f0e96ffb4a42e5e7`. The 13 non-main worktrees expose 1,780 current dirty/untracked status paths; each is SHA-256 inventoried and individually disposed. No prior status path disappeared; new local diagnostics and their final hashes are included.
- Current untracked status files total 1,602 files (455,485,326 bytes) across source worktrees. The per-tree status, bytes and disposition table is `WORKTREE_DISPOSITION.csv`; ignored files remain in place and outside this status-path count.
- The new CPU-only input/cache and per-view color readouts remain local. C1 failed its frozen visual gate; no Fresh B repair or new manuscript claim was added.
- The only designated daily editing directory is `/4T/MV-Painter-main`. Dirty historical worktrees, ignored assets, branch refs and both stashes remain preserved; editor-folder selection cannot be inspected.


### 2026-10-09 final pre-commit inventory correction (06:06:08 UTC)

This snapshot supersedes the earlier 05:49 and 06:02 status totals. The registry contains 14 worktrees and 28 local branch refs. `LOCAL_CHANGE_SOURCE_MANIFEST.csv` now has 1,636 non-main dirty/untracked paths with worktree, HEAD, index, main-counterpart hashes, source branch, and status; `FINAL_LOCAL_CHANGE_DISPOSITION.csv` records those paths plus the separately retained branch-commit, ignored-output, and stash records. The 14-tree staged/unstaged/untracked counts are in `WORKTREE_DISPOSITION.csv`.

The 13 non-main trees contain 1,452 untracked status files totaling 430,603,823 bytes. Those files and ignored data remain in their original trees. The 76 ignored r1color image/intermediate outputs (19,944,261 bytes) still match their local SHA-256 inventory. Two stashes remain untouched; the D19 note references a result directory that is absent at its stash base, so its numbers were not promoted. No old worktree, branch, stash, source asset, or experiment data was deleted in this closeout.

At this pre-commit capture, `/4T/MV-Painter-main` had 0 staged paths, 42 tracked worktree changes, and 9 untracked files awaiting the three authorized commits. Before those commits, local main and live `mvpainter/main` were both `7397fca31998901ca6048375f0e96ffb4a42e5e7`. The editor's open folder remains unverifiable; `/4T/MV-Painter-main` is still the only designated daily editing directory.

The separate B2 raw-source embedding proposal had three earlier launch attempts logged as stopping before diffusion generation. After that snapshot, a concurrent workflow added an `attempt_04` status directory and files named for B2 evidence, reconstruction, and results. This audit checked only paths, Git status, and hashes; it did not open the contents, images, metrics, or verdict, so the current call count and outcome remain unverified. These new files remain outside `mvpainter/main`. The separate r1color campaign branch was pushed to its `origin` remote by that concurrent workflow; this task did not initiate or alter that push, and its files remain pending author review.


### Final authorized main and 1008 delivery

The three requested content commits were published normally and in order to the authorized `mvpainter/main` remote:

1. `2cb1045b4d49814928dbfd6000ce119f89452b7a` — worktree and source disposition.
2. `811b51d7e9709ede0a6083ddcdcfe36fe281db60` — scientific narrative and second-round response.
3. `b50b9cca3f7332d18c36159e274538f4de88ab94` — complete 1008 submission package.

After the package push, local `main` and live `mvpainter/main` both resolved to `b50b9cca3f7332d18c36159e274538f4de88ab94`; the worktree was clean. No other remote was updated by this task. The package contains 47 files, its 46 manifest payload entries and 47 SHA-256 records passed verification, and the 44-member LaTeX source ZIP passed CRC. PDF page counts are 13 (manuscript), 11 (Supplement), 5 (response), 13 (marked-up manuscript), and 18 (combined convenience PDF). The administrative attachments remain `DRAFT`; no journal upload occurred and `SUBMISSION_APPROVED=NO`.

This entry records the verified package-delivery SHA immediately before a documentation-only update to this report. The exact current SHA containing this report update is stated in the task completion record.


### 2026-10-09 post-delivery B2 inventory follow-up (06:14:21 UTC)

After the verified package push, a concurrent workflow added more status paths in the retained r1color worktree, including an `attempt_04` directory and B2 evidence/reconstruction/result-named files. The count is now 1,652 hashed non-main status paths across 14 registered worktrees and 28 local branch refs; 1,462 are untracked, totaling 433,092,188 bytes. All current non-main paths and hashes are in `LOCAL_CHANGE_SOURCE_MANIFEST.csv`; dispositions and per-worktree staged/unstaged/untracked counts are in `FINAL_LOCAL_CHANGE_DISPOSITION.csv` and `WORKTREE_DISPOSITION.csv`. No result content, metrics, images, or verdict from these new B2 files was opened. The current B2 call count and outcome remain unverified, so none is used in the manuscript or acceptance claims. This note supersedes the prior three-attempt-only status for the later r1color activity.

At this snapshot the active main worktree was at commit `a813ffee5f2a4a354e28e831dbd1f0066c35ad8c`, and live `mvpainter/main` matched it before the current report/package refresh. `/4T/MV-Painter-main` remains the designated daily editing directory; historical and experimental worktrees and both stashes remain preserved. The author-review package remains `DRAFT`; no journal upload occurred and `SUBMISSION_APPROVED=NO`.


At the 06:15:26 UTC hash refresh, two existing tracked r1color status files had changed after the 06:14:21 inventory. Their current sizes and SHA-256 values were refreshed in the manifests; their contents were not opened. No non-main status paths were added or removed in that refresh. The B2 result remains unreviewed.
