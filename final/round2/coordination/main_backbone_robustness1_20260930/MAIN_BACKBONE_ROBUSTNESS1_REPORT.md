# MAIN_BACKBONE_ROBUSTNESS1_REPORT — strict-276 Core-5 under an independent reference-preprocessing realization

Branch `codex/main-backbone-robustness1-20260930` (base `codex/next-review-response-20260930` @ `edfb8d0`).
Runs executed 2026-09-30 12:40–16:14 UTC on GPU 0 (RTX 5090), acquired only after the
cross-backbone agent's panel released it (no preemption; its GPU-1 session untouched).
Protocol frozen in `PROTOCOL_LOCK.md` before any Realization-1 metric existed.

## Headline

**Primary robustness gate: `ROBUSTNESS_SUPPORTED`.**
The layer-LLH advantage over Global fixed-low on the strict-276 holdout is essentially
unchanged under a fully independent, pre-frozen reference-preprocessing realization
(R1: `object_seed = 10042 + idx` vs R0: `42 + idx`):

| LLH − GFL, FG-PSNR (dB) | mean paired delta | 95% CI (10k percentile bootstrap, seed 20260930) | win rate |
|---|---|---|---|
| Realization-0 (frozen official rows) | +3.244 | [+2.936, +3.542] | 242/276 |
| Realization-1 (this run) | +3.233 | [+2.928, +3.527] | 241/276 |

Across all 4 core comparisons x 7 metrics (28 cells): **27 STABLE_STRONG,
1 STABLE_DIRECTIONAL, 0 UNSTABLE**, and the Core-5 ranking is **identical in R0 and R1
on all 7 metrics** (LLH first everywhere; zero mid-rank flips).

## Design (frozen before running)

- Core-5 only: GFL 1.25 / GC3 1.25-2.50-1.25 / LFM 1.65-1.65-0.58 / L-LHL / L-LLH —
  definitions byte-identical to the frozen confirmation runners; no additions, no
  re-selection (no HLL/LLL/LHH/HLH/HHH/TRB/FAC, no new schedules; none were looked at).
- Dataset: frozen strict-276 clean-v2 holdout list (SHA-256 `a6aa8ab6…d044`), same order,
  no resampling; config `clean_holdout.yaml`; checkpoint `geotex_step_0002000.pt`
  (SHA-256 `0618d6b2…14c0`); unique6 views @256; 50 steps Euler; latent seed 42;
  metric path `geotex.eval_exploration.compute_metrics` (7 pre-save metrics).
- R1 changes exactly one thing vs R0: the reference-preprocessing seed namespace
  (`10042 + object_idx` instead of `42 + object_idx` for python/np/torch before
  `collate_batch`). Initial latent (seed 42), VAE-eps seed (re-seed 42 before
  generation), schedules, caps, and metric code are bit-identical.
- Per-object-per-method code path is a verbatim copy of
  `scripts/run_layer_confirmation_276_20260930.py`. In-run integrity: every object's
  cond/target/normal/depth/global-embed/initial-latent tensors must hash identically
  across the 5 methods — **0 aborts in 1380 rows**.

## Gates

### Shared-input preflight — PASS

`ROBUSTNESS1_SHARED_INPUT_AUDIT.md/.json` (+ pass1/pass2 raw tables): 10 fixed
strict-276 objects (frozen sample `random.Random(20260930)`, indices 11–256 — the same
10 objects as the R0 audit JSON) x 5 methods; SHA-256 over raw reference PNGs, cond raw
+ resized, VAE cond-latents, targets, normals, depth, masks, geo features, global
embeds, initial latents (GPU fp16 + CPU fp32), scheduler timesteps/sigmas.

- pass1 vs pass2 (separate processes): **0 mismatches / 50 rows**
- cross-method within process: **0 mismatches / 4 pairs x 10 objects x 2 passes**
- cross-realization vs frozen R0 audit: deterministic components match R0 **500/500**
  (protocol identity), reference-derived components differ from R0 **150/150**
  (genuine independence).

### R0 anchor re-check — exact reproduction

