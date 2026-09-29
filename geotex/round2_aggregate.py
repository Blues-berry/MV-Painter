"""Rebuild object-level Round 2 results from raw per-view CSV rows."""

from __future__ import annotations

import argparse

try:
    from .round2_stats import (
        MAIN_HOLDOUT_IDS,
        MAIN_POOLED_IDS,
        MV_ADAPTER_CALIBRATION_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        MV_ADAPTER_TOTAL_IDS,
        PROBE_IDS,
        aggregate_view_csv,
    )
except ImportError:  # direct script execution
    from round2_stats import (
        MAIN_HOLDOUT_IDS,
        MAIN_POOLED_IDS,
        MV_ADAPTER_CALIBRATION_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        MV_ADAPTER_TOTAL_IDS,
        PROBE_IDS,
        aggregate_view_csv,
    )


SPLITS = {
    "probe": PROBE_IDS,
    "main_holdout": MAIN_HOLDOUT_IDS,
    "main_pooled": MAIN_POOLED_IDS,
    "mv_adapter_calibration": MV_ADAPTER_CALIBRATION_IDS,
    "mv_adapter_holdout": MV_ADAPTER_HOLDOUT_IDS,
    "mv_adapter_total": MV_ADAPTER_TOTAL_IDS,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="raw per-view CSV")
    parser.add_argument("--output", required=True, help="per-object CSV")
    parser.add_argument("--split", choices=tuple(SPLITS), required=True)
    parser.add_argument("--metric", action="append", required=True)
    args = parser.parse_args()
    aggregate_view_csv(
        args.input,
        args.output,
        object_ids=SPLITS[args.split],
        metrics=args.metric,
    )


if __name__ == "__main__":
    main()
