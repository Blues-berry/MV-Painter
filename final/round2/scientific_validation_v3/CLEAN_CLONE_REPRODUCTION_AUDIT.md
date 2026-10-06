# Clean-clone A2 reproduction audit — 2026-10-05

## Reproduction result

The clean checkout regenerated the frozen A2 `a_middle_W5` condition for all
300 objects and matched the official campaign outputs. The run completed with
`status=complete`, `row_count=300`; its portable runner SHA256 is
`2038d6e563aa0b5d64bc686c3395fde0e22d54b5cc44bc422d255610ecf6292b`.

| Check | Result |
|---|---:|
| Distinct objects in each ledger | 300 / 300 |
| Six input fingerprints per object | 1,800 / 1,800 exact |
| Non-runtime row fields | 10,800 comparisons, 0 differences |
| Maximum numeric absolute difference | 0 |
| Prediction PNG SHA256 matches | 300 / 300 |
| Residual JSON SHA256 matches | 300 / 300 |
| Rebuilt per-object CSV non-runtime cells | 300 rows, 0 differences |

The only excluded row field is `elapsed_seconds`, a machine/runtime measure.

## CSV snapshot handling

The runner atomically refreshes CSVs every 16 completed rows to avoid repeated
full-table writes. On this run, the final ordinary snapshot had 288 rows while
the authoritative JSON ledger and completion manifest had 300. I used the
runner's documented `MVP_REBUILD_CSVS=1` mode to regenerate the CSV from the
complete ledger. The rebuilt CSV has 300 rows and matches every official
non-runtime cell. This is a snapshot bookkeeping limitation; no measurement
rows were missing from the JSON ledger or image/residual outputs. No runner
code was edited.

## Execution identity and limits

- Executed release checkout: `3c0d4b4037f95eea0815e46ee4357e4fb1f29109`.
- Final sanitized release checkout: `2a44d3e871ce374fe7d5cc2204e392a8be5b6626`; its only difference
  relevant here is the corrected README data-root example.
- Runtime: Python 3.13.5, PyTorch 2.7.1+cu128, NVIDIA RTX 5090.
- Frozen render root: `fresh_confirm_v3_renders`; all model assets were mounted
  on the same host. This is not a second-machine reproduction.
- Failed wrong-root preflight: zero rows, stopped, excluded from the result.

The full clean-run output is preserved outside Git at
`/4T/CXY/MV-Painter_artifacts/scientific_validation_v3_20261005/clean_clone_A2_a_middle_W5.tar.zst`
(SHA256 `fba63f5f01e94e4293e0ccd54d9330bbef526f5808e30f222b1b2217264fe729`,
109,603,212 bytes). The archive passed `zstd -t`; all 605 package checksums
passed.

This closes only the named A2 condition reproduction. Paper-wide tables and
figures still require regeneration after narrative approval.