10 objects re-run under the R0 namespace (`42 + idx`, `layer_llh`) through this task's
runner: **max |delta| = 0.0 on all 7 metrics** vs the frozen R0 rows
(`r0_anchor_llh_10/anchor_comparison.json`). Two consequences: (a) the task runner's
per-object path is execution-identical to the frozen runner; (b) the R0 realization
reproduces bit-exactly across processes, so the pre-registered R0-C3 completion rows
are exactly paired with the frozen R0 rows.

### Row completion

| Block | Rows | Status |
|---|---|---|
| R1 Core-5 (`realization1_core5/`) | 1380 / 1380 | complete, no integrity aborts |
| R0 anchor (`r0_anchor_llh_10/`) | 10 / 10 | bit-exact vs frozen |
| R0 GC3 completion (`r0_completion_global_c3/`) | 276 / 276 | pre-registered matrix completion |

## Full R0 vs R1 stability (4 comparisons x 7 metrics)

Mean paired deltas (first minus second), 95% percentile bootstrap CIs (10,000
resamples, seed 20260930, object-level):

| Comparison | Metric | R0 delta [CI] | R1 delta [CI] | Class |
|---|---|---|---|---|
| LLH − GFL (primary) | fg_psnr | +3.244 [+2.936,+3.542] | +3.233 [+2.928,+3.527] | STABLE_STRONG |
| | fg_ssim | +0.0633 [+0.0582,+0.0683] | +0.0632 [+0.0581,+0.0681] | STABLE_STRONG |
| | fg_lpips | +0.0308 [+0.0283,+0.0331] | +0.0307 [+0.0283,+0.0331] | STABLE_STRONG |
| | full_psnr | +2.599 [+2.353,+2.838] | +2.587 [+2.341,+2.825] | STABLE_STRONG |
| | full_ssim | +0.0076 [+0.0067,+0.0084] | +0.0076 [+0.0067,+0.0085] | STABLE_STRONG |
| | full_lpips | +0.0119 [+0.0098,+0.0141] | +0.0119 [+0.0098,+0.0141] | STABLE_STRONG |
| | edge_ssim | +0.0276 [+0.0242,+0.0308] | +0.0276 [+0.0242,+0.0308] | STABLE_STRONG |
| LLH − GC3 | fg_psnr | +2.037 [+1.803,+2.264] | +2.030 [+1.795,+2.257] | STABLE_STRONG |
| | fg_ssim | +0.0324 [+0.0290,+0.0358] | +0.0322 [+0.0287,+0.0356] | STABLE_STRONG |
| | fg_lpips | +0.0207 [+0.0190,+0.0224] | +0.0207 [+0.0191,+0.0223] | STABLE_STRONG |
| | full_psnr | +1.860 [+1.688,+2.029] | +1.853 [+1.682,+2.021] | STABLE_STRONG |
| | full_ssim | +0.0004 [−0.0003,+0.0010] | +0.0003 [−0.0004,+0.0009] | STABLE_DIRECTIONAL |
| | full_lpips | +0.0041 [+0.0024,+0.0058] | +0.0039 [+0.0022,+0.0057] | STABLE_STRONG |
| | edge_ssim | +0.0198 [+0.0172,+0.0223] | +0.0199 [+0.0173,+0.0224] | STABLE_STRONG |
| LLH − LFM | fg_psnr | +0.875 [+0.769,+0.982] | +0.867 [+0.762,+0.972] | STABLE_STRONG |
| | fg_ssim | +0.0070 [+0.0052,+0.0089] | +0.0069 [+0.0051,+0.0087] | STABLE_STRONG |
| | fg_lpips | +0.0089 [+0.0081,+0.0097] | +0.0089 [+0.0081,+0.0097] | STABLE_STRONG |
| | full_psnr | +1.311 [+1.219,+1.400] | +1.307 [+1.216,+1.395] | STABLE_STRONG |
| | full_ssim | +0.0011 [+0.0006,+0.0016] | +0.0012 [+0.0006,+0.0017] | STABLE_STRONG |
| | full_lpips | +0.0094 [+0.0082,+0.0105] | +0.0093 [+0.0081,+0.0104] | STABLE_STRONG |
| | edge_ssim | +0.0113 [+0.0101,+0.0125] | +0.0113 [+0.0101,+0.0125] | STABLE_STRONG |
| LLH − LHL | fg_psnr | +1.001 [+0.907,+1.097] | +0.992 [+0.899,+1.087] | STABLE_STRONG |
| | fg_ssim | +0.0174 [+0.0154,+0.0195] | +0.0172 [+0.0151,+0.0193] | STABLE_STRONG |
| | fg_lpips | +0.0110 [+0.0101,+0.0118] | +0.0109 [+0.0101,+0.0118] | STABLE_STRONG |
| | full_psnr | +1.193 [+1.123,+1.262] (276/276) | +1.186 [+1.118,+1.254] (276/276) | STABLE_STRONG |
| | full_ssim | +0.0028 [+0.0023,+0.0033] | +0.0027 [+0.0022,+0.0032] | STABLE_STRONG |
| | full_lpips | +0.0290 [+0.0262,+0.0319] | +0.0287 [+0.0259,+0.0316] | STABLE_STRONG |
| | edge_ssim | +0.0203 [+0.0187,+0.0219] | +0.0204 [+0.0188,+0.0220] | STABLE_STRONG |

