# FINAL_EVIDENCE_AUTHORITY.md (Phase 18 — agent B)

Sweeps the coordination records and assigns exactly one authority per
evidence class. Older files are marked SUPERSEDED/HISTORICAL, not deleted.

## Authority map (unique per class)

| evidence class | UNIQUE authority | superseded/historical |
|---|---|---|
| claim ledger + strength/width | `final_audit_20261001/claim_evidence_matrix.md` (parallel session, maintained) + this audit's `CROSS_BACKBONE_CLAIM_BOUNDARY.md`, `RESIDUAL_BUDGET_CONFOUND_AUDIT.md` width rules | `C3_TCAS_CLAIM_LEDGER_20260929.md`, `E1_CLAIM_EVIDENCE_FREEZE_20260929.md` → HISTORICAL |
| experiment registry | `EXPERIMENT_REGISTRY.csv` (keep updated at landings) | `EVIDENCE_DATA_INDEX_*_20260929.md` → HISTORICAL |
| reproducibility/provenance manifest | `final_audit_20261001/FINAL_REPRODUCIBILITY_MANIFEST.json` (+ rescued_tmp) | `E0A_EVIDENCE_FREEZE_20260929.md` → SUPERSEDED |
| strict-276 main evidence | confirmation + Core-7 + robustness artifacts (frozen runner 273c2f75, checkpoint 0618d6b2) | clean-v2 four-condition and stage-placement panels → LEGACY_UNCAPPED_PANEL (within-panel use only) |
| LHL history | `final_audit_20261001/ARCHIVED_LHL_PROVENANCE_AUDIT.md` + `historical_result_exclusion_reason.md` (Case B) | `LAYER_LHL_HANDOFF_20260929.md`, DECISION_LOG D18/D19 entries → HISTORICAL (D19 disposition stands) |
| metric direction/statistics | `final_audit_20261001/metric_direction_audit.md` + `statistics_reproducibility_audit.md` + agent B independent recomputation (digit-match) | `METRIC_SIGN_CONVENTION_ERRATUM.md` (robustness dir) → folded, keep as erratum |
| texture fidelity | `final_audit_20261001/STRICT276_TEXTURE_FIDELITY_AUDIT.md` (+ texture_audit/) | older LapVar-only framings → SUPERSEDED |
| bake evidence | `final_audit_20261001/baking_consistency_report.md` + `BAKE_SEAM_AUDIT_20261001/` (corrected seam) | archived uv_seam_discontinuity=0.0 → INVALID |
| cross-backbone | repo-root `CROSS_BACKBONE_VALIDATION_MVADAPTER.md` / `_MVDIFFUSION.md` + `EVIDENCE_INTEGRATION_STATUS_20261001.md` | `CROSS_BACKBONE_EVIDENCE_FREEZE_20260929.md` → SUPERSEDED |
| mapping sensitivity | `core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_REPORT.md` + `final_audit_20261001/MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md` | earlier BLOCKED notes → SUPERSEDED |
| reviewer readiness | `final_audit_20261001/FINAL_REVIEWER_READINESS_REPORT.md` + this audit's `FINAL_FORENSIC_AUDIT_REPORT.md` | `EXPERT_REVIEW_*_20260929.md` → HISTORICAL |
| coordination state | `EVIDENCE_INTEGRATION_STATUS_20261001.md` | `EXECUTION_STATUS_20260929.md`, `AGENT_ORDERS.md`, `BLOCKERS.md`, `CURRENT_ITERATION_DECISION_20260929.md` → HISTORICAL |

## Rules going forward

1. No file may claim authority for a class already listed above; updates land
   in the authority file (or a dated successor referenced from it).
2. All legacy panels keep their artifacts but inherit the
   LEGACY_UNCAPPED_PANEL caveat from
   `CROSS_RUNNER_SCALE_SEMANTICS_AUDIT.md`.
3. The two active audit directories (`final_audit_20261001` — parallel
   session; `forensic_audit_agentB_20261001` — this session) are complementary;
   the final report indexes both.
