# MV-Adapter Layer-Mapping Sensitivity Report (final_audit_20261001, Phase 2)

Date: 2026-10-01. Protocol: `MVADAPTER_MAPPING_SENSITIVITY_PROTOCOL.md`
(pre-registered, commit `a6d281b`, before any mapping-variant inference).
Analysis script: `analyze_mapping_sensitivity_20261001.py`; bootstrap records:
`MVADAPTER_MAPPING_SENSITIVITY_BOOTSTRAP.json`. Run artifacts:
`results/mapping_sensitivity/` (preflights) and
`results/holdout_exact_layer_llh_mapB211_76/` (main run, 76/76 finite rows).

## 1. What was tested

Reviewer-2 question: *is the layer-wise transfer result an artifact of the arbitrary
4→3 partition?* With 4 ordered injection points and 3 contiguous groups there are
exactly three partitions, and under the frozen source profile (middle = deep = 1.65)
they reduce to two distinct execution states:

| Variant | Partition (shallow/middle/deep) | Per-point multipliers | Disposition |
|---|---|---|---|
| C (frozen, reference) | (1,1,2) | [0.41953, 1.19349, 1.19349, 1.19349] | already run (`holdout_exact_layer_llh_76`) |
| D = (1,2,1) | (1,2,1) | identical to C by arithmetic | degenerate; verified by 3-object identity check |
| B′ = (2,1,1) | (2,1,1) | [0.52018, 0.52018, 1.47982, 1.47982] (weighted mean = 1.0) | full 76-object run, L-LLH |

B′ keeps the frozen normalization rule (per-point budget-neutral, weighted mean 1.0)
and changes only the group-to-point assignment.

## 2. Identity preflight (both PASS, bitwise)

1. Control re-run of C (obj_0024/0025/0026, shared GPU): `per_object_metrics.csv`
   **bitwise identical** to the archived L-LLH rows — the runner is deterministic under
   concurrent GPU workloads.
2. Degenerate partition D: **bitwise identical** to C on the same three objects — the
   arithmetic degeneracy is empirically confirmed; no GPU run for D×76 is needed.

## 3. Main result — L-LLH(B′) vs the existing panel (76 objects, seed 20260928)

Benefit-oriented deltas (positive favors the left condition; ΔE00 / GT-texture
lower-better); `*` = 95% CI excludes 0; 10k object-level percentile bootstrap.

| comparison | psnr | fg_ssim | edge_ssim | fg_lpips | ciede2000 | gt-texture |
|---|---:|---:|---:|---:|---:|---:|
| L-LLH(B′) − G-FL | +0.06553 | −0.00412* | −0.00091 | −0.00020 | +0.28445* | +0.27687* |
| L-LLH(B′) − G-LLH | +0.06940 | −0.00439* | −0.00088 | +0.00045 | +0.29203* | +0.25175* |
| L-LLH(B′) − L-LLH(C) | −0.03109 | −0.00014 | +0.00019 | −0.00016 | −0.05997 | −0.03391 |

Row 3 is the partition effect at constant budget: **no metric separates B′ from C** —
the two partitions are statistically indistinguishable on every surface.

## 4. Verdict against the pre-registered interpretations

**Outcome 1 (mapping-stable), with one pre-registered nuance.**

- The layer-wise advantage replicates under the alternative partition on the same
  primary metrics as the frozen partition C: CIEDE2000 and GT-relative texture error
  significantly favor the layer condition over both global controls (CIs exclude zero),
  matching C's P1/P2 pattern; FG-SSIM retains the same small significant reverse; LPIPS
  remains not separated.
- Nuance (reported, not hidden): the PSNR advantage, significant under C
  (+0.0966* / +0.1005*), is directionally consistent but not significant under B′
  (+0.0655 / +0.0694).
- Combined with the D≡C bitwise identity, the layer-wise effect on MV-Adapter is
  **robust to the tested contiguous layer partitions**: the three defensible
  partitions produce either bitwise-identical results (D) or statistically
  indistinguishable ones (B′ vs C), and the layer-vs-global advantage survives the
  re-partition. This is a statement about the tested partitions, not a claim of
  invariance over all conceivable assignments.

> Allowed wording: "Layer redistribution transfers robustly across the tested
> contiguous layer partitions" (or "is not driven by a single arbitrary partition") —
> with the PSNR-significance nuance if PSNR is cited. Avoid "invariant to the exact
> layer partition".

A companion variant (M3, frozen-value re-assignment, mean 0.8065) is pre-registered in
`coordination/core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_PROTOCOL.md`
by the parallel task; it changes the overall residual budget as well as the assignment.
**Update (2026-10-01 evidence convergence): the M3 runs have landed** — 3 × 76 = 228
rows committed at `75a4068`
(`results/holdout_exact_mapM3_{llh,lhl,fix}_76/`, 77-row per-object CSVs each) and
reported in `core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_REPORT.md`:
**16/18 MAPPING_STABLE**, 1 ATTENUATED (edge_ssim, |Δ| ≤ 0.001), 1 magnitude-trivial
LPIPS flip (|Δ| ≤ 0.001; M1 LPIPS already ns). Under M3 the layer-vs-global primary
effects are slightly **stronger** (P1 PSNR +0.10 → +0.15, CIEDE2000 +0.34 → +0.48,
GT-texture +0.31 → +0.41). M3 is a *budget-changing* axis (per-point mean 0.8065 ≠ 1)
and must not be mixed with B′'s budget-neutral comparison; the frozen M1 mapping
remains the pre-registered mapping of record, and no post-hoc partition selection is
made in either direction.
