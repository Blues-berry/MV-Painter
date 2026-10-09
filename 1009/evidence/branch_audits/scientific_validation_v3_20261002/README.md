# Scientific validation V3: selected evidence

Source: `codex/scientific-validation-v3-20261002`, archived HEAD
`5c2c8829a1e19b42837761160dc4c14cf8f09045`. The branch has 163 unique
commits, 36,865 unique blobs (7,776,031,685 uncompressed bytes), and a
42,729-path tree delta. Its full tree removes the active 1008 files and the
current compact V3 release, so the history was not merged wholesale.

## Included

- `e1_e2/` preserves the 48-object, three-fixed-seed E1 sensitivity and E2
  static-factor summaries, cohort/design records, analysis code, integrity
  gates, and compact derived CSVs. E1 is realization sensitivity on a reused
  cohort. E2 varies static scales; it does not test temporal effects or equal
  realized dose.
- `mvdiffusion/` preserves seven 75-object per-object metric tables, run
  configurations, the paired-bootstrap analysis, and its report. The analysis
  script regenerated the panel CSV, paired-bootstrap JSON, and summary with
  byte-identical output. The result is specific to the correspondence-aware
  CPBlock interface and does not establish cross-backbone transfer.

The existing main-branch 1008 manuscript already contains the Fresh C primary
result and bounded cross-backbone narrative. This addition supplies compact
support for E1/E2 and the MVDiffusion result. It does not change manuscript,
Supplement, response, figures, or the submission package.

## Source and preservation

The ignored `next_stage_20261006` source files remain in the original
`/4T/CXY/MV-Painter/final/round2/scientific_validation_v3/` worktree. The
original worktree HEAD, index, and data were left unchanged. This selection
copies under 1 MB of reports, scripts, aggregate metric rows, and hash gates.
It excludes generated predictions, residual traces, GLBs, model weights,
checkpoints, caches, full image galleries, and participant-level responses.
The separate untracked 1006 candidate and non-human archive also remain at
their original paths for their own branch-by-branch review.

## Validation

- Recomputed MVDiffusion panel and paired-bootstrap outputs: 3/3 files matched
  the source byte-for-byte; the analysis checks all seven 75-row cohorts and
  their shared object identities.
- E1/E2 summary-to-analysis checks: 50 assertions passed, including all
  48-object E2 factor means and the recorded PASS integrity gates.
- No model inference or GPU work was run. The active manuscript SHA remains
  `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4`.
- The updated V3 readiness notes describe a later human-study analysis. Those
  aggregate claims remain for the separately listed human-study branch audit;
  no participant-level data were copied here.

`SHA256SUMS.txt` records hashes for the selected files in this package.
