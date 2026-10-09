# Handoff state

- Active branch: `codex/r1-color-cast-repair-v2-20261009`.
- Base: `46e741180a2fd539a43234c51f4f3019e346424e`.
- Paper worktree, 1008 evidence and untracked historical RGB assets are read-only.
- Start-state inventory: `INITIAL_STATE.json`.
- Frozen GPU probe protocol: `protocol/B_PROTOCOL_LOCK.json`.
- B amendments: `protocol/B_PROTOCOL_AMENDMENT_01.json` adds the current-condition embedding control before generation; `protocol/B_PROTOCOL_AMENDMENT_02.json` binds sampling to physical GPU 1 if that slot is safe.
- Fresh B input-only audits: `protocol/FRESHB_INPUT_ONLY_AUDIT_LOCK.json` and its amendments 01–04. Cache features match neither current transformed condition nor unaugmented selected source for 150/150. Across all 98 selected-014 objects, raw view 000 is closer by max-abs for 84/98 and by cosine for 94/98; no exact raw-view match was found. This is not yet a color-causality result.
- The development set excludes Fresh B. C1 is frozen in `protocol/C1_DEV_METHOD_LOCK.json`; it remains gated on Phase B. No Fresh B candidate image/metric may be opened until the final method lock and validation amendment are in place.
- Dataset source-view tile: tile 0 of the six-view prediction grid (view 014 for reverse objects, view 000 otherwise). The reverse branch rotates only RGB/depth/normal tiles at positions 1 and 3; the source tile is not rotated.
- A model-load-only preflight used physical GPU 1 earlier and completed with zero diffusion generations. Current sampling has not started. The user authorized waiting for an idle time window. Latest snapshot: GPU0 28% utilization with ~19 GiB used; GPU1 0% utilization with ~19 GiB used and only ~12.5 GiB free. Do not compete with unknown workloads; continue CPU-only preparation.
- Current best lead is a Fresh B cache-to-source mismatch, including apparent view-000 origin on objects whose dataset source is view 014. This is not a color root cause until the same-noise global-embedding control shows a color/quality response.
- `run_chroma_anchor_evaluation.py` is prepared for CPU-only C1 correction/evaluation; its holdout mode requires a final repair lock and checks the prior Fresh B input and PNG identities before reading candidate outcomes. Existing Fresh B baseline PNGs use the locked checkpoint/config/runner/list, EulerDiscrete, 50 steps, and unique6 protocol; their inference package versions were not preserved.
- At the pre-Phase-B checkpoint, the all-150 current/raw embedding provenance audit, eight-object alternate-view sentinels, full 98-object raw-view comparison, and C1 method/evaluator preparation were complete. A read-only 1008 aggregate baseline summary was consulted for identity work, not for C1 tuning. The final holdout status is recorded below.

## Final V2 campaign handoff (2026-10-09)

- Phase B complete: 64/64 locked diffusion calls on the four development objects; 485.1 s sampler wall time; runtime SHA-256 `619ca45e907af714b49a1d3b998d7a8a19ab4831ab08b4254bed99762c1103ca`.
- Phase A output readouts complete: 384 per-view rows, four source-statistic rows, and four object-level summaries. See `runs/phase_b/A_COLOR_READOUT_SUMMARY.md` and `A_PER_OBJECT_COLOR_SUMMARY.csv`.
- C1 CPU development trial complete. Numeric criteria pass, but mandatory visual gate fails on both Fig. 4 failure cases (row 1 no clear correction; row 2 retains mismatch and shows a faint cyan/blue rim). See `C1_DEV_GATE_VERDICT.md` and `C_REPAIR_METHOD_LOCK.json`.
- Fresh B remains unopened for repair; no validation amendment exists; D is intentionally not run. Do not reopen the holdout or change the failed candidate's thresholds.
- Final interpretation: global embedding is a causal color-control channel; cache mismatch is a possible object-dependent contributor, with opposite response directions on the two failures. The full root cause remains unresolved, and no validated fix is supported.
- Deliverables are under this directory. `SHA256SUMS.txt` and `LOCAL_ONLY_SHA256SUMS.txt` were verified; campaign commit `98d22d18c4a1f85b7894c387544e0a13b73d823d` was pushed to `origin/codex/r1-color-cast-repair-v2-20261009`. All pre-existing untracked `1008/**` and `geotex/tests/test_residual_gate.py` remain outside the campaign commit. Paper worktree and raw 1008 material remain untouched.

## B2 latest handoff (2026-10-09)

This section supersedes the earlier statement that B2 sampling had not started and the cache follow-up was still pending.

- B2 attempts 01–03 remain preserved with zero diffusion calls; attempt 04 completed 8/8 on idle physical GPU 1 in 77.326 s.
- The locked treatment replaced only `global_embeds` with the official raw selected-source embedding. Paired condition, geometry, latent and VAE-posterior/RNG identity checks passed; all output PNG hashes were verified.
- B2 unseen-view ΔFG-CIEDE2000 was +0.1729 mean (95% object-bootstrap CI [−0.2044, +0.6810], 1/4 wins); the locked improvement gate failed. The two Fig. 4 panels show no clear visible correction. Fresh B remains sealed; do not run validation or parameter search for this treatment.
- B2 reports, tables and casebook are in the package root under `B2_RAW_SOURCE_EMBEDDING_*`; exact GT source identities and same-code CUDA metric-input reconstruction are in `B2_METRIC_INPUT_RECONSTRUCTION.json`. The original generation missed an in-process target-grid/mask-grid hash; the reconstruction is disclosed as supplemental, not presented as a captured run hash.
- Read-only historical Fresh C cache-builder audit is complete (zero GPU calls, no cache writes). The builder and frozen inference runner both seed Python/NumPy/Torch with `42 + ordered_object_index`; both use the same dataset item path, and the builder embeds transformed `cond_imgs`, not raw selected RGB. No code-level seed-policy discrepancy was found. This does not isolate a runtime-library cause for the separate Fresh C output mismatch or change B2's negative verdict.
- Visual review was unblinded and development-only. No independent validation result or successful repair claim is supported. Overall root cause remains partial; color fix is not validated; the prior Fresh C reproducibility mismatch remains unresolved.

## Local-only experiment outputs

- Generated B2 PNGs, run tables, casebook, runtime state and temporary reconstruction files are excluded by `.gitignore`; runner code and frozen protocol locks remain trackable.
- Generated 1008 raw RGB, masks, run traces and reproducibility scratch directories are also ignored. Historical files already tracked before this ignore update were left in their existing state.
- Follow-up commit `b1dd8b82743fa967eb4e96adbc4dd4976ab4d615` was pushed to `origin/codex/r1-color-cast-repair-v2-20261009`. Its scope is source, protocol, documentation and ignore rules; no generated images, metric tables, PDFs, logs or runtime files were staged.
