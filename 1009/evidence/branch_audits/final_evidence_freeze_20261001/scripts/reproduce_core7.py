#!/usr/bin/env python3
"""Rebuild the frozen Core-7 audit in a temporary legacy path layout."""
from __future__ import annotations
import hashlib, shutil, subprocess, sys, tempfile
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parents[3]
SCRIPT = PKG / "scripts/final_core7_forensic_stats_20261001.py"
SOURCES = {
    "no_adapter": ("inputs/no_adapter/per_object_metrics.csv", "final/round2/coordination/core7_same_runner_completion_20261001/formal_no_adapter/per_object_metrics.csv"),
    "global_fixed_low": ("inputs/global_fixed_low/per_object_metrics.csv", "final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930/global_fixed_low_per_object_metrics.csv"),
    "global_fixed_high": ("inputs/global_fixed_high/per_object_metrics.csv", "final/round2/coordination/core7_same_runner_completion_20261001/formal_global_fixed_high/per_object_metrics.csv"),
    "global_c3": ("inputs/global_c3/per_object_metrics.csv", "final/round2/coordination/main_backbone_robustness1_20260930/r0_completion_global_c3/per_object_metrics.csv"),
    "layer_fixed_mean": ("inputs/layer_fixed_mean/per_object_metrics.csv", "final/round2/coordination/layer_confirmation_20260930/layer_fixed_mean_per_object_metrics.csv"),
    "layer_lhl": ("inputs/layer_lhl/per_object_metrics.csv", "final/round2/coordination/layer_confirmation_20260930/layer_lhl_per_object_metrics.csv"),
    "layer_llh": ("inputs/layer_llh/per_object_metrics.csv", "final/round2/coordination/layer_confirmation_20260930/layer_llh_per_object_metrics.csv"),
}
MANIFESTS = {
    "no_adapter": ("inputs/no_adapter/protocol_manifest.json", "final/round2/coordination/core7_same_runner_completion_20261001/formal_no_adapter/protocol_manifest.json"),
    "global_fixed_low": ("inputs/global_fixed_low/protocol_manifest.json", "final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/layer_confirmation_20260930/global_fixed_low_protocol_manifest.json"),
    "global_fixed_high": ("inputs/global_fixed_high/protocol_manifest.json", "final/round2/coordination/core7_same_runner_completion_20261001/formal_global_fixed_high/protocol_manifest.json"),
    "global_c3": ("inputs/global_c3/protocol_manifest.json", "final/round2/coordination/main_backbone_robustness1_20260930/r0_completion_global_c3/protocol_manifest.json"),
    "layer_fixed_mean": ("inputs/layer_fixed_mean/protocol_manifest.json", "final/round2/coordination/layer_confirmation_20260930/layer_fixed_mean_protocol_manifest.json"),
    "layer_lhl": ("inputs/layer_lhl/protocol_manifest.json", "final/round2/coordination/layer_confirmation_20260930/layer_lhl_protocol_manifest.json"),
    "layer_llh": ("inputs/layer_llh/protocol_manifest.json", "final/round2/coordination/layer_confirmation_20260930/layer_llh_protocol_manifest.json"),
}
PRIOR = ("inputs/prior/PAIRED_BOOTSTRAP_CORE7.csv", "final/round2/coordination/core7_same_runner_completion_20261001/PAIRED_BOOTSTRAP_CORE7.csv")
OUTPUTS = ("CORE7_FINAL_AGGREGATES.csv", "CORE7_FINAL_PAIRED_STATISTICS.csv", "CORE7_ROW_AUDIT.json")

def main() -> None:
    with tempfile.TemporaryDirectory(prefix="core7-branch-audit-") as td:
        root = Path(td)
        for pairs in (SOURCES, MANIFESTS):
            for src_rel, staged_rel in pairs.values():
                target = root / staged_rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PKG / src_rel, target)
        prior = root / PRIOR[1]
        prior.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PKG / PRIOR[0], prior)
        script = root / "scripts/final_core7_forensic_stats_20261001.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SCRIPT, script)
        subprocess.run([sys.executable, str(script)], check=True, cwd=REPO)
        generated = root / "final/round2/coordination/final_evidence_freeze_20261001"
        expected = REPO / "1008/audits/source_evidence/r2/core7"
        for name in OUTPUTS:
            actual = (generated / name).read_bytes()
            committed = (expected / name).read_bytes()
            if actual != committed:
                raise SystemExit(f"FAIL: {name} differs from the checked-in result")
            print(f"PASS: {name} byte-identical ({hashlib.sha256(actual).hexdigest()})")

if __name__ == "__main__":
    main()
