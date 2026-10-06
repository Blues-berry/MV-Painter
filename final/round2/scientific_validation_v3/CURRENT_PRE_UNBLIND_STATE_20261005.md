# Current pre-unblinding evidence state — 2026-10-05

**Purpose.** Freeze the evidence and provenance state immediately before
opening condition-level results from `FRESH_CONFIRM_B`. The B integrity gate
has inspected row-level values only for finiteness and exact serialization;
no B condition means, contrasts, rankings, or plots have been computed.

**Repository state.** Branch `codex/scientific-validation-v3-20261002`, parent
HEAD `7e659c7e5695ecc7ea2a0fbd80f2110289b2804a`. This is a local snapshot
commit; nothing is pushed. Manuscript sources remain untouched and
`SCIENTIFIC_EVIDENCE_FREEZE=NO`.

## Evidence already available before B unblinding

### A2 — original 300-object cohort

- 4,800/4,800 rows are present.
- The old production object-resampling interaction bootstrap is retired for
  zero power against object-shared fixed interaction patterns.
- The exploratory object-cluster analysis finds Layer×Window interaction:
  FG-LPIPS Wald `W=481.081`, `p=8.04e-99`, interaction share 43.5%; FG-PSNR
  `W=1879.963`, `p<1e-300`, share 56.8%. This reanalysis is not independent
  confirmation on a new cohort.
- Source report: `A2_FINAL_INTERPRETATION.md`.

### A3 / A3b — dose interpretation

- A3 includes 4,800/4,800 rows. The shallow extreme is stress-test-only; the
  old A3 scale map is not matched-dose causal confirmation.
- A3b's frozen candidate map uses baseline deep/middle/shallow scales
  `1.25/1.25/0.50` and candidate highs
  `1.2625505713698246/1.306085471746726/0.80`.
- Residual-only calibration missed the frozen ±20% equal-dose criterion:
  deep −20.01%, middle −20.20%, shallow +98.98%. The map is therefore a
  **bounded-dose layer-window map**, not a dose-normalized map. No retuning was
  done. Its B confirmation outcomes are still unopened.
- Sources: `A3B_PROTOCOL_LOCK.md`, `A3B_DOSE_FEASIBILITY_AUDIT.md`.

### G — MV-Adapter cross-backbone result

- 98/99 frozen objects are valid; `g_0098` is a technical exclusion because
  its GLB has line geometry without triangle faces. No replacement was used.
- The corrected four-metric family has no corrected Layer×Window
  interaction. Current scope is 98/99 and adapter-architecture-specific;
  there is no universal transfer claim.
- Source: `CROSS_BACKBONE_MECHANISM_REPORT.md`.

### E — prospective texture/failure boundary

- On FRESH_CONFIRM_300, 9/10 corrected tests survive the locked Holm family.
  FG-LPIPS versus coverage is the non-survivor (`p_Holm≈0.0508`); FG-PSNR
  versus coverage survives (`p_Holm≈0.0352`). The four texture measures
  survive for both outcomes.
- This is a pre-registered analysis on the earlier cohort, not yet a
  replication on B.
- Sources: `PROSPECTIVE_FAILURE_BOUNDARY_REPORT.md`,
  `TEXTURE_COMPLEXITY_FAILURE_BOUNDARY.md`.

### Human preference evidence

- The amended blinded study and local site are frozen for 40 target
  participants (minimum 36), 24 comparisons per participant, and three
  pre-specified method pairs. The participant handoff archive SHA256 is
  `28bf23575a601ff797887793d65f35fe6062b4d30db5f844940109f5a0167982`.
- No participant responses have been collected. The retired, undistributed
  72-comparison package is superseded; no human preference claim is available.
- Sources: `human_study_site/HUMAN_STUDY_SITE_FREEZE.md`,
  `human_study_site/README_START_STUDY.md`.

### Generic schedules and 3D evidence

