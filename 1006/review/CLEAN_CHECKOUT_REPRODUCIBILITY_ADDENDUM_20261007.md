# Clean-checkout reproducibility audit — current reviewer-closure candidate

Audit date: 2026-10-07

## Determination

**`CLEAN_CHECKOUT_REPRODUCIBILITY = OPEN`** for the current candidate. The evidence and manuscript were checked in the active worktree, but an exact clean checkout of the edited candidate is not available: the authoritative branch still points to `cf6287731bcf3ad31d135abf1feee64662a20c39`, while the manuscript, reviewer artifacts, authority additions, and compiled PDFs are uncommitted or untracked. A checkout of that HEAD would not contain this candidate.

This is a package/rebuild limitation, not a reason to rerun image generation or training. The historical report [FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md](../evidence/audits/FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md) describes a prior branch snapshot and has been labeled accordingly.

## Read-only source and output checks

| Component | Current verification | Clean-checkout limit |
|---|---|---|
| Fresh C C3−GFH post-hoc audit | Source-integrity manifest reports `PASS`; the direction audit reports `R1_4_DIRECTION_ERRORS = 0`. The seven result rows are hash-linked in both numerical authority tables. | The canonical Fresh C raw CSV, cohort and input manifests, runner/checkpoint identities, and output hash manifests are referenced under `/4T/CXY/MV-Painter/1006/data/fresh_c/`, which is not tracked in this candidate HEAD. |
| Fresh B C3−GFH supporting sensitivity | Recomputed all seven paired endpoint summaries from the existing raw file; values match the prior audit. Source SHA-256: `ce7ba03f6dcb9f1d275b389c633e23dc544404eeac4ddf090e90a11ad278e081`. Script SHA-256: `23dd8e2a4c0e23f4b514cda471a8483bc3be056c0860786579932cf1691a5070`. | Raw source remains in the read-only `/4T/CXY/MV-Painter` workspace and is absent from the current candidate HEAD. It is classified only as `RETROSPECTIVE_POST_HOC_SUPPORTING_SENSITIVITY`; it is not pooled with Fresh C. |
| Reviewer visual candidate pool | The machine audit is `PASS`; the 300-object index, rights/attribution fields, panel hashes, selection metadata, and curation groups are present. Final main-paper UIDs and reasons are recorded. | Candidate images and pool files are not part of the branch HEAD. A clean rebuild of all visual panels has not been demonstrated. |
| Authority tables and reviewer response | Both CSV authority files parse with consistent columns. Fresh B and Fresh C C3−GFH rows carry source, script, and output hashes. The required R1.4 opening sentence is exact. | Current edits are not in HEAD; these tables and response cannot be obtained by checking out the current branch commit. |
| Revised manuscript and supplement | Both sources compiled successfully in the active worktree. The main PDF has 8 pages (SHA-256 `61463087f35b8b90bcf4f9ab60b4ffd1196ec332a83ec8263311bbee35880f29`); the supplement has 4 pages (SHA-256 `ea22cc2f33cdbd63d06f48c8cdfac6ed07d301b74ff3910341c128882f952859`). Page/line references in the external response were checked against the main PDF text layer. | PDF outputs are ignored by the repository rules, and the source edits/figure assets are not committed. A clean checkout cannot reproduce these PDFs yet. Any later source edit requires recompilation and page/line revalidation. |

## Scope and limitations

- The existing Fresh C integrity and direction audits were consumed; no image-generation experiment was started.
- Fresh B's hash-pinned raw file was read for an audit-level recomputation only. The outputs remain a separate retrospective/post-hoc sensitivity.
- Historical generation reproducibility remains limited: this package does not contain all model predictions, residual logs, render inputs, and other payloads needed to rebuild every image from inference.
- No participant-level human responses were accessed or analyzed. No training, GPU job, or submission action occurred.

## Required to close this gate

Create a reviewed candidate commit/package containing the revised sources, authority and response files, approved figure assets, and available analysis inputs; check out that exact candidate into a clean directory; rerun the analysis/package rebuilds that the included inputs support; compile both PDFs; and record which generation steps remain irreproducible. Until that exact-candidate rebuild is done, this gate stays `OPEN`.
