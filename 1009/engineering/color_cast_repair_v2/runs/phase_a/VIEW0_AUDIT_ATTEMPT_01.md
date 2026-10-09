# View-0 cache-origin audit attempt 01

- Status: stopped before data-image access, dataset construction, model load, or embedding inference.
- Cause: the runner's hard-coded expected config SHA omitted one `a` and rejected the correct frozen config (`295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`).
- The runner had read only the frozen UID list and the already completed input-only provenance CSV before this guard. It read no prediction PNGs, GT metrics, or repair outputs and allocated no GPU memory.
- Failure log: `view0_cache_origin_console.log`.
- Correction: fix the expected literal, then rerun the same locked 98-object input-only audit. The object rule and analysis are unchanged.
