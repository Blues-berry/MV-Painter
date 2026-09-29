# Round-two reproducibility package (working snapshot)

This directory records the protocol and scripts for the second revision of
01549. It is not yet a public anonymous repository: the main GeoTex v1
checkpoint and its historical evaluation snapshot are still being recovered.
No third-party base model is redistributed here.

## Fixed protocol

- Main-adapter probe: `obj_0000`--`obj_0023`.
- Main-adapter holdout: `obj_0024`--`obj_0299` (276 objects).
- MV-Adapter calibration probe: the same first 24 objects.
- MV-Adapter holdout: `obj_0024`--`obj_0099` (76 objects).
- Corrected target views: camera IDs `[0, 15, 12, 16, 13, 14]`; the reversed
  order is `[14, 15, 0, 16, 12, 13]`. The old duplicated-top order is audit-only.
- Generation/evaluation resolution: `256x256`.
- Seed: `42`; denoising steps: `50`; bootstrap: 10,000 resamples, seed `20260928`.

The independent MV-Adapter SD2.1 experiment is documented separately in
`final/round2/mv_adapter/REPRODUCE_MV_ADAPTER.md`. It uses the official
image+geometry pipeline at `512x512`, seed `20260928`, and the mixed-geometry
policy currently required by the ten unrecovered source meshes. Its numbers
must not be merged with the main-adapter 256x256/seed-42 results.

## Commands

```bash
python geotex/round2_protocol.py --output results/round2_protocol.json
python geotex/round2_runner.py --dry-run \
  --checkpoint PATH_TO_GEOTEX_V1_PT \
  --config PATH_TO_EVAL_CONFIG \
  --output-root results/main_adapter_unique6 \
  --manifest results/main_adapter_manifest.json
python geotex/mv_adapter_round2.py --output results/mv_adapter_protocol.json
python geotex/round2_holdout.py --split main_holdout \
  --reference c3.csv --compare low=low.csv --compare high=high.csv \
  --metric fg_ssim --metric edge_ssim --metric psnr --metric fg_lpips \
  --lower-is-better fg_lpips --output results/main_holdout.json
```

The external MV-Adapter checkout must use the official SD2.1
image+geometry pipeline. Its model weights are downloaded by the official
script and are not part of this package. Each generated per-object CSV must
include the object identifier and the fixed camera/protocol manifest.

## Release checklist

Before making an anonymous URL public, add the exact commit hash, ZIP SHA-256,
checkpoint hashes (where redistribution is licensed), software versions,
download scripts for third-party models, and the final CSV-to-table command.
# Round-2 revision reproducibility package

This directory is the public, lightweight hand-off for the Computers &
Graphics round-two revision. It contains protocol overlays and schemas only;
model checkpoints, private training data, caches, and temporary GPU outputs
are intentionally excluded.

The complete author-review manuscript package is published under
`final/round2/`, including the layer-wise revision PDF/source, supplementary
material, response letter, reviewer evidence ledger, audit logs, raw paired
CSV summaries, manifests, input hashes, and comparison figures.

Key evidence locations:

- `final/round2/coordination/layer_lhl_v1/`: shared-input 24-object ×
  three-seed layer-wise ablation, raw CSVs, manifests, bootstrap summary,
  SHA-256 records, and visual comparisons.
- `final/round2/clean_dataset_v2/`: object-list and split manifests.
- `final/round2/stage_placement_276_20260929/`: historical strict-276
  stage-placement records and serialized-metric audit.
- `final/round2/main_adapter_baking/`: baking protocol and descriptive
  12-object case-study audit.
- `final/round2/mv_adapter/` and `final/round2/mvdiffusion/`: lightweight
  compatibility manifests and audit summaries; no model weights.
- `geotex/` and `scripts/`: evaluation, audit, aggregation, comparison-figure,
  and reproducibility utilities.

The layer-wise revision does not claim that layer-LHL, LHL, C3, or any CAI
rule is universally optimal. See
`final/round2/coordination/EXPERT_REVIEW_LAYERWISE_20260929.md` and
`FINAL_ACCEPTANCE_LAYERWISE_20260929.md` for the evidence boundary.
