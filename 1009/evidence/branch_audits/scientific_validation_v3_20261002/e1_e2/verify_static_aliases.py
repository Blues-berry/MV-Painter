#!/usr/bin/env python3
"""Verify the two planned seed42 factorial rows can reuse B exactly."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    uids = (HERE / "MULTISEED_48_UIDS.txt").read_text().splitlines()
    all_rows = []
    for shard in (0, 1):
        all_rows.extend(json.loads((RUN / f"rows_shard{shard}.json").read_text()))
    expected = {"F00": "a3_baseline", "F01": "native_gfl"}
    sources = {}
    for target, source in expected.items():
        src = {r["object_uid"]: r for r in all_rows if r["condition"] == source}
        if set(src) < set(uids) or len(src) != 150:
            raise ValueError(f"Missing B rows for alias {source}")
        for uid in uids:
            trace = json.loads((RUN / "residual_logs" / source / f"{uid}.json").read_text())
            target_profile = ({"deep": 1.25, "middle": 1.25, "shallow": 0.50} if target == "F00"
                              else {"deep": 1.25, "middle": 1.25, "shallow": 0.80})
            if len(trace) != 50:
                raise ValueError(f"Wrong step count in {source}/{uid}")
            for step in trace.values():
                for entry in step.values():
                    req_scale = (1.25 if target == "F01" and entry["depth"] == "shallow"
                                 else target_profile[entry["depth"]])
                    if entry["scale"] != req_scale or entry["eff_scale"] != target_profile[entry["depth"]]:
                        raise ValueError(f"Effective profile mismatch for {source}/{uid}")
            pred = RUN / "predictions" / source / f"{uid}.png"
            sources[f"{target}/{uid}/prediction"] = sha(pred)
            sources[f"{target}/{uid}/residual"] = sha(RUN / "residual_logs" / source / f"{uid}.json")
    # Both profiles had native, non-uncapped forward paths in the frozen runner.
    manifests = [json.loads((RUN / f"run_manifest_shard{s}.json").read_text()) for s in (0, 1)]
    if any(m["runner_script_sha256"] != "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3" for m in manifests):
        raise ValueError("Source runner does not match the pinned B path")
    result = {"F00_alias": "a3_baseline", "F01_alias": "native_gfl", "objects_per_alias": len(uids),
              "effective_scale_trace_check": "PASS", "forward_path": "native capped; requested scales below/equal layer ceilings", "reused_seed42_files_hashed": len(sources), "per_file_sha256": sources}
    (HERE / "STATIC_SEED42_REUSE_GATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "per_file_sha256"}, indent=2))


if __name__ == "__main__":
    main()
