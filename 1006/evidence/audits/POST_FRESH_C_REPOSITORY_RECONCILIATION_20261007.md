# Post-Fresh-C repository reconciliation — 2026-10-07

## Git identity and local/public comparison

- Public branch `codex/scientific-validation-v3-20261006`: `f5bad8a1e6ca4265c1823eaa26b2775313de4c96` (matches the requested public SHA).
- Local branch `codex/scientific-validation-v3-20261002` at `5c2c8829a1e19b42837761160dc4c14cf8f09045`.
- The local HEAD is an ancestor of the public tip: **0 local-only commits, 218 public commits beyond local HEAD**. This is not a linear “files after f5” range.
- The worktree was not reset, staged, committed, fetched, or pushed. It remains dirty: **7,206 tracked status entries and 440 untracked file entries** in the reconciled project scope.
- Current local files were compared byte-for-byte with public remote blobs. The inventory has 7,650 rows: 83 already-public exact matches, 7,556 local paths absent from the public tree, 7 local paths with changed contents, and 4 public participant-level paths not represented as dirty local files.
- Formal local evidence paths absent from or different from the public tree: **7,413**, listed path-by-path in [`POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv`](POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv). The manifest classifies participant-level and third-party asset/derivative paths separately.

Because the local branch is behind and the tree is highly dirty, this reconciliation is an inventory only. No reset, new staging operation, commit, fetch, push, merge, cherry-pick, cleanup, or history rewrite was performed; pre-existing staged/dirty state was preserved.

## Evidence status

| Evidence item | Current status | Record |
|---|---|---|
| Fresh C primary | PASS — N=300, 1200/1200 | `data/fresh_c/FRESH_C_INTEGRITY_GATE.json`; 7 frozen endpoints. |
| LLH/generic-linear addendum | PASS — same N=300 cohort, 600/600 | `data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json`; 21 frozen tests. |
| Sign/direction audit | PASS — 28 checks, 0 errors | `data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json`. |
| Fresh C atlas | PASS — 20 locked rank-stratum groups; all 20 source licenses currently verify as CC BY; attribution schedule prepared | `figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json`; `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`. |
| Authority ledger | PASS as evidence bookkeeping — 26 runs, 243 condition records | `evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`; validation record remains separate from science freeze. |
| Novelty audit | COMPLETE; R2.1 OPEN / VENUE RISK | `evidence/audits/FINAL_R21_CONTRIBUTION_AUDIT.md`. |
| GLB feasibility | Sampler inventory complete; synthetic checks 11/11 PASS; full 24-object native-UV/alpha gate FAIL | `FRESH_C_GLB_NATIVE_SAMPLER_AUDIT.md`; new 3D panel formally retired. |
| Readiness | HOLD / not ready for manuscript rewrite or release | `gates/NON_HUMAN_EVIDENCE_FREEZE_VERDICT_20261007.md` supersedes the earlier dated readiness snapshot for this closure. |

The numerical authority file has 148 rows and includes the frozen Fresh C endpoint contrasts, selected interaction and boundary results, execution records, and source hashes. Figures B/C were regenerated locally from canonical Fresh C paired-delta tables. A clean-checkout rebuild of this current candidate has not passed.

## Files prohibited from any new public/supplement package

- Participant-level files present in the public remote tree: `HUMAN_STUDY_RAW_RESPONSES.csv`, `HUMAN_STUDY_SLOT_ASSIGNMENT.csv`, `HUMAN_STUDY_PAIR_MAPPING.csv`, and `HUMAN_STUDY_OBJECT_UIDS.csv`. The decision is `PUBLIC_RAW_HUMAN_DATA=NO`; no response values or results were analyzed in this phase.
- Source GLBs and the 9 `UNKNOWN` Fresh C cohort assets are excluded from the candidate package. The 20-model Figure D atlas is eligible only with the prepared row-level CC BY attributions. UID-linked per-object tables are not part of the proposed public package; aggregate results may be retained.
- The preserved historical 48-row ledger still records 43 `FIGURE_ONLY` and 5 `UNKNOWN` rows; its legacy assets are not current candidate figures.
- Forensic/debug history, caches, and experiment run logs in a reviewer-facing package.

## Conditional candidates for an anonymous supplement

After a clean-candidate rebuild and author release approval, the candidate list may include aggregate [`FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv`](FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv), analysis/figure scripts, frozen non-human protocols, synthetic sampler validation, Figures A–C, Figure D with [`FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`](FRESH_C_ATLAS_ATTRIBUTION_20261007.csv), and aggregate Fresh C tables. Figures E/G contain metric plots rather than source-asset imagery. No source GLBs, the 9 unknown assets, or UID-linked per-object tables are eligible under this scope; the 300-row rights inventory remains an audit record, not a release manifest.

