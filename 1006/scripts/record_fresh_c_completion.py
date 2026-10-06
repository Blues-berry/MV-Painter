#!/usr/bin/env python3
"""Record C's completed integrity-gated result without freezing the paper."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "1006"
DATA = PACKAGE / "data/fresh_c"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    with (DATA / "completion_recorder.lock").open("w") as driver_lock:
        fcntl.flock(driver_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            state = json.loads((DATA / "FRESH_C_CLOSURE_EXECUTION_STATE.json").read_text())
            if state["stage"] in {"COMPLETE_BOUNDED_C3_CONFIRMATION", "STOP_REQUIRES_RECORDED_REVIEW"}:
                break
            if not args.watch:
                raise RuntimeError("Fresh C is still in progress; no comparative result access")
            time.sleep(10)
        authority_lock = (PACKAGE / "data/evidence_authority_update.lock").open("w")
        fcntl.flock(authority_lock, fcntl.LOCK_EX)
        text = ["# Fresh C 闭环结果", "", "科学冻结：否。此记录不修改正文或关闭人工/新方法门禁。", ""]
        if state["stage"] != "COMPLETE_BOUNDED_C3_CONFIRMATION":
            text += ["流程停止，需要核查已记录的失败；不能变更 cohort/条件来追求正结果。", "", state.get("error", "See local execution state.")]
        else:
            gate = json.loads((DATA / "FRESH_C_INTEGRITY_GATE.json").read_text())
            if gate.get("status") != "PASS":
                raise RuntimeError("Fresh C closure requires full integrity PASS")
            result_path = DATA / "fresh_c_c3_minus_gfl_analysis.json"
            result = json.loads(result_path.read_text())
            primary = result["tests"]["fg_psnr"]
            low, high = primary["bootstrap_ci95"]
            if low > 0:
                disposition = "POSITIVE_ENDPOINT_SPECIFIC_NEW_OBJECT_SUPPORT"
                wording = "Fresh C supports a positive GC3−GFL FG-PSNR difference under its specific frozen native-cap protocol; report magnitude, heterogeneity and all secondary trade-offs."
            elif high < 0:
                disposition = "NEGATIVE_NEW_OBJECT_RESULT_CONFLICTS_WITH_HISTORICAL_DIRECTION"
                wording = "Fresh C contradicts the historical positive GC3−GFL FG-PSNR direction; withdraw a general C3 advantage and retain all cohort estimates."
            else:
                disposition = "INCONCLUSIVE_NEW_OBJECT_CONFIRMATION"
                wording = "Fresh C does not establish a positive GC3−GFL FG-PSNR difference; report uncertainty and withdraw general held-out superiority."
            ledger_path = PACKAGE / "evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json"
            ledger = json.loads(ledger_path.read_text())
            added = []
            for source_id, filename in (("fresh_c_completed_integrity", "FRESH_C_INTEGRITY_GATE.json"),
                                       ("fresh_c_completed_analysis", result_path.name),
                                       ("fresh_c_completed_cohort", "FRESH_C_COHORT_MANIFEST.json")):
                p = DATA / filename
                ledger["sources"] = [s for s in ledger["sources"] if s["source_id"] != source_id]
                ledger["sources"].append({"source_id": source_id, "path": str(p.relative_to(ROOT)),
                    "package_path": str(p.relative_to(ROOT)), "sha256": sha(p),
                    "role": "Completed revision-era Fresh C confirmation, not original preregistered replication."})
                added.append(source_id)
            claim = next(c for c in ledger["claims"] if c["claim_id"] == "C01")
            claim["authoritative_sources"] = list(dict.fromkeys(claim["authoritative_sources"] + added))
            claim["authority_status"] = disposition
            claim["estimate"]["fresh_c_primary"] = primary
            claim["allowed_wording"] = wording
            claim["next_gate"] = "Report all secondary endpoints and object heterogeneity; final narrative awaits E6/Fresh D and actual human/GLB gates. Do not transfer C3 evidence to LLH or the new module."
            ledger["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
            ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+"\n")
            text += [f"完整性：PASS；对象数：{result['n_objects']}。", "",
                     f"主终点均值：{primary['mean']:+.6f} dB；中位数：{primary['median']:+.6f} dB。",
                     f"95% bootstrap CI：[{low:+.6f}, {high:+.6f}] dB；有利对象比例：{primary['positive_fraction']:.1%}。", "", disposition, "", wording,
                     "", "全部六项校正后的次要结果和对象差值保存在同一 data/fresh_c 目录。"]
        report = PACKAGE / "evidence/audits/FRESH_C_COMPLETION_DECISION_20261006_ZH.md"
        report.write_text("\n".join(text)+"\n")
        # Do not rewrite old source hashes after reserve-stage changes to force
        # validity: keep a validation failure visible for provenance review.
        subprocess.run([sys.executable, str(PACKAGE / "scripts/validate_claim_evidence_authority_ledger.py")], check=True)
        subprocess.run([sys.executable, str(PACKAGE / "scripts/build_source_inventory.py")], check=True)


if __name__ == "__main__":
    main()
