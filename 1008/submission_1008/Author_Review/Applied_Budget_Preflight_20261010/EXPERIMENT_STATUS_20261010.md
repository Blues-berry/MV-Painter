# Experiment handoff — 2026-10-10

## Workspace and scope

- Isolated branch: `codex/1010-experiments`, based on `mvpainter/main` at `815ab0f70bf408e2d3e2a1b76ce366ec5829c41f`.
- The original dirty workspace was read-only. No manuscript, supplement, response letter, or existing result was edited.
- `PREFLIGHT.json` captures source/cohort identities, existing-row integrity, schedule arithmetic, model-path metadata, and the GPU gate.

## A — MV-Adapter transfer

The actual intervention scales the four `cond_encoder` feature tensors before they enter the UNet as `down_intrablock_additional_residuals`. GeoTex instead scales corrections inside wrapped ResNet blocks. This is related residual control algebra on different injection paths, so any result is partial transfer rather than a matched TCAS replication.

The existing layerwise audit compares its wrapper to the already modified global runner. It does not compare the unmodified official pipeline to the patched runner at native scale 1.0. The four-step equivalence smoke is also insufficient. Strict native identity remains **INCOMPLETE**; no formal MV-Adapter matrix was started.

## B — GeoTex applied-budget placement

The CPU preflight passed for the historical 50-step implementation and current 300-object Fresh C rows. It confirmed:

- C3 high steps are 17–32; early, middle, and late profiles are 0–15, 17–32, and 34–49.
- Deep/middle applied sums equal 82.50 for the three placement profiles and Fixed Applied Mean; shallow applied sum is 40.00 for all four.
- Existing GFL/GFH/C3/no-adapter data contain 300 rows per condition, and the six stored input fingerprints match within each object across conditions.
- Historical runner, config, checkpoint, cohort, and 38 packaged Python source files match their recorded hashes.

The experiment is **RETROSPECTIVE** because the cohort and earlier condition outcomes are already known. The historical run manifest recorded the base-model path but not a content digest for the 9 GB base-model directory. The new launcher records file sizes and mtimes and preserves the same resolved path, but cross-run base-model equality is not cryptographically proven.

No new inference started. The latest gate sample showed about 24 GiB allocated on each 32 GiB RTX 5090, above the launcher limit of 1 GiB and 10% utilization. `launch_applied_budget.py --launch` will refuse to run until both cards pass the gate. The three added conditions are Fixed Applied Mean, Early-high, and Late-high; existing GFL, GFH, and C3 rows will be reused only with the recorded provenance limitation.

No result has been generated for the strict placement contrast. Do not state that Middle-high wins or that temporal placement is independent of realized residual dose.

## C — Fresh C baked 3D evidence

The current input-frozen Fresh C N=24 panel has a failed native-UV/sampler/alpha gate and its 3D claim is formally **RETIRED**. Nine assets use UV coordinates outside `[0,1]` with REPEAT samplers; five assets use BLEND alpha that the available renderer does not implement. The production baker re-unwraps UVs. The experimental CPU baker clamps coordinates and replaces source materials, so it is not an acceptable path for this panel.

The synthetic sampler suite passed 11 cases, but no Fresh C N=24 bake/render was produced. A separate N=20 GLB-native report covers disjoint `FRESH_CONFIRM_300` UIDs, reevaluates stored unlit base-color GLBs, and does not rebake. It cannot substitute for Fresh C evidence. Blender 4.2.4 was not available; downloading the official archive or mirror was stopped after measured rates stayed below 0.2 MB/s.

## Evidence limits and next execution gate

Keep the Fresh C image-space results, the N=20 historical GLB result, and the current N=24 retired panel separate. Do not claim full PBR, lighting robustness, seam improvement for the current panel, a unique schedule winner, or a matched second-backbone replication.

When a GPU is free, run the native MV-Adapter identity comparison before any MV-Adapter schedule matrix. The GeoTex launcher is separately ready for its three missing retrospective conditions when both cards pass the idle gate, subject to the model-identity caveat above. Reopen Fresh C baking only with a compatible Blender runtime and a real-GLB gate that preserves original geometry/UV/sampler/alpha semantics.
