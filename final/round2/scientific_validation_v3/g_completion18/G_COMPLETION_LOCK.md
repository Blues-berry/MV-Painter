# G_COMPLETION_LOCK — finish the original frozen G cohort

Frozen: 2026-10-05 UTC, before any completion output was generated.
Parent design: EXPERIMENT_G_DESIGN.md (frozen 2026-10-02).
Parent manifest SHA256: dd617e36c6fcf532f767d81325a10cf60a590d5ed9587e7326818cfa570214f5.

## Scope and frozen settings

This completes the original 99-object G cohort, not a new hypothesis or
adaptive condition search. The original ledgers contain 81 unique objects and
18 planned objects never run. The only added rows are the IDs in
missing18_objects.txt. Each gets the same 16 frozen conditions (baseline plus
three depth groups × five windows), requested scales 0.75/1.00, six views,
50 DDPM steps, 512×512, seed 42, and the same paired metric implementation.
No scale, mapping, metric, seed, runner, or condition changed.

Two disjoint nine-object manifests are run as independent one-shard jobs to
avoid the previous shard-index/resume failure mode. Outputs go to separate new
folders; original G ledgers and images are immutable. At merge, duplicate
original object-condition pairs are deduplicated only after verifying every
metric field is identical; elapsed time is excluded from equality checks.

## Missing IDs and inputs

The 18 IDs, GLB SHA256 values, and six official-order GT-view hashes per
object are in G_COMPLETION_INPUT_HASHES.json. All missing rows report
available meshes/renders; GLB hashes match the frozen manifest. Each runner
manifest is derived only by restricting the original manifest to its listed
IDs.

## Execution provenance

Runner stack and model-weight hashes, base-model config hashes, parent and
subset manifest hashes, source-input hashes, Torch/CUDA versions, and the
missing-ID list hash are frozen in G_COMPLETION_INPUT_HASHES.json and
SHA256SUMS.txt. No method output from these 18 objects was inspected before
this lock.
