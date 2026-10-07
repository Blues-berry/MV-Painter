# Phase A log

Date: 2026-10-07 UTC  
Branch: `codex/cg-round2-1008-revision-20261008`  
Base: `d59c4606ad54239bf4df4f20067bcc54989404f7`

## Completed

- Authenticated the actual 01549 submission source from the submitted
  `latex.zip`, title/abstract/section/figure/table continuity, PDF identity,
  and clean rebuild comparison.
- Copied the verified source package into
  `1008/manuscript/source_01549/` without replacing the original submission.
- Recorded d59's role as a read-only claim ceiling and captured the current
  Fresh C primary result and paper-facing boundaries.
- Compared public/private remotes, local worktrees, and divergent branch
  candidates. Preserved the unpushed full v3 merge under a local archive ref,
  then rebuilt the candidate from d59 with a curated v3 overlay. Kept all
  separate dirty worktrees and existing remote histories unchanged.
- Retained source documents, logs, reports, JSON, scripts, CSVs, and 24
  selected qualitative panels. Omitted bulk image renders, cached NPZ files,
  GLB intermediates, and bytecode. Excluded four participant-level CSVs from
  the public snapshot and recorded them in the omission manifest.
- Created the 01549→1008 preservation/surgery matrix, including every
  original Figure 1–7 and Table 1–9.

## Not started

- No manuscript, supplement, or reviewer response drafting.
- No canonical evidence files were edited.
- No manuscript or canonical evidence edit and no remote push yet. No existing
  public history was rewritten. The unfiltered local merge commit is
  `eb68d6ce593e374ef73bf633a00339f23f33fb81`, preserved at
  refs/archive/validation-v3-unfiltered-eb68d6ce.

## Phase A decision

`01549_SOURCE_VERIFIED = YES`  
`CLAIM_CEILING_IDENTIFIED = YES`  
`PRESERVATION_MATRIX_COMPLETE = YES`  
`REPOSITORY_BRANCH_MAP_COMPLETE = YES`  
`CURATED_ARCHIVE_PREPARED = YES`  
`UNFILTERED_MERGE_PRESERVED_LOCALLY = YES`  
`MANUSCRIPT_EDITING_STARTED = NO`

Material unresolved items are listed in
`REPOSITORY_UNIFICATION_AUDIT.md`: several 1006/legacy branches have
conflicting files or claim scope. Existing public refs contain participant-
linked CSVs; the sanitized public candidate is based before those files
entered history and does not rewrite existing refs.
