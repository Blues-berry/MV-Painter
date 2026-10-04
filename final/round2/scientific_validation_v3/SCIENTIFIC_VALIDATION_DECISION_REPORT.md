# SCIENTIFIC_VALIDATION_DECISION_REPORT — DRAFT (in progress)

Status: DRAFT — updated as experiments complete. Final gate requires ALL
experiments terminated (A, B, C, D, E, F, G) and every verdict filled.
Do NOT edit the manuscript until this report is final (STOP RULE).

- Cohort: FRESH_CONFIRM_300 (frozen, seed 20261002)
- Runner: scripts/run_validation_v3_experiment.py (verbatim Core-7 per-object
  code path, latent seed 42, unique6, 50 Euler steps)
- Statistics: PRIMARY_HYPOTHESES.md (pre-registered), paired bootstrap 10k,
  seed 20261002, Holm per family

## Confirmed results so far

### Experiment A2 — raw layer × window map (descriptive)

- 15/15 cell effects Holm-significant on FG-LPIPS but tiny
  (|Δ| ≤ 0.006); Layer×Window interaction NOT supported
  (SS-interaction cluster bootstrap p=0.50; FG-PSNR p=0.51).
- Direction pattern: deep/middle late-window injections mildly improve
  FG-PSNR (middle_W5 +0.52 dB); shallow injections mildly harmful.

### Experiment A3 — dose-normalized map (CONFIRMATORY, primary H1)

- **Layer×Window interaction: NOT SUPPORTED** (p=1.0; the cell structure is
  MORE additive than the bootstrap null).
- Layer effect at EQUAL residual dose is decisive:
  FG-LPIPS marginals deep −0.0039 / middle −0.0005 / shallow +0.0175;
  FG-PSNR marginals deep +0.55 dB / middle +0.29 dB / shallow **−6.07 dB**.
  CIEDE2000: deep improves (W3/W4), middle improves broadly, shallow
  catastrophic (+15.9) everywhere.
- a_deep_W* and a3_deep_W* are identical conditions by construction
  (deep high 2.50 below cap in both maps) — internal consistency check.

### H2 (CONFIRMATORY) — LLH vs LFM-EXACT (exact 17/16/17 mean-matched constant)

- ΔFG-PSNR = +0.435 dB [0.356, 0.516], win 69%; ΔFG-LPIPS = −0.0045
  [−0.0052, −0.0039]. Holm family B1: both p=0.0002.
- Pre-registered equivalence NOT established (FG-PSNR CI upper 0.516
  exceeds the ±0.5 dB margin; FG-LPIPS CI inside ±0.01). Verdict:
  LLH's advantage over a budget-identical constant is real but small.

### H3 (CONFIRMATORY) — temporal-location contrasts

- LLH > HLL: +0.854 dB [0.658, 1.052]; LLH > LLL: +0.840 dB [0.747, 0.934];
  (descriptive: LLH > LHL +0.647 dB). All FG-LPIPS deltas favor LLH.
  Holm family B2: all p=0.0004. Late-high placement is genuinely better.

### Reconciliation

- The B-family schedule effects (0.4–0.9 dB) are consistent with the
  ADDITIVE layer+window structure of the A3 map: late-stage deep/middle
  energy helps, early-stage hurts; no interaction term is needed and none
  is supported.

### Experiment B3 — TRUE-GLOBAL decomposition (CONFIRMATORY, claims 1/5/6)

Uniform uncapped scaling is decisively worse; the decomposition is additive:
  * cap/shallow protection alone: native_gfl vs TRUE-GLOBAL-1.25 = **+1.60 dB** [1.37, 1.82]
  * layer redistribution at equal budget: LFM-EXACT vs TRUE-GLOBAL-1.675 = **+2.99 dB** [2.43, 3.55]
  * temporal variation on top (H2): LLH vs LFM-EXACT = +0.43 dB
  * sum ≈ LLH vs TRUE-GLOBAL-1.675 (+3.43 dB) ✓ no interaction residual
  * GFH vs TRUE-GLOBAL-2.50 = +4.66 dB; all FG-LPIPS deltas favor layer-aware.
Residual budgets: log E ratios confirm requested-vs-effective dose accounting;
no_adapter excluded from ratios (zero residuals).

### H4 (CONFIRMATORY) — LLH vs generic schedules (C)

LLH beats cosine bump (+0.46 dB), trapezoid (+0.30), Gaussian peak (+0.53)
and ALL budget-matched variants (+0.15..+0.59), Holm family C: 15/16
rejected at p≤0.0016. **Exception: per-layer linear warm-up is statistically
equivalent to LLH on FG-PSNR (+0.005, p_holm=0.81)** (FG-LPIPS slightly
favors LLH, Δ=−0.001, p_holm=0.0016). The advantage over generic families is
therefore shape-dependent, not universal.

### E (CONFIRMATORY, H5) — prospective texture-complexity failure boundary

REPLICATED on the fresh cohort. Δ(LLH−GFL) vs GT-only texture statistics
(all Spearman CIs exclude 0):
  * ΔFG-PSNR ~ GT HF energy rho=−0.691; ~ GT Laplacian var rho=−0.524
  * ΔFG-LPIPS ~ GT HF energy rho=+0.677; ~ GT Laplacian var rho=+0.604
Quartiles (GT Laplacian variance): LLH wins +4.14 dB (92% win) in Q1,
+1.13 dB in Q2, and LOSES in Q3 (−0.09) / Q4 (−0.03). LLH's average
advantage (+1.29 dB) is carried by texture-poor objects; on texture-rich
objects GFL wins — LLH under-delivers high-frequency detail exactly where
GT texture is rich.

### D — formal qualitative archive

24 pre-frozen objects × (GT + 7 conditions) panels + contact sheet built
(formal_qualitative_archive/); 0 missing panels.

## PENDING (running)

- [x] B3, C, D, E complete (above)
- [ ] G: MV-Adapter cross-backbone map — shard1 complete (800 rows); shard0
      resumed after excluding 1 GLB rejected by the mesh loader (technical
      failure, documented in mvadapter_manifest_v3.json)
- [ ] F: unified same-draw bake — 20/24 objects (4 excluded: mesh without UV
      layer, original-UV protocol requirement; see excluded_uv_missing.json);
      unseen-view + seam metrics after bake completes

## CLAIM TABLE (draft; verdicts finalized at gate)

| Claim | Draft verdict (pending remaining experiments) |
|-------|-----------------------------------------------|
| 1 layer-dependent effect | Supported so far (A3 equal-dose marginals; B3 pending) |
| 2 timestep-dependent effect | Partially supported (A2 window cells; A3 window marginals small) |
| 3 layer × timestep interaction | **Not supported** (A2 raw p=0.50; A3 dose-normalized p=1.0) |
| 4 1/3 stage boundaries | Heuristic only so far (no interaction; boundary-aligned responses absent) |
| 5 LLH gain ≠ budget | Supported, small effect (H2: +0.435 dB over exact mean-match; equivalence marginally not met) |
| 6 layer allocation > truly uniform | PENDING (B3 TRUE-GLOBAL) |
| 7 L-TCAS vs generic schedules | PENDING (C) |
| 8 transfers to MV-Adapter | PENDING (G; pilot suggests weak response in [0.75,1.0] window interventions) |
| 9 practical 3D texturing | PENDING (F) |
| 10 texture-rich failure boundary | PENDING (E) |
