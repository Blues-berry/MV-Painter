#!/usr/bin/env python3
"""Check stored Holm adjustments against the raw p-values in frozen families."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
SOURCE = ROOT / "final/round2/scientific_validation_v3/formal"
OUT_JSON = ROOT / "1006/data/derived/holm_family_audit.json"
OUT_MD = ROOT / "1006/evidence/audits/FORMAL_HOLM_FAMILY_AUDIT_20261006.md"


def holm(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    running = 0.0
    n = len(values)
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (n - rank) * values[index]))
        adjusted[index] = running
    return adjusted


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-10)


def pairwise_matches(family_path: Path, family_root: dict, test_key: str,
                     family_test: dict, raw_p: float) -> list[str]:
    expected_n = family_test.get("n", family_root.get("n", family_root.get("n_objects")))
    expected_mean = family_test.get("mean_delta", family_test.get("mean"))
    expected_ci = family_test.get("ci95", family_test.get("ci"))
    if expected_mean is None or expected_ci is None:
        linked_files = {
            "H3_LLH-HLL": "paired_layer_llh_minus_layer_hll.json",
            "H3_LLH-LLL": "paired_layer_llh_minus_a3_baseline.json",
            "HLL-LLL_exploratory": "paired_layer_hll_minus_a3_baseline_exploratory.json",
        }
        linked_name = next((value for key, value in linked_files.items() if test_key.startswith(key)), None)
        metric = "fg_psnr" if "fg_psnr" in test_key else "fg_lpips" if "fg_lpips" in test_key else None
        linked_path = family_path.parent / linked_name if linked_name else None
        if linked_path and metric and linked_path.is_file():
            try:
                linked = json.loads(linked_path.read_text()).get("tests", {}).get(metric, {})
                linked_p = linked.get("p_bootstrap", linked.get("p"))
                if linked_p is not None and close(float(linked_p), raw_p):
                    return [str(linked_path.relative_to(ROOT))]
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
    if expected_n is None or expected_mean is None or expected_ci is None:
        return []
    matches = []
    for candidate in family_path.parent.glob("*.json"):
        if candidate == family_path or candidate.name.startswith("HOLM"):
            continue
        try:
            data = json.loads(candidate.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for metric_test in data.get("tests", {}).values():
            n = metric_test.get("n", data.get("n", data.get("n_objects", data.get("n_common"))))
            mean = metric_test.get("mean_delta", metric_test.get("mean"))
            ci = metric_test.get("ci95", metric_test.get("ci"))
            p = metric_test.get("p_bootstrap", metric_test.get("p"))
            if n is None or mean is None or ci is None or p is None:
                continue
            if (int(n) == int(expected_n) and close(float(mean), float(expected_mean))
                    and len(ci) == 2 and close(float(ci[0]), float(expected_ci[0]))
                    and close(float(ci[1]), float(expected_ci[1])) and close(float(p), raw_p)):
                matches.append(str(candidate.relative_to(ROOT)))
    return sorted(set(matches))


def main() -> None:
    families = []
    errors = []
    for path in sorted(SOURCE.rglob("HOLM*.json")):
        data = json.loads(path.read_text())
        tests = data.get("tests", {})
        if not tests:
            errors.append({"file": str(path.relative_to(ROOT)), "error": "no tests"})
            continue
        declared_size = data.get("family_size")
        if declared_size is not None and int(declared_size) != len(tests):
            errors.append({"file": str(path.relative_to(ROOT)),
                           "error": f"declared family size {declared_size} != {len(tests)} tests"})
        keys = list(tests)
        raw_values = []
        supplied = []
        rows = []
        for key in keys:
            row = tests[key]
            raw = row.get("p", row.get("p_raw_upper_bound", row.get("p_bootstrap")))
            adj = row.get("p_holm", row.get("p_holm_upper_bound"))
            if raw is None or adj is None:
                errors.append({"file": str(path.relative_to(ROOT)), "test": key,
                               "error": "missing raw or Holm p-value"})
                continue
            raw_values.append(float(raw))
            supplied.append(float(adj))
            linked = pairwise_matches(path, data, key, row, float(raw))
            if len(linked) != 1:
                errors.append({"file": str(path.relative_to(ROOT)), "test": key,
                               "error": f"expected one matching saved paired result, found {len(linked)}",
                               "matches": linked})
            rows.append({"test": key, "source_pairwise_file": linked[0] if len(linked) == 1 else None,
                         "p_raw_or_upper_bound": float(raw),
                         "p_holm_or_upper_bound": float(adj),
                         "reject_holm_0_05": bool(adj <= data.get("alpha", 0.05))})
        computed = holm(raw_values)
        mismatches = []
        for row, expected in zip(rows, computed):
            row["recomputed_p_holm_or_upper_bound"] = expected
            row["matches"] = close(row["p_holm_or_upper_bound"], expected)
            if not row["matches"]:
                mismatches.append(row["test"])
            if row["reject_holm_0_05"] != (expected <= data.get("alpha", 0.05)):
                mismatches.append(row["test"] + " reject flag")
        if mismatches:
            errors.append({"file": str(path.relative_to(ROOT)),
                           "error": "Holm values/decisions do not reproduce",
                           "tests": sorted(set(mismatches))})
        families.append({
            "file": str(path.relative_to(ROOT)),
            "family": data.get("family"),
            "cohort": data.get("cohort"),
            "family_size_declared": data.get("family_size", len(tests)),
            "family_size_observed": len(tests),
            "alpha": data.get("alpha", 0.05),
            "p_floor_note": data.get("p_floor_note"),
            "tests": rows,
            "status": "PASS" if not mismatches else "FAIL",
        })

    result = {"status": "PASS" if not errors else "FAIL",
              "family_count": len(families), "test_count": sum(len(f["tests"]) for f in families),
              "families": families, "errors": errors}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Frozen Holm-family audit — 2026-10-06", "",
        "This audit recomputes each stored Holm-Bonferroni adjustment from the",
        "raw p-value (or the explicitly stored reporting-floor upper bound) in",
        "the corresponding frozen family file. It does not pool cohorts or alter",
        "the registered family definitions. Direction is audited separately",
        "from paired raw rows in `data/derived/formal_pairwise_sign_audit.json`.", "",
        f"**Status: {result['status']}** — {result['family_count']} families; {result['test_count']} tests.", "",
        "| Family file | Cohort | Tests | Holm recomputation |", "|---|---:|---:|---|",
    ]
    for family in families:
        lines.append(f"| `{family['file']}` | {family.get('cohort') or 'see file'} | "
                     f"{family['family_size_observed']} | {family['status']} |")
    lines += ["", "## Test-level values", "", "| Family | Test | Paired result source | raw p / bound | Holm p / bound | Holm decision |",
              "|---|---|---|---:|---:|---|"]
    for family in families:
        for row in family["tests"]:
            source_name = Path(row["source_pairwise_file"]).name if row["source_pairwise_file"] else "not linked"
            lines.append(f"| `{Path(family['file']).name}` | `{row['test']}` | `{source_name}` | "
                         f"{row['p_raw_or_upper_bound']:.6g} | "
                         f"{row['p_holm_or_upper_bound']:.6g} | "
                         f"{'reject' if row['reject_holm_0_05'] else 'retain'} |")
    if errors:
        lines += ["", "## Errors", "", "```json", json.dumps(errors, indent=2), "```"]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": result["status"], "families": result["family_count"],
                      "tests": result["test_count"], "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
