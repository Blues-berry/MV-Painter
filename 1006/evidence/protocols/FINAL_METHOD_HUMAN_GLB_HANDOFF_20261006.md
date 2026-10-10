# Final-method human and GLB handoff — preparation, not a frozen new study

User confirmed on 2026-10-06 that the old LLH participant package has not been
distributed. Preserve its original ZIP, questionnaire, assignment key and hashes.
Mark it superseded-for-distribution, not retrospectively cancelled data. There
are no human responses. A new final lock is required after E6's method decision.

## Current method-decision update

E6 was quantitatively qualified in development but stopped at the separate
method-difference/value gate. The current prospective comparison plan keeps
the original C3 method in the paper lineage without presuming it is the final
winner. The four candidate human-study pairs are C3–GFL, C3–GFH,
C3–no-adapter, and LLH–generic-linear. This uses six unique conditions and
tests the corrected linear direction directly. It is a post-result stimulus
plan, not a new preregistered experiment. Fresh C and its separate LLH/linear
addendum must pass their integrity gates and analyses before any stimulus or
assignment lock is made.

## Human package

Keep the four pairs above regardless of the Fresh C directions. Do not select
pairs by individual-object image ranks or construct an overall winner score.
Any future change must be recorded in a dated pre-response amendment and must
not be described as part of the original 01549 preregistration.

The input-only GLB eligibility selection is now frozen in
`data/fresh_c/FRESH_C_GLB_PANEL_SELECTION_20261006.json`: it takes the first 24
objects in frozen Fresh C cohort order with a hash-matching source GLB, an
allowlisted license tag, and finite UVs on each nonempty mesh. The selection
code did not read predictions or metrics, but Fresh C aggregate outcomes were
already available. This is a same-cohort, outcome-blind eligibility subset,
not an independent holdout. It does not implement the earlier proposed
texture/coverage/geometry stratification; that wording is superseded.

If the human package is built, use these same 24 UIDs so its 2D judgments and
the prospective GLB panel refer to the same fixed cases. Label them as an
eligibility-selected case set, not as stratified or population-representative.
Do not replace any object after generation begins. The CC BY tags are not a
completed source-attribution or redistribution audit, so external stimulus
distribution remains blocked until source-level rights and the institution's
ethics/waiver and consent requirements are recorded.

The existing production bake entry point rewrites UVs through xatlas and is not
valid for this panel's original-UV comparison. A read-only feasibility audit
and required technical gates are recorded in
`FRESH_C_GLB_BAKE_FEASIBILITY_AUDIT_20261006.md`.

40 anonymous slots, 24 trials per participant, six trials per pair, each object
once per participant, ten assignments per object/pair. Randomize A/B, trial and
question order using a new locked assignment manifest. Two separate A/B/tie
questions: reference color/material appearance fidelity, and naturalness of
texture/shape. Reference and complete object views must remain available.

Retain original predeclared attention/completion/duplicate rules, no duration
exclusion, no favorable-file selection. Close all 40 slots before analysis;
36 valid complete participants is the minimum, not a power guarantee. No optional
stopping or replacement after seeing preferences. Analyze eight endpoints using
object-equal preference estimates, tie=.5, participant/object two-way bootstrap
10,000 resamples, plus-one two-sided p values versus .5 and Holm across eight.
Report all exclusions, counts, nominal intervals and adjusted p values.

Do not distribute until source-level rights and the institution's ethics/waiver
and consent requirements are recorded. Do not invent an approval number. Raw
participant CSVs, assignment keys and identities remain private. The old CSV
schema remains usable; answers must come from actual participants, not examples.

## GLB panel

Final method plus the four human comparators: 24 UV-supported input-selected
objects x five conditions x 11 unseen camera views. Use the same bake settings,
UV identity, target cameras, source hashes and glTF base-color sampler for every
condition. No surface/UV or baking optimization tailored to one method. Bake
failures are retained and reported; do not drop objects after method outputs.
The endpoint is unlit base color, not full PBR or material/relighting fidelity.

The surface-boundary diagnostic has a separate known-texture synthetic pilot.
Passing its numeric pilot alone does not authorize an asset seam claim: validate
real glTF wrap/filter modes, known atlas reconstruction, topology assumptions and
UV lineage first. Unsupported/nonmanifold inputs remain explicit failures. Open
geometry boundaries are not seams. Freeze the production metric before inspecting
method comparisons; otherwise omit the seam-improvement claim.

## Current readiness

Method identity: pending. New stimulus/assignment lock: absent. Actual responses:
zero. Ethics record: not supplied. Source-rights verification for new objects:
pending. New GLB outputs: absent. This handoff is not a ready participant package.
