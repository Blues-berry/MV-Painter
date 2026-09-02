#!/usr/bin/env python3
"""Two-level cluster bootstrap for the 3AFC preference study (R1.3 / R3-C3).

The study collects 24 participants x 30 objects x 3 criteria = 720 first-choice
votes per criterion. Votes within a participant and within an object are not
independent, so n=720 must not be treated as independent Bernoulli trials.
This script resamples participants (24) and objects (30) with replacement,
B=10000 times, and reports percentile 95% CIs for:
  - per-criterion first-choice shares of each method,
  - share differences between methods (paired within the same resample),
so results can be compared against the 1/3 chance level.

Real-data mode (once raw votes are exported from the survey backend):
    python cluster_bootstrap_preference.py --votes votes.csv
    votes.csv header: participant,object,criterion,choice
    choice   in {s1.25, s2.50, C3}
    criterion in {texture, shape, overall}
    participant/object ids are 1-based or 0-based (auto-detected).

Simulation mode (preview expected CI widths before raw votes are exported):
generates synthetic datasets whose marginals match Table 9 (tab:preference)
under participant/object ICC in {0.05, 0.10, 0.15}, then bootstraps each:
    python cluster_bootstrap_preference.py
"""

import argparse
import csv
import sys

import numpy as np

METHODS = ["s1.25", "s2.50", "C3"]
CRITERIA = ["texture", "shape", "overall"]
P, O = 24, 30
B = 10000

# First-choice counts from tab:preference in final_submit.tex (out of 720 each).
TARGET = {
    "texture": [332, 104, 284],
    "shape": [96, 331, 293],
    "overall": [176, 126, 418],
}
SHARES = [np.array(TARGET[crit], float) / (P * O) for crit in CRITERIA]


def load_votes(path):
    """Load per-vote records into Y[c, m, p, o] indicator arrays."""
    Y = np.zeros((len(CRITERIA), len(METHODS), P, O))
    seen = set()
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            c = CRITERIA.index(row["criterion"].strip().lower())
            m = METHODS.index(row["choice"].strip())
            pid, oid = int(row["participant"]), int(row["object"])
            seen.add((c, pid, oid))
            Y[c, m, pid, oid] += 1.0
    # normalize 1-based ids to 0-based if needed
    if max(pid for _, pid, _ in seen) == P or max(oid for _, _, oid in seen) == O:
        raise SystemExit("ids look 1-based; re-run with participant-1/object-1 columns")
    for c in range(len(CRITERIA)):
        if len({(pid, oid) for cc, pid, oid in seen if cc == c}) != P * O:
            raise SystemExit(f"criterion '{CRITERIA[c]}' does not have exactly one vote per (participant, object)")
        if not np.allclose(Y[c].sum(0), 1.0):
            raise SystemExit(f"criterion '{CRITERIA[c]}' has (p,o) cells with 0 or >1 choices")
    return Y


def cluster_bootstrap(Y, rng, B=B):
    """Resample participants and objects with replacement; return share draws."""
    C, M = Y.shape[0], Y.shape[1]
    pc = rng.multinomial(P, np.full(P, 1.0 / P), size=B)  # (B, P)
    oc = rng.multinomial(O, np.full(O, 1.0 / O), size=B)  # (B, O)
    shares = np.empty((C, M, B))
    for c in range(C):
        for m in range(M):
            rows = oc @ Y[c, m].T  # (B, P): object-resampled row sums
            shares[c, m] = (pc * rows).sum(1) / (P * O)
    return shares


def fmt_ci(x):
    return f"[{100 * x[0]:.1f}, {100 * x[1]:.1f}]"


def report(shares, label):
    lo, hi = np.percentile(shares, [2.5, 97.5], axis=-1)
    print(f"\n=== {label} ===")
    print(f"{'criterion':<10}{'method':<8}{'share':>7}   95% CI")
    for c, crit in enumerate(CRITERIA):
        for m, meth in enumerate(METHODS):
            pt = 100 * shares[c, m].mean()
            print(f"{crit:<10}{meth:<8}{pt:>6.1f}%   {fmt_ci((lo[c, m], hi[c, m]))}")
    print("--- key paired differences (same resample) ---")
    pairs = [("overall", "C3", "s1.25"), ("overall", "C3", "s2.50"),
             ("texture", "s1.25", "C3"), ("shape", "s2.50", "C3")]
    for crit, a, b in pairs:
        c, ma, mb = CRITERIA.index(crit), METHODS.index(a), METHODS.index(b)
        d = shares[c, ma] - shares[c, mb]
        pt = 100 * (TARGET[crit][ma] - TARGET[crit][mb]) / (P * O)
        lo, hi = np.percentile(d, [2.5, 97.5])
        sig = "sig" if (lo > 0 or hi < 0) else "n.s."
        print(f"{crit:<10}{a} - {b:<6}{pt:>+6.1f}pp  {fmt_ci((lo, hi))}  {sig}")


