#!/usr/bin/env python3
"""Object-level analysis of the locked four-profile static-factor sensitivity."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
BOOT = 10_000
RNG_SEED = 20261006
CONDITIONS = ("F00", "F01", "F10", "F11")
FACTORS = ("deep_middle", "shallow", "interaction")
METRICS = {"fg_lpips": "lower", "fg_psnr": "higher"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def holm(p_values):
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def factors(y00, y01, y10, y11):
    return {
        "deep_middle": 0.5 * ((y10 - y00) + (y11 - y01)),
        "shallow": 0.5 * ((y01 - y00) + (y11 - y10)),
        "interaction": (y11 - y10) - (y01 - y00),
    }


def bootstrap(values):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(RNG_SEED)
    picks = rng.integers(0, len(values), size=(BOOT, len(values)))
    observed = float(values.mean())
    samples = values[picks].mean(axis=1)
    if np.ptp(values) == 0:
        p = 1.0
        degenerate = True
    else:
        null_samples = (values - observed)[picks].mean(axis=1)
        p = (1 + int(np.sum(np.abs(null_samples) >= abs(observed)))) / (BOOT + 1)
        degenerate = False
    return {"mean": observed, "median": float(np.median(values)),
            "ci95_object_bootstrap": np.percentile(samples, [2.5, 97.5]).tolist(),
            "p_centered_object_bootstrap": p, "object_effect_degenerate": degenerate,
            "fraction_positive_objects": float(np.mean(values > 0)),
            "fraction_negative_objects": float(np.mean(values < 0))}


def load_rows(path):
    rows = json.loads(Path(path).read_text())
    result = {}
    for row in rows:
        key = (row["object_uid"], row["condition"])
        if key in result:
            raise ValueError(f"duplicate analysis row: {key}")
        result[key] = row
    return result


def load_seed42():
    run = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
    values = {}
    for shard in (0, 1):
        for row in json.loads((run / f"rows_shard{shard}.json").read_text()):
            key = (row["object_uid"], row["condition"])
            if key in values:
                old = {k: v for k, v in values[key].items() if k != "elapsed_seconds"}
                current = {k: v for k, v in row.items() if k != "elapsed_seconds"}
                if old != current:
                    raise ValueError(f"seed42 source aliases conflict: {key}")
            else:
                values[key] = row
    return values


def verify_synthetic_checks():
    # Additive response has zero difference-in-differences; an injected term is recovered.
    base = 1.7
    a, b = -0.3, 0.8
    additive = [base, base + b, base + a, base + a + b]
    effects = factors(*additive)
    assert abs(effects["deep_middle"] - a) < 1e-12
    assert abs(effects["shallow"] - b) < 1e-12
    assert abs(effects["interaction"]) < 1e-12
    gamma = 0.45
    interaction = [base, base + b, base + a, base + a + b + gamma]
    assert abs(factors(*interaction)["interaction"] - gamma) < 1e-12
    assert bootstrap(np.zeros(48))["p_centered_object_bootstrap"] == 1.0
    assert bootstrap(np.linspace(0.08, 0.12, 48))["p_centered_object_bootstrap"] < 0.05
    # Stable UID ordering gives byte-identical vectors regardless of input mapping order.
    ids = [f"uid{i:02d}" for i in range(48)]
    values = {uid: i / 47 for i, uid in enumerate(ids)}
    left = np.array([values[uid] for uid in sorted(ids)])
    right = np.array([values[uid] for uid in sorted(reversed(ids))])
    assert np.array_equal(left, right)


def main():
    gate_path = HERE / "STATIC_FACTORIAL_INTEGRITY_GATE.json"
    gate = json.loads(gate_path.read_text())
    if gate["status"] != "PASS" or gate["complete_logical_rows"] != 576:
        raise RuntimeError("Do not analyze before all 576 logical rows pass integrity.")
    verify_synthetic_checks()
    design_path = HERE / "STATIC_FACTORIAL_DESIGN.json"
    design = json.loads(design_path.read_text())
    uids = sorted((HERE / "MULTISEED_48_UIDS.txt").read_text().splitlines())
    source42 = load_seed42()
    runs = {
        42: {(uid, "F00"): source42[uid, "a3_baseline"] for uid in uids}
           | {(uid, "F01"): source42[uid, "native_gfl"] for uid in uids},
        43: load_rows(HERE / "static_seed43/rows_shard0.json"),
        44: load_rows(HERE / "static_seed44/rows_shard0.json"),
    }
    runs[42].update(load_rows(HERE / "static_seed42/rows_shard0.json"))
    if len(runs[42]) != 48 * 4:
        raise ValueError("seed 42 matrix must combine two reused aliases and two generated profiles")
    for seed in (43, 44):
        if len(runs[seed]) != 48 * 4:
            raise ValueError(f"bad formal row count for seed {seed}")

    y = {metric: {uid: {seed: {condition: float(runs[seed][uid, condition][metric])
                              for condition in CONDITIONS}
                         for seed in (42, 43, 44)}
                  for uid in uids}
         for metric in METRICS}
    result = {
        "analysis": "Post-B fixed-cohort static 2x2 sensitivity; each object first averages paired contrasts across three fixed generation seeds.",
        "n_objects": len(uids), "generation_seeds": [42, 43, 44],
        "seed42_reuse": {"F00": "a3_baseline", "F01": "native_gfl"},
        "bootstrap_draws": BOOT, "bootstrap_seed": RNG_SEED,
        "test": "Two-sided centered object bootstrap for the mean of object-level seed-averaged factor contrasts; percentile object bootstrap 95% CI.",
        "metrics": {},
        "interpretation_limit": "Selected 48-object post-B sensitivity, conditional on these three fixed generation seeds; not independent-object confirmation or a random-seed population interval. Deep and middle are moved together; no equal-realized-dose claim. Simple contrasts are descriptive.",
    }
    effects_rows = []
    for metric, favorable in METRICS.items():
        object_effects = {factor: {} for factor in FACTORS}
        effect_seed_means = {factor: {} for factor in FACTORS}
        for uid in uids:
            per_seed = {factor: {} for factor in FACTORS}
            for seed in (42, 43, 44):
                vals = y[metric][uid][seed]
                for factor, val in factors(vals["F00"], vals["F01"], vals["F10"], vals["F11"]).items():
                    per_seed[factor][seed] = float(val)
            for factor in FACTORS:
                object_effects[factor][uid] = float(np.mean(list(per_seed[factor].values())))
            effects_rows.append({"metric": metric, "uid": uid,
                                 **{f"{factor}_{seed}": per_seed[factor][seed]
                                    for factor in FACTORS for seed in (42, 43, 44)},
                                 **{f"{factor}_seed_averaged": object_effects[factor][uid]
                                    for factor in FACTORS}})
        blocks, raw_p = [], []
        for factor in FACTORS:
            values = np.array([object_effects[factor][uid] for uid in uids], dtype=float)
            summary = bootstrap(values)
            by_seed = {str(seed): float(np.mean([factors(
                y[metric][uid][seed]["F00"], y[metric][uid][seed]["F01"],
                y[metric][uid][seed]["F10"], y[metric][uid][seed]["F11"])[factor]
                for uid in uids])) for seed in (42, 43, 44)}
            summary.update({"factor": factor,
                            "mean_delta_by_generation_seed": by_seed,
                            "favorable_object_fraction": float(np.mean(values < 0 if favorable == "lower" else values > 0))})
            blocks.append(summary)
            raw_p.append(summary["p_centered_object_bootstrap"])
        adjusted = holm(raw_p)
        for block, p_adj in zip(blocks, adjusted):
            block["p_holm_three_factors"] = p_adj

        simple = []
        contrasts = (("F01-F00 at D0", "F01", "F00"),
                     ("F11-F10 at D1", "F11", "F10"),
                     ("F10-F00 at S0", "F10", "F00"),
                     ("F11-F01 at S1", "F11", "F01"))
        for label, left, right in contrasts:
            delta = np.array([np.mean([y[metric][uid][seed][left] - y[metric][uid][seed][right]
                                       for seed in (42, 43, 44)]) for uid in uids])
            entry = bootstrap(delta)
            entry.update({"contrast": label, "multiplicity_adjusted": False})
            simple.append(entry)
        result["metrics"][metric] = {"holm_family_size": 3,
                                     "factor_effects": blocks,
                                     "simple_contrasts_descriptive": simple,
                                     "condition_means_by_generation_seed": {
                                         str(seed): {condition: float(np.mean([y[metric][uid][seed][condition]
                                                                             for uid in uids]))
                                                     for condition in CONDITIONS}
                                         for seed in (42, 43, 44)}}
    out = HERE / "STATIC_FACTORIAL_ANALYSIS.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    with (HERE / "STATIC_FACTORIAL_OBJECT_EFFECTS.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(effects_rows[0]))
        writer.writeheader()
        writer.writerows(effects_rows)
    lines = ["# Static 2×2 factor sensitivity", "", result["analysis"], "",
             "Effects are arithmetic responses in the reported metric: negative LPIPS is favorable; positive PSNR is favorable.", ""]
    for metric, block in result["metrics"].items():
        lines += [f"## {metric}", "", "| Factor | Mean [95% object-bootstrap CI] | Favorable objects | Seed means (42 / 43 / 44) | Holm p |",
                  "|---|---:|---:|---|---:|"]
        for entry in block["factor_effects"]:
            lo, hi = entry["ci95_object_bootstrap"]
            means = ", ".join(f"{s}: {x:+.5g}" for s, x in entry["mean_delta_by_generation_seed"].items())
            lines.append(f"| {entry['factor']} | {entry['mean']:+.5g} [{lo:+.5g}, {hi:+.5g}] | {entry['favorable_object_fraction']:.1%} | {means} | {entry['p_holm_three_factors']:.5g} |")
        lines.append("")
    lines += [result["interpretation_limit"], ""]
    (HERE / "STATIC_FACTORIAL_ANALYSIS.md").write_text("\n".join(lines))
    print("Computed locked object-level factorial effects for both endpoints.")


if __name__ == "__main__":
    main()
