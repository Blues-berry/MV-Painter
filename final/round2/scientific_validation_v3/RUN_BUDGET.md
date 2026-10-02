# RUN_BUDGET — Phase III

Run-count accounting for formal conditions. "Object-condition" = one
generation of one object under one condition (6 views each).

## Condition inventory

| Phase | Conditions | Cohort | Object-conditions |
|-------|-----------|--------|-------------------|
| A1 preflight | 16 (instrumentation sanity) | 3 dev objects | 48 |
| A2 formal map | 16 (15 interventions + baseline) | FRESH_CONFIRM_N | 16N |
| A3 dose-normalized map | 16 | FRESH_CONFIRM_N | 16N |
| B1 | 2 (LLH, LFM-EXACT) | FRESH_CONFIRM_N | 2N |
| B2 | 5 (LLL, HLL, LLH, LHL, LHH) | FRESH_CONFIRM_N | 5N |
| B3 | 6 (3 TRUE-GLOBAL + 3 NATIVE controls) | FRESH_CONFIRM_N | 6N |
| C | 9 native/generic + family A + family B variants | FRESH_CONFIRM_N | ≥9N (A/B split TBD at freeze) |
| D visualization | 8 (GT-only + 7 conditions) | 24 stratified objects | 168 |
| E | reuses A/B/C outputs (LLH, GFL rows) | FRESH_CONFIRM_N | 0 (derived) |
| F unified bake | 7 + 1 optional | 24 stratified objects | ~192 |
| G MV-Adapter | 16 (reduced or full A replication) | MV-Adapter cohort | 16N_G |

## Notes

- LLH and other overlapping rows (e.g., B2 LLH = B1 LLH) must be generated
  once in one runner namespace and reused; never pool capped/uncapped runner
  outputs.
- FRESH_CONFIRM_N expected ≈ 150–300; budget is finalized after cohort freeze.
- Every run must satisfy the provenance checklist in MASTER_PROTOCOL_LOCK.md.
- Preflight results never enter scientific conclusions.

## Status

- [ ] Cohort freeze (fixes N)
- [ ] A1 preflight
- [ ] Formal campaigns A–G
