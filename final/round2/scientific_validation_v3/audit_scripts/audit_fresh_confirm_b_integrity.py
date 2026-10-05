#!/usr/bin/env python3
"""Pre-unblinding completeness and provenance gate for FRESH_CONFIRM_B.

This gate reports counts, hash integrity, and finite-value status only. It does
not calculate or print condition means or contrasts. It refuses to inspect
metrics until both frozen shards contain all expected object-condition rows.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
COHORT_DIR = V3 / "fresh_confirm_b"
DATA_ROOT = ROOT / "data/fresh_confirm_v3_renders"
EXPECTED_RUNNER = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"
EXPECTED_CONFIG = "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b"
EXPECTED_CHECKPOINT = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
EXPECTED_MANIFEST = "c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050"
EXPECTED_UIDS = "f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28"
CONDITIONS = (
    "a3_baseline",
    *(f"a3_{layer}_W{window}" for layer in ("deep", "middle", "shallow") for window in range(1, 6)),
    "boundary_late_onset_20_60_20", "boundary_late_onset_30_40_30",
    "boundary_late_onset_34_32_34", "boundary_late_onset_40_20_40",
    "native_gfl", "native_gfh", "native_gc3",
    "true_global_0p80", "true_global_1p25", "true_global_1p675", "true_global_2p50",
    "lfm_exact", "layer_llh", "layer_hll",
)
METRIC_FIELDS = {
    "bg_psnr", "bgwhite_lpips", "bgwhite_psnr", "bgwhite_ssim", "crop_area",
    "crop_lpips", "crop_psnr", "crop_ssim", "edge_fscore", "edge_psnr",
    "edge_ssim", "fg_brightness_std", "fg_color_entropy", "fg_grad_mag",
    "fg_hf_energy", "fg_lap_var", "fg_lpips", "fg_mask_corr", "fg_psnr",
    "fg_rgb_std", "fg_ssim", "full_lpips", "full_psnr", "full_ssim",
    "gt_fg_grad_mag", "gt_fg_hf_energy", "gt_fg_lap_var", "gt_fg_rgb_std",
    "nef_ssim",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def fail(errors: list[str]) -> None:
    unique_errors = sorted(set(errors))
    shown_errors = unique_errors[:40]
    report = [
        "# FRESH_CONFIRM_B formal integrity gate", "",
        "**FRESH_CONFIRM_B_FORMAL_INTEGRITY = FAIL**", "",
        "The pre-unblinding checks found the following integrity issue(s). No condition means or contrasts were computed or reported.", "",
    ] + [f"- {e}" for e in shown_errors]
    if len(unique_errors) > len(shown_errors):
        report += [f"- … {len(unique_errors) - len(shown_errors)} additional distinct issue(s) omitted."]
    report += ["", "Repair or rerun affected rows under the frozen protocol before opening the outcome analysis.", ""]
    (V3 / "B_FORMAL_INTEGRITY_GATE.md").write_text("\n".join(report))
    raise SystemExit("Integrity gate failed; outcomes remain blinded.")


def main() -> None:
    errors: list[str] = []
    uids = [line.strip() for line in (COHORT_DIR / "fresh_confirm_B_150.txt").read_text().splitlines() if line.strip()]
    if len(uids) != 150 or len(set(uids)) != 150 or uids != sorted(uids):
        errors.append("Frozen UID list is not 150 unique sorted IDs.")
    if digest(COHORT_DIR / "fresh_confirm_B_150.txt") != EXPECTED_UIDS:
        errors.append("Frozen UID-list SHA256 does not match its pre-output lock.")
    if digest(COHORT_DIR / "FRESH_CONFIRM_B_MANIFEST.json") != EXPECTED_MANIFEST:
        errors.append("Recursive input-manifest SHA256 does not match its pre-output lock.")
    cohort_manifest = read_json(COHORT_DIR / "FRESH_CONFIRM_B_MANIFEST.json")
    manifest_by_uid = {o["source_uid"]: o for o in cohort_manifest["objects"]}
    if set(manifest_by_uid) != set(uids) or len(cohort_manifest["objects"]) != 150:
        errors.append("Cohort manifest UID set differs from the frozen 150-object list.")

    expected_keys = {(uid, c) for uid in uids for c in CONDITIONS}
    rows = []
    shard_counts = {}
    for shard in (0, 1):
        path = RUN / f"rows_shard{shard}.json"
        if not path.is_file():
            errors.append(f"Missing raw ledger for shard {shard}.")
            continue
        shard_rows = read_json(path)
        shard_counts[shard] = len(shard_rows)
        rows.extend((shard, r) for r in shard_rows)
    if any(count != 2250 for count in shard_counts.values()):
        # This is deliberately checked before examining any condition metrics.
        raise SystemExit(f"B remains incomplete: shard row counts {shard_counts}; expected 2,250 each. No outcomes were inspected.")
    if len(rows) != 4500:
        raise SystemExit(f"B remains incomplete: {len(rows)} total raw rows; expected 4,500. No outcomes were inspected.")

    seen = {}
    reference_hashes = {}
    for shard, row in rows:
        uid, condition = row.get("object_uid"), row.get("condition")
        key = (uid, condition)
        if key in seen:
            errors.append(f"Duplicate raw object-condition key: {key}.")
            continue
        seen[key] = row
        if uid not in manifest_by_uid:
            errors.append(f"Unexpected UID in raw ledger: {uid}.")
            continue
        expected_idx = uids.index(uid)
        if row.get("object_idx") != expected_idx or shard != expected_idx % 2:
            errors.append(f"UID index/shard assignment mismatch for {uid}.")
        # The ledger stores the seed base (42); the frozen runner derives the
        # per-object RNG seed as seed_base + object_idx. Do not confuse these.
        if row.get("seed_base") != 42:
            errors.append(f"Frozen seed-base mismatch for {uid}.")
        if row.get("uncapped") is not condition.startswith("true_global_"):
            errors.append(f"Cap-bypass flag differs from frozen condition family for {uid}/{condition}.")
        hashes = row.get("input_hashes")
        if not isinstance(hashes, dict) or set(hashes) != {"cond", "depth", "global_embeds", "init_latent", "normal", "target"}:
            errors.append(f"Missing or malformed input fingerprints for {uid}/{condition}.")
        else:
            if uid in reference_hashes and hashes != reference_hashes[uid]:
                errors.append(f"Per-condition input fingerprints differ for {uid}.")
            reference_hashes.setdefault(uid, hashes)
        for metric in METRIC_FIELDS:
            try:
                value = float(row[metric])
            except (KeyError, TypeError, ValueError):
                errors.append(f"Missing/non-numeric metric field {metric} at {uid}/{condition}.")
                continue
            if not math.isfinite(value):
                errors.append(f"Non-finite metric value at {uid}/{condition}/{metric}.")
    if set(seen) != expected_keys:
        errors.append(f"Raw ledger unique-key coverage is {len(set(seen) & expected_keys)}/4,500, with missing={len(expected_keys - set(seen))} and unexpected={len(set(seen - expected_keys))}.")
    if len(reference_hashes) != 150:
        errors.append("Raw input fingerprints do not cover all 150 frozen objects.")

    # Re-hash every frozen rendered input and original source mesh before
    # unblinding. The exact cohort-manifest hash alone is not a substitute for
    # verifying current bytes.
    input_files_verified = 0
    for uid in uids:
        obj = manifest_by_uid[uid]
        render_dir = DATA_ROOT / uid
        for f in obj["files"]:
            source = render_dir / f["relative_path"]
            if not source.is_file() or source.stat().st_size != f["bytes"] or digest(source) != f["sha256"]:
                errors.append(f"Frozen render input missing or changed for UID {uid}.")
                break
            input_files_verified += 1
        mesh = Path(obj["mesh_path"])
        if not mesh.is_file() or digest(mesh) != obj["mesh_sha256"]:
            errors.append(f"Frozen source mesh missing or changed for UID {uid}.")

    # Run manifests prove the runner/config/checkpoint/data-root identity.
    manifests = []
    condition_specs = None
    for shard in (0, 1):
        path = RUN / f"run_manifest_shard{shard}.json"
        if not path.is_file():
            errors.append(f"Missing completion manifest for shard {shard}.")
            continue
        m = read_json(path)
        manifests.append(m)
        runner = m.get("runner_script_sha256", m.get("runner_sha256_at_start"))
        if runner != EXPECTED_RUNNER:
            errors.append(f"Runner SHA256 mismatch in shard {shard} manifest.")
        if m.get("config_sha256") != EXPECTED_CONFIG:
            errors.append(f"Config SHA256 mismatch in shard {shard} manifest.")
        if m.get("checkpoint_sha256") != EXPECTED_CHECKPOINT:
            errors.append(f"Checkpoint SHA256 mismatch in shard {shard} manifest.")
        if m.get("object_list_sha256") != EXPECTED_UIDS:
            errors.append(f"UID-list SHA256 mismatch in shard {shard} manifest.")
        roots = m.get("effective_data_roots", [])
        if roots != [str(DATA_ROOT.resolve())]:
            errors.append(f"Effective data-root mismatch in shard {shard} manifest.")
        if m.get("shard") != shard or m.get("num_shards") != 2:
            errors.append(f"Shard identity mismatch in shard {shard} manifest.")
        if m.get("status") != "complete" or m.get("row_count") != 2250:
            errors.append(f"Completion status/row count mismatch in shard {shard} manifest.")
        if m.get("conditions") != sorted(CONDITIONS):
            errors.append(f"Condition registry mismatch in shard {shard} manifest.")
        specs = m.get("condition_specs", {})
        if set(specs) != set(CONDITIONS):
            errors.append(f"Condition scale-spec registry mismatch in shard {shard} manifest.")
        else:
            for condition, spec in specs.items():
                if bool(spec.get("uncapped")) != condition.startswith("true_global_"):
                    errors.append(f"Cap-bypass flag differs from frozen condition family for {condition}.")
                trace = spec.get("scale_trace_requested")
                if not isinstance(trace, list) or len(trace) != 50:
                    errors.append(f"Requested-scale trace incomplete for {condition} in shard {shard}.")
                    continue
                if any(not isinstance(step, dict) or set(step) != {"deep", "middle", "shallow"}
                       or any(not isinstance(step[g], (int, float)) or not math.isfinite(float(step[g]))
                              for g in ("deep", "middle", "shallow")) for step in trace):
                    errors.append(f"Requested-scale trace malformed for {condition} in shard {shard}.")
        if condition_specs is None:
            condition_specs = specs
        elif condition_specs != specs:
            errors.append("Shard manifests disagree on condition specs/scale traces.")
        if m.get("residuals_only") is not False:
            errors.append(f"Unexpected residual-only mode in shard {shard} manifest.")
    if len(manifests) == 2:
        common = ("runner_script_sha256", "config_sha256", "checkpoint_sha256", "object_list_sha256", "effective_data_roots", "code_source_sha256")
        for field in common:
            if manifests[0].get(field) != manifests[1].get(field):
                errors.append(f"Shard manifests disagree on {field}.")
    required_sources = {
        "runner", "generation_logic", "adapter_wrapper", "data_utils",
        "metric_implementation", "train_util_dataset_factory", "metric_package",
        "metric_image_functions", "metric_mask_functions", "metric_region_functions",
        "metric_crop_functions",
    }
    for shard, manifest in enumerate(manifests):
        sources = manifest.get("code_source_sha256", {})
        if set(sources) != required_sources:
            errors.append(f"Source-code hash registry mismatch in shard {shard} manifest.")
        for name, item in sources.items():
            source = Path(item.get("path", ""))
            if not source.is_file() or digest(source) != item.get("sha256"):
                errors.append(f"Current source does not match recorded hash for {name} in shard {shard}.")

    # Check all frozen prediction PNGs and residual JSONs exist, are finite,
    # and map one-to-one to the expected UID/condition pairs.
    expected_names = set(uids)
    png_count = residual_count = 0
    for condition in CONDITIONS:
        pred_dir = RUN / "predictions" / condition
        log_dir = RUN / "residual_logs" / condition
        pred_names = {p.stem for p in pred_dir.glob("*.png")} if pred_dir.is_dir() else set()
        log_names = {p.stem for p in log_dir.glob("*.json")} if log_dir.is_dir() else set()
        if pred_names != expected_names:
            errors.append(f"Prediction PNG identity set incomplete/extra for {condition}.")
        if log_names != expected_names:
            errors.append(f"Residual-log identity set incomplete/extra for {condition}.")
        png_count += len(pred_names)
        residual_count += len(log_names)
        for path in pred_dir.glob("*.png") if pred_dir.is_dir() else ():
            try:
                with Image.open(path) as image:
                    width, height = image.size
                    if (image.format != "PNG" or width % 256 or height % 256
                            or width * height != 6 * 256 * 256):
                        raise ValueError("unexpected prediction format or six-view dimensions")
                    image.verify()
            except Exception:
                errors.append(f"Invalid prediction PNG: {condition}/{path.name}.")
        for path in log_dir.glob("*.json") if log_dir.is_dir() else ():
            try:
                log = read_json(path)
                if set(log) != {str(i) for i in range(50)}:
                    raise ValueError("residual log does not contain exactly 50 steps")
                spec = condition_specs.get(condition, {}) if condition_specs else {}
                trace = spec.get("scale_trace_requested", [])
                caps = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
                for step_idx in range(50):
                    entries = log[str(step_idx)]
                    if not isinstance(entries, dict) or not entries:
                        raise ValueError("empty or malformed per-step residual entries")
                    for entry in entries.values():
                        if not isinstance(entry, dict) or not {"depth", "scale", "eff_scale"} <= set(entry):
                            raise ValueError("malformed residual entry")
                        group = entry["depth"]
                        if group not in caps or float(entry["scale"]) != float(trace[step_idx][group]):
                            raise ValueError("requested scale differs from frozen trace")
                        if float(entry["eff_scale"]) != min(float(entry["scale"]), caps[group]):
                            raise ValueError("logged clipped scale differs from native cap")
                def check_finite(value):
                    if isinstance(value, dict):
                        for v in value.values(): check_finite(v)
                    elif isinstance(value, list):
                        for v in value: check_finite(v)
                    elif isinstance(value, (int, float)) and not math.isfinite(float(value)):
                        raise ValueError("non-finite value")
                check_finite(log)
            except Exception:
                errors.append(f"Invalid or non-finite residual log: {condition}/{path.name}.")

    # The live runner checkpoints its shard CSVs every 16 rows, so the last
    # few rows can be absent when a shard ends. Rebuild complete canonical
    # CSVs from the authoritative ledgers before invoking this gate.
    csv_rows = {}
    combined_csv = RUN / "per_object_metrics.csv"
    if not combined_csv.is_file():
        errors.append("Missing rebuilt combined per-object CSV.")
    else:
        with combined_csv.open(newline="") as f:
            combined_rows = list(csv.DictReader(f))
        if len(combined_rows) != 4500:
            errors.append("Rebuilt combined per-object CSV row count mismatch.")
        for r in combined_rows:
            key = (r.get("object_uid"), r.get("condition"))
            if key in csv_rows:
                errors.append(f"Duplicate rebuilt combined CSV key: {key}.")
            csv_rows[key] = r
    if set(csv_rows) != expected_keys:
        errors.append("Rebuilt combined CSV key set differs from the frozen 4,500-row set.")
    else:
        for key, row in csv_rows.items():
            raw = seen[key]
            if row.get("uncapped") != str(raw.get("uncapped")):
                errors.append(f"CSV/raw cap-bypass flag mismatch at {key}.")
            for metric in METRIC_FIELDS:
                try:
                    if float(row[metric]) != float(raw[metric]):
                        errors.append(f"CSV/raw metric serialization mismatch at {key}/{metric}.")
                        break
                except (KeyError, TypeError, ValueError):
                    errors.append(f"CSV missing metric {metric} at {key}.")
                    break
    for condition in CONDITIONS:
        path = RUN / f"{condition}_per_object_metrics.csv"
        if not path.is_file():
            errors.append(f"Missing rebuilt per-condition CSV for {condition}.")
            continue
        with path.open(newline="") as f:
            condition_rows = list(csv.DictReader(f))
        if len(condition_rows) != 150:
            errors.append(f"Rebuilt per-condition CSV row count mismatch for {condition}.")
        condition_keys = set()
        for row in condition_rows:
            key = (row.get("object_uid"), row.get("condition"))
            if key in condition_keys:
                errors.append(f"Duplicate key in rebuilt per-condition CSV: {key}.")
            condition_keys.add(key)
            if key not in expected_keys or key[1] != condition:
                errors.append(f"Unexpected key in rebuilt per-condition CSV: {key}.")
                continue
            raw = seen.get(key)
            if raw is None:
                errors.append(f"Per-condition CSV row missing from raw ledger: {key}.")
                continue
            for metric in METRIC_FIELDS:
                try:
                    if float(row[metric]) != float(raw[metric]):
                        errors.append(f"Condition CSV/raw metric serialization mismatch at {key}/{metric}.")
                        break
                except (KeyError, TypeError, ValueError):
                    errors.append(f"Condition CSV missing metric {metric} at {key}.")
                    break
        if condition_keys != {(uid, condition) for uid in uids}:
            errors.append(f"Rebuilt per-condition CSV UID coverage mismatch for {condition}.")

    if errors:
        fail(sorted(set(errors)))

    report = [
        "# FRESH_CONFIRM_B formal integrity gate", "",
        "**FRESH_CONFIRM_B_FORMAL_INTEGRITY = PASS**", "",
        "This gate was run before condition-level statistical analysis. It checked row keys, source inputs, manifests, shards, finite metrics/residuals, image/log presence, and CSV/ledger agreement. It did not calculate or inspect condition means or contrasts.", "",
        "| Check | Result |", "|---|---:|",
        f"| Frozen objects | {len(uids)}/150 |",
        f"| Unique object-condition rows | {len(seen)}/4500 |",
        f"| Raw rows, shard 0 / shard 1 | {shard_counts[0]} / {shard_counts[1]} |",
        f"| Frozen rendered input files byte/hash verified | {input_files_verified} |",
        f"| Prediction PNGs present | {png_count}/4500 |",
        f"| Per-step residual logs present | {residual_count}/4500 |",
        "| Duplicate keys / missing condition pairs / non-finite values | 0 / 0 / 0 |",
        "| Runner / config / checkpoint / effective data root | MATCH |",
        f"| Recorded inference/metric source files matching current bytes | {len(required_sources)}/{len(required_sources)} per shard |",
        "| Raw ledgers ↔ rebuilt combined/condition CSV values | EXACT |",
        "", "Condition-level outputs remain unopened until this PASS gate is committed.", "",
    ]
    (V3 / "B_FORMAL_INTEGRITY_GATE.md").write_text("\n".join(report))
    print("FRESH_CONFIRM_B_FORMAL_INTEGRITY=PASS; no outcome statistics were computed or printed.")


if __name__ == "__main__":
    main()
