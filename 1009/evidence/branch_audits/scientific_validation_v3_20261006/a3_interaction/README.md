# A3 interaction evidence package

This package restores the compact source rows needed to reproduce the A3 interaction values reported in the active 1008 Supplement. The archived source is `codex/scientific-validation-v3-20261006` at `12da08c7056f5f0c36677668d640477bfb249454`; no registered worktree or uncommitted source state exists.

## Included

- Sixteen condition-specific CSVs: A3 baseline plus 15 layer-window conditions, 300 objects per condition (4,800 rows total). These split files reconstruct the archived combined ledger exactly; the duplicate 4,800-row combined CSV is therefore omitted.
- Four sanitized run-manifest shards, the frozen A3 normalization specification, and the archived corrected interaction-test result snapshot. Absolute machine paths were normalized; the local model checkpoint was not copied, and its source SHA-256 remains in each manifest. The 300-object list is byte-identical to the tracked list already in the main reproducibility release.
- `reproduce_a3_interaction_wald.py`, adapted from the archived cluster-robust Wald audit to read the retained per-condition CSVs rather than absent `rows_shard*.json` files. It uses CPU-only NumPy/SciPy and does not run model inference.

## Reproduction

From this directory:

```bash
python reproduce_a3_interaction_wald.py --input-dir conditions --output /tmp/a3-interaction-reproduction.json
```

The archived corrected results are FG-LPIPS `W=657.237`, `p=1.1444555792962468e-136` and FG-PSNR `W=1389.118`, `p=1.2756891492864911e-294`. CPU reaggregation from the condition rows matches both W values to three decimals and the saved p-values within relative tolerance `1e-10`. These values are interaction tests on the A3 intervention grid; they do not establish a dose-independent mechanism. Current main classifies the deep condition as dose-normalized confirmation, middle as approximate diagnostic, and shallow as stress-only. See `1009/evidence/scientific_validation_v3/A3_DOSE_VALIDITY_AUDIT.md` and the active Supplement for the retained limits.

The source's older `layermap_dosenorm*.json` bootstrap outputs were excluded because the original additive-residual bootstrap has a documented zero-power defect; the corrected cluster-robust Wald result is retained instead. No images, GLBs, residual logs, checkpoints, or other campaign outputs were copied.

`SOURCE_FILE_HASHES.csv` records source and destination SHA-256 for every source-derived file. Run `sha256sum -c SHA256SUMS.txt` from this directory to verify the package.
