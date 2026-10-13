# Intervention Identity and Phase A Audit

## Status

The static identity gates and all dynamic B0/B+/B− identity gates pass. No quality conclusion is drawn from these implementation checks.

## Frozen source and camera identity

- The cohort and camera mappings come from the immutable Fresh C bake handoff `BAKE_INPUT_HANDOFF_V3.json` and its linked `BAKE_INPUT_FREEZE.json`. The full frozen generation cohort contains ten objects; this study selected indices 0, 1, 2, 3, 4 and 7 before producing new conditions.
- In all six selected objects, slot 0 is the reference view. Its raw camera is 14 for objects 0–3 and 0 for objects 4 and 7. It is not rotated. The six-slot mappings, including the two CCW-rotated tiles for the reversed input arrangement, were cross-checked against the source image alpha masks, camera file hashes and recorded poses.
- `prepare_batch` packs `[B, 6, C, H, W]` as a 3-row by 2-column mosaic; the intervention uses exactly `slot = row*2 + column`. The historical 11/11 tile mapping audit remains preserved. The new unit tests also exercised all 720 six-view permutations, including permutation-equivariant scale assignment.
- The untouched source handoff and the linked freeze manifest are hash-verified again when the counterfactual bake handoff is built. New generated views are stored separately under this research folder.

## Schedule and native caps

Fixed Mean is the exact scalar B0 path: request 1.65 for every sampler step and every adapter group. New B+/B− logic is used only at sampler steps 34–49 for deep and middle groups. Shallow remains scalar and is never reallocated.

| Condition | Requested scale order at affected deep/middle steps | Six-view applied sum |
|---|---|---:|
| B0 | `[1.65, 1.65, 1.65, 1.65, 1.65, 1.65]` | 9.90 |
| B+ | `[1.85, 1.61, 1.61, 1.61, 1.61, 1.61]` | 9.90 |
| B− | `[1.45, 1.69, 1.69, 1.69, 1.69, 1.69]` | 9.90 |

Deep and middle caps are 3.0 and 3.5, so neither positive nor negative transfer is clipped. Shallow request 1.65 is capped natively at 0.8 for every view and condition. This conserves the sum over all six views at each affected step and group; it does not conserve each view's individual budget.

## Dynamic replay evidence

- B0 was run on all six selected objects using the untouched checkpoint and configuration. Each saved 768×512 RGB panel was compared against the historical `budget_fixed_mean` panel. All six were pixel-identical: zero changed channel values, zero maximum channel difference.
- For the B+ smoke on object index 0, the six input tensor hashes (condition, target, normal, depth, global embedding and initial latent) exactly match B0. The initial latent SHA256 is `0340047558809127cfbef95fc332f3ae1ce4145167192ddcfc30e1e5778e94dd`.
- The runtime trace has 50 sampler steps and nine adapter injection sites per step. At steps 34–49, all deep/middle sites record `[1.85, 1.61, 1.61, 1.61, 1.61, 1.61]` after native caps; each sum is 9.90 within FP32 representation. Other steps remain `[1.65]*6`. Shallow is `[0.8]*6` throughout.
- The smoke trace records finite post-scale residual L2 and mean-absolute dose separately for all six tiles at every adapter site. This distinguishes applied scale from realized residual dose. Observed feature mosaics are divisible 3×2 with deep 24×16, middle 48×32 and shallow 96×64 tile shapes.
- The completed six-object B+ and B− traces pass the same step/site/cap/dose checks. Across every object and condition, all six input hashes match; the initial latent hash is unchanged. All three conditions have six complete outputs, for 18 total generations.
- The generator resets Python, NumPy and Torch to `42 + object_index` before loading each object's batch, resets Torch to 42 for latent initialization, then resets Torch to 42 again immediately before generation. The input and latent hashes are asserted equal across conditions before results are written. The same precomputed geometry feature tensor is passed to each condition for that object.
- The unchanged scalar Fixed Mean branch remains pixel-identical to the frozen output, and the view-scaled branch runs through the existing FP16 UNet path while returning scaled corrections to the original feature dtype. Existing geometry-feature caching is outside the scale branch and remains shared. The run completed without feature-shape, precision, cache, or finite-dose errors.

## Immutable provenance

- Frozen model checkpoint: `geotex_step_0002000.pt`, SHA256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Frozen generation config `clean_holdout.yaml`, SHA256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Frozen handoff and freeze-manifest hashes are recorded in `phase_a_identity_audit.json` and the generated counterfactual handoff.
- Latest 1014 manuscript SHA256 `142cb121bbb5fb6a50e49137773055587b0d3ac21e4fd7e5267442903b8efb93`; supplement SHA256 `67c2e255cc9aa753cdc724acb4189b653c944f073853b46e6fa3479c8f13194a`. Neither file was changed.
- Implementation lives in isolated worktree `/4T/tmp/MV-Painter-counterfactual`, branch `codex/counterfactual-view-control-20261014`. No main-worktree, checkpoint or historical result was edited.

## Phase A decision

**PASS.** All six B0 outputs match the frozen generator byte-for-byte at RGB pixel level. Both signed interventions hit the reference tile and compensate the other five tiles exactly after native caps. Cross-condition input/latent hashes match for all six objects, and all actual residual-dose traces are finite. The full machine-readable check is `phase_a_dynamic_audit.json`.
