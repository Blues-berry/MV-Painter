#!/usr/bin/env python3
"""Two-level cluster bootstrap for the 3AFC preference study (R1.3 / R3-C3).

The study collects 24 participants x 30 objects x 3 criteria = 720 first-choice
votes per criterion. Votes within a participant and within an object are not
independent, so n=720 must not be treated as independent Bernoulli trials.
This script resamples participants (24) and objects (30) with replacement,
B=10000 times, and reports percentile 95% CIs for per-criterion first-choice
shares and for paired share differences (to be compared against the 1/3
chance level).

Usage:
    python cluster_bootstrap_preference.py --votes votes.csv [--reps 10000]

    votes.csv header: participant,object,criterion,choice
    choice    in {s1.25, s2.50, C3}
    criterion in {texture, shape, overall}
    participant/object ids may be 0-based or 1-based (auto-detected).
"""

import argparse
import csv

import numpy as np

METHODS = ["s1.25", "s2.50", "C3"]
CRITERIA = ["texture", "shape", "overall"]
P, O = 24, 30
B = 10000

# First-choice counts from tab:preference in final_submit.tex (out of 720 each),
# used only as point estimates for the paired differences.
TARGET = {
    "texture": [332, 104, 284],
    "shape": [96, 331, 293],
    "overall": [176, 126, 418],
}


def _numeric(s):
    """Strip leading non-numeric prefixes (e.g. exported id codes) from id fields."""
    s = str(s).strip()
    head = ""
    for ch in s:
        if ch.isdigit():
            break
        head += ch
    return s[len(head):] if head else s


def load_votes(path):
    """Load per-vote records into Y[c, m, p, o] indicator arrays."""
    Y = np.zeros((len(CRITERIA), len(METHODS), P, O))
    recs = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            recs.append((CRITERIA.index(row["criterion"].strip().lower()),
                         METHODS.index(row["choice"].strip()),
                         int(_numeric(row["participant"])),
                         int(_numeric(row["object"]))))
    pids = np.array([r[2] for r in recs])
    oids = np.array([r[3] for r in recs])
    # 0-based or 1-based ids (auto-detect)
    off_p = 1 if pids.min() >= 1 and pids.max() == P else 0
    off_o = 1 if oids.min() >= 1 and oids.max() == O else 0
    for c, m, pid, oid in recs:
        Y[c, m, pid - off_p, oid - off_o] += 1.0
    for c in range(len(CRITERIA)):
        if not np.allclose(Y[c].sum(0), 1.0):
            raise SystemExit(f"criterion '{CRITERIA[c]}' does not have exactly one valid choice per (participant, object)")
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


def report(shares):
    lo, hi = np.percentile(shares, [2.5, 97.5], axis=-1)
    print(f"{'criterion':<10}{'method':<8}{'share':>7}   95% CI")
    for c, crit in enumerate(CRITERIA):
        for m, meth in enumerate(METHODS):
            pt = 100 * TARGET[crit][m] / (P * O)
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--votes", required=True,
                    help="CSV with columns participant,object,criterion,choice")
    ap.add_argument("--reps", type=int, default=B, help="bootstrap replicates (default 10000)")
    args = ap.parse_args()
    rng = np.random.default_rng(20260902)
    report(cluster_bootstrap(load_votes(args.votes), rng, B=args.reps))


if __name__ == "__main__":
    main()
