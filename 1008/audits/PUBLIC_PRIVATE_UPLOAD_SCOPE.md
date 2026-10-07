# Public and private upload scope

The d59 evidence snapshot remains the scientific claim authority. The 1008
revision branch is based on d59 for the private repository candidate.

## Public candidate

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

The private candidate is based on d59 and retains the four participant-level
CSV files because the repository is private. It has the same curated v3
artifact selection and keeps the complete document, log, report, script, and
CSV records.

## Conflict boundary

The conflicting manuscript, audit, and runner variants listed in
`REPOSITORY_UNIFICATION_AUDIT.md` are not included. Their authenticity and
scientific scope remain subject to file-level review.