Machine-readable: `R0_R1_DIRECTION_STABILITY.csv`, `R0_R1_STABILITY_SUMMARY.json`,
`paired_bootstrap.json`. Win rates for every cell are in the CSV/JSON.

### Ranking sensitivity

Core-5 order (best→worst) per metric — **R0 and R1 identical on all 7 metrics**:

| metric | R0 ranking | R1 ranking |
|---|---|---|
| fg_psnr | LLH > LFM > LHL > GC3 > GFL | same |
| fg_ssim | LLH > LFM > LHL > GC3 > GFL | same |
| fg_lpips | LLH > LFM > LHL > GC3 > GFL | same |
| full_psnr | LLH > LHL > LFM > GC3 > GFL | same |
| full_ssim | LLH > GC3 > LFM > LHL > GFL | same |
| full_lpips | LLH > GC3 > LFM > GFL > LHL | same |
| edge_ssim | LLH > LFM > GC3 > LHL > GFL | same |

- LLH above LHL in both realizations on all 7 metrics: YES.
- LLH above GFL in both realizations on all 7 metrics: YES.
- Mid-rank flips ({GFL,GC3,LFM,LHL} internal orders): **none** — no hidden flips.
- Known non-LLH sensitivities persist unchanged: LHL stays last on Full-LPIPS in both
  realizations (the honest global-control Full-LPIPS advantage reported in the paper),
  and LFM/LHL order swaps between FG and Full/Edge metrics in both realizations alike.

### Absolute-value shifts between realizations (context, not pooled)

R0→R1 per-method mean shifts are small and uniform (FG-PSNR: −0.026 to −0.038 dB;
FG-LPIPS: +0.0003 to +0.0004), and per-object FG-PSNR correlates at **r = 0.996**
between realizations. The two realizations are reported strictly separately (no
552-row pooling anywhere).

## Input-realization difference (task item 11)

`REFERENCE_REALIZATION_DIFFERENCE.csv` + `_summary.json` (all 276 objects, both
realizations; passive RNG recording — draws untouched):

| Statistic | median | IQR | p05 | p95 |
|---|---|---|---|---|
| stretch scale (width/height, both realizations) | ≈1.00 | ≈[0.75, 1.23] | ≈0.55 | ≈1.45 |
| cond pixel MAE (R0 vs R1) | 0.0307 | [0.0175, 0.0496] | 0.0052 | 0.0915 |
| cond SSIM (R0 vs R1) | 0.928 | [0.889, 0.957] | 0.824 | 0.978 |
| cond-latent L2 diff | 455.7 | [373.1, 565.2] | 237.3 | 738.8 |
| cond-latent cosine sim | 0.940 | [0.901, 0.962] | 0.830 | 0.984 |

Interpretation: R1 is a genuinely different reference realization (latent cosine 0.94,
not a near-duplicate), drawn from the same augmentation distribution as R0
(scale medians/IQRs agree) — so the stability result above is measured on a meaningful
perturbation, not on two identical inputs.

## The six required answers

