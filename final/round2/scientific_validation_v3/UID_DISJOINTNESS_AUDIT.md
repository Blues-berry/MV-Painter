# UID_DISJOINTNESS_AUDIT — Phase III Fresh Cohort

- Date: 2026-10-02
- Script: `audit_uid_disjointness.py` (this directory)
- Raw audit JSON: `uid_disjointness_audit.json`
- Candidate list: `fresh_disjoint_candidates.txt`

## Exclusion sources loaded (normalized identifiers)

| Source | Path | Entries |
|--------|------|---------|
| main adapter training pool | `mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt` | 1118 |
| FAC/strong-residual pool (2000-list) | `data/train_data/rendered_full/train_objects_2000.txt` | 1706 |
| FAC/strong-residual pool (1200-list) | `data/train_data/rendered_full/train_objects_1200.txt` | 1200 |
| old eval-300 | `data/train_data/rendered_full/test_objects_300.txt` | 300 |
| eval-300 clean-v2 | `final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt` | 300 |
| probe-24 clean-v2 | `final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt` | 24 |
| strict-276 clean-v2 | `final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt` | 276 |
| replacement candidate pool | `final/round2/clean_dataset_v2/replacement_candidate_pool_189.txt` | 189 |
| old→new UID mapping (old side) | `final/round2/clean_dataset_v2/old_to_new_uid_mapping.csv` | 300 |
| bake-12 manifest | `final/round2/main_adapter_clean_v2/exact_baking_cohort_manifest.csv` | 12 |
| MV-Adapter Exact-76 | `final/round2/mvdiffusion/data_manifest_holdout_exact_76.json` | 76 |
| MVDiffusion-75 | `final/round2/mvdiffusion/data_manifest_holdout_exact_75.json` | 75 |

- Scale-sweep-50 and texture-audit-26 rows resolve to probe-24 / strict-276
  position indices (`obj_XXXX`) mapped by `old_to_new_uid_mapping.csv`; their
  UID sets are therefore subsets of the sources above (verified in the Phase
  III cohort audit notes; see `RUN_BUDGET.md` provenance chain).
- Safety bucket: every directory name in `data/train_data/rendered_full/`
  (2014 dirs) is additionally excluded.

## Local GLB inventory

| Location | GLBs |
|----------|------|
| `~/.objaverse/hf-objaverse-v1/glbs/` | 1626 |
| `~/.objaverse/smithsonian/objects/` | 12 |
| **Total inventoried** | **1638** |

## Result

| Metric | Count |
|--------|-------|
| Normalized excluded identifiers (union of sources) | 2006 |
| Local GLBs clashing with any source | 1130 (incl. all 12 smithsonian) |
| **Fresh disjoint candidates** | **508** (all hf-objaverse-v1) |

Subsequent pipeline (`build_fresh_cohort.py`):

- GLB load validation: **507 / 508 passed** (1 failure — see
  `glb_load_failures.json`).
- Rendering, depth conversion, coverage audit, and deterministic selection
  (seed **20261002**) follow the criteria pre-registered in
  `COHORT_FREEZE.md`.

## Disjointness guarantee

Any UID in the final cohort is absent from: both training pools (1118 + FAC
1706/1200), the original eval-300 (old and clean-v2 forms), probe-24,
strict-276, the replacement pool, bake-12, MV-Adapter Exact-76,
MVDiffusion-75, and all rendered dataset directories. The cohort therefore
qualifies as a genuinely unseen confirmatory cohort for experiments designed
after 2026-10-01.
