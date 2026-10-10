#!/usr/bin/env python3
"""Summarize the prelogged cap context of E5 without reading image metrics."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/e5_residual_dose"
RUN = DATA / "runs"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - pos) + ordered[high] * (pos - low)


def main() -> None:
    gate = json.loads((DATA / "E5_TECHNICAL_GATE.json").read_text())
    if gate["status"] != "PASS" or gate["quality_metrics_computed"] is not False:
        raise RuntimeError("E5 numerical gate has not passed, or quality metrics were computed")
    rows = []
    input_hashes = {}
    for shard in (0, 1):
        path = RUN / f"rows_shard{shard}.json"
        input_hashes[path.name] = sha256(path)
        rows.extend(json.loads(path.read_text()))
    strata: dict[tuple[str, float], list[dict]] = {}
    for row in rows:
        if row["condition"] in {"baseline", "alpha0_noop"}:
            continue
        for entry in row["traces"]:
            if entry.get("status") == "reference_pass_skipped_unchanged":
                continue
            strata.setdefault((entry["group"], float(entry["alpha"])), []).append(entry)
    summary = {}
    for (group, alpha), entries in sorted(strata.items()):
        equivalent = [float(e["baseline_plus_delta_equivalent_scale_l2"]) for e in entries]
        cap = [float(e["cap"]) for e in entries]
        if not all(math.isfinite(x) for x in equivalent + cap):
            raise RuntimeError(f"nonfinite cap context at {group}, alpha={alpha}")
        key = f"{group}/alpha={alpha:g}"
        summary[key] = {
            "active_wrapper_steps": len(entries),
            "cap_exceed_steps": sum(x > c for x, c in zip(equivalent, cap)),
            "cap_exceed_fraction": sum(x > c for x, c in zip(equivalent, cap)) / len(entries),
            "median_baseline_plus_delta_equivalent_scale_l2": statistics.median(equivalent),
            "p95_baseline_plus_delta_equivalent_scale_l2": quantile(equivalent, 0.95),
            "maximum_baseline_plus_delta_equivalent_scale_l2": max(equivalent),
            "native_cap": cap[0],
        }
    output = {
        "status": "DESCRIPTIVE_CAP_CONTEXT_ONLY",
        "e5_lock_sha256": sha256(DATA / "E5_LOCK.json"),
        "technical_gate_sha256": sha256(DATA / "E5_TECHNICAL_GATE.json"),
        "raw_ledger_sha256": input_hashes,
        "summary_script_sha256": sha256(Path(__file__).resolve()),
        "quality_metrics_read": False,
        "strata": summary,
        "interpretation": "The equivalent scale is an L2 norm ratio after dtype rounding, not an exact scalar multiplier; this diagnostic may exceed the native cap and is not a deployed schedule result.",
    }
    out_path = DATA / "E5_CAP_CONTEXT_SUMMARY.json"
    out_path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
