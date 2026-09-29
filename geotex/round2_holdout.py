"""Aggregate paired holdout results from round-two per-object CSV files.

Example::

    python geotex/round2_holdout.py --reference c3.csv \
      --compare low=low.csv --compare high=high.csv \
      --output results/main_holdout.json

CSV rows must contain an object identifier (``object``, ``object_id`` or
``object_idx``) and the requested metric columns.  The script never derives a
split from the rows: the fixed object IDs are passed explicitly by ``--split``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .round2_stats import (
        BOOTSTRAP_SEED,
        MAIN_HOLDOUT_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        PROBE_IDS,
        paired_csv_summary,
        read_object_csv,
        validate_split,
        write_json,
    )
except ImportError:  # direct script execution
    from round2_stats import (
        BOOTSTRAP_SEED,
        MAIN_HOLDOUT_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        PROBE_IDS,
        paired_csv_summary,
        read_object_csv,
        validate_split,
        write_json,
    )


def parse_named_paths(values):
    result = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError("expected NAME=CSV_PATH")
        name, path = value.split("=", 1)
        if not name or not path:
            raise argparse.ArgumentTypeError("expected non-empty NAME and CSV_PATH")
        result[name] = Path(path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, help="reference method CSV")
    parser.add_argument("--compare", action="append", required=True, help="NAME=CSV_PATH")
    parser.add_argument("--split", choices=("probe", "main_holdout", "mv_adapter_holdout"), default="main_holdout")
    parser.add_argument("--metric", action="append", required=True)
    parser.add_argument("--lower-is-better", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--resamples", type=int, default=10000)
    args = parser.parse_args()

    ids = {"probe": PROBE_IDS, "main_holdout": MAIN_HOLDOUT_IDS, "mv_adapter_holdout": MV_ADAPTER_HOLDOUT_IDS}[args.split]
    validate_split(ids, split=args.split)
    reference = read_object_csv(args.reference)
    comparisons = {}
    for name, path in parse_named_paths(args.compare).items():
        comparisons[name] = paired_csv_summary(
            reference,
            read_object_csv(path),
            metrics=args.metric,
            object_ids=ids,
            higher_is_better={metric: metric not in args.lower_is_better for metric in args.metric},
            seed=args.seed,
            n_resamples=args.resamples,
        )
    payload = {
        "split": args.split,
        "object_ids": list(ids),
        "reference": str(args.reference),
        "comparisons": comparisons,
        "bootstrap": {"seed": args.seed, "resamples": args.resamples, "confidence": 0.95},
    }
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
