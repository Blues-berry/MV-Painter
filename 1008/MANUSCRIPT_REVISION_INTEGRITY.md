# Manuscript revision timestamps and hashes

Status: `AUTHOR_REVIEW_READY`. This record does not approve journal submission.

## Latest verified revision — final wording and package refresh

At **2026-10-09T08:11:51Z**, the in-place manuscript wording revision and refreshed author-review package were fingerprinted on `main`, based on `ed7471ee57351d7c8d4600d43d2c63bd44d01725`. The pre-edit SHA-256 was `9ffa845eff67d22ec75fbf1c135967fa1d8057bc7c4b13ad44b7c8c1a9ea55bb`; the active, author-review, package, and source-ZIP TeX copies now match at `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`. The prose-only edits refine the abstract, third contribution, and conclusion; data, results, Supplement source, and reviewer-response source did not change.

| File | SHA-256 |
|---|---|
| Active manuscript and synchronized package TeX | `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4` |
| Active Supplement TeX | `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed` |
| Main PDF (13 pages) | `8e231a2941a165de4c5c68b33ef087cc7f53a6550ad5e878eee742a575a08935` |
| Marked-up PDF (13 pages) | `143ecff586aa057e3e81c95cff09f749459b476ae23387890cfbbb5ac392c0b7` |
| Supplement PDF (11 pages) | `79bd2cf57de7e94f62b82c1d7edefe03675427949578ad44fc8ab8b5470156db` |
| Reviewer response PDF (5 pages; source unchanged) | `c9cebb9dc8198ec9077d36f3dcf1dad084a9b064793bce9678303228a28d96a0` |
| Clean LaTeX source ZIP (44 entries) | `348e42dc5663d4761ce0088e5e9af44b01af93b59a3e5cd1b031bd52d72115bd` |

The source-ZIP manuscript, marked-up manuscript, and Supplement each rebuilt from a clean extraction to 13/13/11 pages; normalized extracted text matches the delivered PDFs. Package manifest and SHA256SUMS checks passed. The built-in editor compiler returned `Unable to find standard directories for platform`; the repository's pdfLaTeX scripts succeeded in the working tree and clean extraction. Pre-edit and post-build source hashes are also recorded in `MANUSCRIPT_REVISION_INTEGRITY.csv`. Journal submission was not made; `SUBMISSION_APPROVED=NO`.

## Private-main synchronization — 2026-10-09T08:13:59Z

The paper/package refresh commit `9c3e6bdcc4115cf3ac4b153c6e879439a5ca9a1f` was pushed as a normal fast-forward to private `mvpainter/main`; `git rev-parse HEAD` and `git ls-remote mvpainter refs/heads/main` matched at that checkpoint. The final verification report records the branch/worktree disposition. A follow-up documentation and package-metadata closeout commit is pushed separately as a normal fast-forward; the completion handoff gives the post-closeout `main` SHA.

## Previous verified revision — Core-7 alignment

At **2026-10-09T03:33:24Z**, the active manuscript, Supplement, generated PDFs, response, and author-review package were fingerprinted on authority branch `codex/cg-01549-unified-20261009`, base commit `b327b4875b23ce4f365bb880e4f6faa9b0b0ad10`. This is the pre-commit base for the current package update. The same timestamp and SHA-256 rows were appended to `MANUSCRIPT_REVISION_INTEGRITY.csv` for 52 paper/package files; the recorder excludes JSON. This final capture followed CSV line-ending normalization; content hashes are unchanged from the 03:32:34Z capture.

| File | SHA-256 |
|---|---|
| Active manuscript TeX and author-review copy | `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525` |
| Active Supplement TeX and author-review copy | `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f` |
| Main PDF | `93aefbf6cb5ef68382db18342acbb791b833f1e87f45494558452ae8b4114e4d` |
| Marked-up PDF | `6951be9831fbf7d472ea30e0bee4472d1d25b93fd9508bd3380000563834f424` |
| Supplement PDF | `5a2a41ffd151785469665f53241807ea283fa2894a6eec0fd77f9f969b63989f` |
| Reviewer response Markdown / PDF | `47d74ac5ed14b9c3b45d41e064c1da36219d49b7e872e7e4ba6bf340e2a243d5` / `ff80bbaf94ee1b0b1d6b596e640eab0035f7a7700d3ffa37efdd0671f4a1b203` |
| 01549-to-1008 change log | `c07a77976d93bbcabd49fbb6510df6182174a1442514eb3249202d67f3240dd3` |
| Clean LaTeX source ZIP | `bfd1eddca46cb10d66afca93ab613df8c600225ef16ec076548092f027517659` |

