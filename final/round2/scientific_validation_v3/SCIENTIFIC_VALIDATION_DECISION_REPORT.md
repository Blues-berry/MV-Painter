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

## PENDING (experiments running / queued)

- [ ] B3: TRUE-GLOBAL diagnostics + native controls (claim 1/6 decomposition)
- [ ] C: generic schedules under the authoritative runner (H4, claim 7)
- [ ] D: formal qualitative archive (24-object panels + contact sheet)
- [ ] E: prospective texture-complexity failure boundary (H5, claim 10)
- [ ] F: unified same-draw 3D bake (claim 9)
- [ ] G: MV-Adapter cross-backbone map (claim 8)

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
