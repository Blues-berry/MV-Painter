#!/usr/bin/env python3
"""Phase III analysis pipeline (pre-registered statistics).

Implements PRIMARY_HYPOTHESES.md:
  * paired object-level bootstrap, 10,000 resamples, seed 20261002
  * mean + median paired deltas, 95% percentile CIs, win rate
  * Holm correction within predeclared families
  * Layer x Window two-factor interaction via object-cluster bootstrap

Subcommands:
  pairwise  — one paired comparison (A vs B) on a run CSV
  family    — Holm-correct a set of pairwise results (JSON in/out)
  layermap  — A2/A3 cell map + interaction test + Holm family
  spearman  — H5 texture-complexity relationship (E)

Sign convention: delta = a - b (raw metric difference, per metric direction
as stored; lower-better metrics keep their natural sign in deltas).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

BOOT_SEED = 20261002
BOOT_N = 10_000


def read_rows(path: Path) -> dict:
    """Return {object_key: row} keyed by object_uid (fallback: object)."""
    rows = list(csv.DictReader(path.open()))
    return {(r["object_uid"] if "object_uid" in r else r["object"]): r for r in rows}


def load_condition(run_dir: Path, condition: str) -> dict:
    """Rows for one condition: per-condition CSV if present, else the
    rows_shard*.json ledgers (always current; CSVs may lag by <=15 rows
    due to throttled writes)."""
    run_dir = Path(run_dir)
    csv_path = run_dir / f"{condition}_per_object_metrics.csv"
    if csv_path.exists():
        return read_rows(csv_path)
    merged = {}
    for shard in sorted(run_dir.glob("rows_shard*.json")):
        for r in json.loads(shard.read_text()):
            if r["condition"] == condition:
                merged[r.get("object_uid", r.get("object"))] = r
    if not merged:
        # cross-campaign fallback: search sibling campaign dirs (e.g., LLH
        # rows live in campaign_B1B2 while native_gfl lives in campaign_B3)
        for sib in sorted(run_dir.parent.glob("campaign_*")):
            if sib == run_dir:
                continue
            for shard in sorted(sib.glob("rows_shard*.json")):
                for r in json.loads(shard.read_text()):
                    if r["condition"] == condition:
                        merged.setdefault(r["object_uid"], r)
    if not merged:
        raise FileNotFoundError(f"no rows for condition {condition} in {run_dir}")
    return merged


def paired_bootstrap(deltas: np.ndarray):
    """Percentile bootstrap CI for the mean of paired deltas + sign-flip p."""
    rng = np.random.default_rng(BOOT_SEED)
    n = len(deltas)
    idx = rng.integers(0, n, size=(BOOT_N, n))
    boots = deltas[idx].mean(axis=1)
    mean = float(deltas.mean())
    median = float(np.median(deltas))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    # two-sided bootstrap p (proportion of resamples crossing zero, doubled)
    p = 2.0 * min((boots <= 0).mean(), (boots >= 0).mean())
    return {
        "n": n,
        "mean_delta": mean,
        "median_delta": median,
        "ci95": [float(lo), float(hi)],
        "win_rate": float((deltas > 0).mean()),
        "loss_rate": float((deltas < 0).mean()),
        "p_bootstrap": float(max(p, 1.0 / BOOT_N)),
    }


def get_metric(row: dict, key: str) -> float:
    v = row.get(key)
    if v is None or v == "":
        raise KeyError(f"metric {key} missing in row")
    return float(v)


def cmd_pairwise(args) -> None:
    ra = load_condition(Path(args.run_dir), args.a)
    rb = load_condition(Path(args.run_dir), args.b)
    common = sorted(set(ra) & set(rb))
    missing = (set(ra) ^ set(rb))
    out = {
        "run_dir": str(args.run_dir),
        "a": args.a,
        "b": args.b,
        "n_common": len(common),
        "n_disjoint": len(missing),
        "tests": {},
    }
    for metric in args.metrics.split(","):
        d = np.array([get_metric(ra[o], metric) - get_metric(rb[o], metric) for o in common])
        out["tests"][metric] = paired_bootstrap(d)
    print(json.dumps(out, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2) + "\n")


def holm(pvals: dict) -> dict:
    """Holm-Bonferroni: returns {name: adjusted_p}."""
    order = sorted(pvals, key=lambda k: pvals[k])
    m = len(order)
    adj, running = {}, 0.0
    for i, name in enumerate(order):
        running = max(running, (m - i) * pvals[name])
        adj[name] = min(1.0, running)
    return adj


def cmd_family(args) -> None:
    data = json.loads(Path(args.input).read_text())
    tests = {}
    for entry in data["tests"]:
        tests[entry["name"]] = entry["p_bootstrap"]
    adj = holm(tests)
    for entry in data["tests"]:
        entry["p_holm"] = adj[entry["name"]]
    data["holm_family"] = {"size": len(tests), "alpha": 0.05}
    data["reject_h0_holm"] = {k: bool(adj[k] < 0.05) for k in adj}
    print(json.dumps(data, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(data, indent=2) + "\n")


# ---------------------------------------------------------------- layermap
LAYERS = ("deep", "middle", "shallow")
WINDOWS = (1, 2, 3, 4, 5)


def cmd_layermap(args) -> None:
    prefix = args.prefix  # "a" (raw) or "a3"
    base_cond = f"{prefix}_baseline"
    rb = load_condition(Path(args.run_dir), base_cond)
    cells = {}
    for layer in LAYERS:
        for w in WINDOWS:
            cond = f"{prefix}_{layer}_W{w}"
            ra = load_condition(Path(args.run_dir), cond)
            common = sorted(set(ra) & set(rb))
            cells[(layer, w)] = {
                "condition": cond,
                "n": len(common),
                "deltas": {
                    m: np.array([get_metric(ra[o], m) - get_metric(rb[o], m) for o in common])
                    for m in args.metrics.split(",")
                },
            }

    primary = args.primary_metric
    result = {
        "run_dir": str(args.run_dir),
        "baseline": base_cond,
        "primary_metric": primary,
        "dose": args.dose,
        "cells": {},
        "marginals": {},
    }
    # per-cell stats on the primary metric
    pvals = {}
    for (layer, w), c in cells.items():
        st = paired_bootstrap(c["deltas"][primary])
        result["cells"][f"{layer}_W{w}"] = st
        pvals[f"{layer}_W{w}"] = st["p_bootstrap"]

    # two-factor interaction: object-cluster bootstrap on the additive model
    # response y_{o,l,w} = cell delta for object o; interaction statistic
    # T = sum over cells of (y - row_mean - col_mean + grand_mean)^2 (SS interaction)
    y = {}
    cell_objects = {}
    for layer in LAYERS:
        for w in WINDOWS:
            cond = f"{prefix}_{layer}_W{w}"
            ra = load_condition(Path(args.run_dir), cond)
            common = sorted(set(ra) & set(rb))
            cell_objects[(layer, w)] = common
            for o in common:
                y[(o, layer, w)] = get_metric(ra[o], primary) - get_metric(rb[o], primary)

    obs_objects = sorted(set(rb))
    cell_index = {(l, w): i for i, (l, w) in enumerate(
        [(l, w) for l in LAYERS for w in WINDOWS])}

    def ss_interaction(sample_objects):
        """SS of interaction on the object-level cell means, given a resample
        of objects (weights = multiplicity)."""
        # weighted cell means
        cm = np.zeros((3, 5))
        wsum = np.zeros((3, 5))
        for (l, w), i in cell_index.items():
            objs = cell_objects[(l, w)]
            vals = np.array([y[(o, l, w)] for o in objs])
            wts = np.array([sample_objects.get(o, 0) for o in objs], dtype=float)
            if wts.sum() == 0:
                return np.nan
            cm[i // 5, i % 5] = (vals * wts).sum() / wts.sum()
            wsum[i // 5, i % 5] = wts.sum()
        grand = (cm * wsum).sum() / wsum.sum()
        row_m = (cm * wsum).sum(axis=1) / wsum.sum(axis=1)
        col_m = (cm * wsum).sum(axis=0) / wsum.sum(axis=0)
        resid = cm - row_m[:, None] - col_m[None, :] + grand
        return float((resid ** 2 * wsum).sum())

    base_weights = {o: 1 for o in obs_objects}
    t_obs = ss_interaction(base_weights)
    rng = np.random.default_rng(BOOT_SEED)
    boot_t = []
    for _ in range(BOOT_N):
        picks = rng.integers(0, len(obs_objects), size=len(obs_objects))
        weights = {}
        for p in picks:
            weights[obs_objects[p]] = weights.get(obs_objects[p], 0) + 1
        boot_t.append(ss_interaction(weights))
    boot_t = np.array(boot_t)
    p_int = float((boot_t >= t_obs).mean())
    result["interaction"] = {
        "statistic": "SS_interaction (two-way additive residual, object-weighted)",
        "observed": t_obs,
        "bootstrap_null_mean": float(boot_t.mean()),
        "p_cluster_bootstrap": max(p_int, 1.0 / BOOT_N),
        "n_bootstrap": BOOT_N,
        "seed": BOOT_SEED,
    }

    # Holm family: 15 cells + 1 interaction = 16
    fam = {**pvals, "interaction": p_int}
    adj = holm(fam)
    result["holm_family"] = {k: {"p_raw": fam[k], "p_holm": adj[k]} for k in fam}
    result["reject_h0_holm"] = {k: bool(adj[k] < 0.05) for k in adj}

    # marginals (descriptive)
    for axis, groups in (("layer", LAYERS), ("window", WINDOWS)):
        marg = {}
        for g in groups:
            keys = [k for k in cells if k[0 if axis == "layer" else 1] == g]
            marg[str(g)] = float(np.mean([cells[k]["deltas"][primary].mean() for k in keys]))
        result["marginals"][axis] = marg

    print(json.dumps(result, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n")


# ---------------------------------------------------------------- spearman
def cmd_spearman(args) -> None:
    ra = load_condition(Path(args.run_dir), args.a)
    rb = load_condition(Path(args.run_dir), args.b)
    common = sorted(set(ra) & set(rb))
    gt_stats = json.loads(Path(args.gt_stats).read_text())
    out = {"a": args.a, "b": args.b, "n": len(common), "tests": {}, "quartiles": {}}
    family_p = {}
    for metric in args.metrics.split(","):
        d = np.array([get_metric(ra[o], metric) - get_metric(rb[o], metric) for o in common])
        entry = {"metric": metric}
        for stat_name, values in gt_stats.items():
            v = np.array([values[o] for o in common], dtype=float)
            rho = _spearman(d, v)
            rng = np.random.default_rng(BOOT_SEED)
            n = len(d)
            boots = []
            for _ in range(BOOT_N):
                idx = rng.integers(0, n, n)
                boots.append(_spearman(d[idx], v[idx]))
            lo, hi = np.percentile(boots, [2.5, 97.5])
            n_lower = int((np.array(boots) <= 0).sum())
            n_upper = int((np.array(boots) >= 0).sum())
            p_raw = float(2 * min(n_lower, n_upper) / BOOT_N)
            # Plus-one Monte Carlo correction prevents a finite bootstrap
            # from reporting p=0 when no resample crosses zero.
            p_mc = float(min(1.0, 2 * min((n_lower + 1) / (BOOT_N + 1),
                                         (n_upper + 1) / (BOOT_N + 1))))
            family_key = f"{metric}__{stat_name}"
            family_p[family_key] = p_mc
            entry[stat_name] = {"rho": rho, "ci95": [float(lo), float(hi)],
                                "bootstrap_extreme_count_p_raw": p_raw,
                                "p_bootstrap_plus_one": p_mc}
        out["tests"][metric] = entry
        # quartile table for the primary GT statistic
        prim = args.gt_primary
        v = np.array([gt_stats[prim][o] for o in common], dtype=float)
        qs = np.quantile(v, [0.25, 0.5, 0.75])
        labels = np.digitize(v, qs)
        qtab = {}
        for q in range(4):
            mask = labels == q
            qtab[f"Q{q + 1}"] = {
                "n": int(mask.sum()),
                "mean_delta": float(d[mask].mean()),
                "positive_delta_rate": float((d[mask] > 0).mean()),
                "favorable_object_rate": float((d[mask] < 0).mean() if metric == "fg_lpips"
                                                else (d[mask] > 0).mean()),
            }
        out["quartiles"][metric] = qtab
    adjusted = holm(family_p)
    out["holm_family"] = {
        "name": "E: two metrics x five GT-only statistics",
        "size": len(family_p),
        "alpha": 0.05,
        "p_value_method": "paired object bootstrap of Spearman rho; two-sided plus-one Monte Carlo correction",
        "tests": {k: {"p_raw": family_p[k], "p_holm": adjusted[k],
                       "reject_h0": bool(adjusted[k] < 0.05)} for k in family_p},
    }
    print(json.dumps(out, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2) + "\n")


def _spearman(x, y) -> float:
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx = (rx - rx.mean()) / (rx.std() + 1e-12)
    ry = (ry - ry.mean()) / (ry.std() + 1e-12)
    return float((rx * ry).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pairwise")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--metrics", default="fg_psnr,fg_lpips")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_pairwise)

    p = sub.add_parser("family")
    p.add_argument("--input", required=True)
    p.add_argument("--out")
    p.set_defaults(fn=cmd_family)

    p = sub.add_parser("layermap")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--prefix", default="a", choices=["a", "a3", "g"])
    p.add_argument("--dose", default="raw")
    p.add_argument("--primary-metric", default="fg_lpips")
    p.add_argument("--metrics", default="fg_lpips,fg_psnr,edge_ssim")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_layermap)

    p = sub.add_parser("spearman")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--metrics", default="fg_psnr,fg_lpips")
    p.add_argument("--gt-stats", required=True)
    p.add_argument("--gt-primary", default="gt_fg_lap_var")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_spearman)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
