# Fresh C resume-driver hotfix

**Status:** frozen before the retry smoke or any Fresh C method output.  
**Scope:** orchestration only; the original protocol, input cache, runner,
checkpoint, conditions, cohort, cap semantics, and analyses remain unchanged.

The first resume command stopped while building the archive for the already
documented two-shard `global_embeds` smoke failure. A local import of the
launcher hash helper shadowed the resume driver's module-level `sha256`
function, producing `UnboundLocalError` before any smoke process was started.
The original state and this failure are preserved in
`1006/data/fresh_c/FRESH_C_CLOSURE_RESUME_ATTEMPT1_20261006.json`.

The versioned resume driver removes that name shadowing, binds its own source
hash and this document, and verifies the currently PASS input-embedding
manifest plus the untouched original closure script before proceeding. It
archives both earlier failures and their logs, then uses the already planned
new smoke directory. It does not alter the inference runner or inspect
comparative output.
