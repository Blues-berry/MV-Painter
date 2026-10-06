# COHORT_IDENTITY_AUDIT — FRESH_CONFIRM_300 (2026-10-05)

Scripts: `build_fresh_cohort.py`, `audit_uid_disjointness.py` (frozen at commits
c1fb1b7 → ac62fbe, 2026-10-02, before any formal outcome). Independent re-derivation
performed by reading the funnel artifacts; selection re-derived from the recorded seed.

## 1. Funnel re-derivation (not copied — recomputed from artifacts)

| Stage | Artifact | Recomputed |
|---|---|---|
| Local GLBs | 1638 (1626 hf-objaverse + 12 smithsonian) | ✓ |
| UID-disjoint candidates | `fresh_disjoint_candidates.txt` = 508 (all hf) | ✓ — exclusion union = 2006 normalized identifiers incl. all of `data/train_data/rendered_full/` (2014 dirs) |
| GLB load OK | `glb_load_valid.txt` = 507; `glb_load_failures.json` = 1 (KeyError on a missing referenced texture) | ✓ 508 → 507 |
| Rendered OK | `render_log.json`: 507 attempts, success 493, timeout 14 | ✓ 507 → 493 |
| Technically valid | `technical_validity_audit.json`: pool 507, complete_and_inbounds 450, selected 300, seed 20261002 | ✓ 493 → 450 → 300 |
| Selected | `fresh_confirm_300.txt` = 300 rows; manifest 300 rows × 8 cols | ✓ |

Selection rule (code): `valid.sort()` → `np.random.default_rng(20261002).choice(valid, 300,
replace=False)`, then re-sorted. Deterministic given the frozen valid list.
`stratification_summary.json` records the cohort SHA256 (b81bd142…).

## 2. Leakage / disjointness

`uid_disjointness_audit.json` + `UID_DISJOINTNESS_AUDIT.md`: all identifiers normalized
(lowercase, `-`/`_` stripped) and intersected against 12 named historical sources plus the
safety bucket `rendered_full/`. Recomputed verdict: **zero intersection** with main adapter
training (1118), FAC training (1706/1200), old evaluation (300 + clean-v2 300), probe 24,
strict 276, replacement pool 189, bake 12, MV-Adapter 76, MVDiffusion 75.
Scale-sweep 50 and texture-audit 26 have no standalone UID files; RUN_BUDGET.md traces both
as subsets of probe-24/strict-276, so they are transitively covered. **No training/evaluation
UID overlap** — the P0 leakage gate passes.

## 3. Per-object assets (300/300 verified present)

Render root `data/fresh_confirm_v3_renders/<uid>/` holds 507 object dirs. Every selected UID
has 17× image, 17× normal, 17× depth_png, 17× camera, `meta.npy`, and
`embeddings/global_embeds.npy` (spot checks at cohort positions 1/150/300 + 30-object deep
sample in `audit_scripts/AUDIT_DEEP_VERIFICATION.json`). No stale symlinks to
`rendered_full`; GT mask cache `mask_gt_cache/` holds 300 entries (vestigial for the v3
runner — masks are computed from alpha at run time).

## 4. Duplicate-content finding (P1)

Input-fingerprint uniqueness across the 300 objects (SHA256 over target‖normal‖depth‖
global_embeds‖init_latent hashes; see OBJECT_IDENTITY_PER_ROW.csv) flags exactly one group:
- `0099ab6d44b742b0b62a40a7c70c29b1` (GLB 000-053)
- `0130e5149b6f4156b9799daa5e4006da` (GLB 000-103)

Verified root cause: the two objaverse GLBs have **different file bytes** but produce
**pixel-identical renders in all 17 views × {image, normal, depth_png}** (51/51 compared),
hence identical embeddings and identical tensor hashes. This is a duplicate visual asset in
the source dataset, **not** a pipeline substitution (silent-substitution audit: 0 triggers).

Impact: the cohort contains **299 distinct visual contents across 300 UIDs**. All statistics
treat the two as separate objects (consistently, in every campaign). Effect on group means is
diluted (≈1/300 weight); a leave-one-out sensitivity is trivial if desired. Classified **P1**:
document in the paper's cohort description ("300 objects; one duplicated source asset,
299 unique contents") or drop one member and re-run summary statistics — no experiment rerun
required.

## 5. Verdict

COHORT_IDENTITY: **PASS with one documented P1** (single duplicate source asset). Funnel
numbers, determinism, disjointness, and asset completeness all verified independently.
