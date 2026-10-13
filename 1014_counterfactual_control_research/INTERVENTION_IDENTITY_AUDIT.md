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
- The new handoff's 36 B0 tile crops are pixel-identical to the six historical Fixed Mean bake inputs. The 24 new bakes pass the same per-object coverage, 256-pixel GT resolution and GLB byte-patch gates. All six B0 1024×1024 textures are pixel-identical to the historical UV bake outputs.
- The preserved native EGL renderer produced 264 images (6 objects × 4 bake methods × 11 unseen cameras), with a passing sampler probe. All 66 B0 renders are pixel-identical to the historical native-EGL renders. The renderer SHA matches the historical runner record: `ce729d45ff0e16098ef6dd907877b782f79d9e82a35c3f807078102f4c07e33a`.
- The legacy EGL wrapper had a stale relative renderer path and pointed to a deleted `extraction.json`. Neither archived script was changed. A small research-local shim feeds the wrapper the same Blender bounding boxes already frozen in this handoff and the exact renderer path/hash from the historical run.
- The generator resets Python, NumPy and Torch to `42 + object_index` before loading each object's batch, resets Torch to 42 for latent initialization, then resets Torch to 42 again immediately before generation. The input and latent hashes are asserted equal across conditions before results are written. The same precomputed geometry feature tensor is passed to each condition for that object.
- The unchanged scalar Fixed Mean branch remains pixel-identical to the frozen output, and the view-scaled branch runs through the existing FP16 UNet path while returning scaled corrections to the original feature dtype. Existing geometry-feature caching is outside the scale branch and remains shared. The run completed without feature-shape, precision, cache, or finite-dose errors.

## Immutable provenance

- Frozen model checkpoint: `geotex_step_0002000.pt`, SHA256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Frozen generation config `clean_holdout.yaml`, SHA256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Frozen handoff and freeze-manifest hashes are recorded in `phase_a_identity_audit.json` and the generated counterfactual handoff.
- The frozen `final_paper_20261012` release source SHA256 values are `0f0e4f74a0bccae65447954e8377482028eda0f16f3018ef069c6faf57a614fb` for `Manuscript_final.tex` and `0c61a75718cda6565d760adf4af237a91ba94a653e7f4f8f9f830dfbb50ed0c7` for `Supplementary_final.tex`; their release PDFs hash to `ed6cd3012e1e8a649c9ce93b7cac83092ad4383701c245b9a4c697c2f23a4759` and `e4155b90b54cf5b0f90ed9e4798c00cd7f68e7288c4ffa84b398d00026b96100`. These values match the release `SHA256SUMS.txt`; this study did not modify those files.
- Implementation lives in isolated worktree `/4T/tmp/MV-Painter-counterfactual`, branch `codex/counterfactual-view-control-20261014`. No main-worktree, checkpoint or historical result was edited.

## Phase A decision

**PASS.** All six B0 generation panels, all six B0 baked textures, and all 66 B0 unseen renders match the frozen baseline pixel-for-pixel. Both signed interventions hit the reference tile and compensate the other five tiles exactly after native caps. Cross-condition input/latent hashes match for all six objects, and all actual residual-dose traces are finite. The full machine-readable checks are `phase_a_dynamic_audit.json`, the bake summary and the native-EGL render manifest.

## Equal-cost Fixed Mean candidate audit

To satisfy the same-generation-count Phase C control, a second Fixed Mean candidate was generated on the same six objects using latent seed 43. The per-object object seed and all conditioning/input hashes match seed 42; only the initial latent hashes differ. All 50 steps × 9 adapter sites were traced: deep/middle applied scales remain 1.65 and shallow remains at its native cap 0.8, with finite realized-residual dose logs. A fresh seed-42 replay passed the normal bake path and reproduced all six existing Fixed Mean UV textures pixel-for-pixel. The new seed-43 panels then passed the same native UV/GLB patch checks. The equal-cost baseline produced 18 bake records (GT, B0 seed42 replay and B0 seed43 for six objects) and 198 native-EGL images; the sampler probe passed. Machine-readable checks are in `equal_cost_phase_a_audit.json`, the separate bake handoff, bake summary and EGL manifests under `EQUAL_COST_BASELINE/`.
