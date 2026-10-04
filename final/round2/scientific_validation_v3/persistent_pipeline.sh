#!/bin/bash
# Phase III persistent pipeline — survives SSH disconnect / session close.
# Runs: B3 resume -> C -> CSV rebuild -> G formal -> E + B3 decomposition +
# D archive -> F bake handoff + bake. Each stage is idempotent/resume-safe.
# Install: systemd --user unit (preferred) or tmux detached session.

set -u
cd /4T/CXY/MV-Painter
# systemd --user has no login env: force the anaconda toolchain first
export PATH=/home/ubuntu/anaconda3/bin:/usr/local/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/home/ubuntu/anaconda3/lib:${LD_LIBRARY_PATH:-}
V3=final/round2/scientific_validation_v3
COHORT=$V3/fresh_confirm_300.txt
LOG=/tmp/persistent_pipeline.log
export MVP_NUM_THREADS=10 OMP_NUM_THREADS=10 MKL_NUM_THREADS=10
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

log() { echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }

commit_stage() {
  git add -f "$V3" 2>/dev/null
  git commit -q -m "chore(validation-v3): persistent pipeline stage artifacts ($1)" 2>/dev/null
}

log "=== persistent pipeline start (pid $$) ==="

# Stage 1: campaigns B3 (resume) and C
log "stage1: campaigns B3,C"
python3 $V3/run_campaigns.py --cohort $COHORT --base-dir $V3/formal \
  --campaigns B3,C --gpus 0,1 >> "$LOG" 2>&1
log "stage1 rc=$?"
commit_stage "B3,C"

# Stage 2: rebuild merged CSVs from ledgers for all five campaigns
log "stage2: rebuild CSVs"
for CAMP in A2 A3 B1B2 B3 C; do
  MVP_RUN_DIR=/4T/CXY/MV-Painter/$V3/formal/campaign_$CAMP \
  MVP_OBJECT_LIST=/4T/CXY/MV-Painter/$COHORT \
  MVP_NUM_SHARDS=4 MVP_REBUILD_CSVS=1 \
  python3 scripts/run_validation_v3_experiment.py >> "$LOG" 2>&1
  log "rebuild $CAMP rc=$?"
done

# Stage 3: G formal (100 fresh objects, 16 conditions, 2 GPU shards)
log "stage3: G formal"
cd $V3
python3 run_validation_v3_g.py --manifest mvadapter_manifest_v3.json \
  --base-model ../mv_adapter/models/sd21_base \
  --adapter-path ../mv_adapter/models/mv-adapter \
  --output-dir g_formal --device cuda:0 --num-shards 2 --shard 0 >> /tmp/g_formal_s0.log 2>&1 &
P0=$!
python3 run_validation_v3_g.py --manifest mvadapter_manifest_v3.json \
  --base-model ../mv_adapter/models/sd21_base \
  --adapter-path ../mv_adapter/models/mv-adapter \
  --output-dir g_formal --device cuda:1 --num-shards 2 --shard 1 >> /tmp/g_formal_s1.log 2>&1 &
P1=$!
wait $P0 $P1
log "stage3 rc=$?"
cd /4T/CXY/MV-Painter
commit_stage "G formal"

# Stage 4: B3 decomposition + E (texture-complexity failure boundary) + D archive
log "stage4: B3 decomposition"
python3 $V3/analyze_residual_budgets.py \
  --run-dir $V3/formal/campaign_B3 \
  --conditions no_adapter,native_gfl,native_gfh,native_gc3,true_global_1p25,true_global_1p675,true_global_2p50 \
  --object-list $COHORT --reference native_gfl >> "$LOG" 2>&1
log "stage4 budgets rc=$?"

log "stage4b: E spearman (LLH vs native_gfl)"
python3 $V3/analyze_v3.py pairwise --run-dir $V3/formal/campaign_B3 \
  --a layer_llh --b native_gfl --metrics fg_psnr,fg_lpips \
  --out $V3/formal/campaign_B3/pairwise_layer_llh_vs_native_gfl.json >> "$LOG" 2>&1
python3 $V3/analyze_v3.py spearman --run-dir $V3/formal/campaign_B3 \
  --a layer_llh --b native_gfl --metrics fg_psnr,fg_lpips \
  --gt-stats $V3/gt_stats.json --gt-primary gt_fg_lap_var \
  --out $V3/formal/campaign_B3/spearman_texture_boundary.json >> "$LOG" 2>&1
log "stage4b rc=$?"

log "stage4c: D qualitative archive"
python3 $V3/build_qualitative_archive_v3.py >> "$LOG" 2>&1
log "stage4c rc=$?"
commit_stage "B3-decomposition,E,D"

# Stage 5: F bake handoff + blender bake (CPU) + unseen/seam metrics prep
log "stage5: F handoff"
python3 $V3/build_bake_handoff_v3.py >> "$LOG" 2>&1
log "stage5 handoff rc=$?"
if [ -f $V3/bake_handoff/BAKE_INPUT_HANDOFF_V3.json ]; then
  OBJECTS=$(python3 - <<'PY'
import json
h = json.load(open('final/round2/scientific_validation_v3/bake_handoff/BAKE_INPUT_HANDOFF_V3.json'))
print(','.join(o['object'] for o in h['objects']))
PY
)
  log "stage5 bake objects: $OBJECTS"
  blender-4.2.4-linux-x64/blender --background --factory-startup \
    --python geotex/cpu_texture_bake.py -- \
    --handoff $V3/bake_handoff/BAKE_INPUT_HANDOFF_V3.json \
    --output-dir $V3/bake_handoff/cpu_bake_v3 \
    --objects "$OBJECTS" \
    --methods gt,no_adapter,native_gfl,native_gfh,native_gc3,lfm_exact,layer_lhl,layer_llh \
    >> "$LOG" 2>&1
  log "stage5 bake rc=$?"
fi
commit_stage "F bake"

log "=== persistent pipeline DONE ==="
