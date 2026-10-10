#!/usr/bin/env python3
"""CPU-only preflight for the frozen 50-step GeoTex applied-budget profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

STEPS = 50
LOW = 1.25
HIGH = 2.50
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
GROUPS = tuple(CAPS)
WINDOWS = {
    "early_high_16": (0, 15),
    "middle_high_16": (17, 32),
    "late_high_16": (34, 49),
}


def requested_at(profile: str, step: int) -> dict[str, float]:
    if not 0 <= step < STEPS:
        raise ValueError(f"step must be in [0, {STEPS - 1}], got {step}")
    if profile == "fixed_low":
        value = LOW
    elif profile == "fixed_high":
        value = HIGH
    elif profile == "fixed_applied_mean":
        value = 1.65
    elif profile == "native_gc3":
        value = HIGH if 17 <= step <= 32 else LOW
    elif profile in WINDOWS:
        lo, hi = WINDOWS[profile]
        value = HIGH if lo <= step <= hi else LOW
    else:
        raise KeyError(f"unknown profile: {profile}")
    return {group: value for group in GROUPS}


def effective(requested: dict[str, float]) -> dict[str, float]:
    return {group: min(requested[group], CAPS[group]) for group in GROUPS}


def build_report() -> dict:
    names = (
        "fixed_low",
        "fixed_high",
        "fixed_applied_mean",
        "native_gc3",
        *WINDOWS,
    )
    profiles = {}
    for name in names:
        requested_trace = [requested_at(name, i) for i in range(STEPS)]
        applied_trace = [effective(row) for row in requested_trace]
        high_steps = [i for i, row in enumerate(requested_trace) if row["deep"] == HIGH]
        sums = {
            group: sum(row[group] for row in applied_trace)
            for group in GROUPS
        }
        profiles[name] = {
            "high_step_indices": high_steps,
            "requested_values_by_group": {
                group: sorted({row[group] for row in requested_trace})
                for group in GROUPS
            },
            "applied_values_by_group": {
                group: sorted({row[group] for row in applied_trace})
                for group in GROUPS
            },
            "applied_scale_sum_by_group": sums,
            "applied_scale_mean_by_group": {
                group: sums[group] / STEPS for group in GROUPS
            },
        }

    placement = [profiles[name]["applied_scale_sum_by_group"] for name in WINDOWS]
    for group in GROUPS:
        if not all(row[group] == placement[0][group] for row in placement[1:]):
            raise RuntimeError(f"applied sums differ across placement profiles for {group}")
    if profiles["native_gc3"]["high_step_indices"] != list(range(17, 33)):
        raise RuntimeError("the frozen C3 stage partition is not steps 17–32")
    if profiles["fixed_applied_mean"]["applied_scale_sum_by_group"] != {
        "deep": 82.5, "middle": 82.5, "shallow": 40.0
    }:
        raise RuntimeError("fixed applied-mean profile does not match frozen applied sums")
    for name in WINDOWS:
        if profiles[name]["applied_scale_sum_by_group"] != {
            "deep": 82.5, "middle": 82.5, "shallow": 40.0
        }:
            raise RuntimeError(f"{name} does not match the frozen applied sums")

    return {
        "status": "CPU_PREFLIGHT_PASSED",
        "evidence_grade": "RETROSPECTIVE",
        "steps": STEPS,
        "caps": CAPS,
        "low": LOW,
        "high": HIGH,
        "placement_windows_inclusive": WINDOWS,
        "boundary_steps_low_in_all_placement_profiles": [16, 33],
        "profiles": profiles,
        "interpretation_limit": (
            "Equal applied scale sums do not imply equal realized residual norms or doses."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
