#!/usr/bin/env python3
"""Phase III formal campaign driver (validation-v3).

Runs the formal condition campaigns on the FROZEN fresh cohort, two GPU
shards in parallel, resume-safe via rows_shardN.json ledgers.

Campaigns (condition groups; no overlaps — each condition generated once):
  A2  16  raw layer x window map (native cap semantics; a_baseline + 15)
  A3  16  dose-normalized map (uncapped path per frozen a3_normalization.json)
  B1B2 6  layer_llh, lfm_exact, lll, hll, lhl, lhh
  B3   7  true_global x3 (uncapped diagnostics), native_gfl/gfh/gc3, no_adapter
  C    8  generic schedules endpoint- and budget-matched

Usage: run_campaigns.py --cohort <list.txt> --base-dir <runroot> --campaigns A2,B1B2 [--gpus 0,1]
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
SCRIPT = ROOT / "scripts/run_validation_v3_experiment.py"

CAMPAIGNS = {
    "A2": ["a_baseline"] + [f"a_{l}_W{w}" for l in ("deep", "middle", "shallow") for w in (1, 2, 3, 4, 5)],
    "A3": ["a3_baseline"] + [f"a3_{l}_W{w}" for l in ("deep", "middle", "shallow") for w in (1, 2, 3, 4, 5)],
    "B1B2": ["layer_llh", "lfm_exact", "layer_lll", "layer_hll", "layer_lhl", "layer_lhh"],
    "B3": ["true_global_1p25", "true_global_1p675", "true_global_2p50",
           "native_gfl", "native_gfh", "native_gc3", "no_adapter"],
    "C": ["gen_linear", "gen_linear_bm", "gen_cosine_bump", "gen_cosine_bump_bm",
          "gen_trapezoid", "gen_trapezoid_bm", "gen_gaussian_peak", "gen_gaussian_peak_bm"],
}


def n_done(run_dir: Path, shard: int, conditions: list) -> int:
    rows_path = run_dir / f"rows_shard{shard}.json"
    if not rows_path.exists():
        return 0
    import json

    rows = json.loads(rows_path.read_text())
    return sum(1 for r in rows if r["condition"] in conditions)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--base-dir", required=True)
    ap.add_argument("--campaigns", default="A2,A3,B1B2,B3,C")
    ap.add_argument("--gpus", default="0,1")
    ap.add_argument("--object-limit", type=int, default=0)
    args = ap.parse_args()

    gpus = [g.strip() for g in args.gpus.split(",") if g.strip()]
    cohort_path = Path(args.cohort).resolve()
    n_objects = sum(1 for l in cohort_path.open() if l.strip())

    for campaign in args.campaigns.split(","):
        campaign = campaign.strip()
        if campaign not in CAMPAIGNS:
            raise RuntimeError(f"unknown campaign {campaign}")
        conditions = CAMPAIGNS[campaign]
        run_dir = Path(args.base_dir) / f"campaign_{campaign}"
        run_dir.mkdir(parents=True, exist_ok=True)
        procs = []
        for shard, gpu in enumerate(gpus):
            env = dict(os.environ)
            env.update({
                "MVP_RUN_DIR": str(run_dir),
                "MVP_OBJECT_LIST": str(cohort_path),
                "MVP_DEVICE": f"cuda:{gpu}",
                "MVP_SHARD": str(shard),
                "MVP_NUM_SHARDS": str(len(gpus)),
                "MVP_CONDITIONS": ",".join(conditions),
                "MVP_SAVE_PREDICTED": "1",
                "MVP_SAVE_RESIDUAL": "1",
            })
            if args.object_limit > 0:
                env["MVP_OBJECT_LIMIT"] = str(args.object_limit)
            log = open(run_dir / f"shard{shard}.log", "a")
            procs.append((subprocess.Popen(
                [sys.executable, str(SCRIPT)], env=env, stdout=log, stderr=log), log, shard))
            time.sleep(5)  # stagger model loads
        print(f"[{campaign}] launched {len(procs)} shards -> {run_dir}", flush=True)
        fails = []
        for p, log, shard in procs:
            rc = p.wait()
            log.close()
            if rc != 0:
                fails.append(shard)
            done = n_done(run_dir, shard, conditions)
            expect = (n_objects + len(gpus) - 1 - shard) // len(gpus) * len(conditions) \
                if args.object_limit == 0 else None
            print(f"[{campaign}] shard{shard} rc={rc} done_rows={done}", flush=True)
        if fails:
            print(f"[{campaign}] FAILED shards: {fails}", flush=True)
            sys.exit(1)
        total = sum(n_done(run_dir, s, conditions) for s in range(len(gpus)))
        print(f"[{campaign}] COMPLETE rows={total}", flush=True)


if __name__ == "__main__":
    main()
