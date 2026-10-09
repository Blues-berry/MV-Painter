# Scientific Validation V3 reproducibility release

This is a curated, frozen source snapshot for the V3 scientific validation. It is separate from the current active code under the repository root and must not be used to relabel or regenerate other cohorts. The snapshot preserves the runner/source identity at commit `5359dd773a5093508755985ecd63a8104b96d8fe`.

## Included

- Frozen analysis scripts and one portable experiment runner.
- The historical `MVPainter/` and `geotex/` source dependencies required by that runner.
- The clean holdout configuration, tested-environment requirements, and text provenance records.
- Ordered 300-object A2 and 150-object B UID lists and per-object metric CSVs (about 3.4 MB total).
- The summary table, protocol summary, Apache 2.0 license, and per-file `ASSET_HASHES.csv`.

No model weights, rendered input dataset, participant records, generated RGB/GLB images, tensor caches, checkpoints, per-step residual logs, or JSON files are included. The source worktree retains the original JSON manifests locally. `RUNNER_PROVENANCE.md` and `ENVIRONMENT_TESTED.md` preserve the relevant hashes and runtime facts in text form.

## Rebuild the analysis table

From this directory, run:

```sh
python3 analysis/build_core_evidence_table.py
python3 analysis/analyze_v3.py pairwise \
  --run-dir data/campaign_B \
  --a layer_llh --b lfm_exact \
  --metrics fg_psnr,fg_lpips
```

The analysis uses object-level paired bootstrap, 10,000 draws, and seed `20261002`. The A2 layer-by-window interaction uses the validated object-cluster Wald analysis; the prior zero-power null bootstrap is retired. The 150-object B extract supports only the predeclared LLH contrasts and does not represent the complete 30-condition campaign.

## Regenerate one A2 condition

Generation additionally requires the original source renders, base model, checkpoint, and compatible CUDA environment. Set the documented `MVP_*` variables from `protocol/SCIENTIFIC_PROTOCOL_SUMMARY.md`; use `configs/clean_holdout.yaml` and `data/FRESH_CONFIRM_300.txt`. The external checkpoint must match the SHA-256 in `RUNNER_PROVENANCE.md`. The portable runner writes new artifacts only to `MVP_RUN_DIR`. No GPU generation was run during repository consolidation.

This package reproduces selected frozen analysis evidence. It is not a complete source-dataset or model release.
