# Repository and evidence unification audit

Audit date: 2026-10-07 UTC  
Working branch: `codex/cg-round2-1008-revision-20261008`  
Claim-authority base: `d59c4606ad54239bf4df4f20067bcc54989404f7`  
Working baseline: d59c4606ad54239bf4df4f20067bcc54989404f7

The earlier unpushed full-archive merge is preserved at local ref
refs/archive/validation-v3-unfiltered-eb68d6ce; the 1008 branch no longer
inherits that 7.7 GB artifact commit.

## Repository topology

| Remote | Repository | Visibility / role |
|---|---|---|
| `origin` | `Blues-berry/MV-Painter` | Public working repository |
| `mvpainter` | `Blues-berry/MVPainter` | Private working repository |
| `upstream` | `amap-cvlab/MV-Painter` | Public upstream project |

The remote refs were fetched before this audit. No remote branch was changed
or pushed.

## Worktree preservation

| Worktree | Branch / HEAD | State and treatment |
|---|---|---|
| `/4T/CXY/MV-Painter` | `codex/scientific-validation-v3-20261002`, `5c2c8829` | Preserved untouched. It has 7,212 changed entries, including about 11 GB of staged v3 artifacts and in-flight audit edits. The full artifact checksum manifest passed 50,844/50,844 entries; this verifies file integrity against that manifest, not every scientific claim. |
| `/4T/CXY/MV-Painter-1006-wt` | `codex/paper-1006-20261006`, `a9ac1459` | Preserved untouched; clean at inspection. |
| `/4T/CXY/MV-Painter-1008` | `codex/cg-round2-1008-revision-20261008`, based on d59 | Isolated revision worktree. The verified 01549 source copy and Phase A records are retained. A curated v3 archive overlay is prepared below; the full unfiltered merge remains locally recoverable from the archive ref. |
| `/tmp/MV-Painter-evidence-closure` | `codex/evidence-closure-audit-20261005`, `7e659c7e` | Preserved as an older evidence snapshot. |
| `/tmp/MV-Painter-human-confirmatory-20261007` | `codex/human-confirmatory-analysis-20261007`, `86292c8b` | Preserved with its three in-flight edits; not used as paper-facing authority. |
| `/tmp/MV-Painter-v3-publish` | `codex/scientific-validation-v3-20261006`, `12da08c7` | Preserved as a prior v3 snapshot. |
| Other clean audit worktrees | `e267b2d5`, d59, or `87e4aa13` | Preserved; no cleanup, reset, prune, or garbage collection performed. |

The directory `final/.git` is empty; `final/` is not a separate Git
repository.

## Already integrated history

- `origin/codex/cg-revision-evidence-closure-20261007` points to d59, the
  same commit as the 1008 branch base.
- `origin/codex/scientific-validation-v3-20261006` at
  `f5bad8a1` is an ancestor of d59. Its committed snapshot is already in
  d59 history; it does not need a second merge.
- Earlier evidence-freeze and response branches whose commits are ancestors of
  d59 require no merge action. Their surviving records are in the current
  authority chain.

## Remaining branch candidates and merge decisions

Three-way path comparisons were performed against d59. For overlapping paths,
the base/ours/theirs blobs were compared; text files were checked for
three-way mergeability. A clean Git merge is not by itself a scientific
endorsement.

