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

## Private candidate

Pushed as a new branch:
`mvpainter/codex/cg-round2-1008-revision-20261008`.

The private candidate is based on d59 and retains the four participant-level
CSV files because the repository is private. It has the same curated v3
artifact selection and keeps the complete document, log, report, script, and
CSV records.

## Conflict boundary

Historical non-conflicting documents, logs, reports, code, and CSV files from
the 2026-09-29 and 2026-10-07 branch candidates are preserved under
`1008/archive/branch_snapshots/`, with source commits, Git blob IDs, sizes, and
per-file import/omission decisions. These dated snapshots are provenance, not
active manuscript or code authority. Four generated panels from the 2026-09-29
release and generated 1006 images/figure exports are omitted.

The 1006 branch's two direct audit conflicts are held out. Its candidate
manuscript tree and human-study materials are not in the public archive. The
private candidate keeps the historical human-study records in a separate
private-only archive; they are not accepted as confirmatory paper evidence.
The old runner variants are archived in separate `source_conflicts/`
directories, while d59 remains the active implementation source. No source
version overwrites the active tree unless its authenticity decision is recorded
in `CONFLICT_AUTHENTICITY_DECISIONS.md`.
