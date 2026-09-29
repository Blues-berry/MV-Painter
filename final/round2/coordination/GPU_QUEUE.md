# GPU Queue and Handoff

Audit date: 2026-09-29 UTC. This file records resource state and authorization,
not assumptions from an older conversation.

## Direct resource check

The CUDA-visible read-only check reported:

| GPU | Device | Memory used / total | Utilization | Current decision |
|---:|---|---:|---:|---|
| 0 | NVIDIA RTX 5090 | 41 / 32607 MiB | 0% | free, not yet assigned |
| 1 | NVIDIA RTX 5090 | 15 / 32607 MiB | 0% | free, not yet assigned |

No active MV-Adapter, main-evaluation, stage-placement, trace, CUDA-bake, or
CPU-bake process was found in the read-only process check. D's
`cpu_bake_12` outputs are complete and must not be duplicated; the remaining
D action is bookkeeping only.

The restricted shell cannot see the NVIDIA driver, so any actual CUDA launch
must first run in the CUDA-visible execution context and record
`torch.cuda.is_available()`, device name, PID and output directory.

## Queue

| Order | Owner | Task | Resource | Authorization | Stop/acceptance gate |
|---:|---|---|---|---|---|
| 0 | D | Existing `cpu_bake_12` execution | CPU/Blender | complete; do not duplicate | 48 method records, 528 unseen rows; see bake audit |
| 1 | D | Validation, scope correction and status addendum | CPU/read-only | complete; no cohort expansion | semantic GLB/UV checks, finite enabled metrics, explicit DISTS/GT/exporter limits |
| 2 | A + D | Same-generation float/encoder/PNG trace for 12 objects | GPU0 | complete; output sealed in `float_png_trace_12_controlled_20260929` | A/B/C tensors and hashes; pixel MAE/max error; paired Full-SSIM; no metric patch |
| 3 | A | Main stage-placement 276-object run | GPU1 | independent resumable launcher `stage_placement_276_20260929_resume_v2` is running; do not duplicate | 276 objects × 4 schedules, atomic records, finite fields, paired CI/win rate, residual logs |
| 4 | E | G1–G4 evidence review | CPU | after G1/G2 results; no GPU | update ledger and decide paper narrative; no hidden pooling |

Orders 2 and 3 are intentionally serialized: the trace resolves the metric
gate before the longer stage-placement run consumes another GPU/output path.
If the trace is blocked, record the reason and stop; do not silently switch
to a different metric or cohort. Never kill an unrelated process.

The A-2 launcher persists its state in
`final/round2/stage_placement_276_20260929/status.json`, writes the terminal
summary to `final_manifest.json`, and creates `DONE` or `FAILED`. Its first
scheduled terminal check is at the recorded `estimated_complete_at`; there is
no intermediate progress polling. A detached ETA dispatcher now sleeps until
`2026-09-29T05:45:07Z` and invokes the acceptance gate once. If the runner is
still active, it records that fact and uses an explicit 30-minute checkpoint;
it never reads intermediate records during the training window.

The acceptance gate is
`scripts/validate_stage_placement_276_20260929.py`. It checks the terminal
manifest, 276 atomic records, four schedules per object, finite metrics, 50
actual residual L2/RMS observations per schedule, and 10,000-resample paired
bootstrap summaries. On success it writes `NEXT_ITERATION_READY.json`; on
failure it writes `NEXT_ITERATION_BLOCKED.json`. Neither path edits the paper.

## Explicitly not queued

- no MV-Adapter rerun;
- no retraining or checkpoint search;
- no new clean-v3/cohort selection;
- no application of `METRIC_FLOAT32_RECOMMENDED.patch`;
- no paper claim rewrite by C;
- no GPU bake while the CPU Exact-GLB path is being validated.

