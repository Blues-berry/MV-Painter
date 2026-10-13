# Fresh C deterministic input-embedding preprocessing amendment — version 2

**Amendment date:** 2026-10-06 UTC  
**Status:** frozen pre-inference after amendment-attempt-1 startup failure; no Fresh C method output existed at issuance  
**Applies to:** the frozen Fresh C primary confirmation and its separate LLH/linear revision-era addendum

## Reason for amendment

The first two-object technical smoke stopped before completing a denoising
step. The unchanged runner's generation function requires
`batch["global_embeds"]`, while the newly rendered Fresh C objects did not
contain the optional `embeddings/global_embeds.npy` cache. Both smoke shards
exited with `KeyError: 'global_embeds'`; neither produced a prediction, metric
row, nor residual trace. The original logs and failed execution state remain
preserved.

Amendment attempt 1 is preserved at
`FRESH_C_INPUT_EMBEDDING_PREPROCESSING_AMENDMENT_20261006.json`. Its builder
failed before model loading because the direct-script import path omitted the
repository's `geotex` package. No embedding cache or method output was written.
That exact attempt is recorded in
`1006/data/fresh_c/FRESH_C_EMBEDDING_PREPROCESSING_ATTEMPT1_20261006.json`.
This version binds the corrected import path and the final orchestration and
audit hashes; it does not alter the scientific input or inference protocol.

This amendment adds only the missing inference input. It does not change the
frozen object list, data renders, condition registry, requested scales, native
caps, checkpoint, config, runner, generation or metric code, seed policy,
statistical families, or cohort. The original C protocol and original
LLH/linear addendum lock remain unchanged and are retained as the historical
locks to which this amendment is subordinate. The only execution-code edits
are orchestration and audit checks that require the new cache manifest and
verify the same embedding identity across both runs. The amendment JSON
preserves the original orchestration digests alongside replacement code
hashes.

## Locked embedding construction

For each frozen object index `i`, the builder resets Python, NumPy, and Torch
seeds to `42 + i`, then obtains that object's `cond_imgs` by calling the same
`MVPainterData` dataset and `unique6` configuration used by the locked runner.
The selected source view follows the dataset's existing alpha rule: compare
the zero-alpha-pixel counts in views 000 and 014; use view 014 only when view
000 has the larger count, otherwise use view 000. The embedding is computed
from the resulting, deterministically augmented `cond_imgs` tensor using the
configured image processor and the two vision encoders from the configured
pretrained pipeline. Their projected image embeddings are concatenated along
the feature dimension and saved as float32 at
`renders/<UID>/embeddings/global_embeds.npy`.

The builder independently repeats the seeded dataset access and requires the
`cond_imgs` tensor hash to match before accepting the cache. It records the
UID and ordered-list hashes, seed, chosen source view, source image hashes,
condition tensor hash, cache shape/dtype/file hash, config/checkpoint and
preprocessing-code hashes, and the vision-encoder/processor file hashes. An
existing cache is reused only if its bytes exactly match the newly computed
array; conflicting bytes stop the build. The final manifest is written only
after every frozen UID passes.

This makes `global_embeds` a fixed, shared per-object input across all
conditions. It aligns the embedding with the exact condition tensor emitted by
the locked seeded data path. It does not claim to reconstruct undocumented
historical cache-generation behavior. No output quality or method score is
read or used during construction.

## Gate and resume rules

The primary launcher and both integrity analyzers must verify the PASS
embedding manifest, frozen N and ordered UID hash, every per-object cache
hash, and the same manifest hash in the primary and addendum launch records.
The builder refuses to run if any method row, run manifest, prediction, or
residual output exists in either inference namespace. The retry smoke uses a
new directory, preserving the original failed logs. Analysis remains blocked
until the existing primary and addendum integrity gates independently pass.

The machine-readable amendment binds the source and orchestration hashes,
this document hash, the original protocol and addendum-lock hashes, and the
pre-inference failure-log hashes.
