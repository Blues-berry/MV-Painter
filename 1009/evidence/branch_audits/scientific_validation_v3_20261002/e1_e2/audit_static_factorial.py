#!/usr/bin/env python3
"""Check the locked static-factorial outputs before effect analysis."""
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
PROFILES = {
    "F00": {"deep": 1.25, "middle": 1.25, "shallow": 0.50},
    "F01": {"deep": 1.25, "middle": 1.25, "shallow": 0.80},
    "F10": {"deep": 1.675, "middle": 1.675, "shallow": 0.50},
    "F11": {"deep": 1.675, "middle": 1.675, "shallow": 0.80},
}
METRICS = ("fg_lpips", "fg_psnr")
INPUTS = ("target", "normal", "depth", "global_embeds", "init_latent")
NEW_PROFILES = {42: ("F10", "F11"), 43: tuple(PROFILES), 44: tuple(PROFILES)}
ALIASES = {"F00": "a3_baseline", "F01": "native_gfl"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def finite_tree(value):
    if isinstance(value, dict):
        return all(finite_tree(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(v) for v in value)
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return True


def rows_by_key(rows, label):
    result = {}
    for row in rows:
        key = (row["object_uid"], row["condition"])
        if key in result:
            old = {k: v for k, v in result[key].items() if k != "elapsed_seconds"}
            current = {k: v for k, v in row.items() if k != "elapsed_seconds"}
            require(old == current, f"conflicting duplicate row in {label}: {key}")
        else:
            result[key] = row
    return result


def main():
    design_path = HERE / "STATIC_FACTORIAL_DESIGN.json"
    design = read(design_path)
    require(design["status"] == "EXECUTION_LOCKED" and not design["do_not_run_until_dependencies_pass"],
            "static factorial is not execution-locked")
    design_sha = sha(design_path)
    execution_lock = read(HERE / "STATIC_EXECUTION_LOCK.json")
    require(execution_lock["status"] == "LOCKED_BEFORE_FORMAL_E2_GENERATION"
            and execution_lock["design_sha256"] == design_sha
            and execution_lock["runner_sha256"] == sha(HERE / "run_static_factorial.py")
            and execution_lock["analysis_sha256"] == sha(HERE / "analyze_static_factorial.py")
            and execution_lock["integrity_audit_sha256"] == sha(__file__),
            "formal runner/analysis/audit do not match the pre-generation lock")
    launch_record = read(HERE / "STATIC_RUN_LAUNCH_RECORD.json")
    require(launch_record["status"] == "PASS"
            and launch_record["execution_lock_sha256"] == sha(HERE / "STATIC_EXECUTION_LOCK.json"),
            "formal launch record is incomplete or linked to another execution lock")
    locked_protocol = read(HERE / "MULTISEED_PROTOCOL.json")
    uids = sorted((HERE / "MULTISEED_48_UIDS.txt").read_text().splitlines())
    require(len(uids) == 48 and len(set(uids)) == 48, "locked 48-object sample is not unique")
    source_b = (V3 / locked_protocol["source_full_cohort"]).read_text().splitlines()
    expected_indices = locked_protocol["source_object_indices"]
    uid_index = {uid: i for i, uid in enumerate(source_b)}
    require(set(uids) == {source_b[i] for i in expected_indices}, "UID sample differs from locked E1 sample")

    source_run = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
    source_rows = rows_by_key(sum((read(source_run / f"rows_shard{s}.json") for s in (0, 1)), []), "seed42 B")
    logical = {}
    generated_hashes = {}
    fingerprints = {}
    traces_checked = 0

    # The new seed-42 high-depth profiles complement the two exact B aliases.
    for seed, conditions in NEW_PROFILES.items():
        run_dir = HERE / f"static_seed{seed}"
        identity = read(run_dir / "EXECUTION_IDENTITY_shard0.json")
        manifest = read(run_dir / "run_manifest_shard0.json")
        selected = {name: PROFILES[name] for name in conditions}
        require(identity["preflight_only"] is False and identity["seed"] == seed,
                f"wrong static execution identity for seed {seed}")
        require(identity["design_sha256"] == design_sha and identity["profiles"] == selected,
                f"design/profile identity mismatch for seed {seed}")
        require(identity["reference_object_indices"] == expected_indices,
                f"reference indices changed for seed {seed}")
        require(identity["static_runner_sha256"] == sha(HERE / "run_static_factorial.py"),
                f"static wrapper changed after seed {seed}")
        require(manifest["protocol"] == "fixed_static_depth_shallow_factorial_v1"
                and manifest["static_design_sha256"] == design_sha
                and manifest["latent_seed"] == seed,
                f"manifest identity mismatch for seed {seed}")
        run_rows = read(run_dir / "rows_shard0.json")
        expected = {(uid, condition) for uid in uids for condition in conditions}
        generated = rows_by_key(run_rows, f"static seed {seed}")
        require(set(generated) == expected and len(run_rows) == len(expected),
                f"incomplete/duplicate rows for seed {seed}")

        for (uid, condition), row in generated.items():
            require(row["object_idx"] == uid_index[uid], f"cohort index mismatch {uid}")
            require(row["seed_base"] == 42, f"reference seed mismatch {uid} {condition}")
            require(all(math.isfinite(float(row[m])) for m in METRICS),
                    f"non-finite metric {uid} {condition}")
            trace_path = run_dir / "residual_logs" / condition / f"{uid}.json"
            pred_path = run_dir / "predictions" / condition / f"{uid}.png"
            require(trace_path.is_file() and pred_path.is_file(), f"missing prediction/trace {uid} {condition}")
            trace = read(trace_path)
            require(len(trace) == design["steps"] == 50, f"wrong trace length {uid} {condition}")
            require(finite_tree(trace), f"non-finite residual trace {uid} {condition}")
            effective = {}
            for step in trace.values():
                for entry in step.values():
                    layer = entry["depth"]
                    requested, applied = float(entry["scale"]), float(entry["eff_scale"])
                    require(requested == PROFILES[condition][layer],
                            f"requested scale differs from locked profile {uid}/{condition}/{layer}")
                    require(math.isfinite(applied) and 0 <= applied <= requested,
                            f"invalid effective scale {uid}/{condition}/{layer}")
                    effective.setdefault(layer, set()).add(applied)
                    traces_checked += 1
            require(set(effective) == {"deep", "middle", "shallow"}
                    and all(len(values) == 1 for values in effective.values()),
                    f"effective profile varies over time {uid} {condition}")
            logical[seed, uid, condition] = row
            fingerprints[seed, uid, condition] = {k: row["input_hashes"][k] for k in INPUTS}
            generated_hashes[f"seed{seed}/{condition}/{uid}/prediction"] = sha(pred_path)
            generated_hashes[f"seed{seed}/{condition}/{uid}/trace"] = sha(trace_path)

    # Map the seed-42 aliases into the frozen factorial labels and verify each file hash.
    reuse_gate = read(HERE / "STATIC_SEED42_REUSE_GATE.json")
    require(reuse_gate["effective_scale_trace_check"] == "PASS" and reuse_gate["objects_per_alias"] == 48,
            "seed-42 alias/reuse gate is not closed")
    for uid in uids:
        for condition, source in ALIASES.items():
            row = source_rows[uid, source]
            require(all(math.isfinite(float(row[m])) for m in METRICS), f"non-finite reused row {uid}/{condition}")
            logical[42, uid, condition] = row
            fingerprints[42, uid, condition] = {k: row["input_hashes"][k] for k in INPUTS}
            for kind, path in (
                ("prediction", source_run / "predictions" / source / f"{uid}.png"),
                ("residual", source_run / "residual_logs" / source / f"{uid}.json"),
            ):
                key = f"{condition}/{uid}/{kind}"
                actual_hash = sha(path)
                require(reuse_gate["per_file_sha256"].get(key) == actual_hash,
                        f"seed-42 reused file differs from alias gate: {key}")
                generated_hashes[f"seed42/{condition}/{uid}/{kind}"] = actual_hash

    require(len(logical) == 48 * 4 * 3, "logical factorial matrix is incomplete")
    for seed in (42, 43, 44):
        for uid in uids:
            inputs = [fingerprints[seed, uid, condition] for condition in PROFILES]
            require(all(inputs[0] == current for current in inputs[1:]),
                    f"shared inputs differ across static profiles {uid} seed={seed}")
    changed_latents = 0
    for uid in uids:
        refs = [fingerprints[seed, uid, "F00"] for seed in (42, 43, 44)]
        require(all(refs[0][k] == refs[1][k] == refs[2][k]
                    for k in ("target", "normal", "depth", "global_embeds")),
                f"non-latent references changed across generation seeds: {uid}")
        require(len({ref["init_latent"] for ref in refs}) == 3,
                f"generation seeds do not have distinct initial latents: {uid}")
        changed_latents += 2

    result = {
        "status": "PASS",
        "design_sha256": design_sha,
        "n_objects": len(uids),
        "conditions": list(PROFILES),
        "generation_seeds": [42, 43, 44],
        "reused_seed42_rows": 96,
        "new_rows": 480,
        "complete_logical_rows": len(logical),
        "expected_logical_rows": 576,
        "traces_checked": traces_checked,
        "prediction_and_trace_files_checked": len(generated_hashes),
        "shared_inputs_consistent": True,
        "changed_latents_across_adjacent_seeds": changed_latents,
        "seed42_alias_gate_sha256": sha(HERE / "STATIC_SEED42_REUSE_GATE.json"),
        "execution_lock_sha256": sha(HERE / "STATIC_EXECUTION_LOCK.json"),
        "launch_record_sha256": sha(HERE / "STATIC_RUN_LAUNCH_RECORD.json"),
        "not_analyzed_for_factorial_effects": True,
        "output_sha256": generated_hashes,
    }
    require(result["complete_logical_rows"] == result["expected_logical_rows"],
            "logical factorial matrix is incomplete")
    require(len(generated_hashes) == 576 * 2, "prediction/trace file matrix is incomplete")
    (HERE / "STATIC_FACTORIAL_INTEGRITY_GATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: 576 logical rows (480 new, 96 reused); profiles, shared references, traces, and hashes verified.")


if __name__ == "__main__":
    main()
