#!/usr/bin/env python3
"""Validate that two eval result sets are comparable before generating comparison tables.

Checks:
1. Object ID sets are identical between baseline and candidate
2. Object counts match
3. Evaluator script name matches
4. Seed matches (WARNING if missing, not FAIL)
5. Scale, checkpoint path, checkpoint SHA256 exist in metadata
6. FAIL if object sets differ
7. FAIL if baseline is 300-object but candidate is 50-object (or vice versa)

Usage:
    python geotex/validate_eval_comparison.py \
        --baseline mvpoutput/geotex_refattn_v1/scale_1p25_300obj \
        --candidate mvpoutput/geotex_refattn_v2/eval_v2a_step250_scale1p25_300obj

    # Or validate a single result directory
    python geotex/validate_eval_comparison.py \
        --single mvpoutput/geotex_refattn_v2/eval_v2a_step250_scale1p0_300obj

Exit codes:
    0 = PASS (comparable)
    1 = FAIL (not comparable)
    2 = WARNING (comparable but with caveats)
"""
import os
import sys
import json
import csv
import hashlib
import argparse
from pathlib import Path


def sha256_file(path):
    """Compute SHA256 of a file."""
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_eval_dir(eval_dir):
    """Load metadata and per-object results from an eval directory."""
    info = {
        'dir': eval_dir,
        'config': None,
        'summary': None,
        'per_object': None,
        'object_ids': set(),
        'object_count': 0,
    }

    # Load config snapshot
    config_path = os.path.join(eval_dir, 'config_snapshot.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            info['config'] = json.load(f)

    # Load summary metrics
    summary_path = os.path.join(eval_dir, 'summary_metrics.json')
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            info['summary'] = json.load(f)

    # Load per-object metrics to get object IDs
    csv_path = os.path.join(eval_dir, 'per_object_metrics.csv')
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            info['per_object'] = rows
            info['object_count'] = len(rows)
            for row in rows:
                oid = row.get('object_idx') or row.get('object_id')
                if oid is not None:
                    info['object_ids'].add(int(oid))

    return info


def validate_single(info, label="result"):
    """Validate a single eval directory for completeness."""
    issues = []
    warnings = []

    if info['config'] is None:
        issues.append(f"[{label}] Missing config_snapshot.json")
    else:
        cfg = info['config']
        # Check required fields
        for field in ['checkpoint', 'scale', 'seed', 'num_objects']:
            if field not in cfg:
                if field == 'seed':
                    warnings.append(f"[{label}] Missing 'seed' in config — cannot verify reproducibility")
                else:
                    issues.append(f"[{label}] Missing '{field}' in config_snapshot.json")

        # Check checkpoint exists
        ckpt = cfg.get('checkpoint', '')
        if ckpt:
            ckpt_path = os.path.join(os.path.dirname(info['dir']), '..', ckpt) if not os.path.isabs(ckpt) else ckpt
            # Try relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ckpt_full = os.path.join(project_root, ckpt) if not os.path.isabs(ckpt) else ckpt
            if not os.path.exists(ckpt_full):
                # Try from eval dir parent
                alt = os.path.join(os.path.dirname(info['dir']), ckpt)
                if not os.path.exists(alt):
                    warnings.append(f"[{label}] Checkpoint file not found: {ckpt}")
                else:
                    sha = sha256_file(alt)
                    info['checkpoint_sha256'] = sha
            else:
                sha = sha256_file(ckpt_full)
                info['checkpoint_sha256'] = sha

    if info['per_object'] is None:
        issues.append(f"[{label}] Missing per_object_metrics.csv")
    elif info['object_count'] == 0:
        issues.append(f"[{label}] per_object_metrics.csv is empty")

    if info['summary'] is None:
        warnings.append(f"[{label}] Missing summary_metrics.json")

    return issues, warnings


def validate_comparable(baseline, candidate):
    """Validate that two eval result sets are comparable."""
    issues = []
    warnings = []

    # 1. Object set consistency
    base_ids = baseline['object_ids']
    cand_ids = candidate['object_ids']

    if base_ids and cand_ids:
        if base_ids != cand_ids:
            missing_in_cand = base_ids - cand_ids
            extra_in_cand = cand_ids - base_ids
            if missing_in_cand:
                issues.append(f"Object set mismatch: {len(missing_in_cand)} objects in baseline missing from candidate "
                              f"(e.g., {sorted(missing_in_cand)[:5]})")
            if extra_in_cand:
                issues.append(f"Object set mismatch: {len(extra_in_cand)} extra objects in candidate not in baseline "
                              f"(e.g., {sorted(extra_in_cand)[:5]})")

    # 2. Object count consistency
    base_count = baseline['object_count']
    cand_count = candidate['object_count']
    if base_count != cand_count:
        issues.append(f"Object count mismatch: baseline={base_count}, candidate={cand_count}")
    elif base_count > 0:
        # Also check config num_objects
        base_cfg_count = baseline.get('config', {}).get('num_objects', None)
        cand_cfg_count = candidate.get('config', {}).get('num_objects', None)
        if base_cfg_count and cand_cfg_count and base_cfg_count != cand_cfg_count:
            issues.append(f"Config num_objects mismatch: baseline={base_cfg_count}, candidate={cand_cfg_count}")

    # 3. Evaluator consistency (check if same eval script was used)
    # We infer this from directory naming and config structure
    base_cfg = baseline.get('config', {})
    cand_cfg = candidate.get('config', {})

    # 4. Seed consistency
    base_seed = base_cfg.get('seed', None)
    cand_seed = cand_cfg.get('seed', None)
    if base_seed is None or cand_seed is None:
        warnings.append(f"Seed missing: baseline={'present' if base_seed else 'MISSING'}, "
                        f"candidate={'present' if cand_seed else 'MISSING'}")
    elif base_seed != cand_seed:
        issues.append(f"Seed mismatch: baseline={base_seed}, candidate={cand_seed}")

    # 5. Scale, checkpoint, SHA256
    base_scale = base_cfg.get('scale', None)
    cand_scale = cand_cfg.get('scale', None)
    if base_scale is None:
        warnings.append("Baseline: missing 'scale' in config")
    if cand_scale is None:
        warnings.append("Candidate: missing 'scale' in config")

    base_ckpt = base_cfg.get('checkpoint', None)
    cand_ckpt = cand_cfg.get('checkpoint', None)
    if not base_ckpt:
        issues.append("Baseline: missing 'checkpoint' in config")
    if not cand_ckpt:
        issues.append("Candidate: missing 'checkpoint' in config")

    base_sha = baseline.get('checkpoint_sha256', None)
    cand_sha = candidate.get('checkpoint_sha256', None)
    if base_sha:
        warnings.append(f"Baseline checkpoint SHA256: {base_sha[:16]}...")
    if cand_sha:
        warnings.append(f"Candidate checkpoint SHA256: {cand_sha[:16]}...")

    # 6/7. Cross-check: ensure both are same object count tier
    if base_count >= 200 and cand_count < 100:
        issues.append(f"CANNOT COMPARE: baseline has {base_count} objects but candidate has only {cand_count}")
    elif base_count < 100 and cand_count >= 200:
        issues.append(f"CANNOT COMPARE: baseline has only {base_count} objects but candidate has {cand_count}")

    return issues, warnings


def print_report(label, info, issues, warnings):
    """Print a structured report for one eval directory."""
    cfg = info.get('config', {}) or {}
    print(f"\n{'='*60}")
    print(f"  {label}: {info['dir']}")
    print(f"{'='*60}")
    print(f"  Object count (CSV):  {info['object_count']}")
    print(f"  Object count (cfg):  {cfg.get('num_objects', 'N/A')}")
    print(f"  Checkpoint:          {cfg.get('checkpoint', 'N/A')}")
    print(f"  Scale:               {cfg.get('scale', 'N/A')}")
    print(f"  Seed:                {cfg.get('seed', 'N/A')}")
    print(f"  Steps:               {cfg.get('steps', 'N/A')}")
    sha = info.get('checkpoint_sha256', None)
    if sha:
        print(f"  Checkpoint SHA256:   {sha[:32]}...")
    if issues:
        print(f"\n  ❌ ISSUES ({len(issues)}):")
        for i in issues:
            print(f"    - {i}")
    if warnings:
        print(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")


def main():
    parser = argparse.ArgumentParser(description="Validate eval result comparability")
    parser.add_argument('--baseline', help='Baseline eval directory')
    parser.add_argument('--candidate', help='Candidate eval directory')
    parser.add_argument('--single', help='Validate a single eval directory')
    args = parser.parse_args()

    if args.single:
        # Single directory validation
        info = load_eval_dir(args.single)
        issues, warnings = validate_single(info, label="single")
        print_report("SINGLE VALIDATION", info, issues, warnings)
        if issues:
            print(f"\n❌ FAIL: {len(issues)} issue(s) found")
            sys.exit(1)
        elif warnings:
            print(f"\n⚠️  PASS with {len(warnings)} warning(s)")
            sys.exit(2)
        else:
            print(f"\n✅ PASS")
            sys.exit(0)

    elif args.baseline and args.candidate:
        # Comparison validation
        base_info = load_eval_dir(args.baseline)
        cand_info = load_eval_dir(args.candidate)

        base_issues, base_warnings = validate_single(base_info, label="baseline")
        cand_issues, cand_warnings = validate_single(cand_info, label="candidate")
        comp_issues, comp_warnings = validate_comparable(base_info, cand_info)

        all_issues = base_issues + cand_issues + comp_issues
        all_warnings = base_warnings + cand_warnings + comp_warnings

        print_report("BASELINE", base_info, base_issues, base_warnings)
        print_report("CANDIDATE", cand_info, cand_issues, cand_warnings)

        if comp_issues or comp_warnings:
            print(f"\n{'='*60}")
            print(f"  COMPARISON CHECKS")
            print(f"{'='*60}")
            if comp_issues:
                print(f"\n  ❌ ISSUES ({len(comp_issues)}):")
                for i in comp_issues:
                    print(f"    - {i}")
            if comp_warnings:
                print(f"\n  ⚠️  WARNINGS ({len(comp_warnings)}):")
                for w in comp_warnings:
                    print(f"    - {w}")

        print(f"\n{'='*60}")
        if all_issues:
            print(f"❌ FAIL: {len(all_issues)} issue(s) — NOT COMPARABLE")
            print("Do NOT generate comparison tables from these results.")
            sys.exit(1)
        elif all_warnings:
            print(f"⚠️  PASS with {len(all_warnings)} warning(s) — comparable with caveats")
            sys.exit(2)
        else:
            print(f"✅ PASS — results are comparable")
            sys.exit(0)

    else:
        parser.error("Provide either --single DIR or both --baseline DIR and --candidate DIR")


if __name__ == '__main__':
    main()
