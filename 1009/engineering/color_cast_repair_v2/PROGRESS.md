# Color Cast Repair V2 progress

## 2026-10-09 — setup and protocol lock

- Started from frozen parent commit `46e741180a2fd539a43234c51f4f3019e346424e` on `codex/r1-color-cast-repair-v2-20261009`.
- Preserved all pre-existing untracked 1008 files; no 1008, raw image, TeX, or paper-worktree file was changed.
- The start-of-campaign GPU snapshot was idle. Later snapshots show shared allocations and intermittent compute; this campaign uses one device only after it has a clearly free memory and utilization slot.
- Python 3.13.5 / torch 2.7.1+cu128 / Diffusers 0.37.0 / Transformers 4.57.6 / torchvision 0.22.1+cu128 are present.
- Dataset inspection confirms the selected source view is target tile 0 in both unique6 branches: view 014 under `reverse=True` and view 000 otherwise. In the reverse branch, RGB target tiles 15 and 16 receive 90-degree rotations; tile 0 does not. The mapping is from `MVPainter/src/data/mvpainter_dataset.py`, not visual order inference.
- The eval path applies the condition-only `random_stretch_or_compress` transform before VAE encoding; target RGBs do not receive that transform. The intervention will capture and use the transformed condition alpha mask and will record the discrepancy. Color statistics, rather than pixel registration, are used for source-view calibration.
- Phase B probe objects and perturbation matrix are frozen in `protocol/B_PROTOCOL_LOCK.json` before any new GPU generation.

## 2026-10-09 — condition-cache provenance and GPU scheduling

- The original Fresh B input-only audit recomputed the two frozen vision encoders from the exact seeded `cond_imgs` for all 150 objects. Cache identity was within max-abs `0.03` for `0/150`; median/P95/max mismatch was `3.3992 / 5.1092 / 6.8746`.
- A pre-outcome amendment added the unaugmented selected source image comparison. Cache identity was also within `0.03` for `0/150`; median/P95/max mismatch was `3.3004 / 5.3485 / 6.8331`. Provenance CSV/JSON SHA values: `cc5162631846f67d3f387e2a7cf477a3e8c3c4cb7584d3d1f51bdefa7544d31b` and `60dd7b922882ddea76466f9b83eae7111fed69317f3f16e3afd1ea58303d5fd5`.
- On eight predeclared sentinels (first four source-000 and first four source-014 objects), caches for all four source-014 objects were closer to raw view 000 than raw view 014. The full locked check of all 98 source-014 objects confirms raw view 000 is closer by max-absolute distance for 84/98 and has higher cosine for 94/98. Median max-absolute differences are 3.6740 to raw view 014 and 2.5664 to raw view 000; exact matches within 0.03 are 0/98 for either view. CSV/JSON SHA values: `b67e073f652f598f6f071fcebc8037295ab983d5b8d7b3edfc00ed338dbfe2b7` and `78970c399b1454c6976c410b3941017316893f140ff66f7b54f961725040e8fb`.
- No Fresh B prediction PNG pixels or C1 repair result has been opened. During baseline-identity work, the read-only 1008 aggregate report and manifest tables were consulted; their cohort-level baseline GFL/LLH summaries were not used to select or tune C1. The Fresh B C1 image/metric outcomes remain sealed.
- The current two RTX 5090s fluctuate between 0–100% utilization while each has approximately 19 GiB allocated; no process IDs are visible in the current container. A model-load-only preflight completed on physical GPU 1 earlier with zero diffusion generations. To avoid interference, Phase B sampling has not started while both devices remain occupied.
- The B intervention remains frozen at 64 calls across four development objects. The `global_embedding_recomputed` control was added before any generated-image review in `protocol/B_PROTOCOL_AMENDMENT_01.json`; the physical-GPU binding and processor/scheduler trace are recorded in `B_PROTOCOL_AMENDMENT_02.json`.
- Source-view, per-view, and descriptive magenta-direction readouts are frozen before any new RGB generation in `protocol/A_COLOR_READOUT_LOCK.json`. The source mask and evaluation mask rules are explicit; no augmented-condition pixel registration is assumed. The source-chroma anchor module's seven unit tests pass.
- User authorized waiting for an idle period. Current snapshots show GPU0 at 28% utilization and about 19 GiB used; GPU1 at 0% utilization but also about 19 GiB used, leaving only about 12.5 GiB free. No sampling is running because ownership is unknown and that free memory is below the safe model-load margin.

