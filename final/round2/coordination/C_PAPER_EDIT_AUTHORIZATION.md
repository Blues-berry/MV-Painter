# Codex C Paper-Edit Authorization

Issued by E: 2026-09-29 UTC

## Decision

G1–G4 are accepted with explicit limitations. Codex C is authorized to edit
the manuscript and response letter, subject to the evidence ledger and the
constraints below. This is a scoped release, not permission to improve the
narrative by changing experiments or metrics.

## Frozen evidence C may cite

- Main clean-v2 controlled rerun: checkpoint SHA-256
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` and
  strict holdout list SHA-256
  `a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044`.
- A-2 formal stage placement: 276 objects × four schedules, zero errors,
  finite metrics, 50 actual residual L2/RMS observations per schedule, and
  10,000 object-level paired bootstrap resamples.
- Saved-artifact Full-SSIM: PNG-reloaded float32 prediction versus raw
  RGBA/white-background float32 GT. C3/LHL minus fixed-mean is `+0.00749`
  with CI `[+0.00674,+0.00826]`; minus HLL is `+0.02151`
  `[+0.01984,+0.02319]`; minus LLH is `-0.00170`
  `[-0.00205,-0.00134]`.
- D: 12-object stratified Exact-GLB case study, 48 textured exports and 528
  unseen-view rows, with exporter reindexing, unavailable DISTS, no 12-object
  GT bake, and COLOR/SOURCE-FUSION limitations disclosed.
- B: within-backbone schedule evidence only; CAI is
  `undefined_set_valued`; official MV-Adapter pretraining UID disjointness is
  unknown.

## Required narrative

Frame TCAS as a training-free temporal stage-utility/mechanism study with
bounded support. It is valid to state that stage placement changes outcomes
under the frozen main-adapter protocol. It is not valid to state that LHL is a
unique or universal optimum: LLH is a counterexample, and fixed-low remains
competitive in the clean-v2 baseline.

## Prohibited edits or claims

- Do not restore the old `+0.96 dB` as a current strict result.
- Do not call the historical nominal 276 pool a strict independent holdout.
- Do not claim a unique CAI winner, universal cross-backbone mechanism,
  non-inferiority/equivalence, or population-level 3D superiority.
- Do not use the pre-save A-2 Full-SSIM CSV as the final Full-SSIM table;
  use the serialized branch and identify its provenance.
- Do not modify datasets, checkpoints, C3, metric implementations, frozen
  outputs, or experiment registry rows.

E must inspect C's diff, numerical citations and compiled tables before final
submission. This authorization does not itself approve submission.
