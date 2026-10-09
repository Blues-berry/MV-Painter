# Repository consolidation and 01549 evidence gate — 2026-10-08

> **Superseded gate snapshot.** This earlier gate predates the author's explicit authorization to restore and revise the official post-first-round 01549 submission. Its “no manuscript edit” and “wait for confirmation” decision, and its then-current FAC/preference disposition, do not govern the completed 1008 second-round package. See `submission_1008_final/01549_TO_1008_CHANGELOG.md` and `audits/ROUND1_01549_TO_ROUND2_1008_MAPPING.md` for the current record.

## Decision

CASE B is retained: R2 novelty is partially strengthened, with venue risk open; R1 has image-space evidence and a bounded historical N=20 3D result, but not a general visual-fidelity closure. No fresh GPU run, training, bake, human study, or seam experiment is needed for the truthful bounded revision described in the existing decision. This gate authorizes no manuscript edit.

## Gate values

| Gate | Status | Evidence and reason |
|---|---|---|
| WORKTREE_BACKUP_VERIFIED | PARTIAL | At audit time, the path/hash census covered 331,401 entries; status files and seven critical checkpoints were copied and verified, and 434 ignored paths mapped to byte-identical copies. The ignored payload archive stopped at 283,133,993,984 bytes without final member verification; 323,122 ignored paths had no verified copy, including 291.577 GB of unique regular-file content and 103 symlinks. Full independent backup was not established. After this gate was committed, the user requested removal of the task-created backup roots and all their contents. Those copies and the .partial archive are therefore gone; original source data was left untouched. The committed path/hash manifest is historical inventory metadata, not a backup. See REPOSITORY_STATE_20261008.md. |
| AUTHORITATIVE_BRANCH_IDENTIFIED | YES | Private remote branch head rechecked at 3e592037; local annotated protection tag and new active branch/worktree point to that commit. See authority/BRANCH_AUTHORITY.md. |
| MANUSCRIPT_BASELINE_VERIFIED | YES | The only body source hash matches 203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01; the submitted PDF is preserved and identified. See authority/BRANCH_AUTHORITY.md. |
| EVIDENCE_AUTHORITY_COMPLETE | PARTIAL | Numeric authority and key Fresh C / historical N=20 evidence are indexed with limitations. Formal editor decision provenance is not present in tracked coordinator material, and some historic execution provenance remains bounded. See authority/EVIDENCE_INDEX.md and CLAIM_LEDGER.csv. |
| HISTORICAL_CONFLICTS_ISOLATED | PARTIAL | Branches and source copies are indexed; no merging or deletion occurred. Some older results lack complete source-run proof and duplicate evidence remains physically present. See audits/ARCHIVE_AND_DEDUP_DECISION.csv. |
| PUBLIC_RELEASE_SAFE | NO | Participant-level responses, assignments/linkage, reviewer materials, path-bearing files, and rights gaps remain in public refs/history. See audits/PUBLIC_RELEASE_SECURITY_REAUDIT.md. |
| READY_FOR_01549_SURGICAL_EDIT | NO | Stage 4 requires author confirmation under the task. Archive independence, editor-decision provenance, historical conflicts, and release risks also remain open. No TeX has been edited. |

## Stage 3 evidence decision

The Fresh C primary cohort is distinct from FRESH_CONFIRM_300 and has N=300 unique objects and 1,200 rows over four conditions. The primary C3−GFL foreground-PSNR contrast is +0.522352 dB (95% object-bootstrap CI [+0.404160, +0.640669]); its registered FG-LPIPS contrast is −0.005345 (CI [−0.006326, −0.004403]). The distinct addendum is the same cohort and not an independent replication. It shows that LLH is not C3 and that Generic Linear is an adverse comparator for C3 on key endpoints: C3−Generic Linear FG-PSNR −0.592918 and FG-LPIPS +0.013512. LLH−Generic Linear PSNR does not detect a difference and does not establish equivalence; LPIPS favors Generic Linear. LLH−C3 mean FG-PSNR is +0.621 dB (95% CI [+0.391, +0.855]) but the median is in the opposite direction, while LPIPS favors LLH.

Historical N=20 is an unlit base-color unseen-view analysis over 11 frozen cameras and the UV-compatible subset of 20/24 assets. C3−GFL FG-PSNR is −0.066 dB (95% CI [−0.413, +0.290]), FG-LPIPS is −0.004719, and CIEDE2000 is +0.133 (CI [−1.161, +1.319]); endpoints are mixed. No valid PBR or seam result exists. The Fresh C 24-object bake failed its technical gate and is retired. The old seam metric is retired. The 20 cleared figure assets were selected after metrics and are illustrative only; source GLBs remain uncleared. Human advantage is not confirmed. SSI prior art means no general scheduling novelty claim; retain TCAS/C3 and remove CAI optimality and FAC claims under the existing decision.

## Boundary and next action

No 01549 TeX, submitted figure, or original PDF was edited. No experiment or publication operation was started. Stop here and wait for the author's explicit confirmation before Stage 4. Public release remediation is a separate author/data-governance decision.
