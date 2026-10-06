#!/usr/bin/env python3
"""A1 instrumentation-sanity verification for the Phase III preflight run.

Checks (protocol Experiment A1):
 1. cell isolation: vs a_baseline, ONLY the requested (layer, window) cells
    of requested scale change; every other step/group cell is identical
 2. shared-input integrity: cond/target/normal/depth/global_embeds/init_latent
    tensor hashes identical across all 16 conditions per object
 3. residual logging non-empty (50 steps, entries present)
 4. no unintended cap activation: eff_scale == requested scale everywhere
 5. generated outputs differ from baseline (prediction PNG hash differs)

Exit code 0 iff all checks pass. No scientific conclusion uses preflight data.
"""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

RUN_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else
               "/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/preflight_a1")

LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)
BASE_COND = "a_baseline"


def png_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_trace(cond: str, obj: str):
    """Return {step: {group: requested_scale}} from residual logs."""
    with (RUN_DIR / "residual_logs" / cond / f"{obj}.json").open() as f:
        log = json.load(f)
    trace = {}
    for step_key, entries in log.items():
        step = int(step_key)
        cells = {}
        for e in entries.values():
            cells.setdefault(e["depth"], set()).add(round(float(e["scale"]), 6))
        trace[step] = {g: vals.pop() if len(vals) == 1 else vals for g, vals in cells.items()}
    return trace


def main() -> int:
    rows = json.loads((RUN_DIR / "rows_shard0.json").read_text())
    objects = sorted({r["object"] for r in rows}, key=lambda o: [int(r["object_idx"]) for r in rows if r["object"] == o][0])
    conds = sorted({r["condition"] for r in rows})
    failures = []

    print(f"objects: {objects}")
    print(f"conditions ({len(conds)}): {conds}")

    expected = {f"a_{l}_W{w}" for l in LAYERS for w in WINDOWS} | {BASE_COND}
    if set(conds) != expected:
        failures.append(f"condition set mismatch: {set(conds) ^ expected}")

    # --- check 2: shared-input integrity per object
    for obj in objects:
        obj_rows = [r for r in rows if r["object"] == obj]
        ref = obj_rows[0]["input_hashes"]
        for r in obj_rows[1:]:
            if r["input_hashes"] != ref:
                failures.append(f"integrity mismatch: {obj} {r['condition']}")

    # --- check 1: cell isolation + check 3/4 via logs
    for obj in objects:
        base_trace = load_trace(BASE_COND, obj)
        if len(base_trace) != 50:
            failures.append(f"{BASE_COND} {obj}: {len(base_trace)} steps logged (want 50)")
        for cond in conds:
            if cond == BASE_COND:
                continue
            layer = cond[2:].rsplit("_W", 1)[0]
            w = int(cond.rsplit("_W", 1)[1])
            lo, hi = 10 * (w - 1), 10 * w - 1
            trace = load_trace(cond, obj)
            if len(trace) != 50:
                failures.append(f"{cond} {obj}: {len(trace)} steps logged (want 50)")
            for step in range(50):
                b, t = base_trace[step], trace[step]
                in_window = lo <= step <= hi
                for g in LAYERS:
                    if g == layer and in_window:
                        if t[g] == b[g]:
                            failures.append(f"{cond} {obj} step {step} {g}: cell NOT changed")
                    else:
                        if t[g] != b[g]:
                            failures.append(
                                f"{cond} {obj} step {step} {g}: UNINTENDED change "
                                f"{b[g]} -> {t[g]}")

    # --- check 4: no cap activation anywhere (eff == requested)
    cap_hits = 0
    for cond in conds:
        for obj in objects:
            with (RUN_DIR / "residual_logs" / cond / f"{obj}.json").open() as f:
                log = json.load(f)
            for step_key, entries in log.items():
                for e in entries.values():
                    if abs(float(e["eff_scale"]) - float(e["scale"])) > 1e-9:
                        cap_hits += 1
    if cap_hits:
        failures.append(f"cap activation events: {cap_hits}")

    # --- check 5: outputs differ from baseline
    for obj in objects:
        base_png = png_hash(RUN_DIR / "predictions" / BASE_COND / f"{obj}.png")
        for cond in conds:
            if cond == BASE_COND:
                continue
            if png_hash(RUN_DIR / "predictions" / cond / f"{obj}.png") == base_png:
                failures.append(f"{cond} {obj}: prediction identical to baseline")

    # --- elapsed sanity
    el = [float(r["elapsed_seconds"]) for r in rows]
    print(f"rows: {len(rows)}, median elapsed: {sorted(el)[len(el)//2]:.1f}s")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for f_ in failures[:40]:
            print(" -", f_)
        return 1
    print("\nALL A1 INSTRUMENTATION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
