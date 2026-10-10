# INPUT_IDENTITY_AUDIT — silent-substitution gate (2026-10-05)

**Mandatory P0 gate.** Question: did any formal A2/A3 row consume a different object than
the intended FRESH_CONFIRM UID, given that the dataset loader
(`MVPainter/src/data/mvpainter_dataset.py`) silently retries with a *random* substitute
object on missing files or load errors (`__getitem__` L439-447, L549-554) and returns a dict
without a UID field (L571-588), so the runner cannot directly verify the returned identity?

## 1. Evidence line 1 — substitution never triggered (logs)

The substitution path prints `"wrong path: …"` to stdout. All formal shard logs
(`formal/campaign_*/shard*.log`, A2/A3/B1B2/B3/C, 20 files): **`wrong path` count = 0**.
Dataset-level exceptions therefore never fired during any formal run. The Tracebacks present
in the logs are (a) end-of-run `os.replace` races on the throttled combined-CSV write (A2,
3 shards; ledger already complete) and (b) startup model-load retries (B3, before any row) —
neither touches row identity.

## 2. Evidence line 2 — in-runner integrity abort never fired

`scripts/run_validation_v3_experiment.py` L511-525 recomputes all six tensor hashes per
condition and **aborts the run** if any shared-input hash deviates from the object's first
condition (`shared-input integrity FAILURE`). All campaigns completed → no condition ever
saw different inputs than its siblings. Note this guard alone cannot distinguish "wrong
object, consistently across conditions" — hence lines 3-5.

## 3. Evidence line 3 — fingerprint uniqueness across the 300 objects

If a missing intended object had been replaced by *another cohort member*, two distinct UIDs
would share identical input hashes. The per-object fingerprint
SHA256(target‖normal‖depth‖global_embeds‖init_latent) is unique for 299/300 objects; the one
shared pair (`0099ab6d44…` / `0130e5149b…`) is proven to be a duplicate **source asset**
(different GLB bytes, pixel-identical renders in all 17 views × 3 modalities, 51/51) — not a
substitution. A replacement by a *non-cohort* object cannot produce this signature; lines 4-5
close that gap.

## 4. Evidence line 4 — bit-level re-derivation with the current code path (30 objects)

`audit_scripts/audit_deep_verification.py` re-instantiates the exact validation dataset
(current code, `MVP_DATA_ROOT=data/fresh_confirm_v3_renders`, `unique6`, same per-object
seeding `42+idx` as the runner) and recomputes all six tensor hashes for **30 deterministic
objects spanning every shard boundary** (indices 0-5, 73-78, 147-152, 221-226, 296-299) plus
the duplicate-asset pair. Result: **30/30 match the stored ledger hashes exactly**
(`AUDIT_DEEP_VERIFICATION.json`). The loader's preprocessing is deterministic and the stored
hashes are genuine hashes of the intended objects' rendered data.

## 5. Evidence line 5 — end-to-end live reproduction (3 objects × 3 conditions)

The current runner, executed fresh on 2026-10-05 (scratch RUN_DIR, formal artifacts
untouched), reproduced `a_baseline`, `a_deep_W3`, `a_shallow_W3` for cohort indices 0/149/299:
- 9 rows × 29 metric fields: **max |Δ| = 0.0** vs stored rows;
- all six input hashes identical;
- **9/9 prediction PNGs byte-identical** to the formal archives.

## 6. Conclusion

| Check | Result |
|---|---|
| Substitution trigger observed in logs | 0 occurrences in 20 shard logs |
| Cross-condition hash consistency | 0 violations (16,950 rows) |
| Fingerprint duplication | 1 pair, root-caused to duplicate source asset |
| Bit-level hash re-derivation (30 objects, all shard boundaries) | 30/30 exact |
| Live end-to-end reproduction | 9/9 rows exact, 9/9 PNGs byte-identical |

**OBJECT_IDENTITY: PROVEN for every completed formal row.** No row is invalidated; no rerun
required. Per-row evidence table: `audit_scripts/OBJECT_IDENTITY_PER_ROW.csv`.
