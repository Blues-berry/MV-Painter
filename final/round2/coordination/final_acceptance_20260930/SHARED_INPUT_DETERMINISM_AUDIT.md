# SHARED_INPUT_DETERMINISM_AUDIT (final acceptance, 2026-09-30)

## SHARED_INPUT_AUDIT = PASS

## Design

Rebuild the exact input section of
`scripts/run_layer_confirmation_276_20260930.py` (the strict-276 confirmation
runner) for **10 objects x 5 methods** and SHA-256 every input artifact.
Two fully separate processes (`pass1`, `pass2`) rerun the audit; PASS requires
every hash pair to agree. Because the per-method schedules are constructed
but never applied before generation, rebuilding inputs once per method also
proves empirically that schedule choice cannot perturb inputs.

- Object sample: `random.Random(20260930).sample(range(276), 10)` =
  indices `[3, 23, 45, 60, 88, 137, 166, 199, 232, 262]` (see JSON).
- Methods: `global_fixed_low` (1.25), `global_c3` (1.25/2.50/1.25),
  `layer_fixed_mean` (1.65/1.65/0.58), `layer_lhl`, `layer_llh` — definitions
  copied verbatim from the confirmation runner + frozen global semantics.
- Hashed per (object, method): raw reference PNGs (000/014), cond_imgs raw +
  resized, VAE cond_lat, target_imgs raw + grid, normals raw + grid, depth
  raw + grid, foreground mask grid, geo_clean, geo_encoder feature dict,
  global_embeds, initial latent (GPU fp16 as in the runner + CPU fp32
  reference), Euler scheduler timesteps/sigmas.
- Seeding: `object_seed = 42 + obj_idx` for random/np/torch before
  `collate_batch`; latent seed 42 (identical to the runner).

## Results

| Check | Rows | Mismatches |
|---|---:|---:|
| pass1 vs pass2 (separate processes, all fields) | 50 | **0** |
| across methods within a process (same object) | 4 pairs x 10 objects | **0** |

Raw machine-readable outputs: `SHARED_INPUT_DETERMINISM_AUDIT.pass1.json`,
`SHARED_INPUT_DETERMINISM_AUDIT.pass2.json` (full 50-row hash tables).

## Consequences

1. Same object + seed -> bit-identical inputs across methods AND across
   processes. All same-run paired comparisons in the paper rest on genuinely
   shared inputs; the strict-276 confirmation runs (separate invocations of
   the same runner) share per-object input realizations by construction, now
   verified empirically.
2. The bake "same-draw" claim (layer bake panels vs global bake controls,
   `scripts/generate_layer_bake_panels_20260930.py` /
   `scripts/generate_global_bake_controls_20260930.py`) uses line-identical
   input construction (seed 42 + eval-index, same collate/prepare/latent
   sequence) — the restart-determinism result above therefore extends to
   that pair of runners.
3. Combined with EVAL_AUGMENTATION_AUDIT (LEGAL_INFERENCE_PREPROCESSING),
   the reference-realization draw is a frozen, shared protocol element.
