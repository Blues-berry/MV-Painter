# Fresh C evidence packet index — 2026-10-06

> The image-space packet remains valid for its frozen scope; its human/freeze gate summary predates the 2026-10-07 policy update. Current all-evidence freeze status is YES for bounded claims. See `../../gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md` and `../human_study/HUMAN_EVIDENCE_DISPOSITION_20261007_ZH.md`.

**Scope:** image-space evidence is closed for the registered Fresh C primary and the separately locked revision-era addendum. This packet does not close human fidelity, new 3D baking, source rights, paper-wide reconstruction, or R2.1. `SCIENTIFIC_EVIDENCE_FREEZE=NO`.

## Cohort, protocol, and integrity

| Deliverable | Authority |
|---|---|
| Frozen cohort and exact UID order | `1006/data/fresh_c/FRESH_C_COHORT_MANIFEST.json`, `1006/data/fresh_c/fresh_c_objects.txt`; N=300, UID-list SHA-256 `d93881865b6478dd31222a51c7d3ebafe44839fd5e1b76c5eb9605d3f1fdfa58` |
| Original four-condition protocol | `1006/evidence/protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md`; unchanged primary is `native_gc3 − native_gfl`, FG-PSNR |
| Primary integrity | `1006/data/fresh_c/FRESH_C_INTEGRITY_GATE.json`; PASS, 1,200/1,200 rows |
| Primary per-object results | `1006/data/fresh_c/runs/c3_confirmation/per_object_metrics.csv`; analysis `1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json` |
| Addendum lock | `1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.md` and `.json`; revision-era prospective, motivated by earlier Fresh B, not an original preregistration or independent cohort |
| Addendum integrity and outcomes | `1006/data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json` (PASS, 600/600); `1006/data/fresh_c/runs/revision_era_addendum/per_object_metrics.csv`; analysis `1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json` |
| Independent direction/statistics audit | `1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json`; 28 recomputations, zero discrepancies. Reader's guide: `1006/evidence/audits/DIRECTION_AND_SIGN_AUDIT_20261006.md` |
| Reproducible gate → analysis → sign-check entry point | `1006/scripts/run_fresh_c_locked_analyses_with_sign_audit.py`; analysis JSON hashes were byte-identical before/after its verification run |

## Figures and object-level tables

All figures below are downstream of both integrity gates and the frozen analyses.

| Deliverable | Authority |
|---|---|
| Twenty-group comparison atlas | `1006/figures/strategy_comparison_gallery/fresh_c_final/20_groups_contact_sheet.png`; individual panels under `panels/`; selection and hashes in `gallery_manifest.json` and `gallery_asset_sha256.csv` |
| Caption, selection rule, and caveats | `1006/figures/strategy_comparison_gallery/fresh_c_final/README.md` |
| Six-method × 300-object complete index | `1006/figures/strategy_comparison_gallery/fresh_c_final/six_method_complete_object_index.csv` and `.json`; seven endpoint-specific ranks, no combined score |
| Per-object paired contrasts | `all_contrast_object_deltas.csv`; endpoint-sorted rankings under `rankings/` |
| Cohort effects and uncertainty | `cohort_contrast_summary.csv`, `cohort_contrast_summary_ranked_within_family.csv`, and `cohort_contrast_forest.png` |
| Method-level ranking pages | `strategy_ranking_pages/C3_GFL.png`, `LLH_GFL.png`, `linear_GFL.png`; comparisons remain endpoint- and family-specific |

Individual panels do not carry significance marks. The 20 examples are not an independent sample and were not used to select human-study objects. The full paired cohort, not the displayed cases, defines every cohort-level estimate.

## Current interpretation

- C3−GFL FG-PSNR is +0.522 dB (95% object-bootstrap CI [+0.404, +0.641], N=300; 68.7% of objects favor C3); the original primary paired test is p=5.70×10⁻¹⁶. This is a revision-era follow-up, not replication of the original preregistration.
- C3 and LLH have endpoint- and object-dependent differences. LLH−linear FG-PSNR is not detected as different and has no equivalence margin. LLH−linear FG-LPIPS is +0.001372 (95% CI [+0.000762, +0.002081], six-test Holm p=0.000114), favoring generic linear because lower LPIPS is better.
- These image-space endpoints do not demonstrate perceived fidelity, unseen baked-view quality, full-PBR quality, seam quality, a dose-independent mechanism, or a global schedule winner.

The controlling condition-level provenance index is `1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`; its validator result is `1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_VALIDATION_20261006.json`.
