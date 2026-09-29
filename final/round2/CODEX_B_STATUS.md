# Codex B status — Round 2 audit and MV-Adapter SD2.1

Updated: 2026-09-29

## Completed

### Task 0: audit

- Read the Round 2 status, protocol/statistics, texture, bake, runner, dataset,
  and reproducibility files.
- Preserved the existing uncommitted work; no Codex A process was started,
  stopped, or modified.
- Corrected the dataset's stored `target_order` to the unique six-view order
  `[0, 15, 12, 16, 13, 14]`; the explicit legacy mode remains available.

### Task 1: statistics and texture infrastructure

- Added explicit fixed partitions: main probe 24, main holdout 276, main
  pooled 300; MV-Adapter calibration 24, holdout 76, total 100.
- Added complete partition/disjointness validation.
- Bootstrap now rejects NaN/Inf rather than silently dropping objects, records
  ties, and retains fixed 10,000-resample seeded object-level behavior.
- Added strict raw per-view validation and per-object CSV reconstruction. Each
  object must have exactly one row for each unique camera ID before view means
  are computed.
- Added `geotex/round2_aggregate.py` for reproducible raw-view CSV to
  per-object CSV conversion.
- Added validated variation diagnostics, foreground erosion, sRGB/linear RGB
  conversion, masked PSNR, CIEDE2000, optional masked LPIPS/DISTS, and explicit
  empty-foreground/invalid-input handling.

Tests: `pytest -q geotex/tests` → 57 passed.

### Task 2: official MV-Adapter preparation

- Official source snapshot is in `final/round2/mv_adapter/upstream/`.
- Official `main` commit: `4277e0018232bac82bb2c103caf0893cedb711be`.
- Base model and adapter filename/defaults are recorded in
  `final/round2/mv_adapter/OFFICIAL_DEFAULTS.json`.
- The host NVIDIA driver is now available. GPU0 was used for this work; GPU1
  was reserved by Codex A's existing evaluation and was not touched. The final
  process audit found no remaining compute process on GPU1.
- The official adapter file is downloaded and verified: 708,310,064 bytes,
  SHA-256 `a26fcabcce6e53bd31677074e067030fc93af33381a5559365581e793cc78ae2`;
  safetensors inspection found 198 tensors.
- A public SD2.1 Base copy at `Manojb/stable-diffusion-2-1-base` was found and
  resolved at commit `0094d483a120f3f33dafbd187ea4aa60d10de75c`. The local text
  encoder and UNet match its hashes; the VAE was re-downloaded and also matches.
  The assembled local base plus MV-Adapter pipeline passed a CPU load smoke test.
- An actual GPU0 single-object equivalence smoke test passed: fixed scale 1.0
  with no schedule and `constant_scale(1.0)` produced identical six-view
  outputs (`max_abs_pixel_diff=0`). Record:
  `mv_adapter/GEOMETRY_SCALE_EQUIVALENCE.json`.
- The original Stability AI Hub repository is currently unavailable through the
  authenticated API; the resolved Manojb copy and component hashes are recorded
  in `mv_adapter/BASE_MODEL_VERIFICATION.json`.

### Task 3: geometry scale patch

- Added `upstream/mvadapter/geometry_scale.py` with constant, linear warm-up,
  cosine bump, and three-stage Early/Middle/Late schedules.
- Patched the official SD2.1 pipeline so adapter residuals are scaled inside
  the denoising loop. With no schedule, fixed `control_conditioning_scale`
  behavior is retained; with a schedule, the schedule is the absolute
  geometry residual scale.
- Removed the official pre-loop residual multiplication, avoiding double
  scaling. CFG, reference conditioning, multi-view attention, scheduler
  stepping, and control conditioning factor remain unchanged.
- Patch record: `final/round2/mv_adapter/patches/geometry_scale.patch`.

Tests: `pytest -q geotex/tests final/round2/mv_adapter/tests/test_geometry_scale.py`
→ 57 passed; patched files pass `py_compile`.

### Task 4: original GLB recovery

- The ten missing UIDs were reverse-matched against the official Objaverse-XL
  Smithsonian annotations by recomputing
  `uuid.uuid5(uuid.NAMESPACE_DNS, fileIdentifier)`. All ten matched exactly.
- `objaverse==0.1.7` official download callbacks reported 10 `FOUND`, 0
  `MODIFIED`, and 0 `MISSING`. All ten downloaded GLBs match the official
  metadata SHA-256 and are classified `Exact`.
- The canonical recovery manifest is
  `mv_adapter/GLB_RECOVERY_MANIFEST.json`; the full audit is
  `mv_adapter/GLB_RECOVERY_AUDIT.md`. Recovered files are in
  `mv_adapter/recovered_exact_meshes/`.
