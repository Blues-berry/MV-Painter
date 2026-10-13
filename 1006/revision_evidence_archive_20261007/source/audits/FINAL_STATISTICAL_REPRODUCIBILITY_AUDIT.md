# Statistical reproducibility audit

**Scope:** the anonymized clean-checkout release, its compact evidence table,
the validated A2 interaction test, the registered B bootstrap contrast, and
one complete independent clean-clone A2 condition (`a_middle_W5`, n=300).
This is not a paper-wide regeneration of every manuscript table and figure.

## Independent-process statistical reruns

The evidence-table builder was run in two separate Python processes from the
clean release checkout. Both runs produced byte-identical outputs:

| Output | SHA256 | Bytes |
|---|---|---:|
| `outputs/core_evidence_table.md` | `c18fe574477e25fdf36e4fedf383e2270594ad8fb48948379d964c92d86dedda` | 2,006 |
| `outputs/core_evidence_table.json` | `75e54962aa266cfad0f0414f24866a6aa5a80fe027ca876d73bd86f74d037b37` | 8,936 |

The registered B comparison (`LLH − LFM-EXACT`, n=150, 10,000 paired
bootstrap draws, seed `20261002`) was run twice in separate processes. Both
outputs were byte-identical (SHA256
`8aa060931e014ad8ddb554a4aa34bacd02717a9a9bf541689b46616d9ecb61c`); all
shared result fields match the official frozen JSON.

| Metric | Mean Δ | 95% CI | Favorable-object rate | Raw bootstrap p |
|---|---:|---:|---:|---:|
| FG-PSNR | +0.325165 dB | [+0.209001, +0.445849] | 54.0% | 0.0001 |
| FG-LPIPS | −0.004603 | [−0.005629, −0.003568] | 76.0% | 0.0001 |

The compact A2 cluster-Wald table reproduces FG-LPIPS W=481.081, p=8.045e−99,
interaction share 43.5%; and FG-PSNR W=1879.963, p<1e−300, share 56.8%.

## Clean-clone A2 `a_middle_W5` reproduction

The independent checkout regenerated all 300 objects from the frozen
`fresh_confirm_v3_renders` root. The executed checkout was local commit
`3c0d4b4037f95eea0815e46ee4357e4fb1f29109`; the final sanitized release is
`2a44d3e871ce374fe7d5cc2204e392a8be5b6626`. The release-only difference is a
README data-root correction. The runner was unchanged (SHA256
`2038d6e563aa0b5d64bc686c3395fde0e22d54b5cc44bc422d255610ecf6292b`).

- Official and reproduced ledgers each contain 300 distinct objects.
- All 1,800 input fingerprints (six per object) match exactly.
- All 36 non-runtime row fields match for all objects: 10,800 cell comparisons,
  zero mismatches, maximum numeric absolute difference 0.
- Prediction PNGs: 300/300 SHA256-identical.
- Residual JSON files: 300/300 SHA256-identical.
- The runner throttles CSV rewrites to each 16 completed rows; its final
  snapshot initially contained 288 rows although the authoritative JSON ledger
  and run manifest contained all 300. The supported
  `MVP_REBUILD_CSVS=1` path rebuilt CSVs from the completed ledger. The rebuilt
  300-row CSV has zero non-`elapsed_seconds` cell differences from the official
  condition CSV. Runtime seconds are expected to vary and are excluded from
  equality checks. No runner code was changed.
- The original failed preflight pointed at `rendered_full`, produced zero rows,
  and was stopped. It is not counted as a scientific result. The verified run
  used the correct frozen `fresh_confirm_v3_renders` root.

The raw run, rebuilt CSVs, run manifest, and checksums are preserved in the
external archive
`/4T/CXY/MV-Painter_artifacts/scientific_validation_v3_20261005/clean_clone_A2_a_middle_W5.tar.zst`
(SHA256 `fba63f5f01e94e4293e0ccd54d9330bbef526f5808e30f222b1b2217264fe729`,
109,603,212 bytes). Its 605 packaged file checksums passed; `zstd -t` passed.

## Limits

- The clean clone used model, checkpoint, and data mounted on the same host.
  This establishes same-host reproducibility, not a second-machine reproduction.
- These checks cover a complete A2 condition and core statistical outputs, not
  every row/figure/table in the manuscript.
- Final manuscript tables and figures have not been regenerated after the
  narrative rewrite. Paper-wide reproducibility remains open.

**Status:** `CORE_STATISTICS_REPRODUCED`;
`CLEAN_CLONE_A2_a_middle_W5=PASS`; `PAPER_WIDE_REPRODUCIBILITY=OPEN`.
