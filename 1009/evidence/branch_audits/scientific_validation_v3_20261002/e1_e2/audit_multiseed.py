#!/usr/bin/env python3
"""Check 48-object fixed-reference realization ledgers before opening effects."""
import hashlib
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    lock = read(HERE / "MULTISEED_PROTOCOL.json")
    cohort_file = V3 / lock["source_full_cohort"]
    uids = cohort_file.read_text().splitlines()
    require(sha(cohort_file) == lock["source_cohort_sha256"], "B cohort hash changed")
    expected = {(uids[i], c) for i in lock["source_object_indices"] for c in lock["conditions"]}
    seedrows, render_hashes, trace_hashes = {}, {}, {}
    fixed_inputs = {}
    for seed in (43, 44):
        directory = HERE / f"formal_seed{seed}"
        identity = read(directory / "EXECUTION_IDENTITY_shard0.json")
        require(identity["generation_seed"] == seed and identity["source_object_indices"] == lock["source_object_indices"], "Execution identity mismatch")
        manifest = read(directory / "run_manifest_shard0.json")
        require(manifest["status"] == "complete" and manifest["row_count"] == 288, "Incomplete run manifest")
        for source in manifest["code_source_sha256"].values():
            require(sha(source["path"]) == source["sha256"], "Frozen inference/metric source changed")
        rows = read(directory / "rows_shard0.json")
        keys = [(r["object_uid"], r["condition"]) for r in rows]
        require(len(rows) == 288 and len(set(keys)) == 288 and set(keys) == expected, f"Seed {seed} has incomplete/duplicate rows")
        table = {key: row for key, row in zip(keys, rows)}
        local = {}
        for key, row in table.items():
            require(all(math.isfinite(float(row[m])) for m in ("fg_psnr", "fg_lpips")), "Nonfinite primary metric")
            fixed = {k: v for k, v in row["input_hashes"].items() if k != "init_latent"}
            require(local.setdefault(key[0], fixed) == fixed, "Shared input mismatch across conditions")
            if key[0] in fixed_inputs:
                require(fixed_inputs[key[0]] == fixed, "Reference inputs changed across generation seeds")
            else:
                fixed_inputs[key[0]] = fixed
            png = directory / "predictions" / key[1] / f"{key[0]}.png"
            trace = directory / "residual_logs" / key[1] / f"{key[0]}.json"
            require(png.is_file() and trace.is_file(), "Missing prediction or residual trace")
            render_hashes[f"{seed}/{key[0]}/{key[1]}"] = sha(png)
            trace_hashes[f"{seed}/{key[0]}/{key[1]}"] = sha(trace)
        seedrows[seed] = table
    output = HERE / "MULTISEED_INTEGRITY_GATE.json"
    result = {"status": "PASS", "objects": 48, "conditions": 6, "generation_seeds": [43, 44], "new_rows": 576, "unique_rows": 576, "shared_reference_inputs_across_conditions_and_seeds": "PASS", "prediction_files_hashed": len(render_hashes), "residual_traces_hashed": len(trace_hashes), "per_output_sha256": {"predictions": render_hashes, "residual_traces": trace_hashes}, "provenance": {"audit_script_sha256": sha(__file__), "protocol_sha256": sha(HERE / "MULTISEED_PROTOCOL.json"), "source_cohort_sha256": sha(cohort_file)}, "scientific_summary_opened": False}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "per_output_sha256"}, indent=2))


if __name__ == "__main__":
    main()