- Historical-renderer replay completed for all ten objects and 17 views per
  object. All masks are non-empty; the minimum mask IoU is `0.9994854202`.
  The original archived HDRI was unavailable, so the audit records the
  existing substitute HDRI and does not claim identical lighting provenance.

### Task 5: Exact-only calibration and holdout

- Exact calibration completed in `mv_adapter/results/calibration_exact_24`:
  288 rows, 24 objects, 12 schedules, all `exact_mesh`, all metrics finite.
- The frozen rule was not changed. Exact calibration produced a clear fixed
  scale tradeoff: conservative `fixed_low` (0.75), aggressive `fixed_1.0`.
  All eight stage schedules were reported, but the frozen rule still does not
  define a unique CAI stage winner.
- Exact holdout completed in `mv_adapter/results/holdout_exact_76`: 380 rows
  from 76 objects and five defined schedules (`no_geometry`, `fixed_low`,
  `fixed_1.0`, `linear_warmup`, `cosine_bump`). The paired 10,000-resample
  bootstrap is `paired_bootstrap_exact.json`.
- The undefined CAI schedule is explicitly not fabricated; therefore the
  formal six-comparison claim remains unmade. Mixed-proxy outputs remain
  preserved as historical diagnostics.

## Blockers / not run

- Hugging Face authentication is valid with a read token. The requested
  Stability AI Hub API repository returns HTTP 404 even when authenticated;
  the resolved public copy and all component hashes are recorded in
  `mv_adapter/BASE_MODEL_VERIFICATION.json`.
- The fixed MV-Adapter manifest contains 100 objects (24 calibration, 76
  holdout). The ten previously missing original meshes are recovered as Exact
  Meshes from Smithsonian, and the defined Exact calibration/holdout runs are
  complete. The unclaimed sixth holdout comparison is only the undefined CAI
  schedule under the frozen stage rule.
- A marked recovery path now exists in `mv_adapter/build_proxy_meshes.py`:
  each missing object gets a depth-backprojected convex-hull GLB derived from
  its own rendered views. The proxy manifest records the source, point count,
  mesh counts, and hash; `run_experiment.py --geometry-source mixed` records
  `proxy_depth_convex_hull` per row. Proxy results are not exact-geometry
  protocol results and will be reported separately.
- The official GPU0 50-step mixed-geometry calibration completed over the 24
  calibration objects, four fixed scales, and all eight stage combinations:
  288 rows, 264 exact-mesh rows and 24 explicitly marked proxy rows, with all
  six metrics finite. `mv_adapter/analyze_calibration.py` applied the frozen
  fixed-scale Pareto rule: the sole Pareto candidate is `fixed_1.0`, so the
  result is `NO_CLEAR_TRADEOFF`; no conservative/aggressive pair was forced.
  The eight stage utilities are retained directly in
  `results/calibration_mixed_proxy_50/calibration_analysis.json`.
- An input audit found that `obj_0070` had 17 fully transparent legacy views,
  although file-existence checks had marked them available. The exact GLB was
  valid but outside the archived renderer's camera because its normalization
  transform was restored incorrectly. A narrow direct-normalization repair
  was rendered with the same 17-view camera/HDRI/Cycles settings and installed
  after all masks were verified non-empty. The repair is recorded in
  `mv_adapter/RENDER_REPAIR_OBJ0070.json` and is not treated as untouched
  source-render provenance.
- A two-condition 76-object mixed-proxy diagnostic holdout completed with
  `no_geometry` versus the sole Pareto candidate `fixed_1.0`: 152 rows, 136
  exact-mesh and 16 proxy rows, all metrics finite. The 10,000-resample paired
  object bootstrap is in
  `results/holdout_mixed_proxy_single_pareto_50_retry/paired_bootstrap_diagnostic.json`.
  It is explicitly diagnostic, not the frozen six-comparison holdout,
  because the calibration has no conservative/aggressive pair and no unique
  CAI stage schedule.
- Codex A's controlled main-adapter checkpoint and 300-object unique6 rerun
  are present and must not be marked as missing. They remain distinguished
  from the unrecovered historical v1 checkpoint provenance; this recovery
  task does not alter that distinction.
- The official MV-Adapter checkout documents an `objaverse_list_6w.json`
  training-ID file, but that data file is not included in the source snapshot
  and no local copy was found. Therefore calibration/holdout UID overlap with
  the official training set is not verifiable; this is recorded as unknown,
  not claimed disjoint.
- The `final/` tree is ignored by the repository's `.gitignore`, so the
  artifacts exist in the shared workspace but require an explicit force-add or
  a release-package copy before they become version-controlled deliverables.

## GPU queue and limitations

1. The Exact-only runs are complete in the new `calibration_exact_24` and
   `holdout_exact_76` directories; the proxy outputs were not silently
   upgraded.
