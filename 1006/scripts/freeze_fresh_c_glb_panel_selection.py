#!/usr/bin/env python3
"""Freeze an input-only UV/license-qualified Fresh C GLB panel list.

This script deliberately reads only the frozen UID list, candidate asset
audit, license tags, and GLB geometry/UV attributes. It never reads method
predictions, per-object metrics, or analysis outputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/4T/CXY/MV-Painter")
DATA = ROOT / "1006/data/fresh_c"
OUTPUT = DATA / "FRESH_C_GLB_PANEL_SELECTION_20261006.json"
ALLOWED_LICENSES = {"cc0", "by", "by-sa"}
TARGET = 24


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def inspect_uv(path: Path) -> tuple[bool, dict[str, object]]:
    scene = trimesh.load(path, force="scene", process=False)
    if not isinstance(scene, trimesh.Scene):
        raise TypeError(f"expected a GLB scene, got {type(scene).__name__}")
    details: list[dict[str, object]] = []
    errors: list[str] = []
    total_faces = 0
    for name, geometry in scene.geometry.items():
        faces = np.asarray(geometry.faces)
        vertices = np.asarray(geometry.vertices)
        uv = getattr(getattr(geometry, "visual", None), "uv", None)
        valid = bool(
            len(faces) > 0
            and len(vertices) > 0
            and uv is not None
            and np.asarray(uv).shape == (len(vertices), 2)
            and np.isfinite(np.asarray(uv)).all()
            and np.isfinite(vertices).all()
            and faces.min(initial=0) >= 0
            and faces.max(initial=-1) < len(vertices)
        )
        total_faces += int(len(faces))
        if not valid:
            errors.append(str(name))
        uv_array = None if uv is None else np.asarray(uv)
        details.append({
            "geometry": str(name),
            "vertices": int(len(vertices)),
            "faces": int(len(faces)),
            "uv_shape": None if uv_array is None else list(uv_array.shape),
            "uv_min": None if uv_array is None or not uv_array.size else [float(x) for x in uv_array.min(axis=0)],
            "uv_max": None if uv_array is None or not uv_array.size else [float(x) for x in uv_array.max(axis=0)],
            "valid_uv": valid,
        })
    ok = bool(details) and not errors and total_faces > 0
    return ok, {"geometry_count": len(details), "face_count": total_faces,
                "geometries": details, "invalid_geometry_names": errors}


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite frozen selection: {OUTPUT}")
    cohort_path = DATA / "fresh_c_objects.txt"
    cohort_manifest_path = DATA / "FRESH_C_COHORT_MANIFEST.json"
    asset_audit_path = DATA / "candidate_asset_technical_audit.csv"
    queue_lock_path = DATA / "CANDIDATE_QUEUE_LOCK.json"
    cohort_uids = [line.strip() for line in cohort_path.read_text().splitlines() if line.strip()]
    cohort_manifest = json.loads(cohort_manifest_path.read_text())
    queue_lock = json.loads(queue_lock_path.read_text())
    asset_rows = {row["uid"]: row for row in read_csv(asset_audit_path)}
    expected_licenses = set(queue_lock["allowed_license_tags"])
    if expected_licenses != ALLOWED_LICENSES:
        raise RuntimeError(f"license policy differs from frozen queue lock: {expected_licenses}")
    if cohort_manifest.get("status") != "FROZEN_FRESH_C_300" or len(cohort_uids) != cohort_manifest.get("selected_count"):
        raise RuntimeError("Fresh C cohort is not the expected frozen cohort")
    if len(set(cohort_uids)) != len(cohort_uids):
        raise RuntimeError("frozen UID list contains duplicates")

    selected: list[dict[str, object]] = []
    rejected: list[dict[str, str]] = []
    for cohort_index, uid in enumerate(cohort_uids):
        row = asset_rows.get(uid)
        if row is None:
            rejected.append({"uid": uid, "reason": "missing_input_asset_audit_row"})
            continue
        if row["license"].lower() not in ALLOWED_LICENSES:
            rejected.append({"uid": uid, "reason": "license_not_in_frozen_allowlist"})
            continue
        if row["status"] != "glb_load_valid":
            rejected.append({"uid": uid, "reason": "input_geometry_audit_not_valid"})
            continue
        asset = Path(row["asset_path"])
        if not asset.is_file() or sha256(asset) != row["asset_sha256"]:
            rejected.append({"uid": uid, "reason": "asset_missing_or_hash_mismatch"})
            continue
        try:
            uv_ok, uv = inspect_uv(asset)
        except Exception as exc:  # noqa: BLE001
            rejected.append({"uid": uid, "reason": f"uv_audit_error:{type(exc).__name__}"})
            continue
        if not uv_ok:
            rejected.append({"uid": uid, "reason": "one_or_more_meshes_lack_finite_vertex_uvs"})
            continue
        selected.append({
            "panel_order": len(selected) + 1,
            "cohort_index": cohort_index,
            "uid": uid,
            "license": row["license"].lower(),
            "asset_path": str(asset),
            "asset_sha256": row["asset_sha256"],
            "uv_audit": uv,
        })
        if len(selected) == TARGET:
            break

    selection = {
        "status": "FROZEN_INPUT_ONLY_SELECTION",
        "panel_id": "FRESH_C_GLB_SIX_STRATEGY_UNSEEN_VIEW",
        "target_n": TARGET,
        "selected_n": len(selected),
        "cohort": "FROZEN_FRESH_C_300",
        "selection_rule": "First up to 24 UIDs in frozen Fresh C cohort order with a valid frozen input GLB, a license in the already locked {cc0, by, by-sa} allowlist, and finite vertex UVs on every nonempty mesh. No substitution after output inspection.",
        "eligibility_inputs_only": True,
        "method_predictions_or_metrics_read": False,
        "chronology_limit": "Selection is input-only and is performed without reading method outputs. The primary Fresh C run and its aggregate analysis already exist; the separate LLH/linear addendum was still running when this selection was frozen. Therefore this panel is a same-cohort, outcome-blind object subset, not an independent held-out cohort.",
        "cohort_uid_list_sha256": sha256(cohort_path),
        "cohort_manifest_sha256": sha256(cohort_manifest_path),
        "queue_lock_sha256": sha256(queue_lock_path),
        "asset_audit_sha256": sha256(asset_audit_path),
        "allowed_licenses": sorted(ALLOWED_LICENSES),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected": selected,
        "rejected_before_target_reached": rejected,
        "if_fewer_than_24": "Use all input-eligible objects found in the frozen cohort; do not replace or augment after method output review.",
        "downstream_scope": "Unlit glTF base-color and fixed unseen-view evaluation only. No human-fidelity, full-PBR, lighting, or seam-improvement claim follows from this panel.",
    }
    if len(selected) < 1:
        raise RuntimeError("no UV- and rights-qualified objects in the frozen Fresh C cohort")
    OUTPUT.write_text(json.dumps(selection, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": selection["status"], "selected_n": len(selected),
                      "target_n": TARGET, "rejected_before_target_reached": len(rejected),
                      "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
