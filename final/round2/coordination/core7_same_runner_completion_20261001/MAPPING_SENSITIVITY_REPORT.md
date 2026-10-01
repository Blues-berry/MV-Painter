# REPORT — MV-Adapter 4→3 mapping sensitivity (M1 vs M3, 76-object holdout; 2026-10-01)

Protocol: MAPPING_SENSITIVITY_PROTOCOL.md (pre-registered before any M3 row).
All three canonical layer-wise conditions (L-LLH, L-LHL, L-FIX) were rerun
under the only distinct alternative contiguous mapping
(M3: shallow={p0,p1}, middle={p2}, deep={p3}; per-point vector
[0.41953, 0.41953, 1.19349, 1.19349]) with everything else byte-identical
to the frozen layer-wise runs (seed 20260928, 50 steps, exact geometry,
76 holdout objects). 3 x 76 = 228 new rows
(results/holdout_exact_mapM3_{llh,lhl,fix}_76/).

## Result: layer-vs-global direction is MAPPING-STABLE

Paired benefit-oriented deltas vs the SAME unchanged global rows, M1 vs M3
(labels per protocol; *-magnitudes in metric units):

| comparison | metric | M1 delta | M3 delta | label |
|---|---|---:|---:|---|
| P1 L-LLH − G-FL | psnr | +0.097 | **+0.147** | STABLE |
| P1 | ciede2000 | +0.344 | **+0.484** | STABLE |
| P1 | gt_rel_texture | +0.311 | **+0.409** | STABLE |
| P1 | fg_ssim | −0.0040 | −0.0049 | STABLE |
| P1 | edge_ssim | −0.0011 | −0.0011 | STABLE |
| P1 | fg_lpips | −0.0000 | +0.0010 | SENSITIVE (both ≈ 0) |
| P2 L-LLH − G-LLH | psnr | +0.101 | **+0.151** | STABLE |
| P2 | ciede2000 | +0.352 | **+0.492** | STABLE |
| P2 | gt_rel_texture | +0.286 | **+0.384** | STABLE |
| P2 | fg_ssim / edge_ssim | −0.004 / −0.001 | −0.005 / −0.001 | STABLE |
| P2 | fg_lpips | +0.0006 | +0.0016 | STABLE |
| P4 L-LHL − G-LHL | psnr | +0.102 | **+0.128** | STABLE |
| P4 | ciede2000 | +0.313 | **+0.433** | STABLE |
| P4 | gt_rel_texture | +0.289 | **+0.384** | STABLE |
| P4 | fg_ssim | −0.0032 | −0.0048 | STABLE |
| P4 | edge_ssim | −0.0006 | −0.0009 | ATTENUATED (tiny) |
| P4 | fg_lpips | +0.0001 | +0.0002 | STABLE |

Labels: **16/18 MAPPING_STABLE, 1 ATTENUATED (edge_ssim, |delta| ≤ 0.001),
1 "SENSITIVE" (P1 fg_lpips, −0.0000 → +0.0010 — a near-zero LPIPS flip with
|delta| ≤ 0.001; the frozen M1 report already classified LPIPS as ns).**

## Findings

1. The layer-wise effect on MV-Adapter (positive on PSNR / CIEDE2000 /
   GT-relative texture; small negative on FG-/Edge-SSIM) does NOT depend on
   the mapping choice: every primary fidelity metric is STABLE across M1
   and M3, and the alternative mapping makes the effect slightly STRONGER
   (PSNR +0.10 → +0.15; CIEDE2000 +0.34 → +0.48; texture +0.31 → +0.41).
2. The mapping-arbitrariness objection (Reviewer-2 risk) is therefore
   defused for the scale dimension: the layer-vs-global direction is a
   property of per-layer redistribution on this backbone, not of one
   arbitrary grouping.
3. Honest boundary note: the temporal-position dimension remains
   NOT_SUPPORTED on MV-Adapter (unchanged by this audit); and the one
   mechanical "SENSITIVE" label is a magnitude-trivial LPIPS flip
   (|delta| ≤ 0.001), consistent with the frozen M1 conclusion "LPIPS ns".
4. Per the protocol, M3 results are a sensitivity surface only; the frozen
   M1 mapping remains the pre-registered mapping of record.

Artifacts: MAPPING_SENSITIVITY_BOOTSTRAP.json,
MAPPING_SENSITIVITY_COMPARISONS.csv, results/holdout_exact_mapM3_*/.