2. The formal six-comparison holdout is intentionally not claimed: the frozen
   stage rule reports all eight combinations but does not define a unique CAI
   winner, so no post-hoc CAI schedule was selected.
3. The available 76-object diagnostic uses only the sole Pareto candidate
   (`fixed_1.0`) versus no geometry and is labeled mixed-proxy.
4. Rebuild object CSVs with `geotex/round2_aggregate.py` and summarize paired
   10,000-resample bootstrap results with `geotex/round2_holdout.py`.

No final manuscript numerical values were changed.

### Task 6: Exact scale-protocol audit and selected-pair stage supplement

- Audited `calibration_exact_24/run_config.json`, `calibration_analysis.json`,
  `calibration_rule.json`, `run_experiment.py`, and
  `CALIBRATION_RESULT_FREEZE.json`.
- Confirmed that the original Exact 24-object eight-stage rows used
  `low=0.75, high=1.50`. They are now explicitly classified as an
  **initial-grid stage ablation**, not selected-Pareto-pair CAI calibration.
- Confirmed that the fixed-scale Exact Pareto result remains the clear pair
  `fixed_low=0.75` / `fixed_1.0=1.00`.
- Preserved `CALIBRATION_RESULT_FREEZE.json` unchanged because it is a
  historical mixed-geometry freeze (`264 exact + 24 proxy`), not the Exact
  result.
- Ran the independent selected-pair stage supplement in
  `mv_adapter/results/calibration_exact_selected_pair_24`: 192 rows,
  24 objects × 8 schedules, `low=0.75`, `high=1.00`, all `exact_mesh`, all
  metrics finite. The frozen stage rule returns
  `undefined_set_valued`; no stage winner or tie-break was added.
- The protocol, analysis and checksums are in that directory's
  `PROTOCOL.json`, `calibration_analysis.json`, and `per_object_metrics.csv`.

### Task 7: Direct LHL shape-transfer diagnostic and final handoff

- Ran `LHL=(0.75,1.00,0.75)` on the same 76-object Exact holdout in the new
  directory `mv_adapter/results/holdout_exact_lhl_shape_transfer_76`.
- The run contains 76 Exact rows. The schedule definition, code hashes,
  fixed split, seed and bootstrap plan were recorded before inference in
  `PROTOCOL.json`.
- Computed all five paired object-level comparisons against `fixed_low`,
  `fixed_1.0`, `linear_warmup`, `cosine_bump`, and `no_geometry`, with all six
  requested metrics and 10,000 resamples. The result is labelled
  **Direct LHL shape-transfer diagnostic**, not CAI-calibrated.
- Machine-readable bootstrap output:
  `results/holdout_exact_lhl_shape_transfer_76/lhl_bootstrap_diagnostic.json`.
- Final handoff with Exact recovery proof, both calibration stages, Exact
  holdout, LHL diagnostic, evidence scope, provenance and LaTeX tables:
  `mv_adapter/MV_ADAPTER_FINAL_HANDOFF.md`.
- Evidence scope remains: Exact Mesh = satisfied; calibration-disjoint =
  satisfied; pretraining-disjoint = unknown because the official training UID
  list was not available.
- No model or GLB was downloaded in this supplement. `final_round2.tex` and
  `response_letter_round2.md` were not modified. Codex A's checkpoint and
  GPU1 task remain untouched.

### Task 8: Scale fairness and equal-budget mechanism follow-up

- Confirmed by source audit that the historical Exact holdout's
  `linear_warmup` and `cosine_bump` used `high=1.50`; they are not same-range
  baselines for the selected 0.75/1.00 pair. `fixed_low`, `fixed_1.0`, and
  `no_geometry` do not depend on the unused high parameter and were reused
  only after code/config verification.
- Ran the independent matched-range follow-up in
  `mv_adapter/results/holdout_exact_matched_range_76`: 152 new rows (76 each
  for linear and cosine), `low=0.75`, `high=1.00`, all Exact and finite.
- Generated `matched_range_bootstrap.json` with all requested six metrics and
  10,000 object-level paired resamples, including comparisons to fixed-low,
  fixed-1.0, no-geometry and the completed LHL diagnostic.
- Ran the pre-registered equal-mean follow-up in
  `mv_adapter/results/holdout_exact_equal_budget_76`: 228 new rows for
  fixed-mean 5/6, HLL and LLH. The completed LHL rows were reused without
  rerun. The combined four-condition CSV has 304 rows.
- Generated `equal_budget_bootstrap.json` with pairwise four-condition
  comparisons and each condition versus conservative fixed-low, using 10,000
  object-level resamples.
