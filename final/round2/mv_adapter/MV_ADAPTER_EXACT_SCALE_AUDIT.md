# MV-Adapter Exact Scale Audit

Date: 2026-09-29

## Result

The original Exact holdout used `--low 0.75 --high 1.5`.

`run_experiment.py` dispatches the schedules as follows:

- `fixed_low` → `constant_scale(low)`;
- `fixed_1.0` → `constant_scale(1.0)`;
- `linear_warmup` → `linear_warmup(low, high)`;
- `cosine_bump` → `cosine_bump(low, high)`.

The implementation is:

```text
linear(progress) = low + (high - low) * progress
cosine(progress) = low + (high - low) * sin(pi * progress)
```

Therefore the historical `linear_warmup` and `cosine_bump` rows are in the
0.75–1.50 range and cannot be used as same-range baselines for
`LHL=(0.75,1.00,0.75)`. The historical 76×5 result remains preserved and is
not rewritten.

The constant schedules are safe to reuse:

- `fixed_low` is always 0.75 and does not use `high`;
- `fixed_1.0` is always 1.0 and does not use either bound;
- `no_geometry` is always 0.0.

## Artifacts audited

- Historical configuration: `results/holdout_exact_76/run_config.json`;
- Runner: `run_experiment.py`;
- Schedule implementation: `upstream/mvadapter/geometry_scale.py`;
- Matched-range configuration: `results/holdout_exact_matched_range_76/run_config.json`;
- Matched-range protocol: `results/holdout_exact_matched_range_76/PROTOCOL.json`.

## Code and model provenance

| Artifact | SHA-256 |
|---|---|
| `run_experiment.py` | `ac29e58c7c8efa1d95799cb2d02b59f34941252a151ff7ce16524d7791a1f6a3` |
| `geometry_scale.py` | `a89f15042696b06a1e8fb5196fc7da2cd816cbf1cc94f49c880edf6188edcde4` |
| `data_manifest.json` | `d256c9327d35c26dbcab4dc0cb30d1cffb7802e27827d9950763529df0211db5` |
| base-model provenance record | `BASE_MODEL_VERIFICATION.json` |

The actual SD2.1 base is `Manojb/stable-diffusion-2-1-base`, commit
`0094d483a120f3f33dafbd187ea4aa60d10de75c`. Component hashes remain in
`BASE_MODEL_VERIFICATION.json`; no model was downloaded for this audit.

## Protocol interpretation

The original 76×5 run remains a historical Exact result with `high=1.50` for
linear/cosine. The new 0.75–1.00 linear/cosine run is a targeted follow-up for
scale fairness, not a retroactive replacement and not part of the original
confirmatory freeze. The selected-pair stage result remains set-valued and
undefined; no CAI winner is inferred from this audit.

## Reproduction command for the matched-range supplement

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 PYTHONPATH=. \
python final/round2/mv_adapter/run_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --output-dir final/round2/mv_adapter/results/holdout_exact_matched_range_76 \
  --split holdout --geometry-source exact --device cuda:0 \
  --seed 20260928 --steps 50 --low 0.75 --high 1.0 \
  --schedule linear_warmup --schedule cosine_bump
```
