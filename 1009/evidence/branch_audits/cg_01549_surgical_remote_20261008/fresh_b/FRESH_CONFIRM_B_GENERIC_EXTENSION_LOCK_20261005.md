# FRESH_CONFIRM_B generic-schedule extension lock

Frozen 2026-10-05 14:51:48 UTC, before any generic-extension output.

## Scope and status

The combined `FRESH_CONFIRM_B_FORMAL_PROTOCOL_LOCK.md` fixed 30 conditions
and expressly excludes generic schedules. This extension uses a separate
run directory; it does not modify or amend that locked campaign.

The B core condition outcomes had already been opened before this extension
was designed. The four schedule shapes and both matching variants were
defined earlier in `PRIMARY_HYPOTHESES.md` and the frozen runner. No shape,
parameter, endpoint, comparison, object, or analysis choice here was selected
from B outcomes. Because this extension is post-lock and reuses the now-open
B cohort, report it as **within-cohort, post-lock sensitivity evidence**, not
independent confirmation. The pre-outcome FRESH_CONFIRM_300 Experiment C
remains the independent confirmatory result for H4.

## Frozen cohort and execution

- Cohort: all 150 identities from
  `fresh_confirm_b/fresh_confirm_b.txt`, UID-list SHA256
  `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`.
- Recursive source-input manifest SHA256:
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Runner SHA256:
  `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
- Config SHA256:
  `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Checkpoint SHA256:
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Separate run directory:
  `formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005`.
- Eight conditions × 150 objects = 1,200 rows. Two index-parity shards
  contain 600 rows each; seed policy, views, sampler, metrics, inputs, and
  checkpoint match the main B campaign. Run manifests, prediction PNGs, and
  residual logs are required. No object or row may be removed by outcome.

## Exact condition family

For each frozen shape `linear`, `cosine_bump`, `trapezoid`, and
`gaussian_peak`, include both runner variants:

- `gen_<shape>`: endpoint-matched native scale range;
- `gen_<shape>_bm`: multiplicative per-layer mean matched to LLH's
  `1.675/1.675/0.585` requested budget.

Native cap semantics remain in force. Do not tune any schedule or choose a
winner from this cohort.

## Frozen analysis

- Compare main-run `layer_llh` with each of the eight extension conditions on
  the same 150 objects.
- FG-PSNR is primary; FG-LPIPS is co-reported. Apply the pre-frozen H4 family
  of eight Holm tests separately to each metric.
- Use 10,000 paired object bootstrap resamples and seed 20261002; report
  direction-aware favorable-object rates and 95% CIs.
- Report requested-scale integrals, applied scales, cap activation,
  layer-wise post-scale residual norms/dose, fidelity metrics, and
  GT-relative texture errors. Explain that these comparisons are not
  independent confirmation and cannot replace the pre-outcome C result.
