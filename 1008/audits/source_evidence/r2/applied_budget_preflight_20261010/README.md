# Applied-budget CPU preflight snapshot — 2026-10-10

Author-review evidence only. This snapshot records protocol arithmetic and launch-gate status; it contains no new inference outcomes and is not part of the manuscript source ZIP.

Captured read-only from `/4T/CXY/MV-Painter-1010/1010/experiments` on 2026-10-10 UTC. Source branch: `codex/1010-experiments`; source HEAD: `0cac1b3505f34e4b95f0ed6d8776f049760a99a2`. At capture, `PREFLIGHT.json` was the only modified file among these source inputs. `SOURCE_SHA256SUMS.txt` records the copied bytes.

The 50-step CPU arithmetic preflight passed for the early, middle, and late profiles. Each has applied-scale sums of 82.5 in the deep and middle groups and 40.0 in the shallow group under the recorded caps. This checks the requested profile arithmetic only; equal applied-scale sums do not establish equal realized residual doses.

The experiment status records that no new inference was started. The GPU-idle gate was false (both RTX 5090 cards were using about 24 GiB of 32 GiB), and the historical base-model directory has no cryptographic content hash. The JSON uses null run-state fields rather than a positive inference or model-load record. No experiment result or temporal-placement conclusion follows from this preflight.
