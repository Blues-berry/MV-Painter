# Merge conflict and resolution report

Conflict totals below count only conflicts created by an actual Git merge or cherry-pick attempt. A pre-merge source difference is not reported as a resolved conflict.

## codex/cg-01549-surgical-revision-20261008

- Merge strategy decision: full-history merge rejected at preflight because the branch contributes 165 unique commits, 24,820 unique blobs, about 3.63 GB uncompressed objects, and a 34,797-path tree delta with historical/generated outputs.
- Git merge attempted: no.
- Code conflict: NO_CONFLICT (no merge executed; no conflict was generated).
- Paper conflict: NO_CONFLICT (no paper merge executed; no conflict was generated).
- Candidate source differences reviewed: historical 01549/1008 manuscript, Supplement, response, figures and package outputs differ from current main. The candidate TeX was not applied because current main has the later evidence-bounded 1008 content and matching package source.
- Source-ready review commit deac8925d3bde92bae9ccb5d3ad92ea79ed69eae contained only the review-round mapping. Its content was byte-identical to the existing main file, so cherry-pick was skipped as empty. No conflict was resolved or hidden.
- Actual conflicts resolved: 0.

