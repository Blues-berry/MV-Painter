# Post-load + Output Equivalence Results (2026-09-30, addendum)

## Section 27 - post-load state equivalence

```
POSTLOAD_STATE_EQUIVALENT = YES
shared keys: 1552; bitwise-identical tensors: 1552; value diffs: 0
only_in_compat: 0; only_in_mirror: 0; shape mismatch: 0; dtype mismatch: 0
```

Both models constructed DepthGenerator with their own diffusers base
(`sd21_depth_compat` vs `sd2_depth_native_mirror`), then loaded the identical
`depth_gen_new.pth` through the same explicit key migration with
`strict=True`. Every loaded tensor is bitwise identical (per-tensor SHA-256
and max/mean abs difference checks). Machine record:
`postload_equivalence.json`.

## Section 28 - single-object output equivalence

obj_0024 (first valid holdout object), official runner, seed 42, 50 steps,
12 views, both bases:

```
OUTPUT_EQUIVALENT = YES
PNG SHA-256 equal: 12/12 (bitwise)
max absolute pixel difference on any view: 0
```

Dirs: `results/phase_c_output_eq_compat/`, `results/phase_c_output_eq_mirror/`.

## Section 29 verdict

```
POSTLOAD_STATE_EQUIVALENT = YES
OUTPUT_EQUIVALENT         = YES
NATIVE_MIRROR_EQUIVALENT  = YES
native rerun of 75 objects: NOT REQUIRED
```

The existing 75-object deployment (and every Phase D panel condition run on
the compat base) remains the valid deployment record; the native mirror is a
bitwise-equivalent provenance upgrade of the same weights.
