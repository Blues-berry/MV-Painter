#!/bin/bash
# Waits for the background render to finish, then runs depth conversion and
# the technical audit + deterministic selection (cohort freeze artifacts).
set -x
cd /4T/CXY/MV-Painter

# wait until the render driver finishes (max ~3h)
for i in $(seq 1 120); do
  if grep -q "Rendered ok" /tmp/fresh_render.log 2>/dev/null; then
    echo "render driver finished"
    break
  fi
  sleep 90
done

tail -2 /tmp/fresh_render.log

# depth conversion (incremental; completes the remaining objects)
python3 final/round2/scientific_validation_v3/build_fresh_cohort.py depth --workers 10

# technical audit + deterministic selection + freeze artifacts
python3 final/round2/scientific_validation_v3/build_fresh_cohort.py audit

echo "FREEZE PIPELINE DONE"
