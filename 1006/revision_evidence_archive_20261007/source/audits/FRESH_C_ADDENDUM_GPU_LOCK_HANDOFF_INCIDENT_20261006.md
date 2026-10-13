# Fresh C addendum GPU lock handoff incident

- Status: recorded before addendum inference.
- Primary Fresh C integrity: PASS (300 objects, 1200/1200 rows).
- Cause: the primary closure driver retained `scientific_gpu_campaign.lock` while waiting for the addendum watcher; the addendum launcher requested the same lock before starting workers.
- At record time, the addendum had not written shard rows or run manifests. No addendum inference or metric inspection had occurred.
- Resolution: release the completed primary driver's lock so the already frozen addendum can acquire the lease and execute unchanged.
- Protocol, cohort, condition set, source hashes, input embeddings, and primary outputs remain unchanged.

Machine record: [`FRESH_C_ADDENDUM_GPU_LOCK_HANDOFF_INCIDENT_20261006.json`](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_ADDENDUM_GPU_LOCK_HANDOFF_INCIDENT_20261006.json).
