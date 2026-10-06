#!/usr/bin/env python3
"""Record the completed locked development decision without authorizing Fresh D."""
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
DATA = PACKAGE / "data/e6_cap_calibration"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    with (DATA / "completion_recorder.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            state = json.loads((DATA / "E6_EXECUTION_STATE.json").read_text())
            if state["stage"] in {"DEVELOPMENT_COMPLETE_REVIEW_REQUIRED", "STOP_REQUIRES_RECORDED_REVIEW"}:
                break
            if not args.watch:
                raise RuntimeError("E6 still running; do not read partial quality results")
            time.sleep(10)
        ledger_path = PACKAGE / "evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json"
        ledger = json.loads(ledger_path.read_text())
        claim = next(c for c in ledger["claims"] if c["claim_id"] == "C15")
        selected = DATA / "E6_DEVELOPMENT_SELECTION.json"
        text = ["# E6 完成后的开发决策", "", "科学证据冻结：否；原稿不改。", ""]
        if state["stage"] == "DEVELOPMENT_COMPLETE_REVIEW_REQUIRED":
            result = json.loads(selected.read_text())
            source_id = "e6_development_selection"
            source = {"source_id": source_id, "path": str(selected.relative_to(ROOT)),
                      "sha256": sha(selected), "role": "Complete fixed 24-object, three-seed development selection; not confirmation."}
            ledger["sources"] = [s for s in ledger["sources"] if s["source_id"] != source_id] + [source]
            if source_id not in claim["authoritative_sources"]:
                claim["authoritative_sources"].append(source_id)
            claim["authority_status"] = result["status"] + "; NOVELTY_NOT_ESTABLISHED"
            claim["estimate"] = {"development_candidates": result["candidate_results"],
                                 "selected_multiplier": result["selected_multiplier"]}
            text += ["固定的 288 行开发比较及完整性检查已完成。", "",
                     "| 倍率 | 平均 FG-PSNR 差值 | 平均 FG-LPIPS 差值 | 开发资格 |",
                     "|---|---:|---:|---|"]
            for c in result["candidate_results"]:
                text.append(f"| {c['multiplier']} | {c['means']['fg_psnr']:+.6f} | {c['means']['fg_lpips']:+.6f} | {c['qualifies']} |")
            if result["selected_multiplier"] is None:
                claim["next_gate"] = "Candidate stopped under fixed development rule. Archive negative results; do not launch Fresh D for this method. Complete C3 empirical framing and retain R2.1 venue risk."
                text += ["", "无候选达到联合均值改善，按协议停止此方法；不启动 Fresh D。"]
            else:
                claim["next_gate"] = "Selected development candidate requires contribution-difference review and complete prospective Fresh D locks before independent outputs; no manuscript or human efficacy claim yet."
                text += ["", f"开发选择倍率：{result['selected_multiplier']}。需要差异复核与 Fresh D 事前锁定；本记录不自动启动确认。"]
        else:
            claim["authority_status"] = "STOP_REQUIRES_RECORDED_REVIEW"
            claim["next_gate"] = "Review recorded infrastructure/technical failure without changing magnitudes, cohort or caps; do not silently retune or start Fresh D."
            text += ["任务停止，不能声称开发比较完成。", "", state.get("error", "See local execution log.")]
        text += ["", "开发结果不是独立对象确认，不关闭 R2.1，也不证明感知或三维保真。"]
        (PACKAGE / "evidence/audits/E6_DEVELOPMENT_DECISION_20261006_ZH.md").write_text("\n".join(text)+"\n")
        ledger["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+"\n")
        subprocess.run([sys.executable, str(PACKAGE / "scripts/validate_claim_evidence_authority_ledger.py")], check=True)
        # Fresh C live stages can change its own input-audit artifacts; if that
        # makes authority validation fail, preserve the failure rather than
        # rewriting historical source hashes to force a pass.
        (DATA / "E6_COMPLETION_RECORDED.json").write_text(json.dumps({"status": "RECORDED_LOCAL_ONLY",
            "recorded_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "fresh_d_started": False, "scientific_freeze": False}, indent=2)+"\n")
        subprocess.run([sys.executable, str(PACKAGE / "scripts/build_source_inventory.py")], check=True)


if __name__ == "__main__":
    main()
