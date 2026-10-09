# Code and runner authority

## Current editable and build paths

- Active manuscript: 1008/manuscript/revision_01549_restored/manuscript_1008.tex.
- Active Supplement: 1008/manuscript/revision_01549_restored/Supplementary_1008.tex.
- Project build scripts: build_revision_1008.sh, build_supplement_1008.sh, and build_marked_up_1008.sh in that directory.
- Fresh C figure reconstruction: build_fresh_c_qualitative_figures.py; layout comparison: build_figure_layout_comparison.py. The resulting main figures and per-object source/ROI hashes are frozen in the author-review package.
- Core implementation files in the private branch and their SHA-256 values:
  - MVPainter/mvpainter/model_unet_geotex.py: b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0
  - geotex/data_utils.py: e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3
  - geotex/explore_contradiction.py: 5da7fff22ea73b6d9500603d0905eda9a1ac9c44406346b259f3aba368b6ca13
  - geotex/eval_exploration.py: adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5
  - geotex/round2_main_eval.py: a461e5ab6559072ab9cb5c86be8061b02e39443b0d8f32caa7172cbe686ff4c8
  - geotex/round2_runner.py: 15c6a18b822c8d14d75c76393d5e5a2190acc5de511ddecd68f829752a15bf89

## Frozen evidence runners

Fresh C is the 300-object R1.2 paired study, independent from the historical 24-object schedule-selection probe and the older 01549 cohorts. Its primary and same-cohort addendum share one frozen checkpoint, runner, cohort, inputs, views, metric code and object seed policy. The exact C3 minus GFL FG-PSNR effect is +0.522352 dB, 95% object-bootstrap CI [+0.404160,+0.640669]. The scale caps are deep/middle/shallow 3.0/3.5/0.8.

- Fresh C checkpoint SHA-256: 0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0.
- Fresh C runner SHA-256: e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3.
- Frozen runner snapshot: evidence_sources/run_validation_v3_experiment_frozen.py; byte-identical to source commit 5c2c8829a1e19b42837761160dc4c14cf8f09045:scripts/run_validation_v3_experiment.py.
- Fresh C protocol snapshot: evidence_sources/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md.
- Fresh C integrity gates and paired analysis are in 1008/audits/source_evidence/r2/fresh_c/.

The snapshot is for provenance. It contains environment-specific absolute roots and depends on external model/config/checkpoint and input data; it is not represented as runnable from a clean checkout. Do not edit the snapshot and then claim exact reproduction.

Fresh B is a separate 150-object cohort with a separately frozen lock, even though the checkpoint and runner hashes overlap. Its lock is evidence_sources/FRESH_CONFIRM_B_FORMAL_PROTOCOL_LOCK_20261005.md. Do not pool Fresh B with Fresh C or call it an independent Fresh C replication.

## Statistical and archived code

The 2026-10-05 scientific decision report and cross-backbone mechanism report are retained as dated source snapshots under evidence_sources/. The latter supersedes the manuscript's invalid production additive-residual bootstrap inference for MV-Adapter interaction: its null is zero-power. Use only the post hoc exploratory object-cluster robust Wald results, with the exploratory status and four-metric Holm correction visible. No corrected interaction metric is significant.

Historical code and experiment families remain distinct. The 01549 v1 main adapter, 01549 v2 FAC/strict-276 adapter, Fresh C, Fresh B, V3 FRESH_CONFIRM_300, MV-Adapter, and MVDiffusion do not form one runner or one cohort. Their different checkpoints, adapter interfaces, seeds and metrics must not be normalized in prose or merged into a single estimate.