| Candidate | Git / content finding | Current decision |
|---|---|---|
| `codex/scientific-validation-v3-20261002` (`5c2c8829`) | 40,198 changed paths and 76,972,976 inserted lines relative to its merge base; 438 overlapping paths produced no content conflict. Its separate worktree also has about 11 GB of uncommitted data. | The unpushed full merge eb68d6ce was preserved locally, then removed from the 1008 branch ancestry before curation. The curated public-profile overlay retains source documents, logs, JSON reports, scripts, CSVs, and 24 selected qualitative panels; it imports 17,864 files (~1.60 GiB). The v3 results remain bounded by d59 and are not promoted wholesale as paper claims. The separate 11 GB worktree remains untouched. |
| `origin/codex/scientific-validation-v3-20261002` (`11cffe79`) | 1,419 branch-only paths; six add/add path conflicts in protocol, analysis, and manifest files. | Keep separate pending file-level provenance reconciliation with the newer v3 and d59 records. |
| `codex/evidence-closure-audit-20261005` (`7e659c7e`) | 14 add/add conflicts among 403 overlapping paths, including claim, visual, and analysis artifacts. | Do not merge wholesale; d59 is the later claim authority. Compare any disputed result at the artifact level first. |
| `codex/paper-1006-20261006` and public `origin/codex/paper-1006-20261006` | The 1006 branch adds a separate candidate/evidence package; one conflicting audit file is `FORMAL_VISUAL_EVIDENCE_REPORT.md`. The public tip is newer than the local 1006 worktree. | Keep as a separate candidate archive. Do not adopt its manuscript or overwrite d59 audit decisions. |
| `codex/human-confirmatory-analysis-20261007` / public paper-1006 tip | Conflicts in `FINAL_REVIEWER_RESPONSE_SKELETON.md` and `FORMAL_VISUAL_EVIDENCE_REPORT.md`. The “confirmatory” interpretation conflicts with execution deviations and the d59 human-data gate. | Exclude human results from 1008. No participant-level data copied. Preserve the branch for audit only. |
| `origin/codex/round2-author-review-20260929` | Five add/add conflicts in evaluation and runtime scripts among 37 overlapping paths; adds a 118-file dated evidence snapshot. | Do not merge scripts blindly. The 2026-09-29 snapshot is historical and its manuscript/evidence claims are superseded where d59 says so. |
| `origin/codex/adaptive-control-pilot-20260929` | Same five code conflicts in evaluation/runtime paths; three branch commits. | Keep as historical experiment branch; do not combine runner changes without source-level reconciliation. |
| Private `mvpainter/codex/round2-evidence-integrated-20261001` (`5a059b30`) | Three direct text conflicts in `final_round2.tex`, `response_letter_round2.md`, and `supplementary_round2.tex`; its manuscript narrative predates d59's authority and removes later audit records. | Do not merge the manuscript snapshot. d59's evidence and 01549's source remain the controlling inputs. |

The full merge commit eb68d6ce is retained only under the local archive ref;
it is not an ancestor of the candidate upload branches. The curated import
uses d59 as its claim authority and leaves its existing files unchanged. The
v3 source commit contains 40,196 files; 438 matching files were already in
d59. The public-profile archive imports 17,864 new files (~1.60 GiB), keeps
all source documents, JSON/log records, scripts, CSVs, and 24 selected formal
qualitative panels, and omits bulk rendered images, NPZ caches, GLBs, and
bytecode. The omission manifest records paths, sizes, Git blob IDs, and
reasons. Four participant-level CSVs in d59 are excluded from the public
snapshot; a public candidate is based on the last commit before those CSVs
entered history. The private candidate retains the records. No remote history
is rewritten.

## Cross-version evidence decisions

1. The 01549 submitted package is the only manuscript base. The current root
   `final/final_0903.tex` and d59's restructured `final_round2.tex` are not
   substitutes.
2. d59 is the newest paper-facing non-human claim authority for this revision.
   Older evidence ledgers remain provenance/history unless their raw inputs,
   identity, protocol, and analysis survive the d59 gates.
3. d59 Fresh C and v3 `FRESH_CONFIRM_300` are distinct N=300 cohorts with
   zero UID overlap. They are never pooled or relabeled as a replication.
4. Historical source tables/figures are not automatically validated by their
   presence in the 01549 PDF or LaTeX package. If the supporting rows and
   protocol are not in current authority, those results remain development or
   historical-only.
5. The private 2026-10-01 manuscript branch, the 2026-10-06/07 1006 candidate,
   and the 01549 submission are different document versions; they are not
   concatenated into a single manuscript.
6. The public v3 history contains participant-linked response and assignment
   files. d59 records that public redistribution permission is not established.
   This audit does not copy those rows or rewrite public history.

## Merge and release boundary

The candidate archive and source/audit package are prepared locally. No
remote branch has been changed yet. The public candidate avoids adding the
four participant-level CSVs and does not rewrite existing public history;
existing public refs still contain those files. The other conflicting
branches remain separate pending artifact-level authenticity review.
