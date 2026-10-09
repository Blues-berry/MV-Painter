# R1.3 fidelity-language audit

This small audit record was selectively retained from archived source HEAD `e267b2d59bbb722827ca5ad72f7ca4475b13c8f1` (`refs/archive/codex/main-unification-20261009/detached/cg-closure-clean-audit`). The source worktree `/tmp/cg-closure-clean-audit` was clean at that committed HEAD and was left in place.

`R1_3_FIDELITY_LANGUAGE_AUDIT.csv` contains 149 sentence-level dispositions: 132 `REWRITE`, 9 `KEEP`, and 8 `REMOVE`. It distinguishes image-space variation proxies and illustrative panels from measured reference fidelity, material correctness, or a population-level preference result. These are editorial evidence classifications, not newly computed experiment outcomes. The core limitations already appear in the active 1008 manuscript and response; this file preserves their sentence-level audit trail.

## Provenance limits

- Of the 149 rows, 122 cite `final/final_0903.tex` with SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`, matching the authenticated `final_0903.tex` in the current 1008 source tree. Seven rows cite `final/supplementary_0903.tex` with SHA-256 `a4c797c3c90f6592bde08a802f6c67ec07e8c9c887472232adb1c5d66c5f854a`; that member was not independently checked in this branch audit.
- Twenty rows cite the auxiliary `CAG-S-26-01549 (1)(1).pdf` with SHA-256 `5de31993ec9f40a0e7a43d5c8d2ac0816a6d057e715348d23f2e157dc0aca6ba`. The authenticated submitted 01549 PDF in main has SHA-256 `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da`; they are not byte-identical. The audit is therefore retained as a historical wording crosswalk, not as authority for PDF identity.
- The source's `audit_r1_3_fidelity_language.py` (SHA-256 `7e7ea5bbec35e19051fddf61e687af4e72fa925c1c90cb1fb7ef2a6f1ebf58ae`) and the auxiliary PDF remain available through the local archive reference; they were not copied or rerun. No image, participant-level record, or generated figure was added.

This is an internal audit artifact, not part of the 1008 submission package. `SUBMISSION_APPROVED=NO`.
