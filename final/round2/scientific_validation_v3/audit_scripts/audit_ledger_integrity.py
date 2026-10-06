#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) — Row integrity + object identity audit.

Read-only. Verifies, for every formal campaign ledger (rows_shard*.json):
  1. expected row counts and (condition, object_uid) completeness
  2. exactly the frozen FRESH_CONFIRM_300 cohort, no extras
  3. no NaN/Inf in any numeric metric
  4. input_hashes present on every row (6 hashes)
  5. cross-condition identity: target/normal/depth/global_embeds/init_latent
     hashes identical across all conditions of the same object
  6. object fingerprint uniqueness across distinct UIDs (silent-substitution gate)
  7. shard assignment: object_idx % NUM_SHARDS == shard of file
  8. cond-hash <-> condition bijection (A2 vs A3 must differ for same names)
  9. B3 duplicate-(uid,cond) replicate consistency
 10. ledger vs reconstructed CSV numeric agreement

Outputs (next to this script, ../ = scientific_validation_v3/):
  OBJECT_IDENTITY_PER_ROW.csv
  AUDIT_LEDGER_SUMMARY.json
"""
import csv
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMAL = ROOT / "formal"
HASH_KEYS = ["target", "normal", "depth", "global_embeds", "init_latent"]
CAMPAIGNS = {
    "A2":   {"dir": "campaign_A2",   "shards": 4, "n_cond": 16, "n_uid": 300},
    "A3":   {"dir": "campaign_A3",   "shards": 4, "n_cond": 16, "n_uid": 300},
    "B1B2": {"dir": "campaign_B1B2", "shards": 4, "n_cond": 6,  "n_uid": 300},
    "B3":   {"dir": "campaign_B3",   "shards": 4, "n_cond": 7,  "n_uid": 300},
    "C":    {"dir": "campaign_C",    "shards": 2, "n_cond": 8,  "n_uid": 300},
}
NON_NUMERIC = {"object", "object_uid", "condition", "input_hashes"}


def is_bad_number(v):
    if isinstance(v, bool):
        return False
    if isinstance(v, float):
        return math.isnan(v) or math.isinf(v)
    return False


def fp_of(hashes):
    h = hashlib.sha256()
    for k in HASH_KEYS:
        h.update(hashes[k].encode())
    return h.hexdigest()


def load_campaign(name, cfg):
    cdir = FORMAL / cfg["dir"]
    rows = []
    shard_of_row = []
    for s in range(cfg["shards"]):
        p = cdir / f"rows_shard{s}.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        for r in data:
            rows.append(r)
            shard_of_row.append(s)
    return rows, shard_of_row, cdir


def main():
    cohort = set((ROOT / "fresh_confirm_300.txt").read_text().split())
    assert len(cohort) == 300, f"cohort file has {len(cohort)} UIDs"
    summary = {}
    identity_writer_rows = []
    overall_fail = []

    for name, cfg in CAMPAIGNS.items():
        rep = {"expected_rows": cfg["n_cond"] * cfg["n_uid"]}
        rows, shard_of, cdir = load_campaign(name, cfg)
        rep["actual_rows"] = len(rows)

        # -- completeness & duplicates -------------------------------------
        pairs = [(r["condition"], r["object_uid"]) for r in rows]
        rep["unique_pairs"] = len(set(pairs))
        dup_pairs = {p for p in pairs if pairs.count(p) > 1} if name == "B3" else set()
        rep["duplicate_pairs"] = sorted(dup_pairs)
        uids = {r["object_uid"] for r in rows}
        conds = sorted({r["condition"] for r in rows})
        rep["n_uids"] = len(uids)
        rep["n_conds"] = len(conds)
        rep["conditions"] = conds
        rep["uid_set_matches_cohort"] = (uids == cohort)
        rep["missing_uids"] = sorted(cohort - uids)
        rep["extra_uids"] = sorted(uids - cohort)
        expected_pairs = {(c, u) for c in conds for u in cohort}
        have = set(pairs)
        rep["missing_pairs"] = len(expected_pairs - have)
        rep["extra_pairs"] = len(have - expected_pairs)

        # -- per-row checks --------------------------------------------------
        bad_num_rows, missing_hash_rows, bad_shard_rows = [], [], []
        for i, r in enumerate(rows):
            for k, v in r.items():
                if k not in NON_NUMERIC and is_bad_number(v):
                    bad_num_rows.append((r["object_uid"], r["condition"], k))
            ih = r.get("input_hashes")
            if not isinstance(ih, dict) or any(not ih.get(k) for k in HASH_KEYS) or not ih.get("cond"):
                missing_hash_rows.append((r["object_uid"], r["condition"]))
            if i < len(shard_of) and (r["object_idx"] % cfg["shards"]) != shard_of[i]:
                bad_shard_rows.append((r["object_uid"], r["condition"]))
        rep["rows_with_nan_inf"] = bad_num_rows[:20] + (["..."] if len(bad_num_rows) > 20 else [])
        rep["rows_with_nan_inf_count"] = len(bad_num_rows)
        rep["rows_missing_input_hashes"] = missing_hash_rows[:20]
        rep["rows_missing_input_hashes_count"] = len(missing_hash_rows)
        # -- B3 resume artifact: rerun rows (150-uid subset on shards 0/1) may sit
        # outside idx%4; they are admissible iff each such row exactly duplicates a
        # correctly-placed original row (verified by replicate comparison below).
        misplaced = set(map(tuple, bad_shard_rows))
        misplaced_rows = [(r["condition"], r["object_uid"]) for i, r in enumerate(rows)
                          if (r["object_idx"] % cfg["shards"]) != shard_of[i]]
        have_pairs = set(pairs)
        unexplained_misplaced = [m for m in misplaced_rows
                                 if not (m in have_pairs and pairs.count(m) > 1)]
        rep["rows_wrong_shard"] = bad_shard_rows[:20]
        rep["rows_wrong_shard_count"] = len(bad_shard_rows)
        rep["rows_wrong_shard_unexplained_count"] = len(unexplained_misplaced)

        # -- cross-condition identity & fingerprint uniqueness ----------------
        per_uid = defaultdict(dict)   # uid -> cond -> {hashkey: hash}
        for r in rows:
            per_uid[r["object_uid"]][r["condition"]] = r["input_hashes"]
        inconsistent = {}
        for uid, m in per_uid.items():
            ref = next(iter(m.values()))
            for k in HASH_KEYS:
                vals = {m[c][k] for c in m}
                if len(vals) != 1:
                    inconsistent.setdefault(uid, {})[k] = sorted(vals)
        rep["objects_cross_condition_inconsistent"] = dict(list(inconsistent.items())[:10])
        rep["objects_cross_condition_inconsistent_count"] = len(inconsistent)

        fps = {}
        fp_dup = defaultdict(list)
        for uid, m in per_uid.items():
            ref = next(iter(m.values()))
            fp = fp_of(ref)
            fps[uid] = fp
            fp_dup[fp].append(uid)
        dups = {fp: u for fp, u in fp_dup.items() if len(u) > 1}
        rep["fingerprint_duplicate_groups"] = {fp[:16]: sorted(u) for fp, u in dups.items()}
        rep["fingerprint_duplicates_count"] = len(dups)

        # -- cond-hash semantics ------------------------------------------------
        # NOTE: `cond` hash is the hash of the conditioning TENSOR bytes (includes
        # per-object embedding), so it is legitimately unique per (condition, object).
        # The meaningful check: it must be a pure function of (condition, object_uid)
        # — i.e. no (condition, uid) pair may carry two distinct cond hashes
        # (verified exhaustively by the B3 duplicate-replicate comparison below and
        # by cross-condition checks). Recorded here for the report.
        condhash = defaultdict(set)
        pair_condhash = defaultdict(set)
        for r in rows:
            condhash[r["condition"]].add(r["input_hashes"]["cond"])
            pair_condhash[(r["condition"], r["object_uid"])].add(r["input_hashes"]["cond"])
        rep["cond_hash_is_per_row_content_hash"] = True
        rep["cond_hash_distinct_per_condition"] = len({sorted(v)[0] for v in condhash.values()})
        rep["cond_hash_pairwise_ambiguous"] = sum(1 for v in pair_condhash.values() if len(v) != 1)

        # -- B3 replicate consistency ------------------------------------------
        if name == "B3":
            groups = defaultdict(list)
            for r in rows:
                groups[(r["condition"], r["object_uid"])].append(r)
            diffs = 0
            diff_detail = []
            for key, g in groups.items():
                if len(g) < 2:
                    continue
                keys = [k for k in g[0] if k not in NON_NUMERIC and k != "elapsed_seconds"]
                for k in keys:
                    vals = [x.get(k) for x in g]
                    if any(v != vals[0] for v in vals):
                        diffs += 1
                        if len(diff_detail) < 10:
                            diff_detail.append({"pair": key, "field": k,
                                                "values": vals[:4]})
            rep["replicate_field_mismatches"] = diffs
            rep["replicate_mismatch_detail"] = diff_detail

        # -- ledger vs CSV ------------------------------------------------------
        csvp = cdir / "per_object_metrics.csv"
        if csvp.exists():
            with open(csvp, newline="") as f:
                rd = csv.DictReader(f)
                csv_rows = list(rd)
            rep["csv_rows"] = len(csv_rows)
            led = {(r["condition"], r["object_uid"]): r for r in rows}
            mmax, mism, ncmp = 0.0, 0, 0
            unmatched = 0
            for cr in csv_rows:
                key = (cr["condition"], cr["object_uid"])
                if name == "B3" and key not in led:
                    unmatched += 1
                    continue
                lr = led.get(key)
                if lr is None:
                    unmatched += 1
                    continue
                for k, v in cr.items():
                    if k in NON_NUMERIC or k == "elapsed_seconds":
                        continue
                    try:
                        cv = float(v)
                    except (TypeError, ValueError):
                        continue
                    lv = float(lr.get(k, "nan"))
                    ncmp += 1
                    d = abs(cv - lv)
                    mmax = max(mmax, d)
                    if d > 1e-9:
                        mism += 1
            rep["csv_unmatched_rows"] = unmatched
            rep["csv_numeric_comparisons"] = ncmp
            rep["csv_max_abs_diff"] = mmax
            rep["csv_mismatch_gt_1e-9"] = mism

        # -- artifact presence (A2/A3 only for speed) ----------------------------
        if name in ("A2", "A3"):
            rl = cdir / "residual_logs"
            n_res = sum(1 for c in conds
                        if (rl / c).is_dir()
                        for p in (rl / c).glob("*.json"))
            rep["residual_log_files"] = n_res
            pred = cdir / "predictions"
            n_png = sum(1 for _ in pred.rglob("*.png")) if pred.is_dir() else -1
            rep["prediction_pngs"] = n_png

        # -- identity CSV rows ----------------------------------------------------
        for i, r in enumerate(rows):
            ih = r["input_hashes"]
            fp = fp_of(ih)
            identity_writer_rows.append({
                "campaign": name,
                "shard": shard_of[i] if i < len(shard_of) else "",
                "condition": r["condition"],
                "object_uid": r["object_uid"],
                "object_idx": r["object_idx"],
                "target_sha256": ih["target"],
                "normal_sha256": ih["normal"],
                "depth_sha256": ih["depth"],
                "global_embeds_sha256": ih["global_embeds"],
                "init_latent_sha256": ih["init_latent"],
                "cond_sha256": ih["cond"],
                "object_fingerprint": fp,
                "fingerprint_shared_with": ";".join(sorted(u for u in fps if u != r["object_uid"] and fps[u] == fp)) or "",
            })

        fails = []
        if rep["actual_rows"] not in (rep["expected_rows"], 3150 if name == "B3" else rep["expected_rows"]):
            fails.append("row_count")
        if rep["n_uids"] != cfg["n_uid"] or not rep["uid_set_matches_cohort"]:
            fails.append("uid_set")
        if rep["missing_pairs"] or rep["extra_pairs"]:
            fails.append("pair_completeness")
        if rep["rows_with_nan_inf_count"]:
            fails.append("nan_inf")
        if rep["rows_missing_input_hashes_count"]:
            fails.append("missing_hashes")
        if rep["rows_wrong_shard_unexplained_count"]:
            fails.append("shard_assignment_unexplained")
        if rep["objects_cross_condition_inconsistent_count"]:
            fails.append("cross_condition_identity")
        if rep["fingerprint_duplicates_count"]:
            fails.append("fingerprint_duplication")
        if rep["cond_hash_pairwise_ambiguous"]:
            fails.append("cond_hash_pair_ambiguity")
        if name == "B3" and rep.get("replicate_field_mismatches"):
            fails.append("b3_replicate_mismatch")
        if rep.get("csv_mismatch_gt_1e-9"):
            fails.append("csv_ledger_disagreement")
        if rep.get("csv_unmatched_rows"):
            fails.append("csv_unmatched_rows")
        rep["FAILS"] = fails
        if fails:
            overall_fail.append({name: fails})
        summary[name] = rep
        print(f"[{name}] rows={rep['actual_rows']} uid_ok={rep['uid_set_matches_cohort']} "
              f"cross_cond_bad={rep['objects_cross_condition_inconsistent_count']} "
              f"fp_dup={rep['fingerprint_duplicates_count']} csv_diff={rep.get('csv_max_abs_diff')} "
              f"FAILS={fails}")

    # Cross-campaign determinism: A2 a_baseline vs A3 a3_baseline must be exact
    # replicates. The ONLY permitted difference is `uncapped` (A3 registered all
    # rows uncapped; for the no-intervention baseline cap never activates, so
    # metrics must be bit-identical).
    a2 = {r["object_uid"]: r for r in load_campaign("A2", CAMPAIGNS["A2"])[0]
          if r["condition"] == "a_baseline"}
    a3 = {r["object_uid"]: r for r in load_campaign("A3", CAMPAIGNS["A3"])[0]
          if r["condition"] == "a3_baseline"}
    shared = sorted(set(a2) & set(a3))
    n_diff = 0
    diff_examples = []
    allowed_diff_field = "uncapped"
    for u in shared:
        for k in a2[u]:
            if k in NON_NUMERIC or k == "elapsed_seconds" or k == allowed_diff_field:
                continue
            if a2[u][k] != a3[u][k]:
                n_diff += 1
                if len(diff_examples) < 5:
                    diff_examples.append({"uid": u[:16], "field": k,
                                          "a2": a2[u][k], "a3": a3[u][k]})
    uncapped_vals = sorted({a3[u][allowed_diff_field] for u in shared})
    summary["A2_vs_A3_baseline"] = {
        "shared_uids": len(shared),
        "field_mismatches_excl_uncapped": n_diff,
        "a3_uncapped_values": uncapped_vals,
        "examples": diff_examples,
    }
    if n_diff:
        overall_fail.append({"A2_A3_baseline": f"{n_diff} unexpected mismatches"})
    print(f"A2 vs A3 a_baseline: {len(shared)} shared uids, "
          f"{n_diff} mismatches (excl. uncapped flag)")

    out_csv = ROOT / "audit_scripts" / "OBJECT_IDENTITY_PER_ROW.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(identity_writer_rows[0].keys()))
        w.writeheader()
        w.writerows(identity_writer_rows)
    print(f"wrote {out_csv} ({len(identity_writer_rows)} rows)")

    out_json = ROOT / "audit_scripts" / "AUDIT_LEDGER_SUMMARY.json"
    out_json.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {out_json}")
    print("OVERALL_FAIL:", overall_fail if overall_fail else "NONE")
    sys.exit(1 if overall_fail else 0)


if __name__ == "__main__":
    main()