## 2026-10-09 — C1 development method and evaluator prepared

- `protocol/C1_DEV_METHOD_LOCK.json` freezes one source-conditioned Lab chroma anchor for the four development objects. It uses independent foreground medians, 3-pixel erosion, at least 64 trusted pixels, and a fixed per-channel ±6 Lab limit; no GT RGB enters the estimate. Execution remains gated on Phase B evidence.
- Added `run_chroma_anchor_evaluation.py` for CPU-only correction and scoring. It refuses to overwrite an existing output run. Its Fresh B path requires a final method lock and validation amendment, checks the frozen UID list, reconstructs and verifies five saved model-input tensor hashes, verifies each baseline PNG SHA, and writes candidates separately from GFL.
- The existing Fresh B GFL outputs match the frozen checkpoint, config, runner, 150-object list, unique6 order, EulerDiscrete scheduler and 50 steps. Original inference package versions are absent from those manifests; the post-processing validator records this limitation and performs no new diffusion sampling.
- Static Python compilation, CLI import/help, and JSON protocol parsing passed. The repair module SHA remains `8d2f460509280e9cbe4e22081a47e3ce938f53262bd321d8971be18095572be8`; the evaluator SHA at this checkpoint is recorded in Git history after final fixes.

## Current queue

1. Phase B and the C1 development-only trial are complete.
2. C1's numeric criteria passed, but its pre-registered visual failure-case gate failed. The final method lock closes the Fresh B holdout; do not open or run Fresh B repair outcomes.
3. Reports, casebooks, and checksum inventories are complete; the scoped experiment commit is pushed to the new campaign branch.


## 2026-10-09 — Phase B runner fix before first generation

- Resource checks showed both RTX 5090s fully free and low I/O pressure before launch. A model-load-only preflight from 01:52 had already completed with zero diffusion calls; its console logs remain under `runs/phase_b/`.
- Phase B attempt 02 loaded all seven pipeline components and the GeoTex adapter on physical GPU 1, then failed at the first object’s feature-hash serialization. It completed zero diffusion calls and wrote no prediction PNGs. The raw started runtime/state and full console traceback are preserved in `runs/phase_b/attempt_02_geometry_hash_type_error/`.
- Source inspection confirmed `GeoTexEncoder.forward` returns a named tensor mapping. Fixed the probe logger to hash mapping values in sorted-key order; no method, model, sampler, or generation settings changed. Amendment `protocol/B_PROTOCOL_AMENDMENT_03.json` locks old/new runner identities before any generation.
- `py_compile` passed. A CPU `GeoTexEncoder` smoke check produced eight named tensor hashes and serialized them as JSON. No diffusion call occurred during the check.
- The attempted load raised I/O pressure during component reads, so all subsequent Phase B launches use idle-class I/O priority (`ionice -c3`) and lower CPU priority.

## 2026-10-09 — Phase B causal intervention complete

- The final Phase B run completed exactly 64/64 generation calls across four locked objects; 64 prediction PNGs and 384 per-view metric rows are present. `run_state.json` and `runtime.json` both report `complete`; generation wall time was 485.1 s.
- Shared-factor hashes for the initial latent, geometry features, and pre-posterior RNG agree within each object. Runtime recorded FP16 weights, physical GPU 1, 50-step `EulerDiscreteScheduler` sampling, pipeline `EulerAncestralDiscreteScheduler`, both CLIP processors, all backend flags, and checkpoint/config/runner identities.
- The locked response rule passed for embedding-only a* in both signs (4/4 source objects and 4/4 unseen-view objects per sign); the joint arm also passed. VAE-only controls failed the directional rule. The cache-recomputed arm remains a separate input-consistency comparison.
- The rule supports causal color control through the global embedding path; it does not show that an output shift improves GT-relative color error. The frozen C1 candidate is now eligible for its four-object development gate only. Fresh B predictions and C1 metrics remain unopened.

## 2026-10-09 — C1 development gate and final delivery

