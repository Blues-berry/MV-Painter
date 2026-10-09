# Fresh C C3–GFH post-hoc audit (2026-10-07)

This is a selective source integration from archived branch `codex/cg-round2-1008-revision-20261008` (source HEAD `5e3e88e95c81e28200704988e4aaa7ef88239b1b`). The complete Fresh C source dataset was left at its existing local location, `/4T/CXY/MV-Painter/1006/data/fresh_c`; no images, embeddings, checkpoints, or per-object raw table were copied into this repository.

The analysis script was rerun read-only against that source. The integrity gate passed all 23 checks for 300 paired objects, 1,200 source rows, matching UIDs/indices/seeds/input hashes, and a common runner, checkpoint, and metric implementation. The raw CSV SHA-256 is `6967375a66a523beeab2089a9e51fbd68b756f2a07b13439d443078bd4482cd6`; the analysis script SHA-256 is `ec87a8b5b729b198a501d66a49850bac3b54bc7a090b9d33e7e50050b59a251d`.

The audit is reviewer-requested and post hoc, uses 10,000 paired object-bootstrap resamples with `numpy.default_rng(20261002)`, and reports no p-values. It is not a registered confirmatory comparison, independent replication, equivalence test, or non-inferiority test. The point estimates and directions agree with the active manuscript's C3–GFH table. The Edge-SSIM interval from this reproducible seed is [-0.020803, -0.016790]; the active manuscript uses [-0.02084, -0.01683]. Both are below zero and support the same endpoint-specific direction. The active manuscript and its certified package were not changed; this alternate bootstrap realization is retained as a source audit, not substituted into the paper.

The source integrity JSON records the absolute input paths and source hashes observed during this local verification. The original source files remain in their original worktree.
