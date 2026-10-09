# Source evidence copies

The files in `r1/` and `r2/` are byte-identical copies of the frozen source
reports, metric summaries, CSVs, manifests, analysis scripts, and renderer
used by the 2026-10-08 review. Their original paths and SHA-256 values are
recorded in `1008/audits/R1_SOURCE_EVIDENCE_MANIFEST.csv` and
`1008/audits/R2_SOURCE_EVIDENCE_MANIFEST.csv`.

The `r1/superseded/` directory preserves historical bake reports for
provenance. Their prior seam and cross-view interpretations were superseded
by the native-sampler and seam-disposition audits. Do not use their old seam
metrics or renderer results as current evidence.

Large source images, GLBs, and training data remain in the original local
evidence store. This source package includes the associated hashes, metric
CSVs, audit reports, scripts, cohort manifests, rights records, and data
lineage needed to identify the evidence used here.

The R2 copies include Fresh B temporal contrasts, the same-cohort
budget-matched generic-schedule sensitivity, the A3b object-level CSV, Fresh C
object deltas, and focused analysis/audit scripts. Generated prediction
images and training data are not copied.
