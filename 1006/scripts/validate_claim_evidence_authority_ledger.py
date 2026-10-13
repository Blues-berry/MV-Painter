#!/usr/bin/env python3
"""Validate the 1006 claim-to-evidence ledger without touching 01549 files."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "1006/evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json"
AUDIT = ROOT / "1006/evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_AUDIT.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = []
    source_ids = set()
    for source in ledger.get("sources", []):
        source_id = source.get("source_id", "")
        if not source_id or source_id in source_ids:
            errors.append(f"missing or duplicate source_id: {source_id!r}")
        source_ids.add(source_id)
        evidence_path = source.get("package_path", source.get("path", ""))
        path = ROOT / evidence_path
        if not path.is_file():
            errors.append(f"source missing: {source_id} -> {evidence_path}")
        elif sha256(path) != source.get("sha256"):
            errors.append(f"source hash mismatch: {source_id} -> {source.get('path')}")
    claim_ids = set()
    required = ("authority_status", "comparison", "registration_status", "selection_status",
                "intervention_profile", "statistical_unit", "statistical_method", "multiplicity",
                "allowed_wording", "prohibited_wording", "next_gate")
    for claim in ledger.get("claims", []):
        claim_id = claim.get("claim_id", "")
        if not claim_id or claim_id in claim_ids:
            errors.append(f"missing or duplicate claim_id: {claim_id!r}")
        claim_ids.add(claim_id)
        for source_id in claim.get("authoritative_sources", []):
            if source_id not in source_ids:
                errors.append(f"unknown source {source_id!r} referenced by {claim_id}")
        for key in required:
            if not claim.get(key):
                errors.append(f"{claim_id} missing required field {key}")
    if ledger.get("manuscript_policy", {}).get("editing_state") != "FROZEN_UNTIL_SCIENTIFIC_EVIDENCE_FREEZE":
        errors.append("manuscript freeze policy is missing or changed")
    if ledger.get("manuscript_policy", {}).get("submission_ready") is not False:
        errors.append("ledger must not mark submission ready")
    audit = {
        "ledger_id": ledger.get("ledger_id"), "ledger_sha256": sha256(LEDGER),
        "validated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_count": len(source_ids), "claim_count": len(claim_ids),
        "source_hashes_match": not any("hash mismatch" in e for e in errors),
        "manuscript_policy_preserved": not any("manuscript" in e for e in errors),
        "scientific_evidence_freeze": ledger.get("authority_status"),
        "errors": errors, "status": "PASS" if not errors else "FAIL",
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