1. **Is Realization-1 truly independent of the existing reference realization?**
   Yes. Preflight: all 150 reference-derived hashes differ from R0 while all 500
   deterministic-component hashes match (protocol identity, draw independence); §11:
   cond pixel MAE median 0.031, cond SSIM 0.928, cond-latent cosine 0.940 across 276
   objects; stretch-scale distributions of R0 and R1 agree (same U(0.5,1.5) source).

2. **Is Core-5 strictly shared-input per object?**
   Yes, verified twice: preflight (0 cross-method mismatches in two independent
   processes) and in-run integrity hashing on all 1380 formal rows (0 aborts; any
   cond/target/normal/depth/global-embed/initial-latent mismatch would have aborted).

3. **Is LLH > Global fixed-low direction-consistent across R0/R1?**
   Yes — better on 7/7 metrics in BOTH realizations, every CI excludes zero in both,
   deltas agree to ≤0.012 dB (FG-PSNR +3.244 → +3.233; Edge-SSIM +0.0276 → +0.0276).

4. **Is LLH > Layer-LHL direction-consistent across R0/R1?**
   Yes — better on 7/7 metrics in BOTH realizations, every CI excludes zero in both
   (FG-PSNR +1.001 → +0.992; Full-PSNR 276/276 wins in both realizations).

5. **Which metrics are sensitive to the reference-preprocessing realization?**
   At the population level, none of the 7 metrics shows meaningful realization
   sensitivity: absolute means shift ≤0.04 dB / ≤0.0005 LPIPS, per-object r = 0.996,
   all 28 paired-delta cells keep sign, 27/28 keep CI-excludes-zero (the single
   exception, LLH−GC3 Full-SSIM, has a negligible ~0.0003 effect whose CI crosses
   zero in BOTH realizations — direction-consistent, magnitude trivial). Method-level
   ranks are identical in both realizations. This controlled result also shows that
   the historical archived-LHL-vs-replica gap (14.78 vs 12.97 dB, r = 0.66) cannot be
   attributed to reference-realization randomness alone — consistent with that
   record's existing quarantine as a non-reproducibility caveat (its per-object delta
   vs the replica is position-dependent, +5.0 dB on objects 0–69 decaying to +0.6 dB,
   pointing to a different data/process state at archived-run time, not to the
   augmentation draw).

6. **Overall classification:**
   **ROBUSTNESS_SUPPORTED** — primary gate direction matches R0, all paired CIs
   exclude 0 in both realizations (27/28 STABLE_STRONG, 0 UNSTABLE), no attenuation
   beyond noise (effect sizes agree to ~0.01 dB), no systematic reversal, no
   mid-rank flips. Per the frozen gate definitions: not SUPPORTED_WITH_ATTENUATION
   (no shrinkage), certainly not NOT_SUPPORTED.

## Provenance & artifacts

- Runner: `scripts/run_robustness1_core5_20260930.py` (per-object block verbatim from
  the frozen confirmation runner; only the seed namespace / output dir / manifest /
  in-run integrity logging are new). Anchor re-check proves execution equivalence.
- All raw rows: `realization1_core5/` (per-method CSVs + combined
  `per_object_metrics.csv` + `rows.json` + manifests), `r0_completion_global_c3/`,
  `r0_anchor_llh_10/`. Top-level copies per the output contract:
  `per_object_metrics.csv`, `aggregate_metrics.csv`.
- Hashes: `ARTIFACT_SHA256SUMS.txt`; protocol values: `RUN_MANIFEST.json`.
- No third realization was created; no schedule was added or re-selected; no paper
  text, supplementary, or response-letter file was touched.

## Notes

- The R0 audit MD prose lists sample indices [3,23,45,...] while the R0 audit JSON
  (machine record) contains [11,25,113,141,157,207,214,236,239,256]; this task's audit
  used the frozen `random.Random(20260930)` draw and therefore matches the R0 JSON.
  The frozen R0 MD prose line is stale; the R0 JSON is authoritative.
- R0's same-runner set lacked global_c3; the pre-registered R0-C3 completion
  (276 rows, R0 namespace) fills that cell so all four core comparisons have R0/R1
  anchors. It is matrix completion under the frozen protocol, not a new method.
- The equal-budget pilot artifacts remain out of the paper evidence set (unchanged).
