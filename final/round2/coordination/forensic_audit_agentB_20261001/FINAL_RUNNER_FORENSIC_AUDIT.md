# FINAL_RUNNER_FORENSIC_AUDIT.md (Phase 6 — agent B)

Assembles the per-experiment runner registry from archived manifests
(read-only) and documents the RNG inventory and eval-mode status.

## 1. Experiment registry (main backbone)

| field | value | source |
|---|---|---|
| checkpoint | `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt` — SHA-256 `0618d6b2…14c0` | robustness RUN_MANIFEST; confirmation protocol manifests |
| config | `clean_holdout.yaml` — original under volatile `/4T/tmp/mvpainter-recovery-HLzm9O/`; rescued copy: `final_audit_20261001/rescued_tmp_20261001/clean_holdout.yaml` (hash in FINAL_REPRODUCIBILITY_MANIFEST) | manifest + rescue record |
| frozen runner | `scripts/run_layer_confirmation_276_20260930.py` — SHA-256 `273c2f75…914` (R0/R1/Core-7 all declare the verbatim frozen code path) | robustness RUN_MANIFEST `frozen_runner_reference` |
| scheduler / steps / precision | EulerDiscreteScheduler, 50 steps, fp16 | manifests + runner source |
| resolution | 256x256; unique6 targets `[0, 15, 12, 16, 13, 14]` | manifests |
| metric path | `geotex.eval_exploration.compute_metrics` (in-memory tensor = PRE_SAVE) | manifests |
| seeds | R0: `object_seed = 42+idx` (random/np/torch before collate); R1: `10042+idx`; initial latent: `torch.manual_seed(42)`; cond-VAE path re-seeded before generation | manifest `seed_policies` + runner source L190-208 |
| git commits | robustness run at `edfb8d0`; Core-7 delivered at `75a4068` (base d30ed4f); confirmations at `4eacbc6`/`2b788e6` era | manifests + git log |
| output paths | `coordination/layer_confirmation_20260930/<schedule>/`, `core7_same_runner_completion_20261001/formal_*/`, `main_backbone_robustness1_20260930/` | manifests |

Cross-backbone (registry level): MV-Adapter 76-object panel and MVDiffusion
450-run panel carry their own manifests, identity gates (9/9 and 36/36
bitwise), hash manifests, and bootstrap seeds 20260928; native-mirror
equivalence 1552/1552 tensors + 12/12 views (see
`CROSS_BACKBONE_VALIDATION_*.md`, verified in Phase 13/14 of this audit).

## 2. RNG inventory (what "same input" actually pins)

| RNG stream | seeded by | governs |
|---|---|---|
| Python `random` | `object_seed` (=42+idx R0 / 10042+idx R1) before collate | cond-image stretch/compress draw (`random_stretch_or_compress`, 0.5-1.5x) — the only active dataset augmentation; targets/normals/depth random_resize are commented out in the imported copy |
| NumPy | seeded with object_seed | (no active consumer found in the path) |
| Torch CPU/CUDA | `torch.manual_seed(42)` for initial latent and again before generation | initial latent (same values for every object/method — paired by construction), cond-VAE stochastic path |
| VAE | deterministic encode for cond latents; stochastic path pinned by the pre-generation reseed | cond latent sampling |
| not seeded across objects | initial latent values | identical latent tensor across objects — a design choice; removes latent noise as an object-level variance source and is uniform across methods |

Because the stretch draw is pinned per object and the latent/cond-VAE seeds
are fixed constants, a same-seed restart is deterministic per runner —
verified empirically by the cross-process audits (GFL anchor bit-exact;
0/276 input-hash mismatches; R0 anchor images re-executed bitwise).

## 3. Model mode / eval state

All paper-facing runners construct the model via `ee.load_model` (no
`unet.eval()` call in the runner path). Verified inert: no BatchNorm layers,
dropout p=0.0 / PyTorch p=0 early-return, no `self.training` branches in the
wrapper/adapter/geo-encoder chain; VAE explicitly eval'd. Train-mode is
therefore the uniform protocol across every condition, so no comparison is
mode-confounded. (Hygiene note for any future re-run: add `eval()`; numeric
impact expected zero.) This matches the D19 disposition in the parallel
session's records.

## 4. Gaps / notes

1. Initial latent is the same tensor for all 276 objects (seed 42) — paired
   and uniform, but reviewers may ask about latent diversity; the dev-24
   3-seed study covers generation-noise robustness instead (P5 disposition).
2. The config's original location was volatile; the rescued copy must be the
   one cited going forward.
3. Formal strict-276 runs archived metrics but not prediction PNGs (see
   `FAILURE_MODE_AUDIT.md` section 5) — acceptable for metrics-only claims, blocking
   for any future visual claim on the holdout.
4. Residual logs (`residual_log`) are not archived for formal runs; budget
   claims rest on the effective-scale analysis (`LLH_EFFECTIVE_CONTROL_AUDIT.md`).

## Verdict

`VALIDATED_WITH_LIMITATIONS` — the runner chain is hash-pinned, seed-pinned,
uniform across conditions, and cross-process reproducibility is proven
bitwise; limitations are archival (config rescued, no PNGs, no residual logs),
none affecting existing numbers.
