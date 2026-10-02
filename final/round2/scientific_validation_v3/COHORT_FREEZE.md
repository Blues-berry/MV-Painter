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

## Pre-registered technical validity criteria (frozen BEFORE any render outcome is observed)

An object enters the selection pool only if ALL hold:

1. **GLB load success**: GLB loads via trimesh with non-empty geometry
   (≥1 mesh primitive, finite bounding box).
2. **Render success**: Blender (4.2.4, Cycles, same settings as
   `rendered_full`: 512×512 RGBA, ortho, ortho_scale=1.0, distance=3,
   HDRI `studio_small_08_1k.hdr`, scale=0.8, 17 fixed views) completes
   all 17 views: `image/000..016.png`, `normal/000..016.png`,
   `camera/000..016.npy`, `meta.npy`.
3. **Depth availability**: `depth/000..016.exr` produced by the render and
   converted to `depth_png/000..016.png` (16-bit).
4. **Foreground coverage bounds**: alpha-channel coverage
   (mask.mean(), same definition as `geotex/audit_clean_v2_raw_metrics.py`)
   for each of the 8 protocol views {000, 014} ∪ unique6 {0,15,12,16,13,14}
   must lie in **[0.02, 0.95]**.
   Rationale: <0.02 ≈ empty render; >0.95 ≈ degenerate full-frame fill
   under the normalized ortho scale.
5. **UID disjointness**: passes the audit in
   `uid_disjointness_audit.json` (11 named exclusion sources + rendered_full
   directory-name safety bucket).

## Selection rule

- Pool = objects passing criteria 1–5, sorted lexicographically by UID.
- `numpy.random.default_rng(20261002).choice(pool, size=300, replace=False)`
  (or `size=min(300, len(pool))` if fewer).
- The selection uses NO generated-method performance and NO image-quality
  information beyond the pre-registered coverage bounds.

## Freeze record

- Final cohort name: TBD
- N: TBD
- Selection pipeline commit SHA: TBD
- Freeze commit SHA: TBD
