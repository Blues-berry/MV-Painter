#!/usr/bin/env bash
# Robustness-1 formal run launcher (task-gated).
# - Waits for a GPU with ZERO compute processes (both GPUs belong to the
#   other agent until then; no preemption).
# - Then, on that GPU only:
#     1. R1 smoke/formal start: object 0 x Core-5 (MVP_OBJECT_LIMIT=1) —
#        exercises the 5-method in-run integrity path before the bulk run;
#     2. R1 formal: 276 x 5 = 1380 rows (resume-safe);
#     3. R0 anchor re-check: 10 objects, seed 42 namespace, layer_llh via
#        this script, compared to the frozen R0 rows (drift quantified;
#        chain aborts if any metric drifts > 1e-3 — gates R0-C3 only);
#     4. R0 global_c3 completion: 276 rows (pre-registered matrix completion).
set -euo pipefail

ROOT=/4T/CXY/MV-Painter
TASK=$ROOT/final/round2/coordination/main_backbone_robustness1_20260930
LOG=$TASK/formal_run.log
cd "$ROOT"

echo "[launcher] $(date -Is) waiting for a free GPU (zero compute processes)..." | tee -a "$LOG"
GPU=""
while [ -z "$GPU" ]; do
  for g in 0 1; do
    n_proc=$(nvidia-smi --id="$g" --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -c . || true)
    if [ "$n_proc" -eq 0 ]; then
      GPU=$g
      break
    fi
  done
  if [ -z "$GPU" ]; then
    sleep 300
  fi
done
echo "[launcher] $(date -Is) GPU $GPU is free; binding" | tee -a "$LOG"
export CUDA_VISIBLE_DEVICES=$GPU
export MVP_DEVICE=cuda:0

echo "[launcher] step 1: R1 smoke (object 0 x Core-5, starts the formal rows)" | tee -a "$LOG"
MVP_RUN_DIR="$TASK/realization1_core5" MVP_OBJECT_LIMIT=1 \
  python3 scripts/run_robustness1_core5_20260930.py 2>&1 | tee -a "$LOG"

echo "[launcher] step 2: R1 formal 276 x Core-5 (1380 rows, resume-safe)" | tee -a "$LOG"
MVP_RUN_DIR="$TASK/realization1_core5" \
  python3 scripts/run_robustness1_core5_20260930.py 2>&1 | tee -a "$LOG"

echo "[launcher] step 3: R0 anchor re-check (10 objects, seed 42, layer_llh)" | tee -a "$LOG"
MVP_RUN_DIR="$TASK/r0_anchor_llh_10" MVP_SEED_BASE=42 MVP_SCHEDULES=layer_llh MVP_OBJECT_LIMIT=10 \
  python3 scripts/run_robustness1_core5_20260930.py 2>&1 | tee -a "$LOG"

echo "[launcher] step 3b: anchor comparison vs frozen R0 rows (gates R0-C3 completion only)" | tee -a "$LOG"
python3 - "$TASK" <<'PY' 2>&1 | tee -a "$LOG"
import json, sys
from pathlib import Path
task = Path(sys.argv[1])
anchor = {int(r["object_idx"]): r for r in json.loads((task / "r0_anchor_llh_10/rows.json").read_text())}
frozen_rows = json.loads(Path("/4T/tmp/mvpainter-layer-confirmation-20260930/layer_llh_rows.json").read_text())
frozen = {int(r["object_idx"]): r for r in frozen_rows}
metrics = ["fg_psnr","fg_ssim","fg_lpips","full_psnr","full_ssim","full_lpips","edge_ssim"]
max_abs = {}
for idx in sorted(anchor):
    for m in metrics:
        d = abs(float(anchor[idx][m]) - float(frozen[idx][m]))
        max_abs[m] = max(max_abs.get(m, 0.0), d)
worst = max(max_abs.values())
print("[anchor] per-metric max |delta| vs frozen R0 rows:", {k: round(v, 8) for k, v in max_abs.items()})
result = {"max_abs_delta": max_abs, "worst": worst, "gate": "PASS" if worst <= 1e-3 else "FAIL"}
(task / "r0_anchor_llh_10/anchor_comparison.json").write_text(json.dumps(result, indent=2) + "\n")
if worst > 1e-3:
    print("[anchor] FAIL — investigate before formal rows / R0-C3 completion")
    sys.exit(1)
print("[anchor] PASS")
PY

echo "[launcher] step 4: R0 global_c3 completion (276 rows, seed 42 namespace)" | tee -a "$LOG"
MVP_RUN_DIR="$TASK/r0_completion_global_c3" MVP_SEED_BASE=42 MVP_SCHEDULES=global_c3 \
  python3 scripts/run_robustness1_core5_20260930.py 2>&1 | tee -a "$LOG"

echo "[launcher] $(date -Is) ALL FORMAL RUNS COMPLETE" | tee -a "$LOG"
