#!/usr/bin/env python3
"""Join existing CPU-only input hashes; never opens generated RGB predictions."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
INPUT_PAIR_AUDIT = ROOT / "1008/engineering/fidelity_validation_48h/ALL_COHORT_INPUT_PAIR_AUDIT.csv"
CURRENT_CONDITION_AUDIT = HERE / "runs/phase_a/FRESHB_INPUT_EMBEDDING_PROVENANCE.csv"
HOLDOUT_LOCK = HERE / "protocol/D_VALIDATION_LOCK.json"
UID_LIST = BASE / "final/round2/scientific_validation_v3/fresh_confirm_b/fresh_confirm_b.txt"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    lock = json.loads(HOLDOUT_LOCK.read_text())
    uids = [line.strip() for line in UID_LIST.read_text().splitlines() if line.strip()]
    if len(uids) != 150 or sha_file(UID_LIST) != lock["cohort_list_sha256"]:
        raise RuntimeError("Fresh B UID list no longer matches its frozen identity")
    input_rows = {r["uid"]: r for r in read_csv(INPUT_PAIR_AUDIT) if r["cohort"] == "FreshB"}
    condition_rows = {r["uid"]: r for r in read_csv(CURRENT_CONDITION_AUDIT)}
    if set(uids) != set(input_rows) or set(uids) != set(condition_rows):
        raise RuntimeError("input audits do not cover the exact frozen Fresh B objects")

    rows = []
    for index, uid in enumerate(uids):
        old = input_rows[uid]
        current = condition_rows[uid]
        if int(old["object_idx"]) != index or int(current["object_idx"]) != index:
            raise RuntimeError(f"{uid}: input audit ordering/index changed")
        condition_match = current["condition_tensor_sha256"] == old["input_cond_sha256"]
        embedding_match = current["global_embedding_cache_tensor_sha256"] == old["input_global_embeds_sha256"]
        rows.append({
            "uid": uid,
            "object_idx": index,
            "object_seed": int(old["seed_base"]) + index,
            "condition_png": current["condition_source_png"],
            "condition_png_sha256": current["condition_source_png_sha256"],
            "condition_tensor_sha256_current_audit": current["condition_tensor_sha256"],
            "condition_tensor_sha256_prior_generation": old["input_cond_sha256"],
            "condition_tensor_matches_prior_generation": condition_match,
            "condition_alpha_tensor_sha256": current["condition_alpha_sha256"],
            "cached_embedding_tensor_sha256_current_audit": current["global_embedding_cache_tensor_sha256"],
            "cached_embedding_tensor_sha256_prior_generation": old["input_global_embeds_sha256"],
            "cached_embedding_matches_prior_generation": embedding_match,
            "target_tensor_sha256_prior_generation": old["input_target_sha256"],
            "normal_tensor_sha256_prior_generation": old["input_normal_sha256"],
            "depth_tensor_sha256_prior_generation": old["input_depth_sha256"],
        })

    out_dir = HERE / "runs/phase_d/input_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "FRESHB_BASELINE_INPUT_RECONSTRUCTION.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "scope": "Hash join of prior CPU-only input audits; no prediction PNG pixels or generated quality metrics read",
        "freshb_uid_list_sha256": sha_file(UID_LIST),
        "prior_input_hash_audit_sha256": sha_file(INPUT_PAIR_AUDIT),
        "current_condition_provenance_sha256": sha_file(CURRENT_CONDITION_AUDIT),
        "freshb_n": len(rows),
        "condition_matches_prior_generation_n": sum(bool(r["condition_tensor_matches_prior_generation"]) for r in rows),
        "cached_embeddings_match_prior_generation_n": sum(bool(r["cached_embedding_matches_prior_generation"]) for r in rows),
        "condition_alpha_sha256_rows": sum(bool(r["condition_alpha_tensor_sha256"]) for r in rows),
        "csv_sha256": sha_file(output),
    }
    (out_dir / "FRESHB_BASELINE_INPUT_RECONSTRUCTION.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
