# ROBUSTNESS1_SHARED_INPUT_AUDIT (Realization-1 namespace)

## Verdict: PASS

## Design

Adapted from the frozen R0 shared-input audit
(`final_acceptance_20260930/SHARED_INPUT_DETERMINISM_AUDIT.md`): 10 fixed
strict-276 objects (sample indices [11, 25, 113, 141, 157, 207, 214, 236, 239, 256], drawn once
with `random.Random(20260930)`) x Core-5 methods, SHA-256 over every input
artifact of the frozen confirmation-runner input section, but under the
Realization-1 reference-seed namespace **object_seed = 10042 + obj_idx**
(R0 used 42 + obj_idx). Two fully separate Python processes (`pass1`,
`pass2`) reran the audit.

Hashed per (object, method): raw reference PNGs (000/014), cond_imgs raw +
resized, VAE cond-latent, target raw + grid, normals raw + grid, depth raw +
grid, mask grid, geo_clean, geo_encoder feature dict, global embeds,
initial latent (GPU fp16 + CPU fp32, seed 42), Euler scheduler
timesteps/sigmas.

## Results

| Check | Rows | Mismatches |
|---|---:|---:|
| pass1 vs pass2 (separate processes, all fields) | 50 | 0 |
| across methods within a process (same object) | 4 pairs x 10 objects x 2 passes | 0 |

Cross-realization consistency (vs the frozen R0 audit, same 10 objects):

| Component class | Fields | Expected vs R0 | Observed |
|---|---|---|---|
| deterministic (targets/normals/depth/mask/global embeds/geo) | 10 fields x 50 rows | identical | 500 matches |
| reference-derived (cond raw/resized/latent) | 3 fields x 50 rows | different | 150 differ |

Anomalies: 0.

Interpretation: the deterministic components being bit-identical to R0
proves the protocol (dataset, object list, view mode, latent seed 42,
scheduler) is unchanged; the reference-derived components differing on every
row proves Realization-1 is a genuinely independent reference-preprocessing
draw, not a near-duplicate of R0.

Initial latent (seed 42) GPU/CPU hashes and scheduler timestep/sigma hashes
match the frozen R0 audit exactly.

## Gate decision

PASS — the formal strict-276 x Core-5 (1380 rows) run may start.

Raw tables: `ROBUSTNESS1_SHARED_INPUT_AUDIT.pass1.json`,
`ROBUSTNESS1_SHARED_INPUT_AUDIT.pass2.json` (full 50-row hash tables).
