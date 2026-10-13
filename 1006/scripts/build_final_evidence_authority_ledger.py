#!/usr/bin/env python3
"""Build a hash-addressed run/condition authority index without changing analyses."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/4T/CXY/MV-Painter")
OUT_JSON = ROOT / "1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json"
OUT_MD = ROOT / "1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.md"
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}
ALIASES = {
    "native_gfl": ["GFL", "fixed-low"],
    "native_gfh": ["GFH", "fixed-high"],
    "native_gc3": ["C3", "GC3", "native cap-cycle-3"],
    "no_adapter": ["no-adapter", "unmodified control"],
    "layer_llh": ["LLH", "layer low-low-high"],
    "gen_linear": ["generic linear", "endpoint-matched linear"],
    "lfm_exact": ["LFM-exact", "layer-fixed-mean exact"],
    "a3_baseline": ["A3 low-profile baseline"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def source(path: Path | None, role: str) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {"path": rel(path) if path else None, "sha256": None, "role": role, "availability": "not recorded or absent"}
    return {"path": rel(path), "sha256": sha256(path), "role": role, "availability": "present"}


def compress_trace(trace: Any) -> list[dict[str, Any]] | None:
    if not isinstance(trace, list) or not trace:
        return None
    result: list[dict[str, Any]] = []
    start = 0
    current = trace[0]
    for index, value in enumerate(trace[1:], start=1):
        if value != current:
            result.append({"step_start_inclusive": start, "step_end_exclusive": index, "values": current})
            start, current = index, value
    result.append({"step_start_inclusive": start, "step_end_exclusive": len(trace), "values": current})
    return result


def applied_trace(trace: Any, uncapped: bool) -> list[dict[str, Any]] | None:
    if not isinstance(trace, list) or not trace:
        return None
    applied = []
    for step in trace:
        if not isinstance(step, dict):
            return None
        applied.append({group: float(value) if uncapped else min(float(value), CAPS[group])
                        for group, value in step.items()})
    return compress_trace(applied)


def family_context(run_dir: Path) -> dict[str, Any]:
    path = rel(run_dir).lower()
    if "revision_era_addendum" in path:
        return {
            "evidence_class": "revision-era prospective comparison motivated by prior Fresh-B evidence; same Fresh C cohort; not original preregistration",
            "allowed_claim": "Only named LLH/C3/linear image-space comparisons under the frozen native-cap profiles, with object and endpoint heterogeneity reported.",
            "prohibited_claim": "No equivalence without a margin, no overall winner, no independent cohort claim, no dose-independent mechanism, and no human/3D fidelity claim.",
            "lock_time": "2026-10-06T11:48:12.919124+00:00",
        }
    if "c3_confirmation" in path:
        return {
            "evidence_class": "revision-era prospective confirmation on a new frozen cohort; motivated by prior revision evidence; not original preregistration",
            "allowed_claim": "C3−GFL FG-PSNR on the frozen N=300 image-space cohort, with paired CI, favorable-object fraction, and chronology limit.",
            "prohibited_claim": "No original-preregistration replication, no human fidelity, no 3D quality, and no universal schedule law.",
            "lock_time": "2026-10-06T13:35:00.957920+00:00 (cohort freeze; protocol lock date 2026-10-06 UTC)",
        }
    if "generic_extension" in path:
        return {
            "evidence_class": "post-lock same-cohort sensitivity analysis",
            "allowed_claim": "Descriptive Fresh-B generic-linear comparator sensitivity only, kept separate from other cohorts.",
            "prohibited_claim": "Not an independent confirmation or prespecified primary comparison.",
            "lock_time": "see final/round2/scientific_validation_v3/FRESH_CONFIRM_B_GENERIC_EXTENSION_LOCK_20261005.md",
        }
    if "campaign_fresh_confirm_b" in path or "fresh_b" in path:
        return {
            "evidence_class": "new-cohort campaign with post-discovery chronology limitation; registry records no valid prospective pre-unblind lock",
            "allowed_claim": "Bounded A3b/boundary/cap-budget evidence on Fresh B; report exact tested profiles and dose limitations.",
            "prohibited_claim": "No original-preregistration replication, no dose-independent Layer×Window law, no unique winner, and no extra independent N from seeds/views.",
            "lock_time": "2026-10-05T08:40:00+00:00 (campaign protocol lock; authority registry flags prior outcome exposure)",
        }
    if "formal_seed" in path or "static_seed" in path:
        return {
            "evidence_class": "post-result realization sensitivity or static-factor follow-up on reused objects",
            "allowed_claim": "Descriptive object-level seed sensitivity or fixed-depth static intervention, separately named.",
            "prohibited_claim": "Does not increase independent object N and does not validate a time-varying causal mechanism.",
            "lock_time": "see 1006/evidence/audits/next_stage_20261006/MULTISEED_PROTOCOL.json and STATIC_EXECUTION_LOCK.json",
        }
    if "dev" in path or "pilot" in path or "preflight" in path or "a3b_development" in path:
        return {
            "evidence_class": "development-only, pilot, or technical feasibility",
            "allowed_claim": "Development feasibility or candidate-selection context only; no independent effectiveness estimate.",
            "prohibited_claim": "Do not describe as held-out confirmation or as final quality evidence.",
            "lock_time": "recorded in the corresponding development lock where available; exact wall-clock unblind time not recorded",
        }
    return {
        "evidence_class": "historical registered or retrospective analysis; claim-specific chronology is in the linked evidence ledger",
        "allowed_claim": "Use only the claim wording and limitations in the linked authoritative reports and claim ledger.",
        "prohibited_claim": "Do not merge across cohort, runner, seed, cap, metric, or protocol; no cross-metric winner.",
        "lock_time": None,
    }


def n_from_manifests(manifests: list[dict[str, Any]]) -> tuple[int | None, str]:
    estimates = []
    for manifest in manifests:
        conditions = manifest.get("conditions") or []
        row_count = manifest.get("row_count")
        shards = manifest.get("num_shards") or 1
        if conditions and isinstance(row_count, int):
            estimate = row_count * int(shards) / len(conditions)
            if estimate.is_integer():
                estimates.append(int(estimate))
    if estimates and len(set(estimates)) == 1:
        return estimates[0], "derived from locked rows-per-shard × shard count ÷ condition count"
    if estimates:
        return None, f"inconsistent N derivations across shard manifests: {estimates}"
    return None, "N not inferable from available manifests"


def classification_sources(run_dir: Path) -> list[dict[str, Any]]:
    relpath = rel(run_dir)
    candidates: list[Path] = []
    if "revision_era_addendum" in relpath:
        candidates += [ROOT / "1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.json",
                       ROOT / "1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.md"]
    elif "c3_confirmation" in relpath:
        candidates += [ROOT / "1006/evidence/protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md",
                       ROOT / "1006/data/fresh_c/FRESH_C_COHORT_MANIFEST.json"]
    elif "campaign_FRESH_CONFIRM_B_20261005" in relpath:
        candidates += [ROOT / "final/round2/scientific_validation_v3/FRESH_CONFIRM_B_FORMAL_PROTOCOL_LOCK.md",
                       ROOT / "final/round2/scientific_validation_v3/B_CONDITION_REGISTRY.json"]
    elif "formal_seed" in relpath or "static_seed" in relpath:
        candidates += [ROOT / "1006/evidence/audits/next_stage_20261006/MULTISEED_PROTOCOL.json",
                       ROOT / "1006/evidence/audits/next_stage_20261006/STATIC_EXECUTION_LOCK.json"]
    return [source(path, "protocol/chronology authority") for path in candidates]


def run_records() -> list[dict[str, Any]]:
    manifest_paths = set((ROOT / "final/round2/scientific_validation_v3").glob("**/run_manifest_shard0.json"))
    manifest_paths |= set((ROOT / "1006/data").glob("**/run_manifest_shard0.json"))
    records: list[dict[str, Any]] = []
    seen_runs: set[str] = set()
    for shard0 in sorted(manifest_paths):
        run_dir = shard0.parent
        run_id = rel(run_dir)
        if run_id in seen_runs:
            continue
        seen_runs.add(run_id)
        manifests = []
        manifest_files = sorted(run_dir.glob("run_manifest_shard*.json"))
        for path in manifest_files:
            try:
                manifests.append(json.loads(path.read_text()))
            except (OSError, json.JSONDecodeError):
                continue
        if not manifests:
            continue
        canonical = manifests[0]
        conditions = sorted({condition for manifest in manifests for condition in manifest.get("conditions", [])})
        cohort_n, n_basis = n_from_manifests(manifests)
        context = family_context(run_dir)
        source_artifacts = [source(path, "per-shard execution manifest") for path in manifest_files]
        row_files = sorted(run_dir.glob("rows_shard*.json"))
        for path in row_files:
            source_artifacts.append(source(path, "raw per-object/per-condition row ledger"))
        for candidate in (run_dir / "per_object_metrics.csv", run_dir / "OUTPUT_FILE_SHA256.csv"):
            if candidate.is_file():
                source_artifacts.append(source(candidate, "derived per-object metrics or output hash manifest"))
        residual_root = run_dir / "residual_logs"
        prediction_root = run_dir / "predictions"
        source_hashes = canonical.get("code_source_sha256", {})
        metric_hash = None
        if isinstance(source_hashes, dict):
            metric_hash = (source_hashes.get("metric_implementation") or {}).get("sha256")
        if not metric_hash:
            metric_hash = canonical.get("metric_implementation_sha256")
        n_per_condition = cohort_n
        for condition in conditions:
            spec = next((m.get("condition_specs", {}).get(condition) for m in manifests
                         if condition in m.get("condition_specs", {})), None)
            spec = spec or {}
            requested = spec.get("scale_trace_requested")
            uncapped = bool(spec.get("uncapped", False))
            residual_dir = residual_root / condition
            prediction_dir = prediction_root / condition
            residual_count = len(list(residual_dir.glob("*.json"))) if residual_dir.is_dir() else 0
            prediction_count = len(list(prediction_dir.glob("*.png"))) if prediction_dir.is_dir() else 0
            adapter_enabled = spec.get("adapter")
            row = {
                "run_id": run_id,
                "canonical_condition_name": condition,
                "historical_aliases": ALIASES.get(condition, []),
                "requested_scale_profile": {
                    "step_count": len(requested) if isinstance(requested, list) else None,
                    "segments": compress_trace(requested),
                    "source": source(manifest_files[0] if manifest_files else None, "exact requested-scale trace"),
                },
                "actually_applied_scale_cap_trace": {
                    "cap_by_depth": None if uncapped else CAPS,
                    "cap_bypass": uncapped,
                    "deterministic_segments_from_requested_trace": applied_trace(requested, uncapped),
                    "per_object_realized_trace_source": rel(residual_dir) if residual_dir.exists() else None,
                    "interpretation": "applied scales are request clipped by native caps; residual magnitude is a separate measured quantity",
                },
                "realized_residual_measurement": {
                    "status": ("per-object logs present" if residual_count else "not present/unknown; see source records"),
                    "log_file_count": residual_count,
                    "expected_count": n_per_condition if adapter_enabled is not False else 0,
                    "verified_by_integrity_gate": "see run-specific audit; no gate status inferred from file count alone",
                },
                "cohort": run_id,
                "n_objects": cohort_n,
                "n_derivation": n_basis,
                "seed_policy": {
                    "latent_seed": canonical.get("latent_seed"),
                    "reference_seed_policy": canonical.get("reference_seed_policy"),
                    "generation_seed_or_realization": canonical.get("realization"),
                },
                "checkpoint": {
                    "path_or_name": canonical.get("checkpoint"),
                    "sha256": canonical.get("checkpoint_sha256"),
                },
                "runner_commit_provenance": {
                    "runner_sha256": canonical.get("runner_script_sha256") or (source_hashes.get("runner") or {}).get("sha256"),
                    "code_source_hashes": source_hashes,
                    "commit_hash": canonical.get("git_commit") or canonical.get("commit_hash"),
                    "commit_hash_status": "recorded" if canonical.get("git_commit") or canonical.get("commit_hash") else "not present in run manifest; source hashes retained",
                },
                "input_conditioning_provenance": {
                    "object_list": canonical.get("object_list"),
                    "object_list_sha256": canonical.get("object_list_sha256"),
                    "cohort_manifest_sha256": canonical.get("cohort_manifest_sha256"),
                    "input_embeddings_manifest_sha256": canonical.get("input_embeddings_manifest_sha256"),
                    "per_row_input_hashes": bool(row_files),
                    "protocol_sources": classification_sources(run_dir),
                },
                "output_provenance": {
                    "raw_row_ledgers": [source(path, "raw rows") for path in row_files],
                    "per_object_metrics_path": rel(run_dir / "per_object_metrics.csv") if (run_dir / "per_object_metrics.csv").exists() else None,
                    "prediction_directory": rel(prediction_dir) if prediction_dir.exists() else None,
                    "prediction_file_count": prediction_count,
                    "residual_directory": rel(residual_dir) if residual_dir.exists() else None,
                    "run_manifest_sources": [source(path, "run manifest") for path in manifest_files],
                },
                "metric_implementation_version": {
                    "metric_path": canonical.get("metric_path"),
                    "metric_implementation_sha256": metric_hash,
                    "metric_code_version_status": "source hash recorded; package/version string not always recorded",
                },
                "protocol_freeze_time_utc": context["lock_time"],
                "outcome_exposure_time_utc": None,
                "outcome_exposure_time_status": "exact first-view/unblind wall-clock not consistently recorded; run/analysis completion records are retained separately",
                "evidence_class": context["evidence_class"],
                "allowed_claim": context["allowed_claim"],
                "prohibited_claim": context["prohibited_claim"],
                "superseded_artifacts": [],
                "run_dimensions": {
                    "conditions": conditions,
                    "adapter_enabled": adapter_enabled,
                    "uncapped_flag": uncapped,
                    "sampler": canonical.get("sampler"),
                    "steps": canonical.get("steps"),
                    "resolution": canonical.get("resolution"),
                    "target_views": canonical.get("target_views"),
                    "status": canonical.get("status"),
                },
                "source_artifacts": source_artifacts,
            }
            if condition == "layer_llh" or condition == "gen_linear":
                row["superseded_artifacts"] = [
                    "1006/evidence/audits/superseded/AUTHORITATIVE_GENERIC_SCHEDULE_REPORT_AS_RECEIVED.md (sign and interpretation superseded by LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md)"
                ]
            records.append(row)
    return records


def evidence_families() -> list[dict[str, Any]]:
    entries = [
        ("01549 submitted paper and original evidence", "historical/submitted", "Continuity and original claim provenance only; do not overwrite source manuscript.", ["1006/MANUSCRIPT_PRESERVATION_AUDIT.md", "01549.tex"]),
        ("clean-v2 and strict-276", "retrospective/re-evaluation", "Historical supporting analyses; strict-276 is not new held-out confirmation and legacy runner/input provenance is incomplete.", ["1006/evidence/audits/COHORT_IDENTITY_AUDIT.md", "1006/data/strict276"]),
        ("A1/A2/A3 and stage placement", "historical registered plus development", "Pipeline-specific response profile evidence; report native dose/caps and exact family; no general control-space law.", ["final/round2/scientific_validation_v3/formal/campaign_A2", "final/round2/scientific_validation_v3/formal/campaign_A3", "1006/evidence/audits/FINAL_CAP_BUDGET_CAUSAL_ACCOUNTING.md"]),
        ("A3b, boundary, Fresh B B1/B2/B3 and generic schedule", "new cohort with chronology limits; separate post-lock sensitivity", "Named profile comparisons, bounded-map and failure-boundary evidence; not dose-independent or universal.", ["1006/data/fresh_b", "final/round2/scientific_validation_v3/B_CONDITION_REGISTRY.json", "1006/evidence/audits/FRESH_B_TEMPORAL_CONFIRMATION_REPORT.md"]),
        ("Fresh C original four-condition run", "revision-era prospective new-cohort image-space confirmation", "Only registered C3−GFL FG-PSNR primary and named secondary effects; no human or 3D claim.", ["1006/data/fresh_c/FRESH_C_INTEGRITY_GATE.json", "1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json"]),
        ("Fresh C LLH/linear addendum", "revision-era prospective comparison on same Fresh C cohort", "Three frozen named comparisons, six-test primary and separate 15-test secondary Holm families.", ["1006/evidence/protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.json", "1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json"]),
        ("E1 multiseed and E2 static factorial", "realization sensitivity and fixed-scale follow-up", "Object-level sensitivity/fixed-depth effects only; no new independent object N or temporal mechanism.", ["1006/evidence/audits/next_stage_20261006/MULTISEED_ANALYSIS.md", "1006/evidence/audits/next_stage_20261006/STATIC_FACTORIAL_ANALYSIS.md"]),
        ("MV-Adapter and MVDiffusion", "tested-interface boundaries", "Report interfaces separately; no pooled architecture effect or transfer causality.", ["1006/evidence/audits/CROSS_BACKBONE_MECHANISM_REPORT.md", "1006/evidence/audits/MVDIFFUSION_STANDARD_PANEL_REPORT.md"]),
        ("GLB-native N=20, seam, FAC and visual panels", "bounded historical outputs and retired/unverified endpoints", "Unlit base-color endpoint only where validated; no human fidelity, full PBR or seam improvement claim.", ["1006/data/glb_native", "1006/evidence/audits/FINAL_UNIFIED_3D_VALIDATION_SUPERSEDED.md", "1006/evidence/audits/GLB_NATIVE_EGL_RENDER_REPORT_20261006.md"]),
        ("Human study", "not distributed; zero responses", "No perceptual preference inference; future response data require frozen package and private-data handling.", ["1006/evidence/protocols/HUMAN_STUDY_FINAL_PAIR_LOCK.md", "1006/guides/FINAL_METHOD_HUMAN_RESPONSE_HANDOFF_20261006_ZH.md"]),
        ("E5/E6 development", "technical feasibility/development; E6 stopped", "No matched-dose quality or Fresh D efficacy claim; E6 method candidate stopped at value gate.", ["1006/evidence/audits/E5_RESIDUAL_DOSE_FEASIBILITY_REPORT_20261006.md", "1006/evidence/audits/E6_DEVELOPMENT_DECISION_20261006_ZH.md"]),
    ]
    result = []
    for name, classification, allowance, paths in entries:
        refs = []
        for item in paths:
            path = ROOT / item
            if path.is_file():
                refs.append(source(path, "evidence authority"))
            elif path.is_dir():
                manifests = sorted(path.glob("**/run_manifest_shard0.json"))[:10]
                refs.extend(source(candidate, "campaign run manifest; truncated to first 10 only") for candidate in manifests)
            else:
                refs.append({"path": item, "sha256": None, "role": "referenced evidence", "availability": "not found at expected path"})
        result.append({"evidence_family": name, "evidence_class": classification,
                       "allowed_claim": allowance,
                       "prohibited_claim": "Do not pool across cohort/runner/seed/cap/metric; report limitations and opposing endpoints.",
                       "sources": refs})
    return result


def main() -> None:
    records = run_records()
    claim_ledger_path = ROOT / "1006/evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json"
    claim_ledger = json.loads(claim_ledger_path.read_text()) if claim_ledger_path.exists() else {}
    payload = {
        "schema_version": 1,
        "ledger_id": "FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006",
        "updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "authority_status": "CANONICAL_RUN_INDEX_WITH_EXPLICIT_PROVENANCE_GAPS",
        "scientific_evidence_freeze": "NO",
        "authority_rules": [
            "Per-object paired rows and locked protocols/manifests are numerical authority; old summaries do not overwrite them.",
            "Never pool cohorts, seeds, runners, cap semantics, or measurement endpoints into one ranking.",
            "Positive lower-is-better metric differences favor the second condition when contrasts are A minus B.",
            "A missing provenance field is represented as null with an explicit reason; it is not reconstructed by guesswork.",
            "Manuscript tables, figures, and reviewer responses must cite this run ledger and the claim-centric E0 ledger.",
        ],
        "claim_ledger": {
            "path": "1006/evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json",
            "sha256": sha256(claim_ledger_path) if claim_ledger_path.exists() else None,
            "claim_count": len(claim_ledger.get("claims", [])),
            "source_count": len(claim_ledger.get("sources", [])),
        },
        "run_condition_record_count": len(records),
        "run_count": len({row["run_id"] for row in records}),
        "condition_records": records,
        "evidence_families": evidence_families(),
        "global_open_gates": [
            "real human responses or formal withdrawal of all perceptual-fidelity claims",
            "new 24-object GLB bake/unseen-view gate or explicit exclusion of new 3D claim",
            "source-level redistribution rights for included assets and derivatives",
            "R2.1 adversarial contribution/venue review after available R1 fidelity decisions",
            "paper-wide raw-to-table provenance rebuild and final manuscript/response mapping",
        ],
        "manuscript_policy": {"do_not_edit_01549_until_scientific_evidence_freeze": True,
                              "final_response_letter_not_ready": True,
                              "github_release_not_license_cleared": True},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    md = [
        "# Final Evidence Authority Ledger — 2026-10-06", "",
        f"**State:** `{payload['authority_status']}`; `SCIENTIFIC_EVIDENCE_FREEZE=NO`.",
        f"**Run coverage:** {payload['run_count']} execution directories and {payload['run_condition_record_count']} method-condition records; {payload['claim_ledger']['claim_count']} claims and {payload['claim_ledger']['source_count']} hash-addressed sources in the linked claim ledger.",
        "",
        "This is the condition-level provenance index. The linked E0 ledger is the claim-level wording authority. Both must be consulted before using a number in manuscript text, a figure, or a reviewer response.",
        "",
        "## Authority and scope rules", "",
    ]
    md += [f"- {rule}" for rule in payload["authority_rules"]]
    md += ["", "## Fresh C authority", "",
           "The unchanged four-condition Fresh C run is the only locked primary comparison in this revision stage: `native_gc3 − native_gfl`, FG-PSNR. The LLH/linear addendum is separate, revision-era prospective, on the same frozen cohort, and uses its own six-test primary and 15-test secondary Holm families. Its positive `LLH − linear` LPIPS favors generic linear because lower is better.",
           "", "## Condition fields and provenance gaps", "",
           "Each JSON condition record contains requested profile, cap-applied profile, residual-trace availability, cohort/N, seed policy, checkpoint, runner/source hashes, input/output provenance, metric implementation hash, lock and outcome-exposure timing, evidence class, allowed/prohibited claim, and superseded artifact pointers. Unknown commit or exact first-unblind times remain explicitly null; the ledger does not infer them.",
           "", "## Open evidence gates", ""]
    md += [f"- {item}" for item in payload["global_open_gates"]]
    md += ["", "Machine-readable condition records: `FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`.",
           "Claim-centric E0 ledger: `next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json`.",
           ""]
    OUT_MD.write_text("\n".join(md))
    print(json.dumps({"ledger": rel(OUT_JSON), "run_count": payload["run_count"],
                      "condition_record_count": payload["run_condition_record_count"],
                      "status": payload["authority_status"], "freeze": "NO"}, indent=2))


if __name__ == "__main__":
    main()
