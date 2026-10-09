# MV-Adapter mapping sensitivity records

This package preserves two distinct tests from the archived Round-2 branch. Both use the same 76-object Exact holdout, checkpoint, runner family, and global comparison rows. They are separate mapping/scale analyses and are not an independent replication of the main-backbone result.

## Budget-neutral B′ sensitivity

Protocol `budget_neutral_Bprime_20261001/protocol.md` was committed at `a6d281b83b8ee7314e2fab78a3069d9843f0f89f` (2026-10-01 01:52:54 UTC), before the B′ result rows first appeared at `77a1efa4142c4b06ce7581a90796e0f427b213c8` (02:27:49 UTC). The frozen C mapping and B′ alternative use normalized per-point vectors with mean 1. The D=(1,2,1) partition is arithmetically identical to C and was checked on three objects; it does not require a separate 76-object run.

The 76-object B′ result is mixed and bounded. CIEDE2000 and GT-relative texture error favor B′ over the tested global controls with intervals excluding zero. PSNR points in the same direction but its interval crosses zero; FG-SSIM reverses toward the global controls; LPIPS is unresolved. B′ versus C has no separated metric. The CPU reanalysis regenerated the source bootstrap JSON byte-for-byte. The preflight's C rows reproduce the frozen M1 values and D reproduces C bit-for-bit on all three checked objects.

This supports only a pre-specified, budget-neutral sensitivity on the tested MV-Adapter cohort and conditions. It does not establish architecture-general transfer or the absence of mapping effects on other interfaces/cohorts.

## Budget-changing M3 sensitivity

`budget_changing_M3_20261001/protocol.md` and its M3 metric rows were first recorded together in commit `75a4068e30098a3d758bec83c48b4d1f00346165`. The claimed pre-output timing cannot be independently verified from Git history. Treat this result as retrospective sensitivity evidence.

M3 assigns the frozen source group values to a different point grouping, producing per-point values `[0.41953, 0.41953, 1.19349, 1.19349]` and a mean total multiplier of approximately 0.8065. It therefore changes total residual budget as well as grouping. The source analysis reports 16/18 sign/interval classifications as stable, one tiny edge-SSIM attenuation, and one near-zero LPIPS sign flip. This does not isolate a partition-only effect and must not be combined with the budget-neutral B′ result.

The adapted CPU analyzer regenerated the source M3 bootstrap JSON and 36-row comparison CSV byte-for-byte. It never loads model assets or runs inference. Per-object CSVs, small run configurations, original protocol/report snapshots, and source hashes are retained; images, checkpoints, generated logs, and model assets are not.

## Reproduction

From this directory, with NumPy available:

```bash
python budget_neutral_Bprime_20261001/reproduce_mapping_sensitivity.py \
  --inputs shared_inputs --output-dir /tmp/mvadapter-bprime-reproduction

python budget_changing_M3_20261001/reproduce_mapping_sensitivity.py \
  --inputs shared_inputs --output-dir /tmp/mvadapter-m3-reproduction
```

The scripts read only the included per-object metric CSVs and write aggregate statistics to the requested output directories. Adaptations replace historical absolute paths with package-relative inputs, add an output-directory option, and fix output ordering/line endings for deterministic reproduction. Original source hashes and retained-file hashes are recorded separately.

## Provenance and integrity

`SOURCE_FILE_HASHES.csv` maps each retained input and both adapted scripts to its source path at archived private-remote HEAD `5a059b30eba959e69a2f36f484f06807e5c2c152`, with source and retained SHA-256 values. The source snapshots are byte-identical except for the two documented reproducers. `SHA256SUMS.txt` covers every package file other than itself; verify it from this directory with `sha256sum -c SHA256SUMS.txt`.
