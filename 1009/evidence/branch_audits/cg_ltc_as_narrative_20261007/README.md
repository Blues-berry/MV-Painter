# 2026-10-07 narrative branch: compact numerical audit

This selected bundle preserves a hash-pinned reaggregation audit from the historical narrative-convergence branch. It is a reproducibility check for the branch's previous revision authority, not a replacement for the later active 1008 claim ledger or manuscript values.

## Source and rerun

- Source branch tip/WIP: `ecbb246b76cccf148dfbbdfa85515b53590aa584`; WIP-before source: `bf1dc3d41edd597421c067a972c82abfb4b8fdf7`.
- Archive ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/cg-ltcas-narrative-convergence-20261007`.
- The exact historical verifier and its relative `1006/` inputs are kept under `bundle/`. The bundle is 13 files / 4,055,726 bytes; it contains four compact per-object metric/delta CSV inputs, a 162-row historical numerical-authority table, the verifier, and the small analysis/output records whose hashes it checks. It has no rendered images, GLBs, model weights, caches, or participant-level human data.
- Re-run from the repository root with:

  `python 1009/evidence/branch_audits/cg_ltc_as_narrative_20261007/bundle/1006/scripts/verify_bundled_numerical_authority.py`

- The rerun passed all 42 selected authority rows at tolerance `2e-10`; maximum absolute differences were `2.22e-16` (effect), `5.55e-17` (median), `1.11e-16` (lower CI), and `5.20e-18` (upper CI). The generated JSON is byte-identical to the archived output, SHA-256 `ae6a325f507018e0b084d29d132c7058e9e58d162a50c34a42e03491c7d1b7b4`.
- Two input CSVs are already present byte-for-byte in the current 1008 R2 evidence directory. They are duplicated inside this isolated bundle only because the historical verifier pins its original relative paths. No raw rendered data were copied.

The verifier reaggregates saved paired metrics; it does not rerun image generation, reproduce rendered outputs, or make the historical candidate paper the current authority. Use current `1008/authority/CLAIM_LEDGER.csv` and the active 1008 manuscript for present claims. Any small C3−GFH bootstrap interval provenance difference remains recorded in the earlier C3−GFH audit; no paper value was changed here.

## Human-data publication boundary

The exact sanitized decision cited by the current claim ledger is restored at `1006/evidence/audits/PUBLIC_HUMAN_DATA_DISPOSITION_20261007.md`. SHA-256: `57fc15b1130d45ddffdb6ff7441d397bcc1005101cb2fa46933c09cfd462b4af`. It contains a historical public-release risk disposition, not participant responses. `PUBLIC_RAW_HUMAN_DATA=NO` remains the rule; no participant-level file was copied or interpreted.

No active manuscript, Supplement, response, figure, or submission-package file was changed. `SUBMISSION_APPROVED=NO`.
