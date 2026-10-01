# ERRATUM — 10-object preflight sample indices in two earlier documents (2026-10-01)

Trigger: external review flagged that main_backbone_robustness1_20260930/
PROTOCOL_LOCK.md names sample "[3,23,45,60,88,137,166,199,232,262]" while
the frozen JSON records "[11,25,113,141,157,207,214,236,239,256]".

## Facts established (by execution and file inspection, 2026-10-01)

1. `random.Random(20260930).sample(range(276), 10)` =
   [236, 207, 113, 157, 256, 214, 11, 25, 141, 239]
   (sorted: [11, 25, 113, 141, 157, 207, 214, 236, 239, 256]).
2. The EXECUTED sample, recorded in the audit JSONs, is the correct draw in
   BOTH audits:
   - final_acceptance_20260930/SHARED_INPUT_DETERMINISM_AUDIT{,.pass1,.pass2}.json
     -> object_sample_indices = [11,25,113,141,157,207,214,236,239,256]
   - main_backbone_robustness1_20260930/ROBUSTNESS1_SHARED_INPUT_AUDIT.json
     -> object_sample_indices = [11,25,113,141,157,207,214,236,239,256]
3. The inline list "[3,23,45,60,88,137,166,199,232,262]" appears ONLY in
   the MD prose of SHARED_INPUT_DETERMINISM_AUDIT.md (L15-16) and was
   copied from there into PROTOCOL_LOCK.md (robustness1). It is a
   transcription error with no corresponding execution anywhere that we
   can locate; no JSON, log, or rows file records a preflight on that list.
4. Therefore the robustness1 PROTOCOL_LOCK's claim "(same frozen sample as
   the R0 shared-input audit)" is TRUE at the executed-JSON level; the MD
   texts contradict their own JSONs.

## Validity impact

None. The 10-object sample is a fixed preflight gate, not a statistical
estimator; both audits executed the correct canonical draw, passed
cross-process checks on it, and the formal 276-object runs never depended
on the sample. No result changes.

## Actions

- Original documents left untouched (no silent history edits).
- This erratum records the canonical sample and the propagation path.
- The Core-7 completion protocol lock quotes the canonical sample and
  runs its preflight on exactly [11,25,113,141,157,207,214,236,239,256].
