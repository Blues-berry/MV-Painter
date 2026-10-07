# FAC final disposition

**Final state: `REMOVED_FROM_REVISION`**

Audit date: 2026-10-07

Authority branch: `codex/cg-revision-evidence-closure-20261007`

Authority HEAD: `cf6287731bcf3ad31d135abf1feee64662a20c39`

FAC is not required for the revised paper's main contribution. The available FAC material does not meet the revision's stated reproducibility gate, so FAC has been removed rather than retained as an incompletely reproducible result. The revised main manuscript and supplement contain no FAC method, result, or dose-response material. No training, inference, GPU job, or participant-data analysis was run for this audit or revision edit.

## Artifact audit

| Required item | Finding |
|---|---|
| Source and configuration | Present: `geotex/train_fac_v2.py`, `geotex/eval_fac_v2.py`, `geotex/analyze_fac_table.py`, and `MVPainter/configs/mvpainter-geotex-fac-train.yaml`. The authority branch tracks the source/configuration, but not the FAC model/data package. |
| Checkpoints and model artifacts | FAC checkpoints and evaluation outputs exist in local experiment directories. The authority worktree contains the v5 FAC checkpoints/results and the v4 evaluation CSV/summary, but not the v4 checkpoint. The v3/v4 checkpoints and v3 results, plus the GeoTex v2 base checkpoint, are in the separate `/4T/CXY/MV-Painter` source workspace. These ignored artifacts are not recoverable from a clean checkout of the authority commit. |
| Training and inference commands | Training recipes exist in `geotex/run_fac_v4.sh`, `geotex/run_fac_v5.sh`, and `geotex/run_fac_v5_fix.sh`; the inference entry point is `geotex/eval_fac_v2.py`. They are not bound to each stored result by a committed run manifest. |
| Seed | Evaluation seed 42 is explicit in `eval_fac_v2.py`. Training has no seed argument or seed initialization in the trainer or retained launch scripts, and the checkpoints/logs do not record a training seed. |
| Input manifest | The tracked FAC config points to `train_objects_1200.txt` and `test_objects_300.txt`; the available training list has 1,200 entries. The submitted manuscript and supplement describe FAC as trained on 1,706 objects. No run-bound manifest or input hashes resolve this discrepancy. |
| Output manifest | Per-object metric CSVs, aggregate `summary.json` files, logs, and first-20 sample images are retained for some runs. No manifest hashes and binds the full outputs to the exact checkpoint, input list, code, and runtime. |
| Analysis script | `geotex/analyze_fac_table.py` is present. Its exact input/result bundle is not part of a clean checkout. |
| Environment | `MVPainter/requirements.txt` is available but does not pin a complete FAC runtime. The separate environment snapshot is not tied to the FAC runs, so the exact Python/PyTorch/CUDA/package environment is unverified. |
| Logs | Training/evaluation logs and per-object evaluation tables exist for multiple FAC attempts, split between local ignored outputs and the separate source workspace. They do not supply the missing seed or input/output provenance. |

The output CSVs and checkpoints are useful internal historical evidence, but their presence does not close the listed provenance gaps. A clean-checkout recovery cannot establish the exact historical training run without inventing missing metadata or running new training, which this revision explicitly excludes.

For local identification, the observed checkpoint SHA-256 values are:

| Artifact | SHA-256 |
|---|---|
| GeoTex v2 base | `d27a4f148949480c3188723e67c66cc14e5640d701a72aa9a5e9fd9724ef6d2c` |
| v3 LTAG | `4d0a3b6bfc72c4cd1a78ca12982896edacd55a5a04a44406fb176ec4cb067a56` |
| v3 LTAG+GSG | `3b0a0dbde9497be40de6fe9298d6a3d4e8e94c3b654263b2adbdbfa33f900193` |
| v3 Full FAC | `e5ee71c31c214a86a6ddc0fe5830476d599467af71b9310a79e3c13b383c41e5` |
| v4 frozen LTAG Full FAC | `cbb1e4c62c36664560c3897b516bbbb8512a5f3276f86d6e1d85c23b39006208` |
| v5 envelope penalty | `3867177f33f8d77f0383af754fd3424dec92ce079c6c477b6ea26632ef08d243` |
| v5 fidelity weighting | `bfb5d6a5fe9c01fb4377bf9c9620883ae0281a8bb2eef8ffe25ccb1f63306da7` |
| v5 gentle schedule | `186c6ebf8dfbd86142ca1c71aca1d660d362564c1de465aa0c2cd55976301606` |

## Manuscript action

The formal manuscript edit removed FAC descriptions and result claims from the main manuscript and supplement, including FAC controlled-re-examination tables and training-pool/checkpoint reproducibility entries. The revised paper does not claim that FAC is reproducible or released.

The source manuscript has been revised as described above. Reviewer-facing wording:

> We agree that the historical FAC experiment does not meet the reproducibility standard adopted for this revision. Because FAC is not required for the main contribution, we removed it from the revised manuscript rather than retain an incompletely reproducible result.

## Audit scope

This is a file/configuration/provenance audit only. It does not invalidate or recompute the historical FAC metrics, and it does not authorize new experiments. The historical files remain available for internal reference; they are not revision evidence for a reproducible FAC claim.
