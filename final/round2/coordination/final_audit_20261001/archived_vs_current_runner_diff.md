# Archived vs Current Runner Diff (final_audit_20261001, Phase 1.2)

Compared: `rescued_tmp_20261001/recovery_scripts/run_layer_official.py` (archived
official layer-LHL runner, last modified 2026-09-29 12:44:09) vs
`scripts/run_layer_confirmation_276_20260930.py` (frozen confirmation runner, protocol
`layer-confirmation-strict276-v1`). Shared kernels `geotex/explore_contradiction.py`,
`geotex/eval_exploration.py`, `MVPainter/mvpainter/model_unet_geotex.py` are
SHA-identical to the hashes recorded in the archived handoff, so the diff below is the
complete runner-level difference surface.

| Axis | Archived runner | Frozen confirmation runner | Verdict |
|---|---|---|---|
| Seed initialization | `random.seed(42); np.random.seed(42); torch.manual_seed(42)` ONCE at process start (L150-152) | Per object before `collate_batch`: `object_seed = 42 + obj_idx`, all three RNGs (L190-193) | **DIFFERENT — the functional difference** |
| Random calls per object | `python.random` draws inside `MVPainterData.__getitem__` (`random_stretch_or_compress` 0.5–1.5× per axis + `random_resize` 0.8–1.0 on the cond branch only) advance a process-global stream; stream position depends on how many objects the process has loaded and on resume splits | Same draws, but frozen per object by the per-object seed | Different realization policy (see note below) |
| DataLoader behavior | No DataLoader; sequential in-process `collate_batch(dataset, obj_idx, device)`, one object at a time | Identical | SAME |
| Object ordering | `obj_{idx+24:04d}` for idx 0..275, ascending; completed set skipped via rows.json resume | Identical | SAME |
| Preprocessing (targets) | `prepare_batch`; GT stats bitwise identical to frozen protocol (proven in provenance audit §5.1) | Identical | SAME |
| Target view selection | `target_view_mode='unique6'`, views [0,15,12,16,13,14] | Identical | SAME |
| Latent generation | `torch.manual_seed(42)` → `init_latents = randn(1,4,48,64,fp16)`; re-seed 42 before `generate_with_schedule` | Identical (L200-203) | SAME |
| VAE sampling | cond VAE samples inside `generate_with_schedule` after the re-seed | Identical | SAME |
| Scheduler / schedule | `stage(progress, …)` on `step/49`, 17/16/17 partition; LHL deep/middle [1.25,2.50,1.25], shallow [0.50,0.75,0.50]; 50 steps | Identical values for the LHL replica (L79-86) | SAME |
| Metric calculation | `ee.compute_metrics(pred, target, mask, edge, lpips_fn, device)` with `compute_edge_mask(real_depth, threshold=0.1)` | Identical | SAME |
| Scale semantics | wrapper caps deep 3.0 / middle 3.5 / shallow 0.8 (from protocol manifest) | Identical | SAME |
| Resume semantics | restart re-seeds 42 at process start and skips completed objects without loading them → stream replay for the remaining objects; the shipped record is such a split (head + tail concurrent processes) | Same skip logic, but realizations are per-object frozen so resume is inert | DIFFERENT in effect |
| Logging | no per-object realization/scale/residual record (`residual_log` created empty, discarded) | full protocol + run manifests | archival gap (archived side) |
| Hygiene note (D19) | neither runner calls `unet.eval()`; per the D19 falsification this has zero numeric effect (no BatchNorm, no non-zero dropout, no `self.training` branch anywhere on the RefOnlyNoisedUNet path; VAE explicitly eval'd) | same | SAME (non-issue) |

## Interpretation

1. The only runner-level functional difference is the RNG policy governing the
   reference-image stretch realization (plus its resume interaction).
2. The robustness R0/R1 experiment quantifies that policy's aggregate effect: changing
   every realization moves absolute schedule means by ≈0.03 dB and leaves all paired
   deltas unchanged. The runner diff therefore CANNOT account for the archived record's
   +1.80 dB mean gap or its +3.23 dB head-block gap.
3. Since the archived runner diff is otherwise byte-equivalent in protocol terms, and
   the shipped record is a same-day merge of two processes run against an
   unreconstructible working tree (dataset committed 3 h later as `78c871f`), the
   discrepancy must originate in an execution state that no surviving artifact records.
   This is the basis for the Case B ruling in
   `historical_result_exclusion_reason.md`.
