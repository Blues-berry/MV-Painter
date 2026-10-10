# Fresh C technical smoke failure record

**Disposition:** recorded pre-inference technical stop; no method output was generated.  
**Cohort:** the frozen Fresh C cohort remains unchanged (N=300).  
**Original protocol:** retained without edits.

Both two-object smoke shards exited with status 1. The runner loaded the frozen
checkpoint and dataset, selected its condition image, and then stopped in
`geotex.explore_contradiction.generate_with_schedule` because the dataset
batch did not contain the required `global_embeds` key. Fresh C renders did not
include the optional per-object embedding cache. The exception occurred before
the denoising loop; no prediction, metric row, or residual trace was written.

The original shard logs are preserved at
`1006/data/fresh_c/runs/technical_smoke/shard0.log` and `shard1.log`; their
SHA-256 hashes and the stopped closure state are recorded in
`1006/data/fresh_c/FRESH_C_CLOSURE_FAILED_ATTEMPT3.json`. No run directory,
cohort UID, method condition, model source, cap, or analysis family is changed.

The pre-inference repair is limited to a deterministic input-preprocessing
amendment: build the missing global embeddings from each frozen object's exact
seeded `cond_imgs` using the configured image processor and two vision
encoders, verify the ordered cohort and each cache hash, then repeat the
two-object residual-only smoke in a new directory. The new cache manifest must
pass before either primary or addendum inference can launch. The prior failed
logs remain intact; any retry failure is preserved as a separate attempt.