- CPU-only C1 processing completed on the four locked development objects. Object-paired unseen-view ΔFG-CIEDE2000 mean was −1.5602 (95% percentile CI [−2.2621, −0.6299], 4/4 wins; 10,000 bootstrap draws, seed 20261009). Mean ΔFG-PSNR was +0.1805 dB, ΔFG-LPIPS −0.00186, and foreground L* SSIM-to-GT Δ −0.00015.
- The frozen visual criterion failed: Fig. 4 row 1 had no clear visible improvement; Fig. 4 row 2 retained substantial mismatch and developed faint cyan/blue silhouette rims. The normal and high-texture objects showed no obvious detail/structure damage.
- `C_REPAIR_METHOD_LOCK.json` records `development_gate_pass=false`, `validation_authorized=false`, no Fresh B outcomes opened, and a closed holdout guard. No validation amendment, Fresh B repair run, or C2 generation-time constraint was created.
- Final root-cause analysis is partial: global embeddings causally control chroma, while cached/current embedding mismatch affects the two failure cases in opposite directions. The complete generation cause remains unresolved; C1 is not a validated fix.
- Added per-view and per-object source/unseen color readouts, root-level copies of the Phase B intervention and C1 development result tables, the development before/after casebook, failure analysis, verdict, and SHA-256 inventory. Phase B used 64 GPU diffusion calls in 485.1 s; C1 used zero GPU calls.
- The campaign package commit `98d22d18c4a1f85b7894c387544e0a13b73d823d` was pushed to `origin/codex/r1-color-cast-repair-v2-20261009` as a new branch. The branch has no changes from the paper Agent's worktree; pre-existing untracked 1008 files remain untouched.
- The main SHA manifest covers the committed package. A separate local-only SHA manifest covers 76 retained image intermediates (64 Phase B outputs, four C1 candidate grids, and eight C1 source/GT case images).
- Completion audit added an explicit half-alpha mask-edge assertion to the repair module tests; the first assertion attempt exposed a test-shape bug, which was corrected. Final focused result: 8 passed under Python 3.13.5. See `runs/phase_c/test_color_repair_pytest.log`.
- Added the estimated cost of the cache-provenance follow-up to `FAILURE_CASES.md`: 8 development calls (~61 s sampler) and, only if its gate passes, a strict 300-call paired Fresh B rerun (~37.9 min sampler), plus startup/preprocessing.

## 2026-10-09 — B2 raw selected-source embedding intervention

- User authorized waiting for an idle GPU window. A fresh check showed physical GPU 1 idle (0% utilization, 15 MiB allocated); B2 ran only on `CUDA_VISIBLE_DEVICES=1` with idle I/O and low CPU priority. Runtime UUID: `2abab5d9-0ecf-cfff-c0f1-95921fe8c165`.
- B2 attempts 01–03 failed before diffusion sampling and each records zero generation calls. The amendment chain preserves the runner/hash changes; attempt 04 completed exactly 8/8 calls in 77.326 s.
- Treatment replaced only cached `global_embeds` with the frozen vision-encoder output of the official raw selected source view. Four Phase B development objects, same unique6 protocol and paired latent/geometry/condition/VAE posterior factors. No Fresh B outputs or repair metrics were opened.
- Paired PNG and shared-factor hash checks passed. Source RGB, target RGB source files, target/mask reconstruction hashes, output image hashes and bootstrap table are linked in the B2 result CSVs and `B2_METRIC_INPUT_RECONSTRUCTION.json`. The original run omitted target-grid/mask-grid hashes; the report explicitly identifies the same-code, same-CUDA post-run reconstruction limitation.
- Unseen-view FG-CIEDE2000 object deltas were +0.0773, +0.0068, +0.9058 and −0.2982; mean +0.1729, 95% object-bootstrap CI [−0.2044, +0.6810], 1/4 wins. The locked CIEDE gate required ≥3/4 wins and mean ≤−1.0; it failed. Fig. 4 cases show no clear visual correction. Stop B2 and keep Fresh B sealed.
- The four-page B2 casebook, paired metrics and object summaries are complete. Visual review was unblinded and is reported as a development review only; no independent validation claim is made.
- Updated the next route to a read-only audit of the historical embedding-cache builder (zero GPU calls). At B2's measured 9.67 s/call, a future 8-call development probe would take ~77 s; a 300-call independent paired validation would take ~48.3 min plus startup/preprocessing, only if a new correction is independently justified and locked.
