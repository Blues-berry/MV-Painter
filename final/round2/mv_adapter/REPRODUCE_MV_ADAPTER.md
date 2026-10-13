# Reproduce the MV-Adapter Round 2 run

Run from `/4T/CXY/MV-Painter` with the official MV-Adapter snapshot at commit
`4277e0018232bac82bb2c103caf0893cedb711be`. The local SD2.1 base resolves to
the public `Manojb/stable-diffusion-2-1-base` snapshot at commit
`0094d483a120f3f33dafbd187ea4aa60d10de75c`; component hashes are in
`BASE_MODEL_VERIFICATION.json`.

The calibration and diagnostic holdout commands below are the preserved
historical mixed-proxy runs. Their explicit proxy meshes are listed in
`proxy_manifest.json`; these outputs are not exact-geometry protocol results.
The ten original GLBs have since been recovered from Objaverse-XL Smithsonian
and verified in `GLB_RECOVERY_AUDIT.md`.

## Static and regression checks

```bash
pytest -q geotex/tests final/round2/mv_adapter/tests/test_geometry_scale.py
python -m py_compile \
  final/round2/mv_adapter/run_experiment.py \
  final/round2/mv_adapter/analyze_calibration.py \
  final/round2/mv_adapter/analyze_holdout_diagnostic.py
```

## Calibration

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 PYTHONPATH=. \
python final/round2/mv_adapter/run_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --output-dir final/round2/mv_adapter/results/calibration_mixed_proxy_50 \
  --split calibration --geometry-source mixed \
  --proxy-manifest final/round2/mv_adapter/proxy_manifest.json \
  --device cuda:0 --seed 20260928 --steps 50 --low 0.75 --high 1.5 \
  --schedule fixed_low --schedule fixed_1.0 --schedule fixed_1.25 \
  --schedule fixed_high --schedule LLL --schedule LLH --schedule LHL \
  --schedule LHH --schedule HLL --schedule HLH --schedule HHL --schedule HHH

python final/round2/mv_adapter/analyze_calibration.py \
  --csv final/round2/mv_adapter/results/calibration_mixed_proxy_50/per_object_metrics.csv \
  --rule final/round2/mv_adapter/calibration_rule.json \
  --output final/round2/mv_adapter/results/calibration_mixed_proxy_50/calibration_analysis.json
```

The frozen result is `NO_CLEAR_TRADEOFF`; the sole fixed-scale Pareto
candidate is `fixed_1.0`. The frozen rule does not define a unique winner
among the eight stage combinations, so no CAI schedule is invented.

## Available diagnostic holdout

This is not the formal six-comparison holdout. It compares the sole Pareto
candidate against no geometry because conservative/aggressive and CAI labels
are undefined under the frozen result.

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 PYTHONPATH=. \
python final/round2/mv_adapter/run_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --output-dir final/round2/mv_adapter/results/holdout_mixed_proxy_single_pareto_50_retry \
  --split holdout --geometry-source mixed \
  --proxy-manifest final/round2/mv_adapter/proxy_manifest.json \
  --device cuda:0 --seed 20260928 --steps 50 --low 0.75 --high 1.5 \
  --schedule no_geometry --schedule fixed_1.0

python final/round2/mv_adapter/analyze_holdout_diagnostic.py \
  --csv final/round2/mv_adapter/results/holdout_mixed_proxy_single_pareto_50_retry/per_object_metrics.csv \
  --output final/round2/mv_adapter/results/holdout_mixed_proxy_single_pareto_50_retry/paired_bootstrap_diagnostic.json
```

## Exact-only reruns

The completed Exact-only outputs are kept separately from the historical
mixed-proxy outputs:

- `results/calibration_exact_24/`: 288 rows, 24 objects, 12 schedules.
- `results/holdout_exact_76/`: 380 rows, 76 objects, five defined schedules.
- `results/holdout_exact_76/paired_bootstrap_exact.json`: 10,000-resample
  paired bootstrap.

The exact commands, object-level provenance, SHA-256 values, and the reason
the sixth CAI comparison is undefined are recorded in
`GLB_RECOVERY_MANIFEST.json` and `GLB_RECOVERY_AUDIT.md`.
