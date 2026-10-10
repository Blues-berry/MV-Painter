# Direction and sign audit — 2026-10-06

## Verdict

**`SIGN_DIRECTION_ERROR = 0`.** The independent checker rejoined per-object rows from the frozen Fresh C primary and addendum, then recomputed the mean, median, 95% object-bootstrap interval, paired p-value, Holm-adjusted p-value, favorable-object fraction, and metric direction for **28/28 registered checks**. Status: PASS. Machine result: `1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json`.

The checker is called after both integrity gates and frozen analyses by `1006/scripts/run_fresh_c_locked_analyses_with_sign_audit.py`. A failed integrity gate prevents analysis; any summary mismatch fails the audit. It is not a substitute for protocol locking and does not alter endpoints or multiplicity families.

## Controlling LPIPS convention

Every contrast is written A−B. LPIPS is lower-is-better, so a positive value favors B and a negative value favors A. Therefore **positive `LLH−linear` FG-LPIPS favors generic linear**.

| Source | Contrast | FG-LPIPS | 95% interval | Holm p | Direction |
|---|---|---:|---:|---:|---|
| Historical Campaign C, retrospective sibling runs, N=300 | LLH−linear | +0.001226 | [+0.000692, +0.001816] | 0.0016 | generic linear |
| Fresh B, post-lock same-cohort sensitivity, N=150 | LLH−linear | +0.0011 | [+0.0004, +0.0019] | 0.0024 | generic linear |
| Fresh C revision-era addendum, N=300 | LLH−linear | +0.001372 | [+0.000762, +0.002081] | 0.000114 | generic linear |

These are distinct cohorts and analysis classes; they are not pooled. The historical reconstruction is documented in `CAMPAIGN_C_LLH_LINEAR_DIRECTION_AUDIT_20261006.md` and corrected by `LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md`.

## Scope of the search and disposition

- **Current controlling report, ledger, and figure logic:** the source-row audit, erratum, current Fresh C comparison report, E0 claim ledger, and strategy-figure generator encode the lower-is-better LPIPS direction correctly. The historical trade-off figure labels positive LLH−linear LPIPS as favoring linear; its generator checks the source-row means before rendering.
- **Superseded prose:** `final/round2/scientific_validation_v3/AUTHORITATIVE_GENERIC_SCHEDULE_REPORT.md` contained the direction/interpretation error. Its original copy is retained unchanged at `1006/evidence/audits/superseded/AUTHORITATIVE_GENERIC_SCHEDULE_REPORT_AS_RECEIVED.md`; it is not an authority. The correction scope is logged in `LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md`.
- **Submitted and candidate manuscripts:** 01549 remains byte-preserved. The current 1006 candidate is a pre-Fresh-C draft and must be rebuilt only after evidence freeze; it is not yet the numerical authority for the new addendum. Its existing B extension correctly says positive LPIPS favors linear. No final response letter is being generated before freeze.
- **Format-reference copies and archived snapshots:** old text retained under `1006/manuscript/source_format/` is historical source/reference material, not controlling prose. It must not be copied forward without the erratum and current ledger. Current readiness and reviewer matrices are updated to the 28-check audit.
- **Other listed metric classes:** the current Fresh C family contains FG/Full PSNR, LPIPS, SSIM, and Edge-SSIM; it has no CIEDE2000 or texture-error endpoint. The historical C3D/GLB and texture diagnostic families are separately identified in their audits. No sign conversion or win-rate interpretation is transferred across those families; each uses its own stored `metric_direction`/favorable-condition field.

The package-level sweep was limited to current 1006 evidence/narrative/figure sources and the named V3 source tree. Superseded files remain searchable for traceability but are explicitly listed as non-authoritative. No correction was made by changing a cohort, metric, contrast, figure endpoint, or manuscript result.