- Added final reports:
  `mv_adapter/MV_ADAPTER_EXACT_SCALE_AUDIT.md`,
  `mv_adapter/MV_ADAPTER_MATCHED_RANGE_RESULTS.md`, and
  `mv_adapter/MV_ADAPTER_EQUAL_BUDGET_RESULTS.md`; expanded
  `mv_adapter/MV_ADAPTER_FINAL_HANDOFF.md`.

### Task 9: Cross-backbone evidence boundary

- The MV-Adapter equal-budget results establish a targeted within-backbone
  mechanism diagnostic: schedule-position effects are measurable, but no
  uniformly dominant fixed-mean/HLL/LHL/LLH condition and no unique CAI stage
  choice are established.
- The main-adapter equal-mean/HLL/LLH formal inference remains pending in
  `final/round2/STAGE_PLACEMENT_RESULTS.md`. Existing main-adapter C3
  comparisons use a different scale protocol, so no absolute cross-backbone
  PSNR comparison or same-direction mechanism claim is made.
- Exact Mesh provenance, calibration/holdout disjointness, pretraining UID
  overlap, selected-pair stage ablation, direct LHL diagnostic and frozen-rule
  uniqueness remain separate evidence labels. Undefined CAI means no legal
  unique selection, not absence of stage effects.

### Task 10: Unified Exact results aggregation

- Stopped adding MV-Adapter inference and aggregated the existing
  `holdout_exact_76`, `holdout_exact_lhl_shape_transfer_76`,
  `holdout_exact_matched_range_76`, and `holdout_exact_equal_budget_76` rows.
- Verified that all reported rows use the same 76-object Exact Mesh cohort and
  that all six requested metrics are finite.
- Kept historical linear/cosine `high=1.50` results separate from matched-range
  linear/cosine `high=1.00` results; no cross-range pooling was performed.
- Generated `mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.csv` and
  `mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.md`.
- Generated the complete LHL paired comparison record in
  `mv_adapter/MV_ADAPTER_PAIRED_COMPARISONS.json`: eight comparators, six
  metrics, object-level paired bootstrap, 10,000 resamples, seed `20260928`,
  95% CIs and direction-aware object win rates.
- Preserved the CAI status as `undefined_set_valued`. LHL remains a direct
  shape-transfer diagnostic; fixed mean/HLL/LHL/LLH remain equal-budget
  follow-up ablations.

### Task 11: GPU handoff

- Read-only checks found no active MV-Adapter inference or training process.
- GPU0 is idle (`41 MiB / 32607 MiB`, 0% utilization); GPU1 is also idle.
- Recorded the CUDA-enabled environment, PyTorch/CUDA versions, model paths,
  Exact data paths and the non-escalated-shell CUDA visibility caveat in
  `mv_adapter/GPU_HANDOFF_STATUS.md`.
- No Codex A/D task was started and no final paper or response letter was
  modified.

### Task 12: C3/TCAS full-baseline audit and follow-up protocol

- Audited the existing main-adapter clean-v2 strict 276 stage-placement CSV:
  1,104 rows, 276 objects × 4 schedules, all recorded metrics finite. The
  saved-artifact Full-SSIM branch was checked separately with 1,104 finite
  rows.
- Audited the MV-Adapter Exact calibration/holdout artifacts and unified 76-
  object table. All six requested MV-Adapter metrics are finite and all
  reported geometry sources are `exact_mesh`.
- Main-adapter provenance is explicitly labelled source-stratified rather than
  all-Exact-Mesh: only 10/276 rows have locally verified original GLB files in
  the provenance join; CIEDE2000 and GT-relative texture error are not present
  in the main stage CSV and were not reconstructed.
- Re-audited the strict 24-object TRB and TRB2 development pilots. FG-LPIPS,
  calibration timing, paired object sets and 50-step accounting are present;
  both promotion gates are `do_not_promote`. No 276-object TRB holdout was
  started.
- Generated independent audit outputs in
  `final/round2/coordination/`:
  `C3_TCAS_FULL_BASELINE_AUDIT_20260929.md`,
  `C3_TCAS_BASELINE_MANIFEST_20260929.json`,
  `C3_TCAS_PAIRED_STATISTICS_20260929.json`,
  `STRICT_TRB_DEVELOPMENT_GATE_SUPPLEMENT_20260929.json`, and
  `C3_TCAS_CLAIM_LEDGER_20260929.md`.
- Froze a development-only schedule protocol for `LLH_ramp_eq` and
  `LLH_cosine_eq` in
  `C3_TCAS_NEW_SCHEDULE_PROTOCOL_20260929.json/.md`. It uses only the 24-
  object development cohort, keeps the 276/76 holdouts locked, and does not
  authorize a CAI or cross-backbone claim.
- Added the reproducible read-only auditor:
  `scripts/audit_c3_tcas_baseline.py`. No checkpoint, dataset, C3 result,
  manuscript, or response letter was modified.
