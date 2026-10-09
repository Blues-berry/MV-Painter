# Phase B attempt 02 — stopped before generation

- Started: 2026-10-09T05:24:50.490346+00:00
- Ended: 2026-10-09T05:26:02.156005+00:00
- Runner SHA-256: 2a0f3f0158520d15b2fbb3bbddd6895a0b51440e10f830306d8965bfcd784817
- Checkpoint SHA-256: 0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0
- Config SHA-256: 295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b
- Device: GPU 1, RTX 5090; model components reached 7/7; adapter loaded.
- Generation count: 0. No prediction PNG or metric was produced by this attempt.
- Failure: `AttributeError: 'dict' object has no attribute 'detach' at geo feature hashing; no diffusion call completed.`
- Cause verified from `GeoTexEncoder.forward`: it returns a dict of named feature tensors (`x1`–`x4` and UNet aliases); the runner treated the dict itself as a tensor.
- Launch used `ionice -c3` and `nice -n 10`; GPU memory returned to baseline after process exit.
- The previous successful preflight console logs remain in `../preflight_console.log` and `../preflight_amendment02.log`. Its runtime manifest was replaced when this attempt initialized; the failed attempt's raw runtime is preserved here.
