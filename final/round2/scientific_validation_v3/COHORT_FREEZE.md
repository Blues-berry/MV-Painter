# COHORT_FREEZE — Phase III

Status: **AUDIT IN PROGRESS** (this file will be finalized at cohort freeze)

## Rules (locked)

- The existing strict-276 has been inspected repeatedly during revision and
  must NOT be described as a new unseen holdout for experiments designed
  after 2026-10-01. It may only serve as STRICT276_REEVALUATION.
- Selection must depend ONLY on pre-generation technical properties:
  - GLB load success
  - required geometry availability
  - render success
  - foreground coverage bounds
  - UID disjointness
- Do NOT select by generated-method performance.
- Deterministic selection seed: **20261002**
- If >= 300 technically valid disjoint objects are available → `FRESH_CONFIRM_300`.
  Otherwise use the maximum >= 150 if possible, called `FRESH_CONFIRM_N`.
  If none can be constructed → strict-276 as STRICT276_REEVALUATION only.

## Exclusion list (any UID appearing in the following is excluded)

- [ ] main adapter training pool (1118)
- [ ] FAC/strong-residual training pool (1706)
- [ ] original 300 evaluation pool
- [ ] probe-24
- [ ] strict-276
- [ ] scale-sweep 50
- [ ] texture-audit 26
- [ ] bake-12
- [ ] MV-Adapter Exact-76
- [ ] MVDiffusion-75
- [ ] any previous exploratory or robustness cohort

## Freeze artifacts (to be produced)

- [ ] `fresh_confirm_300.txt` (or `fresh_confirm_N.txt`)
- [ ] `fresh_confirm_300_manifest.csv`
- [ ] `UID_DISJOINTNESS_AUDIT.md`
- [ ] `SHA256SUMS.txt`

## Freeze record

- Final cohort name: TBD
- N: TBD
- Selection pipeline commit SHA: TBD
- Freeze commit SHA: TBD
