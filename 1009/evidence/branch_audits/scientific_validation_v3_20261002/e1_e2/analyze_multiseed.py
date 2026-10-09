#!/usr/bin/env python3
"""Object-level analysis conditional on the three frozen generation seeds."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CONDITIONS = ("native_gfl", "native_gfh", "native_gc3", "lfm_exact", "layer_llh", "gen_linear")
COMPARISONS = tuple(("layer_llh", c) for c in CONDITIONS if c != "layer_llh")
METRICS = {"fg_lpips": "lower", "fg_psnr": "higher"}
BOOT = 10_000
SEED = 20261006


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def holm(p):
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0.0
    for rank, ix in enumerate(order):
        running = max(running, (len(p) - rank) * p[ix])
        adj[ix] = min(1.0, running)
    return adj.tolist()


def bootstrap(delta):
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(delta), size=(BOOT, len(delta)))
    samples = delta[picks].mean(axis=1)
    # Center the empirical object distribution at the null mean for a paired,
    # object-level two-sided bootstrap test. This keeps the CI and test unit the
    # same; it does not treat generation seeds as independent observations.
    observed = float(delta.mean())
    null_samples = (delta - observed)[picks].mean(axis=1)
    degenerate = bool(np.ptp(delta) == 0)
    p = (1.0 if degenerate else
         (1 + int(np.sum(np.abs(null_samples) >= abs(observed)))) / (BOOT + 1))
    return {"mean_delta": float(delta.mean()), "median_delta": float(np.median(delta)),
            "ci95_object_bootstrap": np.percentile(samples, [2.5, 97.5]).tolist(),
            "p_centered_object_bootstrap": p,
            "object_effect_degenerate": degenerate}


def load(seed):
    if seed == 42:
        v3 = HERE.parent
        bases = [
            v3 / "formal/campaign_FRESH_CONFIRM_B_20261005",
            v3 / "formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005",
        ]
        result = {}
        for base in bases:
            for path in sorted(base.glob("rows_shard*.json")):
                for row in json.loads(path.read_text()):
                    key = (row["object_uid"], row["condition"])
                    if key in result:
                        old = {k: v for k, v in result[key].items() if k != "elapsed_seconds"}
                        current = {k: v for k, v in row.items() if k != "elapsed_seconds"}
                        if old != current:
                            raise ValueError(f"conflicting seed-42 source row: {key}")
                    else:
                        result[key] = row
        return result
    path = HERE / f"formal_seed{seed}/rows_shard0.json"
    with path.open() as f:
        rows = json.load(f)
    return {(r["object_uid"], r["condition"]): r for r in rows}


def main():
    integrity = json.loads((HERE / "MULTISEED_INTEGRITY_GATE.json").read_text())
    if integrity["status"] != "PASS" or integrity["new_rows"] != 576:
        raise RuntimeError("Do not analyze before the full 576-row integrity gate passes.")
    reaudit = json.loads((HERE / "MULTISEED_REAUDIT_20261006.json").read_text())
    if (reaudit["status"] != "PASS" or reaudit["new_rows"] != 576
            or reaudit["per_output_sha256"] != integrity["per_output_sha256"]):
        raise RuntimeError("Post-lock provenance re-audit does not match the locked output hashes.")
    protocol = json.loads((HERE / "MULTISEED_PROTOCOL.json").read_text())
    source_uids = (HERE.parent / protocol["source_full_cohort"]).read_text().splitlines()
    uids = sorted(source_uids[i] for i in protocol["source_object_indices"])
    runs = {seed: load(seed) for seed in (42, 43, 44)}
    expected_keys = {(uid, condition) for uid in uids for condition in CONDITIONS}
    for seed, table in runs.items():
        if not expected_keys <= set(table):
            raise RuntimeError(f"Seed {seed} is missing fixed analysis rows.")
    row_paths = []
    for base in (HERE.parent / "formal/campaign_FRESH_CONFIRM_B_20261005",
                 HERE.parent / "formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005",
                 HERE / "formal_seed43", HERE / "formal_seed44"):
        row_paths.extend(sorted(base.glob("rows_shard*.json")))
    result = {"analysis": "Post-B supplementary multi-realization sensitivity; fixed stratified 48-object sample; effects average three generation-seed paired contrasts within object; object bootstrap conditional on these three seeds", "n_objects": len(uids), "generation_seeds": [42, 43, 44], "bootstrap_draws": BOOT, "bootstrap_seed": SEED, "provenance": {"locked_integrity_gate_sha256": sha(HERE / "MULTISEED_INTEGRITY_GATE.json"), "read_only_reaudit_sha256": sha(HERE / "MULTISEED_REAUDIT_20261006.json"), "protocol_sha256": sha(HERE / "MULTISEED_PROTOCOL.json"), "cohort_file_sha256": sha(HERE.parent / protocol["source_full_cohort"]), "locked_uid_list_sha256": sha(HERE / "MULTISEED_48_UIDS.txt"), "analysis_script_sha256": sha(__file__), "row_files_sha256": {str(path.relative_to(HERE.parent)): sha(path) for path in row_paths}}, "metrics": {}}
    for metric, favorable in METRICS.items():
        tests, raw_p = [], []
        for method, comparator in COMPARISONS:
            by_seed = {}
            deltas = np.empty((len(uids), 3), dtype=float)
            for j, seed in enumerate((42, 43, 44)):
                for i, uid in enumerate(uids):
                    deltas[i, j] = float(runs[seed][uid, method][metric]) - float(runs[seed][uid, comparator][metric])
                by_seed[str(seed)] = float(deltas[:, j].mean())
            mean_object_delta = deltas.mean(axis=1)
            summary = bootstrap(mean_object_delta)
            median_seed_range = float(np.median(np.ptp(deltas, axis=1)))
            summary.update({"contrast": f"{method}-{comparator}", "mean_delta_by_generation_seed": by_seed,
                            "favorable_object_fraction": float(np.mean(mean_object_delta < 0 if favorable == "lower" else mean_object_delta > 0)),
                            "same_sign_object_fraction_across_all_three_seeds": float(np.mean(np.all(deltas < 0, axis=1) if favorable == "lower" else np.all(deltas > 0, axis=1))),
                            "median_absolute_within_object_seed_range": median_seed_range,
                            "absolute_mean_effect_over_median_seed_range": (abs(summary["mean_delta"]) / median_seed_range if median_seed_range > 0 else None)})
            tests.append(summary)
            raw_p.append(summary["p_centered_object_bootstrap"])
        adjusted = holm(raw_p)
        for entry, p_adj in zip(tests, adjusted):
            entry["p_holm_five_contrasts"] = p_adj
        result["metrics"][metric] = {"holm_family_size": 5, "contrasts": tests}
    result["interpretation_limit"] = "Inference describes these 48 fixed objects averaged over these three seeds; seed variability and the absolute-effect/median-seed-range ratio are descriptive, not a random-seed population CI or a test against realization noise. This selected post-B cohort is not independent-object confirmation. p values at the reporting floor are not exact zero."
    out = HERE / "MULTISEED_ANALYSIS.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Multi-seed sensitivity results", "", result["analysis"], "", "All deltas are LLH minus comparator. Positive FG-PSNR and negative FG-LPIPS favor LLH.", ""]
    for metric, block in result["metrics"].items():
        lines += [f"## {metric}", "", "| Comparator | Mean [95% object-bootstrap CI] | Favorable objects | Same-sign objects in all seeds | Effect / median seed range | Seed means | Holm p |", "|---|---:|---:|---:|---:|---|---:|"]
        for row in block["contrasts"]:
            ci = row["ci95_object_bootstrap"]
            means = ", ".join(f"{seed}: {x:+.5g}" for seed, x in row["mean_delta_by_generation_seed"].items())
            ratio = row["absolute_mean_effect_over_median_seed_range"]
            lines.append(f"| {row['contrast'].split('-', 1)[1]} | {row['mean_delta']:+.5g} [{ci[0]:+.5g}, {ci[1]:+.5g}] | {row['favorable_object_fraction']:.1%} | {row['same_sign_object_fraction_across_all_three_seeds']:.1%} | {ratio:.3g} | {means} | {row['p_holm_five_contrasts']:.5g} |")
        lines.append("")
    lines += [result["interpretation_limit"], "",
              f"Provenance: locked integrity gate `{result['provenance']['locked_integrity_gate_sha256']}`; read-only re-audit `{result['provenance']['read_only_reaudit_sha256']}`; analysis source `{result['provenance']['analysis_script_sha256']}`; {len(row_paths)} raw row files hashed.", ""]
    (HERE / "MULTISEED_ANALYSIS.md").write_text("\n".join(lines))
    print("Computed fixed-cohort, object-level seed-averaged estimates for both frozen endpoints.")


if __name__ == "__main__":
    main()
