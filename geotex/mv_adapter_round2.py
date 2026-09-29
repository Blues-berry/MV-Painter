"""Protocol guard for the official MV-Adapter SD2.1 cross-backbone study.

The actual model checkout remains external and is never vendored here.  This
tool writes the fixed object split and the eight three-stage binary schedules
that the external runner must consume.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .round2_stats import MV_ADAPTER_HOLDOUT_IDS, PROBE_IDS, validate_split, write_json
except ImportError:  # direct script execution
    from round2_stats import MV_ADAPTER_HOLDOUT_IDS, PROBE_IDS, validate_split, write_json


SCHEDULES = {
    "LLL": ("low", "low", "low"),
    "LLH": ("low", "low", "high"),
    "LHL": ("low", "high", "low"),
    "LHH": ("low", "high", "high"),
    "HLL": ("high", "low", "low"),
    "HLH": ("high", "low", "high"),
    "HHL": ("high", "high", "low"),
    "HHH": ("high", "high", "high"),
}


def manifest() -> dict:
    validate_split(PROBE_IDS, split="probe")
    validate_split(MV_ADAPTER_HOLDOUT_IDS, split="mv_adapter_holdout")
    return {
        "backbone": "official MV-Adapter SD2.1 image+geometry pipeline",
        "probe_objects": list(PROBE_IDS),
        "holdout_objects": list(MV_ADAPTER_HOLDOUT_IDS),
        "schedules": {name: list(stages) for name, stages in SCHEDULES.items()},
        "comparisons": ["no_geometry", "fixed_scale", "linear_warmup", "cosine_bump", "low_high_low"],
        "absolute_score_comparison_across_backbones": False,
        "required_shared_factors": ["object", "seed", "initial_latent", "camera", "resolution", "metric_code"],
        "official_sources": {
            "paper": "https://openaccess.thecvf.com/content/ICCV2025/papers/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.pdf",
            "implementation": "https://github.com/huanngzh/MV-Adapter",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = manifest()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
