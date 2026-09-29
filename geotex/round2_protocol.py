"""Validate and record the fixed data protocol used by the second revision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .round2_stats import (
        BOOTSTRAP_SEED,
        LEGACY_TARGET_VIEWS,
        MAIN_HOLDOUT_IDS,
        MAIN_POOLED_IDS,
        MV_ADAPTER_CALIBRATION_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        MV_ADAPTER_TOTAL_IDS,
        PROBE_IDS,
        UNIQUE_TARGET_VIEWS,
        validate_view_ids,
        validate_fixed_partitions,
        write_json,
    )
except ImportError:  # direct ``python geotex/round2_protocol.py`` execution
    from round2_stats import (
        BOOTSTRAP_SEED,
        LEGACY_TARGET_VIEWS,
        MAIN_HOLDOUT_IDS,
        MAIN_POOLED_IDS,
        MV_ADAPTER_CALIBRATION_IDS,
        MV_ADAPTER_HOLDOUT_IDS,
        MV_ADAPTER_TOTAL_IDS,
        PROBE_IDS,
        UNIQUE_TARGET_VIEWS,
        validate_view_ids,
        validate_fixed_partitions,
        write_json,
    )


def protocol_manifest(*, resolution: int = 256, target_views=UNIQUE_TARGET_VIEWS) -> dict:
    views = validate_view_ids(target_views)
    validate_fixed_partitions()
    return {
        "protocol_version": "round2-unique6-v1",
        "resolution_px": [resolution, resolution],
        "target_views": list(views),
        "legacy_target_views_audit_only": list(LEGACY_TARGET_VIEWS),
        "splits": {
            "probe": list(PROBE_IDS),
            "main_holdout": list(MAIN_HOLDOUT_IDS),
            "main_pooled": list(MAIN_POOLED_IDS),
            "mv_adapter_calibration": list(MV_ADAPTER_CALIBRATION_IDS),
            "mv_adapter_holdout": list(MV_ADAPTER_HOLDOUT_IDS),
            "mv_adapter_total": list(MV_ADAPTER_TOTAL_IDS),
        },
        "bootstrap": {"resamples": 10000, "seed": BOOTSTRAP_SEED, "confidence": 0.95},
        "notes": [
            "No duplicate camera ID may be counted as a separate generated view.",
            "Absolute scores are compared only within a backbone; cross-backbone claims use paired deltas.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=int, default=256)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = protocol_manifest(resolution=args.resolution)
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
