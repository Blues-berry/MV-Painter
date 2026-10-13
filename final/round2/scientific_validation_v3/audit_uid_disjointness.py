#!/usr/bin/env python3
"""Phase III cohort audit — UID disjointness against all historical cohorts.

Reads every canonical exclusion source, normalizes identifiers, and computes
the set of locally available Objaverse GLBs that are disjoint from ALL of them.
Selection itself happens later (deterministic seed 20261002) after technical
validation; this script only performs the disjointness audit.
"""
import csv
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = "/4T/CXY/MV-Painter"
OUT_DIR = os.path.join(ROOT, "final/round2/scientific_validation_v3")

REPO = ROOT
GLB_DIRS = [
    "/home/ubuntu/.objaverse/hf-objaverse-v1/glbs",
    "/home/ubuntu/.objaverse/smithsonian/objects",
]
RENDERED_FULL = os.path.join(REPO, "data/train_data/rendered_full")


def norm(uid: str) -> str:
    """Normalize an identifier: lowercase, strip, remove dashes/underscores."""
    return re.sub(r"[-_]", "", uid.strip().lower())


def load_lines(path, label, bucket):
    n = 0
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            bucket.add(norm(s))
            n += 1
    print(f"  {label}: {n} entries")
    return n


def main():
    excluded = set()
    sources = OrderedDict()

    def add(label, path, loader=load_lines):
        sources[label] = path
        loader(path, label, excluded)

    print("== Loading exclusion sources ==")
    add("main_train_1118", os.path.join(REPO, "mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt"))
    add("fac_train_1706", os.path.join(REPO, "data/train_data/rendered_full/train_objects_2000.txt"))
    add("fac_train_1200", os.path.join(REPO, "data/train_data/rendered_full/train_objects_1200.txt"))
    add("old_eval_300", os.path.join(REPO, "data/train_data/rendered_full/test_objects_300.txt"))
    add("eval300_clean_v2", os.path.join(REPO, "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"))
    add("probe24_clean_v2", os.path.join(REPO, "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"))
    add("strict276_clean_v2", os.path.join(REPO, "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"))
    add("replacement_pool_189", os.path.join(REPO, "final/round2/clean_dataset_v2/replacement_candidate_pool_189.txt"))
    add("old_to_new_mapping_old", os.path.join(REPO, "final/round2/clean_dataset_v2/old_to_new_uid_mapping.csv"),
        lambda p, l, b: _load_csv_uids(p, l, b, ["old_uid", "old", "uid_old"]))
    add("bake12_manifest", os.path.join(REPO, "final/round2/main_adapter_clean_v2/exact_baking_cohort_manifest.csv"),
        lambda p, l, b: _load_csv_uids(p, l, b, ["uid", "object_uid", "source_uid"]))
    for tag in ("exact_76", "exact_75"):
        add(f"mvdiffusion_holdout_{tag}", os.path.join(REPO, f"final/round2/mvdiffusion/data_manifest_holdout_{tag}.json"),
            _load_json_manifest)

    # Safety bucket: any object ever rendered into the dataset tree
    rendered_dirs = set()
    if os.path.isdir(RENDERED_FULL):
        for name in os.listdir(RENDERED_FULL):
            rendered_dirs.add(norm(name))
    print(f"  rendered_full dirs: {len(rendered_dirs)}")

    print(f"\nTotal normalized excluded identifiers: {len(excluded)}")

    # Inventory local GLBs
    glbs = OrderedDict()
    for gd in GLB_DIRS:
        if not os.path.isdir(gd):
            print(f"WARNING: GLB dir missing: {gd}")
            continue
        for dirpath, _, filenames in os.walk(gd):
            for fn in filenames:
                if fn.lower().endswith(".glb"):
                    uid = fn[:-4]
                    glbs[uid] = os.path.join(dirpath, fn)
    print(f"Local GLBs inventoried: {len(glbs)}")

    def source_of(uid):
        if uid.startswith(norm("hf-objaverse")):
            return "hf"
        if "/smithsonian/" in uid:
            return "smithsonian"
        return "other"

    fresh, clashes = [], []
    for uid, path in glbs.items():
        n = norm(uid)
        hit = []
        if n in excluded:
            hit.append("named_exclusion")
        if n in rendered_dirs:
            hit.append("rendered_full_dir")
        if hit:
            clashes.append((uid, ",".join(hit)))
        else:
            fresh.append(uid)

    src = lambda u: "hf" if "/hf-objaverse-v1/" in glbs[u] else "smithsonian"
    n_hf = sum(1 for u in fresh if src(u) == "hf")
    n_sm = sum(1 for u in fresh if src(u) == "smithsonian")
    print(f"\nDisjoint fresh candidates: {len(fresh)} (hf={n_hf}, smithsonian={n_sm})")
    print(f"Clashing (excluded) GLBs locally: {len(clashes)}")

    # Persist audit JSON
    out = {
        "audit": "phase3_uid_disjointness",
        "excluded_identifier_count_normalized": len(excluded),
        "rendered_full_dir_count": len(rendered_dirs),
        "local_glb_count": len(glbs),
        "fresh_disjoint_count": len(fresh),
        "fresh_hf": n_hf,
        "fresh_smithsonian": n_sm,
        "clash_count": len(clashes),
        "sources": sources,
        "fresh_uids": sorted(fresh),
        "clashes": sorted(clashes),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "uid_disjointness_audit.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(OUT_DIR, "fresh_disjoint_candidates.txt"), "w") as f:
        for u in sorted(fresh):
            f.write(u + "\n")
    print(f"\nWrote {OUT_DIR}/uid_disjointness_audit.json")
    print(f"Wrote {OUT_DIR}/fresh_disjoint_candidates.txt")


def _load_csv_uids(path, label, bucket, uid_col_candidates):
    n = 0
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        cols = [c for c in (rdr.fieldnames or [])]
        uid_col = next((c for c in uid_col_candidates if c in cols), None)
        if uid_col is None:
            # fall back: any column whose name contains 'uid'
            uid_col = next((c for c in cols if "uid" in c.lower()), None)
        if uid_col is None:
            print(f"  {label}: NO uid column found (cols={cols})")
            return
        for row in rdr:
            v = (row.get(uid_col) or "").strip()
            if v:
                bucket.add(norm(v))
                n += 1
    print(f"  {label}: {n} entries (col={uid_col})")


def _load_json_manifest(path, label, bucket):
    with open(path) as f:
        data = json.load(f)
    n = 0

    def walk(node):
        nonlocal n
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("source_uid", "uid", "object_uid") and isinstance(v, str):
                    bucket.add(norm(v))
                    n += 1
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    print(f"  {label}: {n} entries")


if __name__ == "__main__":
    sys.exit(main())
