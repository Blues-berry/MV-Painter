# E Final G1–G4 Evidence Review

Review time: 2026-09-29 UTC

## Gate decision

All four scientific gates are accepted with limitations. Codex C is released
for scoped manuscript and response-letter edits under
`C_PAPER_EDIT_AUTHORIZATION.md`. No further GPU experiment is required for
the current decision cycle.

| Gate | Decision | Evidence | Limitation that must remain |
|---|---|---|---|
| G1 Full-SSIM | `PASS_WITH_LIMITATIONS` | Controlled 12-object trace confirms identical A/B pre-save tensors and a nonzero PNG reload boundary. | Historical 300-object A tensors are missing; use the serialized PNG/raw-GT path and do not patch historical values. |
| G2 stage mechanism | `PASS_WITH_LIMITATIONS` | 276 objects × 4 schedules; zero errors; finite metrics; 50 actual residual steps; serialized Full-SSIM paired bootstrap. | C3/LHL beats fixed-mean and HLL but loses to LLH; no unique winner or universal schedule rule. |
| G3 cross-backbone | `PASS_WITH_LIMITATIONS` | B's frozen Exact MV-Adapter 76-object unified results and paired bootstrap. | CAI is set-valued; pretraining UID disjointness is unknown; no absolute cross-backbone PSNR claim. |
| G4 real 3D | `PASS_WITH_LIMITATIONS` | D's 12-object Exact-GLB bake: 48 textured exports and 528 unseen-view rows. | Stratified case study only; DISTS unavailable; no 12-object GT bake; exporter/color caveats remain. |

## G2 serialized Full-SSIM result

The formal runner's pre-save metrics are retained as audit evidence. The
paper-facing Full-SSIM result is the CPU-only recomputation from frozen PNG
predictions reloaded as float32 against original RGBA composited-over-white
float32 GT:

| Comparison | Mean delta | 95% paired CI | Direction-aware win rate |
|---|---:|---:|---:|
| C3/LHL − fixed-mean | `+0.00749` | `[+0.00674,+0.00826]` | `0.906` |
| C3/LHL − HLL | `+0.02151` | `[+0.01984,+0.02319]` | `0.996` |
| C3/LHL − LLH | `−0.00170` | `[-0.00205,-0.00134]` | `0.199` |

All values use 10,000 object-level paired bootstrap resamples with seed
`20260928`. The valid interpretation is an adapter- and protocol-scoped
stage-utility effect with a counterexample, not a universal LHL optimizer.

## Release narrative

Use the mechanism-study narrative: TCAS is a training-free temporal
stage-utility analysis with bounded application evidence. Retain the
serialization finding, the fixed-low tradeoff, the undefined CAI result, the
cross-backbone provenance boundary, and the stratified 3D bake limitations.

E must review C's final diff, numerical citations and compiled tables before
submission. This review does not authorize new experiments or submission by
itself.
