# Public and private upload scope

The d59 evidence snapshot remains the scientific claim authority. The 1008
revision branch is based on d59 for the private repository candidate.

## Public candidate

Pushed as a new branch:
`origin/codex/cg-round2-1008-public-sanitized-20261008`.

The public repository already contains four participant-level CSVs in
`final/round2/scientific_validation_v3/human_study_results_20261006/`. Their
first introduction is commit f5bad8a1e6ca4265c1823eaa26b2775313de4c96, whose
parent is 12da08c7056f5f0c36677668d640477bfb249454.

The public candidate branch is built from the d59 tree snapshot with those four
CSV paths removed, and its parent is the pre-data commit 12da08c7. This keeps
the candidate branch history free of those participant-level records without
rewriting any existing public ref. Existing public refs remain unchanged and
still contain the earlier data.

The public candidate retains all source documents, reports, logs, JSON, CSV,
scripts, and 24 selected formal qualitative panels. It omits bulk image
renders, cached NPZ files, GLB intermediates, and bytecode. Every omission is
listed by path, size, Git blob ID, and reason in
`final/round2/scientific_validation_v3/OMITTED_EXPERIMENT_ARTIFACTS.csv`.
The 1006 public-profile archive likewise retains its non-conflicting reports,
logs, scripts, and CSVs (413 files); generated images/figure exports and
candidate manuscript files are omitted. The two same-path audit conflicts
were reviewed: the d59 versions remain in the candidate tree, with the
alternative source blobs and final decisions recorded in the import and
conflict-audit manifests.

The full B and generic-extension campaign records are also included at their
original `formal/` paths: 5,824 non-image files (per-object residual JSON,
result JSON, CSVs, and run logs; 596,128,347 bytes). All 11,524 source files
were verified against the retrospective campaign checksum inventory; 5,700
generated PNGs were verified and omitted. The source inventory labels itself
retrospective after outcome disclosure, so it establishes file integrity but
not pre-unblinding status. The imported residual logs reproduce the stored
10-condition dose/cap audit; the H5 statistics rebuild exactly from the
campaign CSVs and frozen GT manifest.

## Private candidate

Pushed as a new branch:
`mvpainter/codex/cg-round2-1008-revision-20261008`.

The private candidate is based on d59 and retains the four participant-level
CSV files because the repository is private. It has the same curated v3
artifact selection and keeps the complete non-human document, log, report,
script, and CSV records. A separate private-only archive contains 24
human-study protocol, audit, analysis-code, and aggregate-result files; the
two generated plots are omitted. Those study records are not promoted as
confirmatory paper evidence.

## Conflict boundary

Historical non-conflicting documents, logs, reports, code, and CSV files from
the 2026-09-29 and 2026-10-07 branch candidates are preserved under
`1008/archive/branch_snapshots/`, with source commits, Git blob IDs, sizes, and
per-file import/omission decisions. These dated snapshots are provenance, not
active manuscript or code authority. Four generated panels from the 2026-09-29
release and generated 1006 images/figure exports are omitted.

The 1006 candidate manuscript tree and human-study materials are not in the
public archive. The 2026-09-29 runner variants are archived in separate
`source_conflicts/` directories, while d59 remains the active implementation
source. Resolved source choices and Phase A holdouts are recorded in
`CONFLICT_AUTHENTICITY_DECISIONS.md`; no source version overwrites the
authenticated 01549 manuscript baseline.