- The existing generic-schedule result is from FRESH_CONFIRM_300. LLH's
  FG-PSNR contrast with endpoint-matched linear warm-up is effectively null
  (`+0.005 dB`, Holm `p=0.81`); several smoother schedules are lower. This is
  cohort-specific existing evidence, not a B result.
- A unified same-draw bake report exists for 20 objects after frozen UV
  exclusions. LLH versus GFL is not significant on schedule-level PSNR
  (`+0.14 dB`, 95% CI `[-1.29, 1.65]`); image-space and baked 3D evidence
  remain discordant. The acceptance-oriented final bake report is outstanding.
- Sources: `AUTHORITATIVE_GENERIC_SCHEDULE_REPORT.md`,
  `UNIFIED_COREDRAW_BAKE_REPORT.md`.

## FRESH_CONFIRM_B — sealed state

- Frozen cohort: 150 disjoint unused objects. UID-list SHA256
  `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`;
  recursive source-input manifest SHA256
  `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`.
- Frozen family: 30 conditions × 150 objects = 4,500 rows, covering the
  A3b map, four fixed boundary pulses, native GFL/GFH/GC3, four true-global
  diagnostics, LFM-EXACT, LLH, and HLL. No generic schedules were added to
  this locked campaign.
- Both shards completed: 2,250 rows each. Raw ledger SHA256 values:
  - shard 0: `91e209fdea4feecde5da6f9a4eccba6d20c44968b9666efb27908fa9c1bcabf4`
  - shard 1: `20e13ec67c5209f1f36a6496f844e41d3716769218ac63cc53ce4447ad3ac976`
- Completion manifest SHA256 values:
  - shard 0: `ae4d241ccaeda03b886dd403823b3af654bf6afda4d90a206e98fe3c732cc827`
  - shard 1: `593d6dae6ddb801882f8747716cbbd10348bf586f94861e2a686dbe3e68c371a`
- Runner SHA256 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`,
  config SHA256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`,
  and checkpoint SHA256
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` match
both shard manifests.
- The integrity gate is **PASS**: 13,888 rendered input files byte/hash
  verified; 4,500/4,500 prediction PNGs and residual logs present; residual
  logs contain 50 finite steps with requested scales matching the run
  manifest; no duplicate/missing keys or non-finite values; rebuilt combined
  and per-condition CSVs match the raw ledgers exactly.
- Gate report SHA256:
  `b0d7d3607abdb70a01abc08c2a84df24958ff0bda897e0474f22fe65f1069d10`;
  gate script SHA256:
  `4f7e2f6beb1914ea0b45da51a38a5ae917a23cfc74c9f57fe99c676243326b1a`.
- The runner-hash discrepancy in two sub-locks is documented and closed by
  the pre-output combined lock and both runtime manifests. One transitive
  metric dependency, `geotex/metrics_extended.py`, was not included in the
  runtime source-hash registry; its current SHA256
  `ee32281fbee97e71050e8b2d74bbf6bc476efd372f6a898f1e0a3078863bb2b5`
  matches HEAD and has no worktree modification. This limitation is recorded
  in `FRESH_CONFIRM_B_RUNNER_HASH_PROVENANCE_20261005.md`.
- B condition-level means, contrasts, significance tests, and figures remain
  unopened and uncomputed at this snapshot.
- Sources: `FRESH_CONFIRM_B_FORMAL_PROTOCOL_LOCK.md`,
  `B_FORMAL_INTEGRITY_GATE.md`,
  `FRESH_CONFIRM_B_RUNNER_HASH_PROVENANCE_20261005.md`.

## Remaining gates at this point

- Unblind and analyze B in the frozen order; write the A3b map, boundary,
  cap/budget, and residual-dose reports, preserving the bounded-dose caveat.
- Resolve the generic-schedule extension question without modifying the
  locked 30-condition B campaign or describing a post-lock extension as
  independent confirmation.
- Finalize the unified 3D report and obtain the human study responses.
- Complete sanitized release, clean-clone reproduction, statistical
  reproducibility audit, narrative decision, evidence freeze, manuscript
  rewrite, adversarial review, and final acceptance gates.