The clean-source ZIP build passed at 13 main pages and 11 Supplement pages. Supplement S5's Core-7 tables were inspected at page size on pp. 6–7. The final local backup at `/4T/MV-Painter-01549-local-records-20261009/20261009T033353Z/` contains the complete author-review package and current changed project files; all 54 listed files passed `sha256sum -c`. Its manifest SHA-256 is `2d267d59fabea06f3d95ed774961f092d1ff947740eccbd90457402408cdec83`. It contains no JSON.

## Previous verified revision — 2026-10-09T02:38:30Z

The author-review package was fingerprinted and backed up at **2026-10-09T02:38:30Z**. This is a verification/backup timestamp, not a claim that the manuscript text was edited at that time. The manuscript content was last changed in commit `7372c06b97747694ac822b03ade8feb8671ce3a6`; the authority branch was at `9da90d26160c6cac0aa4257633b33b2bc3a1792e` when this checkpoint was captured.

The authoritative editable source remains `1008/manuscript/revision_01549_restored/manuscript_1008.tex`. The author-review TeX files are generated copies and must remain byte-identical to their active sources.

| File | SHA-256 |
|---|---|
| Active manuscript TeX | `0803055686f8d6660df18a909daceeb604e904f57b2b19c44d2dfc3b5bda6636` |
| Author-review manuscript TeX | `0803055686f8d6660df18a909daceeb604e904f57b2b19c44d2dfc3b5bda6636` |
| Active Supplement TeX | `1af44120a01d9098e226ebe78439e525fdb61c1815b3dfc1d862c00236596e88` |
| Author-review Supplement TeX | `1af44120a01d9098e226ebe78439e525fdb61c1815b3dfc1d862c00236596e88` |
| Main PDF | `4c0e0b2ea655a43a70bf8d96fc1371009c1497a820d53cae11b2cfd964a61ea8` |
| Marked-up PDF | `4dd6dc162f577ec7ad35b09def626599d0d293b79eab32863856504681d7dbab` |
| Supplement PDF | `1bbc6a56a38b67855a5103fec9292108a7306aa0b529f4ac56d56c99bf6e4321` |
| Response Markdown | `02bb0479490c2cfd0e08d7bcc3946a7f06d2b70dff758155ceab6a96aa76fb8d` |
| Response PDF | `fb43402f7ea929f65992c475eee0d82efd4d1833b7171caeea0a73a9f7f9eb9e` |
| 01549-to-1008 change log | `e1af646da01953c975cb726ae4677bdf875cb786f157408a5fe446e11391cdf5` |
| Clean LaTeX source ZIP | `308d27024adc174efb437c999c656e661b82ae2caf22bbcc55315317b99eab4a` |

The verified local backup, including the source TeX, generated PDFs, response, change log, and source ZIP, is at:

`/4T/MV-Painter-01549-local-records-20261009/20261009T023830Z/`

Its `MANIFEST.sha256` verifies every backup file. The separately retained local-only diagnostic JSON is in that backup's `local_only_json/` directory and is excluded from the Git package.

Backup manifest SHA-256: `82247470ff919f12769619465c6812bd8bbf8e89b5933cc934663e4bc5a7f332`.

## Required procedure for every later paper edit

1. Before editing, run `1008/scripts/record_manuscript_integrity.sh before-<short-label>` from this worktree root. This records a UTC timestamp and SHA-256 for the active paper sources and publication package files.
2. Edit the Level 2 manuscript or Supplement first. Do not edit generated author-review copies as independent sources.
3. Rebuild the affected PDFs and package, then run the same script with `after-<short-label>`.
4. Commit the source changes and the appended `MANUSCRIPT_REVISION_INTEGRITY.csv` rows together. Do not replace or delete older ledger rows. The recorded base commit and Git history identify the commit containing each revision.
5. Before pushing, inspect the exact staged path list and explicitly exclude JSON unless a file is demonstrated to be necessary and is separately authorized for the package. Local JSON files stay in local storage with their own checksum record.

The script uses a file-extension allowlist and never scans or records JSON files.
