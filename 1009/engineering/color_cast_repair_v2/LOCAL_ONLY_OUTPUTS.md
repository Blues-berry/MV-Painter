# Local-only image intermediates

The following image files remain in the isolated worktree and are not included in the campaign commit. Their paths and SHA-256 values are recorded in the result/identity CSVs and `LOCAL_ONLY_SHA256SUMS.txt`. The tracked `SHA256SUMS.txt` verifies the committed package, including that local-only hash inventory. The reviewed pathway and before/after panels are embedded in the tracked PDFs.

- `runs/phase_b/predictions/`: 64 generated Phase B PNGs, approximately 18 MB. They contain every locked perturbation-arm output; all per-view metrics and PNG SHA-256 values are in `runs/phase_b/COLOR_INTERVENTION_RESULTS.csv`. The four-object `A_COLOR_PATHWAY_GALLERY.pdf` embeds source condition, GT unique6, No Adapter, GFL, recomputed-embedding GFL, and LLH reference-view panels. The complete 64-image set is retained locally for pixel-level audit without adding generated intermediate payload to the repository.
- `runs/phase_c/dev/predictions/`: four six-view C1 candidate grids, approximately 1.1 MB. Their identity hashes are in the C1 paired results and manual review; the candidate grids appear in the tracked four-page before/after casebook.
- `runs/phase_c/dev/case_images/`: source condition, GT, and mask-derived casebook inputs, approximately 0.9 MB. Their hashes are recorded in the paired results and manual-review manifest; reviewed panels are embedded in the casebook.

No checkpoint, dataset tree, or original paper-worktree file is copied into this campaign. Those remain referenced by immutable hashes and source paths in the protocol and run manifests.
