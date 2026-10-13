# Historical LHL quarantine manifest — 2026-10-01

## Binding status

`QUARANTINED / PROVENANCE INSUFFICIENT`. The archived LHL record has no
recoverable runner-time source snapshot. Prior forensic work excludes
preprocessing realization, GT/mask/metric drift, data-file drift, and the
tested conditional-augmentation explanations; the remaining cause is an
unidentifiable transient code/state difference. Do not invent a benign cause.

The old unseeded-RNG explanation is refuted as the cause of the 1.8 dB mean
gap. The independent R0/R1 realization shift is small, and disabling the
tested conditional augmentation did not reproduce the archived predictions.
The archived record and its companion historical means remain preserved as
forensic artifacts only.

## Forbidden quantitative reuse

Do not include in any active table, abstract, claim, or cross-method
comparison:

- archived Full-PSNR `22.052`, FG-PSNR `14.776` (rounded `14.78`), or the
  associated archived Full/FG SSIM and LPIPS means;
- the archived-vs-seeded `12.97 vs 14.78` comparison or its `r=0.66` as an
  explanation of the mean gap;
- any statement that Python RNG / reference-preprocessing randomness caused
  the archived mean discrepancy.

The current seeded Core-7 LHL mean (`FG-PSNR 12.974`, etc.) is valid as a
Core-7 row and is **not** quarantined. The forbidden comparison is its use
against the archived 14.78 record.

## Source scan and hits

`scripts/index_historical_lhl_hits_20261001.py` scanned tracked human-readable
`.md/.tex/.txt/.py/.sh/.yaml/.yml` sources for `14.776`, `22.052`, `14.78`,
`12.97`, `unseeded`, `Python RNG`, `reference preprocessing randomness`, and
`archived LHL`. The complete path/line/marker/excerpt index is
`HISTORICAL_LHL_SEARCH_HITS.csv`. Generated metric CSV/JSON/log files and
vendored `final/tools/` were excluded because bare numeric substrings occur
as ordinary measurements or dictionary content; preserved historical data
remain untouched.

### Active manuscript sources — unresolved, must fix in the next authorized rewrite

| File and lines | Hit | Status |
|---|---|---|
| `final/round2/final_round2.tex:472-481` | archived-runner/unseeded-Python-RNG explanation and archived means including `22.052` / `14.776` | **ACTIVE / BLOCKING** |
| `final/round2/final_round2.tex:604-605` | `12.97 vs 14.78`, `r=0.66`, and archived unseeded cause language | **ACTIVE / BLOCKING** |
| `final/round2/supplementary_round2.tex:471-475` | same unseeded explanation and archived mean comparison | **ACTIVE / BLOCKING** |
| `final/round2/response_letter_round2.md:113-116` | same archived comparison and “single unseeded run” framing | **ACTIVE / BLOCKING** |

No manuscript, supplement, or response-letter file was edited in this task.
Gate 3 therefore remains failed until these claims are removed/replaced in the
separately authorized manuscript rewrite.

### Historical and audit-only hits

- `final/round2/archive/revision_before_next_round_20260930/final_round2.tex:539`
- `final/round2/archive/revision_before_layer_lhl_20260929/LAYER_LHL_HANDOFF_20260929.md:39`
- `final/round2/coordination/LAYER_LHL_HANDOFF_20260929.md:55`
- `final/round2/coordination/final_audit_20261001/rescued_tmp_20261001/official_lhl_v2_merged/OFFICIAL_LAYER_LHL_REPORT.md:10-15`
- `final/round2/coordination/core7_same_runner_completion_20261001/ARCHIVED_LHL_PROVENANCE_AUDIT.md`
- `final/round2/coordination/final_audit_20261001/ARCHIVED_LHL_PROVENANCE_AUDIT.md`
- `final/round2/coordination/final_audit_20261001/historical_result_exclusion_reason.md`
- `final/round2/coordination/final_acceptance_20260930/EVAL_AUGMENTATION_AUDIT.md` and `revision_next_20260930/EXPERIMENT_PROTOCOL_LOCK.md` (contain the now-retired RNG attribution)

The `ARCHIVE_SUPERSEDED` and `AUDIT_OR_COORDINATION_RECORD` rows in the hit
index preserve history and audit reasoning; they are not active evidence.
The seeded R0 LHL row in the active Supplementary results table is an active
Core-7 measurement and should not be confused with the archived record.

## Related quarantines

- Cross-panel absolute values mixing capped and uncapped runners: quarantined;
  use the capped same-runner Core-7 for the current strict-276 baseline family.
- The old `uv_seam_discontinuity=0.0` 48/48 output: invalid and superseded by
  the corrected ΔE00 seam audit.
- Legacy CAI “C3 uniquely selected / only promising” claims in
  `final/final_0903.tex` and `final/final_0903_marked_addonly.tex`: superseded.
  The current round-2 source instead treats CAI as diagnostic and does not
  identify a unique schedule.
- Additive causal arithmetic over overlapping LLH−GFL contrasts: forbidden;
  retain only “combined allocation effect.”

Do not delete old artifacts. Preserve them as
`SUPERSEDED / QUARANTINED`.
