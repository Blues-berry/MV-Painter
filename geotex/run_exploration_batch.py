"""Batch runner for exploration experiments A/B/C.

Runs all 17 variants sequentially on the 24-object probe set.

Usage:
    python geotex/run_exploration_batch.py --device cuda:0
"""
import subprocess, os, sys, json, time
from datetime import datetime

BASE_DIR = "mvpoutput/geotex_refattn_v1/exploration_v1/inference_matrix"
CONFIG = "mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT = "mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
PROBE_SET = "mvpoutput/geotex_refattn_v1/exploration_v1/probe_set.json"

# ============================================================
# Experiment A: Global scale baseline
# ============================================================
EXPERIMENT_A = [
    {"name": "A_s1p25", "type": "global", "scale": 1.25},
    {"name": "A_s1p75", "type": "global", "scale": 1.75},
    {"name": "A_s2p00", "type": "global", "scale": 2.00},
    {"name": "A_s2p25", "type": "global", "scale": 2.25},
    {"name": "A_s2p50", "type": "global", "scale": 2.50},
]

# ============================================================
# Experiment B: Layer-wise scale
# shallow=up_2, middle=up_1, deep=up_0+mid
# ============================================================
EXPERIMENT_B = [
    {"name": "B1", "type": "layer_wise",
     "layer_scales": {"shallow": 2.5, "middle": 1.25, "deep": 1.25}},
    {"name": "B2", "type": "layer_wise",
     "layer_scales": {"shallow": 1.25, "middle": 2.5, "deep": 1.25}},
    {"name": "B3", "type": "layer_wise",
     "layer_scales": {"shallow": 1.25, "middle": 1.25, "deep": 2.5}},
    {"name": "B4", "type": "layer_wise",
     "layer_scales": {"shallow": 2.25, "middle": 2.25, "deep": 1.25}},
    {"name": "B5", "type": "layer_wise",
     "layer_scales": {"shallow": 1.25, "middle": 2.25, "deep": 2.25}},
    {"name": "B6", "type": "layer_wise",
     "layer_scales": {"shallow": 2.25, "middle": 1.25, "deep": 2.25}},
]

# ============================================================
# Experiment C: Timestep-wise scale
# early=timestep 0-33%, mid=33-66%, late=66-100%
# ============================================================
EXPERIMENT_C = [
    {"name": "C1", "type": "timestep_wise",
     "timestep_schedule": {"early": 2.5, "mid": 1.75, "late": 1.25}},
    {"name": "C2", "type": "timestep_wise",
     "timestep_schedule": {"early": 1.25, "mid": 1.75, "late": 2.5}},
    {"name": "C3", "type": "timestep_wise",
     "timestep_schedule": {"early": 1.25, "mid": 2.5, "late": 1.25}},
    {"name": "C4", "type": "timestep_wise",
     "timestep_schedule": {"early": 1.25, "mid": 1.25, "late": 2.5}},
    {"name": "C5", "type": "timestep_wise",
     "timestep_schedule": {"early": 2.5, "mid": 1.25, "late": 1.25}},
    {"name": "C6", "type": "timestep_wise",
     "timestep_schedule": {"early": 2.25, "mid": 2.25, "late": 2.25}},
]

ALL_EXPERIMENTS = EXPERIMENT_A + EXPERIMENT_B + EXPERIMENT_C


def run_variant(variant, device):
    """Run a single variant."""
    name = variant["name"]
    out_dir = os.path.join(BASE_DIR, name)

    # Skip if already done
    if os.path.exists(os.path.join(out_dir, "summary_metrics.json")):
        print(f"  SKIP {name} (already done)")
        return True

    cmd = [
        sys.executable, "geotex/eval_exploration.py",
        "--config", CONFIG,
        "--checkpoint", CHECKPOINT,
        "--num_objects", "24",
        "--probe_set", PROBE_SET,
        "--output_dir", out_dir,
        "--device", device,
        "--variant_name", name,
        "--steps", "50",
        "--seed", "42",
    ]

    if variant["type"] == "global":
        cmd.extend(["--scale", str(variant["scale"])])
    elif variant["type"] == "layer_wise":
        cmd.extend(["--layer_scales", json.dumps(variant["layer_scales"])])
    elif variant["type"] == "timestep_wise":
        cmd.extend(["--timestep_schedule", json.dumps(variant["timestep_schedule"])])

    print(f"\n{'='*60}")
    print(f"Running {name} ({variant['type']})")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT {name} after 3600s")
        return False
    except Exception as e:
        print(f"  ERROR {name}: {e}")
        return False
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"  FAIL {name}")
        print(f"  stderr: {result.stderr[-500:]}")
        if result.stdout:
            print(f"  stdout: {result.stdout[-300:]}")
        return False

    print(f"  DONE {name} in {elapsed:.0f}s")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--only", type=str, default=None,
                        help="Run only this variant name (e.g. B1)")
    args = parser.parse_args()

    os.makedirs(BASE_DIR, exist_ok=True)

    experiments = ALL_EXPERIMENTS
    if args.only:
        experiments = [e for e in ALL_EXPERIMENTS if e["name"] == args.only]
        if not experiments:
            print(f"Unknown variant: {args.only}")
            print(f"Available: {[e['name'] for e in ALL_EXPERIMENTS]}")
            return

    print(f"Starting exploration batch: {len(experiments)} variants")
    print(f"Device: {args.device}")
    print(f"Start: {datetime.now().isoformat()}")

    results = {}
    for i, variant in enumerate(experiments):
        print(f"\n[{i+1}/{len(experiments)}] {variant['name']}")
        ok = run_variant(variant, args.device)
        results[variant["name"]] = "PASS" if ok else "FAIL"

    # Summary
    print(f"\n{'='*60}")
    print("BATCH SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v == "PASS")
    failed = sum(1 for v in results.values() if v == "FAIL")
    print(f"Passed: {passed}, Failed: {failed}")
    for name, status in results.items():
        marker = "✓" if status == "PASS" else "✗"
        print(f"  {marker} {name}")

    # Save summary
    with open(os.path.join(BASE_DIR, "batch_status.json"), "w") as f:
        json.dump({"results": results, "timestamp": datetime.now().isoformat(),
                    "device": args.device}, f, indent=2)


if __name__ == "__main__":
    main()
