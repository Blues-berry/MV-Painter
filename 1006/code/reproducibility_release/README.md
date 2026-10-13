# Scientific Validation V3 reproducibility release

This small, anonymized release separates analysis of the frozen per-object
results from regeneration of one A2 condition. It contains no participant
key, human responses, model weights, rendered source dataset, caches, or
generated image archive.

## Contents

- `scripts/run_validation_v3_experiment.py`: the campaign runner from source
  commit `5359dd773a5093508755985ecd63a8104b96d8fe`, with only the four
  repository/config/checkpoint/protocol roots changed to environment-variable
  paths. The original runner SHA256 and portable runner SHA256 are recorded in
  `protocol/RUNNER_PROVENANCE.json`.
- `data/campaign_A2/`: per-object metrics for the 3×5 A2 map and shared
  baseline, from 300 frozen objects.
- `data/campaign_B/`: four conditions supporting the preregistered LLH versus
  LFM-EXACT and LLH versus HLL/LLL comparisons on 150 frozen objects. The
  post-unblinding HLL versus LLL contrast is labeled exploratory.
- `analysis/build_core_evidence_table.py`: regenerates a compact evidence
  table, the validated A2 cluster-Wald interaction, and paired bootstrap
  summaries from those rows.
- `analysis/analyze_v3.py`: the frozen paired-bootstrap implementation used
  for the B comparison.
- `outputs/core_evidence_table.md`: generated A2/B summary, including the
  preregistered directional checks and practical-equivalence margins.
- `data/FRESH_CONFIRM_300.txt` and `data/FRESH_CONFIRM_B_150.txt`: ordered
  object IDs; their SHA256 values are recorded in the provenance JSON.

## Rebuild the analysis table

From this repository root, run:

```sh
python3 analysis/build_core_evidence_table.py
python3 analysis/analyze_v3.py pairwise \
  --run-dir data/campaign_B \
  --a layer_llh --b lfm_exact \
  --metrics fg_psnr,fg_lpips \
  --out outputs/b_llh_minus_lfm_exact.json
```

The table uses the object as the resampling unit, 10,000 paired bootstrap
draws, seed `20261002`, and the original metric directions. The A2 interaction
uses the validated object-cluster Wald test; it does not repeat the retired
zero-power bootstrap-null test. Outputs contain no run timestamps or machine
paths, so separate processes should produce byte-identical files under the
tested environment.

## Regenerate one A2 condition

The runner needs the original data tree, base image model, and trained
checkpoint supplied separately. No asset path is embedded in this release.
The asset owner must set these variables to their local copies:

```sh
export MVP_DATA_ROOT=/path/to/fresh_confirm_v3_renders
export MVP_BASE_MODEL=/path/to/base_model
export MVP_CHECKPOINT=/path/to/geotex_checkpoint.pt
```

Then run one complete 300-object A2 condition:

```sh
export MVP_REPO_ROOT="$PWD"
export MVP_CONFIG="$PWD/configs/clean_holdout.yaml"
export MVP_OBJECT_LIST="$PWD/data/FRESH_CONFIRM_300.txt"
export MVP_RUN_DIR="$PWD/reproduction_runs/a2_middle_W5"
export MVP_CONDITIONS=a_middle_W5
export MVP_SHARD=0
export MVP_NUM_SHARDS=1
export MVP_DEVICE=cuda:0
export MVP_SAVE_PREDICTED=1
export MVP_SAVE_RESIDUAL=1
python3 scripts/run_validation_v3_experiment.py
```

For the formal FRESH_CONFIRM_300 cohort, `MVP_DATA_ROOT` must point to the
`fresh_confirm_v3_renders` directory, whose immediate children are the 300
frozen object UIDs. The similarly named `rendered_full` training tree is not
the experiment input and will not load this cohort. The checkpoint must have SHA256
`0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
The ordered A2 object list SHA256 is recorded in
`protocol/RUNNER_PROVENANCE.json`. This runner will record the supplied asset
hashes in its output manifest.

## Tested environment and scope

`environment/runtime_tested.json` records the Python, framework, CUDA build,
and GPU versions used for the clean-clone audit. A full model-generation
reproduction still requires access to the original data and weights; the
included CSVs reproduce the stated result-row analyses without those assets.
The B extract does not reproduce the full 30-condition campaign.
The existence of this local release does not imply it has been published to a
remote repository.
