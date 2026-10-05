# FRESH_CONFIRM_B combined formal campaign lock

Frozen: 2026-10-05 08:40 UTC, before any method output on FRESH_CONFIRM_B.

## Frozen cohort, data, and execution

- Use all 150 identities in `fresh_confirm_b/fresh_confirm_b.txt`, sorted by
  UID. UID-list SHA256:
  `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`.
- Recursive input manifest SHA256:
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Explicit data root: `data/fresh_confirm_v3_renders`.
- Runner SHA256:
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
- Config SHA256:
  `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- GeoTex checkpoint SHA256:
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- One run, 30 conditions × 150 objects = 4,500 unique object-condition
  rows. Two shards split by sorted UID-list index parity, one per GPU.
  Object seed is 42 + list index; initial latent seed is 42. All conditions
  share the same 50-step Euler sampler, 256×256 output, unique6 target views,
  model, source inputs, and metric implementation. Native cap semantics apply
  except the four explicitly marked true-global diagnostic conditions.
- Save raw object ledgers, per-object CSVs, per-step residual logs,
  predictions, and per-shard manifests. No object or row is removed based on
  its metric outcome. Complete the campaign before inspecting condition
  metrics; resume only from the per-object ledger under this same lock.

## Exact frozen condition family (30)

**A3b baseline and bounded map (16):**

- `a3_baseline`
- `a3_deep_W1`, `a3_deep_W2`, `a3_deep_W3`, `a3_deep_W4`, `a3_deep_W5`
- `a3_middle_W1`, `a3_middle_W2`, `a3_middle_W3`, `a3_middle_W4`, `a3_middle_W5`
- `a3_shallow_W1`, `a3_shallow_W2`, `a3_shallow_W3`, `a3_shallow_W4`, `a3_shallow_W5`

**Boundary sensitivity (4):**

- `boundary_late_onset_20_60_20`
- `boundary_late_onset_30_40_30`
- `boundary_late_onset_34_32_34`
- `boundary_late_onset_40_20_40`

**Cap/budget diagnostics (10):**

- `native_gfl`, `native_gfh`, `native_gc3`
- `true_global_0p80`, `true_global_1p25`, `true_global_1p675`, `true_global_2p50`
- `lfm_exact`, `layer_llh`, `layer_hll`

Condition scales and exact 50-step requested traces are recorded by the
runner manifest. No other condition may be substituted or added to this
campaign.

## A3b analysis family

Follow `A3B_PROTOCOL_LOCK.md`. Primary endpoint is FG-LPIPS; secondary is
FG-PSNR. For each endpoint, report the 15 paired cell-versus-baseline
contrasts plus the 8-df object-cluster Wald Layer×Window test, Holm corrected
as one family of 16. The repeated-measures GEE tests Layer, Window, and their
interaction with object clusters and robust covariance; correct its two
Layer/Window secondary omnibus tests together. Use 10,000 paired bootstrap
draws, seed 20261002, for cell effect CIs and direction-aware favorable
object rates. Report requested/effective scales, cap hits, dose proxies,
post-scale residual norms, and the failed development equal-dose criterion.
Do not call A3b dose-normalized.

## Boundary sensitivity analysis

Follow `STAGE_BOUNDARY_PROTOCOL_LOCK.md`. Primary endpoint FG-LPIPS.
Compare each of the four fixed pulses with the shared `a3_baseline`; Holm
correct the four contrasts. Compare the thirds-onset pulse with the other
three frozen onsets in a separate Holm family of three. Use paired object
bootstrap CIs (10,000 draws, seed 20261002). Report all effects; do not select
or tune a winning boundary.

## Cap/budget analysis

Follow `CAP_BUDGET_DIAGNOSTIC_PROTOCOL_LOCK.md`. For its seven named
contrasts, FG-PSNR is primary and FG-LPIPS secondary; apply one Holm family of
seven to each metric. The true-global path is a causal diagnostic, not a
deployment baseline. Report requested and actually applied scales, cap
activation, layer-wise post-scale residual norms, integrated residual
energy, paired effects, CIs, and favorable-object rates. Interpret only the
frozen contrast meanings in that lock; do not add contrasts or decompose
effects across mismatched endpoints.

## Interpretation boundary

This combined B campaign provides fresh evidence for the post-discovery A3b
map, fixed boundary family, and missing TGU-0.80 diagnostic. The earlier
FRESH_CONFIRM_300 results from B1/B2/C/E remain governed by their original
pre-outcome locks and are not relabeled as results on the new cohort. All
negative, null, dose-imbalanced, and metric-discordant outcomes must be
reported. No parameter or boundary may be selected from this cohort.