def _softmax(x):
    x = x - x.max(-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(-1, keepdims=True)


def calibrate_beta(p, sa, sg, rng, n=400_000, iters=4):
    """Baseline logits such that E[softmax(beta + participant/object effects)] = p."""
    beta = np.log(p)
    A = rng.normal(0.0, sa, size=(n, len(p)))
    G = rng.normal(0.0, sg, size=(n, len(p)))
    for _ in range(iters):
        s = _softmax(beta + A + G).mean(0)
        beta += np.log(p) - np.log(s)
    return beta


def simulate_world(rng, rho_p, rho_o, betas, tol=0.02):
    """One synthetic dataset with Table 9 marginals and given ICCs."""
    Y = np.zeros((len(CRITERIA), len(METHODS), P, O))
    for c in range(len(CRITERIA)):
        p = SHARES[c]                                  # (M,) target shares
        a = rng.normal(0.0, 1.0, size=(P, len(METHODS)))
        g = rng.normal(0.0, 1.0, size=(O, len(METHODS)))
        a *= np.sqrt(rho_p / (p * (1 - p)))            # logit-scale sd -> observed ICC ~ rho
        g *= np.sqrt(rho_o / (p * (1 - p)))
        U = betas[c] + a[:, None, :] + g[None, :, :] + rng.gumbel(size=(P, O, len(METHODS)))
        choice = U.argmax(-1)
        for m in range(len(METHODS)):
            Y[c, m] = choice == m
    ok = all(abs(Y[c, m].sum() - TARGET[crit][m]) <= tol * P * O
             for c, crit in enumerate(CRITERIA) for m in range(len(METHODS)))
    return Y, ok


DIFF_PAIRS = [("overall", "C3", "s1.25"), ("overall", "C3", "s2.50"),
              ("texture", "s1.25", "C3"), ("shape", "s2.50", "C3")]


def run_sim(n_worlds=80):
    rng = np.random.default_rng(20260902)
    for rho in (0.05, 0.10, 0.15):
        betas = [calibrate_beta(SHARES[c], np.sqrt(rho / (SHARES[c] * (1 - SHARES[c]))),
                                np.sqrt(rho / (SHARES[c] * (1 - SHARES[c]))), rng)
                 for c in range(len(CRITERIA))]
        bounds, diffs = [], []
        tries = 0
        while len(bounds) < n_worlds:
            tries += 1
            Y, ok = simulate_world(rng, rho, rho, betas, tol=0.02)
            if not ok:
                continue
            shares = cluster_bootstrap(Y, rng)
            q = np.percentile(shares, [2.5, 97.5], axis=-1)  # (2, C, M)
            bounds.append(np.moveaxis(q, 0, -1))             # (C, M, 2)
            for crit, a, b in DIFF_PAIRS:
                c, ma, mb = CRITERIA.index(crit), METHODS.index(a), METHODS.index(b)
                diffs.append(np.percentile(shares[c, ma] - shares[c, mb], [2.5, 97.5]))
        bounds = np.array(bounds)
        diffs = np.array(diffs).reshape(n_worlds, len(DIFF_PAIRS), 2)
        print(f"\n=== simulated ICC(P)=ICC(O)={rho:.2f}: accepted {n_worlds}/{tries} worlds, B={B} ===", flush=True)
        print(f"{'criterion':<10}{'method':<8}{'share':>7}   mean 95% CI        (world-to-world range of CI)")
        for c, crit in enumerate(CRITERIA):
            for m, meth in enumerate(METHODS):
                pt = 100 * TARGET[crit][m] / (P * O)
                lo_m, hi_m = bounds[:, c, m, 0].mean(), bounds[:, c, m, 1].mean()
                lo_r = (bounds[:, c, m, 0].min(), bounds[:, c, m, 1].max())
                print(f"{crit:<10}{meth:<8}{pt:>6.1f}%   {fmt_ci((lo_m, hi_m))}   {fmt_ci(lo_r)}")
        print("--- key paired differences (mean 95% CI; range over worlds) ---")
        for k, (crit, a, b) in enumerate(DIFF_PAIRS):
            pt = 100 * (TARGET[crit][METHODS.index(a)] - TARGET[crit][METHODS.index(b)]) / (P * O)
            lo_m, hi_m = diffs[:, k, 0].mean(), diffs[:, k, 1].mean()
            lo_r = (diffs[:, k, 0].min(), diffs[:, k, 1].max())
            sig = "sig" if lo_m > 0 else "n.s."
            print(f"{crit:<10}{a} - {b:<6}{pt:>+6.1f}pp  {fmt_ci((lo_m, hi_m))}  {fmt_ci(lo_r)}  {sig}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--votes", help="CSV with columns participant,object,criterion,choice")
    args = ap.parse_args()
    if args.votes:
        rng = np.random.default_rng(20260902)
        report(cluster_bootstrap(load_votes(args.votes), rng), f"real votes: {args.votes}")
    else:
        run_sim()


if __name__ == "__main__":
    main()
