#!/usr/bin/env bash
set -euo pipefail

for required in MVP_DATA_ROOT MVP_BASE_MODEL MVP_CHECKPOINT; do
  if [[ -z "${!required:-}" ]]; then
    printf 'Set %s to the locally available original asset.\n' "$required" >&2
    exit 2
  fi
done

export MVP_REPO_ROOT="${MVP_REPO_ROOT:-$PWD}"
export MVP_CONFIG="${MVP_CONFIG:-$MVP_REPO_ROOT/configs/clean_holdout.yaml}"
export MVP_OBJECT_LIST="${MVP_OBJECT_LIST:-$MVP_REPO_ROOT/data/FRESH_CONFIRM_300.txt}"
export MVP_RUN_DIR="${MVP_RUN_DIR:-$MVP_REPO_ROOT/reproduction_runs/a2_middle_W5}"
export MVP_CONDITIONS=a_middle_W5
export MVP_SHARD=0
export MVP_NUM_SHARDS=1
export MVP_DEVICE="${MVP_DEVICE:-cuda:0}"
export MVP_SAVE_PREDICTED=1
export MVP_SAVE_RESIDUAL=1

python3 scripts/run_validation_v3_experiment.py
