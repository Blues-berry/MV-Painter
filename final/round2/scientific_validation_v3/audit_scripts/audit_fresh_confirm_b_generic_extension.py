#!/usr/bin/env python3
"""Integrity gate for the separately locked B generic-schedule extension."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
sys.path.insert(0, str(V3 / "audit_scripts"))
from audit_fresh_confirm_b_integrity import METRIC_FIELDS, digest, read_json  # noqa: E402

RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005"
CORE = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
COHORT = V3 / "fresh_confirm_b"
DATA_ROOT = ROOT / "data/fresh_confirm_v3_renders"
UID_SHA = "f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28"
MANIFEST_SHA = "c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050"
RUNNER_SHA = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"
CONFIG_SHA = "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b"
CHECKPOINT_SHA = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
CONDITIONS = (
    "gen_linear", "gen_cosine_bump", "gen_trapezoid", "gen_gaussian_peak",
    "gen_linear_bm", "gen_cosine_bump_bm", "gen_trapezoid_bm", "gen_gaussian_peak_bm",
)
REQUIRED_SOURCES = {
    "runner", "generation_logic", "adapter_wrapper", "data_utils",
    "metric_implementation", "train_util_dataset_factory", "metric_package",
    "metric_image_functions", "metric_mask_functions", "metric_region_functions",
    "metric_crop_functions",
}


def fail(errors: list[str]) -> None:
    unique = sorted(set(errors))
    report = [
        "# FRESH_CONFIRM_B generic-extension integrity gate", "",
        "**FRESH_CONFIRM_B_GENERIC_EXTENSION_INTEGRITY = FAIL**", "",
        "No condition means or contrasts were computed or reported.", "",
        *[f"- {e}" for e in unique[:40]],
    ]
    if len(unique) > 40:
        report.append(f"- … {len(unique) - 40} additional distinct issue(s) omitted.")
    report += ["", "Repair the extension under its separate lock before opening its outcomes.", ""]
    (V3 / "B_GENERIC_EXTENSION_INTEGRITY_GATE.md").write_text("\n".join(report))
    raise SystemExit("Generic-extension integrity gate failed; extension outcomes remain blinded.")


def main() -> None:
    errors: list[str] = []
    uids = [x.strip() for x in (COHORT / "fresh_confirm_B_150.txt").read_text().splitlines() if x.strip()]
    if len(uids) != 150 or len(set(uids)) != 150 or uids != sorted(uids):
        raise SystemExit("B extension remains incomplete or UID list is invalid; no outcomes inspected.")
    if digest(COHORT / "fresh_confirm_B_150.txt") != UID_SHA:
        errors.append("Frozen UID-list checksum mismatch.")
    if digest(COHORT / "FRESH_CONFIRM_B_MANIFEST.json") != MANIFEST_SHA:
        errors.append("Frozen input-manifest checksum mismatch.")
    expected = {(uid, condition) for uid in uids for condition in CONDITIONS}
    rows: dict[tuple[str, str], dict] = {}
    counts = {}
    for shard in (0, 1):
        path = RUN / f"rows_shard{shard}.json"
        if not path.is_file():
            raise SystemExit(f"B extension remains incomplete: shard {shard} ledger missing.")
        shard_rows = read_json(path)
        counts[shard] = len(shard_rows)
        if counts[shard] != 600:
            raise SystemExit(f"B extension remains incomplete: shard counts {counts}; expected 600 each.")
        for row in shard_rows:
            uid, condition = row.get("object_uid"), row.get("condition")
            key = (uid, condition)
            if key in rows:
                errors.append(f"Duplicate raw key {key}.")
                continue
            rows[key] = row
            if uid not in uids or condition not in CONDITIONS:
                errors.append(f"Unexpected raw key {key}.")
                continue
            idx = uids.index(uid)
            if row.get("object_idx") != idx or idx % 2 != shard or row.get("seed_base") != 42:
                errors.append(f"Object index/shard/seed-base mismatch for {key}.")
            if row.get("uncapped") is not False:
                errors.append(f"Unexpected cap-bypass flag for {key}.")
            if not isinstance(row.get("input_hashes"), dict):
                errors.append(f"Missing input hashes for {key}.")
            for metric in METRIC_FIELDS:
                try:
                    if not math.isfinite(float(row[metric])):
                        errors.append(f"Non-finite metric at {key}/{metric}.")
                except (KeyError, TypeError, ValueError):
                    errors.append(f"Missing/non-numeric metric at {key}/{metric}.")
    if set(rows) != expected:
        errors.append(f"Raw key coverage is {len(set(rows) & expected)}/1200.")

    core_hashes = {}
    for shard in (0, 1):
        for row in read_json(CORE / f"rows_shard{shard}.json"):
            core_hashes.setdefault(row["object_uid"], row["input_hashes"])
    for uid in uids:
        hashes = [rows[(uid, c)].get("input_hashes") for c in CONDITIONS if (uid, c) in rows]
        if len(hashes) == len(CONDITIONS) and (any(h != hashes[0] for h in hashes) or hashes[0] != core_hashes.get(uid)):
            errors.append(f"Input fingerprints differ from the main B run for {uid}.")

    manifests = []
    for shard in (0, 1):
        path = RUN / f"run_manifest_shard{shard}.json"
        if not path.is_file():
            errors.append(f"Missing shard {shard} completion manifest.")
            continue
        m = read_json(path)
        manifests.append(m)
        if m.get("status") != "complete" or m.get("row_count") != 600:
            errors.append(f"Shard {shard} completion status/row count mismatch.")
        if m.get("shard") != shard or m.get("num_shards") != 2:
            errors.append(f"Shard {shard} identity mismatch.")
        if m.get("runner_script_sha256") != RUNNER_SHA or m.get("config_sha256") != CONFIG_SHA:
            errors.append(f"Shard {shard} runner/config mismatch.")
        if m.get("checkpoint_sha256") != CHECKPOINT_SHA or m.get("object_list_sha256") != UID_SHA:
            errors.append(f"Shard {shard} checkpoint/UID-list mismatch.")
        if m.get("effective_data_roots") != [str(DATA_ROOT.resolve())]:
            errors.append(f"Shard {shard} effective data-root mismatch.")
        if m.get("conditions") != sorted(CONDITIONS) or m.get("residuals_only") is not False:
            errors.append(f"Shard {shard} condition registry or mode mismatch.")
        specs = m.get("condition_specs", {})
        if set(specs) != set(CONDITIONS):
            errors.append(f"Shard {shard} condition-spec registry mismatch.")
        else:
            for condition, spec in specs.items():
                trace = spec.get("scale_trace_requested", [])
                if bool(spec.get("uncapped")) or len(trace) != 50:
                    errors.append(f"Shard {shard} scale trace/cap semantics invalid for {condition}.")
                for step in trace:
                    if not isinstance(step, dict) or set(step) != {"deep", "middle", "shallow"}:
                        errors.append(f"Malformed scale trace in shard {shard}/{condition}.")
        sources = m.get("code_source_sha256", {})
        if set(sources) != REQUIRED_SOURCES:
            errors.append(f"Shard {shard} source-hash registry mismatch.")
        for name, item in sources.items():
            src = Path(item.get("path", ""))
            if not src.is_file() or digest(src) != item.get("sha256"):
                errors.append(f"Source bytes differ from run manifest for {name}, shard {shard}.")
    if len(manifests) == 2 and manifests[0].get("condition_specs") != manifests[1].get("condition_specs"):
        errors.append("Shard manifests disagree on condition scale traces.")

    pred_count = residual_count = 0
    expected_names = set(uids)
    caps = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
    for condition in CONDITIONS:
        pred_dir = RUN / "predictions" / condition
        log_dir = RUN / "residual_logs" / condition
        preds = list(pred_dir.glob("*.png")) if pred_dir.is_dir() else []
        logs = list(log_dir.glob("*.json")) if log_dir.is_dir() else []
        if {p.stem for p in preds} != expected_names:
            errors.append(f"Prediction identity set incomplete for {condition}.")
        if {p.stem for p in logs} != expected_names:
            errors.append(f"Residual-log identity set incomplete for {condition}.")
        pred_count += len(preds)
        residual_count += len(logs)
        for p in preds:
            try:
                with Image.open(p) as im:
                    if im.format != "PNG" or im.width % 256 or im.height % 256 or im.width * im.height != 6 * 256 * 256:
                        raise ValueError("invalid six-view PNG dimensions")
                    im.verify()
            except Exception:
                errors.append(f"Invalid prediction PNG {condition}/{p.name}.")
        spec = manifests[0].get("condition_specs", {}).get(condition, {}) if manifests else {}
        trace = spec.get("scale_trace_requested", [])
        for p in logs:
            try:
                log = read_json(p)
                if set(log) != {str(i) for i in range(50)}:
                    raise ValueError("expected 50 step records")
                for step_idx in range(50):
                    if not isinstance(log[str(step_idx)], dict) or not log[str(step_idx)]:
                        raise ValueError("empty step residuals")
                    for entry in log[str(step_idx)].values():
                        group = entry["depth"]
                        if group not in caps or float(entry["scale"]) != float(trace[step_idx][group]):
                            raise ValueError("logged scale differs from manifest")
                        if float(entry["eff_scale"]) != min(float(entry["scale"]), caps[group]):
                            raise ValueError("logged native cap differs")
                        if any(not math.isfinite(float(entry[k])) for k in ("l2", "mean_abs", "max_abs", "scale", "eff_scale")):
                            raise ValueError("non-finite residual summary")
            except Exception:
                errors.append(f"Invalid residual log {condition}/{p.name}.")

    combined = RUN / "per_object_metrics.csv"
    csv_rows = {}
    if not combined.is_file():
        errors.append("Missing rebuilt combined per-object CSV.")
    else:
        with combined.open(newline="") as f:
            for row in csv.DictReader(f):
                key = (row["object_uid"], row["condition"])
                if key in csv_rows:
                    errors.append(f"Duplicate combined CSV key {key}.")
                csv_rows[key] = row
        if set(csv_rows) != expected:
            errors.append("Rebuilt combined CSV key set differs from frozen 1,200 rows.")
        for key, row in csv_rows.items():
            raw = rows.get(key)
            if raw is None:
                errors.append(f"Combined CSV key absent from ledger {key}.")
                continue
            for metric in METRIC_FIELDS:
                try:
                    if float(row[metric]) != float(raw[metric]):
                        errors.append(f"CSV/ledger mismatch at {key}/{metric}.")
                        break
                except (KeyError, TypeError, ValueError):
                    errors.append(f"CSV metric missing at {key}/{metric}.")
                    break
    if pred_count != 1200 or residual_count != 1200:
        errors.append(f"Prediction/residual counts are {pred_count}/{residual_count}, expected 1200 each.")

    if errors:
        fail(errors)
    report = [
        "# FRESH_CONFIRM_B generic-extension integrity gate", "",
        "**FRESH_CONFIRM_B_GENERIC_EXTENSION_INTEGRITY = PASS**", "",
        "Pre-analysis checks only; no condition means or contrasts were computed.", "",
        "| Check | Result |", "|---|---:|",
        "| Frozen objects | 150/150 |",
        f"| Unique extension rows | {len(rows)}/1200 |",
        f"| Shard rows | {counts[0]} / {counts[1]} |",
        "| Shared input fingerprints match main B | 150/150 |",
        "| Prediction PNGs / 50-step residual logs | 1200/1200 each |",
        "| Runner/config/checkpoint/data-root/conditions/source hashes | MATCH |",
        "| Rebuilt CSV to raw-ledger numeric fields | EXACT |",
        "| Duplicate/missing/non-finite rows | 0/0/0 |", "",
    ]
    (V3 / "B_GENERIC_EXTENSION_INTEGRITY_GATE.md").write_text("\n".join(report))
    print("FRESH_CONFIRM_B_GENERIC_EXTENSION_INTEGRITY=PASS; no outcome statistics were computed or printed.")


if __name__ == "__main__":
    main()
