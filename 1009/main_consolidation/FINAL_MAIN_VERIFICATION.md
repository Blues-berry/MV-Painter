# Final Main Verification

Verified from `/4T/MV-Painter-main` on 2026-10-09 after the repository report commit was pushed to the authorized private remote.

| Check | Result |
|---|---|
| Authoritative branch | `main` |
| Base SHA at start of this Git pass | `02ab94ad5e6539bf010a001994d57ff3231f7b4c` |
| Local main equals `mvpainter/main` after normal push | `YES` |
| Push type | Normal fast-forward; no force push |
| Other remotes changed | `NO` (`origin` and `upstream` untouched) |
| Main worktree clean after commit | `YES` |
| Unexpected tracked generated outputs under the four new ignore paths | `NONE` |
| Global JSON/CSV/PDF ignore rule added | `NO` |
| Main manuscript changed during Git-only phase | `NO` |
| 1008 integrity entries checked | `7/7 MATCH` |
| Journal submission performed | `NO` |

The checked 1008 files were the active manuscript TeX, Supplement TeX, response letter, manuscript PDF, Supplement PDF, response PDF, and LaTeX source ZIP. Their SHA-256 values matched the latest recorded entries in `1008/MANUSCRIPT_REVISION_INTEGRITY.csv` at the Git-phase checkpoint. The authenticated 01549 source was not edited.

`git diff --check` passed. The four generated-output examples matched the new ignore rules; representative protocol JSON, result CSV, and report PDF paths remained trackable. No application source change was made in this repository phase, so no runtime/model test suite was run.

The exact full SHA of the final pushed `main` is included in the completion handoff. The local and remote refs were compared after the push.

`MAIN_IS_CANONICAL = YES`  
`MAIN_LOCAL_REMOTE_MATCH = YES`  
`MAIN_WORKTREE_CLEAN = YES`  
`SCIENTIFIC_DATA_PRESERVED = YES`  
`MANUSCRIPT_AND_SUBMISSION_PACKAGE_INTACT = YES`  
`SUBMISSION_APPROVED = NO`
